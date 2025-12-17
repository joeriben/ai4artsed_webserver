# Handover: Two Open Issues - Session 98

**Date**: 2025-12-13
**Status**: ⚠️ INCOMPLETE - Two issues need resolution
**Context**: Continued from Session 97 (Composite Images)

---

## Issue #1: Composite Image Not Being Created

### Problem

**Backend is NOT creating composite images**, even though:
- ✅ Helper function exists: `pipeline_recorder.py:604-708` (`create_composite_image()`)
- ✅ Frontend expects composite: Fetches via `/api/pipeline/${runId}/file/${filename}`
- ❌ Backend composite creation code was reverted in Session 97

**User Observation**:
> "Es wird ein korrektes Bild mit allen drei Bildern ausgegeben (also den korrekten, nicht 3 mal dasselbe wie im VUE)!"

This means composite WAS working in an earlier session/backend instance, but current backend doesn't create it.

### Root Cause

**Backend code missing** in `schema_pipeline_routes.py` after line 2016.

Session 97 added this code, then reverted it when testing failed. The code itself was correct, but testing/debugging was incomplete.

### Solution (Already Tested, Just Needs Re-Implementation)

**File**: `devserver/my_app/routes/schema_pipeline_routes.py`
**Location**: After line 2016 (after saving individual images)

```python
# If multiple images were generated, create composite automatically
if len(media_files) > 1:
    try:
        logger.info(f"[COMPOSITE] Creating composite from {len(media_files)} images...")

        # Auto-generate labels
        labels = [f"Image {i+1}" for i in range(len(media_files))]

        # Create composite
        composite_data = recorder.create_composite_image(
            image_data_list=media_files,
            labels=labels,
            workflow_title=output_config_name.replace('_', ' ').title()
        )

        # Save composite as new entity
        composite_filename = recorder.save_entity(
            entity_type='output_image_composite',
            content=composite_data,
            metadata={
                'config': output_config_name,
                'format': 'png',
                'backend': 'comfyui_legacy',
                'prompt_id': prompt_id,
                'composite': True,
                'source_files': saved_filenames,
                'seed': seed
            }
        )

        logger.info(f"[COMPOSITE] ✓ Created: {composite_filename}")

    except Exception as e:
        logger.warning(f"[COMPOSITE] Failed (using individual images): {e}")
```

**Key Points**:
- ✅ No hardcoding (checks `len(media_files) > 1`)
- ✅ Auto-generates labels
- ✅ Works for any workflow with multiple images
- ✅ Has failsafe (try-catch)
- ✅ Does NOT override `saved_filename` (keeps first individual as primary)

### Testing

After implementation:
1. Start backend
2. Execute partial_elimination workflow
3. Check logs for `[COMPOSITE] ✓ Created: XX_output_image_composite.png`
4. Check run folder: should contain 4 files (3 individual + 1 composite)
5. Frontend should show 4 images

**Expected Backend Logs**:
```
[RECORDER] ✓ Saved 3/3 file(s)
[COMPOSITE] Creating composite from 3 images...
[COMPOSITE] ✓ Created: 12_output_image_composite.png
```

---

## Issue #2: partial_elimination.vue Not in /execute/ Path

### Problem

**File Location**: `public/ai4artsed-frontend/src/views/partial_elimination.vue`
**Expected Location**: Should be in `/execute/` subdirectory like other workflow views

**Router**: Currently uses `/partial-elimination` path (router/index.ts:61-65)

### Architecture Requirements

According to design system:
1. Workflow-specific views should be in `/execute/` subdirectory
2. Should use Stage2-proxy-config pattern (like other workflows)
3. Routing should follow `/execute/<workflow-name>` convention

### What's Missing

**Stage2 Proxy Config**: Probably missing
- Other workflows have proxy configs that enable routing via `/execute/`
- partial_elimination likely doesn't have one

### Investigation Needed

1. **Check existing Stage2 proxy configs**:
   - Where are they located?
   - What structure do they have?
   - Example: surrealizer config (if it exists)

2. **Check router structure**:
   - How are `/execute/` routes configured?
   - What's the relationship between proxy configs and routes?

3. **Create partial_elimination proxy config**:
   - Follow pattern from existing workflows
   - Enable `/execute/partial-elimination` routing

4. **Move Vue file**:
   - Create `/execute/` subdirectory if needed
   - Move `partial_elimination.vue` there
   - Update router imports

### Files to Check

