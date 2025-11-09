# Execution History & Research Data Export - Design Document

**Date:** 2025-11-03
**Status:** ✅ PHASE 1 COMPLETE - Core data structures implemented
**Priority:** HIGH (fixes broken research data export)
**Architecture:** **Hybrid - Stateless Pipeline + Stateful Research Tracker**

**Implementation Progress:**
- ✅ Phase 1: Core data structures (`execution_record.py`, `execution_tracker.py`)
- ⏳ Phase 2: Integration with StageOrchestrator
- ⏳ Phase 3: Research API endpoints
- ⏳ Phase 4: Frontend execution viewer

---

## Problem Statement

The current system has:
- ✅ ComfyUI `prompt_id` tracking (for media retrieval)
- ✅ `USER_INPUT` variable preservation in pipelines
- ❌ **No complete execution history** (Stage 1-4 outputs)
- ❌ **Broken research data export** (reported by user)
- ❌ **No intermediate result tracking** (translation, interception, safety checks)
- ❌ **No async/parallel execution support** for future optimization

---

## Solution: Stateful Execution Tracker (Observer Pattern)

### Core Architecture Principles

1. **Pipeline stays stateless** - Pure functions, no side effects
2. **Tracker is stateful** - Observes pipeline, tracks execution history
3. **Loose coupling** - Tracker failure doesn't break pipeline
4. **Async-ready** - Built for concurrent/parallel execution from day one
5. **Research-focused** - Enables rich analytics, session tracking, pattern analysis

### What Gets Tracked

1. **Inputs** (user text, uploaded images)
2. **All stage outputs** (translation, interception, safety, generation)
3. **Metadata** (configs used, models used, timestamps)
4. **Semantic labels** (what each item means)
5. **Sequential order** (actual execution order, including parallel stages)
6. **Sessions** (multiple executions from same user/session)
7. **Timing** (stage duration, total execution time)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Pipeline Execution (STATELESS - Pure Functions)        │
│  ├─ Stage 1: Translation (async)                        │
│  ├─ Stage 2: Interception (async)                       │
│  ├─ Stage 3: Safety (async) ────┐                       │
│  └─ Stage 4: Generation (async) ─┴─ Can run in parallel │
└─────────────────────────────────────────────────────────┘
              │
              │ (observes via log_item() calls)
              │ (non-blocking, failure-safe)
              ↓
┌─────────────────────────────────────────────────────────┐
│  ExecutionTracker (STATEFUL - In-Memory + Disk)         │
│  ├─ Active executions (in memory)                       │
│  ├─ Event queue (async, thread-safe)                    │
│  ├─ Session tracking                                    │
│  ├─ Pattern analysis                                    │
│  └─ Auto-export to disk (periodic + on completion)      │
└─────────────────────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────┐
│  Research Data Storage (Disk)                           │
│  research_data/                                         │
│  ├── executions/<execution_id>.json                     │
│  ├── sessions/<session_id>.json                         │
│  └── analytics/daily_stats.json                         │
└─────────────────────────────────────────────────────────┘
```

---

## Data Structures

### 1. Data Structures

**File:** `devserver/schemas/engine/execution_record.py` (NEW)

```python
from dataclasses import dataclass, field
from typing import List, Literal, Optional
from datetime import datetime
from pathlib import Path
import json

# Type definitions
MediaType = Literal["text", "image", "audio", "video", "3d_model", "json"]
StageType = Literal["stage1_translation", "stage1_safety", "stage2_interception",
                     "stage3_safety", "stage4_generation"]

