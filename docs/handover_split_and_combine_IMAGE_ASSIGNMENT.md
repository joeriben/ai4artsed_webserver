# Handover: Split and Combine - Image Assignment Bug
**Date:** 2025-12-14 21:30
**Session:** Image assignment fix attempt
**Status:** Parameter injection ✅ WORKS - Image assignment ❌ BROKEN

---

## What Works Now

### ✅ Parameter Injection (Commit 245d58c)

**File:** `devserver/my_app/routes/schema_pipeline_routes.py`

**Changes:**
1. Lines 1268-1273: Extract custom_params from request
2. Lines 1862-1870: Create PipelineContext with custom_placeholders
3. Line 1878: Pass context_override to execute_pipeline()

**Result:**
- Frontend sends: `element1`, `element2`, `combination_type`
- Backend receives them via custom_placeholders
- input_mappings successfully inject into workflow nodes
- **PROMPTS ARRIVE AT NODES 43, 137, 133/134** ✅

---

## What's Broken

### ❌ Image Assignment in Frontend

**Problem:**
Images are displayed but in WRONG order. Order differs between linear and spherical modes.

**Current Frontend Code:** `public/ai4artsed-frontend/src/views/split_and_combine.vue:317-323`

```typescript
// Hard-coded reordering (BRITTLE!)
const reorderedImages = [
  imagesResponse.data.images[0],  // Original
  imagesResponse.data.images[1],  // Vektor-Fusion
  imagesResponse.data.images[3],  // Element 1 (was at index 3)
  imagesResponse.data.images[2]   // Element 2 (was at index 2)
]
```

**Why This Breaks:**
- ComfyUI returns images in dictionary iteration order (non-deterministic)
- Order can change between linear/spherical due to execution parallelization
- Frontend assumes fixed order → wrong assignments

---

## What Was Attempted (Session 2)

### Attempt: semantic_role enrichment

**Files Modified:**
1. `devserver/schemas/chunks/legacy_split_and_combine.json` - Changed "Element" → "Prompt" in output_labels
2. `devserver/my_app/routes/media_routes.py` - Added semantic_role enrichment from output_labels
3. `public/ai4artsed-frontend/src/views/split_and_combine.vue` - Replaced hard-coded reordering with semantic_role matching

**Result:** ❌ FAILED
- Only composite image displayed, 4 individual images disappeared
- Likely cause: semantic_role not reaching frontend, or find() returning undefined

**Rollback:** `git reset --hard 245d58c` (all changes reverted)

---

## Next Session: Alternative Approach

### User's Preferred Method: Use SaveImage Node Titles Directly

**Concept:**
Instead of semantic_role, use the actual SaveImage node TITLES from the workflow.

**SaveImage Nodes in Workflow:**
- Node 9: `"title": "save_image vector-fused"`
- Node 110: `"title": "save_image original (concatenated)"`
- Node 124: `"title": "save_image prompt#1"`
- Node 131: `"title": "save_image prompt#2"`

**Implementation Strategy:**
1. Backend: Extract node title from workflow when saving images
2. API: Include node title in /api/media/images response
3. Frontend: Match by node title substring (e.g., contains "vector-fused", "original", "prompt#1", "prompt#2")

**Why This Should Work:**
- Titles are directly from ComfyUI workflow (no intermediate abstraction)
- Titles are unique and descriptive
- No dependency on output_labels abstraction layer
- More direct mapping: node → title → frontend

---

## Current State (Post-Reset)

**Committed:**
- ✅ Commit f6c18cf: LIST format support in _apply_input_mappings
- ✅ Commit d6a200f: Call _apply_input_mappings for legacy workflows
- ✅ Commit 8be2e69: Simplified split_and_combine workflow
- ✅ Commit 245d58c: Custom parameter support via context_override

**Uncommitted:**
- NONE (git reset --hard completed)

**Working:**
- ✅ Parameter injection (element1, element2, combination_type reach workflow)
- ✅ Workflow executes and generates 4 images + 1 composite

**Broken:**
- ❌ Image assignment in frontend (wrong order for linear vs spherical)

---

## Key Files

**Backend:**
- `devserver/my_app/routes/schema_pipeline_routes.py` (parameter extraction)
- `devserver/my_app/routes/media_routes.py` (API response for images)
- `devserver/schemas/chunks/legacy_split_and_combine.json` (workflow + output_labels)

**Frontend:**
- `public/ai4artsed-frontend/src/views/split_and_combine.vue` (image display logic)

---

## Testing Commands

**Test Split and Combine:**
```bash
curl -X POST http://localhost:17802/api/schema/pipeline/execute -H "Content-Type: application/json" -d '{"schema": "split_and_combine", "input_text": "test", "element1": "cat", "element2": "moon", "safety_level": "open", "output_config": "split_and_combine_legacy", "combination_type": "linear", "user_language": "en", "seed": 12345}'
```

**Check Images API:**
```bash
curl http://localhost:17802/api/media/images/{run_id}
```

---

## Priority for Next Session

**HIGH:** Fix image assignment using SaveImage node titles directly (user's method)

**Steps:**
1. Modify backend to include node title in API response
2. Modify frontend to match by node title substring
3. Test linear AND spherical modes
4. Verify assignments are consistent

---

## Notes

- User requirement: "Bedeutung sollte den image_save nodes automatisch entnommen werden, nicht hardgecoded werden"
- User requirement: "Element" is forbidden → use "Prompt" terminology
- semantic_role approach failed → switch to direct node title approach
- No more experimentation - implement user's method exactly

---

## Session Statistics

- **Commits:** 1 (custom parameter support)
- **Files Changed:** 1 (schema_pipeline_routes.py)
- **Parameter Injection:** ✅ FIXED
- **Image Assignment:** ❌ STILL BROKEN
- **Next Approach:** Use SaveImage node titles directly
