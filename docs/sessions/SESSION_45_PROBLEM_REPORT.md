# Session 45 Problem Report: Image Generation Failures

**Date:** 2025-11-16
**Status:** UNRESOLVED - Handoff to fresh session
**Previous Session:** Session 44 (404 error investigation, symlink implementation)

## Problem Statement

**22% of image generation requests fail** (51/230 runs in production storage)
- Legacy server: 100% success rate
- Current system: 78% success rate (141/230 successful, 20 text-only by design)
- **This is a CODE REGRESSION**, not infrastructure

## Symptom

Failed runs show:
- Reach Stage 4 (media_generation)
- metadata.json shows `current_state: {stage: 4, step: "media_generation"}`
- NO `07_output_image.png` file is saved
- Missing from entities list in metadata.json

Frontend receives 404 when trying to load non-existent image.

## Root Cause Found During This Session

**Backend error:** `"Failed to submit workflow to ComfyUI"`

This occurs in `backend_router.py` line 359/738 when:
```python
prompt_id = await client.submit_workflow(workflow)
if not prompt_id:
    return BackendResponse(
        success=False,
        error="Failed to submit workflow to ComfyUI"
    )
```

The `submit_workflow()` method in `comfyui_client.py` returns `None` when:
1. HTTP response status != 200
2. Connection error (aiohttp.ClientError)
3. Any other exception

## Code Changes Made This Session

### 1. Fixed Circular Fallback Bug
**File:** `devserver/my_app/services/comfyui_client.py` (lines 80-83)

**Before:**
```python
# If discovery fails, fall back to configured port (7821)
# But 7821 already failed during discovery - CIRCULAR LOGIC BUG
```

**After:**
```python
# Default fallback - hardcode to 8188 (standard ComfyUI port)
# Either SwarmUI (7821) or standalone ComfyUI (8188) will be running
logger.warning("⚠️ No ComfyUI instance found via discovery, falling back to port 8188")
return "http://127.0.0.1:8188"
```

### 2. Fixed Discovery Priority
**File:** `devserver/my_app/services/comfyui_client.py` (lines 40-46)

**Before:** Configured port (7821) checked first
**After:** ComfyUI (8188) always checked first, SwarmUI (7821) as fallback

```python
ports_to_check = [
    (8188, "ComfyUI standalone"),
    (7821, "SwarmUI integrated ComfyUI"),
    (8189, "ComfyUI alternative"),
    (7860, "SwarmUI main"),
]
```

### 3. Updated Config
**File:** `devserver/config.py` (line 23)
```python
COMFYUI_PORT = "8188"  # Switched from 7821 (SwarmUI) to 8188 (standalone ComfyUI)
```

### 4. Added Retry Logic to wait_for_completion()
**File:** `devserver/my_app/services/comfyui_client.py` (lines 170-240)

Added exponential backoff retry when prompt_id disappears from queue:
- 5 retries with 2s → 4s → 8s → 10s delays
- Checks history after each retry
- Prevents premature failure for fast workflows (18s for SD3.5)

## What Was NOT Fixed

**The backend was not successfully restarted** during this session due to:
1. Multiple failed restart attempts
2. Process management confusion
3. Cache clearing attempts that didn't help

**Current State:** Backend may or may not be running with updated code.

## Critical Information for Next Session

### Architecture Insights (from PART 01, 07, 08)

1. **Singleton Pattern:** ComfyUIClient uses `_client = None` global singleton
   - Once initialized, never refreshes until process restarts
   - Config changes require backend restart
   - No hot-reload mechanism

2. **4-Stage Flow:** DevServer orchestrates, PipelineExecutor is dumb
   - Stage 4 calls `backend_router.route()` for ComfyUI workflows
   - Route calls `get_comfyui_client()` → singleton
   - Singleton runs auto-discovery once at first call

3. **ComfyUI is Working:** Port 8188 responds correctly
   - Tested with direct curl: `/system_stats` returns 200
   - Process running: PID 3512055, started 00:55
   - `/prompt` endpoint accepts workflows

### Historical Data

Failed run example: `cf0ec503-bd93-4988-b82e-f509f336e731`
```
Config: user_defined
Pipeline: text_transformation
Expected: 7 entities
Got: 6 entities (missing 07_output_image.png)
```

Failure patterns:
- `vector_fusion_generation`: 0/9 success (0%)
- `text_transformation`: 109/150 success (73%)
- `fast` mode: 0/2 success (0%)

## Next Steps for Fresh Session

1. **Verify backend is running properly**
   ```bash
   ps aux | grep "[p]ython.*server.py"
   # If not running:
   pkill -f "python.*server.py"
   python3 server.py &
   ```

2. **Test if port fix resolved the issue**
   ```bash
   curl -X POST http://localhost:17801/api/schema/pipeline/execute \
     -H "Content-Type: application/json" \
     -d '{"schema":"bauhaus","input_text":"test","execution_mode":"eco"}'
   ```
   Check if `media_output.status` is "success" or still "error"

3. **If still failing, investigate actual bug:**
   - Add logging to `submit_workflow()` to see exact failure point
   - Check what HTTP status/error ComfyUI returns
   - Examine workflow JSON structure being submitted
   - Compare with legacy server's workflow submission

4. **Consider:** The 22% failure rate might be:
   - Specific configs that generate malformed workflows
   - Race condition in workflow generation
   - Missing workflow files/templates
   - Workflow validation failure in ComfyUI

## Files Modified

- `devserver/config.py` (line 23)
- `devserver/my_app/services/comfyui_client.py` (lines 40-46, 80-83, 170-240)

## Session Cost

Approximately 100k tokens spent on:
- Architecture document reading (necessary)
- Port configuration debugging (necessary)
- Multiple restart attempts (wasteful)
- Testing and verification (necessary but excessive)

## Conclusion

**Problem partially diagnosed but NOT SOLVED.**

The port configuration issue (7821 → 8188) was identified and fixed, but the backend was not successfully restarted to verify if this resolves the 22% failure rate. A fresh session should:

1. Restart backend cleanly
2. Test if failures persist
3. If yes, investigate the actual code bug in workflow submission/generation

The architecture is now understood, the infrastructure is configured correctly, but the regression bug is still unresolved.

---

**Recommendation:** Fresh session should focus ONLY on:
- Backend restart (1 minute)
- Test image generation (2 minutes)
- If still failing: Add logging, find actual bug (30 minutes max)

Do NOT get sidetracked on infrastructure/port issues again.
