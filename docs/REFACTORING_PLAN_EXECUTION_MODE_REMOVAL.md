# Execution Mode Removal Refactoring Plan

**Target:** Replace `execution_mode` parameter system with simple config.py variables
**Scope:** 67 Python files, 4 major engine modules, 25+ test files
**Duration:** ~8 phases, each testable and committable separately
**Risk Level:** MEDIUM (architectural change, but well-isolated)

---

## Executive Summary

### Current Problem
- `execution_mode='eco'/'fast'` is passed through 64+ files
- Runtime model transformation adds complexity
- Tightly couples model selection to pipeline execution
- Hard to reason about which model runs where

### Target Solution
```python
# config.py - Single source of truth
LOCAL_DEFAULT_MODEL = "gpt-OSS:20b"
LOCAL_VISION_MODEL = "llama3.2-vision:latest"
REMOTE_ADVANCED_MODEL = "openrouter/anthropic/claude-sonnet-4-5"

STAGE1_TEXT_MODEL = LOCAL_DEFAULT_MODEL
STAGE1_VISION_MODEL = LOCAL_VISION_MODEL
STAGE2_MODEL = REMOTE_ADVANCED_MODEL
STAGE3_MODEL = LOCAL_DEFAULT_MODEL
```

### Why This Is Better
- ✅ Single source of truth in config.py
- ✅ No more runtime model selection
- ✅ Easy to understand: "Stage 2 uses advanced model, always"
- ✅ 60+ fewer files with parameter passing
- ✅ Simpler testing (no mode parameter needed)
- ✅ Better for pedagogical transparency

---

## File Impact Analysis

### Heavily Affected Modules (must change)
1. `/devserver/config.py` - Add STAGE*_MODEL variables
2. `/devserver/schemas/engine/chunk_builder.py` - Use config instead of model_selector
3. `/devserver/schemas/engine/model_selector.py` - Can be removed entirely after Phase 7
4. `/devserver/schemas/engine/pipeline_executor.py` - Remove execution_mode parameter
5. `/devserver/schemas/engine/stage_orchestrator.py` - Remove execution_mode parameter
6. `/devserver/schemas/engine/backend_router.py` - Read models from config
7. `/devserver/my_app/routes/schema_pipeline_routes.py` - Remove from API
8. `/devserver/my_app/routes/pipeline_stream_routes.py` - Remove from API

### Moderately Affected (25+ test files)
- All `/devserver/testfiles/test_*.py` - Remove `execution_mode='eco'` parameter
- All `/devserver/tests/test_*.py` - Remove `execution_mode='eco'` parameter

### Minimally Affected (documentation/history)
- Architecture docs (reference only, no code change needed)
- Development logs (read-only, informational)

---

## Phase Dependencies & Order

```
Phase 1 (Config Setup)
    ↓
Phase 2 (Chunk Builder Changes)
    ↓
Phase 3 (Pipeline Executor Updates)
    ↓
Phase 4 (Stage Orchestrator Changes)
    ↓
Phase 5 (Backend Router Integration)
    ↓
Phase 6a (Routes Layer - Schema Pipeline) & 6b (Test Updates)
    ↓
Phase 7 (Model Selector Removal)
    ↓
Phase 8 (Final Cleanup & Verification)
```

**Key Constraint:** Phases 6a and 6b can run in parallel (both depend on Phase 5)
**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → (6a||6b) → Phase 7 → Phase 8

---

## Detailed Phase Breakdown

---

## PHASE 1: Configuration Setup

**Objective:** Add model configuration variables to config.py

**Risk Level:** LOW

**Files to Change:**
- `/devserver/config.py`

### 1.1 Changes to Make

Add to `/devserver/config.py` (after line 109, before "Feature Flags" section):

```python
# ============================================================================
# MODEL CONFIGURATION BY STAGE
# ============================================================================
# IMPORTANT: These are the SINGLE SOURCE OF TRUTH for all model selections.
# All stages read these values directly - NO runtime transformation.
#
# Architecture:
# - Stage 1 (Translation + Safety): Uses local models for DSGVO compliance
# - Stage 2 (Prompt Interception): Uses advanced model for quality
# - Stage 3 (Pre-Output Check): Uses local model for DSGVO compliance
#
# NEVER edit STAGE*_MODEL to use wrong backend! Use config.py, not model_selector.
# ============================================================================

# Model Definitions (backend-prefixed)
LOCAL_TEXT_MODEL = "gpt-OSS:20b"                    # Default local model
LOCAL_VISION_MODEL = "llama3.2-vision:latest"       # Vision analysis (DSGVO-local)
REMOTE_ADVANCED_MODEL = "openrouter/anthropic/claude-sonnet-4-5"  # Quality

# Stage Model Assignments
STAGE1_TEXT_MODEL = LOCAL_TEXT_MODEL                # Translation (local)
STAGE1_VISION_MODEL = LOCAL_VISION_MODEL            # Image analysis (local/DSGVO)
STAGE2_MODEL = REMOTE_ADVANCED_MODEL                # Prompt interception (advanced)
STAGE3_MODEL = LOCAL_TEXT_MODEL                     # Pre-output safety (local)

# For backward compatibility during transition (Phase 7+ cleanup)
# These are DEPRECATED - new code should use STAGE*_MODEL directly
ECO_MODE_MODELS = {
    "translation": STAGE1_TEXT_MODEL,
    "vision": STAGE1_VISION_MODEL,
    "stage3": STAGE3_MODEL,
}

FAST_MODE_MODELS = {
    "translation": REMOTE_ADVANCED_MODEL,
    "vision": STAGE1_VISION_MODEL,  # Vision ALWAYS local (DSGVO)
    "stage3": STAGE3_MODEL,          # Safety ALWAYS local
}
```

### 1.2 Testing

