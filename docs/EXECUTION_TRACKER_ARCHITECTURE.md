# Execution Tracker Architecture - Technical Design

**Date Created:** 2025-11-03 (Session 19)
**Purpose:** Define HOW the stateful execution tracker works
**Status:** 🚧 DRAFT v0.1 - Ready for review
**Related:** `ITEM_TYPE_TAXONOMY.md` (what to track), `EXECUTION_HISTORY_UNDERSTANDING_V3.md` (why)

---

## 🚨 CRITICAL DESIGN CONSTRAINTS

**Non-Blocking & Fail-Safe Requirements:**

```
✅ Event logging < 1ms per event (in-memory append only)
✅ No disk I/O during pipeline execution
✅ Total overhead < 100ms for entire execution
✅ Tracker failures NEVER stall pipeline
✅ Try-catch around ALL tracker calls
```

**Performance Target:**
- Pipeline execution time should be identical ±5% with/without tracking
- Typical execution: 15-20 events logged, ~20-50ms total tracking overhead

---

## 1. Architecture Overview

### 1.1 Core Concept

**Stateful Tracker = Single Source of Truth**

```
┌─────────────────────────────────────────────────────────────┐
│                    ExecutionTracker                         │
│                 (In-Memory State Machine)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  - Collects items chronologically during pipeline run      │
│  - Maintains global sequence numbers (1, 2, 3, ...)        │
│  - Tracks stage/iteration context                          │
│  - FAST: In-memory list append only (~0.1-0.5ms)          │
│                                                             │
│  ExecutionRecord {                                          │
│    execution_id: "exec_abc123",                            │
│    items: [                                                │
│      {seq: 1, stage: 0, item_type: "pipeline_start", ...}, │
│      {seq: 2, stage: 1, item_type: "user_input_text", ...},│
│      {seq: 3, stage: 2, item_type: "interception_..."},   │
│      ...                                                   │
│    ]                                                       │
│  }                                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
           ↓                                    ↓
           ↓                                    ↓
    ┌──────────────┐                   ┌─────────────────┐
    │ Export API   │                   │ Live UI Stream  │
    │ (Research)   │                   │ (WebSocket)     │
    └──────────────┘                   └─────────────────┘
    XML, PDF, JSON                     Real-time events
```

### 1.2 Design Principles

1. **Request-Scoped Lifecycle**
   - One tracker instance per pipeline execution
   - Created at pipeline start, finalized at completion
   - Passed explicitly through orchestration layers (no globals)

2. **In-Memory First, Persist After**
   - Collect all items in memory during execution
   - Write to disk/DB AFTER pipeline completes
   - No I/O blocking during stages

3. **Fail-Safe Wrapper**
   - All tracker calls wrapped in try-catch
   - Log warnings on failure, continue execution
   - Pipeline NEVER depends on tracker success

4. **Explicit Over Implicit**
   - Tracker passed as parameter (not global/singleton)
   - Stage functions call `tracker.log_item()` explicitly
   - Clear integration points in orchestration code

---

## 2. Tracker Lifecycle

### 2.1 Creation & Initialization

**Where:** `schema_pipeline_routes.py` (main orchestration entry point)

```python
@app.route('/api/schema/pipeline/execute', methods=['POST'])
async def execute_pipeline_endpoint():
    """Main API endpoint - creates tracker at request start"""

    # 1. Parse request
    data = request.get_json()
    config_name = data.get('schema')
    input_text = data.get('input_text')
    execution_mode = data.get('execution_mode', 'eco')
    safety_level = data.get('safety_level', 'kids')

    # 2. Create tracker (request-scoped)
    from execution_history.tracker import ExecutionTracker
    tracker = ExecutionTracker(
        config_name=config_name,
        execution_mode=execution_mode,
        safety_level=safety_level,
        user_id=session.get('user_id', 'anonymous'),
        session_id=session.get('session_id', 'default')
    )

    # 3. Log pipeline start
    tracker.log_pipeline_start(
        input_text=input_text,
        metadata={
            'request_id': request.id,
            'timestamp': datetime.now().isoformat()
        }
    )

    # 4. Pass tracker through orchestration
    try:
        result = await orchestrate_4_stage_pipeline(
            config_name=config_name,
            input_text=input_text,
            execution_mode=execution_mode,
            safety_level=safety_level,
            tracker=tracker  # ← Explicit parameter
        )

        # 5. Log pipeline completion
        tracker.log_pipeline_complete(
            total_duration=result.execution_time,
            outputs_generated=len(result.media_outputs)
        )

        # 6. Persist tracker data (AFTER pipeline completes)
        tracker.finalize()

        return jsonify(result.to_dict())

    except Exception as e:
        # 7. Log pipeline error
        tracker.log_pipeline_error(
            error_type=type(e).__name__,
            error_message=str(e),
            stage=tracker.current_stage
        )
        tracker.finalize()  # Persist even on error
        raise
```

### 2.2 State Machine

**Tracker maintains current execution context:**

```python
class ExecutionTracker:
    def __init__(self, config_name, execution_mode, safety_level, ...):
        self.execution_id = generate_execution_id()  # "exec_abc123"
        self.config_name = config_name
        self.execution_mode = execution_mode
        self.safety_level = safety_level

        # State tracking
        self.current_stage = 0  # Updated by orchestrator
        self.current_stage_iteration = None  # For Stille Post iterations
        self.current_loop_iteration = None  # For multi-output loop
        self.sequence_counter = 0  # Global item counter

        # Collected items
        self.items: List[ExecutionItem] = []

        # Timing
        self.start_time = time.time()
        self.finalized = False
```

### 2.3 Stage Context Management

**Orchestrator updates tracker context as stages progress:**

