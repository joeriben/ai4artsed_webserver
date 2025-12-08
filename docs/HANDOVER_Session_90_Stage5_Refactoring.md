# Handover: Stage 5 Image Analysis - Universal Helper Refactoring
**Session**: 90 - December 4, 2025
**Status**: Implementation Complete, Testing Failed (JSON Parse Error)

---

## Executive Summary

**Goal**: Refactor Stage 5 from wrong architecture (Session 89) to correct universal helper approach.

**Status**: ✅ Implementation complete, ❌ Testing failed with JSON parse error

**Commit**: `1343607` - All changes safely committed, can be reverted if needed.

---

## What Was Implemented

### 1. Universal Helper Function
**File**: `/devserver/my_app/utils/image_analysis.py` (NEW, 150 lines)

Two main functions:
- `analyze_image(image_path, prompt=None, analysis_type='bildwissenschaftlich')` → str
- `analyze_image_from_run(run_id, prompt=None, analysis_type='bildwissenschaftlich')` → str

**Features**:
- Works with file paths, base64, or data URLs
- 4 framework support: bildungstheoretisch, bildwissenschaftlich, ethisch, kritisch
- Fallback cascade: Parameter → config.py[type][lang] → "Analyze this image thoroughly."
- Auto language selection based on DEFAULT_LANGUAGE
- VRAM management: `keep_alive: "0s"`

### 2. Analysis Prompts in Config
**File**: `/devserver/config.py` (lines 114-227)

```python
IMAGE_ANALYSIS_PROMPTS = {
    'bildwissenschaftlich': {'de': "...", 'en': "..."},  # ✅ Complete (Panofsky)
    'bildungstheoretisch': {'de': "TODO", 'en': "TODO"},  # ⚠️ Needs prompt
    'ethisch': {'de': "TODO", 'en': "TODO"},              # ⚠️ Needs prompt
    'kritisch': {'de': "TODO", 'en': "TODO"}              # ⚠️ Needs prompt
}
```

Only bildwissenschaftlich (Panofsky 4-stage iconological analysis) is complete.

### 3. New Simple Endpoint
**File**: `/devserver/my_app/routes/schema_pipeline_routes.py` (lines 2917-2983)

**Endpoint**: `/api/image/analyze` (POST)

**Request**:
```json
{
    "run_id": "uuid",
    "analysis_type": "bildwissenschaftlich",  // optional, default
    "prompt": "custom prompt"                 // optional
}
```

**Response**:
```json
{
    "success": true,
    "analysis": "full analysis text...",
    "analysis_type": "bildwissenschaftlich",
    "run_id": "uuid"
}
```

**Reduced from 146 lines to 66 lines** (Session 89 → Session 90)

### 4. Deleted Session 89 Code
**File**: `/devserver/my_app/services/ollama_service.py`

**Deleted** (290 lines, lines 308-597):
- `analyze_image_pedagogical()` method
- `_extract_reflection_prompts()` helper
- `_extract_insights()` helper

These were hardcoded, non-reusable, and violated architecture principles.

### 5. Updated Frontend
**File**: `/public/ai4artsed-frontend/src/views/text_transformation.vue`

**Changes**:
- Line 1107: Changed endpoint from `/api/schema/pipeline/stage5` to `/api/image/analyze`
- Lines 1110-1115: Updated request body (removed safety_level, language; added analysis_type)
- Lines 1125-1137: Parse raw text response into structured format
- Lines 1148-1166: Added `extractReflectionPrompts()` and `extractInsights()` helpers

**Kept from Session 89**:
- Universal Action Toolbar (all media types)
- Download Button functionality
- Analysis UI display components

---

## Code Statistics

**Total Changes**:
- 5 files changed
- +342 insertions
- -423 deletions
- **Net reduction: 81 lines**

**Files Modified**:
1. `/devserver/my_app/utils/image_analysis.py` (NEW)
2. `/devserver/config.py` (+114 lines)
3. `/devserver/my_app/routes/schema_pipeline_routes.py` (-80 lines)
4. `/devserver/my_app/services/ollama_service.py` (-290 lines)
5. `/public/ai4artsed-frontend/src/views/text_transformation.vue` (+20 lines)

