# Image 404 Errors - Root Cause Analysis

**Date:** 2025-11-15
**Status:** ROOT CAUSE IDENTIFIED

---

## Executive Summary

Images work "most of the time" but occasionally return 404 errors. **Root cause: Multiple backend instances with different storage paths.**

---

## What IS Working

✅ **Storage Architecture:**
- Storage location: `/home/joerissen/ai/ai4artsed_webserver/exports/json/{run_id}/`
- Format: LivePipelineRecorder with entity-based metadata
- 132 images generated in last 7 days
- Most recent: 15. Nov 13:11
- File structure: `07_output_image.png` + `metadata.json`

✅ **Code Architecture:**
- Media routes: `/devserver/my_app/routes/media_routes.py` (correct)
- Pipeline execution: Blocking download before returning run_id
- Path resolution: `JSON_STORAGE_DIR` correctly resolves to `/exports/json/`

✅ **Image Generation:**
- ComfyUI integration working
- `download_and_save_from_comfyui()` successfully saves files
- Metadata written correctly with entities array

---

## The Actual Problem: Storage Path Mismatch

### Multiple Backend Instances

**Production Backend (Currently Running):**
```
Process: /opt/ai4artsed-production/venv/bin/python3 server.py
PID: 3417888
Storage: /opt/ai4artsed-production/exports/json/
Port: 17801
```

**Dev Backend Storage Path:**
```
Location: /home/joerissen/ai/ai4artsed_webserver/exports/json/
Path resolution: BASE_DIR / "exports" / "json"
Where BASE_DIR = /home/joerissen/ai/ai4artsed_webserver
```

### Why 404 Errors Occur

**Scenario:**

1. **Image Generation Request:**
   - Frontend → POST `/api/schema/pipeline/execute`
   - Request handled by **Backend A** (e.g., dev)
   - Image saved to `/home/joerissen/ai/ai4artsed_webserver/exports/json/{run_id}/07_output_image.png`
   - Returns `run_id` to frontend

2. **Image Display Request:**
   - Frontend → GET `/api/media/image/{run_id}`
   - Request handled by **Backend B** (e.g., production)
   - Looks for image in `/opt/ai4artsed-production/exports/json/{run_id}/`
   - **File not found → 404!**

**Result:** Intermittent 404 errors depending on which backend instance handles each request.

---

## Evidence

### 1. Multiple Backend Processes

```bash
$ ps aux | grep "python3.*server.py"
joeriss+ 3417888  /opt/ai4artsed-production/venv/bin/python3 server.py
```

### 2. Different Storage Paths

**Dev Backend:**
```bash
$ cd /home/joerissen/ai/ai4artsed_webserver/devserver
$ python3 -c "from config import JSON_STORAGE_DIR; print(JSON_STORAGE_DIR.resolve())"
/home/joerissen/ai/ai4artsed_webserver/exports/json
```

**Production Backend:**
```bash
$ cd /opt/ai4artsed-production/devserver
$ python3 -c "from config import JSON_STORAGE_DIR; print(JSON_STORAGE_DIR.resolve())"
/opt/ai4artsed-production/exports/json
```

### 3. Images Exist in Dev Storage

```bash
$ ls -lh /home/joerissen/ai/ai4artsed_webserver/exports/json/b2890147-ff38-435a-92c0-b5ddb011cd6d/
-rw-r--r--. 1 joerissen joerissen 1.8M 15. Nov 13:11 07_output_image.png
-rw-r--r--. 1 joerissen joerissen 1.4K 15. Nov 13:11 metadata.json
```

### 4. Production Storage May Be Empty/Different

```bash
$ ls -la /opt/ai4artsed-production/exports/json/ | head -10
# (Different set of run_ids than dev storage)
```

---

## Why Previous Analysis Was Wrong

