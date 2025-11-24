# Session 47: SwarmUI API Architecture - CORRECTED

**Date:** 2025-11-16
**Issue:** Confusion about SwarmUI's role and API access patterns
**Correction Date:** 2025-11-16 (Same session)

## THE REAL ARCHITECTURE (Corrected)

SwarmUI provides **TWO different API access methods** to the same ComfyUI backend:

### Port Architecture
- **Port 7801**: SwarmUI REST API - **GOOD FEEDBACK** ✅
  - Clean REST API (`/API/GenerateText2Image`)
  - Returns image paths immediately
  - Proper error handling
  - Used by: `swarmui_client.py`

- **Port 7821**: Raw ComfyUI API - **POOR FEEDBACK** ❌
  - Raw workflow submission (`/prompt`, `/history`, `/queue`)
  - Requires polling `/history` endpoint
  - Fragile history parsing
  - Used by: `comfyui_client.py`

**Both ports access the SAME ComfyUI backend** - just different API styles.

### The ORIGINAL Misconception (NOW CORRECTED)
Initially thought: "SwarmUI is just a wrapper with no value"
**THIS WAS WRONG**

### The Corrected Understanding
SwarmUI's REST API (port 7801) provides CRITICAL value:
- Eliminates fragile history polling
- Provides immediate, clean feedback
- Returns image paths directly in response
- Much more reliable than raw ComfyUI API

## Goal: Eliminate comfyui_client.py

**Target State:** Use ONLY SwarmUI REST API (port 7801) for ALL ComfyUI operations

### Why?
- Port 7801 provides clean, immediate feedback
- Port 7821 requires fragile history polling
- All operations go to same ComfyUI backend anyway
- Simpler, more reliable architecture

### Implementation Plan

#### Phase 1: Research (IN PROGRESS)
- [ ] Check if SwarmUI REST API supports custom workflow submission
- [ ] Document SwarmUI API endpoints beyond `/API/GenerateText2Image`
- [ ] Test custom workflow submission via port 7801

#### Phase 2: Extend swarmui_client.py
- [ ] Add `submit_custom_workflow()` method if supported
- [ ] Add audio/video output extraction methods
- [ ] Add WebSocket support for progress monitoring (if available)

#### Phase 3: Migrate backend_router.py
- [ ] Update `_process_comfyui_legacy()` to use swarmui_client
- [ ] Test all output chunks (image, audio, video)
- [ ] Verify metadata extraction works correctly

#### Phase 4: Remove comfyui_client.py
- [ ] Delete `devserver/my_app/services/comfyui_client.py`
- [ ] Remove all imports
- [ ] Update tests

#### Phase 5: Clean Up Terminology
- [ ] Keep `swarmui_client.py` name (accurate - it IS the SwarmUI client)
- [ ] Update log messages to clarify "SwarmUI REST API" vs "raw ComfyUI API"
- [ ] Update architecture docs

## Status

- [x] Problem identified and correctly understood
- [x] Architecture clarified (port 7801 vs 7821)
- [x] Goal defined (eliminate comfyui_client.py)
- [x] Implementation plan created
- [ ] Research phase in progress
- [ ] Code implementation pending
- [ ] Testing pending

## Next Steps

1. Research SwarmUI API capabilities for custom workflows
2. Test if port 7801 can handle raw workflow submission
3. Implement unified client using only port 7801
4. Remove fragile port 7821 polling code
