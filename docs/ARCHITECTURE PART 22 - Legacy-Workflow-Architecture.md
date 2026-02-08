# DevServer Architecture

**Part 22: Legacy Workflow Architecture & Convention-Based Routing**

---

## Overview

Legacy workflows are complete ComfyUI workflow JSON files that cannot be decomposed into DevServer's chunk system due to complex node connections and custom processing logic. They bypass Stage 2 (Prompt Interception) and pass prompts directly to ComfyUI with parameter injection.

**Key Pattern:** Config → Pipeline → Vue (Convention-based routing)

---

## Architecture Pattern

### Convention-Based Routing

**No explicit registry needed!** The system uses **filename matching convention**:

```
Pipeline JSON "name" field = Vue component filename

Example:
  pipelines/surrealizer.json → "name": "surrealizer" → views/surrealizer.vue
  pipelines/direct.json       → "name": "direct"       → views/direct.vue
```

**Complete Flow:**

```
1. User navigates to: /execute/surrealizer
2. Frontend: PipelineRouter.vue extracts configId = "surrealizer"
3. Frontend: GET /api/config/surrealizer/pipeline
4. Backend: Loads configs/interception/surrealizer.json
5. Backend: Reads "pipeline": "surrealizer"
6. Backend: Loads pipelines/surrealizer.json
7. Backend: Reads "name": "surrealizer"
8. Backend: Returns {"pipeline_name": "surrealizer", ...}
9. Frontend: Receives pipeline_name = "surrealizer"
10. Frontend: import(`../views/${pipelineName}.vue`) → surrealizer.vue
11. Vue component renders
```

**Critical File Locations:**
- **Backend route:** `devserver/my_app/routes/schema_pipeline_routes.py:2915-2955`
- **Frontend router:** `public/ai4artsed-frontend/src/views/PipelineRouter.vue:18-49`

---

## Two Types of Legacy Workflows

### 1. Production Workflows (Dedicated Vue)

**Pattern:** One config → One pipeline → One dedicated Vue

**Example: Surrealizer**
```
configs/interception/surrealizer.json
  └─ "pipeline": "surrealizer"
       └─ pipelines/surrealizer.json
            └─ "name": "surrealizer"
                 └─ views/surrealizer.vue (dedicated, no dropdown)
```

**Characteristics:**
- **Hardcoded output config** (e.g., `surrealization_legacy`)
- **No dropdown selection** - focused UX
- **Production-stable** - tested in workshops
- **Non-reusable pipeline** (`"reusable": false`)

**Use Cases:**
- Workshop-tested workflows
- Stable pedagogical tools
- Workflows with specific UI requirements (sliders, advanced controls)

### 2. Experimental Workflows (Generic Vue with Dropdown)

**Pattern:** Multiple configs → One pipeline → One generic Vue with dropdown

**Example: Direct/Hacking Lab** (currently deactivated)
```
configs/interception/direct_workflow.json
  └─ "pipeline": "direct"
       └─ pipelines/direct.json
            └─ "name": "direct"
                 └─ views/direct.vue (dropdown to select configs)
```

**Characteristics:**
- **Dropdown selection** for multiple output configs
- **Generic interface** - same UI for all experiments
- **Rapid prototyping** - no new Vue needed
- **Reusable pipeline** (`"reusable": true`)

**Use Cases:**
- Testing new ComfyUI workflows
- Research experiments
- Short-term prototypes before promoting to dedicated Vue

---

## Legacy Workflow Service

**File:** `devserver/my_app/services/legacy_workflow_service.py`

**Responsibilities:**
1. Load complete workflow JSON from chunk
2. Inject parameters via `input_mappings`
3. Submit to ComfyUI API
4. Poll for completion
5. Download all outputs

### Input Mappings Pattern

**Modern pattern (Session 94+):**

```json
{
  "input_mappings": {
    "prompt": {
      "node_id": "43",
      "field": "inputs.value",
      "description": "User prompt input"
    },
    "alpha": {
      "node_id": "50",
      "field": "inputs.value",
      "description": "T5-CLIP fusion alpha factor"
    },
    "seed": {
      "node_id": "3",
      "field": "inputs.seed",
      "default": "random"
    }
  }
}
```