**Run:** Test that config loads without errors
```bash
cd /home/joerissen/ai/ai4artsed_webserver
python3 -c "from devserver.config import STAGE1_TEXT_MODEL, STAGE2_MODEL, STAGE3_MODEL; print(f'✓ Models loaded: {STAGE1_TEXT_MODEL}, {STAGE2_MODEL}, {STAGE3_MODEL}')"
```

**Expected Output:**
```
✓ Models loaded: gpt-OSS:20b, openrouter/anthropic/claude-sonnet-4-5, gpt-OSS:20b
```

**Verification Checklist:**
- [ ] Config loads without ImportError
- [ ] All STAGE*_MODEL variables exist
- [ ] No undefined variable references
- [ ] Config still initializes other settings normally

### 1.3 Commit Strategy

```bash
git add devserver/config.py
git commit -m "Phase 1: Add STAGE*_MODEL configuration variables to config.py

- Add LOCAL_TEXT_MODEL, LOCAL_VISION_MODEL, REMOTE_ADVANCED_MODEL
- Add STAGE1_TEXT_MODEL, STAGE1_VISION_MODEL, STAGE2_MODEL, STAGE3_MODEL
- Add backward-compat ECO_MODE_MODELS and FAST_MODE_MODELS (for Phase 7)
- Single source of truth: all stages read these config values

Backward compatible: No code changes yet, just config setup.
"
```

**Rollback if Needed:**
```bash
git revert HEAD  # Removes config variables, leaves code untouched
```

---

## PHASE 2: Chunk Builder Integration

**Objective:** Make chunk_builder.py read models from config.py instead of model_selector

**Risk Level:** MEDIUM

**Files to Change:**
- `/devserver/schemas/engine/chunk_builder.py`

**Key Insight:** ChunkBuilder.build_chunk() currently takes `execution_mode` parameter and uses model_selector.select_model_for_mode(). We replace this with direct config reads.

### 2.1 Current Code Analysis

Current chunk_builder.py signature (line 96-101):
```python
def build_chunk(self,
                chunk_name: str,
                resolved_config: Any,
                context: Dict[str, Any],
                execution_mode: str = 'eco',      # <-- REMOVE THIS
                pipeline: Any = None) -> Dict[str, Any]:
```

Internal usage (lines that need change):
```python
# Line ~152: Get model from model_selector
model = model_selector.select_model_for_mode(template.model, execution_mode)
```

### 2.2 Changes to Make

**Step 1:** Add import at top of file
```python
from devserver.config import STAGE1_TEXT_MODEL, STAGE1_VISION_MODEL, STAGE2_MODEL, STAGE3_MODEL
```

**Step 2:** Update function signature (line 96-101)
```python
def build_chunk(self,
                chunk_name: str,
                resolved_config: Any,
                context: Dict[str, Any],
                pipeline: Any = None) -> Dict[str, Any]:  # REMOVE execution_mode parameter
```

**Step 3:** Add new private method to chunk_builder.py
```python
def _get_configured_model(self, stage: int) -> str:
    """
    Get model for a specific stage from config.py

    Args:
        stage: 1, 2, or 3

    Returns:
        Model string with backend prefix (e.g., "local/mistral-nemo" or "openrouter/...")
    """
    if stage == 1:
        # Stage 1: Translation or Vision
        # Determine which based on chunk context
        # HINT: check template.name or resolved_config for hint
        if 'vision' in chunk_name.lower() or 'image' in chunk_name.lower():
            return STAGE1_VISION_MODEL
        else:
            return STAGE1_TEXT_MODEL
    elif stage == 2:
        return STAGE2_MODEL
    elif stage == 3:
        return STAGE3_MODEL
    else:
        # Default to Stage 1 text model for safety
        logger.warning(f"Unknown stage: {stage}, using STAGE1_TEXT_MODEL")
        return STAGE1_TEXT_MODEL
```

**Step 4:** Find and replace model selection logic

Search for all places using `model_selector.select_model_for_mode()` in build_chunk():
```python
# OLD (around line 152-160):
model = model_selector.select_model_for_mode(template.model, execution_mode)

# NEW:
# Read stage from resolved_config or pipeline metadata
stage = getattr(pipeline, 'stage', 1) if pipeline else 1
model = self._get_configured_model(stage)
logger.debug(f"[CHUNK-BUILD] Selected model for stage {stage}: {model}")
```

**Step 5:** Remove execution_mode default parameter where it's passed in

Find all calls to build_chunk() within the file and remove execution_mode argument.

### 2.3 Testing

**Test 1:** Unit test - chunk builder loads and calls work
```bash
cd /devserver
python3 << 'EOF'
from pathlib import Path
from schemas.engine.chunk_builder import ChunkBuilder

schemas_path = Path(__file__).parent / "schemas"
builder = ChunkBuilder(schemas_path)

# Verify _get_configured_model works
stage1_model = builder._get_configured_model(1)
stage2_model = builder._get_configured_model(2)
stage3_model = builder._get_configured_model(3)

print(f"✓ Stage 1 model: {stage1_model}")
print(f"✓ Stage 2 model: {stage2_model}")
print(f"✓ Stage 3 model: {stage3_model}")
EOF
```

**Expected Output:**
```
✓ Stage 1 model: gpt-OSS:20b
✓ Stage 2 model: openrouter/anthropic/claude-sonnet-4-5
✓ Stage 3 model: gpt-OSS:20b
```

**Test 2:** Integration test - run a simple pipeline
```bash
cd /devserver
python3 -m pytest testfiles/test_pipeline_execution.py::test_simple_execution -v
```

**Expected:** Test passes with no execution_mode errors