---

## Current Issue: JSON Parse Error

### Error Message
```
"Image analysis failed: JSON.parse: unexpected character at line 1 column 1 of the JSON data!"
```

### What This Means
Frontend is receiving a **non-JSON response** from the backend. Likely causes:

1. **Backend Error**: Endpoint is crashing and returning HTML error page
2. **Missing Import**: `from my_app.utils.image_analysis import analyze_image_from_run` might be failing
3. **Path Issue**: LivePipelineRecorder not finding image
4. **Model Issue**: Ollama not running or model not loaded

### Where to Debug

**Backend Logs**:
```bash
# Check if backend started successfully
tail -f devserver/logs/app.log

# Check for import errors
grep "ImportError\|ModuleNotFoundError" devserver/logs/app.log

# Check if endpoint is registered
grep "image/analyze" devserver/logs/app.log
```

**Test Endpoint Directly**:
```bash
# Check if endpoint responds
curl -X POST http://localhost:17802/api/image/analyze \
  -H "Content-Type: application/json" \
  -d '{"run_id": "test-123"}'

# Should return JSON (even if 404), not HTML
```

**Check Imports**:
```python
# In Python console:
from my_app.utils.image_analysis import analyze_image_from_run
# Should not raise ImportError
```

**Likely Fix**:
The error is probably in the new helper file. Possible issues:
1. Syntax error in `/devserver/my_app/utils/image_analysis.py`
2. Missing `requests` import (needed for Ollama call)
3. Circular import with `config.py`

---

## Testing Plan (After Bug Fix)

### Prerequisites
1. Backend running: `./devserver/start.sh`
2. Frontend built: `cd public/ai4artsed-frontend && npm run build`
3. Ollama running: `ollama list | grep llama3.2-vision`

### Test Steps
1. **Generate Test Image**:
   - Open frontend
   - Enter any prompt
   - Generate image via Stage 1-4
   - Wait for image to appear

2. **Click Bildanalyse Button** (🔍):
   - Should show loading state
   - Console should log: `[Stage 5] Starting image analysis for run_id: ...`

3. **Verify Analysis Displays**:
   - Analysis text appears below image
   - Reflection questions extracted (bulleted list)
   - Insight tags appear (if any keywords match)
   - Close button (×) collapses section

4. **Test Language**:
   - Change `DEFAULT_LANGUAGE` in config.py to 'en'
   - Restart backend
   - Generate new image
   - Analyze → Should return English analysis

5. **Test Fallback**:
   - Change analysis_type to 'bildungstheoretisch' (has TODO prompt)
   - Should use fallback: "Analyze this image thoroughly."

---

## Known Limitations

1. **Only 1 of 4 frameworks complete**: bildwissenschaftlich (Panofsky) works, others need prompts
2. **No caching**: Each analysis re-generates (could save to recorder)
3. **No analysis history**: Previous analyses not saved
4. **Image-only**: Audio/video analysis not implemented
5. **Simple parsing**: Keyword-based insight extraction (could use NLP)

---

## Next Steps (Priority Order)

### Immediate (Blocking)
1. **Fix JSON Parse Error**:
   - Check backend logs for import/syntax errors
   - Test endpoint with curl
   - Verify helper file syntax
   - Check requests library is available

2. **Verify Ollama**:
   ```bash
   ollama list | grep llama3.2-vision
   ollama run llama3.2-vision:latest "test"
   ```

3. **Test End-to-End**:
   - Generate image
   - Click analyze button
   - Verify analysis appears

### Short-term (Enhancement)
4. **Add Missing Prompts**:
   - bildungstheoretisch: Jörissen/Marotzki framework
   - ethisch: Check legacy code for ethical advisor prompt
   - kritisch: Decolonial & critical media studies prompt

5. **Error Handling**:
   - Better frontend error messages
   - Retry logic for Ollama timeouts
   - Graceful degradation if model unavailable

### Long-term (Future)
6. **Analysis Caching**: Save to LivePipelineRecorder
7. **Analysis History**: Show previous analyses
8. **Multi-framework UI**: Dropdown to select framework
9. **Audio/Video Analysis**: Extend to other media types

---

## Architecture Benefits (vs Session 89)