```python
async def orchestrate_4_stage_pipeline(config_name, input_text, tracker, ...):
    """Main orchestration - updates tracker.current_stage"""

    # STAGE 1: Pre-Interception
    tracker.set_stage(1)
    translated_text = await execute_stage1_translation(input_text, tracker)
    is_safe = await execute_stage1_safety(translated_text, tracker)

    if not is_safe:
        return  # Pipeline blocked, Stage 2-4 not executed

    # STAGE 2: Interception (can be recursive)
    tracker.set_stage(2)

    if pipeline.is_recursive:
        # Stille Post: 8 iterations
        for iteration in range(1, 9):
            tracker.set_stage_iteration(iteration)
            result = await execute_interception_iteration(text, tracker)
            text = result  # Feed forward
    else:
        # Dada: Single transformation
        result = await execute_interception(translated_text, tracker)

    # STAGE 3-4: Multi-Output Loop
    tracker.set_stage(3)  # Will toggle between 3 and 4

    for loop_idx, output_config in enumerate(output_configs, start=1):
        tracker.set_loop_iteration(loop_idx)

        # Stage 3: Pre-output safety
        tracker.set_stage(3)
        safety_result = await execute_stage3_safety(prompt, tracker)

        if not safety_result['safe']:
            continue  # Skip this output, move to next

        # Stage 4: Media generation
        tracker.set_stage(4)
        media = await execute_stage4_media(prompt, output_config, tracker)
```

### 2.4 Finalization & Persistence

**After pipeline completes (or errors), persist data:**

```python
def finalize(self):
    """Persist execution record to disk/DB"""
    if self.finalized:
        return  # Already finalized

    self.finalized = True

    # Build complete record
    record = ExecutionRecord(
        execution_id=self.execution_id,
        config_name=self.config_name,
        timestamp=datetime.fromtimestamp(self.start_time),
        execution_mode=self.execution_mode,
        safety_level=self.safety_level,
        user_id=self.user_id,
        session_id=self.session_id,
        total_execution_time=time.time() - self.start_time,
        items=self.items,
        taxonomy_version="1.0"
    )

    # Persist to storage (AFTER pipeline execution, not during)
    storage_service.save_execution_record(record)

    # Optionally: Send to live UI WebSocket
    if has_live_listeners(self.execution_id):
        websocket_service.send_execution_complete(self.execution_id, record)
```

---

## 3. Integration Points

### 3.1 Entry Point: schema_pipeline_routes.py

**Main orchestration function:**

```python
async def orchestrate_4_stage_pipeline(
    config_name: str,
    input_text: str,
    execution_mode: str,
    safety_level: str,
    tracker: ExecutionTracker  # ← Explicit parameter
) -> PipelineResult:
    """
    4-Stage orchestration with execution tracking

    Integration: Tracker is passed to ALL stage functions
    """
    # ... (see section 2.3 above)
```

### 3.2 Stage 1: Translation + Safety

**Modified stage_orchestrator.py functions:**

```python
async def execute_stage1_translation(
    text: str,
    execution_mode: str,
    pipeline_executor,
    tracker: ExecutionTracker  # ← NEW parameter
) -> str:
    """Execute Stage 1a: Translation"""

    # Log user input
    tracker.log_user_input_text(text)

    # Execute translation
    result = await pipeline_executor.execute_pipeline(
        'pre_interception/correction_translation_de_en',
        text,
        execution_mode=execution_mode
    )

    if result.success:
        # Log translation result
        tracker.log_translation_result(
            translated_text=result.final_output,
            from_lang='de',
            to_lang='en',
            model_used=result.model_used,
            execution_time=result.execution_time
        )
        return result.final_output
    else:
        logger.warning(f"Translation failed: {result.error}")
        return text


async def execute_stage1_safety(
    text: str,
    safety_level: str,
    execution_mode: str,
    pipeline_executor,
    tracker: ExecutionTracker  # ← NEW parameter
) -> Tuple[bool, List[str]]:
    """Execute Stage 1b: Hybrid Safety Check"""

    # Fast filter check
    has_terms, found_terms = fast_filter_check(text, 'stage1')

    if not has_terms:
        # FAST PATH: Log safety check passed
        tracker.log_stage1_safety_check(
            safe=True,
            method='fast_filter',
            execution_time=0.001
        )
        return (True, [])

    # SLOW PATH: Llama-Guard verification
    result = await pipeline_executor.execute_pipeline(
        'pre_interception/safety_llamaguard',
        text,
        execution_mode=execution_mode
    )

    if result.success:
        is_safe, codes = parse_llamaguard_output(result.final_output)

        if not is_safe:
            # Log blocked
            tracker.log_stage1_blocked(
                blocked_reason='§86a_violation',
                blocked_codes=codes,
                model_used=result.model_used
            )
            return (False, codes)
        else:
            # Log safety check passed (false positive)
            tracker.log_stage1_safety_check(
                safe=True,
                method='llm_context_check',
                found_terms=found_terms,
                model_used=result.model_used,
                execution_time=result.execution_time
            )
            return (True, [])
```

### 3.3 Stage 2: Interception (Recursive Loops)

**Integration with PipelineExecutor:**

```python
# In schema_pipeline_routes.py orchestration:

if pipeline.control_flow == 'iterative':
    # Stille Post: 8 iterations
    iterations = pipeline.meta.get('max_iterations', 8)

    for iteration_num in range(1, iterations + 1):
        # Update tracker context
        tracker.set_stage_iteration(iteration_num)

        # Execute one iteration
        result = await pipeline_executor.execute_pipeline(
            pipeline_name,
            current_text,
            execution_mode=execution_mode,
            tracker=tracker  # ← Pass tracker to executor
        )

        # Log iteration result (done inside executor or here)
        tracker.log_interception_iteration(
            iteration_num=iteration_num,
            result_text=result.final_output,
            from_lang=current_lang,
            to_lang=next_lang,
            model_used=result.model_used
        )

        current_text = result.final_output

    # Log final result
    tracker.log_interception_final(
        final_text=current_text,
        total_iterations=iterations
    )
```

### 3.4 Stage 3-4: Multi-Output Loop

**Integration with output configs:**

```python
# In schema_pipeline_routes.py orchestration:

output_configs = config.media_preferences.get('output_configs', [])

for loop_idx, output_config_name in enumerate(output_configs, start=1):
    # Update tracker context
    tracker.set_loop_iteration(loop_idx)
    tracker.set_stage(3)

    # STAGE 3: Pre-output safety
    safety_result = await execute_stage3_safety(
        prompt=final_prompt,
        safety_level=safety_level,
        media_type='image',
        execution_mode=execution_mode,
        pipeline_executor=pipeline_executor,
        tracker=tracker  # ← Pass tracker
    )

    # Log safety check
    tracker.log_stage3_safety_check(
        loop_iteration=loop_idx,
        safe=safety_result['safe'],
        method=safety_result['method'],
        config_used=output_config_name
    )

    if not safety_result['safe']:
        # Log blocked
        tracker.log_stage3_blocked(
            loop_iteration=loop_idx,
            config_used=output_config_name,
            abort_reason=safety_result['abort_reason']
        )
        continue  # Skip this output

    # STAGE 4: Media generation
    tracker.set_stage(4)

    media_result = await pipeline_executor.execute_pipeline(
        output_config_name,
        final_prompt,
        execution_mode=execution_mode
    )

    # Log output
    if media_result.success:
        tracker.log_output_image(
            loop_iteration=loop_idx,
            config_used=output_config_name,
            file_path=media_result.file_path,
            model_used=media_result.model_used,
            backend_used=media_result.backend_used,
            metadata={
                'width': 1024,
                'height': 1024,
                'seed': media_result.seed,
                'cfg_scale': 7.0,
                # ... all backend parameters for reproducibility
            }
        )
```

