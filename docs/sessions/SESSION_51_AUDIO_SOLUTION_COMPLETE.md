# Session 51: Audio Generation Solution - Implementation Complete

**Date:** 2025-11-17
**Status:** ✅ CODE COMPLETE - Needs Testing
**Branch:** develop

---

## Session Overview

Successfully recovered from Session 50's critical breakage and implemented complete audio generation solution using filesystem-based copying.

---

## What Was Accomplished

### 1. Restored Broken swarmui_client.py

**Problem:** Session 50 used `git checkout` which deleted uncommitted workflow methods

**Solution:** Recreated workflow methods by:
- Consulting `comfyui_client.py` as reference implementation
- Adapting for SwarmUI's proxy endpoints (`/ComfyBackendDirect/prompt`, `/ComfyBackendDirect/history`)

**Methods Added** (my_app/services/swarmui_client.py:223-383):
```python
async def submit_workflow(workflow) -> Optional[str]
    # Submits to SwarmUI proxy: /ComfyBackendDirect/prompt
    # Returns prompt_id

async def wait_for_completion(prompt_id, timeout=300) -> Optional[Dict]
    # Polls /ComfyBackendDirect/history/{prompt_id} every 2 seconds
    # Returns history dict when complete

async def get_generated_audio(history_entry) -> List[str]
    # Extracts audio file paths from history

async def get_generated_video(history_entry) -> List[str]
    # Extracts video file paths from history
```

### 2. Implemented Filesystem-Based Audio Extraction

**Problem:** ComfyUI history parsing unreliable for non-image media

**Solution:** Direct filesystem access (backend_router.py:553-598)

**Implementation:**
```python
# Find most recent audio file
output_dir = '/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/audio'
files = glob.glob(f"{output_dir}/*.mp3")
filesystem_path = max(files, key=os.path.getmtime)

# Return in metadata for handler to copy
metadata = {
    'filesystem_path': filesystem_path,  # Full path for direct copy
    'media_type': 'audio',
    ...
}
```

### 3. Direct File Copy Implementation

**Location:** schema_pipeline_routes.py:897-926

**Logic:**
```python
if output_value == 'workflow_generated':
    filesystem_path = output_result.metadata.get('filesystem_path')
    if filesystem_path:
        # Direct copy (no downloading)
        output_filename = f"07_output_{media_type}.mp3"
        dest_path = os.path.join(recorder.run_dir, output_filename)
        shutil.copy2(filesystem_path, dest_path)
        logger.info(f"[RECORDER] ✓ Copied {media_type} from filesystem")
```

**Advantages:**
- No SwarmUI API dependency for file download
- Works around ComfyUI's poor non-image media handling
- Simple, direct copy from known location
- Same approach can be used for video files

---

## Frontend Media Access

**URL Pattern:** `/api/media/audio/{run_id}`

**Backend Endpoint:** `media_routes.py:102-155` (already implemented)

**Flow:**
1. Frontend makes request: `GET /api/media/audio/{run_id}`
2. Backend loads metadata from `exports/json/{run_id}/metadata.json`
3. Backend finds entity with type `'output_audio'`
4. Backend serves `exports/json/{run_id}/07_output_audio.mp3` with MIME type `audio/mpeg`
5. Frontend `<audio>` element streams and plays file

**Frontend API Service:** `api.ts:325-327`
```typescript
getMediaUrl(run_id, 'audio')  // Returns '/api/media/audio/{run_id}'
```

---

## Files Modified

### 1. my_app/services/swarmui_client.py
- **Lines 223-383:** Added workflow submission methods
- **Status:** Ready for commit

### 2. schemas/engine/backend_router.py
- **Lines 301-598:** Added workflow chunk processing and filesystem extraction
- **Key Change:** Returns `filesystem_path` instead of `media_paths`
- **Status:** Needs testing, then commit

### 3. my_app/routes/schema_pipeline_routes.py
- **Lines 897-926:** Modified `workflow_generated` handler for filesystem copy
- **Key Change:** Uses `shutil.copy2()` instead of `download_and_save_from_swarmui()`
- **Status:** Needs testing, then commit

---

## Testing Status

**Workflow Execution:** ✅ VERIFIED
- Workflows submit successfully via `/ComfyBackendDirect/prompt`
- `wait_for_completion()` polls and detects completion
- Test run: `69bc0e70-57a6-4d47-b5c4-557e67d2297f` completed in 56 seconds