**Backend Injection (backend_router.py:739-753):**
```python
# Handle alpha_factor for T5-CLIP fusion workflows
if input_mappings and 'alpha' in input_mappings and 'alpha_factor' in parameters:
    alpha_mapping = input_mappings['alpha']
    alpha_value = parameters['alpha_factor']

    logger.info(f"[LEGACY-WORKFLOW] Injecting alpha_factor={alpha_value}")

    alpha_node_id = alpha_mapping.get('node_id')
    alpha_field = alpha_mapping.get('field', 'inputs.value')
    if alpha_node_id and alpha_node_id in workflow:
        field_parts = alpha_field.split('.')
        target = workflow[alpha_node_id]
        for part in field_parts[:-1]:
            target = target.setdefault(part, {})
        target[field_parts[-1]] = alpha_value
        logger.info(f"[LEGACY-WORKFLOW] ✓ Injected alpha into node {alpha_node_id}.{alpha_field}")
```

**Fallback pattern (legacy):**
- Title-based node search for `ai4artsed_text_prompt`
- Used when `input_mappings` not defined

---

## Hallucinator (formerly Surrealizer) — Workflow Specifics

**Display Name:** Hallucinator (renamed Session 162 — the effect is genuine AI hallucination, not stylistic surrealism)
**Internal IDs:** `surrealizer` (configs, pipeline, route, Vue filename — unchanged)
**Two Backends:** Diffusers (active, primary) and Legacy ComfyUI (preserved)

### The Mechanism: Token-Level CLIP-L/T5 Extrapolation

The Hallucinator exploits the fact that SD3.5 uses two fundamentally different text encoders:
- **CLIP-L** (77 tokens, 768-dim): Trained on image-text pairs. "Thinks" visually.
- **T5-XXL** (512 tokens, 4096-dim): Trained on pure text. "Thinks" linguistically.

Both encode the same prompt, but produce entirely different vector representations. The alpha slider controls a LERP formula applied to the **first 77 token positions**:

```
fused[0:77] = (1 - α) · CLIP-L + α · T5     ← extrapolation zone
fused[77:]  = T5 (unchanged)                   ← semantic anchor
```

**Why this creates hallucinations (not just "surreal" images):**
- At α=0: Pure CLIP-L → normal image
- At α=1: Pure T5 → still fairly normal (different but coherent)
- At α=20: `(1-20)·CLIP-L + 20·T5 = -19·CLIP-L + 20·T5`
  The embedding is pushed **19× past T5's representation**, into a region of the 4096-dimensional vector space that the model has **never encountered during training**. The model must interpret these out-of-distribution vectors, producing genuine AI hallucinations.
- The remaining T5 tokens (78-512) are appended **unchanged**, acting as a semantic anchor that keeps the image thematically connected to the prompt even as the visual representation becomes hallucinatory.

**Alpha ranges (empirical):**
| Range | Effect |
|-------|--------|
| α = 0 | Normal image (CLIP-L only) |
| α = 1 | Pure T5 (still coherent) |
| α = 2–10 | Beginning to lose coherence |
| **α = 15–35** | **Hallucination sweet spot** |
| α > 50 | Extreme distortion, may lose all coherence |
| α > 76 | Blackout (embeddings too extreme) |
| Negative α | Extrapolation in reverse direction (past CLIP-L, away from T5) |

### Backend 1: Diffusers (Primary — Session 162)

**File:** `devserver/my_app/services/diffusers_backend.py`
**Method:** `DiffusersImageGenerator.generate_image_with_fusion()`

Uses individual SD3 pipeline text encoders directly (bypasses `encode_prompt()`):

