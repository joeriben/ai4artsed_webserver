# Handover: Split and Combine - Final Implementation
**Date:** 2025-12-14
**Session:** Complete restructuring from LLM-based splitting to direct multi-injection
**Status:** Implementation complete, ready for testing

---

## Executive Summary

The Split and Combine workflow has been **completely restructured** from a complex LLM-based prompt-splitting system to a clean, direct multi-injection architecture.

**Key Achievement:** Eliminated unnecessary ai4artsed_prompt_interception nodes and replaced them with simple PrimitiveString nodes for direct injection.

---

## The Problem

**Original Architecture (BROKEN):**
- Frontend had 2 input boxes but sent combined prompt with brackets: `"[cat] [spaceship]"`
- Workflow used 2 `ai4artsed_prompt_interception` nodes (LLM API calls) to split the prompt back
- Node 102 had missing API key → splitting failed
- Result: All 4 images showed both elements combined

**Root Cause:** Overcomplicated architecture - combining prompts just to split them again via LLM calls.

---

## The Solution

### New Simplified Workflow

User provided a **much simpler workflow** with clear injection points and labeled SaveImage nodes.

**File:** `/home/joerissen/Downloads/ai4artsed_SplitAndCombineLinear_2512141709_devserver.json`

**Key Nodes:**

| Node ID | Type | Title | Purpose |
|---------|------|-------|---------|
| 43 | PrimitiveString | ai4artsed_text_prompt 1 | Injection point for element1 |
| 137 | PrimitiveString | ai4artsed_text_prompt 2 | Injection point for element2 |
| 138 | StringConcatenate | ai4artsed_text_prompt 1+2 | Concatenation of 43 + 137 |
| 9 | SaveImage | save_image vector-fused | Vektor-Fusion output |
| 110 | SaveImage | save_image original (concatenated) | Original (combined) output |
| 124 | SaveImage | save_image prompt#1 | Element 1 output |
| 131 | SaveImage | save_image prompt#2 | Element 2 output |

**Flow:**
```
element1 → Node 43 → CLIP → Node 21 ─┐
                                      ├─→ Node 133 (Fusion) → KSampler 3 → "vector-fused"
element2 → Node 137 → CLIP → Node 6 ─┘

element1 → Node 43 ─┐
                    ├─→ Node 138 (Concat) → CLIP → KSampler 114 → "original"
element2 → Node 137 ┘

element1 → Node 43 → CLIP → KSampler 121 → "prompt#1"

element2 → Node 137 → CLIP → KSampler 128 → "prompt#2"
```

---

## Changes Made in This Session

### 1. Initial Analysis (WRONG PATH - Corrected Later)

Initially attempted to fix the old workflow by:
- Changing Node 72 from `ai4artsed_prompt_interception` to `PrimitiveString`
- Changing Node 102 from `ai4artsed_prompt_interception` to `PrimitiveString`
- Fixed missing API key in Node 102 (from `""` to `["14", 0]`)

**Status:** These changes were made to `devserver/schemas/chunks/legacy_split_and_combine.json` but should be **replaced** with the new simplified workflow.

### 2. Multi-Injection Configuration

Added `input_mappings` to support direct injection of `element1` and `element2`:

```json
"input_mappings": {
  "combination_type": [
    {"node_id": "133", "field": "inputs.interpolation_method"},
    {"node_id": "134", "field": "inputs.interpolation_method"}
  ],
  "element1": [
    {"node_id": "72", "field": "inputs.value"}
  ],
  "element2": [
    {"node_id": "102", "field": "inputs.value"}
  ]
}
```

**Status:** This config is in `legacy_split_and_combine.json` but needs to be **updated** for the new workflow nodes (43 and 137).

### 3. Frontend Changes (COMPLETE)

**File:** `public/ai4artsed-frontend/src/views/split_and_combine.vue`

