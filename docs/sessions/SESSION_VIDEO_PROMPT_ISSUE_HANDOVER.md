# Video Prompt Injection Issue - Session Handover

**Date**: 2025-11-26
**Status**: ✅ FIXED in Session 72
**Branch**: `develop`
**Resolution**: See `SESSION_72_VIDEO_PROMPT_FIX.md`

---

## ✅ SOLUTION (Session 72)

**Root Cause**: Legacy workflows bypassed `_apply_input_mappings()`, leaving prompts empty.

**Fix**: Modified `backend_router.py:656-669` to call `_apply_input_mappings()` before service execution - same as standard workflows.

**Details**: See `SESSION_72_VIDEO_PROMPT_FIX.md` for complete technical explanation and architecture update.

---

## ORIGINAL BUG REPORT (Historical Reference)

---

## Problem Summary

Videos generated with LTX-Video workflow always show the same deterministic scene regardless of user input prompt.

### Symptoms
- User inputs custom prompt (e.g., "Ein rotes Auto fährt durch einen Wald")
- Stage 2/3 transform and translate correctly
- Generated video shows generic scene with no relation to prompt
- Videos vary when regenerated (after seed fix) but content is random, not prompt-based

---

## Root Cause Analysis

### What We Discovered

1. **Workflow Archive Evidence**
   - Node 6 (`CLIP Text Encode (Positive Prompt)`) has `"text": ""` ← **EMPTY**
   - Node 72 (`SamplerCustom`) had `"noise_seed": 123456789` ← **FIXED** (now randomized)
   - Located: `/exports/json/{run_id}/08_workflow_archive.json`

2. **Legacy Workflow Architecture**
   - File: `/devserver/schemas/engine/backend_router.py:624-689`
   - Function: `_process_legacy_workflow()`
   - Current flow:
     ```python
     workflow = chunk.get('workflow')  # Get raw workflow
     # [MISSING: input_mappings processing]
     service.execute_workflow(workflow, prompt, chunk_config)  # Legacy injection
     ```

3. **The Disconnect**
   - `output_video_ltx.json` defines: `"source": "{{PREVIOUS_OUTPUT}}"`
   - This should replace with Stage 3 translated prompt
   - BUT: Legacy workflows skip `_apply_input_mappings()` entirely
   - Standard workflows call `_apply_input_mappings()` ✅
   - Legacy workflows bypass it ❌

4. **Empirical Testing**
   - Deleted SwarmUI template → Same generic video generated
   - Confirmed template not involved
   - Seed randomization works after fix
   - Videos vary but remain prompt-agnostic

---

## What We Fixed

### Partial Solution: Seed Randomization

**File**: `/devserver/schemas/engine/backend_router.py:656-676`

```python
# Apply seed randomization from input_mappings (but not prompt)
input_mappings = chunk.get('input_mappings', {})
if input_mappings and 'seed' in input_mappings:
    import random
    seed_mapping = input_mappings['seed']
    seed_value = parameters.get('seed', seed_mapping.get('default', 'random'))

    if seed_value == 'random' or seed_value == -1:
        seed_value = random.randint(0, 2**32 - 1)
        logger.info(f"[LEGACY-WORKFLOW] Generated random seed: {seed_value}")

    # Inject seed into workflow
    seed_node_id = seed_mapping.get('node_id')
    seed_field = seed_mapping.get('field', 'inputs.noise_seed')
    if seed_node_id and seed_node_id in workflow:
        field_parts = seed_field.split('.')
        target = workflow[seed_node_id]
        for part in field_parts[:-1]:
            target = target.setdefault(part, {})
        target[field_parts[-1]] = seed_value
```

**Result**:
- ✅ Videos now vary with each generation
- ❌ Videos still ignore user prompts

---

## What Didn't Work

### Attempted Solution: Full input_mappings Processing

We tried applying `_apply_input_mappings()` in `_process_legacy_workflow()`:

```python
# ATTEMPTED FIX (FAILED)
input_data = {'prompt': prompt, **parameters}
workflow, generated_seed = self._apply_input_mappings(
    workflow,
    input_mappings,
    input_data
)
```

**Why It Failed:**
1. Seed randomization worked ✅
2. `{{PREVIOUS_OUTPUT}}` was replaced
3. BUT: Videos had NO connection to prompts whatsoever
4. Possible causes:
   - `prompt` parameter to `_process_legacy_workflow()` is empty?
   - input_mappings conflicts with legacy service's title-based injection?
   - Prompt from Stage 3 not reaching this point?
   - Node structure changed after mappings, breaking legacy injection?

---

## Critical Files

