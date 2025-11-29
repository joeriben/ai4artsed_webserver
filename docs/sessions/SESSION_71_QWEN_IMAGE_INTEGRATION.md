# Session 70: Qwen Image Integration

**Date**: 2025-11-25
**Branch**: develop → main
**Status**: ✅ Committed & Pushed (1 commit)

---

## Session Summary

Integrated Qwen Image as a new Stage 4 output config using ComfyUI workflow submission. Critical architectural discovery: Qwen requires `media_type: "image_workflow"` (not `"image"`) due to separate UNET/CLIP/VAE loaders instead of unified checkpoint.

---

## Commits

| Commit | Description |
|--------|-------------|
| `65ebe44` | feat: Add Qwen Image output config with workflow submission |

---

## Work Completed

### 1. Backend Integration

**Files Created**:
- `devserver/schemas/chunks/output_image_qwen.json` (252 lines)
- `devserver/schemas/configs/output/qwen.json` (79 lines)

**Files Modified**:
- `devserver/schemas/chunks/dual_encoder_fusion_image.json` (fixed alpha parameter: 0.5)

**Files Renamed**:
- `qwen_image.json` → `qwen.json` (to match Vue frontend ID)

### 2. Architecture

**Qwen Image Model Stack**:
- **UNET**: `qwen_image_fp8_e4m3fn.safetensors` (Node 37: UNETLoader)
- **CLIP**: `qwen_2.5_vl_7b_fp8_scaled.safetensors` (Node 38: CLIPLoader with `type="qwen_image"`)
- **VAE**: `qwen_image_vae.safetensors` (Node 39: VAELoader)
- **Sampler**: ModelSamplingAuraFlow (Node 66: shift=3.1)

**Key Configuration**:
```json
{
  "media_type": "image_workflow",  // NOT "image"!
  "backend_type": "comfyui",
  "resolution": "1328x1328"
}
```

---

## Critical Architecture Decision: `image_workflow` vs `image`

### The Problem

Initial implementation used `media_type: "image"`, which routed to SwarmUI's Simple Text2Image API (port 7801). This API:
1. Expects `checkpoint` parameter with unified model file
2. Cannot handle separate UNET/CLIP/VAE loaders
3. Defaults to `'sd3.5_large'` when checkpoint missing
4. **Result**: Generated images with SD3.5 instead of Qwen

### The Solution

Changed to `media_type: "image_workflow"`:
1. Routes to ComfyUI Direct workflow submission (port 7821)
2. Submits complete ComfyUI node graph via `/ComfyBackendDirect`
3. Supports separate model loaders and custom sampling
4. **Result**: Qwen models load correctly

### Routing Logic (backend_router.py)

**Line 323-328**:
```python
if media_type == 'image':
    # Use SwarmUI's simple Text2Image API (unified checkpoint only)
    return await self._process_image_chunk_simple(...)
else:
    # Use ComfyUI workflow submission (supports complex workflows)
    return await self._process_workflow_chunk(...)
```

**Line 559**:
```python
if media_type in ['image', 'image_workflow']:
    output_dir = '/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output'
```

### Port Architecture

| `media_type` | API Endpoint | Port | Use Case |
|--------------|--------------|------|----------|
| `"image"` | SwarmUI Simple Text2Image | 7801 | Unified checkpoint models (SD3.5, Flux1, etc.) |
| `"image_workflow"` | ComfyUI Direct Workflow | 7821 | Separate loaders, custom workflows (Qwen, surrealization, audio) |

---

## Why Qwen Is Different

**Unified Checkpoint Models** (SD3.5, SDXL):
- Single `.safetensors` file contains UNET + VAE + CLIP
- Can use Simple Text2Image API
- Example: `sd3.5_large.safetensors`

**Separate Loader Models** (Qwen, surrealization):
- UNET, CLIP, VAE are separate files
- CLIP requires special `type` parameter (e.g., `type="qwen_image"`)
- Custom sampling nodes (e.g., ModelSamplingAuraFlow)
- **Must use workflow submission**

---

## Technical Details

### SwarmUI Workflow Export