@dataclass
class ExecutionItem:
    """Single item in execution history"""

    # Order and timing
    sequence_number: int          # 0, 1, 2... (temporal order)
    timestamp: str                # ISO format

    # Stage metadata
    stage: StageType              # Which stage produced this
    stage_step: Optional[int]     # null = single output, 1/2/3... = multiple outputs

    # Content type
    media_type: MediaType
    item_type: str                # Semantic label (see taxonomy below)

    # Data
    content: Optional[str] = None         # For text/JSON
    file_path: Optional[str] = None       # For media files

    # Context
    config_used: Optional[str] = None     # Which config (e.g., "dada")
    model_used: Optional[str] = None      # Which model (e.g., "gpt-oss:20b")
    prompt_id: Optional[str] = None       # For ComfyUI media

    # Metadata (flexible)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize for JSON export"""
        return {
            "sequence_number": self.sequence_number,
            "timestamp": self.timestamp,
            "stage": self.stage,
            "stage_step": self.stage_step,
            "media_type": self.media_type,
            "item_type": self.item_type,
            "content": self.content,
            "file_path": self.file_path,
            "config_used": self.config_used,
            "model_used": self.model_used,
            "prompt_id": self.prompt_id,
            "metadata": self.metadata
        }


@dataclass
class ExecutionRecord:
    """Complete execution history for one request"""

    # Request metadata
    execution_id: str                     # Unique ID (UUID)
    start_time: str                       # ISO format
    end_time: Optional[str] = None

    # Request parameters
    config_name: str                      # User-selected config (e.g., "dada")
    user_input: str                       # Original input text
    execution_mode: str                   # "eco" or "fast"
    safety_level: str                     # "kids" or "youth"

    # Execution history (ordered list)
    items: List[ExecutionItem] = field(default_factory=list)

    # Status
    status: Literal["running", "completed", "failed"] = "running"
    error: Optional[str] = None

    def add_item(self, item: ExecutionItem):
        """Add item to history"""
        self.items.append(item)

    def get_items_by_stage(self, stage: StageType) -> List[ExecutionItem]:
        """Get all items from a specific stage"""
        return [item for item in self.items if item.stage == stage]

    def get_items_by_type(self, item_type: str) -> List[ExecutionItem]:
        """Get all items of a specific type"""
        return [item for item in self.items if item.item_type == item_type]

    def to_dict(self) -> dict:
        """Serialize for JSON export"""
        return {
            "execution_id": self.execution_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "config_name": self.config_name,
            "user_input": self.user_input,
            "execution_mode": self.execution_mode,
            "safety_level": self.safety_level,
            "items": [item.to_dict() for item in self.items],
            "status": self.status,
            "error": self.error
        }

    def export_json(self, output_path: Path):
        """Export to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
```

---

### 2. Item Type Taxonomy

```python
# User Inputs (original from user)
USER_INPUT_TEXT = "user_input_text"           # Original text prompt
USER_INPUT_IMAGE = "user_input_image"         # Uploaded image
USER_INPUT_AUDIO = "user_input_audio"         # Uploaded audio (future)
USER_INPUT_VIDEO = "user_input_video"         # Uploaded video (future)

# Pipeline Inputs (fed into pipeline stages)
PIPELINE_INPUT_TEXT = "pipeline_input_text"   # Text fed to stage
PIPELINE_INPUT_IMAGE = "pipeline_input_image" # Image fed to stage
PIPELINE_INPUT_AUDIO = "pipeline_input_audio" # Audio fed to stage

# Stage Outputs
TRANSLATION_RESULT = "translation_result"                 # Stage 1 translation
SAFETY_CHECK_RESULT = "safety_check_result"               # Stage 1/3 safety
INTERCEPTION_RESULT = "interception_result"               # Stage 2 transformation
PRE_OUTPUT_SAFETY_CHECK = "pre_output_safety_check"       # Stage 3 safety
GENERATION_RESULT = "generation_result"                   # Stage 4 media
```

---

### 3. Integration with Export Manager

**File:** `devserver/my_app/services/export_manager.py` (EXTEND)

```python
class ExportManager:
    """Manager for session exports + execution history"""

    def __init__(self):
        self.exports_dir = EXPORTS_DIR
        self.execution_records = {}  # ← NEW: execution_id → ExecutionRecord

    # ========== NEW: Execution History Tracking ==========

    def start_execution(self, execution_id: str, config_name: str,
                       user_input: str, execution_mode: str,
                       safety_level: str) -> ExecutionRecord:
        """Initialize execution record"""
        from schemas.engine.execution_record import ExecutionRecord

        record = ExecutionRecord(
            execution_id=execution_id,
            start_time=datetime.utcnow().isoformat() + 'Z',
            config_name=config_name,
            user_input=user_input,
            execution_mode=execution_mode,
            safety_level=safety_level
        )
        self.execution_records[execution_id] = record
        return record

    def log_item(self, execution_id: str, stage: str, media_type: str,
                item_type: str, content: Optional[str] = None,
                file_path: Optional[str] = None, **kwargs):
        """Add item to execution record"""
        from schemas.engine.execution_record import ExecutionItem

        record = self.execution_records.get(execution_id)
        if not record:
            logger.warning(f"No execution record for {execution_id}")
            return

        sequence_number = len(record.items)
        item = ExecutionItem(
            sequence_number=sequence_number,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            stage=stage,
            media_type=media_type,
            item_type=item_type,
            content=content,
            file_path=file_path,
            **kwargs
        )
        record.add_item(item)

    def complete_execution(self, execution_id: str, success: bool = True,
                          error: Optional[str] = None):
        """Mark execution as complete and export"""
        record = self.execution_records.get(execution_id)
        if not record:
            return

        record.end_time = datetime.utcnow().isoformat() + 'Z'
        record.status = "completed" if success else "failed"
        record.error = error

        # Auto-export to research_data/
        self._export_execution_record(record)

    def _export_execution_record(self, record: ExecutionRecord):
        """Export record to research data directory"""
        output_dir = Path("research_data") / record.config_name
        filename = f"{record.execution_id}.json"
        record.export_json(output_dir / filename)
        logger.info(f"Exported execution record: {output_dir / filename}")

    def get_execution_record(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Get execution record by ID"""
        return self.execution_records.get(execution_id)