### Backend
- `/devserver/schemas/engine/backend_router.py:624-689` - `_process_legacy_workflow()`
- `/devserver/my_app/services/legacy_workflow_service.py:35-96` - `execute_workflow()`
- `/devserver/my_app/services/legacy_workflow_service.py:123-186` - `_inject_prompt()`

### Configuration
- `/devserver/schemas/chunks/output_video_ltx.json` - Video workflow chunk
- `/devserver/schemas/configs/output/ltx_video.json` - Video output config

### Evidence
- `/exports/json/{run_id}/08_workflow_archive.json` - Shows empty prompt in Node 6
- `/exports/json/{run_id}/06_interception.txt` - Stage 2 transformed prompt
- `/exports/json/{run_id}/04_stage1_output.txt` - Stage 3 translated prompt

---

## Debug Strategy for Next Session

### Step 1: Verify Prompt Flow
```python
# Add logging in backend_router.py:_process_legacy_workflow()
logger.info(f"[DEBUG] prompt parameter: '{prompt[:200]}...'")
logger.info(f"[DEBUG] parameters: {parameters}")
```

### Step 2: Check input_data
```python
# When building input_data for mappings
input_data = {'prompt': prompt, **parameters}
logger.info(f"[DEBUG] input_data['prompt']: '{input_data.get('prompt', '')[:200]}...'")
```

### Step 3: Verify {{PREVIOUS_OUTPUT}} Replacement
```python
# In _apply_input_mappings() around line 1207
if source == '{{PREVIOUS_OUTPUT}}':
    value = input_data.get('prompt', '')
    logger.info(f"[DEBUG] Replacing {{{{PREVIOUS_OUTPUT}}}} with: '{value[:200]}...'")
```

### Step 4: Check Legacy Service Injection
```python
# In legacy_workflow_service.py:_inject_prompt() around line 166
logger.info(f"[DEBUG] Injecting into Node {node_id}: '{prompt[:200]}...'")
logger.info(f"[DEBUG] Node before: {node_data['inputs']}")
# ... injection ...
logger.info(f"[DEBUG] Node after: {node_data['inputs']}")
```

---

## Hypotheses to Test

### Hypothesis 1: Prompt Parameter is Empty
**Test**: Add logging to verify `prompt` parameter value at function entry
**If True**: Trace back through pipeline_executor to find where prompt is lost

### Hypothesis 2: input_mappings Overwrites Legacy Injection
**Test**: Check order of operations - does input_mappings run before or after legacy injection?
**If True**: Modify order or skip prompt mapping in input_mappings

### Hypothesis 3: Stage 3 Output Not Reaching Stage 4
**Test**: Check pipeline_executor's handoff between stages
**If True**: Fix stage transition in pipeline orchestration

### Hypothesis 4: {{PREVIOUS_OUTPUT}} Resolves to Empty
**Test**: Verify `input_data.get('prompt')` actually contains Stage 3 output
**If True**: Check how `input_data` is built from `parameters`

---

## Current Status

### Working
✅ Seed randomization enables video variation
✅ Videos are different each generation
✅ No more deterministic "woman with long brown hair" scene

### Broken
❌ User prompts completely ignored
❌ Videos show random content unrelated to input
❌ `{{PREVIOUS_OUTPUT}}` replacement mechanism unclear

---

## Next Steps

1. **Instrument Code**: Add comprehensive logging at all prompt handoff points
2. **Trace Prompt Flow**: Follow prompt from Stage 3 → Stage 4 → Legacy Service
3. **Test Isolation**:
   - Does legacy title-based injection work alone?
   - Does input_mappings prompt replacement work alone?
   - Do they conflict when both run?
4. **Compare with Images**: Image workflows work - what's different?

---

## Questions to Answer

1. What is the actual value of `prompt` parameter in `_process_legacy_workflow()`?
2. Where does this `prompt` come from in the call chain?
3. Does `parameters` dict contain the Stage 3 output?
4. Why did full input_mappings processing break prompt injection?
5. Does legacy service's `_inject_prompt()` even receive a non-empty prompt?

---

## References

### Logs Showing Issue
```
[LEGACY-INJECT] ✓ Injected prompt into node 6.inputs.text (title match)
[LEGACY-INJECT] ✓ Prompt preview: '...'  ← EMPTY!
```

### Successful Image Workflow Pattern
Standard image chunks successfully use:
```python
workflow, generated_seed = self._apply_input_mappings(workflow, input_mappings, input_data)
# Works for images! Why not videos?
```

### Architecture Notes
- DevServer = Smart Orchestrator
- PipelineExecutor = Dumb Engine
- Backend Router = Stage 4 Handler
- Legacy Service = ComfyUI Communication

---

**Status**: Ready for next debugging session with improved instrumentation strategy.