---

## 4. Tracker Implementation

### 4.1 Core Class Structure

**File:** `devserver/execution_history/tracker.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import time
import logging
import uuid

logger = logging.getLogger(__name__)


class ExecutionTracker:
    """
    Stateful execution tracker - collects items during pipeline execution

    Design: In-memory only during execution, persisted after completion
    Performance: <1ms per log_* call (list append only)
    Fail-safe: All public methods wrapped in try-catch
    """

    def __init__(
        self,
        config_name: str,
        execution_mode: str,
        safety_level: str,
        user_id: str = 'anonymous',
        session_id: str = 'default'
    ):
        """Initialize tracker for a single pipeline execution"""
        self.execution_id = self._generate_execution_id()
        self.config_name = config_name
        self.execution_mode = execution_mode
        self.safety_level = safety_level
        self.user_id = user_id
        self.session_id = session_id

        # State tracking
        self.current_stage = 0
        self.current_stage_iteration: Optional[int] = None
        self.current_loop_iteration: Optional[int] = None
        self.sequence_counter = 0

        # Collected items (in-memory during execution)
        self.items: List[ExecutionItem] = []

        # Timing
        self.start_time = time.time()
        self.finalized = False

        logger.info(f"[TRACKER] Created tracker {self.execution_id} for config '{config_name}'")

    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique = uuid.uuid4().hex[:8]
        return f"exec_{timestamp}_{unique}"

    # ========================================================================
    # STATE MANAGEMENT (called by orchestrator)
    # ========================================================================

    def set_stage(self, stage: int):
        """Update current stage context"""
        self.current_stage = stage

    def set_stage_iteration(self, iteration: Optional[int]):
        """Update current stage iteration (for recursive pipelines)"""
        self.current_stage_iteration = iteration

    def set_loop_iteration(self, iteration: Optional[int]):
        """Update current loop iteration (for multi-output)"""
        self.current_loop_iteration = iteration

    # ========================================================================
    # LOGGING METHODS (called by stage functions)
    # ========================================================================
    # All methods follow fail-safe pattern: try-catch, log warning, continue

    def log_pipeline_start(self, input_text: str, metadata: Dict[str, Any] = None):
        """Log pipeline start event"""
        try:
            self._log_item(
                stage=0,
                media_type=MediaType.METADATA,
                item_type=ItemType.PIPELINE_START,
                content=None,
                metadata={
                    'config_name': self.config_name,
                    'execution_mode': self.execution_mode,
                    'safety_level': self.safety_level,
                    'user_id': self.user_id,
                    'session_id': self.session_id,
                    **(metadata or {})
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log pipeline start: {e}")

    def log_user_input_text(self, text: str):
        """Log user text input (Stage 1)"""
        try:
            self._log_item(
                stage=1,
                media_type=MediaType.TEXT,
                item_type=ItemType.USER_INPUT_TEXT,
                content=text,
                metadata={
                    'input_language': 'de',  # Detect or default
                    'char_count': len(text)
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log user input: {e}")

    def log_translation_result(
        self,
        translated_text: str,
        from_lang: str,
        to_lang: str,
        model_used: str,
        execution_time: float
    ):
        """Log translation result (Stage 1)"""
        try:
            self._log_item(
                stage=1,
                media_type=MediaType.TEXT,
                item_type=ItemType.TRANSLATION_RESULT,
                content=translated_text,
                model_used=model_used,
                execution_time=execution_time,
                metadata={
                    'from_lang': from_lang,
                    'to_lang': to_lang
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log translation: {e}")

    def log_stage1_safety_check(
        self,
        safe: bool,
        method: str,
        execution_time: float = 0.001,
        found_terms: List[str] = None,
        model_used: str = None
    ):
        """Log Stage 1 safety check result"""
        try:
            self._log_item(
                stage=1,
                media_type=MediaType.METADATA,
                item_type=ItemType.STAGE1_SAFETY_CHECK,
                content=None,
                model_used=model_used,
                execution_time=execution_time,
                metadata={
                    'safe': safe,
                    'method': method,
                    'found_terms': found_terms or [],
                    'risk_level': 'none' if safe else 'high'
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log stage1 safety check: {e}")

    def log_stage1_blocked(
        self,
        blocked_reason: str,
        blocked_codes: List[str],
        model_used: str
    ):
        """Log Stage 1 blocked event (pipeline stops here)"""
        try:
            # Build educational message
            from schemas.engine.stage_orchestrator import build_safety_message
            error_message = build_safety_message(blocked_codes, lang='de')

            self._log_item(
                stage=1,
                media_type=MediaType.METADATA,
                item_type=ItemType.STAGE1_BLOCKED,
                content=error_message,
                model_used=model_used,
                metadata={
                    'blocked_reason': blocked_reason,
                    'blocked_codes': blocked_codes
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log stage1 blocked: {e}")

    def log_interception_iteration(
        self,
        iteration_num: int,
        result_text: str,
        from_lang: str,
        to_lang: str,
        model_used: str,
        config_used: str = None
    ):
        """Log one interception iteration (Stage 2, recursive)"""
        try:
            self._log_item(
                stage=2,
                stage_iteration=iteration_num,
                media_type=MediaType.TEXT,
                item_type=ItemType.INTERCEPTION_ITERATION,
                content=result_text,
                config_used=config_used,
                model_used=model_used,
                metadata={
                    'from_lang': from_lang,
                    'to_lang': to_lang,
                    'iteration_type': 'translation'
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log interception iteration: {e}")

    def log_interception_final(
        self,
        final_text: str,
        total_iterations: int,
        config_used: str = None
    ):
        """Log final interception result (Stage 2)"""
        try:
            self._log_item(
                stage=2,
                media_type=MediaType.TEXT,
                item_type=ItemType.INTERCEPTION_FINAL,
                content=final_text,
                config_used=config_used,
                metadata={
                    'total_iterations': total_iterations,
                    'transformation_type': config_used or 'generic'
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log interception final: {e}")

    def log_stage3_safety_check(
        self,
        loop_iteration: int,
        safe: bool,
        method: str,
        config_used: str
    ):
        """Log Stage 3 pre-output safety check"""
        try:
            self._log_item(
                stage=3,
                loop_iteration=loop_iteration,
                media_type=MediaType.METADATA,
                item_type=ItemType.STAGE3_SAFETY_CHECK,
                content=None,
                config_used=config_used,
                metadata={
                    'safe': safe,
                    'method': method,
                    'safety_level': self.safety_level
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log stage3 safety check: {e}")

    def log_stage3_blocked(
        self,
        loop_iteration: int,
        config_used: str,
        abort_reason: str
    ):
        """Log Stage 3 blocked event (output skipped, not entire pipeline)"""
        try:
            self._log_item(
                stage=3,
                loop_iteration=loop_iteration,
                media_type=MediaType.METADATA,
                item_type=ItemType.STAGE3_BLOCKED,
                content=abort_reason,
                config_used=config_used,
                metadata={
                    'blocked_reason': 'age_inappropriate',
                    'safety_level': self.safety_level,
                    'fallback': 'text_alternative_provided'
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log stage3 blocked: {e}")

    def log_output_image(
        self,
        loop_iteration: int,
        config_used: str,
        file_path: str,
        model_used: str,
        backend_used: str,
        metadata: Dict[str, Any]
    ):
        """Log Stage 4 image output"""
        try:
            self._log_item(
                stage=4,
                loop_iteration=loop_iteration,
                media_type=MediaType.IMAGE,
                item_type=ItemType.OUTPUT_IMAGE,
                file_path=file_path,
                config_used=config_used,
                model_used=model_used,
                backend_used=backend_used,
                metadata=metadata  # width, height, seed, cfg_scale, steps, sampler, etc.
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log output image: {e}")

    def log_pipeline_complete(
        self,
        total_duration: float,
        outputs_generated: int
    ):
        """Log pipeline completion event"""
        try:
            self._log_item(
                stage=5,
                media_type=MediaType.METADATA,
                item_type=ItemType.PIPELINE_COMPLETE,
                content=None,
                metadata={
                    'total_duration_seconds': total_duration,
                    'total_items_logged': len(self.items) + 1,  # +1 for this item
                    'outputs_generated': outputs_generated,
                    'stages_completed': [1, 2, 3, 4]
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log pipeline complete: {e}")

    def log_pipeline_error(
        self,
        error_type: str,
        error_message: str,
        stage: int
    ):
        """Log pipeline error event"""
        try:
            self._log_item(
                stage=stage,
                media_type=MediaType.METADATA,
                item_type=ItemType.PIPELINE_ERROR,
                content=f"{error_type}: {error_message}",
                metadata={
                    'error_type': error_type,
                    'error_stage': stage,
                    'error_message': error_message,
                    'recoverable': False
                }
            )
        except Exception as e:
            logger.warning(f"[TRACKER] Failed to log pipeline error: {e}")

    # ========================================================================
    # INTERNAL HELPERS
    # ========================================================================

    def _log_item(
        self,
        stage: int,
        media_type: 'MediaType',
        item_type: 'ItemType',
        content: Optional[str] = None,
        file_path: Optional[str] = None,
        config_used: Optional[str] = None,
        model_used: Optional[str] = None,
        backend_used: Optional[str] = None,
        execution_time: Optional[float] = None,
        stage_iteration: Optional[int] = None,
        loop_iteration: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Internal method to log an item (fast in-memory append)

        Performance: ~0.1-0.5ms (list append + dataclass creation)
        """
        self.sequence_counter += 1

        item = ExecutionItem(
            sequence_number=self.sequence_counter,
            timestamp=datetime.now(),
            stage=stage,
            stage_iteration=stage_iteration or self.current_stage_iteration,
            loop_iteration=loop_iteration or self.current_loop_iteration,
            media_type=media_type,
            item_type=item_type,
            content=content,
            file_path=file_path,
            config_used=config_used,
            model_used=model_used,
            backend_used=backend_used,
            execution_time=execution_time,
            metadata=metadata or {}
        )

        self.items.append(item)  # FAST: in-memory list append

    def finalize(self):
        """
        Persist execution record to storage (called AFTER pipeline completes)

        This is the ONLY method that does disk I/O
        """
        if self.finalized:
            logger.warning(f"[TRACKER] Tracker {self.execution_id} already finalized")
            return

        self.finalized = True

        try:
            # Build complete record
            record = ExecutionRecord(
                execution_id=self.execution_id,
                config_name=self.config_name,
                timestamp=datetime.fromtimestamp(self.start_time),
                user_id=self.user_id,
                session_id=self.session_id,
                execution_mode=self.execution_mode,
                safety_level=self.safety_level,
                used_seed=None,  # TODO: Extract from media outputs
                total_execution_time=time.time() - self.start_time,
                items=self.items,
                taxonomy_version="1.0"
            )

            # Persist to storage
            from execution_history.storage import save_execution_record
            save_execution_record(record)

            logger.info(
                f"[TRACKER] Finalized {self.execution_id}: "
                f"{len(self.items)} items, "
                f"{record.total_execution_time:.1f}s total"
            )

        except Exception as e:
            logger.error(f"[TRACKER] Failed to finalize tracker {self.execution_id}: {e}")
            # Don't raise - tracker failures should never break pipeline
```

