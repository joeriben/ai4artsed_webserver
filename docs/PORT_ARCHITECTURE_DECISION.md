# Port Architecture Decision: SwarmUI vs Direct ComfyUI Access

**Document Type:** Critical Architecture Decision
**Date:** 2025-12-15
**Status:** APPROVED - Migrate to SwarmUI Single Front Door
**Sources Verified:** SwarmUI GitHub, API docs, SillyTavern integration docs

---

## Executive Summary

**Previous Architecture (INCORRECT):**
- Port 7801 (SwarmUI): "Only for images/SD3.5"
- Port 7821 (ComfyUI): "For all other workflows, video, audio"

**New Architecture (CORRECT):**
- Port 7801 (SwarmUI): **Single Front Door for ALL operations**
- Port 7821 (ComfyUI): **Emergency fallback only (NEVER in production)**

**Root Cause of Confusion:**
Agents derived a false rule ("7821 for workflows because 7801 can't do it") from contingent practice, not architectural necessity.

---

## Critical Fact-Check: User Claims vs Official Documentation

### Claim 1: "SwarmUI bewirbt Video-Modelle als native Funktionalität"

**VERIFIED ✅**

Source: [SwarmUI README](https://github.com/mcmonkeyprojects/SwarmUI)
> "Supports AI image models (Stable Diffusion, Flux, Qwen Image, etc.), and AI video models (Wan, Hunyuan Video, etc.)."

**Conclusion:** Video is explicitly first-class in SwarmUI.

---

### Claim 2: "Audio ist 'planned/future', nicht first-class"

**VERIFIED ✅**

Source: [SwarmUI README](https://github.com/mcmonkeyprojects/SwarmUI)
> "plans to support eg audio and more in the future"

**Additional Evidence:** API.md mentions `/Audio/*.*` endpoints, but only for "user audio files in Data/Audio", NOT for generated audio outputs.

**Conclusion:** Audio generation works technically, but lacks UI/preview/history integration.

---

### Claim 3: "Raw ComfyUI workflows können über 7801 eingespeist werden"

**VERIFIED ✅**

Source: [SwarmUI Advanced Usage](https://github.com/mcmonkeyprojects/SwarmUI/blob/master/docs/Advanced%20Usage.md)
> "After building a workflow in the ComfyUI editor, users click the 'Use This Workflow' button to activate it."

**Additional Evidence:** API.md documents `/ComfyBackendDirect/*` as "direct pass-through to a comfy instance".

**Conclusion:** SwarmUI explicitly supports raw workflow submission via UI and API.

---

### Claim 4: "Die Begründung '7801 kann Video/Audio nicht' ist falsch"

**VERIFIED ✅**

**Technical Reality:**
- Both ports access the **same ComfyUI backend** (`~/ai/SwarmUI/dlbackend/ComfyUI/`)
- Port 7821 is SwarmUI's **managed ComfyUI server**, not a separate service
- SwarmUI proxies requests via `/ComfyBackendDirect/*` to the same backend

Source: [SillyTavern Docs](https://docs.sillytavern.app/extensions/stable-diffusion/)
> "If you are using SwarmUI, the default port for the managed ComfyUI server is 7821"

**Conclusion:** The limitation is NOT technical (port capabilities), but epistemological (artifact handling in UI).

---

## The Epistemological Argument: Why Video ≠ Audio

### User's Core Insight

**Video is structurally "easy" for SwarmUI:**
- Frame sequence (spatial + temporal)
- Visual preview (animated grid)
- Iterative comparison (A/B testing frames)
- Same evaluation epistemology as images ("view, compare, iterate")

**Audio is structurally "different":**
- Temporal continuum (not discrete frames)
- Non-visual artifact (waveform ≠ image)
- Different evaluation ("listen, judge duration/tone")
- Requires new interaction patterns (playback, scrubbing, looping)

**Conclusion:** SwarmUI is currently a **visual orchestration system**. Video fits because it's "images in motion". Audio would require fundamental epistemological shift.

**This is NOT a limitation of port 7801, but of SwarmUI's artifact ontology.**

---

## Current AI4ArtsEd Architecture Analysis

### Port Usage Inventory

**Port 7801 (SwarmUI) Currently Used For:**
- Simple image generation (`/API/GenerateText2Image`)
- Session management (`/API/GetNewSession`)
- ❌ NOT used for legacy workflows
- ❌ NOT used for audio workflows

**Port 7821 (Direct ComfyUI) Currently Used For:**
- All 4 legacy workflows:
  - `legacy_partial_elimination` (3 images)
  - `legacy_split_and_combine` (4 images)
  - `legacy_surrealization` (1 image, Ollama models)
  - `output_legacy` (proxy)
- Audio workflows (ACENet, StableAudio, etc.)
- Direct workflow submission via `legacy_workflow_service.py`

**Critical Files:**
- `legacy_workflow_service.py:24` - Hardcoded `http://127.0.0.1:7821`
- `backend_router.py:800` - Hardcoded ComfyUI URL for img2img

---

### Why Current Architecture is Wrong

**False Causality:**
```
WRONG: "Legacy workflows use 7821 BECAUSE 7801 can't handle them"
RIGHT: "Legacy workflows use 7821 BECAUSE we hardcoded it that way"
```

**Evidence:**
1. SwarmUI `/ComfyBackendDirect` proxies ALL ComfyUI endpoints
2. Custom AI4ArtsEd nodes are installed in SwarmUI's managed ComfyUI
3. `legacy_workflow_service.py` could route via 7801 with 5-line change
4. Audio workflows could run via 7801 (filesystem extraction works identically)

**No Technical Blocker Exists.** This is a configuration choice, not an architectural constraint.

---

## Correct Decision Matrix

### When to Use Port 7801 (SwarmUI):

✅ **ALWAYS** - SwarmUI is the Single Front Door

**Rationale:**
- Unified orchestration (queueing, history, metadata)
- Backend routing (multi-GPU support)
- Consistent error handling
- `/ComfyBackendDirect` provides full ComfyUI access

**Use Cases:**
- Simple image generation (`/API/GenerateText2Image`)
- Complex workflows (`/ComfyBackendDirect/prompt`)
- Audio generation (via workflow + filesystem extraction)
- Video generation (first-class artifact)
- Legacy workflows (transparent migration)

---

### When to Use Port 7821 (Direct ComfyUI):

❌ **NEVER** (except emergency debugging)

**Only When:**
- SwarmUI service completely down (health check fails)
- Critical debugging session requiring direct backend access
- Must be manually enabled: `ALLOW_DIRECT_COMFYUI=true`

**This is NOT a production pathway.**

---

## Migration Strategy

### Affected Components

**4 Legacy Workflows:**
- All currently hardcoded to port 7821
- All contain custom AI4ArtsEd nodes
- All can migrate transparently via `/ComfyBackendDirect`

**Audio Workflows:**
- Currently use port 7821
- Will migrate to 7801 with filesystem extraction
- SwarmUI doesn't provide artifact preview, but execution works

**Critical Code Changes:**

1. **config.py** - Add feature flag:
   ```python
   USE_SWARMUI_ORCHESTRATION = True  # Default
   ALLOW_DIRECT_COMFYUI = False  # Emergency only
   ```

2. **legacy_workflow_service.py** - Refactor routing:
   ```python
   if use_swarmui:
       endpoint = f"{swarmui_url}/ComfyBackendDirect/prompt"
   else:
       endpoint = f"{comfyui_url}/prompt"
   ```

3. **swarmui_client.py** - Add missing methods:
   - `get_generated_images()` (parity with legacy service)
   - `get_image()` (download via `/ComfyBackendDirect/view`)

4. **backend_router.py** - Update hardcoded URLs:
   ```python
   upload_url = f"{swarmui_url}/ComfyBackendDirect/upload/image"
   ```

### Rollout Timeline

**Week 1:** Configuration + SwarmUI client enhancement
**Week 2:** Legacy service refactoring + development testing
**Week 3:** Production deployment with monitoring
**Week 4:** Deprecation warnings for direct access

**Rollback Strategy:** Environment variable `USE_SWARMUI_ORCHESTRATION=false`

---

## Audio Special Case: Not a Bug, a Feature Gap

### Why Audio Needs Filesystem Extraction

**SwarmUI's Limitation:**
- No audio preview in UI (waveform player)
- No audio history metadata (duration, sample rate)
- `/Audio/*.*` endpoints only for input files, not generated outputs

**This Does NOT Prevent Execution:**
- Audio workflows run via `/ComfyBackendDirect/prompt`
- ComfyUI generates audio files to `output/audio/`
- DevServer extracts via direct filesystem access
- Frontend plays audio via standard `<audio>` tag

**Why This Works:**
- SwarmUI proxies execution to ComfyUI (same backend)
- Output directory is accessible to DevServer
- Filesystem extraction is reliable (used for video too)

**Future-Proofing:**
When SwarmUI adds first-class audio support, we can:
1. Switch from filesystem to SwarmUI artifact API
2. Gain audio preview/history features
3. No workflow changes needed (transparent upgrade)

---

## Key Architectural Principles

### Principle 1: Separation of Concerns

**SwarmUI (Port 7801):**
- Smart orchestrator
- Queueing, routing, history, metadata
- Multi-backend coordination
- Artifact management (where supported)

**ComfyUI (Port 7821):**
- Execution engine
- Should NEVER be accessed directly by DevServer
- Managed by SwarmUI, not by clients

### Principle 2: Artifact Epistemology Over Port Capabilities

**Don't Ask:** "Which port supports this media type?"
**Ask Instead:** "Is this media type a first-class artifact in SwarmUI?"

- **Image:** Yes (native UI/preview/history)
- **Video:** Yes (frame-based UI/preview/history)
- **Audio:** No (execute via proxy, extract via filesystem)
- **3D Models:** No (not yet implemented)

### Principle 3: Transparent Migration

Legacy workflows should be **unaware** of routing change:
- Same workflow JSON format
- Same prompt injection mechanism
- Same output structure
- Only internal routing differs (7821 → 7801 via proxy)

### Principle 4: Graceful Degradation

Emergency fallback to direct ComfyUI if:
- SwarmUI health check fails
- Explicit override via `ALLOW_DIRECT_COMFYUI=true`
- Per-workflow override for critical debugging

**This is NOT a feature, it's a safety net.**

---

## Lessons Learned: How Agents Got This Wrong

### The False Rule

**What Agents Said:**
> "Video and audio cannot run over 7801, must use 7821"

**How This Happened:**
1. Observed: Legacy workflows use 7821
2. Observed: Audio workflows use 7821
3. Inferred: 7821 is the "workflow port"
4. Concluded: 7801 "can't" do workflows

**What Was Missed:**
- Causality inverted (hardcoded config, not technical limit)
- Port 7821 is SwarmUI's **managed backend**, not separate service
- SwarmUI explicitly documents workflow submission capabilities
- Audio limitation is epistemological (artifact handling), not technical (port capabilities)

### Correct Mental Model

```
OLD (WRONG):
Port 7801 = "Simple image API"
Port 7821 = "Complex workflow API"

NEW (CORRECT):
Port 7801 = "Single orchestration layer (proxies to ComfyUI)"
Port 7821 = "Managed ComfyUI backend (accessed ONLY via 7801 proxy)"
```

---

## Verification Checklist

Before closing this decision:

- [x] Verified SwarmUI docs support raw workflow submission
- [x] Verified `/ComfyBackendDirect` endpoints exist and documented
- [x] Verified video is first-class (native SwarmUI feature)
- [x] Verified audio is planned/future (not first-class yet)
- [x] Verified port 7821 is SwarmUI's managed ComfyUI
- [x] Identified all 4 legacy workflows requiring migration
- [x] Identified audio workflows requiring migration
- [x] Designed rollback strategy for safety
- [x] Documented artifact epistemology rationale

---

## References

1. **SwarmUI Main Repo:** https://github.com/mcmonkeyprojects/SwarmUI
   - Video support documented
   - Audio marked as "planned/future"

2. **SwarmUI Advanced Usage:** https://github.com/mcmonkeyprojects/SwarmUI/blob/master/docs/Advanced%20Usage.md
   - "Use This Workflow" feature documented
   - Custom workflow integration explained

3. **SwarmUI API Docs:** https://github.com/mcmonkeyprojects/SwarmUI/blob/master/docs/API.md
   - `/ComfyBackendDirect/*` documented as ComfyUI pass-through
   - `/Audio/*.*` endpoints for input files only

4. **SillyTavern Integration:** https://docs.sillytavern.app/extensions/stable-diffusion/
   - Port 7821 identified as "SwarmUI's managed ComfyUI server"
   - Confirms single backend architecture

---

## Decision Log

**Date:** 2025-12-15
**Decision:** Migrate all workflows to SwarmUI Single Front Door (port 7801)
**Rationale:** Unified orchestration, consistent with SwarmUI architecture, no technical blockers
**Risk:** Low (gradual rollout, emergency fallback available)
**Status:** APPROVED for implementation

**Next Steps:**
1. Implement configuration flags (Phase 1)
2. Enhance swarmui_client.py (Phase 2)
3. Refactor legacy_workflow_service.py (Phase 3)
4. Deploy to development environment
5. Test all 4 legacy workflows + audio
6. Production rollout with monitoring
