# Phase 3 Handover: Implement DevServer 4-Stage Orchestrator

**Date:** 2025-11-01
**Status:** Ready to start Phase 3
**Branch:** `feature/schema-architecture-v2`
**Estimated Time:** 3 hours

---

## ⚠️ IMPORTANT: Read Before Starting

**This document assumes you have read:**
- ✅ `docs/README_FIRST.md` (mandatory reading)
- ✅ `docs/ARCHITECTURE.md` Section 1 (4-Stage Flow - AUTHORITATIVE)
- ✅ `docs/IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md` Phase 3

**Current Progress:**
- ✅ Phase 1 Complete (metadata added to 49 JSON files)
- ✅ Phase 2 Complete (helper functions extracted to `stage_orchestrator.py`)
- ⏭️ **Phase 3: YOU ARE HERE** - Implement DevServer orchestrator

---

## 📋 Phase 3 Goal

**Implement NEW 4-stage orchestration in DevServer** while keeping old system working.

**Key Principle:** DevServer orchestrates (SMART), PipelineExecutor executes (DUMB).

**Strategy:**
1. Create new `execute_4_stage_flow()` function in `schema_pipeline_routes.py`
2. Add feature flag: `USE_NEW_4_STAGE_ARCHITECTURE = False`
3. Route old path → old code, new path → new function
4. Test both paths work independently
5. NO breaking changes (flag off by default)

---

## 🎯 What Phase 3 Implements

### NEW Flow (When flag = True)

```
POST /api/schema/pipeline/execute
  ↓
schema_pipeline_routes.py: execute_4_stage_flow()
  ↓
┌─ STAGE 1: Pre-Interception ─────────────────────┐
│ DevServer orchestrates (using stage_orchestrator helpers)
│ - execute_stage1_translation()
│ - execute_stage1_safety()
└──────────────────────────────────────────────────┘
  ↓
┌─ STAGE 2: Interception ──────────────────────────┐
│ PipelineExecutor.execute_pipeline() [DUMB MODE]
│ - Just executes chunks
│ - NO Stage 1-3 logic inside
│ - Returns output + output_requests
└──────────────────────────────────────────────────┘
  ↓
┌─ STAGE 3-4: For each output request ────────────┐
│ FOR EACH request in output_requests:
│   - Stage 3: execute_stage3_safety()
│   - Stage 4: execute_pipeline(output_config)
└──────────────────────────────────────────────────┘
```

### OLD Flow (When flag = False)

```
POST /api/schema/pipeline/execute
  ↓
pipeline_executor.py: execute_pipeline()
  ↓
Stage 1-3 inside PipelineExecutor (lines 308-499)
```

---

## 📁 Key Files for Phase 3

### Files to READ:

1. **`my_app/routes/schema_pipeline_routes.py`** (Main file to modify)
   - Current endpoint: `/api/schema/pipeline/execute`
   - Line ~50-150: Current request handling
   - Need to add: Feature flag + new orchestrator

2. **`schemas/engine/stage_orchestrator.py`** (Created in Phase 2)
   - Use these functions:
     - `execute_stage1_translation(text, execution_mode, pipeline_executor)`
     - `execute_stage1_safety(text, safety_level, execution_mode, pipeline_executor)`
     - `execute_stage3_safety(prompt, safety_level, media_type, execution_mode, pipeline_executor)`
     - `build_safety_message(codes, lang)`

3. **`schemas/engine/pipeline_executor.py`**
   - Understand `execute_pipeline()` signature
   - Understand `PipelineResult` structure
   - We'll add `skip_stages` parameter in Phase 4

4. **`schemas/engine/config_loader.py`**
   - Understand `get_config()` and `get_pipeline()`
   - ResolvedConfig structure

### Files to MODIFY:

1. **`my_app/routes/schema_pipeline_routes.py`**
   - Add feature flag at top
   - Create `execute_4_stage_flow()` function
   - Route based on flag

2. **`docs/DEVELOPMENT_LOG.md`**
   - Add Session 9 entry

3. **`docs/devserver_todos.md`**
   - Mark Phase 3 complete

---

## 🔧 Step-by-Step Implementation

### Step 1: Read Current Implementation

**Location:** `my_app/routes/schema_pipeline_routes.py`

```bash
# Read the current endpoint
cd /home/joerissen/ai/ai4artsed_webserver/devserver
grep -n "def execute_pipeline" my_app/routes/schema_pipeline_routes.py
```

**What to understand:**
- How requests are parsed (config_name, input_text, execution_mode, safety_level)
- How responses are built (final_output, media_output, metadata)
- Error handling patterns

### Step 2: Add Feature Flag

**Location:** `my_app/routes/schema_pipeline_routes.py` (top of file)

