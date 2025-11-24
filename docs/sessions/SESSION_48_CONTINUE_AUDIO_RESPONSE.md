# Session 48: Continue Audio Response Formatting

**Date:** 2025-11-17
**Previous Session:** Session 47 (SwarmUI Unification + AceStep Audio)
**Context:** Audio generation works, but response formatting needs adjustment for frontend

---

## ✅ Session 47 Achievements (DO NOT REDO)

### SwarmUI Client Unification - COMPLETE ✓
- Unified all ComfyUI operations through `swarmui_client.py` (port 7801)
- Added `/ComfyBackendDirect` passthrough methods for custom workflows
- Deprecated `comfyui_client.py` - no longer used
- **Status:** FULLY WORKING - do not modify

### AceStep Audio Generation - BACKEND COMPLETE ✓
- Implemented `_process_workflow_chunk()` in `backend_router.py:457`
- Supports template-based (`{{PROMPT}}`) and node-based parameter injection
- Audio file successfully generated: `ComfyUI_00345_.mp3` (3.5MB)
- Workflow submission/completion/extraction all working
- **Status:** BACKEND WORKS - audio files are being created

---

## 🎯 Current Task: Fix Audio Response Formatting

### The Problem

**Audio workflows generate files but response lacks `media_output` field:**

**Current Response (BROKEN for frontend):**
```json
{
  "status": "success",
  "final_output": "workflow_generated",
  "metadata": {
    "media_type": "audio",
    "model": "ace_step_v1_3.5b.safetensors"
  }
  // Missing: media_output field!
}
```

**Expected Response (like images):**
```json
{
  "status": "success",
  "media_output": {
    "media_type": "audio",
    "audio_url": "/api/media/download/run_id/filename.mp3",
    "metadata": { ... }
  }
}
```

### Root Cause

The `_process_workflow_chunk()` method returns:
```python
BackendResponse(
    success=True,
    content="workflow_generated",
    metadata={
        'media_files': ['audio/ComfyUI_00345_.mp3'],  ← Data is here
        'media_type': 'audio',
        'prompt_id': '...'
    }
)
```

But somewhere in the pipeline execution flow, this metadata doesn't get converted to the `media_output` structure that the frontend expects.

---

## 🔍 Investigation Steps

### 1. Find the Response Formatter

Search for where `media_output` gets created for images:
```bash
grep -r "media_output" devserver/my_app/routes/
grep -r "image_paths" devserver/my_app/routes/ | grep -i response
```

Likely locations:
- `my_app/routes/schema_pipeline_routes.py`
- `schemas/engine/pipeline_executor.py`
- Response serialization/formatting code

### 2. Compare Image vs Audio Paths

**For Images:** `BackendResponse` with `metadata['image_paths']` → gets converted to `media_output`

**For Audio:** `BackendResponse` with `metadata['media_files']` → needs same conversion

Find where the conversion happens and add audio/video support.

### 3. Implementation

Add conditional logic:
```python
if metadata.get('media_type') == 'image':
    media_output = {
        'media_type': 'image',
        'image_url': construct_image_url(metadata['image_paths'][0]),
        ...
    }
elif metadata.get('media_type') == 'audio':
    media_output = {
        'media_type': 'audio',
        'audio_url': construct_audio_url(metadata['media_files'][0]),
        ...
    }
```

---

## 🧪 Test Commands

**Test audio generation (backend - WORKS):**
```bash
curl -X POST http://localhost:17802/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{"schema":"acestep_instrumental","input_text":"chill lofi beats","execution_mode":"eco"}'
```

**Check backend logs:**
```bash
tail -100 /tmp/backend_ACESTEP_TEST.log | grep -E "(audio|prompt_id|completed)"
```

**Verify audio file exists:**
```bash
ls -lah /home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/audio/ | tail -5
```

---

## 📝 Key Implementation Details

### Backend Flow (WORKING):
1. `_process_output_chunk()` routes to `_process_workflow_chunk()` for audio ✓
2. Template-based mappings detected and applied ✓
3. Workflow submitted via `swarmui_client.submit_workflow()` ✓
4. Completion monitored via `swarmui_client.wait_for_completion()` ✓
5. Audio extracted via `swarmui_client.get_generated_audio(history)` ✓
6. Returns `BackendResponse` with metadata ✓

### Frontend Integration (NEEDS FIX):
7. Response formatter needs to create `media_output` field ❌
8. Audio URL construction ❌
9. Frontend display logic ❌

---

## 📚 Reference Files

**Backend (working - don't modify unless necessary):**
- `devserver/schemas/engine/backend_router.py:457` - `_process_workflow_chunk()`
- `devserver/my_app/services/swarmui_client.py:234` - Custom workflow methods

**To investigate:**
- `devserver/my_app/routes/schema_pipeline_routes.py` - API endpoint
- Where response gets formatted before returning to frontend

**Audio chunk:**
- `devserver/schemas/chunks/output_audio_acestep_instrumental.json`
- `devserver/schemas/configs/output/acestep_instrumental.json`

---

## ⚡ Quick Context

- **Port 7801** = SwarmUI (all operations go through this now)
- **Template-based mappings** = Simple `{{PLACEHOLDER}}` string replacement in workflow JSON
- **Node-based mappings** = Explicit `node_id` + `field` targeting
- Both formats supported in `_process_workflow_chunk()`

---

## 🎯 Success Criteria

1. Audio response includes `media_output` field
2. Frontend displays audio player (not "generated image" placeholder)
3. Audio file downloadable via provided URL
4. No regression in image generation

---

**Estimated Time:** 30-60 minutes
**Priority:** Medium (audio works, just needs proper frontend integration)