### 4.2 Helper Methods

**Additional convenience methods:**

```python
class ExecutionTracker:
    # ... (above)

    def get_execution_record(self) -> ExecutionRecord:
        """Get current execution record (without finalizing)"""
        return ExecutionRecord(
            execution_id=self.execution_id,
            config_name=self.config_name,
            timestamp=datetime.fromtimestamp(self.start_time),
            user_id=self.user_id,
            session_id=self.session_id,
            execution_mode=self.execution_mode,
            safety_level=self.safety_level,
            used_seed=None,
            total_execution_time=time.time() - self.start_time,
            items=self.items,
            taxonomy_version="1.0"
        )

    def get_items_by_stage(self, stage: int) -> List[ExecutionItem]:
        """Get all items for a specific stage"""
        return [item for item in self.items if item.stage == stage]

    def get_items_by_type(self, item_type: ItemType) -> List[ExecutionItem]:
        """Get all items of a specific type"""
        return [item for item in self.items if item.item_type == item_type]
```

---

## 5. Storage Strategy

### 5.1 Storage Service Interface

**File:** `devserver/execution_history/storage.py`

```python
from pathlib import Path
import json
import logging
from typing import Optional
from .models import ExecutionRecord

logger = logging.getLogger(__name__)

STORAGE_DIR = Path(__file__).parent.parent.parent / "exports" / "executions"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_execution_record(record: ExecutionRecord):
    """
    Save execution record to JSON file

    File location: exports/executions/{execution_id}.json
    Format: Human-readable JSON (indented, sorted keys)
    """
    try:
        file_path = STORAGE_DIR / f"{record.execution_id}.json"

        # Convert to dict (dataclass → dict)
        record_dict = record.to_dict()

        # Write JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(record_dict, f, indent=2, ensure_ascii=False, sort_keys=True)

        logger.info(f"[STORAGE] Saved execution record: {file_path}")

    except Exception as e:
        logger.error(f"[STORAGE] Failed to save execution record {record.execution_id}: {e}")
        raise


def load_execution_record(execution_id: str) -> Optional[ExecutionRecord]:
    """Load execution record from JSON file"""
    try:
        file_path = STORAGE_DIR / f"{execution_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            record_dict = json.load(f)

        # Convert dict → dataclass
        return ExecutionRecord.from_dict(record_dict)

    except Exception as e:
        logger.error(f"[STORAGE] Failed to load execution record {execution_id}: {e}")
        return None


def list_execution_records(limit: int = 100, offset: int = 0) -> List[str]:
    """List execution IDs (sorted by creation time, newest first)"""
    try:
        files = sorted(
            STORAGE_DIR.glob("exec_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        execution_ids = [f.stem for f in files[offset:offset+limit]]
        return execution_ids

    except Exception as e:
        logger.error(f"[STORAGE] Failed to list execution records: {e}")
        return []
```

