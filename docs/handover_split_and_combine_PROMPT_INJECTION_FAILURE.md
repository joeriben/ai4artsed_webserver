# Handover: Split and Combine - Prompt Injection Failure

**Date:** 2025-12-14 22:06
**Session:** Image assignment fix + bytes error fix
**Status:** Image assignment ✅ FIXED - Prompt injection ❌ BROKEN

---

## What Works Now

### ✅ Image Assignment (Commit f3032f8)

**Problem Solved:** Images displayed in wrong order due to non-deterministic dict iteration

**Solution Implemented:**
1. Extract SaveImage node titles from workflow JSON
2. Add `node_title` to entity_metadata and API response
3. Frontend matches by node_title substring instead of index

**Files Modified:**
- `devserver/my_app/routes/schema_pipeline_routes.py:1972-2040` - Node title extraction
- `devserver/my_app/routes/media_routes.py:348` - node_title in API
- `public/ai4artsed-frontend/src/views/split_and_combine.vue:317-337` - Substring matching

**Test Results:**
- Linear mode: Images have correct node_titles (124, 131, 9, 110)
- Spherical mode: Images have correct node_titles (124, 9, 110, 131)
- Different ordering between modes proves fix was necessary
- Frontend displays with correct labels (node titles used DIRECTLY, no i18n)

### ✅ Bytes Serialization Error Fixed (Commit f3032f8)

**Problem:** `TypeError: Object of type bytes is not JSON serializable`

**Root Cause:** Binary `media_files` from metadata added to response BEFORE cleanup

**Solution:** Immediate cleanup after extraction (lines 2014-2019)
```python
# Extract binary data
media_files = output_result.metadata.get('media_files', [])
outputs_metadata = output_result.metadata.get('outputs_metadata', [])

# IMMEDIATE CLEANUP: Remove binary data before it goes into response dicts
if 'media_files' in output_result.metadata:
    del output_result.metadata['media_files']
if 'outputs_metadata' in output_result.metadata:
    del output_result.metadata['outputs_metadata']
```

**Result:** ✅ Workflows complete successfully, no JSON serialization errors

### ✅ Type Hint Bug Fixed (Commit f3032f8)

**Problem:** `NameError: name 'Dict' is not defined`

**Solution:** Changed `Dict` → `dict` in function signature (line 1972)

**Result:** ✅ Helper function executes without errors

---

## What's Broken

### ❌ Prompt Injection for element1 and element2

**Problem:**
User reports that element1 and element2 prompts are NOT being injected into the workflow nodes. The workflow generates images but uses placeholder/default prompts instead of the user-provided element1 and element2 values.

**Backend Logs (from bash 893c99, timestamp 2025-12-14 18:10:20):**
```
2025-12-14 18:10:20,856 - INFO - [LEGACY-WORKFLOW] Applying input_mappings for: ['combination_type', 'element1', 'element2']
2025-12-14 18:10:20,856 - INFO - [LEGACY-SERVICE] Initialized for http://127.0.0.1:7821
2025-12-14 18:10:20,856 - INFO - [DEBUG-PROMPT] Legacy service received prompt: 'a cat  a train...'
2025-12-14 18:10:20,856 - INFO - [DEBUG-PROMPT] Starting prompt injection...
2025-12-14 18:10:20,856 - INFO - [LEGACY-INJECT] No input_mappings found, searching for node with title 'ai4artsed_text_prompt'
2025-12-14 18:10:20,856 - ERROR - [LEGACY-INJECT] ✗ Could not find injection target
2025-12-14 18:10:20,856 - WARNING - [LEGACY-SERVICE] Prompt injection failed, continuing anyway
```

**Analysis:**

1. **input_mappings ARE detected** at the BackendRouter level:
   - Log: "Applying input_mappings for: ['combination_type', 'element1', 'element2']"
   - This happens in `backend_router.py:_apply_input_mappings()`
   - Values should be injected to workflow nodes 43, 137, 133, 134

2. **LegacyWorkflowService doesn't see them:**
   - Log: "No input_mappings found, searching for node with title..."
   - Legacy service is using OLD prompt injection method (title-based search)
   - Legacy service does NOT use the new _apply_input_mappings() system

3. **Root Cause Hypothesis:**
   - `_apply_input_mappings()` runs in BackendRouter and modifies workflow
   - BUT the modified workflow might not be passed to LegacyWorkflowService
   - OR LegacyWorkflowService reloads the workflow from chunk, losing modifications
   - OR context_override is not being passed correctly to legacy service

**Chunk Definition:** `devserver/schemas/chunks/legacy_split_and_combine.json`
```json
"input_mappings": {
  "combination_type": [
    {"node_id": "133", "field": "inputs.interpolation_method"},
    {"node_id": "134", "field": "inputs.interpolation_method"}
  ],
  "element1": [
    {"node_id": "43", "field": "inputs.value"}
  ],
  "element2": [
    {"node_id": "137", "field": "inputs.value"}
  ]
}
```

**Expected Behavior:**
- User sends: `element1: "apple"`, `element2: "banana"`
- BackendRouter applies input_mappings → Node 43.inputs.value = "apple", Node 137.inputs.value = "banana"
- Workflow executes with user prompts
- Images generated showing "apple" and "banana"

**Actual Behavior:**
- Workflow executes with placeholder/default values
- Images show placeholder content instead of user prompts

---

## Code Locations