```

---

### 4. Integration with Stage Orchestrator

**File:** `devserver/schemas/engine/stage_orchestrator.py` (EXTEND)

Add execution tracking to each stage:

```python
from my_app.services.export_manager import export_manager

class StageOrchestrator:

    async def execute_4_stage_pipeline(self, config_name: str, user_input: str,
                                      execution_mode: str, safety_level: str):
        """Execute 4-stage pipeline with full history tracking"""

        # 1. START EXECUTION TRACKING
        execution_id = str(uuid.uuid4())
        export_manager.start_execution(
            execution_id=execution_id,
            config_name=config_name,
            user_input=user_input,
            execution_mode=execution_mode,
            safety_level=safety_level
        )

        try:
            # 2. LOG USER INPUT
            export_manager.log_item(
                execution_id=execution_id,
                stage="stage1_translation",
                media_type="text",
                item_type="user_input_text",
                content=user_input,
                metadata={
                    "detected_language": self._detect_language(user_input),
                    "is_original_input": True
                }
            )

            # 3. STAGE 1: Translation
            translated_text = await self.execute_stage1_translation(user_input)

            export_manager.log_item(
                execution_id=execution_id,
                stage="stage1_translation",
                media_type="text",
                item_type="translation_result",
                content=translated_text,
                config_used="gpt_oss_unified",
                model_used="gpt-oss:20b",
                metadata={"source_lang": "de", "target_lang": "en"}
            )

            # 4. STAGE 1: Safety Check
            safety_result = await self.execute_stage1_safety(translated_text)

            export_manager.log_item(
                execution_id=execution_id,
                stage="stage1_safety",
                media_type="json",
                item_type="safety_check_result",
                content=json.dumps(safety_result),
                config_used="gpt_oss_unified",
                model_used="gpt-oss:20b",
                metadata={"check_type": "stgb_86a"}
            )

            if not safety_result["safe"]:
                export_manager.complete_execution(execution_id, success=False,
                                                 error="Stage 1 safety check failed")
                return {"error": "Safety check failed"}

            # 5. LOG STAGE 2 INPUT
            export_manager.log_item(
                execution_id=execution_id,
                stage="stage2_interception",
                media_type="text",
                item_type="pipeline_input_text",
                content=translated_text,
                metadata={"source": "stage1_translation_result"}
            )

            # 6. STAGE 2: Interception
            interception_result = await self.execute_stage2(config_name, translated_text)

            export_manager.log_item(
                execution_id=execution_id,
                stage="stage2_interception",
                stage_step=1,
                media_type="text",
                item_type="interception_result",
                content=interception_result,
                config_used=config_name,
                model_used="llama3.2"
            )

            # 7. STAGE 3: Pre-Output Safety
            stage3_result = await self.execute_stage3_safety(interception_result, safety_level)

            export_manager.log_item(
                execution_id=execution_id,
                stage="stage3_safety",
                media_type="json",
                item_type="pre_output_safety_check",
                content=json.dumps(stage3_result),
                config_used=f"text_safety_check_{safety_level}",
                model_used="gpt-oss:20b"
            )

            # 8. LOG STAGE 4 INPUT
            export_manager.log_item(
                execution_id=execution_id,
                stage="stage4_generation",
                media_type="text",
                item_type="pipeline_input_text",
                content=stage3_result["positive_prompt"],
                metadata={"source": "stage3_safety_result"}
            )

            # 9. STAGE 4: Media Generation
            generation_result = await self.execute_stage4(
                interception_result,
                output_config="sd35_large"
            )

            export_manager.log_item(
                execution_id=execution_id,
                stage="stage4_generation",
                stage_step=1,
                media_type="image",
                item_type="generation_result",
                file_path=generation_result.file_path,
                prompt_id=generation_result.prompt_id,
                config_used="sd35_large",
                model_used="sd3.5_large",
                metadata={
                    "width": 1024,
                    "height": 1024,
                    "steps": 25,
                    "cfg": 5.5
                }
            )

            # 10. COMPLETE EXECUTION
            export_manager.complete_execution(execution_id, success=True)

            return {
                "execution_id": execution_id,
                "status": "completed",
                "media_output": generation_result
            }

        except Exception as e:
            export_manager.complete_execution(execution_id, success=False, error=str(e))
            raise