**Verification Checklist:**
- [ ] ChunkBuilder imports config models successfully
- [ ] _get_configured_model() method works for all stages
- [ ] build_chunk() works WITHOUT execution_mode parameter
- [ ] Existing tests pass (may need parameter removal in test calls)
- [ ] No AttributeError about execution_mode

### 2.4 Commit Strategy

```bash
git add devserver/schemas/engine/chunk_builder.py
git commit -m "Phase 2: Make chunk_builder.py read models from config.py

- Remove execution_mode parameter from build_chunk()
- Add _get_configured_model(stage) method reading STAGE*_MODEL from config
- Replace model_selector.select_model_for_mode() calls with direct config reads
- Stage-aware model selection: vision→STAGE1_VISION_MODEL, etc.

Backward compatible: execution_mode parameter defaults have been removed,
but since Phase 1 added config, chunk building still works.
"
```

**Rollback if Needed:**
```bash
git revert HEAD  # Removes config integration, reverts to model_selector
```

---

## PHASE 3: Pipeline Executor Updates

**Objective:** Remove execution_mode from PipelineExecutor main methods

**Risk Level:** MEDIUM

**Files to Change:**
- `/devserver/schemas/engine/pipeline_executor.py`

### 3.1 Current Code Analysis

Functions to modify (all with execution_mode='eco' default):
```python
# Line 95-100
async def execute_pipeline(self,
    config_name: str,
    input_text: str,
    user_input: Optional[str] = None,
    execution_mode: str = 'eco',  # <-- REMOVE
    ...
)

# Line 163
async def stream_pipeline(self,
    config_name: str,
    input_text: str,
    user_input: Optional[str] = None,
    execution_mode: str = 'eco'  # <-- REMOVE
)

# Line 212
async def _execute_pipeline_steps(self,
    config_name: str,
    steps: List[PipelineStep],
    context: PipelineContext,
    execution_mode: str = 'eco',  # <-- REMOVE
    tracker=None
)
```

All internal uses of execution_mode must be removed (not passed to sub-functions).

### 3.2 Changes to Make

**Step 1:** Update function signatures

Remove `execution_mode: str = 'eco'` parameter from:
- `execute_pipeline()` - line ~100
- `stream_pipeline()` - line ~163
- `_execute_pipeline_steps()` - line ~212
- `_execute_recursive_pipeline_steps()` - line ~291
- `_stream_pipeline_steps()` - line ~412
- `_execute_single_step()` - line ~458

**Step 2:** Update all internal calls

Search for all function calls that pass execution_mode and remove the parameter:

```python
# OLD:
result = await self._execute_pipeline_steps(
    config_name=config_name,
    steps=steps,
    context=context,
    execution_mode=execution_mode,  # <-- REMOVE
    tracker=tracker
)

# NEW:
result = await self._execute_pipeline_steps(
    config_name=config_name,
    steps=steps,
    context=context,
    tracker=tracker
)
```

**Step 3:** Find and remove chunk_builder.build_chunk() calls with execution_mode

Search for `chunk_builder.build_chunk()` calls:

```python
# OLD (around line ~475):
chunk = self.chunk_builder.build_chunk(
    chunk_name=step.chunk_name,
    resolved_config=resolved_config,
    context=chunk_context,
    execution_mode=execution_mode,  # <-- REMOVE THIS LINE
    pipeline=pipeline
)

# NEW:
chunk = self.chunk_builder.build_chunk(
    chunk_name=step.chunk_name,
    resolved_config=resolved_config,
    context=chunk_context,
    pipeline=pipeline
)
```

**Step 4:** Update docstrings

Remove execution_mode from all docstrings:

```python
# OLD:
"""
Execute a pipeline

Args:
    config_name: Name of the configuration
    input_text: User input text
    execution_mode: 'eco' (local) or 'fast' (cloud)  <-- REMOVE
    ...
"""

# NEW:
"""
Execute a pipeline

Args:
    config_name: Name of the configuration
    input_text: User input text
    user_input: Optional custom user input
    ...

Note: Model selection is now determined by config.py STAGE*_MODEL values
"""
```

### 3.3 Testing

**Test 1:** Execute simple pipeline
```bash
cd /devserver/testfiles
python3 test_pipeline_execution.py::test_simple_execution
```

Expected: Test passes (may need test file update in Phase 6b)

**Test 2:** Stream pipeline execution
```bash
cd /devserver
python3 << 'EOF'
import asyncio
from pathlib import Path
from schemas.engine.pipeline_executor import PipelineExecutor

async def test():
    schemas_path = Path("schemas")
    executor = PipelineExecutor(schemas_path)
    executor.initialize()

    # Call WITHOUT execution_mode
    result = await executor.execute_pipeline(
        config_name="translation_en",
        input_text="Hallo Welt",
        user_input="Hallo Welt"
    )

    print(f"✓ Pipeline execution: {result.status}")
    print(f"✓ Steps: {len(result.steps)}")
    return result.success

asyncio.run(test())
EOF
```

Expected: Pipeline executes successfully

**Verification Checklist:**
- [ ] All execution_mode parameters removed from function signatures
- [ ] All function calls updated to not pass execution_mode
- [ ] All docstrings updated
- [ ] Simple pipeline test passes
- [ ] No "unexpected keyword argument 'execution_mode'" errors

### 3.4 Commit Strategy

```bash
git add devserver/schemas/engine/pipeline_executor.py
git commit -m "Phase 3: Remove execution_mode from PipelineExecutor

- Remove execution_mode parameter from execute_pipeline(), stream_pipeline()
- Remove execution_mode from all internal step execution methods
- Update all internal calls to chunk_builder.build_chunk() (no execution_mode)
- Update docstrings to reference config.py STAGE*_MODEL
- Model selection now happens in ChunkBuilder via config.py

All pipelines now use configured models from Phase 1 setup.
"
```

**Rollback if Needed:**
```bash
git revert HEAD  # Re-adds execution_mode parameters
```