```python
def _fuse_prompt(text: str):
    # 1. CLIP-L only (77 tokens × 768d)
    clip_l_embeds, clip_l_pooled = pipe._get_clip_prompt_embeds(text, clip_model_index=0)
    # 2. CLIP-G (only for pooled output — standard SD3 requirement)
    _, clip_g_pooled = pipe._get_clip_prompt_embeds(text, clip_model_index=1)
    # 3. T5-XXL (512 tokens × 4096d, padded to max_sequence_length)
    t5_embeds = pipe._get_t5_prompt_embeds(text, max_sequence_length=512)

    # 4. Pad CLIP-L to T5 dimension: [CLIP-L₇₆₈ | zeros₃₃₂₈] → (1, 77, 4096)
    clip_l_padded = F.pad(clip_l_embeds, (0, t5_embeds.shape[-1] - clip_l_embeds.shape[-1]))

    # 5. LERP first 77 tokens (THE CORE FORMULA)
    interp_len = min(clip_l_padded.shape[1], t5_embeds.shape[1])
    fused_part = (1.0 - alpha) * clip_l_padded[:, :interp_len, :] + alpha * t5_embeds[:, :interp_len, :]

    # 6. Append remaining T5 tokens unchanged (semantic anchor)
    t5_remainder = t5_embeds[:, interp_len:, :]
    fused_embeds = torch.cat([fused_part, t5_remainder], dim=1)  # (1, 512, 4096)

    # 7. Pooled: standard CLIP-L + CLIP-G
    pooled = torch.cat([clip_l_pooled, clip_g_pooled], dim=-1)   # (1, 2048)
    return fused_embeds, pooled
```

**Key design decisions (Diffusers backend):**

1. **CLIP-L only in fused tokens (no CLIP-G):** Matches the original ComfyUI workflow which only loads `clip_l.safetensors`. CLIP-G is used only for pooled output.
2. **Output shape (1, 512, 4096) instead of standard (1, 589, 4096):** The SD3 transformer uses flexible attention — any sequence length works. 512 = 77 fused + 435 T5 anchor tokens.
3. **Private method `_get_clip_prompt_embeds`:** Stable in diffusers v0.36.0, protected by `hasattr` guard.
4. **Negative prompt fused with same alpha:** Matches ComfyUI workflow (both fusion nodes receive the same alpha). All 4 embedding tensors passed to pipeline, fully bypassing `encode_prompt()`.
5. **Why not `encode_prompt()` with different prompt strings?** Because `encode_prompt()` returns **joint embeddings** (CLIP-L + CLIP-G + T5 concatenated). Blending two joint embeddings destroys the CLIP signal instead of extrapolating between encoder spaces. See "Failed approach" below.

**Failed approach (Session 162, pre-fix):**
```python
# BROKEN: blends joint SD3 embeddings
clip_embeds = pipe.encode_prompt(prompt, prompt, "", 512)   # CLIP active, T5 empty
t5_embeds = pipe.encode_prompt("", "", prompt, 512)         # CLIP empty, T5 active
blended = (1 - α) * clip_embeds + α * t5_embeds

# At α=20, the CLIP region (tokens 0-76) becomes:
#   -19 * CLIP(prompt) + 20 * CLIP("")
# This DESTROYS the CLIP signal instead of extrapolating toward T5.
# Result: α=10 already extreme, α=25 white/blank image.
```

### Backend 2: Legacy ComfyUI (Preserved)

**Key Nodes (from `chunks/legacy_surrealization.json`):**
- **Node 43:** `ai4artsed_text_prompt` — User prompt input
- **Node 50:** `set t5-Influence` — Alpha factor control (-75 to +75)
- **Node 68:** Prompt optimization for T5 encoder (250 words, rich paragraph, outputs `#a=XX`)
- **Node 69:** Prompt optimization for CLIP-L (50 words, token-reordered)
- **Node 70:** Auto-alpha extraction (parses `#a=XX` from T5-optimized prompt)
- **Nodes 51/52:** `ai4artsed_t5_clip_fusion` — Token-level LERP + append

**Note:** The ComfyUI workflow uses **two different prompts** (CLIP-optimized and T5-optimized) and **auto-alpha calculation**. The Diffusers backend currently uses the same prompt for both encoders and user-controlled alpha.