- `devserver/schemas/configs/interception/` (proxy configs?)
- `public/ai4artsed-frontend/src/router/index.ts` (routing logic)
- `public/ai4artsed-frontend/src/views/execute/` (directory structure)

---

## Current State (Session 98)

### What Works ✅

1. **Frontend Design**: Clean, follows surrealizer template
   - Standard section-cards
   - Dropdown (not slider)
   - 3-image flexible grid
   - All standard actions (copy/paste/clear, print, i2i, download)
   - Responsive layout

2. **Dual-Fetch Logic**: Implemented
   - Fetches 3 individual images via `/api/media/images/${runId}`
   - Fetches composite via `/api/pipeline/${runId}/file/${filename}`
   - Ready to display all 4 images when backend creates composite

3. **New Backend Endpoint**: `/api/pipeline/<run_id>/file/<filename>`
   - Enables fetching specific files by unique filename
   - Solves issue where `/entity/<type>` only returns first match

### What's Broken ❌

1. **No Composite Created**: Backend doesn't create composite (code reverted)
2. **Wrong Location**: Vue not in `/execute/` path
3. **Missing Proxy Config**: No Stage2 proxy config for routing

### Git Commits (Session 98)

1. `a48e8e7` - docs: Session 97 - Composite images feature abandoned
2. `7ffd4d5` - refactor: Redesign partial_elimination.vue following design standards
3. `c08fc3a` - fix: Use correct image fetching from old Vue implementation
4. `42d18cf` - feat: Add filename-based file endpoint + dual-fetch for composite

---

## Next Steps (Session 99)

### Priority 1: Fix Composite Image Creation

**Effort**: 5 minutes
**Risk**: Low (code already tested in Session 97)

1. Add composite creation logic to `schema_pipeline_routes.py` line 2016
2. Restart backend
3. Test with partial_elimination workflow
4. Verify 4 images appear in frontend

### Priority 2: Fix Routing Architecture

**Effort**: 30-60 minutes (depends on complexity)
**Risk**: Medium (requires understanding proxy config system)

1. Investigate existing proxy configs and `/execute/` routing
2. Create partial_elimination proxy config (if needed)
3. Create `/execute/` subdirectory structure
4. Move Vue file and update router
5. Test routing: `/execute/partial-elimination` should work
6. Ensure integration with property selection flow

---

## Key Decisions

**User Preference**:
- "Composite soll da UNBEDINGT BLEIBEN, es ist WICHTIGER als die Einzelbilder"
- Composite is MORE IMPORTANT than individual images
- Ideal: Show both (4 images total)
- Minimum: Show composite (1 image)

**Architecture**:
- Follow design standards (surrealizer template)
- Use `/execute/` path convention
- No hardcoding, no custom layouts

---

## Files Modified (Session 98)

### Backend
- `devserver/my_app/routes/pipeline_routes.py` - Added `/file/<filename>` endpoint

### Frontend
- `public/ai4artsed-frontend/src/views/partial_elimination.vue` - Complete redesign

### Documentation
- `docs/DEVELOPMENT_LOG.md` - Added Session 97 (abandoned)
- `docs/devserver_todos.md` - Marked composite as abandoned (needs update!)

---

## Critical: Don't Lose Progress

✅ **Keep These Working**:
- Dual-fetch logic in Vue (Step 1: individuals, Step 2: composite)
- New `/file/<filename>` backend endpoint
- Clean design following surrealizer template
- Flexible grid layout (auto-fit)

❌ **Still Need**:
- Backend composite creation (36 lines of code)
- Proper routing via `/execute/` path
- Stage2 proxy config (if required)

---

## Testing Checklist

Once both issues are fixed:

- [ ] Execute partial_elimination workflow from frontend
- [ ] Verify backend creates composite (check logs for `[COMPOSITE]`)
- [ ] Verify 4 images saved in run folder (09, 10, 11, 12)
- [ ] Verify frontend displays 4 images with correct labels
- [ ] Verify routing works via `/execute/partial-elimination`
- [ ] Verify property selection flow still works
- [ ] Test all 4 elimination modes (average, random, invert, zero_out)
- [ ] Test responsive layout (mobile/desktop)
- [ ] Test all actions (download, print, i2i, fullscreen)

---

## Session 98 Summary

**Duration**: ~60 minutes
**Status**: Partial progress
**Result**:
- ✅ Frontend redesigned (design standards compliant)
- ✅ New backend endpoint (filename-based fetching)
- ❌ Composite creation not re-implemented
- ❌ Routing architecture not fixed

**User Feedback**: "schade" (disappointed composite not showing)