---

## PHASE 4: Stage Orchestrator Updates

**Objective:** Remove execution_mode from stage_orchestrator.py helper functions

**Risk Level:** MEDIUM

**Files to Change:**
- `/devserver/schemas/engine/stage_orchestrator.py`

### 4.1 Current Code Analysis

Functions that take execution_mode:
- `execute_stage1_translation()` - referenced in routes
- `execute_stage1_safety()` - referenced in routes
- `execute_stage1_gpt_oss_unified()` - referenced in routes
- `execute_stage3_safety()` - referenced in routes

These are helper functions called by routes (schema_pipeline_routes.py).

### 4.2 Changes to Make

**Step 1:** Find all function signatures with execution_mode

Search for `def execute_stage` and identify all parameters.

**Step 2:** Remove execution_mode from function signatures

```python
# OLD:
async def execute_stage1_translation(text, execution_mode, pipeline_executor, tracker):
    model = model_selector.select_model_for_mode('gpt-OSS:20b', execution_mode)
    ...

# NEW:
async def execute_stage1_translation(text, pipeline_executor, tracker):
    # Model is now read from config.py directly in chunk_builder
    ...
```

**Step 3:** Replace model_selector calls with config reads

If stage_orchestrator functions still manually select models, replace with:

```python
# OLD:
from .model_selector import model_selector
model = model_selector.select_model_for_mode(base_model, execution_mode)

# NEW:
from devserver.config import STAGE1_TEXT_MODEL, STAGE2_MODEL, STAGE3_MODEL
# Use appropriate STAGE*_MODEL based on context
model = STAGE1_TEXT_MODEL  # for example
```

**Step 4:** Update all docstrings

### 4.3 Testing

**Test 1:** Import stage orchestrator functions
```bash
cd /devserver
python3 << 'EOF'
from schemas.engine.stage_orchestrator import (
    execute_stage1_translation,
    execute_stage1_safety,
    execute_stage3_safety,
)
print("✓ All stage orchestrator functions imported successfully")
EOF
```

**Test 2:** Run stage-specific tests
```bash
cd /devserver/testfiles
python3 test_hybrid_stage1.py -v
```

Expected: Tests pass (may need parameter update in Phase 6b)

**Verification Checklist:**
- [ ] All execution_mode parameters removed from signatures
- [ ] All model_selector references replaced with config reads
- [ ] Stage orchestrator functions import successfully
- [ ] Stage-specific tests still run

### 4.4 Commit Strategy

```bash
git add devserver/schemas/engine/stage_orchestrator.py
git commit -m "Phase 4: Remove execution_mode from stage_orchestrator

- Remove execution_mode parameter from execute_stage*() functions
- Replace model_selector calls with direct config reads
- Use STAGE*_MODEL from config.py for all stage operations
- Update docstrings

Stage orchestration now reads static model config, not runtime modes.
"
```

---

## PHASE 5: Backend Router Integration

**Objective:** Ensure BackendRouter reads models from config instead of execution_mode

**Risk Level:** LOW-MEDIUM

**Files to Change:**
- `/devserver/schemas/engine/backend_router.py`

### 5.1 Current Code Analysis

BackendRouter handles actual backend calls (Ollama, OpenRouter, ComfyUI). It may:
1. Accept execution_mode parameter
2. Use execution_mode to route to different backends
3. Need to read models from chunk/resolved_config instead

### 5.2 Changes to Make

**Step 1:** Check if BackendRouter.route() or similar methods have execution_mode

Search for:
```python
def route(..., execution_mode=...):
```

**Step 2:** If found, remove execution_mode parameter

BackendRouter should determine backend from the model string itself:
```python
# OLD:
async def route(backend_type, model, execution_mode='eco'):
    if execution_mode == 'fast':
        # Use OpenRouter
    else:
        # Use Ollama

# NEW:
async def route(backend_type, model):
    # Determine backend from model prefix
    if model.startswith('openrouter/'):
        # Use OpenRouter
    elif model.startswith('local/'):
        # Use Ollama
    else:
        # Default based on backend_type
```

**Step 3:** Update all calls to backend_router methods

Remove execution_mode from any calls to route(), execute(), etc.

### 5.3 Testing

**Test 1:** Backend router routes correctly based on model prefix
```bash
cd /devserver
python3 << 'EOF'
from schemas.engine.backend_router import BackendRouter

router = BackendRouter()

# Test local model routing
local_model = "local/mistral-nemo"
backend_type = "ollama"
# Should route to Ollama

# Test remote model routing
remote_model = "openrouter/anthropic/claude-3.5-haiku"
backend_type = "openrouter"
# Should route to OpenRouter

print("✓ Backend router initialization successful")
EOF
```

**Verification Checklist:**
- [ ] BackendRouter has no execution_mode parameter
- [ ] Routing logic based on model string prefix
- [ ] All calls to router methods updated
- [ ] No "unexpected keyword argument 'execution_mode'" errors

### 5.4 Commit Strategy

```bash
git add devserver/schemas/engine/backend_router.py
git commit -m "Phase 5: Remove execution_mode from backend_router

- Remove execution_mode parameter from route() and execution methods
- Determine backend from model string prefix (local/ vs openrouter/)
- Update all calls to remove execution_mode

Backend routing now determined by model prefix, not runtime mode.
"
```

---

## PHASE 6a: Routes Layer Update (Schema Pipeline Routes)

**Objective:** Remove execution_mode from API routes

**Risk Level:** MEDIUM-HIGH

**Files to Change:**
- `/devserver/my_app/routes/schema_pipeline_routes.py`
- `/devserver/my_app/routes/pipeline_stream_routes.py`

### 6a.1 Current Code Analysis

