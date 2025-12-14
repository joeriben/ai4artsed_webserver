# Handover: Split and Combine Implementation
**Date:** 2025-12-13
**Session:** Interface migration from text_transformation.vue
**Status:** Frontend complete, Backend integration incomplete

---

## Completed Work

### Frontend (`public/ai4artsed-frontend/src/views/split_and_combine.vue`)

✅ **Two Input Boxes (Side-by-Side)**
- Structure copied from `text_transformation.vue` (lines 7-46)
- Classes: `input-bubble` and `context-bubble` with `bubble-card` parent
- Template: `<section class="input-context-section">` for flexbox layout
- CSS: `.input-context-section { display: flex; gap: clamp(1rem, 3vw, 2rem); }`
- Responsive: Stacks vertically on mobile (`flex-direction: column`)

✅ **Width Consistency**
- All elements (input boxes, dropdown, button, output frame) match width
- `max-width: calc(480px * 2 + clamp(1rem, 3vw, 2rem))`

✅ **Combination Type Dropdown**
- Options: Linear, Spherical
- Variable: `combinationType` (ref)
- Currently switches between two output_configs

### Backend Configuration Files

✅ **Created (but incorrect structure):**
- `devserver/schemas/configs/interception/split_and_combine.json`
- `devserver/schemas/pipelines/split_and_combine.json`
- `devserver/schemas/configs/output/split_and_combine_linear.json`
- `devserver/schemas/configs/output/split_and_combine_spherical.json`
- `devserver/schemas/chunks/legacy_split_and_combine_linear.json`
- `devserver/schemas/chunks/legacy_split_and_combine_spherical.json`

✅ **Workflows Copied:**
- From: `/home/joerissen/ai/ai4artsed_webserver_legacy/workflows/vector/`
  - `ai4artsed_SplitAndCombineLinear_2507021805.json`
  - `ai4artsed_SplitAndCombineSpherical_2507021805.json`
- To: `workflows_legacy/vector/legacy_split_and_combine_{linear|spherical}.json`

---

## Problems

### ❌ Wrong Architecture Pattern

**Current (WRONG):**
- TWO output configs: `split_and_combine_linear`, `split_and_combine_spherical`
- Frontend switches `output_config` based on dropdown

**Should be (CORRECT - like surrealization):**
- ONE output config: `split_and_combine_legacy`
- Frontend sends `combination_type: "linear"|"spherical"` parameter
- Backend selects workflow based on parameter

### ❌ Backend Execution Fails
```
Error: "Failed to submit workflow to ComfyUI"
```
Could be:
1. ComfyUI not running
2. Backend router not configured
3. Workflow format incompatible

---

## Required Next Steps

### 1. Fix Backend Architecture

**Delete:**
- `devserver/schemas/configs/output/split_and_combine_linear.json`
- `devserver/schemas/configs/output/split_and_combine_spherical.json`

**Create:**
- `devserver/schemas/configs/output/split_and_combine_legacy.json` (single config)

**Structure (copy from surrealization_legacy.json):**
```json
{
  "pipeline": "legacy_workflow_passthrough",
  "name": {
    "en": "Split and Combine (Legacy)",
    "de": "Teilen und Kombinieren (Legacy)"
  },
  "parameters": {
    "OUTPUT_CHUNK": "legacy_split_and_combine"
  },
  "meta": {
    "notes": ["Combination type parameter: linear, spherical"]
  }
}
```

### 2. Fix Chunk Architecture

**Question:** How do other configs (e.g., partial_elimination) handle multiple workflow variants?
- Partial Elimination has 8 workflow files but only 1 chunk
- Where is the logic that selects the correct workflow based on `mode` parameter?
- Need to find and replicate this pattern

**Options:**
1. Embed both workflows in one chunk with selection logic
2. Backend code dynamically loads workflow file based on parameter
3. Custom node in ComfyUI workflow handles the parameter

### 3. Update Frontend

**File:** `split_and_combine.vue` (line ~263-270)

**Change API call from:**
```javascript
const outputConfig = combinationType.value === 'linear'
  ? 'split_and_combine_linear'
  : 'split_and_combine_spherical'

const response = await axios.post('/api/schema/pipeline/execute', {
  schema: 'split_and_combine',
  output_config: outputConfig,
  // ...
})
```

**To:**
```javascript
const response = await axios.post('/api/schema/pipeline/execute', {
  schema: 'split_and_combine',
  output_config: 'split_and_combine_legacy',
  combination_type: combinationType.value,  // 'linear' or 'spherical'
  // ...
})
```

### 4. Verify ComfyUI

- Check if ComfyUI is running
- Verify backend router configuration
- Test workflow submission manually

---

## Files Modified

```
public/ai4artsed-frontend/src/views/split_and_combine.vue
  - Lines 6-44: Changed to input-context-section structure
  - Lines 520-541: Added CSS for side-by-side layout
  - Lines 543-605: Added bubble-card CSS from text_transformation
  - Lines 717-730: Adjusted output-frame width

workflows_legacy/vector/
  + legacy_split_and_combine_linear.json (copied)
  + legacy_split_and_combine_spherical.json (copied)

devserver/schemas/chunks/
  + legacy_split_and_combine_linear.json (created - needs revision)
  + legacy_split_and_combine_spherical.json (created - needs revision)
```

---

## Critical Question for Next Session

**How does partial_elimination select between 8 different workflow files using only ONE chunk and ONE config?**

The answer to this question will determine the correct implementation pattern for split_and_combine.

Possible locations to investigate:
- `devserver/my_app/services/legacy_workflow_service.py`
- `devserver/schemas/engine/pipeline_executor.py`
- `devserver/schemas/engine/backend_router.py`

---

## Session Notes

- User frustrated with excessive back-and-forth
- Simple UI copy task escalated to backend architecture investigation
- Core issue: Not understanding the parameter-based workflow selection pattern
- Lesson: Study existing implementations COMPLETELY before creating new ones