```python
# ============================================================================
# FEATURE FLAG: 4-Stage Architecture Refactoring
# ============================================================================
USE_NEW_4_STAGE_ARCHITECTURE = False  # Set to True to enable new flow
```

### Step 3: Create New Orchestrator Function

**Location:** `my_app/routes/schema_pipeline_routes.py` (new function)

**Template:**

```python
from schemas.engine.stage_orchestrator import (
    execute_stage1_translation,
    execute_stage1_safety,
    execute_stage3_safety,
    build_safety_message
)

async def execute_4_stage_flow(
    config_name: str,
    input_text: str,
    execution_mode: str = 'eco',
    safety_level: str = 'kids'
) -> Dict[str, Any]:
    """
    NEW: 4-Stage orchestration with DevServer as smart orchestrator

    Stage 1: Pre-Interception (Translation + Safety)
    Stage 2: Interception (Main Pipeline)
    Stage 3: Pre-Output Safety (per output request)
    Stage 4: Output (Media generation per output request)

    Returns same structure as old execute_pipeline() for API compatibility
    """

    # Load config and pipeline
    config = config_loader.get_config(config_name)
    if not config:
        return {"error": f"Config '{config_name}' not found"}

    pipeline = config_loader.get_pipeline(config.pipeline_name)
    if not pipeline:
        return {"error": f"Pipeline '{config.pipeline_name}' not found"}

    # Check if this is an output config (skip Stage 1-3 for output configs)
    is_output_config = config.meta.get('stage') == 'output'

    if is_output_config:
        # Output configs called from Stage 4 - just execute
        # (Stage 1-3 already done by main pipeline)
        result = await pipeline_executor.execute_pipeline(
            config_name,
            input_text,
            execution_mode=execution_mode,
            safety_level=safety_level
        )

        return {
            "success": result.success,
            "final_output": result.final_output,
            "metadata": result.metadata
        }

    # ====================================================================
    # STAGE 1: PRE-INTERCEPTION
    # ====================================================================
    logger.info(f"[4-STAGE-NEW] Stage 1: Pre-Interception for '{config_name}'")

    # Stage 1a: Translation
    translated_text = await execute_stage1_translation(
        input_text,
        execution_mode,
        pipeline_executor
    )

    # Stage 1b: Safety Check
    is_safe, codes = await execute_stage1_safety(
        translated_text,
        safety_level,
        execution_mode,
        pipeline_executor
    )

    if not is_safe:
        # Build error message
        error_message = build_safety_message(codes, lang='de')
        logger.warning(f"[4-STAGE-NEW] Stage 1 BLOCKED: {codes}")

        return {
            "success": False,
            "error": error_message,
            "metadata": {
                "stage": "pre_interception",
                "safety_codes": codes
            }
        }

    # ====================================================================
    # STAGE 2: INTERCEPTION (Main Pipeline)
    # ====================================================================
    logger.info(f"[4-STAGE-NEW] Stage 2: Interception (Main Pipeline)")

    result = await pipeline_executor.execute_pipeline(
        config_name,
        translated_text,
        execution_mode=execution_mode,
        safety_level=safety_level
        # TODO Phase 4: Add skip_stages=True here
    )

    if not result.success:
        return {
            "success": False,
            "error": result.error,
            "metadata": result.metadata
        }

    # ====================================================================
    # STAGE 3-4: PRE-OUTPUT + OUTPUT (If media requested)
    # ====================================================================

    # Check if config requests media output
    media_type = config.media_preferences.get('default_output') if config.media_preferences else None

    if media_type and media_type != 'text' and safety_level != 'off':
        logger.info(f"[4-STAGE-NEW] Stage 3: Pre-Output Safety for {media_type}")

        # Stage 3: Pre-Output Safety
        safety_result = await execute_stage3_safety(
            result.final_output,
            safety_level,
            media_type,
            execution_mode,
            pipeline_executor
        )

        if not safety_result['safe']:
            # Build user-friendly message
            abort_reason = safety_result.get('abort_reason', 'Content blocked by safety filter')
            error_message = f"🛡️ Sicherheitsfilter ({safety_level.upper()}):\n\n{abort_reason}\n\nℹ️ Dein Text wurde verarbeitet, aber die Bildgenerierung wurde aus Sicherheitsgründen blockiert."

            logger.warning(f"[4-STAGE-NEW] Stage 3 BLOCKED: {abort_reason}")

            return {
                "success": True,
                "final_output": f"{result.final_output}\n\n---\n\n{error_message}",
                "metadata": {
                    "stage_3_blocked": True,
                    "abort_reason": abort_reason
                }
            }

        # Stage 4: Media Generation (if Stage 3 passed)
        # TODO: Implement media generation call
        # For now, return text result
        logger.info(f"[4-STAGE-NEW] Stage 3 PASSED, Stage 4 would execute here")

    # Return result
    return {
        "success": True,
        "final_output": result.final_output,
        "metadata": result.metadata
    }
```