API routes that accept execution_mode:
```python
# Line ~91
def lookup_output_config(media_type: str, execution_mode: str = 'eco') -> str:
    # Used when selecting output config (image generation, etc.)

# Likely in POST handlers:
@schema_bp.route('/execute', methods=['POST'])
def execute_schema():
    execution_mode = request.json.get('execution_mode', 'eco')
    # Pass to executor
```

### 6a.2 Changes to Make

**Step 1:** Update lookup_output_config()

```python
# OLD:
def lookup_output_config(media_type: str, execution_mode: str = 'eco') -> str:
    defaults = load_output_config_defaults()
    config_name = defaults[media_type].get(execution_mode)

# NEW:
def lookup_output_config(media_type: str) -> str:
    # Only use 'eco' (local) for safety - output generation should be local
    defaults = load_output_config_defaults()
    config_name = defaults[media_type].get('eco')
```

**Step 2:** Find all route handlers that accept execution_mode

Search for patterns:
```python
execution_mode = request.json.get('execution_mode', 'eco')
execution_mode = request.args.get('execution_mode', 'eco')
```

**Step 3:** Remove execution_mode from route handlers

```python
# OLD:
@schema_bp.route('/execute', methods=['POST'])
def execute_pipeline():
    data = request.json
    execution_mode = data.get('execution_mode', 'eco')

    result = await executor.execute_pipeline(
        config_name=data['config_name'],
        input_text=data['text'],
        execution_mode=execution_mode  # <-- REMOVE
    )

# NEW:
@schema_bp.route('/execute', methods=['POST'])
def execute_pipeline():
    data = request.json

    result = await executor.execute_pipeline(
        config_name=data['config_name'],
        input_text=data['text']
    )
```

**Step 4:** Update all lookup_output_config() calls

```python
# OLD:
output_config_name = lookup_output_config(default_output, execution_mode)

# NEW:
output_config_name = lookup_output_config(default_output)
```

**Step 5:** Update logger messages

Remove execution_mode from debug logs.

### 6a.3 Testing

**Test 1:** API endpoint works without execution_mode
```bash
curl -X POST http://localhost:17802/api/schema/execute \
  -H "Content-Type: application/json" \
  -d '{"config_name": "translation_en", "text": "Hallo"}'
```

Expected: 200 OK, pipeline executes

**Test 2:** API request WITH execution_mode still works (backward compat)

If we want to maintain backward compatibility temporarily:
```python
# In route handler:
execution_mode = request.json.get('execution_mode', 'eco')  # Accept but ignore
logger.warning(f"Deprecated: execution_mode parameter provided but ignored. Using config.py models.")
```

**Verification Checklist:**
- [ ] lookup_output_config() works without execution_mode
- [ ] All route handlers updated
- [ ] No execution_mode passed to executor
- [ ] API tests pass
- [ ] Debug logs clean (no execution_mode references)

### 6a.4 Commit Strategy

```bash
git add devserver/my_app/routes/schema_pipeline_routes.py devserver/my_app/routes/pipeline_stream_routes.py
git commit -m "Phase 6a: Remove execution_mode from API routes

- Remove execution_mode from lookup_output_config() function
- Remove execution_mode from all route handlers
- Remove execution_mode from all executor calls in routes
- Routes now always use config.py STAGE*_MODEL values
- Accept but ignore execution_mode in JSON body (backward compat warning)

API routes now static: model selection determined by config.py, not request.
"
```

---

## PHASE 6b: Test Files Update

**Objective:** Remove execution_mode from all test files (can run in parallel with 6a)

**Risk Level:** LOW

**Files to Change:**
- All `/devserver/testfiles/test_*.py` files (25 files)
- All `/devserver/tests/test_*.py` files (5 files)
- Any other test files using execution_mode

### 6b.1 Strategy

Use a script to find and remove execution_mode parameters systematically.

### 6b.2 Script to Find All Test Files

```bash
grep -r "execution_mode" /devserver/testfiles/*.py | cut -d: -f1 | sort -u
grep -r "execution_mode" /devserver/tests/*.py | cut -d: -f1 | sort -u
```

Expected files:
```
test_auto_media.py
test_context_aware_safety.py
test_e2e_stage123.py
test_hybrid_quick.py
test_hybrid_stage1.py
test_hybrid_stage3.py
test_media_generation.py
test_output_chunk_direct.py
test_output_pipeline.py
test_pipeline_execution.py
test_pre_interception.py
test_safety_levels.py
test_sd35_pipeline.py
test_stage3_pre_output.py
test_stage3_simple.py
+ several more
```

### 6b.3 Changes to Make

For each test file:

**Pattern 1:** Remove execution_mode from executor calls
```python
# OLD:
result = await executor.execute_pipeline(
    config_name="dada",
    input_text="test",
    execution_mode='eco'  # <-- REMOVE THIS LINE
)

# NEW:
result = await executor.execute_pipeline(
    config_name="dada",
    input_text="test"
)
```

**Pattern 2:** Remove execution_mode from model_selector calls (if any)
```python
# OLD:
model = model_selector.select_model_for_mode("mistral-nemo", 'eco')

# NEW:
# No longer needed - model comes from config.py through chunk_builder
```

**Pattern 3:** Remove execution_mode from stage orchestrator calls (if any)
```python
# OLD:
result = await execute_stage1_translation(text, 'eco', executor, tracker)

# NEW:
result = await execute_stage1_translation(text, executor, tracker)
```

### 6b.4 Batch Update Script