### Alpha Factor Control

**Range:** -75 to +75, default 0 (normal). Sweet spot: 15–35.

**Frontend (surrealizer.vue):**
```typescript
const alphaFaktor = ref<number>(0)  // Slider default

// Slider UI:
// - 5 labels: "extrem", "invers", "normal", "halluziniert", "extrem"
// - Color gradient: purple → blue → pink
// - Value display shows: α = <value>

// API call (Diffusers backend):
const response = await axios.post('/api/schema/pipeline/legacy', {
  prompt: inputText.value,
  output_config: 'surrealization_diffusers',
  alpha_factor: mappedAlpha.value,  // Raw alpha value, no mapping
  seed: currentSeed.value
})
```

**Backend routing (backend_router.py:1795-1808):**
- Detects `alpha_factor` + `fusion_mode: 't5_clip_alpha'` in diffusers_config
- Routes to `backend.generate_image_with_fusion()` instead of `generate_image()`

### Seed Logic (Intelligent Experimentation)

**Purpose:** Enable iterative experimentation with consistent seeds

**Logic (surrealizer.vue:240-254):**
```typescript
const promptChanged = inputText.value !== previousPrompt.value
const alphaChanged = alphaFaktor.value !== previousAlpha.value

if (promptChanged || alphaChanged) {
  // Keep same seed (user wants to see parameter variation)
  if (currentSeed.value === null) {
    currentSeed.value = 123456789  // First run default
  }
  previousPrompt.value = inputText.value
  previousAlpha.value = alphaFaktor.value
} else {
  // Generate new random seed (user wants different variation)
  currentSeed.value = Math.floor(Math.random() * 2147483647)
}
```

**Rationale:**
- If prompt OR alpha changes → **keep seed** (compare parameter effects)
- If nothing changes → **new seed** (explore variations)

**Testing:**
- Seed exported in metadata JSON for reproducibility
- Backend extracts seed from Node 3 in workflow for output metadata

---

## Migration Path: Adding New Legacy Workflows

### Decision Tree

**Is this workflow stable and tested?**
- **YES** → Create dedicated Vue (Option A)
- **NO** → Add to `direct.vue` dropdown (Option B) [if reactivated]

### Option A: Dedicated Vue (Like Surrealizer)

**When to use:**
- Workshop-tested workflow
- Production-ready feature
- Custom UI needed (sliders, advanced controls)

**Steps (CRITICAL ORDER!):**

1. **FIRST: Create Vue component**
   ```bash
   cp public/ai4artsed-frontend/src/views/surrealizer.vue \
      public/ai4artsed-frontend/src/views/new_workflow.vue

   # Edit new_workflow.vue:
   # - Update API call: output_config: 'new_workflow_legacy'
   # - Customize UI as needed
   ```

2. **THEN: Create pipeline definition**
   ```bash
   # File: devserver/schemas/pipelines/new_workflow.json
   {
     "name": "new_workflow",  // MUST match Vue filename!
     "pipeline_type": "passthrough",
     "skip_stage2": true,
     "description": "Description of workflow",
     "meta": {
       "reusable": false  // Dedicated workflow
     }
   }
   ```

3. **LAST: Update config reference**
   ```bash
   # File: devserver/schemas/configs/interception/new_workflow.json
   {
     "pipeline": "new_workflow",  // Changed from "direct"
     "instruction_type": "new_workflow",
     ...
   }
   ```

4. **Restart backend** (to reload configs)
   ```bash
   ./3_start_backend_dev.sh
   ```

5. **Test routing**
   ```bash
   curl http://localhost:17802/api/config/new_workflow/pipeline | jq '.pipeline_name'
   # Should return: "new_workflow"
   ```

**Why this order matters:**
- ❌ WRONG: Change config first → Backend can't find pipeline → 404 error
- ✅ RIGHT: Create all dependencies first → No breaking changes

### Option B: Add to direct.vue Dropdown (Experimental)

**When to use:**
- Testing new workflow
- Research prototype
- Short-term experiment