Original workflow exported from SwarmUI contains:
- 11 nodes (UNETLoader, CLIPLoader, VAELoader, ModelSamplingAuraFlow, KSampler, VAEDecode, SaveImage, etc.)
- Prompt input: Node 75 (PrimitiveStringMultiline)
- Image output: Node 60 (SaveImage)

### Input Mappings

All parameters mapped to correct nodes:
```json
"prompt": {"node_id": "75", "field": "inputs.value", "source": "{{PREVIOUS_OUTPUT}}"},
"width": {"node_id": "58", "field": "inputs.width", "default": 1328},
"height": {"node_id": "58", "field": "inputs.height", "default": 1328},
"steps": {"node_id": "3", "field": "inputs.steps", "default": 20},
"cfg": {"node_id": "3", "field": "inputs.cfg", "default": 2.5}
```

---

## Debugging Journey

### Issue 1: Config Not Found
**Error**: `Config 'qwen' not found`
**Cause**: File named `qwen_image.json` but Vue sends ID `'qwen'`
**Fix**: Renamed file to `qwen.json` (ConfigLoader uses filename stem as ID)

### Issue 2: SD3.5 Used Instead of Qwen
**Error**: SwarmUI logs show `sd3.5_large.safetensors` instead of Qwen models
**Cause**: `media_type: "image"` routes to Simple API, which expects `checkpoint` parameter
**Fix**: Changed to `media_type: "image_workflow"` for workflow submission

### Issue 3: Models in Wrong Directory
**Error**: ComfyUI couldn't find Qwen model files
**Cause**: User had placed models in incorrect SwarmUI directory
**Fix**: User moved models to correct location
**Note**: This was independent of routing issue - both problems needed fixing

---

## Testing Status

✅ **Completed**:
- Config recognized by backend
- File rename successful
- Routing to ComfyUI Direct confirmed
- Model files accessible after directory fix

⏳ **Pending**:
- Full end-to-end image generation test
- Quality comparison vs SD3.5
- Performance benchmarking (1328x1328 resolution)

---

## Lessons Learned

### 1. Always Consult Architecture Expert First

Started coding without understanding the routing architecture. Should have consulted `devserver-architecture-expert` agent immediately to understand:
- Simple API vs Workflow submission paths
- When to use `"image"` vs `"image_workflow"`
- Port 7801 vs 7821 usage

**Lesson**: Use specialized agents BEFORE coding, not after debugging.

### 2. Filename = Config ID

ConfigLoader uses filename stem (without `.json`) as internal config ID:
- `sd35_large.json` → ID: `"sd35_large"`
- `qwen_image.json` → ID: `"qwen_image"`
- `qwen.json` → ID: `"qwen"`

**Lesson**: Config filename must EXACTLY match Vue frontend ID.

### 3. Not All Image Models Use Simple API

Assumption: All image generation uses SwarmUI Simple Text2Image API.
Reality: Models with separate loaders require full workflow submission.

**Lesson**: Check model architecture (unified vs separate loaders) before choosing `media_type`.

---

## Future Considerations

### Other Models Requiring `image_workflow`

Potential candidates for workflow submission:
- **Flux1** (if using separate TE1/TE2 text encoders)
- **SDXL Refiner** (if using separate base + refiner models)
- **Custom ComfyUI workflows** with special nodes

### Pattern Reusability

This integration establishes a clear pattern:
1. Check if model uses unified checkpoint or separate loaders
2. If separate: use `media_type: "image_workflow"`
3. Export workflow from SwarmUI/ComfyUI
4. Create chunk with full node graph
5. Map parameters via `input_mappings`

---

## Related Sessions

- **Session 69**: Surrealization model selection (also uses `image_workflow`)
- **Session 68**: Gemini 3 Pro integration (cloud API, different pattern)
- **Session 55**: Model selector consolidation (Vue frontend structure)

---

## Files to Review

For understanding this integration:
1. `devserver/schemas/engine/backend_router.py` (lines 323-328, 559)
2. `devserver/schemas/chunks/output_image_qwen.json` (complete workflow)
3. `devserver/schemas/chunks/dual_encoder_fusion_image.json` (reference: another workflow-based model)
4. `docs/ARCHITECTURE PART 05 - Pipeline-Chunk-Backend-Routing.md` (routing architecture)