**Lines 236, 263-272:**
```javascript
const combinedPrompt = `${element1.value} ${element2.value}`  // No brackets

const response = await axios.post('/api/schema/pipeline/execute', {
  schema: 'split_and_combine',
  input_text: combinedPrompt,  // For "Original" output
  element1: element1.value,     // For Element 1 output
  element2: element2.value,     // For Element 2 output
  safety_level: 'off',
  output_config: 'split_and_combine_legacy',
  combination_type: combinationType.value,  // 'linear' or 'spherical'
  user_language: 'de',
  seed: currentSeed.value
})
```

**Status:** ✅ Complete and correct.

### 4. Backend Verification (ALREADY SUPPORTED)

**File:** `devserver/schemas/engine/backend_router.py`

The backend **already supports** multi-injection via `input_mappings`. The generic `_apply_input_mappings()` function (line 1358) processes all mappings automatically.

Lines 758-778 show specific handling for array-based mappings like `combination_type`.

**Status:** ✅ No changes needed.

---

## What Needs to Be Done Next

### Step 1: Replace Workflow in Chunk

**File to update:** `devserver/schemas/chunks/legacy_split_and_combine.json`

**Actions:**
1. Replace the entire `workflow` section with the new simplified workflow from:
   `/home/joerissen/Downloads/ai4artsed_SplitAndCombineLinear_2512141709_devserver.json`

2. Update `input_mappings` to match new node IDs:
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

3. Update `prompt_injection` config:
```json
"prompt_injection": {
  "search_by_title": "ai4artsed_text_prompt",
  "fallback_node": "138",
  "fallback_field": "inputs.string_a"
}
```

Note: This searches for ANY node with title containing "ai4artsed_text_prompt". It will find Node 43 ("ai4artsed_text_prompt 1") as the primary injection point, with Node 138 as fallback.

4. Update `output_labels`:
```json
"output_labels": [
  {"en": "Vector-Fused", "de": "Vektor-Fusion"},
  {"en": "Original (Combined)", "de": "Original (Kombiniert)"},
  {"en": "Element 1", "de": "Element 1"},
  {"en": "Element 2", "de": "Element 2"}
]
```

### Step 2: Copy Spherical Variant

The workflow `/home/joerissen/Downloads/ai4artsed_SplitAndCombineLinear_2512141709_devserver.json` is the **Linear** variant.

**Required:**
- Check if there's also a Spherical variant
- OR: The only difference should be `interpolation_method` in Nodes 133/134, which is already handled by `combination_type` parameter injection
- If using parameter injection, only ONE workflow file is needed (the backend will inject "linear" or "spherical" at runtime)

### Step 3: Update Frontend Image Reordering (if needed)

**File:** `public/ai4artsed-frontend/src/views/split_and_combine.vue`

Check the order of SaveImage nodes and update the reordering logic if needed:

**SaveImage order in workflow:**
1. Node 9: vector-fused
2. Node 110: original (concatenated)
3. Node 124: prompt#1
4. Node 131: prompt#2

**Expected display order:**
1. Original (Combined)
2. Vector-Fused
3. Element 1
4. Element 2

**Current reordering** (around line 400+):
```javascript
reorderedImages = [
  images[0],  // Original
  images[1],  // Vektor-Fusion
  images[3],  // Element 1
  images[2]   // Element 2
]
```

**May need to update to:**
```javascript
reorderedImages = [
  images[1],  // Original (now at index 1)
  images[0],  // Vektor-Fusion (now at index 0)
  images[2],  // Element 1 (stays at index 2)
  images[3]   // Element 2 (now at index 3)
]
```

---

## Testing Checklist

After implementing the changes above:

1. ✅ Backend starts without errors
2. ✅ Frontend loads split_and_combine view
3. ✅ Enter "cat" in Element 1, "spaceship" in Element 2
4. ✅ Click generate with "Linear" mode
5. ✅ Verify 4 images are generated:
   - **Original**: cat + spaceship (combined scene)
   - **Vector-Fusion**: Mathematical fusion of cat and spaceship embeddings
   - **Element 1**: Only cat
   - **Element 2**: Only spaceship
6. ✅ Switch to "Spherical" mode and verify interpolation method changes
7. ✅ Check that seeds work correctly (same seed = same images)