| Aspect | Session 89 (Wrong) | Session 90 (Correct) |
|--------|-------------------|---------------------|
| **Location** | Hardcoded in ollama_service.py | Universal helper in utils/ |
| **Reusability** | ❌ Locked to one endpoint | ✅ Callable from anywhere |
| **Prompts** | ❌ Hardcoded in Python | ✅ Configurable in config.py |
| **Frameworks** | ❌ Single approach | ✅ 4 theoretical frameworks |
| **Flexibility** | ❌ Fixed prompt | ✅ Custom prompts supported |
| **Code Size** | 436 lines (endpoint + service) | 316 lines (helper + endpoint) |
| **Maintenance** | ❌ Changes in 2 files | ✅ Single helper file |

---

## Files Reference

### New Files
- `/devserver/my_app/utils/image_analysis.py` - Universal helper

### Modified Files
- `/devserver/config.py` (lines 114-227) - Analysis prompts
- `/devserver/my_app/routes/schema_pipeline_routes.py` (lines 2917-2983) - New endpoint
- `/devserver/my_app/services/ollama_service.py` (deleted lines 308-597) - Removed Session 89 code
- `/public/ai4artsed-frontend/src/views/text_transformation.vue` (lines 1107-1166) - Updated frontend

### Stage 5 Directories Created (Empty)
- `/devserver/schemas/chunks/stage5/` - Not used (universal helper approach)
- `/devserver/schemas/pipelines/stage5/` - Not used
- `/devserver/schemas/configs/stage5/` - Not used

**Note**: Originally planned to use pipeline/chunk/config architecture, but pivoted to simpler universal helper approach per user request.

---

## Rollback Plan

If implementation fails completely:

```bash
# Revert to Session 89 code
git revert 1343607

# Or reset to before refactoring
git reset --hard 3027914  # Session 89 commit
```

This restores the old (wrong) architecture but at least makes Stage 5 functional again.

---

## Debugging Commands

```bash
# Check backend running
lsof -i :17802

# Check Ollama running
lsof -i :11434

# Test helper function directly
cd /home/joerissen/ai/ai4artsed_development/devserver
python3 -c "from my_app.utils.image_analysis import analyze_image; print('Import OK')"

# Check for syntax errors
python3 -m py_compile my_app/utils/image_analysis.py

# View endpoint registration
grep -n "api/image/analyze" my_app/routes/schema_pipeline_routes.py

# Check if requests library available
python3 -c "import requests; print('Requests OK')"
```

---

## Contact for Issues

**Frontend Issues**:
- Check browser console for errors
- Verify endpoint URL is correct
- Test with curl to isolate frontend vs backend

**Backend Issues**:
- Check `devserver/logs/app.log`
- Verify imports work
- Test helper function in Python console

**Ollama Issues**:
- Verify model installed: `ollama list`
- Test model works: `ollama run llama3.2-vision:latest "test"`
- Check Ollama logs: `journalctl -u ollama -f` (if systemd service)

---

## Session Context

**User's Original Goal**: Fix Stage 5 architecture violation from Session 89

**Decisions Made**:
1. ❌ Initial plan: Pipeline/Chunk/Config architecture → Too complex
2. ✅ Final plan: Universal helper function → Simple and reusable
3. ✅ 4 frameworks instead of 2 (safety_level removed - not needed for analysis)
4. ✅ Fallback prompt: "Analyze this image thoroughly."

**Key Learning**: Architecture exists to prevent chaos. Session 89's "special endpoint" approach caused confusion about where to put prompts, how to handle language, etc. Session 90's universal helper approach is clean and clear.

---

## Handover Checklist

- [x] All code changes committed (1343607)
- [x] Documentation written (this file)
- [x] Critical bug identified (JSON parse error)
- [x] Debugging steps provided
- [x] Rollback plan provided
- [ ] Bug fixed (pending next session)
- [ ] End-to-end testing (pending bug fix)
- [ ] DEVELOPMENT_LOG.md updated (pending)

---

**Handover Date**: December 4, 2025
**Session**: 90
**Commit**: 1343607
**Status**: Implementation complete, needs debugging
**Next Action**: Fix JSON parse error in new endpoint
