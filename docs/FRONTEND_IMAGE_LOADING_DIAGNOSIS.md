# Frontend Image Loading - Complete Diagnosis

**Date:** 2025-11-15
**Issue:** Images not displaying, 404 errors, "Generated Image" placeholder text

---

## Executive Summary

**The image loading architecture is CORRECT.** The problem is NOT the code - it's that **no images are being generated/stored**.

**Evidence:** `/devserver/exports/json/` directory exists but is completely empty.

---

## Complete Flow Analysis

### 1. Frontend Image Request (Phase2CreativeFlowView.vue)

**Line 726:**
```javascript
previewImage.value = `/api/media/image/${runId}`
```

**What happens:**
- Frontend receives `run_id` from backend after generation
- Sets image src to `/api/media/image/{run_id}`
- Browser makes GET request to this URL
- Vite proxy forwards to backend: `http://localhost:17801/api/media/image/{run_id}`

### 2. Vite Proxy Configuration (vite.config.ts)

**Lines 30-34:**
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:17801',
    changeOrigin: true,
  },
```

**Status:** ✅ **CORRECT** - All `/api/*` requests proxied to backend

### 3. Backend Media Serving (media_routes.py)

**Blueprint registration:** Line 43, 54 in `__init__.py` ✅
**Route:** `/api/media/image/<run_id>` (line 48-99)

**Flow:**
```python
@media_bp.route('/image/<run_id>', methods=['GET'])
def get_image(run_id: str):
    # 1. Load recorder from disk
    recorder = load_recorder(run_id, base_path=JSON_STORAGE_DIR)

    # 2. Find image entity in metadata
    image_entity = _find_entity_by_type(recorder.metadata.get('entities', []), 'image')

    # 3. Get filename and serve
    filename = image_entity['filename']
    file_path = recorder.run_folder / filename
    return send_file(file_path, mimetype='image/png')
```

**Status:** ✅ **CORRECT** - Using LivePipelineRecorder (MediaStorage is deprecated)

### 4. Backend Image Storage (schema_pipeline_routes.py)

**Stage 4 (lines 888-907):**
```python
# ComfyUI generation
saved_filename = asyncio.run(recorder.download_and_save_from_comfyui(
    prompt_id=output_value,
    media_type=media_type,
    config=output_config_name,
    seed=seed
))
```

**Response (lines 932-941):**
```python
media_outputs.append({
    'config': output_config_name,
    'status': 'success',
    'run_id': run_id,  # Frontend uses this to request image
    'output': run_id if media_stored else output_result.final_output,
    'media_stored': media_stored
})
```

**Status:** ✅ **CORRECT** - Downloads from ComfyUI and stores via PipelineRecorder

### 5. Storage Structure

**Location:** `/devserver/exports/json/{run_id}/`

**Expected structure:**
```
exports/json/
├── 12345678-1234-1234-1234-123456789abc/
│   ├── metadata.json       # Contains entities array
│   ├── 01_input.txt        # User input
│   ├── 02_translation.txt  # Translated text
│   ├── 03_interception.txt # Transformed prompt
│   └── 06_output_image.png # Generated image ← This is what frontend requests
```

**Actual Status:** ❌ **EMPTY** - No run folders exist

---

## The Real Problem

**The storage directory is EMPTY:**
```bash
$ ls -la /home/joerissen/ai/ai4artsed_webserver/devserver/exports/json/
total 0
drwxr-xr-x. 1 joerissen joerissen 0 15. Nov 13:16 .
drwxr-xr-x. 1 joerissen joerissen 8 15. Nov 13:16 ..
```

**This means:**
1. **Either:** No images have been generated yet (user just refreshing browser)
2. **Or:** Image generation is failing before reaching storage
3. **Or:** Backend is not running
4. **Or:** ComfyUI is not running/accessible

---

## Diagnostic Steps

### Test 1: Is backend running?
```bash
curl http://localhost:17801/api/pipeline_configs_with_properties
```
**Expected:** JSON response with config list
**If fails:** Backend not running, start with `cd devserver && python3 server.py`

### Test 2: Is ComfyUI running?
```bash
curl http://localhost:7821/system_stats
```
**Expected:** JSON response with system stats
**If fails:** ComfyUI not running

### Test 3: Generate test image
```bash
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "sd35_large",
    "input_text": "a red apple",
    "execution_mode": "eco",
    "output_config": "sd35_large"
  }'
```
**Expected:** Returns `{ status: "success", run_id: "..." }`
**Then check:** `ls -la /devserver/exports/json/` should show new folder

### Test 4: Request image
```bash
# Use run_id from Test 3
curl http://localhost:17801/api/media/image/{run_id} > /tmp/test.png
file /tmp/test.png  # Should say "PNG image data"
```

---

## Architecture Validation

### ✅ What's Working:
1. Frontend image URL generation
2. Vite proxy configuration
3. Backend media serving routes
4. LivePipelineRecorder integration
5. Response format (run_id as identifier)

### ❌ What's Broken:
1. **No images in storage** - Either not generating or failing silently
2. **Empty exports/json/** - No runs created

### 🔍 What's Unknown:
1. Is backend actually running?
2. Is ComfyUI accessible?
3. Are image generation requests actually reaching Stage 4?
4. Are there errors in backend logs?

---

## Historical Context

**MediaStorage vs PipelineRecorder:**
- Old system: `MediaStorageService` (deprecated weeks ago)
- New system: `LivePipelineRecorder` (Session 29+)
- Migration status: ✅ Complete (media_routes.py uses PipelineRecorder)

**PWA Service Worker:**
- Removed in previous session due to caching chaos
- Anti-cache meta tags added to index.html
- **Not related to current issue** (404s are from missing files, not cache)

---

## Next Steps

1. **Verify backend is running** - Check if port 17801 responds
2. **Check backend logs** - Look for errors during image generation
3. **Test image generation** - Create one test image end-to-end
4. **Verify ComfyUI connection** - Ensure ComfyUI is accessible

**DO NOT:**
- Rewrite the architecture (it's correct!)
- Add workarounds (fix the root cause)
- Blame caching (storage is empty, not cache issue)

---

## Code References

- **Frontend:** `/public/ai4artsed-frontend/src/views/Phase2CreativeFlowView.vue:726`
- **Vite Proxy:** `/public/ai4artsed-frontend/vite.config.ts:30-34`
- **Media Routes:** `/devserver/my_app/routes/media_routes.py:48-99`
- **Pipeline Exec:** `/devserver/my_app/routes/schema_pipeline_routes.py:888-942`
- **Storage Path:** `/devserver/exports/json/{run_id}/`
- **Config:** `/devserver/config.py:12-13` (JSON_STORAGE_DIR definition)

---

**Conclusion:** The code is fine. Find out why images aren't being generated in the first place.