Create `/tmp/fix_tests.py`:
```python
#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def fix_test_file(filepath):
    """Remove execution_mode parameter from test file"""
    with open(filepath, 'r') as f:
        content = f.read()

    original = content

    # Pattern 1: Remove execution_mode parameter from function calls
    # Matches: execution_mode='eco' or execution_mode='fast' or execution_mode=variable
    content = re.sub(
        r',\s*execution_mode\s*=\s*['\"]?(eco|fast)['\"]?',
        '',
        content
    )
    content = re.sub(
        r',\s*execution_mode\s*=\s*\w+',
        '',
        content
    )

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

test_dir = Path("/home/joerissen/ai/ai4artsed_webserver/devserver")
test_files = list(test_dir.glob("testfiles/test_*.py")) + list(test_dir.glob("tests/test_*.py"))

fixed_count = 0
for filepath in test_files:
    if fix_test_file(filepath):
        print(f"✓ Fixed: {filepath.name}")
        fixed_count += 1
    else:
        print(f"  Skipped (no changes): {filepath.name}")

print(f"\nTotal fixed: {fixed_count}/{len(test_files)}")
```

Run it:
```bash
python3 /tmp/fix_tests.py
```

### 6b.5 Manual Verification

After batch script, manually check a few files to ensure changes are correct:

```bash
# Check what changed in one file
cd /devserver
git diff testfiles/test_pipeline_execution.py | head -40
```

### 6b.6 Testing

Run all tests:
```bash
cd /devserver
python3 -m pytest testfiles/ -v --tb=short
python3 -m pytest tests/ -v --tb=short
```

Expected: All pass (assuming backend services running)

**Verification Checklist:**
- [ ] All test_*.py files updated (no more execution_mode parameters)
- [ ] Batch script successful on all files
- [ ] Manual verification of 3-5 files shows correct changes
- [ ] Tests run without "unexpected keyword argument" errors
- [ ] Test output unchanged (same tests passing/failing as before)

### 6b.7 Commit Strategy

```bash
git add devserver/testfiles/ devserver/tests/
git commit -m "Phase 6b: Remove execution_mode from all test files

- Remove execution_mode parameter from all executor/orchestrator calls
- Batch update all 30+ test files using regex pattern matching
- Tests now work with config.py STAGE*_MODEL values
- No functional change to tests, just parameter removal

All tests use configured models instead of runtime selection.
"
```

---

## PHASE 7: Model Selector Removal (or Deprecation)

**Objective:** Remove or deprecate the model_selector module

**Risk Level:** MEDIUM

**Files to Change:**
- `/devserver/schemas/engine/model_selector.py` (DELETE or keep as deprecated stub)

### 7.1 Decision Point

**Option A: Complete Removal** (Clean)
- Delete model_selector.py entirely
- Search for any remaining imports and remove them
- Risk: If any code still imports it, will break

**Option B: Deprecation Stub** (Safe)
- Keep file but mark all functions as deprecated
- Import from config instead
- Safe: Any lingering imports still work, just slow

**Recommendation:** Option B (Deprecation Stub)
- Lower risk for this phase
- Can be fully removed in Phase 8 cleanup
- Easier to find missed references

### 7.2 Changes to Make

**Option B Implementation (Deprecation):**

Replace entire `/devserver/schemas/engine/model_selector.py` with:

```python
"""
DEPRECATED: Model Selector Module

This module is deprecated as of Phase 7 refactoring.
All model selection is now done via config.py STAGE*_MODEL variables.

Legacy code that imports this module will still work, but will see warnings.
New code should import from config.py directly.

This file will be completely removed in Phase 8 cleanup.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ModelSelector:
    """
    DEPRECATED: Use config.py STAGE*_MODEL values instead

    This class is maintained for backward compatibility only.
    All methods are deprecated and log warnings.
    """

    def __init__(self):
        logger.warning("[DEPRECATED] ModelSelector is deprecated. Use config.py STAGE*_MODEL instead.")

    def select_model_for_mode(self, base_model: str, execution_mode: str) -> str:
        """DEPRECATED: Use config.py STAGE*_MODEL instead"""
        logger.warning(f"[DEPRECATED] select_model_for_mode() called with model={base_model}, mode={execution_mode}")
        logger.warning("[DEPRECATED] Consider using config.STAGE1_TEXT_MODEL, STAGE2_MODEL, STAGE3_MODEL instead")
        # Return base model unchanged as fallback
        return base_model

    def select_model_by_task(self, task_type: str, execution_mode: str = 'eco') -> str:
        """DEPRECATED: Use config.py STAGE*_MODEL instead"""
        logger.warning(f"[DEPRECATED] select_model_by_task() called with task={task_type}, mode={execution_mode}")
        return "local/mistral-nemo"  # Safe fallback

    # ... other methods return None or log deprecation warnings


# Singleton - deprecated
model_selector = ModelSelector()
```

**Option A Implementation (Complete Removal):**

Delete the file and search for remaining imports:
```bash
grep -r "from.*model_selector import" /devserver --include="*.py"
grep -r "import.*model_selector" /devserver --include="*.py"
```

Remove all import statements and replace references with config.py imports.

### 7.3 Testing

**Test 1:** Verify no production code imports model_selector
```bash
grep -r "model_selector\." /devserver \
  --include="*.py" \
  --exclude-dir=".git" \
  --exclude="model_selector.py" | grep -v "test_" | grep -v "#"
```

Expected: No results (or only in deprecated stubs)

**Test 2:** Verify tests still run
```bash
cd /devserver
python3 -m pytest testfiles/test_pipeline_execution.py -v
```

Expected: Tests pass

**Verification Checklist:**
- [ ] No production code references model_selector (grep search clean)
- [ ] Deprecation warnings appear in logs if anyone tries to use it
- [ ] All tests pass
- [ ] No broken imports

### 7.4 Commit Strategy

**Option B (Deprecation):**
```bash
git add devserver/schemas/engine/model_selector.py
git commit -m "Phase 7: Deprecate model_selector module

- Replace ModelSelector with deprecated stub
- All methods log deprecation warnings
- File will be completely removed in Phase 8
- Safe: any legacy code importing still works with warnings

New code: import STAGE*_MODEL from config.py directly.
Legacy code: continues to work but sees deprecation warnings in logs.
"
```