### 5.2 Storage Format: JSON

**Example file:** `exports/executions/exec_20251103_143025_abc12345.json`

```json
{
  "execution_id": "exec_20251103_143025_abc12345",
  "config_name": "dada",
  "timestamp": "2025-11-03T14:30:25.123456",
  "user_id": "user_abc123",
  "session_id": "session_xyz789",
  "execution_mode": "eco",
  "safety_level": "kids",
  "used_seed": null,
  "total_execution_time": 45.234,
  "taxonomy_version": "1.0",
  "items": [
    {
      "sequence_number": 1,
      "timestamp": "2025-11-03T14:30:25.123456",
      "stage": 0,
      "stage_iteration": null,
      "loop_iteration": null,
      "media_type": "metadata",
      "item_type": "pipeline_start",
      "content": null,
      "file_path": null,
      "config_used": null,
      "model_used": null,
      "backend_used": null,
      "execution_time": null,
      "metadata": {
        "config_name": "dada",
        "execution_mode": "eco",
        "safety_level": "kids"
      }
    },
    {
      "sequence_number": 2,
      "timestamp": "2025-11-03T14:30:25.234567",
      "stage": 1,
      "stage_iteration": null,
      "loop_iteration": null,
      "media_type": "text",
      "item_type": "user_input_text",
      "content": "Eine Blume auf der Wiese",
      "file_path": null,
      "config_used": null,
      "model_used": null,
      "backend_used": null,
      "execution_time": null,
      "metadata": {
        "input_language": "de",
        "char_count": 24
      }
    }
    // ... more items ...
  ]
}
```

### 5.3 Future: Database Storage (Optional)

**When to migrate to SQLite/PostgreSQL:**

- User has >1000 execution records
- Need complex queries (e.g., "Find all Stille Post executions with >5 iterations")
- Need full-text search across prompts
- Need aggregation (e.g., "Average execution time by config")

**Schema:**

```sql
CREATE TABLE executions (
    execution_id TEXT PRIMARY KEY,
    config_name TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    user_id TEXT,
    session_id TEXT,
    execution_mode TEXT,
    safety_level TEXT,
    total_execution_time REAL,
    taxonomy_version TEXT,
    record_json TEXT  -- Store full JSON for flexibility
);

CREATE TABLE execution_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    stage INTEGER NOT NULL,
    stage_iteration INTEGER,
    loop_iteration INTEGER,
    media_type TEXT NOT NULL,
    item_type TEXT NOT NULL,
    content TEXT,
    file_path TEXT,
    config_used TEXT,
    model_used TEXT,
    backend_used TEXT,
    execution_time REAL,
    metadata_json TEXT,
    FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
);

CREATE INDEX idx_execution_items_execution_id ON execution_items(execution_id);
CREATE INDEX idx_execution_items_item_type ON execution_items(item_type);
CREATE INDEX idx_execution_items_stage ON execution_items(stage);
```

---

## 6. Live UI Event Streaming (Optional)

### 6.1 WebSocket Architecture

**For real-time progress display in UI:**

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend (Browser)                                          │
│                                                             │
│  ws://localhost:17801/ws/execution/{execution_id}          │
│  │                                                          │
│  └─→ Receives events as they happen:                       │
│       - STAGE_TRANSITION: "Stage 1 → Stage 2"              │
│       - INTERCEPTION_ITERATION: "Iteration 3/8 complete"   │
│       - OUTPUT_IMAGE: "Image generated"                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↑
                         │ WebSocket messages
                         │
┌─────────────────────────────────────────────────────────────┐
│ ExecutionTracker                                            │
│                                                             │
│  def _log_item(...):                                        │
│      self.items.append(item)  # In-memory                  │
│                                                             │
│      # OPTIONAL: Stream to WebSocket if client connected   │
│      if has_live_listeners(self.execution_id):             │
│          websocket_service.broadcast_event(               │
│              self.execution_id,                            │
│              item.to_dict()                                │
│          )                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Implementation (Flask-SocketIO)

**File:** `devserver/my_app/routes/websocket_routes.py`