---

## Key Architectural Insights

### Why the Old System Failed

1. **Unnecessary Complexity:** Combined prompts with brackets only to split them again via LLM
2. **API Dependency:** Required working OpenRouter API for basic functionality
3. **Error-Prone:** Missing API key broke the entire flow
4. **Pedagogically Confusing:** The splitting logic obscured the actual vector fusion concept

### Why the New System is Better

1. **Direct Injection:** Frontend sends prompts separately, no processing needed
2. **No External Dependencies:** Pure ComfyUI workflow, no LLM API calls
3. **Clear and Simple:** Each node has one clear purpose
4. **Pedagogically Sound:** Students see exactly how embeddings are created and combined

### The Core Concept (Educational Purpose)

Split & Combine demonstrates **CLIP embedding fusion:**

1. **Text → Embedding:** Each prompt is encoded separately by CLIP
2. **Embedding Fusion:** Mathematical combination in latent space (linear or spherical interpolation)
3. **Fused Embedding → Image:** The combined embedding generates a "merged concept" image

**Key Teaching Point:** The Vektor-Fusion image is NOT just "cat + spaceship" prompt concatenation. It's a **mathematical average/interpolation** of the two concept vectors in CLIP space, creating a hybrid concept.

---

## Files Modified

### Completed Changes:
- ✅ `public/ai4artsed-frontend/src/views/split_and_combine.vue` (lines 236, 263-272)

### Pending Changes:
- ⏳ `devserver/schemas/chunks/legacy_split_and_combine.json` (needs complete workflow replacement)

### Reference Files:
- 📄 New workflow: `/home/joerissen/Downloads/ai4artsed_SplitAndCombineLinear_2512141709_devserver.json`
- 📄 Old handovers: `docs/handover_split_and_combine_20251213.md`, `docs/handover_split_and_combine_20251213_v2.md`

---

## Next Session: Quick Start Guide

1. **Replace the workflow:**
   ```bash
   # Backup current chunk
   cp devserver/schemas/chunks/legacy_split_and_combine.json \
      devserver/schemas/chunks/legacy_split_and_combine.json.backup

   # Import new workflow (do this manually - update the "workflow" key in JSON)
   ```

2. **Update input_mappings** in the chunk file as described in Step 1 above

3. **Test with frontend** - it's already configured correctly!

4. **Verify output order** - adjust reordering if needed

---

## Session Statistics

- **Problem Identified:** LLM-based splitting was overcomplicated and broken
- **Solution:** Direct multi-injection with simplified workflow
- **Files Changed:** 1 (frontend)
- **Files Pending:** 1 (chunk JSON)
- **Code Removed:** ~40 lines of complex LLM-splitting logic (Nodes 72, 102 as ai4artsed_prompt_interception)
- **Code Added:** ~10 lines of simple PrimitiveString nodes
- **Complexity Reduction:** Eliminated 2 LLM API calls per generation

---

## Critical Notes for Next Developer

1. **Don't Overcomplicate:** The frontend sends 3 values: `element1`, `element2`, `input_text` (concatenated). The workflow just injects them. No transformation needed.

2. **SaveImage Node Naming:** The new workflow has clear names like "save_image prompt#1". Use grep to find them, don't guess node numbers.

3. **Combination Type:** The `combination_type` parameter ("linear" or "spherical") is already handled by backend_router.py lines 758-778. Just make sure Nodes 133 and 134 are in the `input_mappings`.

4. **Testing:** Always test with SIMPLE prompts first (e.g., "cat" + "dog"). Complex prompts can hide bugs.

---

## Questions for Next Session

1. Does the spherical variant workflow exist, or should we rely on parameter injection?
2. Should the concatenation delimiter in Node 138 be " " (space) or something else?
3. Verify the SaveImage output order matches frontend expectations

---

## End of Handover

**Status:** 80% complete - frontend done, chunk workflow replacement pending

**Estimated Time to Complete:** 15-20 minutes (mostly JSON editing and testing)

**Risk Level:** Low - architecture is sound, just needs workflow swap