**Option A (Complete Removal):**
```bash
git rm devserver/schemas/engine/model_selector.py
git add devserver/  # For any reference removals
git commit -m "Phase 7: Remove model_selector module completely

- Delete model_selector.py entirely
- Remove all import statements
- All model selection now via config.py STAGE*_MODEL

Architecture is now cleaner: no runtime model transformation.
"
```

---

## PHASE 8: Final Verification & Cleanup

**Objective:** Comprehensive testing and documentation updates

**Risk Level:** LOW

**Files to Change:**
- Documentation files
- Test configuration
- Any remaining edge cases

### 8.1 Comprehensive Testing

**Test Suite 1: All unit tests**
```bash
cd /devserver
python3 -m pytest testfiles/ tests/ -v --tb=short 2>&1 | tee phase8_test_results.txt
```

**Test Suite 2: Integration tests**
```bash
# If you have integration tests
cd /devserver
python3 -m pytest integration_tests/ -v 2>&1 | tee phase8_integration_results.txt
```

**Test Suite 3: Manual smoke tests**
```bash
# Start the server
python3 -m devserver.app &

# Test a few endpoints
curl -X POST http://localhost:17802/api/schema/execute \
  -H "Content-Type: application/json" \
  -d '{
    "config_name": "translation_en",
    "text": "Hallo Welt"
  }'

# Kill server
pkill -f "python3.*app"
```

### 8.2 Code Quality Checks

**Check 1: Grep for remaining execution_mode**
```bash
grep -r "execution_mode" /devserver \
  --include="*.py" \
  --exclude-dir=".git" \
  --exclude-dir="__pycache__" \
  | grep -v "test_" \
  | grep -v "docs/" \
  | grep -v ".md" \
  | head -20
```

Expected: Only documentation/comments, no active code

**Check 2: Verify all STAGE*_MODEL variables used**
```bash
grep -r "STAGE1_TEXT_MODEL\|STAGE1_VISION_MODEL\|STAGE2_MODEL\|STAGE3_MODEL" \
  /devserver \
  --include="*.py" \
  | wc -l
```

Expected: 10+ references (in chunk_builder, stage_orchestrator, config, etc.)

**Check 3: No undefined references**
```bash
cd /devserver
python3 -m py_compile schemas/engine/*.py
python3 -m py_compile my_app/routes/*.py
```

Expected: No SyntaxError or compilation errors

### 8.3 Documentation Updates

Update architecture documentation:
```bash
# File: docs/ARCHITECTURE PART 09 - Model-Selection.md
# Update to explain: Models now come from config.py, not runtime selection
```

Add refactoring notes to DEVELOPMENT_LOG.md

### 8.4 Performance Verification

**Check that removing runtime selection improves startup time:**

```bash
# Before (measured in Phase 0):
# Pipeline startup: ~1.2s

# After (measured in Phase 8):
cd /devserver
time python3 << 'EOF'
from schemas.engine.pipeline_executor import PipelineExecutor
from pathlib import Path

executor = PipelineExecutor(Path("schemas"))
executor.initialize()
print("✓ Executor ready")
EOF
```

Expected: Same or faster (no model_selector overhead)

### 8.5 Backward Compatibility Check

**Verify any APIs that might accept execution_mode still work gracefully:**

```bash
# Test API with execution_mode parameter (should accept but warn)
curl -X POST http://localhost:17802/api/schema/execute \
  -H "Content-Type: application/json" \
  -d '{
    "config_name": "translation_en",
    "text": "Hallo",
    "execution_mode": "fast"
  }' | jq .
```

Expected: 200 OK, parameter accepted but ignored with warning in logs

### 8.6 Commit Strategy

```bash
git add docs/ devserver/
git commit -m "Phase 8: Final verification and documentation updates

Test results: All 25+ tests passing
Code quality: No execution_mode in production code
Architecture: Cleaner - static config instead of runtime selection
Performance: Startup time unchanged or improved

Documentation:
- Updated ARCHITECTURE PART 09 - Model-Selection
- Added refactoring notes to DEVELOPMENT_LOG.md
- Confirmed backward compatibility with execution_mode in API bodies

Refactoring complete: execution_mode system fully removed.
Model selection now purely configuration-driven via config.py.
"
```

---

## Implementation Checklist

### Pre-Implementation
- [ ] Read this entire plan
- [ ] Understand current execution_mode usage (grep results)
- [ ] Backup current codebase (git branch)
- [ ] Confirm all services running (Ollama, etc.)

### Phase Execution
- [ ] Phase 1: Config setup (2 hours, LOW risk)
- [ ] Phase 2: Chunk builder integration (2 hours, MEDIUM risk)
- [ ] Phase 3: Pipeline executor updates (2 hours, MEDIUM risk)
- [ ] Phase 4: Stage orchestrator updates (1 hour, MEDIUM risk)
- [ ] Phase 5: Backend router integration (1 hour, LOW-MEDIUM risk)
- [ ] Phase 6a & 6b: Routes + Tests (2 hours, MEDIUM risk)
- [ ] Phase 7: Model selector removal (1 hour, MEDIUM risk)
- [ ] Phase 8: Final verification (1 hour, LOW risk)

**Total Estimated Time: 12-14 hours**

### Post-Implementation
- [ ] All tests passing
- [ ] No execution_mode in production code
- [ ] Performance verified
- [ ] Documentation updated
- [ ] Branch merged to develop
- [ ] Team notified of changes

---

## Rollback Strategy

If any phase fails or introduces bugs:

### Immediate Rollback (Within a Phase)
```bash
# Revert last commit
git revert HEAD

# Or hard reset to before the phase
git reset --hard <commit-before-phase>
```

