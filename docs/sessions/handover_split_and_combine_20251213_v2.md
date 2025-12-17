# Handover: Split and Combine - Session 2
**Date:** 2025-12-13 23:55
**Status:** Partial implementation - Prompt injection works, workflow logic broken

---

## What Works ✅

### Architecture (Correct Pattern)
- **Single output config**: `split_and_combine_legacy.json`
- **Single chunk**: `legacy_split_and_combine.json`
- **Parameter injection**: `combination_type` → `interpolation_method` in nodes 133, 134
- **Frontend**: Sends `combination_type: "linear"|"spherical"` parameter
- **Backend**: Extended with `combination_type` parameter injection in `backend_router.py:757-778`

### Prompt Injection (Fixed)
- **Working**: User prompts now reach the workflow
- **Fix applied**: `fallback_node: "86"` (was "102" which didn't exist after Note cleanup)
- **Injection target**: Node 86 (`PrimitiveStringMultiline` with title "YOUR PROMPT GOES HERE")

### Files Created
```
devserver/schemas/configs/output/split_and_combine_legacy.json
devserver/schemas/chunks/legacy_split_and_combine.json
devserver/schemas/pipelines/split_and_combine.json
devserver/schemas/configs/interception/split_and_combine.json
public/ai4artsed-frontend/src/views/split_and_combine.vue
workflows_legacy/vector/legacy_split_and_combine_{linear|spherical}.json
```

### Frontend
- Two input boxes (side-by-side layout)
- Dropdown for Linear/Spherical
- Image reordering for correct display (swaps positions 2-3)
- Correct labels: Original, Vektor-Fusion, Element 1, Element 2

---

## What Doesn't Work ❌

### Workflow Logic Broken
**Symptom:** All 4 images show variations of the COMBINED prompt (e.g., "sofa on spaceship")

**Expected behavior:**
1. **Original**: Full combined prompt → `[ein sofa] [auf einem raumschiff]`
2. **Vektor-Fusion**: Mathematical fusion of separated vectors
3. **Element 1**: Only first bracket → `ein sofa`
4. **Element 2**: Only second bracket → `auf einem raumschiff`

**Actual behavior:**
- All 4 images show combined prompt variations
- No separation happening
- Workflow treats input as single unified prompt

---

## Root Cause Analysis

### The Workflow Has Two Prompt Processing Paths

**Node 72** (`ai4artsed_prompt_interception` - "Prompt Splitter"):
- Purpose: Extract "main aspect" from prompt
- Input: Node 43 (which gets from Node 86)
- Output: Should be "Element 1" (main aspect only)

**Node 102** (`ai4artsed_prompt_interception` - second splitter):
- Purpose: Extract "secondary aspect"
- **PROBLEM**: This node was DELETED during Note cleanup!
- Should extract Element 2

**Critical Issue:**
The workflow uses **TWO** `ai4artsed_prompt_interception` nodes to split the prompt:
- Node 72: Extracts main aspect (Element 1)
- Node 102: Extracted secondary aspect (Element 2)

When I removed Note nodes, I likely also removed Node 102 or broke its connections!

---

## Investigation Needed

### Check Original Workflows
Compare chunk workflow with original workflows:
```bash
# Chunk workflow (what we use)
devserver/schemas/chunks/legacy_split_and_combine.json

# Original workflows (reference)
workflows_legacy/vector/legacy_split_and_combine_linear.json
workflows_legacy/vector/legacy_split_and_combine_spherical.json
```

### Find Missing Node 102
1. Search for Node 102 in original workflow
2. Check if it was a Note node or ai4artsed_prompt_interception
3. If deleted: restore it
4. If present: verify its connections

### Verify Prompt Flow
```
User Input: "[ein sofa] [auf einem raumschiff]"
  ↓
Node 86: Injection target (PrimitiveStringMultiline)
  ↓
Node 43: PrimitiveString (title: ai4artsed_text_prompt)
  ↓ (splits into two paths)
Path A: Node 72 → Extract main → Element 1
Path B: Node 102 → Extract secondary → Element 2
```

**Verify:**
- Does Node 102 exist in chunk?
- Does it have correct class_type and connections?
- Are both paths feeding into different KSamplers?

---

## SaveImage Node Mapping (From Workflow)

Based on grep analysis:
- Node 9: "vector-fused"
- Node 110: "original"
- Node 124: "prompt#1"
- Node 131: "prompt#2"

**Frontend reordering** (to match expected positions):
```javascript
reorderedImages = [
  images[0],  // Original
  images[1],  // Vektor-Fusion
  images[3],  // Element 1 (was at index 3)
  images[2]   // Element 2 (was at index 2)
]
```

---

## Next Steps (Priority Order)

1. **Find Node 102** in original workflow files
2. **Compare** chunk workflow with original (use diff or visual inspection)
3. **Restore missing Node 102** if it was ai4artsed_prompt_interception
4. **Verify connections** from Node 43 to both splitters
5. **Test** that Element 1 and Element 2 show separated prompts
6. **Verify** combination_type parameter switches between linear/spherical

---

## Files to Compare

```bash
# What's in the chunk now
jq '.workflow."102"' devserver/schemas/chunks/legacy_split_and_combine.json

# What was in original
jq '."102"' workflows_legacy/vector/legacy_split_and_combine_linear.json
```

---

## Commands for Next Session

```bash
# Check if Node 102 exists in chunk
jq '.workflow."102"' devserver/schemas/chunks/legacy_split_and_combine.json

# Check original workflow
jq '."102"' workflows_legacy/vector/legacy_split_and_combine_linear.json

# Find all ai4artsed_prompt_interception nodes in original
jq '.[] | select(.class_type == "ai4artsed_prompt_interception") | {node_id: .node_id, title: ._meta.title}' workflows_legacy/vector/legacy_split_and_combine_linear.json

# Compare node counts
echo "Chunk nodes: $(jq '.workflow | keys | length' devserver/schemas/chunks/legacy_split_and_combine.json)"
echo "Original nodes: $(jq 'keys | length' workflows_legacy/vector/legacy_split_and_combine_linear.json)"
```

---

## Session Notes

- Correctly identified that split_and_combine uses same pattern as partial_elimination
- Successfully implemented parameter injection for combination_type
- Fixed prompt injection target (Node 86)
- **Mistake**: Removed Note nodes without verifying which nodes were actually Notes vs functional nodes
- **Lesson**: When cleaning workflows, check node class_type AND connections, not just class name