### BackendRouter (Works)
**File:** `devserver/schemas/engine/backend_router.py`
**Function:** `_apply_input_mappings()` (lines 1367-1434)
**Status:** ✅ Detects and applies input_mappings correctly

### LegacyWorkflowService (Broken?)
**File:** `devserver/schemas/engine/backend_router.py`
**Function:** `_process_legacy_workflow()` (around line 700-750)
**Status:** ❌ Might not receive modified workflow or might reload chunk

### Schema Pipeline Routes (Passes context)
**File:** `devserver/my_app/routes/schema_pipeline_routes.py`
**Location:** Lines 1268-1273, 1862-1870, 1878
**Status:** ✅ Extracts custom_params and passes context_override

---

## Investigation Needed

**Questions to Answer:**

1. **Does _apply_input_mappings() actually modify the workflow?**
   - Check if workflow dict is modified in-place
   - Verify modified workflow is passed to LegacyWorkflowService

2. **Does LegacyWorkflowService receive the modified workflow?**
   - Check if service gets workflow from context or reloads from chunk
   - Trace workflow flow from BackendRouter → LegacyWorkflowService

3. **Is context_override being passed correctly?**
   - Verify custom_placeholders reach BackendRouter
   - Check if BackendRouter passes them to _apply_input_mappings()

4. **Logging discrepancy:**
   - BackendRouter says "Applying input_mappings for: ['combination_type', 'element1', 'element2']"
   - LegacyWorkflowService says "No input_mappings found"
   - Why the disconnect?

**Files to Check:**
- `devserver/schemas/engine/backend_router.py` - Both _apply_input_mappings() and _process_legacy_workflow()
- Check if workflow modifications persist through the call chain

---

## Test Case

**Request:**
```bash
curl -X POST http://localhost:17802/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "split_and_combine",
    "input_text": "test",
    "element1": "a red apple",
    "element2": "a yellow banana",
    "safety_level": "open",
    "output_config": "split_and_combine_legacy",
    "combination_type": "linear",
    "user_language": "en",
    "seed": 123456
  }'
```

**Expected:** 4 images generated with "a red apple" and "a yellow banana" visible

**Actual:** 4 images generated with placeholder/default prompts (NOT user prompts)

---

## Session Commits

**Commit f6c18cf** - Support LIST format in _apply_input_mappings
- Fixed "'list' object has no attribute 'get'" error
- Enables multi-node injection for combination_type

**Commit 245d58c** (Previous session) - Custom parameter support via context_override
- Extract custom_params from request
- Create PipelineContext with custom_placeholders
- Pass context_override to execute_pipeline()

**Commit f3032f8** (This session) - Node_title extraction + bytes fix
- Add node_title to image metadata
- Fix bytes serialization error
- Fix type hint error
- **Image assignment now works correctly**
- **BUT prompt injection still broken**

---

## Current State

**Working:**
- ✅ Image assignment via node_title matching
- ✅ API includes node_title field
- ✅ Frontend displays correct labels
- ✅ No bytes serialization errors
- ✅ No type hint errors
- ✅ Workflow executes and generates 4 images

**Broken:**
- ❌ element1 and element2 prompts NOT injected into nodes 43 and 137
- ❌ Generated images use placeholder content instead of user prompts

**Git Status:**
- Branch: develop
- HEAD: f3032f8
- Working tree: clean

---

## Next Session Priority

**CRITICAL:** Fix prompt injection for element1 and element2

**Investigation Steps:**
1. Add extensive logging to _apply_input_mappings() to verify modifications
2. Add logging to LegacyWorkflowService to see what workflow it receives
3. Trace workflow object through entire call chain
4. Verify context_override reaches _apply_input_mappings()
5. Check if workflow modifications are lost somewhere in the pipeline

**Expected Fix Location:**
Likely in `backend_router.py` where workflow is passed between _apply_input_mappings() and LegacyWorkflowService.

---

## Failure Analysis

**What I Did Wrong:**
1. Focused on image assignment without verifying end-to-end workflow
2. Didn't test that element1/element2 actually appear in generated images
3. Assumed that commit 245d58c (custom parameter support) was working
4. Tested API responses but not actual image content

**What Should Have Been Done:**
1. Test with VISIBLE prompts (e.g., element1="RED APPLE TEXT", element2="YELLOW BANANA TEXT")
2. Verify text appears in generated images BEFORE declaring success
3. Check both linear AND spherical modes for prompt injection
4. Trace custom_params from frontend → backend → workflow → ComfyUI

---

## User Feedback

"Oh nein. Die Bildbezeichnungen stimmen aber BEIDE prompts werden nicht injected! Schreib ein Handover, DU hast versagt."

Translation: "Oh no. The image labels are correct BUT both prompts are not being injected! Write a handover, YOU have failed."

**User is correct.** Image assignment was fixed but the core functionality (prompt injection) is still broken.

---

## Rollback

If needed, revert to commit 245d58c:
```bash
git reset --hard 245d58c
```

This will remove my changes but won't fix the prompt injection issue, which was already broken.

---

## Key Insight for Next Session

The problem is NOT in my changes - it's in how the existing system passes workflows between components. Commit 245d58c claimed to fix custom parameter support, but it only fixed the EXTRACTION of custom_params from the request. The actual INJECTION into workflow nodes is still broken.

**The real bug:** Somewhere between schema_pipeline_routes.py passing context_override and backend_router.py applying input_mappings, the values are getting lost or the modified workflow is being discarded.