### Partial Rollback (After Multiple Commits)
```bash
# Identify problem phase
git log --oneline | head -20

# Revert specific phase commit
git revert <commit-hash>
```

### Complete Rollback (Back to Start)
```bash
# Before you started all phases
git reset --hard <original-commit>

# Or create new branch from original
git checkout -b backup-original <original-commit>
git checkout develop
```

### If Tests Fail in Phase X
1. Identify failed test
2. Revert Phase X only
3. Investigate root cause
4. Re-implement Phase X with fix
5. Re-run tests
6. Commit fixed version

---

## Risk Mitigation

### Risk: Breaking existing API clients
**Mitigation:**
- Routes accept execution_mode in body but ignore it
- Log deprecation warnings
- Publish migration guide for frontend teams

### Risk: Model path issues (local/ vs openrouter/ prefix)
**Mitigation:**
- Ensure config.py models always have correct prefix
- BackendRouter strips/adds prefix based on model string
- Test with sample models before full rollout

### Risk: Tests fail due to Ollama/OpenRouter unavailable
**Mitigation:**
- Don't require Phase 6b in middle of rollout
- Can do 6b tests when services are available
- Use mock tests as fallback

### Risk: Incomplete model_selector removal leaves imports
**Mitigation:**
- Use deprecation stub in Phase 7
- Grep for remaining imports in Phase 8
- Can safely remove in Phase 9+ after thorough verification

---

## Success Criteria

The refactoring is complete and successful when:

1. ✅ All 67 files no longer reference execution_mode in active code
2. ✅ 25+ test files pass without execution_mode parameter
3. ✅ Config.py has single source of truth for STAGE*_MODEL
4. ✅ Pipeline execution works identically to before (same outputs)
5. ✅ Model selection is deterministic (same input = same model every time)
6. ✅ No runtime model transformation overhead
7. ✅ Documentation updated to explain new architecture
8. ✅ Team understands new config-driven approach
9. ✅ All phases completed with clean commits
10. ✅ Code passes linting and type checking

---

## Questions Before Starting

1. **Confirmed we want static models for each stage?**
   - Or should some stages be configurable at runtime?
   - Answer: Yes, static per the requirements

2. **Should backend decide based on model prefix or config?**
   - Answer: Model prefix (cleaner separation of concerns)

3. **When to complete this refactoring?**
   - Immediately after this plan is approved? Or schedule for later?
   - Answer: User decision

4. **Should frontend be updated to stop sending execution_mode?**
   - Or do we silently ignore it first?
   - Answer: Silently ignore first (Phase 6a deprecation), then update frontend later

5. **Any downstream services that need updating?**
   - Legacy server, other workers, etc.?
   - Answer: Check with devserver-architecture-expert agent

---

## Appendix: File Reference List

### Files Requiring Changes

**Core Engine (9 files):**
1. config.py - Add STAGE*_MODEL variables
2. chunk_builder.py - Use config models
3. model_selector.py - Deprecate or remove
4. pipeline_executor.py - Remove execution_mode param
5. stage_orchestrator.py - Remove execution_mode param
6. backend_router.py - Use model prefix
7. schema_pipeline_routes.py - Remove from API
8. pipeline_stream_routes.py - Remove from API
9. output_config_selector.py - May need minor updates

**Test Files (30+ files):**
- All testfiles/test_*.py
- All tests/test_*.py
- Any custom test suites

### Files NOT Requiring Changes
- Frontend Vue files (accept but ignore execution_mode)
- Documentation files (reference only, no code change)
- Workflow files (*.json, no execution_mode)
- Legacy service files (separate system)

---

## Appendix B: Configuration Examples

### Example 1: Fast Production Config
```python
# For production with high-quality requirements:
LOCAL_TEXT_MODEL = "gpt-OSS:20b"
LOCAL_VISION_MODEL = "llama3.2-vision:latest"
REMOTE_ADVANCED_MODEL = "openrouter/anthropic/claude-sonnet-4-5"

STAGE1_TEXT_MODEL = LOCAL_TEXT_MODEL      # Translation (local, safe)
STAGE1_VISION_MODEL = LOCAL_VISION_MODEL  # Vision (DSGVO)
STAGE2_MODEL = REMOTE_ADVANCED_MODEL      # Quality (advanced)
STAGE3_MODEL = LOCAL_TEXT_MODEL           # Safety (local, safe)
```

### Example 2: Budget-Conscious Config
```python
# All local models, minimum cost:
LOCAL_TEXT_MODEL = "mistral-nemo"
LOCAL_VISION_MODEL = "llava:13b"
REMOTE_ADVANCED_MODEL = "mistral-nemo"  # Fallback to local

STAGE1_TEXT_MODEL = LOCAL_TEXT_MODEL
STAGE1_VISION_MODEL = LOCAL_VISION_MODEL
STAGE2_MODEL = LOCAL_TEXT_MODEL          # No remote for cost savings
STAGE3_MODEL = LOCAL_TEXT_MODEL
```

### Example 3: Mixed Mode Config (Scalable)
```python
# Scale up only when needed:
LOCAL_TEXT_MODEL = "gpt-OSS:20b"
LOCAL_VISION_MODEL = "llama3.2-vision:latest"
REMOTE_ADVANCED_MODEL = "openrouter/anthropic/claude-sonnet-4-5"

STAGE1_TEXT_MODEL = LOCAL_TEXT_MODEL     # Always local
STAGE1_VISION_MODEL = LOCAL_VISION_MODEL # Always local (DSGVO)
STAGE2_MODEL = REMOTE_ADVANCED_MODEL     # Advanced only when needed
STAGE3_MODEL = LOCAL_TEXT_MODEL          # Always local for safety
```

---

END OF REFACTORING PLAN