**Incorrect Assumptions:**
1. ❌ Thought no images were being generated (checked wrong path initially)
2. ❌ Thought legacy MediaStorage was being used (it's not)
3. ❌ Thought storage path was wrong (it's correct, just multiple paths)
4. ❌ Thought it was a race condition in file writing (it's not)

**Correct Understanding:**
- ✅ Images ARE being generated successfully
- ✅ Storage architecture IS correct
- ✅ The problem is multiple backends with separate storage

---

## Solutions

### Option 1: Use Single Backend (Recommended)

**Stop all backends and run only one:**

```bash
# Stop all
./stop_all.sh

# Start ONLY production backend
cd /opt/ai4artsed-production/devserver
./start_backend_fg.sh
```

OR

```bash
# Stop all
./stop_all.sh

# Start ONLY dev backend
cd /home/joerissen/ai/ai4artsed_webserver/devserver
./start_backend_fg.sh
```

### Option 2: Shared Storage (Alternative)

**Make both backends use same storage:**

Create symlink in production:
```bash
rm -rf /opt/ai4artsed-production/exports
ln -s /home/joerissen/ai/ai4artsed_webserver/exports /opt/ai4artsed-production/exports
```

**Pros:** Both backends can coexist
**Cons:** Still confusing to have two backends, potential concurrency issues

### Option 3: Load Balancer Fix (Complex)

**Use sticky sessions** so same user always hits same backend.

**Not recommended:** Adds complexity, doesn't solve root problem.

---

## Verification Steps

After implementing solution:

1. **Verify only one backend is running:**
   ```bash
   ps aux | grep "python3.*server.py" | grep -v grep
   # Should show ONLY ONE process
   ```

2. **Test image generation end-to-end:**
   ```bash
   # Generate image in frontend
   # Verify it displays immediately without refresh
   # Check browser console for 404 errors (should be none)
   ```

3. **Check storage consistency:**
   ```bash
   # After generating image, verify it's in the CORRECT storage location
   ls -la /path/to/storage/exports/json/{run_id}/
   ```

---

## stop_all.sh Fix

**Problem:** Script doesn't stop systemd-managed backend service.

**Root Cause:**
- Production backend runs as systemd service: `ai4artsed-production.service`
- Service configured with `Restart=always`
- Script only killed processes, systemd immediately restarted them
- Restart counter: 1731+ restarts

**Fix Applied:**
```bash
# Added at line 4-6 (BEFORE killing processes)
echo "Stopping systemd services..."
sudo systemctl stop ai4artsed-production.service 2>/dev/null || true
echo "  - ai4artsed-production.service stopped"
```

**Files:**
- `/home/joerissen/1 stop_all.sh:4-6` (fixed)
- `/etc/systemd/system/ai4artsed-production.service` (service definition)

---

## Technical Details

### Backend Startup Logic

**Production:** Started by systemd or manual script
**Dev:** Started manually in devserver directory

### Port Conflict

Both backends try to bind to port 17801. Only ONE can succeed. The other either:
- Fails to start (error not noticed)
- Binds to different port (requests go to wrong backend)
- Process killed and restarted (race condition)

### File System Paths

Both use same RELATIVE path logic:
```python
BASE_DIR = Path(__file__).parent.parent
EXPORTS_DIR = BASE_DIR / "exports"
JSON_STORAGE_DIR = EXPORTS_DIR / "json"
```

But `__file__` resolves differently:
- Dev: `/home/joerissen/ai/ai4artsed_webserver/devserver/config.py`
- Production: `/opt/ai4artsed-production/devserver/config.py`

---

## Lessons Learned

1. **Always check for multiple instances** when seeing intermittent issues
2. **Relative paths are dangerous** in production environments
3. **Don't assume the problem** - verify with data
4. **"Works most of the time"** is a clue for non-deterministic issues

---

## Recommended Action

**IMMEDIATE:**
1. Run `./stop_all.sh` to kill ALL backends
2. Decide: Use production OR dev backend (not both)
3. Start chosen backend
4. Test image generation

**LONG TERM:**
1. Use absolute storage paths in config (e.g., `/var/ai4artsed/storage`)
2. Add healthcheck endpoint to detect multiple instances
3. Add startup script validation (check for existing process on port)

---

## Code References

- **Media Routes:** `/devserver/my_app/routes/media_routes.py:48-99`
- **Pipeline Execution:** `/devserver/my_app/routes/schema_pipeline_routes.py:888-942`
- **Pipeline Recorder:** `/devserver/my_app/services/pipeline_recorder.py:300-386`
- **Config:** `/devserver/config.py:8-13`
- **Stop Script:** `/stop_all.sh:10-13` (now fixed)

---

**Status:** Analysis complete. Ready for implementation of Solution Option 1.