### Step 4: Route Based on Feature Flag

**Location:** `my_app/routes/schema_pipeline_routes.py` (in the endpoint handler)

**Find the current endpoint (probably around line 50-100):**
```python
@bp.route('/execute', methods=['POST'])
async def execute_pipeline():
    # Current implementation
```

**Modify to route based on flag:**
```python
@bp.route('/execute', methods=['POST'])
async def execute_pipeline():
    """Execute pipeline endpoint - routes to old or new implementation"""

    # Parse request
    data = await request.get_json()
    config_name = data.get('config_name')
    input_text = data.get('input_text')
    execution_mode = data.get('execution_mode', 'eco')
    safety_level = data.get('safety_level', 'kids')

    # Route based on feature flag
    if USE_NEW_4_STAGE_ARCHITECTURE:
        logger.info(f"[ROUTING] Using NEW 4-stage architecture for '{config_name}'")
        result = await execute_4_stage_flow(
            config_name,
            input_text,
            execution_mode,
            safety_level
        )
    else:
        logger.info(f"[ROUTING] Using OLD architecture for '{config_name}'")
        # OLD PATH: Use pipeline_executor directly
        pipeline_result = await pipeline_executor.execute_pipeline(
            config_name,
            input_text,
            user_input=input_text,
            execution_mode=execution_mode,
            safety_level=safety_level
        )

        result = {
            "success": pipeline_result.success,
            "final_output": pipeline_result.final_output,
            "error": pipeline_result.error if not pipeline_result.success else None,
            "metadata": pipeline_result.metadata
        }

    # Return response (same format for both paths)
    return jsonify(result)
```

### Step 5: Test Both Paths

**Test 1: OLD path (flag = False)**
```bash
# Start server
python3 server.py

# Test from another terminal
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "config_name": "dada",
    "input_text": "Eine Blume auf der Wiese",
    "execution_mode": "eco",
    "safety_level": "kids"
  }'
```