```python
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

socketio = SocketIO(app, cors_allowed_origins="*")

# Track which clients are listening to which executions
active_listeners = {}  # {execution_id: [client_sid, client_sid, ...]}


@socketio.on('subscribe_execution')
def handle_subscribe_execution(data):
    """Client subscribes to live execution events"""
    execution_id = data.get('execution_id')
    if not execution_id:
        return {'error': 'execution_id required'}

    join_room(execution_id)

    if execution_id not in active_listeners:
        active_listeners[execution_id] = []
    active_listeners[execution_id].append(request.sid)

    emit('subscribed', {'execution_id': execution_id})


@socketio.on('unsubscribe_execution')
def handle_unsubscribe_execution(data):
    """Client unsubscribes from execution events"""
    execution_id = data.get('execution_id')
    if not execution_id:
        return

    leave_room(execution_id)

    if execution_id in active_listeners:
        active_listeners[execution_id] = [
            sid for sid in active_listeners[execution_id]
            if sid != request.sid
        ]


def broadcast_execution_event(execution_id: str, item: Dict[str, Any]):
    """Broadcast execution item to subscribed clients"""
    if execution_id in active_listeners and active_listeners[execution_id]:
        socketio.emit(
            'execution_event',
            {'item': item},
            room=execution_id
        )


def has_live_listeners(execution_id: str) -> bool:
    """Check if any clients are listening to this execution"""
    return execution_id in active_listeners and len(active_listeners[execution_id]) > 0
```

### 6.3 Frontend Integration

**JavaScript client:**

```javascript
// Connect to WebSocket
const socket = io('http://localhost:17801');

// Start pipeline execution
const executionId = await startPipelineExecution(config, input);

// Subscribe to live events
socket.emit('subscribe_execution', { execution_id: executionId });

// Handle events
socket.on('execution_event', (data) => {
    const item = data.item;

    switch (item.item_type) {
        case 'stage_transition':
            updateProgressBar(item.metadata.to_stage);
            break;

        case 'interception_iteration':
            showIterationProgress(item.stage_iteration, item.content);
            break;

        case 'output_image':
            displayImage(item.file_path);
            break;

        case 'pipeline_complete':
            showCompletionMessage();
            socket.emit('unsubscribe_execution', { execution_id: executionId });
            break;
    }
});
```

---

## 7. Export API

### 7.1 Query Interface

**REST API for research data export:**

```python
# File: devserver/my_app/routes/export_routes.py

@app.route('/api/export/executions', methods=['GET'])
def list_executions():
    """List available execution records"""
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    execution_ids = list_execution_records(limit=limit, offset=offset)

    return jsonify({
        'executions': execution_ids,
        'limit': limit,
        'offset': offset
    })


@app.route('/api/export/execution/<execution_id>', methods=['GET'])
def get_execution(execution_id: str):
    """Get full execution record as JSON"""
    record = load_execution_record(execution_id)

    if not record:
        return jsonify({'error': 'Execution not found'}), 404

    return jsonify(record.to_dict())


@app.route('/api/export/execution/<execution_id>/xml', methods=['GET'])
def export_execution_xml(execution_id: str):
    """Export execution record as XML (legacy format compatible)"""
    record = load_execution_record(execution_id)

    if not record:
        return jsonify({'error': 'Execution not found'}), 404

    # Convert to legacy XML format
    xml_content = convert_to_legacy_xml(record)

    return Response(xml_content, mimetype='application/xml')


@app.route('/api/export/execution/<execution_id>/pdf', methods=['GET'])
def export_execution_pdf(execution_id: str):
    """Export execution record as PDF report"""
    record = load_execution_record(execution_id)

    if not record:
        return jsonify({'error': 'Execution not found'}), 404

    # Generate PDF from record
    pdf_bytes = generate_execution_pdf(record)

    return Response(pdf_bytes, mimetype='application/pdf')
```

### 7.2 Legacy Format Conversion

**Maintain compatibility with existing research data:**

```python
def convert_to_legacy_xml(record: ExecutionRecord) -> str:
    """
    Convert ExecutionRecord to legacy XML format

    Legacy format expected by existing research tools
    """
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom

    root = Element('session_data')

    # Metadata
    SubElement(root, 'user_id').text = record.user_id
    SubElement(root, 'session_id').text = record.session_id
    SubElement(root, 'timestamp').text = record.timestamp.isoformat()
    SubElement(root, 'workflow_name').text = record.config_name
    SubElement(root, 'safety_level').text = record.safety_level

    # Extract prompts from items
    user_input = next(
        (item.content for item in record.items if item.item_type == ItemType.USER_INPUT_TEXT),
        ''
    )
    translated_prompt = next(
        (item.content for item in record.items if item.item_type == ItemType.TRANSLATION_RESULT),
        user_input
    )

    SubElement(root, 'prompt').text = user_input
    SubElement(root, 'translated_prompt').text = translated_prompt

    # Outputs section
    outputs_elem = SubElement(root, 'outputs')

    order = 1
    for item in record.items:
        if item.item_type == ItemType.INTERCEPTION_FINAL:
            output = SubElement(outputs_elem, 'output')
            output.set('order', str(order))
            output.set('type', 'text')
            output.set('node_title', 'interception_result')
            SubElement(output, 'content').text = item.content
            order += 1

        elif item.item_type == ItemType.OUTPUT_IMAGE:
            output = SubElement(outputs_elem, 'output')
            output.set('order', str(order))
            output.set('type', 'image')
            output.set('node_title', item.config_used or 'generated_image')
            SubElement(output, 'filename').text = Path(item.file_path).name
            SubElement(output, 'path').text = item.file_path
            order += 1

    # Pretty print XML
    xml_str = tostring(root, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

**File:** `devserver/tests/test_execution_tracker.py`

```python
import pytest
from execution_history.tracker import ExecutionTracker
from execution_history.models import ItemType, MediaType


def test_tracker_initialization():
    """Test tracker initialization"""
    tracker = ExecutionTracker(
        config_name='dada',
        execution_mode='eco',
        safety_level='kids'
    )

    assert tracker.config_name == 'dada'
    assert tracker.execution_mode == 'eco'
    assert tracker.safety_level == 'kids'
    assert tracker.current_stage == 0
    assert len(tracker.items) == 0


def test_log_user_input():
    """Test logging user input"""
    tracker = ExecutionTracker('dada', 'eco', 'kids')
    tracker.set_stage(1)

    tracker.log_user_input_text("Eine Blume auf der Wiese")

    assert len(tracker.items) == 1
    item = tracker.items[0]
    assert item.sequence_number == 1
    assert item.stage == 1
    assert item.item_type == ItemType.USER_INPUT_TEXT
    assert item.content == "Eine Blume auf der Wiese"