```

---

### 5. Storage Structure

```
research_data/
├── dada/
│   ├── 550e8400-e29b-41d4-a716-446655440000.json
│   ├── 661f9511-f3ac-52e5-b827-557766551111.json
│   └── ...
├── bauhaus/
│   └── ...
├── passthrough/
│   └── ...
└── stillepost/
    └── ...
```

Each JSON file contains complete execution history with all inputs, outputs, and metadata.

---

### 6. Export API Endpoints

**File:** `devserver/my_app/routes/research_routes.py` (NEW)

```python
from flask import Blueprint, jsonify, send_file
from pathlib import Path
import zipfile
from io import BytesIO

research_bp = Blueprint('research', __name__, url_prefix='/api/research')

@research_bp.route('/execution/<execution_id>', methods=['GET'])
def get_execution_history(execution_id: str):
    """Get execution history by ID"""
    # Try in-memory first
    record = export_manager.get_execution_record(execution_id)
    if record:
        return jsonify(record.to_dict())

    # Try from disk
    for config_dir in Path("research_data").iterdir():
        file_path = config_dir / f"{execution_id}.json"
        if file_path.exists():
            return send_file(file_path, mimetype='application/json')

    return {"error": "Execution not found"}, 404


@research_bp.route('/config/<config_name>/executions', methods=['GET'])
def list_config_executions(config_name: str):
    """List all executions for a config"""
    config_dir = Path("research_data") / config_name
    if not config_dir.exists():
        return {"error": "Config not found"}, 404

    executions = []
    for json_file in config_dir.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
            executions.append({
                "execution_id": data["execution_id"],
                "start_time": data["start_time"],
                "status": data["status"],
                "user_input": data["user_input"][:50] + "..."
            })

    return jsonify({"config": config_name, "executions": executions})


@research_bp.route('/config/<config_name>/export', methods=['GET'])
def export_config_data(config_name: str):
    """Export all executions for a config as ZIP"""
    config_dir = Path("research_data") / config_name
    if not config_dir.exists():
        return {"error": "Config not found"}, 404

    # Create ZIP in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for json_file in config_dir.glob("*.json"):
            zf.write(json_file, json_file.name)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{config_name}_research_data.zip'
    )
```

---

### 7. Frontend Display Controls

**Educational Transparency Levels:**

```javascript
// public_dev/js/execution-viewer.js