**Expected:** Should work as before (using pipeline_executor's Stage 1-3)

**Test 2: NEW path (flag = True)**
```python
# In schema_pipeline_routes.py, change:
USE_NEW_4_STAGE_ARCHITECTURE = True
```

```bash
# Restart server
python3 server.py

# Test same request
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "config_name": "dada",
    "input_text": "Eine Blume auf der Wiese",
    "execution_mode": "eco",
    "safety_level": "kids"
  }'
```

**Expected:** Should work via new orchestrator (using stage_orchestrator helpers)

**Check logs for:**
- `[4-STAGE-NEW]` messages
- Stage 1 translation
- Stage 1 safety check
- Stage 2 execution
- Stage 3 safety (if media requested)

---

## ✅ Success Criteria

Phase 3 is complete when:

1. ✅ Feature flag added to `schema_pipeline_routes.py`
2. ✅ `execute_4_stage_flow()` function created
3. ✅ Routing logic works (flag controls which path)
4. ✅ OLD path still works (flag = False)
5. ✅ NEW path works (flag = True)
6. ✅ Both paths return same response structure
7. ✅ Logs show correct orchestration
8. ✅ No breaking changes to API

**Test Coverage:**
- Text transformation config (e.g., dada)
- With safe input (should pass all stages)
- With unsafe input (should block at Stage 1)
- Output config call (should skip Stage 1-3)

---

## 🚨 Common Issues to Watch For

### Issue 1: Import Errors
**Symptom:** `ImportError: cannot import name 'execute_stage1_translation'`

**Solution:** Make sure imports at top of `schema_pipeline_routes.py`:
```python
from schemas.engine.stage_orchestrator import (
    execute_stage1_translation,
    execute_stage1_safety,
    execute_stage3_safety,
    build_safety_message
)
```

### Issue 2: PipelineExecutor Not Available
**Symptom:** `NameError: name 'pipeline_executor' is not defined`

**Solution:** Check if `pipeline_executor` is initialized in route file. Look for:
```python
from schemas.engine.pipeline_executor import PipelineExecutor
pipeline_executor = PipelineExecutor('schemas')
```

### Issue 3: Recursive Stage 1-3 Calls
**Symptom:** Logs show Stage 1 running twice, translation happening multiple times

**Cause:** Phase 4 not implemented yet - `skip_stages` parameter doesn't exist

**Solution:** Expected for Phase 3! Will be fixed in Phase 4. For now:
- OLD path: Stage 1-3 runs inside pipeline_executor (current behavior)
- NEW path: Stage 1-3 runs in DevServer, but ALSO inside pipeline_executor (redundant but not breaking)

### Issue 4: Response Format Mismatch
**Symptom:** Frontend can't parse response

**Solution:** Ensure both paths return same structure:
```python
{
    "success": bool,
    "final_output": str,
    "error": str | None,
    "metadata": dict
}
```

---

## 📊 Testing Strategy

### Manual Tests (Both Paths)

1. **Safe Text Transformation**
   - Config: dada
   - Input: "Eine Blume auf der Wiese"
   - Expected: Stage 1-2 pass, return transformed text

2. **Unsafe Input (Stage 1 Block)**
   - Config: dada
   - Input: "violent content here" (use actual unsafe term from stage1_safety_filters.json)
   - Expected: Blocked at Stage 1, error message returned

3. **Media Request (Stage 3)**
   - Config: dada (has media_preferences.default_output = "image")
   - Input: "Eine Blume"
   - Expected: Stage 1-2-3 pass, Stage 4 TODO message

4. **Output Config Direct Call**
   - Config: gpt5_image
   - Input: "A beautiful flower"
   - Expected: Skip Stage 1-3, just execute

### Automated Test Script

Create `test_phase3_integration.py`:

```python
import asyncio
import json
from schemas.engine.pipeline_executor import PipelineExecutor
from schemas.engine.config_loader import config_loader

# Test will be written after implementing execute_4_stage_flow()
# For now, focus on manual testing via curl
```

---

## 📝 Documentation Updates Required

After implementation, update:

1. **`docs/DEVELOPMENT_LOG.md`**
   - Add Session 9 entry
   - Document Phase 3 implementation
   - Include test results
   - Note any issues encountered

2. **`docs/devserver_todos.md`**
   - Mark Phase 3 complete: `[x] Phase 3 (3h): ✅ COMPLETE (2025-11-01)`

3. **`docs/ARCHITECTURE.md` (Optional)**
   - Update Section 1.6 "Implementation Status" if significant changes

---

## 🔗 Key References

**Must Read:**
- `docs/IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md` Phase 3 section (lines 250-340)
- `docs/ARCHITECTURE.md` Section 1 (4-Stage Flow)

**Helpful:**
- `schemas/engine/stage_orchestrator.py` (Phase 2 implementation)
- `test_stage_orchestrator_phase2.py` (examples of how to call helpers)

**Current State:**
- Phase 1 summary: `/tmp/phase1_summary.md`
- Phase 2 summary: `/tmp/phase2_summary.md`

---

## ⏭️ After Phase 3

**Phase 4 (1h):** Add `skip_stages` parameter to PipelineExecutor
- Prevents recursive Stage 1-3 calls
- NEW path will use `skip_stages=True` for output configs
- Fixes redundancy issue

**Phase 5 (2h):** Enable feature flag, run integration tests
- Set `USE_NEW_4_STAGE_ARCHITECTURE = True` by default
- Run full test suite
- Fix any issues

**Phase 6 (1h):** Remove old code, cleanup
- Remove lines 308-499 from pipeline_executor.py
- Remove feature flag (only new path remains)
- Final cleanup

---

## 🎯 Quick Start Commands

```bash
# Navigate to devserver
cd /home/joerissen/ai/ai4artsed_webserver/devserver

# Read current route implementation
grep -A 50 "def execute_pipeline" my_app/routes/schema_pipeline_routes.py

# Read stage_orchestrator helpers
head -100 schemas/engine/stage_orchestrator.py

# Start implementing!
# Edit: my_app/routes/schema_pipeline_routes.py
```

---

## ✅ Implementation Checklist

Use this checklist while implementing:

- [ ] Read `schema_pipeline_routes.py` current implementation
- [ ] Add feature flag `USE_NEW_4_STAGE_ARCHITECTURE = False`
- [ ] Add imports from `stage_orchestrator`
- [ ] Create `execute_4_stage_flow()` function
  - [ ] Load config and pipeline
  - [ ] Check if output config (skip Stage 1-3)
  - [ ] Stage 1a: Translation
  - [ ] Stage 1b: Safety check
  - [ ] Stage 2: Main pipeline execution
  - [ ] Stage 3: Pre-output safety (if media)
  - [ ] Stage 4: TODO placeholder
- [ ] Modify endpoint to route based on flag
- [ ] Test OLD path (flag = False)
- [ ] Test NEW path (flag = True)
- [ ] Update `DEVELOPMENT_LOG.md`
- [ ] Update `devserver_todos.md`
- [ ] Commit and push

---

**Status:** Ready to start Phase 3
**Estimated Time:** 3 hours
**Complexity:** Medium (routing + orchestration logic)

Good luck! 🚀