def test_stage_iteration_context():
    """Test stage iteration tracking"""
    tracker = ExecutionTracker('stillepost', 'eco', 'kids')
    tracker.set_stage(2)

    # Log 3 iterations
    for i in range(1, 4):
        tracker.set_stage_iteration(i)
        tracker.log_interception_iteration(
            iteration_num=i,
            result_text=f"Iteration {i} result",
            from_lang='de',
            to_lang='en',
            model_used='gpt-oss:20b'
        )

    assert len(tracker.items) == 3
    assert tracker.items[0].stage_iteration == 1
    assert tracker.items[1].stage_iteration == 2
    assert tracker.items[2].stage_iteration == 3


def test_fail_safe_logging():
    """Test that logging failures don't break tracker"""
    tracker = ExecutionTracker('dada', 'eco', 'kids')
    tracker.set_stage(1)

    # This should not raise even if there's an error
    # (simulated by passing invalid data)
    try:
        tracker.log_user_input_text(None)  # Invalid: None instead of str
    except Exception:
        pytest.fail("Tracker should not raise exceptions")

    # Tracker should still be usable
    tracker.log_user_input_text("Valid text")
    assert len(tracker.items) >= 1


def test_finalize_creates_record():
    """Test finalization creates ExecutionRecord"""
    tracker = ExecutionTracker('dada', 'eco', 'kids')
    tracker.set_stage(1)
    tracker.log_user_input_text("Test")
    tracker.log_pipeline_complete(total_duration=1.5, outputs_generated=1)

    # Get record before finalize
    record = tracker.get_execution_record()

    assert record.execution_id == tracker.execution_id
    assert record.config_name == 'dada'
    assert len(record.items) == 2
```

### 8.2 Integration Tests

**File:** `devserver/tests/test_tracker_integration.py`

```python
import pytest
from schemas.engine.pipeline_executor import PipelineExecutor
from execution_history.tracker import ExecutionTracker


@pytest.mark.asyncio
async def test_full_pipeline_with_tracker():
    """Test complete pipeline execution with tracking"""
    tracker = ExecutionTracker('dada', 'eco', 'kids')
    executor = PipelineExecutor('schemas')

    # Simulate full 4-stage flow
    tracker.log_pipeline_start(input_text="Eine Blume", metadata={})

    # Stage 1
    tracker.set_stage(1)
    tracker.log_user_input_text("Eine Blume")
    tracker.log_translation_result(
        translated_text="A flower",
        from_lang='de',
        to_lang='en',
        model_used='mistral-nemo',
        execution_time=0.5
    )
    tracker.log_stage1_safety_check(
        safe=True,
        method='fast_filter',
        execution_time=0.001
    )

    # Stage 2
    tracker.set_stage(2)
    tracker.log_interception_final(
        final_text="Deconstructed floral assemblage",
        total_iterations=1,
        config_used='dada'
    )

    # Stage 3-4 (1 output)
    tracker.set_loop_iteration(1)
    tracker.set_stage(3)
    tracker.log_stage3_safety_check(
        loop_iteration=1,
        safe=True,
        method='fast_filter',
        config_used='sd35_large'
    )

    tracker.set_stage(4)
    tracker.log_output_image(
        loop_iteration=1,
        config_used='sd35_large',
        file_path='/exports/test_image.png',
        model_used='sd35_large',
        backend_used='comfyui',
        metadata={'width': 1024, 'height': 1024}
    )

    # Complete
    tracker.log_pipeline_complete(total_duration=5.0, outputs_generated=1)

    # Verify record
    record = tracker.get_execution_record()
    assert len(record.items) == 7  # start + 5 stages + complete

    # Verify stage distribution
    assert len(tracker.get_items_by_stage(1)) == 3  # input, translation, safety
    assert len(tracker.get_items_by_stage(2)) == 1  # interception final
    assert len(tracker.get_items_by_stage(3)) == 1  # safety check
    assert len(tracker.get_items_by_stage(4)) == 1  # output image
```

### 8.3 Performance Tests

**File:** `devserver/tests/test_tracker_performance.py`

```python
import pytest
import time
from execution_history.tracker import ExecutionTracker


def test_logging_performance():
    """Test that logging meets <1ms requirement"""
    tracker = ExecutionTracker('dada', 'eco', 'kids')
    tracker.set_stage(1)

    # Measure 100 log operations
    iterations = 100
    start_time = time.time()

    for i in range(iterations):
        tracker.log_user_input_text(f"Test input {i}")

    total_time = time.time() - start_time
    avg_time_ms = (total_time / iterations) * 1000

    print(f"\nAverage logging time: {avg_time_ms:.3f}ms")

    # Should be well under 1ms per operation
    assert avg_time_ms < 1.0, f"Logging too slow: {avg_time_ms:.3f}ms (target: <1ms)"


def test_overhead_on_pipeline():
    """Test total overhead on realistic pipeline execution"""
    tracker = ExecutionTracker('dada', 'eco', 'kids')

    start_time = time.time()

    # Simulate typical pipeline: 15-20 events
    tracker.log_pipeline_start(input_text="Test", metadata={})
    tracker.set_stage(1)
    tracker.log_user_input_text("Test")
    tracker.log_translation_result("Test", 'de', 'en', 'model', 0.5)
    tracker.log_stage1_safety_check(True, 'fast', 0.001)

    tracker.set_stage(2)
    tracker.log_interception_final("Transformed", 1, 'dada')

    tracker.set_stage(3)
    tracker.set_loop_iteration(1)
    tracker.log_stage3_safety_check(1, True, 'fast', 'sd35_large')

    tracker.set_stage(4)
    tracker.log_output_image(1, 'sd35_large', '/path', 'model', 'comfyui', {})

    tracker.log_pipeline_complete(5.0, 1)

    total_time_ms = (time.time() - start_time) * 1000

    print(f"\nTotal tracking overhead: {total_time_ms:.1f}ms for {len(tracker.items)} events")

    # Should be well under 100ms total
    assert total_time_ms < 100.0, f"Total overhead too high: {total_time_ms:.1f}ms (target: <100ms)"