class ExecutionViewer {
    constructor(executionData, viewLevel = 'student') {
        this.data = executionData;
        this.viewLevel = viewLevel; // 'student', 'advanced', 'researcher'
    }

    render() {
        const container = document.getElementById('execution-history');

        switch(this.viewLevel) {
            case 'student':
                // Show only: input, final transformation, final output
                this.renderSimpleView();
                break;
            case 'advanced':
                // Show: input, translation, transformation, output
                this.renderAdvancedView();
                break;
            case 'researcher':
                // Show: EVERYTHING (all stages, all metadata)
                this.renderFullView();
                break;
        }
    }

    renderSimpleView() {
        const items = this.data.items;

        // Show user input
        const input = items.find(i => i.item_type === 'user_input_text');
        this.renderItem(input, '📝 Your Input');

        // Show interception result
        const interception = items.find(i => i.item_type === 'interception_result');
        this.renderItem(interception, `🎨 ${this.data.config_name} Transformation`);

        // Show final output
        const output = items.find(i => i.item_type === 'generation_result');
        this.renderMedia(output, '🖼️ Your Creation');
    }

    renderFullView() {
        // Show ALL items with full metadata
        this.data.items.forEach(item => {
            this.renderItemDetailed(item);
        });
    }
}
```

---

## Implementation Phases

### Phase 1: Core Data Structures ✅
- [ ] Create `execution_record.py` with data structures
- [ ] Define item type taxonomy
- [ ] Test JSON serialization

### Phase 2: Export Manager Extension ✅
- [ ] Add execution tracking to `export_manager.py`
- [ ] Implement `start_execution()`, `log_item()`, `complete_execution()`
- [ ] Test record persistence to disk

### Phase 3: Stage Orchestrator Integration ✅
- [ ] Add logging to Stage 1 (translation + safety)
- [ ] Add logging to Stage 2 (interception)
- [ ] Add logging to Stage 3 (pre-output safety)
- [ ] Add logging to Stage 4 (media generation)
- [ ] Test complete 4-stage execution

### Phase 4: API Endpoints ✅
- [ ] Create `research_routes.py`
- [ ] Implement `/api/research/execution/<id>`
- [ ] Implement `/api/research/config/<name>/executions`
- [ ] Implement `/api/research/config/<name>/export`

### Phase 5: Frontend Display ✅
- [ ] Create `execution-viewer.js`
- [ ] Implement view level switching (student/advanced/researcher)
- [ ] Add UI controls to show/hide intermediate results
- [ ] Test with real execution data

---

## Benefits

### For Students (Simple View)
```
📝 You wrote: "Eine Blume auf der Wiese"
    ↓
🎨 Dada transformed it to: "BLUME CHAOS WIESE ANTI-LOGIK"
    ↓
🖼️ [Generated image]
```

### For Advanced Students (Advanced View)
```
📝 Original: "Eine Blume auf der Wiese" (German)
🌍 Translated: "A flower on the meadow"
✅ Safety: Passed
🎨 Dada: "BLUME CHAOS WIESE ANTI-LOGIK"
✅ Content check: Passed
🖼️ [Generated image with SD3.5 Large]
```

### For Researchers (Full View)
```json
{
  "execution_id": "550e8400...",
  "config_name": "dada",
  "items": [
    {"sequence": 0, "stage": "stage1_translation", "item_type": "user_input_text", ...},
    {"sequence": 1, "stage": "stage1_translation", "item_type": "translation_result", ...},
    {"sequence": 2, "stage": "stage1_safety", "item_type": "safety_check_result", ...},
    ...
  ]
}
```

---

## Success Criteria

✅ All stage inputs and outputs are tracked
✅ Execution records export to JSON automatically
✅ Research data organized by config (dada/, bauhaus/, etc.)
✅ API endpoints for retrieving/exporting execution history
✅ Frontend can show/hide intermediate results
✅ Complete provenance: Can trace from final output → all intermediate steps → original input

---

**Created:** 2025-11-03
**Estimate:** ~4-6 hours implementation
**Status:** Ready to implement
