# Session 49: Audio Generation Problem - Detailed Analysis

**Date:** 2025-11-17
**Status:** INCOMPLETE - Root cause identified, needs frontend fix
**Commits:** 6a8f3b0 (partial backend fix)

---

## Executive Summary

Audio generation via ComfyUI/SwarmUI **works** (files created), but audio files are **NOT being saved** to run storage (`exports/json/{run_id}/`). Frontend displays "generated image" instead of audio player.

**Root Cause:** Two-part problem:
1. ✅ **Backend (PARTIALLY FIXED):** Missing handler for `workflow_generated` outputs
2. ❌ **Frontend/Backend Integration (NOT FIXED):** Audio output config not being selected when user clicks audio button

---

## Evidence: Failed Audio Runs

### Run 1: `05071e91-230d-4ad8-996e-8d4fed31ba2d`
**When:** 2025-11-17 08:54 (morning)
**Config:** `dada` (interception config)
**Expected:** Audio output via `acestep_instrumental`
**Actual:**
- ✅ Stage 1: Translation complete → `02_input.txt`, `03_translation.txt`
- ✅ Stage 1: Safety complete → `04_safety.json`
- ✅ Stage 2: Interception complete → `05_interception.txt`
- ✅ Stage 3: Pre-output safety → `06_safety_pre_output.json`
- ❌ Stage 4: **NO audio file saved** (missing `07_output_*.mp3`)
- Status: `progress: "6/6"` but media file missing

### Run 2: `65c18afd-ec59-40fd-b881-bd6f979ad739`
**When:** 2025-11-17 11:55 (second attempt)
**Config:** `dada`
**Actual:**
- Only `01_config_used.json` and `metadata.json`
- Status: `progress: "1/6"` (incomplete)
- No stage outputs saved at all

---

## Problem Analysis

### Part 1: Backend Media Storage (PARTIALLY FIXED)

**File:** `my_app/routes/schema_pipeline_routes.py:885-930`

**The Issue:**
Stage 3-4 loop media storage dispatcher had these cases:

```python
if output_value == 'swarmui_generated':
    # Images: use metadata['image_paths']
elif output_value.startswith('http'):
    # API-based: download from URL
else:
    # ComfyUI: treat as prompt_id
```

Missing case for `output_value == 'workflow_generated'` (audio/video chunks).

**Fix Applied (Commit 6a8f3b0):**
Added elif branch at line 897:

```python
elif output_value == 'workflow_generated':
    media_paths = output_result.metadata.get('media_paths', [])
    saved_filename = asyncio.run(recorder.download_and_save_from_swarmui(
        image_paths=media_paths,
        media_type=media_type,
        config=output_config_name,
        seed=seed
    ))
```

**Status:** ✅ Committed, but never triggered because of Part 2 issue.

---

### Part 2: Output Config Selection (NOT FIXED - MAIN PROBLEM)

**The Real Issue:**

When user clicks audio button for `dada` in frontend, the backend is **NOT executing audio output config**. Instead:

1. Frontend sends request (need to verify what parameters)
2. Backend receives config name: `dada`
3. Backend should detect audio request and select `acestep_instrumental`
4. **But instead:** Backend selects default image config (e.g., `sd35_large`)
5. Stage 4 tries to generate IMAGE, not audio
6. No audio file ever gets created

**Evidence:**
- Run metadata shows `expected_outputs: ["output_image"]` (not `output_audio`)
- Both failed runs tried to generate images, not audio
- `metadata['current_state']` shows Stage 4 started but failed

**Where to Fix:**

Need to investigate `schema_pipeline_routes.py` around line 385:

```python
output_config = data.get('output_config')  # From frontend request
```

Then check output config selection logic around line 900-950 to see why audio configs not being selected.

---

## System Architecture (For Context)

### DevServer Entity Structure

**Pipelines:**
- `text_transformation` (jugendsprache, dada, bauhaus)
- `single_text_media_generation` (output configs)
- Others...

**Configs:**
- **Interception Configs:** `dada`, `jugendsprache`, `bauhaus` (in `schemas/configs/interception/`)
- **Output Configs:** `sd35_large`, `acestep_instrumental`, `gpt_image_1` (in `schemas/configs/output/`)

**Chunks:**
- Processing chunks: `translate_to_english`, `enhance_prompt`, etc.
- Output chunks: `output_audio_acestep_instrumental`, `dual_encoder_fusion_image`, etc.

### Request Flow

**User Action:** Clicks audio button for `dada`
**Frontend Sends:** `{"schema": "dada", "output_config": "acestep_instrumental", ...}` (hypothesis - needs verification)
**Backend Should:**
1. Stage 1-2: Execute `dada` interception
2. Stage 3: Pre-output safety check
3. Stage 4: Execute `acestep_instrumental` output config
4. Download audio from SwarmUI
5. Save to `exports/json/{run_id}/07_output_*.mp3`
6. Return `media_output` field with audio URL

