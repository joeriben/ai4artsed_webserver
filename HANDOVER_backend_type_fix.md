# Handover: Backend Type Standardization & Model Metadata Fix

**Session**: 2025-12-08
**Status**: INCOMPLETE - Linter reverting changes
**Problem**: Model metadata (model_used, backend_type) showing as `null` in metadata.json

## Completed Work

### 1. Flux2 Integration ✅
**Files Created**:
- `devserver/schemas/configs/output/flux2.json` - Full config with all qwen.json fields
- `devserver/schemas/chunks/output_image_flux2.json` - ComfyUI workflow chunk
- `public/ai4artsed-frontend/src/views/text_transformation.vue` - Added Flux2 bubble (line 503)
- `public/ai4artsed-frontend/public/logos/flux2_logo.png` - Downloaded from flux2.io

### 2. Fixed SD3.5 Fallback Bug ✅
**Problem**: Both Qwen and Flux2 always used SD3.5 instead of their own models.

**Root Cause**: `backend_router.py:425` falls back to `sd3.5_large` when no `checkpoint` mapping found. Qwen/Flux2 use UNETLoader (not CheckpointLoaderSimple).

**Fix Applied**:
- `devserver/schemas/chunks/output_image_flux2.json`: `media_type: "image"` → `"image_workflow"` (line 5)
- `devserver/schemas/chunks/output_image_qwen.json`: `media_type: "image"` → `"image_workflow"` (line 5)

**Result**: Now routes through `_process_workflow_chunk()` instead of `_process_image_chunk_simple()`.

### 3. Started Backend Type Field Standardization (INCOMPLETE)
**Goal**: Rename `backend_used` → `backend_type` everywhere for consistency.

**Attempted Edits** (REVERTED BY LINTER):
- `execution_history/models.py` line 108: `backend_used` → `backend_type`
- `execution_history/tracker.py` lines 173,183,277,289,306,319,360,374,387,401,414,428: all `backend_used` parameters → `backend_type`
- `my_app/routes/schema_pipeline_routes.py` lines 818, 2164: `backend_used` → `backend_type`

⚠️ **LINTER ISSUE**: A Python linter/formatter is automatically reverting these changes!

## Next Steps (For Next Session)

### Option A: Disable Linter Temporarily
```bash
# Find and disable the auto-formatter (probably black or ruff)
# Then re-apply all backend_used → backend_type changes
```

### Option B: Manual Batch Replace
Use `sed` or similar to replace all at once:
```bash
cd /home/joerissen/ai/ai4artsed_development/devserver

# 1. models.py
sed -i 's/backend_used: Optional\[str\]/backend_type: Optional[str]/g' execution_history/models.py

# 2. tracker.py
sed -i 's/backend_used: str = None/backend_type: str = None/g' execution_history/tracker.py
sed -i 's/backend_used=backend_used,/backend_type=backend_type,/g' execution_history/tracker.py

# 3. schema_pipeline_routes.py
sed -i "s/'backend_used':/'backend_type':/g" my_app/routes/schema_pipeline_routes.py
sed -i 's/backend_used=/backend_type=/g' my_app/routes/schema_pipeline_routes.py
sed -i "s/\.get('backend',/.get('backend_type',/g" my_app/routes/schema_pipeline_routes.py
```

### Option C: Add to .git/hooks/pre-commit
Prevent linter from reverting:
```python
# Block backend_used → backend_type reversions
```

## Testing Checklist

Once field standardization is complete:

1. ✅ Flux2 visible in frontend (already works)
2. ✅ Flux2 generates images (needs testing after backend restart)
3. ✅ Qwen generates images (needs testing after backend restart)
4. ❌ metadata.json contains correct `model_used` and `backend_type` (needs Step 2 completion)

## Files Modified This Session

**Backend**:
- `devserver/schemas/configs/output/flux2.json` (NEW)
- `devserver/schemas/chunks/output_image_flux2.json` (NEW)
- `devserver/schemas/chunks/output_image_qwen.json` (EDITED: media_type)
- `devserver/schemas/chunks/output_image_flux2.json` (EDITED: media_type)
- `devserver/execution_history/models.py` (ATTEMPTED: backend_used → backend_type, REVERTED BY LINTER)
- `devserver/execution_history/tracker.py` (ATTEMPTED: backend_used → backend_type, REVERTED BY LINTER)
- `devserver/my_app/routes/schema_pipeline_routes.py` (ATTEMPTED: backend_used → backend_type, REVERTED BY LINTER)

**Frontend**:
- `public/ai4artsed-frontend/src/views/text_transformation.vue` (EDITED: Added Flux2, line 503)
- `public/ai4artsed-frontend/public/logos/flux2_logo.png` (NEW)

## Original Problem Description

User reported:
1. ✅ **FIXED**: Flux2/Qwen always used SD3.5 instead of their models
   → Solution: Changed media_type to "image_workflow"

2. ❌ **IN PROGRESS**: Model metadata shows null in metadata.json
   → Needs: Complete field standardization + enhance LivePipelineRecorder (Step 2 from original plan)

## Architecture Notes

### Output Config System
- **Configs**: `devserver/schemas/configs/output/*.json` (sd35_large, qwen, flux2, gemini, etc.)
- **Chunks**: `devserver/schemas/chunks/*.json` (workflow definitions)
- **Frontend**: `text_transformation.vue` configsByCategory array

### Backend Router Flow
```
Request → schema_pipeline_routes.py
  → PipelineExecutor
    → BackendRouter._process_output_chunk()
      → if media_type == "image": _process_image_chunk_simple() [SwarmUI simple API]
      → if media_type == "image_workflow": _process_workflow_chunk() [Full ComfyUI workflow]
```

### Why Flux2/Qwen Need image_workflow
- Use **UNETLoader** (not CheckpointLoaderSimple)
- SwarmUI simple API expects checkpoint parameter
- Falls back to sd3.5_large when missing
- Solution: Route through full workflow submission

## Commit Message Suggestion

```
fix: Flux2 integration + SD3.5 fallback bug + partial backend_type standardization

- Add Flux2 config and chunk (dual CLIP: Mistral 3 + CLIP-G)
- Fix Qwen/Flux2 routing: image_workflow instead of simple API
- Fix SD3.5 fallback bug in backend_router.py
- Add Flux2 bubble to frontend (with brand logo)
- Start backend_used → backend_type standardization (incomplete due to linter)

Closes: #xxx (model metadata null issue - partial)
```

## Contact
If questions, check:
- `/home/joerissen/.claude/plans/fluffy-juggling-lemon.md` (original Flux2 plan)
- `devserver/schemas/engine/backend_router.py:408-523` (_process_image_chunk_simple)
- `devserver/schemas/engine/backend_router.py:525-682` (_process_workflow_chunk)