**Steps:**

1. **Add to dropdown** (if direct.vue reactivated)
   ```typescript
   // In direct.vue:
   const availableConfigs: OutputConfig[] = [
     { id: 'surrealization_legacy', label: 'Surrealization' },
     { id: 'new_experiment_legacy', label: 'New Experiment' }  // Add here
   ]
   ```

2. **No pipeline changes needed** - uses `direct` pipeline

3. **Promote to dedicated Vue when stable**

---

## Common Pitfalls & Solutions

### Pitfall 1: Pipeline Name ≠ Vue Filename

**Problem:**
```json
// pipelines/surrealizer.json
{"name": "surrealizerWorkflow"}  // ❌ Vue file is surrealizer.vue
```

**Solution:** **EXACT match required (case-sensitive!)**
```json
{"name": "surrealizer"}  // ✅ Matches surrealizer.vue
```

### Pitfall 2: Wrong Order of Operations

**Problem:**
```bash
# ❌ WRONG ORDER:
1. Update config: "pipeline": "new_workflow"
2. Create pipeline
3. Create Vue
# → 404 errors between step 1 and 2!
```

**Solution:**
```bash
# ✅ CORRECT ORDER:
1. Create Vue
2. Create pipeline
3. Update config
# → No 404, all dependencies met
```

### Pitfall 3: Typo in Filename

**Problem:**
```
Pipeline: "surrealizer"
Vue:      "Surrealizer.vue"  // ❌ Capital S
```

**Solution:** Use exact lowercase match
```
Pipeline: "surrealizer"
Vue:      "surrealizer.vue"  // ✅
```

### Pitfall 4: Forgot to Restart Backend

**Problem:**
```bash
# Changed config
curl /api/config/surrealizer/pipeline
# Still returns old pipeline_name ❌
```

**Solution:**
```bash
# Restart backend to reload configs
./3_start_backend_dev.sh

curl /api/config/surrealizer/pipeline
# Now returns new pipeline_name ✅
```

### Pitfall 5: Input Mappings Not Defined

**Problem:**
```python
# Backend tries to inject alpha_factor
# But chunk JSON has no input_mappings.alpha
# → Parameter silently ignored
```

**Solution:** Define `input_mappings` in chunk JSON
```json
{
  "input_mappings": {
    "alpha": {
      "node_id": "50",
      "field": "inputs.value"
    }
  }
}
```

---

## Testing Checklist

### Backend Tests

```bash
# 1. Check pipeline routing
curl http://localhost:17802/api/config/surrealizer/pipeline | jq '.pipeline_name'
# Expected: "surrealizer"

# 2. Check config loads
curl http://localhost:17802/api/config/surrealizer/pipeline | jq '.'
# Should return full pipeline metadata

# 3. Test workflow execution (requires ComfyUI running)
curl -X POST http://localhost:17802/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "surrealizer",
    "input_text": "test prompt",
    "output_config": "surrealization_legacy",
    "alpha_factor": 0,
    "seed": 123456789
  }'
```

### Frontend Tests

1. Navigate to `/execute/surrealizer`
   - ✓ Loads surrealizer.vue (no dropdown visible)
   - ✓ Slider appears (5 labels, gradient)
   - ✓ No console errors

2. Test workflow execution
   - ✓ Enter prompt, adjust alpha slider
   - ✓ Click execute
   - ✓ Progress animation shows
   - ✓ Image appears in output frame
   - ✓ Action toolbar visible (⭐🖨️➡️💾🔍)

3. Test parameter injection
   - ✓ Backend logs show: `[LEGACY-WORKFLOW] Injecting alpha_factor=X`
   - ✓ Backend logs show: `[LEGACY-WORKFLOW] ✓ Injected alpha into node 50`
   - ✓ Different alpha values produce different images

### Integration Tests

1. **Test routing for multiple configs**
   ```bash
   curl http://localhost:17802/api/config/surrealizer/pipeline | jq '.pipeline_name'
   # → "surrealizer"

   curl http://localhost:17802/api/config/displaced_world/pipeline | jq '.pipeline_name'
   # → "displaced_world" (if implemented)
   ```