**Filesystem Extraction:** ✅ VERIFIED
- Audio file found: `/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/audio/ComfyUI_00349_.mp3`
- File path logged correctly

**File Copy:** ⚠️ NOT YET VERIFIED
- Python bytecode caching prevented new code from loading
- Metadata showed old keys (no `filesystem_path`)
- Direct copy code not executed

---

## Next Session Tasks

### Critical: Test with Caching Disabled

Run backend with bytecode caching disabled to verify file copy:

```bash
cd /home/joerissen/ai/ai4artsed_webserver/devserver

# Option 1: Environment variable
export PYTHONDONTWRITEBYTECODE=1
python3 server.py

# Option 2: Python flag
python3 -B server.py
```

**Test Command:**
```bash
curl -X POST http://localhost:17802/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{"schema":"dada","input_text":"test","output_config":"acestep_instrumental","execution_mode":"eco","safety_level":"off"}'
```

**Success Criteria:**
1. Log shows: `[RECORDER] ✓ Copied audio from filesystem: 07_output_audio.mp3`
2. File exists: `exports/json/{run_id}/07_output_audio.mp3`
3. File is playable MP3 audio
4. Frontend can access via `/api/media/audio/{run_id}`

### Optional: Permanent Cache Disable for Dev

Add to beginning of `server.py`:
```python
import sys
sys.dont_write_bytecode = True
```

Or create `.env` file with:
```
PYTHONDONTWRITEBYTECODE=1
```

---

## Architecture Notes

### Why Filesystem Approach?

**ComfyUI/SwarmUI Limitations:**
- History parsing unreliable for audio/video
- No direct file path return (unlike images)
- API doesn't provide media download endpoints for non-images

**Filesystem Benefits:**
- Predictable file locations
- No API dependency
- Faster (no HTTP request/response cycle)
- Works for any media type

### File Storage Locations

**ComfyUI Output:**
- Audio: `/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/audio/*.mp3`
- Video: `/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/video/*.mp4`

**Application Storage:**
- Audio: `exports/json/{run_id}/07_output_audio.mp3`
- Video: `exports/json/{run_id}/07_output_video.mp4`

---

## Known Issues

### 1. Python Bytecode Caching

**Problem:** Changed code not loaded due to .pyc files
**Solution:** Use `PYTHONDONTWRITEBYTECODE=1` or `python3 -B`
**Permanent Fix:** Add to server.py startup

### 2. Metadata "expected_outputs" Wrong Type

**Observation:** Metadata shows `"output_image"` even for audio workflows
**Impact:** Cosmetic only - doesn't affect file serving
**Status:** Low priority, can be fixed later

---

## Git Status

**Modified (Uncommitted):**
- `my_app/services/swarmui_client.py` - Workflow methods
- `my_app/services/comfyui_client.py` - (unrelated changes)
- `schemas/engine/backend_router.py` - Workflow chunk + filesystem
- `my_app/routes/schema_pipeline_routes.py` - Filesystem copy handler
- `config.py` - (unrelated changes)
- `public_dev/index.html` - (unrelated changes)

**Recommendation:** Test audio generation, then commit all working changes together with message:
```
feat: Add audio/video workflow support with filesystem extraction

- Recreate swarmui_client workflow methods (submit, wait, extract)
- Implement filesystem-based media file detection for ComfyUI
- Add direct file copy for audio/video to avoid API limitations
- ComfyUI history parsing unreliable for non-image media
```

---

## Critical Lessons Learned

1. **ALWAYS commit working code immediately** - Uncommitted work from Session 47 was permanently lost
2. **Python bytecode caching is dangerous** - Use `PYTHONDONTWRITEBYTECODE=1` for dev
3. **Check git history before using `git checkout`** - Verify file exists in commits first
4. **Filesystem approach is pragmatic** - When APIs are unreliable, use direct filesystem access

---

## Success Metrics (For Next Session)

- [ ] Audio file appears in `exports/json/{run_id}/07_output_audio.mp3`
- [ ] File is valid MP3 (playable)
- [ ] Frontend can load audio via `/api/media/audio/{run_id}`
- [ ] Browser's `<audio>` element plays the file
- [ ] Metadata correctly updated (entity saved)

Once verified, audio generation will be fully functional end-to-end.
