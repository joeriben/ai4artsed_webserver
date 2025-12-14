# Handover: Split and Combine - Parameter Propagation Bug
**Date:** 2025-12-14 18:11
**Session:** Parameter propagation investigation
**Status:** BUG IDENTIFIED - Parameters lost in transit

---

## Executive Summary

**Problem:** The `element1`, `element2`, and `combination_type` parameters are NOT reaching `_process_legacy_workflow()`, even though the frontend sends them correctly.

**Evidence from Logs:**
```
[DEBUG-PROMPT] Received parameters: ['output_chunk', 'prompt', 'OUTPUT_CHUNK', 'seed']
```

**Expected parameters:**
```
['output_chunk', 'prompt', 'OUTPUT_CHUNK', 'seed', 'element1', 'element2', 'combination_type']
```

**Status:** The input_mappings fix works, but it has no data to map because the parameters are filtered out earlier in the call chain.

---

## What Works

1. ✅ **Workflow simplified** - 27 nodes → 20 nodes
2. ✅ **input_mappings defined** in chunk - element1 → 43, element2 → 137, combination_type → 133/134
3. ✅ **Backend router fix** - Calls `_apply_input_mappings()` for legacy workflows
4. ✅ **LIST format support** - `_apply_input_mappings()` handles multi-node injection
5. ✅ **Frontend sends correctly** - element1, element2, combination_type are in the POST request

---

## What's Broken

**Symptom:**
```python
# Backend log shows this:
[LEGACY-WORKFLOW] Applying input_mappings for: ['combination_type', 'element1', 'element2']
[DEBUG-PROMPT] Received parameters: ['output_chunk', 'prompt', 'OUTPUT_CHUNK', 'seed']
```

**Root Cause:**
The parameters dict passed to `_process_legacy_workflow(chunk, prompt, parameters)` is MISSING the custom parameters (element1, element2, combination_type).

**Where the parameters are lost:**
Unknown - need to trace the call chain from the API endpoint to `_process_legacy_workflow()`.

---

## Investigation Trail

### Files Modified (3 Commits)

1. **Commit 8be2e69** - `devserver/schemas/chunks/legacy_split_and_combine.json`
   - Replaced workflow with simplified version
   - Added input_mappings for element1, element2, combination_type

2. **Commit d6a200f** - `devserver/schemas/engine/backend_router.py:718-725`
   - Added call to `_apply_input_mappings()` in `_process_legacy_workflow()`

3. **Commit f6c18cf** - `devserver/schemas/engine/backend_router.py:1367-1433`
   - Updated `_apply_input_mappings()` to support LIST format

### Call Chain (Partial - NEEDS COMPLETION)

1. **Frontend POST:** `element1`, `element2`, `combination_type`, `seed`, `input_text` → `/api/schema/pipeline/execute`
2. **Route Handler:** ??? (file unknown)
3. **Pipeline Executor:** ??? (execution flow unknown)
4. **output_legacy Chunk:** `devserver/schemas/chunks/output_legacy.json`
   - Type: `proxy_chunk`
   - Parameters defined: `{"output_chunk": "{{OUTPUT_CHUNK}}", "prompt": "{{PREVIOUS_OUTPUT}}"}`
   - **CRITICAL:** Only passes `output_chunk` and `prompt` - NO custom parameters!
5. **Backend Router:** `_process_output_chunk()` → calls → `_process_legacy_workflow(chunk, text_prompt, parameters)`
6. **Parameters received:** ONLY `['output_chunk', 'prompt', 'OUTPUT_CHUNK', 'seed']`

---

## The Likely Culprit

**File:** `devserver/schemas/chunks/output_legacy.json`

**Lines 11-14:**
```json
"parameters": {
  "output_chunk": "{{OUTPUT_CHUNK}}",
  "prompt": "{{PREVIOUS_OUTPUT}}"
}
```

**Issue:** This proxy chunk ONLY forwards `output_chunk` and `prompt`. It does NOT forward custom parameters like `element1`, `element2`, `combination_type`.

**Hypothesis:** The chunk executor replaces the full parameter set with ONLY the parameters defined in the chunk's `parameters` field, filtering out everything else.

---

## Possible Solutions

### Option 1: Update output_legacy.json to forward all parameters
```json
"parameters": {
  "output_chunk": "{{OUTPUT_CHUNK}}",
  "prompt": "{{PREVIOUS_OUTPUT}}",
  "element1": "{{element1}}",
  "element2": "{{element2}}",
  "combination_type": "{{combination_type}}",
  "mode": "{{mode}}"
}
```

**Pros:** Simple, explicit
**Cons:** Need to add every custom parameter manually

### Option 2: Use wildcard/passthrough syntax
```json
"parameters": {
  "output_chunk": "{{OUTPUT_CHUNK}}",
  "prompt": "{{PREVIOUS_OUTPUT}}",
  "...": "{{...}}"  // Forward all other parameters
}
```

**Pros:** Automatic forwarding of all parameters
**Cons:** Need to implement wildcard support in chunk executor

### Option 3: Make proxy_chunk forward all parameters by default
Modify the chunk executor to automatically forward ALL parameters for chunks with `type: "proxy_chunk"`, not just those explicitly listed.

**Pros:** Clean, no config changes needed
**Cons:** Requires backend code change, might affect other proxy chunks

---

## Next Steps

1. **Verify hypothesis:** Add debug logging to chunk executor to confirm parameters are being filtered
2. **Choose solution:** Decide between Options 1-3
3. **Implement fix:** Update either output_legacy.json or the chunk executor
4. **Test:** Verify element1, element2, combination_type reach `_process_legacy_workflow()`

---

## Testing Command

```bash
curl -X POST http://localhost:17802/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "split_and_combine",
    "input_text": "fallback text",
    "element1": "a cat",
    "element2": "a train",
    "safety_level": "off",
    "output_config": "split_and_combine_legacy",
    "combination_type": "linear",
    "user_language": "en",
    "seed": 123456789
  }'
```

**Expected in logs:**
```
[DEBUG-PROMPT] Received parameters: ['output_chunk', 'prompt', 'OUTPUT_CHUNK', 'seed', 'element1', 'element2', 'combination_type']
```

**Currently seeing:**
```
[DEBUG-PROMPT] Received parameters: ['output_chunk', 'prompt', 'OUTPUT_CHUNK', 'seed']
```

---

## Key Files

- `devserver/schemas/chunks/output_legacy.json` - Proxy chunk (likely culprit)
- `devserver/schemas/chunks/legacy_split_and_combine.json` - Target workflow (✅ fixed)
- `devserver/schemas/engine/backend_router.py` - Router (✅ fixed)
- `devserver/schemas/engine/pipeline_executor.py` - Executor (needs investigation)

---

## Session Statistics

- **Commits:** 3 (workflow update, router fix, LIST format support)
- **Files Changed:** 2 (legacy_split_and_combine.json, backend_router.py)
- **Bug Status:** Identified but not fixed
- **Blocker:** Parameters not propagating through proxy_chunk

---

## Critical Notes

1. **Don't modify input_mappings** - They're correct as-is
2. **Don't modify backend_router** - The fix is correct, it just needs data to work with
3. **Focus on parameter propagation** - Find where element1, element2, combination_type are being filtered out
4. **Test after each change** - Use the curl command above to verify parameters reach _process_legacy_workflow

---

## End of Handover

**Priority:** HIGH - Workflow is useless without parameter injection
**Estimated Fix Time:** 10-15 minutes once culprit is confirmed
**Risk Level:** Low - Solution is straightforward once location is found