2. **Test seed reproducibility**
   - Run same prompt + alpha + seed twice
   - ✓ Images should be identical (verify by hash)

3. **Test metadata export**
   - Download generated image metadata JSON
   - ✓ Contains: seed, alpha_factor, workflow_json

---

## Architecture Principles

### Principle 1: Convention Over Configuration

**No explicit routing registry needed.** The system uses filename matching:
```
Pipeline "name" = Vue filename → Automatic routing
```

**Benefits:**
- Less code to maintain
- No registry to update
- Fails gracefully (fallback to text_transformation.vue)

### Principle 2: Dependencies Before References

**Always create dependencies BEFORE referencing them:**
```
Vue exists → Pipeline exists → Config references → No 404 errors
```

### Principle 3: Separation of Concerns

**Three-layer architecture:**
- **Config (Stage 2):** UI metadata, user-facing properties
- **Pipeline (Stage 2):** Execution logic, stage flow
- **Vue (Frontend):** User interface, interaction patterns

Each layer has a single responsibility.

### Principle 4: Data Flow Through input_mappings

**Modern pattern (Session 94+):**
```
Frontend → API (alpha_factor) → Backend Router → input_mappings → Workflow Nodes
```

**No hardcoded node IDs in code!** All injection points defined in chunk JSON.

---

## Historical Context

### Session 93 (Failed)
- Attempted to add slider without understanding routing
- Confused about how to inject simple integer (alpha value)
- Did not properly copy working patterns from other Vues

### Session 94 (Successful)
- Understood convention-based routing
- Followed correct order of operations
- Created dedicated Vue with proper separation
- Documented pattern for future use

**Key Learning:** Past failures were due to:
1. Not understanding filename convention
2. Wrong order of file creation
3. Trying to "improve" instead of copying working code

---

## Future Directions

### Planned Workflows (User mentioned 2-3 more)
- `displaced_world` - Already has config, needs dedicated Vue?
- `relational_inquiry` - Already has config, needs dedicated Vue?
- `digital_photography` - Recently added

### Reactivating Generic Hacking Lab
If needed, `direct.vue` can be reactivated by:
1. Renaming `direct_workflow.json.deactivated` → `direct_workflow.json`
2. Adding experimental workflows to `availableConfigs` array
3. Using for rapid prototyping before promoting to dedicated Vues

---

## References

### Key Architecture Documents
- `ARCHITECTURE PART 01` - 4-Stage Orchestration Flow
- `ARCHITECTURE PART 12` - Frontend Architecture
- `DATA_FLOW_ARCHITECTURE.md` - Custom placeholders pattern

### Code Files
- **Backend routing:** `devserver/my_app/routes/schema_pipeline_routes.py:2915-2955`
- **Frontend routing:** `public/ai4artsed-frontend/src/views/PipelineRouter.vue`
- **Legacy service:** `devserver/my_app/services/legacy_workflow_service.py`
- **Backend router:** `devserver/schemas/engine/backend_router.py:739-753`

### Session Documents
- `docs/sessions/HANDOVER_SURREALIZER_SLIDER_SESSION93.md` - Failed attempt
- `docs/DEVELOPMENT_DECISIONS.md` - Session 94 entry
- Plan file: `/home/joerissen/.claude/plans/hashed-stargazing-dongarra.md`

### Example Workflow
- **Chunk:** `devserver/schemas/chunks/legacy_surrealization.json`
- **Output config:** `devserver/schemas/configs/output/surrealization_legacy.json`
- **Stage2 config:** `devserver/schemas/configs/interception/surrealizer.json`
- **Pipeline:** `devserver/schemas/pipelines/surrealizer.json`
- **Vue:** `public/ai4artsed-frontend/src/views/surrealizer.vue`

---

**Document Status:** Active (2026-02-08)
**Maintainer:** AI4ArtsEd Development Team
**Last Updated:** Session 162 (Hallucinator Diffusers backend, token-level fusion)