```

---

## 9. Implementation Roadmap

### Phase 1: Core Data Structures (1-2 hours)

✅ Already completed in Session 18:
- `docs/ITEM_TYPE_TAXONOMY.md` (662 lines, v1.0 finalized)

**Next: Create Python implementations**

**Files to create:**
1. `devserver/execution_history/__init__.py`
2. `devserver/execution_history/models.py` - ExecutionItem, ExecutionRecord, Enums
3. `devserver/execution_history/tracker.py` - ExecutionTracker class (from section 4)
4. `devserver/execution_history/storage.py` - Storage service (from section 5)

### Phase 2: Integration with Orchestration (2-3 hours)

**Files to modify:**
1. `devserver/my_app/routes/schema_pipeline_routes.py`
   - Add tracker initialization
   - Pass tracker to orchestration function
   - Add finalize() call in try-finally

2. `devserver/schemas/engine/stage_orchestrator.py`
   - Add `tracker` parameter to all stage functions
   - Add tracker.log_* calls at appropriate points

### Phase 3: Export API (1-2 hours)

**Files to create:**
1. `devserver/my_app/routes/export_routes.py` - REST API for research export
2. `devserver/my_app/services/export_converter.py` - Legacy XML/PDF conversion

### Phase 4: Live UI Streaming (Optional, 2-3 hours)

**Files to create:**
1. `devserver/my_app/routes/websocket_routes.py` - WebSocket handlers
2. `devserver/public_dev/js/live-execution-viewer.js` - Frontend client

**Dependencies:**
```bash
pip install flask-socketio python-socketio
```

### Phase 5: Testing (2-3 hours)

**Files to create:**
1. `devserver/tests/test_execution_tracker.py` - Unit tests
2. `devserver/tests/test_tracker_integration.py` - Integration tests
3. `devserver/tests/test_tracker_performance.py` - Performance tests

### Phase 6: Documentation & Migration

**Files to update:**
1. `docs/DEVELOPMENT_LOG.md` - Session stats
2. `docs/devserver_todos.md` - Mark tasks complete
3. `docs/ARCHITECTURE.md` - Add execution tracking section

---

## 10. Open Questions & Decisions Needed

### Q1: Live UI Streaming - Implement Now or Later?

**Options:**
- **A) Implement in Phase 4** - Full real-time progress display
- **B) Skip for now** - Add later when UI needs it (YAGNI)
- **C) Stub implementation** - Basic WebSocket setup, no full UI

**Recommendation:** Option B (skip for now)
- Research export is primary goal (confirmed in Session 17)
- Live UI is "nice to have" but not critical for v1
- Can add later without changing tracker architecture

### Q2: Storage Format - JSON Only or Add Database?

**Options:**
- **A) JSON files only** - Simple, human-readable, no dependencies
- **B) SQLite database** - Queryable, scalable, more complex
- **C) Both** - JSON for backup, SQLite for queries

**Recommendation:** Option A (JSON only) for v1
- User has <100 executions currently
- Research doesn't need complex queries yet
- Can migrate to SQLite later without changing tracker API

### Q3: Tracker Failures - Fail-Open or Fail-Closed?

**Current Design:** Fail-Open (tracker errors logged, pipeline continues)

**Alternative:** Fail-Closed (tracker errors abort pipeline)

**Recommendation:** Keep Fail-Open
- Pedagogical pipeline execution > research tracking
- User would be upset if pipeline failed due to logging bug
- Research data is valuable but not mission-critical

### Q4: Stage Transition Events - Track or Skip?

**Decision Made in Session 18:** Track `STAGE_TRANSITION` events

**Rationale:**
- Required for live UI progress display
- DevServer knows stages internally, but UI needs events
- Adds 3-4 items per execution (acceptable overhead)

**Implementation:**
```python
def log_stage_transition(self, from_stage: int, to_stage: int):
    """Log stage transition event"""
    try:
        self._log_item(
            stage=from_stage,  # Current stage before transition
            media_type=MediaType.METADATA,
            item_type=ItemType.STAGE_TRANSITION,
            content=None,
            metadata={
                'from_stage': from_stage,
                'to_stage': to_stage,
                'transition_time_ms': 5  # Negligible
            }
        )
    except Exception as e:
        logger.warning(f"[TRACKER] Failed to log stage transition: {e}")
```

---

## 11. Success Criteria

### Must Have (v1.0)

✅ **Core Tracking**
- [ ] ExecutionTracker tracks all 20+ item types from taxonomy
- [ ] Non-blocking: <1ms per event, <100ms total overhead
- [ ] Fail-safe: Tracker errors never stall pipeline
- [ ] Stage/iteration context tracked correctly

✅ **Storage**
- [ ] JSON persistence to `exports/executions/`
- [ ] Load/save ExecutionRecord working
- [ ] Human-readable format (indented JSON)

✅ **Integration**
- [ ] Integrated with schema_pipeline_routes.py
- [ ] Integrated with stage_orchestrator.py helpers
- [ ] Stille Post (8 iterations) tracked correctly
- [ ] Multi-output loop tracked correctly

✅ **Export API**
- [ ] REST endpoint: `/api/export/execution/<id>`
- [ ] Legacy XML conversion working
- [ ] Compatible with existing research tools

✅ **Testing**
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass (full pipeline)
- [ ] Performance tests pass (<1ms, <100ms)

### Nice to Have (v2.0+)

⏳ **Advanced Features**
- [ ] Live UI WebSocket streaming
- [ ] SQLite database storage (for queries)
- [ ] PDF export generation
- [ ] Full-text search across prompts
- [ ] Aggregation queries (stats by config)

---

## 12. Related Documents

**Must Read:**
- `docs/ITEM_TYPE_TAXONOMY.md` - WHAT to track (20+ item types, v1.0 finalized)
- `docs/EXECUTION_HISTORY_UNDERSTANDING_V3.md` - WHY we need this (research context)
- `docs/SESSION_18_HANDOVER.md` - Context from previous session

**For Context:**
- `docs/ARCHITECTURE PART 01 - 4-Stage Orchestration Flow.md` - How stages work
- `devserver/schemas/engine/stage_orchestrator.py` - Current stage helpers
- `devserver/my_app/routes/schema_pipeline_routes.py` - Main orchestration

---

**Created:** 2025-11-03 Session 19
**Status:** 🚧 DRAFT v0.1 - Ready for review and implementation
**Next:** Review with user, then start Phase 1 (create models.py + tracker.py)
**Estimated Implementation Time:** 8-12 hours total (all phases)