**Backend Actually Does:**
1. ✅ Stage 1-2: Interception works
2. ✅ Stage 3: Safety works
3. ❌ Stage 4: Executes IMAGE config instead of audio
4. ❌ Image generation fails (SwarmUI error)
5. ❌ No media file saved

---

## Next Session Tasks

### 1. Investigate Output Config Selection

**Find where audio output config should be selected:**

```bash
grep -n "output_config.*audio\|acestep" my_app/routes/schema_pipeline_routes.py
grep -n "configs_to_execute\|output_config_name" my_app/routes/schema_pipeline_routes.py | head -20
```

**Questions to answer:**
- How does frontend request audio vs image output?
- Where does backend parse `output_config` parameter?
- Why is `sd35_large` being selected instead of `acestep_instrumental`?
- Is there output config lookup logic based on `media_type`?

### 2. Test Complete Flow

**Proper test command (hypothesis):**

```bash
curl -X POST http://localhost:17802/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "dada",
    "input_text": "epic drums and bass",
    "output_config": "acestep_instrumental",
    "execution_mode": "eco"
  }'
```

**Expected result:**
```json
{
  "status": "success",
  "media_output": {
    "media_type": "audio",
    "run_id": "{uuid}",
    "config": "acestep_instrumental",
    "output": "{run_id}",
    "media_stored": true
  }
}
```

**Verify:**
```bash
ls /home/joerissen/ai/ai4artsed_webserver/exports/json/{run_id}/
# Should contain: 07_output_*.mp3
```

### 3. Frontend Investigation

**Check how audio button works:**

```bash
grep -r "output_config\|acestep\|audio.*button" public/ai4artsed-frontend/src/
```

**Verify request payload:**
- Does frontend send `output_config` parameter?
- Or does it send `media_type: "audio"`?
- Or something else entirely?

### 4. Fix Frontend/Backend Integration

Once output config selection logic is found, ensure:
- Audio button request triggers correct output config
- Backend selects `acestep_instrumental` when audio requested
- Stage 4 executes audio chunk, not image chunk
- Audio file gets downloaded and saved (my fix should handle this)

---

## Technical Details

### Backend Router Returns (From Session 47)

**When audio chunk executes successfully:**

```python
BackendResponse(
    success=True,
    content="workflow_generated",
    metadata={
        'chunk_name': 'output_audio_acestep_instrumental',
        'media_type': 'audio',
        'prompt_id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
        'media_files': ['audio/ComfyUI_00345_.mp3'],  # Relative path
        'media_paths': ['/full/path/to/ComfyUI/output/audio/ComfyUI_00345_.mp3'],  # Absolute
        'swarmui_available': True,
        'seed': 123456,
        'workflow_completed': True
    }
)
```

**My Session 49 fix** correctly handles this in media storage, extracting `media_paths` and downloading the file.

### File Organization

**ComfyUI generates audio:**
- Path: `/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/audio/ComfyUI_XXXXX_.mp3`

**Should be saved to:**
- Path: `/home/joerissen/ai/ai4artsed_webserver/exports/json/{run_id}/07_output_audio.mp3`

**Frontend accesses via:**
- URL: `/api/media/download/{run_id}/07_output_audio.mp3`

---

## Code References

### Backend Files
- `my_app/routes/schema_pipeline_routes.py:385` - `output_config` parameter parsing
- `my_app/routes/schema_pipeline_routes.py:897-907` - Session 49 fix (workflow_generated handler)
- `my_app/routes/schema_pipeline_routes.py:900-970` - Output config selection logic (INVESTIGATE)
- `my_app/services/pipeline_recorder.py:343` - Audio file saving logic
- `schemas/engine/backend_router.py:457-607` - `_process_workflow_chunk()` (audio generation)

### Frontend Files (TO INVESTIGATE)
- Check how audio button sends request
- Verify `output_config` or `media_type` parameter
- Find where "generated image" text comes from

### Config Files
- `schemas/configs/interception/dada.json` - Used in failed runs
- `schemas/configs/output/acestep_instrumental.json` - Audio output config
- `schemas/chunks/output_audio_acestep_instrumental.json` - Audio chunk definition

---

## Session 49 Summary

**What I Fixed:**
- Added `workflow_generated` handler for audio/video media storage (+11 lines)
- Follows existing pattern (swarmui_generated → workflow_generated)
- Commit: 6a8f3b0

**What's Still Broken:**
- Output config selection NOT choosing audio when requested
- Frontend integration (audio button → backend audio config)
- Audio files NOT being saved to run storage

**Why My Fix Wasn't Enough:**
I fixed the download/storage step, but the audio output config is never being executed in the first place. Need to fix output config selection logic BEFORE my storage fix can help.

---

## Next Steps

1. Find where `output_config` parameter is used to select which config to execute
2. Add logging to understand why audio config not being selected
3. Fix output config selection to honor frontend audio request
4. Test complete flow end-to-end
5. Verify audio appears in exports/json and frontend displays correctly

---

**Key Insight:** The problem is in **output config selection**, not media storage. My fix addresses storage (Part 2) but Part 1 (selection) is broken.
