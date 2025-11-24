# Session 50: Audio Problem Investigation & Critical Error

**Date:** 2025-11-17
**Status:** FAILED - Broke swarmui_client.py, system needs restoration
**Branch:** develop

---

## Critical Error - MUST FIX FIRST

**I broke `my_app/services/swarmui_client.py` by using `git checkout` without checking git history first.**

The file is now missing workflow support methods (`submit_workflow`, `wait_for_completion`, `get_generated_audio`, etc.) that were added in Session 47.

**To restore:**
```bash
cd /home/joerissen/ai/ai4artsed_webserver/devserver
git show 924b1b6:devserver/my_app/services/swarmui_client.py > my_app/services/swarmui_client.py
```

Or restore from production/backup if available.

---

## Audio Problem - What I Found

**Problem:** Audio generation works (ComfyUI creates files) but files not saved to exports/json.

**Root Cause:** ComfyUI history parsing is unreliable for non-image media.
- `swarmui_client.get_generated_audio()` returns empty list
- History DOES contain file data: `{'filename': 'ComfyUI_00348_.mp3', 'subfolder': 'audio', 'type': 'output'}`
- Method code looks correct but doesn't extract files

**Solution Identified:**
Use filesystem-based approach instead of history parsing:
- Audio files are in: `/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/output/audio/`
- After workflow completes, list files in directory
- Copy most recent file to `exports/json/{run_id}/07_output_audio.mp3`

**Partial Implementation:**
Added filesystem extraction to `schemas/engine/backend_router.py:553-582` but CANNOT TEST until swarmui_client.py is restored.

---

## Session 49 Fix (Still Intact)

File: `my_app/routes/schema_pipeline_routes.py:897-907`

Added `workflow_generated` handler for audio/video media storage. This will work once the file extraction issue is resolved.

---

## Files Modified This Session

1. `schemas/engine/backend_router.py` - Added filesystem-based media extraction
2. `my_app/services/swarmui_client.py` - BROKEN, needs restoration

---

## Next Session Tasks

1. **CRITICAL:** Restore swarmui_client.py from commit 924b1b6
2. Test filesystem-based audio extraction
3. If working, audio files should be saved to exports/json
4. Still TODO: Frontend needs to send `output_config` parameter for audio requests

---

## Architecture Note

ComfyUI/SwarmUI treat non-image media poorly. History parsing is unstable. The pragmatic solution is to use filesystem directly for audio/video, which avoids their API limitations.

Consider alternative backends for audio/video in the future (e.g., if better APIs available).
