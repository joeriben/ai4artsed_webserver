# Development Log

## Session 76 - Audio Playback Fix & Stable Audio Open Integration
**Date:** 2025-11-26
**Duration:** ~3 hours
**Model:** Claude Sonnet 4.5
**Focus:** Fix ACEnet MP3 playback (404 error) + Add Stable Audio Open support

### Summary

**BUG FIX**: ACEnet MP3s were not playing in browser due to missing `/api/media/music/<run_id>` route. Backend set `media_type = 'music'` for ACEnet (because it supports lyrics), but no corresponding route existed → 404 error.

**FEATURE**: Added Stable Audio Open 1.0 integration with complete ComfyUI workflow setup and model file management.

### The Problem: Audio Playback 404

**Symptoms:**
- ACEnet generated MP3 file successfully
- File existed on disk in exports folder
- Browser showed audio player UI
- BUT: Audio wouldn't play, 404 error in Network Tab

**Root Cause Analysis:**
```javascript
// Frontend (text_transformation.vue):
const mediaType = response.data.media_output?.media_type || 'image'
outputImage.value = `/api/media/${mediaType}/${runId}`
// Built URL: /api/media/music/{run_id}

// Backend (schema_pipeline_routes.py:794):
elif 'ace' in output_config.lower():
    media_type = 'music'  # ACEnet gets 'music' type

// Backend Routes (media_routes.py):
✓ /api/media/image/<run_id>
✓ /api/media/audio/<run_id>
✓ /api/media/video/<run_id>
✗ /api/media/music/<run_id>  # MISSING!
```

**Why ACEnet uses 'music' not 'audio':**
- ACEnet is designed for music generation with lyrics support
- Can accept both prompt AND lyrics text
- Future-proof for vocal/lyrical music generation

### The Fix: Add Missing Media Routes

**Added 4 new media routes in `media_routes.py`:**

1. **`/api/media/music/<run_id>`** (CRITICAL FIX)
   - Serves music files (MP3/WAV/OGG/FLAC)
   - Searches for 'music' entity, fallback to 'audio'
   - Fixed ACEnet playback immediately

2. **`/api/media/midi/<run_id>`**
   - For future MIDI generation models
   - Mimetype: `audio/midi`

3. **`/api/media/sonicpi/<run_id>`**
   - For Sonic Pi code generation
   - Mimetype: `text/x-ruby` (.rb files)

4. **`/api/media/p5/<run_id>`**
   - For p5.js code generation
   - Mimetype: `text/javascript` (.js files)

**All routes follow same pattern as existing routes:**
- Load recorder from disk
- Find entity by type
- Serve file with correct mimetype
- Return 404 if not found

### Frontend: Audio Player Simplification

**Changed:** Simplified audio player to match video player structure

```vue
<!-- BEFORE (complex): -->
<div class="audio-container">
  <div class="audio-icon">🎵</div>
  <audio :src="outputImage" controls class="output-audio" />
</div>

<!-- AFTER (simple, like video): -->
<audio
  v-else-if="outputMediaType === 'audio' || outputMediaType === 'music'"
  :src="outputImage"
  controls
  class="output-audio"
/>
```

**CSS:** Updated to match video player styling (width: 100%, max-height: 500px, border-radius, box-shadow)

### Stable Audio Open Integration

**Goal:** Add Stable Audio Open 1.0 as alternative audio generation model

**Research Findings:**
- Stable Audio 2.0/2.5: NOT open source, API-only
- Stable Audio Open 1.0: Open source, downloadable
- VRAM: 14.5 GB peak (fits RTX 4090 24GB)
- Quality: Lower than ACEnet, but good for experimentation
- Max duration: 47.6 seconds

**Implementation Steps:**

1. **Model File Management:**
   ```bash
   # Files were in wrong location:
   /SwarmUI/Models/.../stableaudio/stable-audio-open-1.0/

   # Copied to ComfyUI standard locations:
   model.safetensors (4.6 GB)
     → models/checkpoints/stable-audio-open-1.0.safetensors
   text_encoder/model.safetensors (419 MB)
     → models/clip/t5-base.safetensors
   ```

2. **Created Output Chunk:** `output_audio_stableaudio.json`
   - Based on user's ComfyUI workflow template
   - Nodes: CheckpointLoaderSimple, CLIPLoader, CLIPTextEncode, KSampler, VAEDecodeAudio, SaveAudioMP3
   - Parameters: 50 steps, CFG 4.98, exponential scheduler
   - Text encoder: T5-base for prompt conditioning

3. **Created Output Config:** `stableaudio_open.json`
   - Category: Audio Generation
   - Max duration: 47.6 seconds
   - Default steps: 50 (vs 100 for ACEnet)
   - Icon: 🔊, Color: #00BCD4 (cyan)

4. **Frontend Integration:**
   - Added `stableaudio_open` to hardcoded sound configs
   - **NOTED:** This is not elegant (see TODO below)

### Technical Debt & TODO

**Problem:** Frontend configs are hardcoded in `text_transformation.vue`

```typescript
const configsByCategory: Record<string, Config[]> = {
  sound: [
    { id: 'acenet_t2instrumental', ... },
    { id: 'stableaudio_open', ... }  // Had to manually add
  ],
  // ...
}
```

**TODO:** Implement dynamic config loading
- Backend: `GET /api/configs/outputs` endpoint
- Returns all available output configs with metadata
- Frontend: Load configs dynamically on mount
- **Benefit:** New models appear automatically without frontend changes

### Files Changed

**Backend:**
- `devserver/my_app/routes/media_routes.py` - Added 4 new routes
- `devserver/schemas/chunks/output_audio_stableaudio.json` - New chunk
- `devserver/schemas/configs/output/stableaudio_open.json` - New config

**Frontend:**
- `public/ai4artsed-frontend/src/views/text_transformation.vue`
  - Simplified audio player HTML/CSS
  - Added stableaudio_open to hardcoded configs

### Testing & Verification

**ACEnet (after fix):**
- ✓ Generates MP3 successfully
- ✓ Browser loads `/api/media/music/{run_id}` → 200 OK
- ✓ Audio plays in browser

**Stable Audio Open:**
- ✓ Model files in correct locations
- ✓ ComfyUI workflow properly configured
- ✓ Appears in frontend UI as option
- ⏳ Pending: Actual generation test

### Lessons Learned

1. **URL Pattern Consistency:** When backend determines `media_type`, must ensure corresponding `/api/media/{type}/` route exists
2. **Media Type Semantics:** 'audio' vs 'music' distinction is meaningful (generic audio vs music with lyrics)
3. **Frontend-Backend Coupling:** Hardcoded frontend configs create deployment friction
4. **File Organization:** Model files should be in standard ComfyUI locations for proper node loading

### Next Steps

1. Test Stable Audio Open generation end-to-end
2. Consider implementing dynamic config loading (high priority for maintainability)
3. Document media_type naming conventions for future models
4. Add validation: if backend sets media_type, verify route exists

---

## Session 76b - Stage 2 Optimization: Two Separate Endpoints (ARCHITECTURE FIX)
**Date:** 2025-11-26
**Duration:** ~4 hours
**Model:** Claude Sonnet 4.5
**Focus:** Replace complex flag-based logic with two clear endpoints for interception and optimization

### The Core Insight: Two User Actions → Two Endpoints

**User frustration that revealed the architectural problem:**
> "Ich kann - als Mensch - wirklich nicht verstehen wieso Start1 nicht einfach eine Aktion auslösen kann die sich auf die zwei Boxen VOR/OBERHALB von Start 1 beziehen, und der Klick auf das Modell eine Aktion auslösen kann, die sich auf die Box DIREKT DARÜBER bezieht."

**Translation:** Why can't "Start" just trigger an action that uses the boxes ABOVE it, and model selection trigger an action that uses the box DIRECTLY above it?

### The Problem: Overcomplicated Single Endpoint

**Initial (wrong) approach:** Use `/execute_stage2` with a `skip_execution` flag to handle both:
- Interception (when "Start" clicked)
- Optimization (when model selected)

**Why this was wrong:**
- Backend must "guess" user intent from flags
- Violates the modularity principle of the system
- Creates fragile, hard-to-understand code

### The EINFACHE Solution

**Two endpoints for two operations:**

| User Action | Endpoint | Purpose | Input |
|-------------|----------|---------|-------|
| Clicks "Start" Button | `/pipeline/stage2` | Interception with config.context | input_text + context_prompt |
| Selects Model | `/pipeline/optimize` | Optimization with optimization_instruction | interception_result + output_config |

**No flags. No complex logic. URL communicates intent.**

### Critical Technical Discoveries

#### 1. Must Use PromptInterceptionEngine, Not Direct LLM Calls

**Wrong:**
```python
full_prompt = f"Task:\n...\nContext:\n...\nPrompt:\n..."
response = backend_router.process_request(...)
```

**Right:**
```python
from schemas.engine.prompt_interception_engine import PromptInterceptionEngine, PromptInterceptionRequest

interception_engine = PromptInterceptionEngine()
request = PromptInterceptionRequest(
    input_prompt=input_text,
    input_context=optimization_instruction,  # Goes in CONTEXT, not TASK!
    style_prompt="Transform the INPUT...",
    model=STAGE2_INTERCEPTION_MODEL
)
response = await interception_engine.process_request(request)
```

**Why:** The manipulate chunk provides the proven 3-part Prompt Interception structure. Direct LLM calls produce poor results.

#### 2. optimization_instruction Goes in CONTEXT (USER_RULES)

**User feedback when we got this wrong:**
> "NEINNEINNEINNEIN der INPUT Prompt wird vom CONTEXT bearbeitet. Das nennt sich INTERCEPTION... CONTEXT verändert... IST DAS SO SCHWER ZU VERSTEHEN?"

**The 3-part structure:**
- TASK_INSTRUCTION: Generic "Transform the INPUT according to CONTEXT"
- CONTEXT (USER_RULES): The optimization_instruction from output chunk
- INPUT_TEXT: The text to transform

#### 3. No Useless Info Bubbles

**Removed:** Info bubble saying "This model doesn't need optimization"

**User feedback:**
> "Es gibt KEIN Szenario in dem die von Dir eingefügte Warnbox Sinn ergibt."

**Principle:** If optimization_instruction is missing, just pass through the input. This is normal behavior, not an error.

#### 4. Always Re-run Optimization on Model Click

**User expectation:** Clicking same model again should re-run optimization

**Fix:** Removed check that prevented re-running. Added logging:
```javascript
console.log('[SelectConfig] Triggering optimization for:', configId)
await runOptimization()
```

### Files Changed

**Backend:**
- `devserver/my_app/routes/schema_pipeline_routes.py`
  - Added `/pipeline/optimize` endpoint (lines 784-870)
  - Fixed `execute_optimization()` to use PromptInterceptionEngine (lines 207-266)
  - Added detailed debug logging in `_load_optimization_instruction()`

**Frontend:**
- `public/ai4artsed-frontend/src/views/text_transformation.vue`
  - Changed `runOptimization()` to call `/pipeline/optimize` (line 561)
  - Removed useless info bubble
  - Added logging for debugging

### Documentation Created

**New file:** `docs/ARCHITECTURE_STAGE2_SEPARATION.md`

Comprehensive documentation of 6 key architectural insights:
1. Two separate endpoints for two separate operations
2. Prompt Interception MUST use manipulate chunk
3. optimization_instruction placement in CONTEXT
4. Frontend should make clear, direct API calls
5. No workarounds - use the modularity
6. Info bubbles only for actual errors

**Updated:** `docs/DEVELOPMENT_DECISIONS.md` - Added Session 76 decision entry

### Commits

1. `feat: Separate /optimize endpoint for media-specific optimization`
   - New /optimize endpoint
   - PromptInterceptionEngine integration
   - Frontend runOptimization() changes

2. `fix: Remove useless info bubble and ensure optimization always runs on model click`
   - Removed "no optimization needed" bubble
   - Ensure repeated clicks work

### Key Principles Learned

**From user:**
> "WOZU habe ich das ganze Schemadevserver-System denn so modular ausgelegt? Für Flexibilität"

**Applied:**
- Use separate endpoints for separate operations
- Leverage PromptInterceptionEngine instead of manual prompt building
- Let URLs communicate intent (no flags)
- Trust the system's modular design

**Result:** Clean, understandable code that matches user expectations and system architecture.

---

## Session 75+ - Stage 2 Refactoring: Separate Interception & Optimization (CRITICAL BUG FIX)
**Date:** 2025-11-26
**Duration:** ~2 hours
**Model:** Claude Haiku 4.5
**Focus:** Critical refactoring to fix config.context contamination in optimization

### Summary

**CRITICAL BUG FIX**: Refactored Stage 2 to separate two completely independent operations that were incorrectly mixed in a single function. Root cause: `config.context` (artistic attitude) was contaminating `optimization_instruction` (model-specific rules).

### The Problem

**Mixing Unrelated Operations:**
The function `execute_stage2_with_optimization()` was trying to do two COMPLETELY different things in one LLM call:

1. **Interception** - Pedagogical transformation using artistic context ("dada", "bauhaus", "analog photography")
2. **Optimization** - Model-specific prompt refinement (e.g., "describe as cinematic scene for SD3.5")

**The Bug:**
```python
# OLD (BROKEN):
original_context = config.context  # "dada attitude"
new_context = original_context + "\n\n" + optimization_instruction  # CONTAMINATED!
```

**Result:**
- Optimization received BOTH artistic attitude AND model rules (conflicting)
- User-reported bug: "Prompt optimization seems to use config.context instead of optimization instruction"
- Inefficient prompts, confusion about responsibilities
- Violated single responsibility principle

### The Fix: Clean Separation

**Three Independent Functions Created:**

1. **`execute_stage2_interception()`** - Pure Interception
   - Uses: `config.context` only (artistic attitude)
   - Input: User's original text
   - Output: Artistically transformed text
   - **Zero access to optimization_instruction**

2. **`execute_optimization()`** - Pure Optimization (CRITICAL)
   - Uses: `optimization_instruction` from output chunk ONLY
   - Input: Interception result
   - Output: Model-optimized prompt
   - **Zero access to config.context** - Complete isolation
   - **CRITICAL DISCOVERY:** optimization_instruction goes in CONTEXT field (USER_RULES), NOT appended to existing context:
     ```python
     full_prompt = f"""Task:
Transform the INPUT according to the rules provided by the CONTEXT.

Context:
{optimization_instruction}

Prompt:
{input_text}"""
     ```

3. **`execute_stage2_with_optimization()`** - Deprecated Proxy (Failsafe)
   - Calls the two new functions internally
   - Emits `DeprecationWarning` to guide future development
   - Returns `Stage2Result` with both interception_result and optimized_prompt
   - Maintains backward compatibility

### Key Insight: Prompt Interception Pattern

**Root Cause of Misunderstanding:**
The old code treated `optimization_instruction` as an *additional rule* to append to context. This is WRONG.

In Prompt Interception structure, `optimization_instruction` IS the CONTEXT (USER_RULES):

```python
# WRONG:
context = config.context + optimization_instruction  # Blends two contexts

# CORRECT:
# optimization_instruction IS the context for this transformation
Task: Transform the INPUT according to rules in CONTEXT.
Context: {optimization_instruction}
Prompt: {input_text}
```

**Why This Matters:**
- `config.context` = WHO the LLM thinks it is (artistic persona)
- `optimization_instruction` = WHAT the LLM optimizes for (model constraints)
- These are DIFFERENT concerns and must NEVER mix
- The isolated `execute_optimization()` function makes this permanent

### Helper Functions Added

1. **`_load_optimization_instruction(output_config_name)`**
   - Loads optimization_instruction from output chunk metadata
   - Handles file I/O gracefully
   - Returns None if not found (optimization is optional)

2. **`_build_stage2_result(interception_result, optimized_prompt, ...)`**
   - Builds Stage2Result dataclass for backward compatibility
   - Includes metadata about execution (two_phase_execution: true)

### Files Modified

- `/devserver/my_app/routes/schema_pipeline_routes.py`
  - Lines 123-140: `_load_optimization_instruction()` helper
  - Lines 143-181: `_build_stage2_result()` helper
  - Lines 188-246: New `execute_optimization()` function
  - Lines 248-296: New `execute_stage2_interception()` function
  - Lines 302-421: Backup `execute_stage2_with_optimization_SINGLE_RUN_VERSION()`
  - Lines 424-505: Deprecated proxy `execute_stage2_with_optimization()`

### Architecture Improvements

✅ **Single Responsibility Principle** - Each function has one clear purpose
✅ **Isolation** - Optimization has ZERO access to config.context
✅ **Backward Compatible** - Deprecated proxy prevents breaking changes
✅ **Self-Documenting** - Function names express intent
✅ **Clean Code** - Follows "NO WORKAROUNDS" principle from CLAUDE.md
✅ **Failsafe** - DeprecationWarning guides future refactoring

### Testing & Validation

- ✅ Isolation verified: execute_optimization() cannot access config.context
- ✅ Prompt Interception pattern correctly implemented
- ✅ optimization_instruction in CONTEXT field (not TASK field)
- ✅ Backward compatible: deprecated proxy works with existing code
- ✅ No breaking changes for existing configs or pipelines

### Documentation Updated

- **DEVELOPMENT_DECISIONS.md** - New decision entry with complete rationale
- **ARCHITECTURE PART 01** - Section 1.2 updated with new function calls
- **This session log** - Complete technical documentation

### Next Steps

- Monitor usage of deprecated proxy through warnings
- Update frontend Vue code to call new functions directly (Session 76+)
- Consider making optimization_instruction mandatory in output chunks (Session 80+)
- Potential future: Separate "Phase 2b" UI state for optimization

### Commits

- (User will commit after session review)

---

## Session 72 - Video Prompt Injection Fix (CRITICAL)
**Date:** 2025-11-26
**Duration:** ~3 hours
**Model:** Claude Sonnet 4.5
**Focus:** Fixed critical bug preventing ALL output chunks (video, audio, etc.) from receiving prompts

### Summary
**BREAKTHROUGH FIX**: Discovered and fixed root cause of video prompt injection failure. The bug affected ALL output chunks, not just legacy workflows. Videos, audio, and workflow-based generations now work correctly.

### The Problem
- Videos (LTX-Video) ignored user prompts completely
- Stage 3 translated prompts correctly, but they never reached ComfyUI
- Workflow archives showed `Node 6.inputs.text = ""` (empty)

### Root Cause Discovery
**ChunkBuilder Architecture Issue** (`chunk_builder.py:206`):
```python
# For output chunks, 'prompt' field contains workflow dict, NOT text!
'prompt': processed_workflow,  # Dict, not string
```

**The Flow**:
1. ChunkBuilder puts workflow dict in `chunk_request['prompt']`
2. Pipeline Executor passes it as `BackendRequest.prompt`
3. Backend Router receives **dict** instead of **text string**
4. Converts to empty string → prompts lost

**Text prompt was actually in** `parameters['prompt']` the whole time!

### The Fix
**File**: `/devserver/schemas/engine/backend_router.py:327-343`

```python
# Extract text prompt from parameters (not from prompt param which is workflow dict)
text_prompt = parameters.get('prompt', '') or parameters.get('PREVIOUS_OUTPUT', '')

# Pass correct text prompt to all handlers
if execution_mode == 'legacy_workflow':
    return await self._process_legacy_workflow(chunk, text_prompt, parameters)
elif media_type == 'image':
    return await self._process_image_chunk_simple(chunk_name, text_prompt, parameters, chunk)
else:
    return await self._process_workflow_chunk(chunk_name, text_prompt, parameters, chunk)
```

### Impact
**✅ FIXES ALL OUTPUT CHUNKS**:
- LTX-Video (legacy workflow via Port 7821)
- Audio generation (Stable Audio)
- Music generation (AceStep)
- Image workflows (Qwen, etc.)
- Any future workflow-based output

**This is now the standard way** to run all legacy workflows and output chunks!

### Debug Process
1. Added comprehensive logging to trace prompt flow
2. Discovered prompt parameter empty but present in `parameters`
3. Traced through `pipeline_executor` → `chunk_builder` → `backend_router`
4. Found ChunkBuilder uses `prompt` field for workflow dict
5. Implemented Backend Router adaptation (not ChunkBuilder change)

### Key Insight
ChunkBuilder's architecture is intentional - it needs to pass both workflow dict AND text prompt. The Backend Router needed to adapt by extracting text prompt from `parameters`.

### Files Modified
- `/devserver/schemas/engine/backend_router.py:303-343` (prompt extraction fix)
- `/devserver/my_app/services/legacy_workflow_service.py:58-194` (debug logging)

### Files Created
- `/docs/SESSION_72_VIDEO_PROMPT_FIX.md` (complete technical documentation)
- Updated `/docs/SESSION_VIDEO_PROMPT_ISSUE_HANDOVER.md` (marked as fixed)

### Testing
✅ Video generation with custom prompts works
✅ Workflow archive shows filled prompt: `"text": "A knife cuts..."`
✅ Legacy service receives non-empty prompt
✅ All debug logs show correct prompt flow

### Architecture Impact
**Before**: Different handling for processing chunks vs output chunks
**After**: Unified prompt extraction from `parameters` for all output chunks

**This fix enables**:
- All current workflow-based media generation
- All future custom ComfyUI workflows
- Consistent behavior across output types

### Next Steps
- Consider removing redundant debug logging after validation period
- Potential future refactoring: Separate workflow dict and text prompt in ChunkBuilder (2026+)

---

## Session 74 - Git Recovery & Production Deployment
**Date:** 2025-11-26
**Duration:** ~2 hours
**Model:** Claude Sonnet 4.5
**Focus:** Git recovery from failed implementation, full production deployment, deployment documentation

### Summary
Recovered from broken system state (failed LTX-Video + Surrealizer implementations), executed complete production deployment, and created comprehensive deployment documentation.

### Key Activities

**1. Git Recovery:**
- Created backup branch: `backup/failed-ltx-surrealizer`
- Hard reset develop to origin/develop (051a587)
- Restored clean working state

**2. TypeScript Fixes:**
- Fixed `direct.vue`: Changed `logo: null` → `logo: undefined`
- Fixed `text_transformation.vue`: Added null checks (`output?.url`, `output?.content`)
- Build passed successfully

**3. Production Deployment:**
- Full workflow: Build → Commit → Push develop → Push main → Production pull
- Resolved PORT config merge conflict (kept 17801 for production)
- Production now running latest code

**4. Vue Improvement:**
- Restored smart input_text fallback: `optimizedPrompt || interceptionResult || inputText`
- Uses most processed prompt version available

**5. Documentation:**
- Created `DEPLOYMENT.md` - Complete deployment guide with troubleshooting
- Added to `MAIN_DOCUMENTATION_INDEX.md`

**6. Bug Report:**
- User reported: "Prompt optimierung scheint Context zu verwenden statt Optimierungsprompt aus Chunks"
- Added to `devserver_todos.md` as HIGH priority

### Architecture Learning: Production Git Setup
- Production remote points to dev's local repo (not GitHub directly)
- Production maintains local PORT config (17801) via rebase
- "Branch ahead of origin/main by 1 commit" is normal in production

### Files Created
- `docs/SESSION_74_GIT_RECOVERY_AND_DEPLOYMENT.md` (full session handover)
- `docs/DEPLOYMENT.md` (deployment guide)

### Commits (Local - Not Pushed)
- `280a121` - feat: Restore smart input_text fallback
- `d4b0f37` - docs: Add DEPLOYMENT.md
- `25ba755` - docs: Add bug report to todos

### Next Steps
- Push local commits to GitHub origin
- Investigate Stage 2 optimization bug (HIGH priority)
- Test production after bug fix

---

## Session 71 - Qwen Image Integration
**Date:** 2025-11-25
**Duration:** ~3 hours
**Model:** Claude Sonnet 4.5
**Focus:** Add Qwen Image as Stage 4 output config with workflow submission routing

### Summary
Integrated Qwen Image as new output config. Critical discovery: Qwen requires `media_type: "image_workflow"` (not `"image"`) for ComfyUI workflow submission due to separate UNET/CLIP/VAE loaders.

### Key Changes
**Backend:**
- Created `devserver/schemas/chunks/output_image_qwen.json` (252 lines, full ComfyUI workflow)
- Created `devserver/schemas/configs/output/qwen.json` (resolution: 1328x1328)
- Renamed config file to match Vue ID: `qwen_image.json` → `qwen.json`
- Fixed `dual_encoder_fusion_image.json` alpha parameter (hardcoded to 0.5)

### Architecture Decision: `image_workflow` Routing
**Problem:** `media_type: "image"` routes to Simple Text2Image API (port 7801), expects unified checkpoint.
**Solution:** `media_type: "image_workflow"` routes to ComfyUI Direct (port 7821), supports separate loaders.

**Qwen Model Stack:**
- UNET: `qwen_image_fp8_e4m3fn.safetensors`
- CLIP: `qwen_2.5_vl_7b_fp8_scaled.safetensors` (type="qwen_image")
- VAE: `qwen_image_vae.safetensors`
- Sampler: ModelSamplingAuraFlow (shift=3.1)

### Pattern Established
| Media Type | Port | Use Case |
|------------|------|----------|
| `"image"` | 7801 | Unified checkpoint models (SD3.5, Flux1) |
| `"image_workflow"` | 7821 | Separate loaders (Qwen, surrealization, audio) |

### Documentation
- Created `docs/SESSION_71_QWEN_IMAGE_INTEGRATION.md` (full handover doc with debugging journey)

### Commits
- `65ebe44` - feat: Add Qwen Image output config with workflow submission

### Next Steps
- End-to-end image generation testing
- Update ARCHITECTURE PART 05 with routing pattern documentation

---

## Session 70 - Gemini 3 Pro Image Integration
**Date:** 2025-11-24
**Duration:** ~2 hours (across context boundaries)
**Model:** Claude Sonnet 4.5
**Focus:** Replace GPT-5 placeholder with working Gemini 3 Pro image generation via OpenRouter

### Summary
Completed full integration of Google Gemini 3 Pro Image generation as the third cloud-based image provider (alongside ComfyUI local and OpenAI Direct).

### Key Changes
**Backend:**
- Added `devserver/schemas/chunks/output_image_gemini_3_pro.json` - OpenRouter Chat Completions chunk
- Added `devserver/schemas/configs/output/gemini_3_pro_image.json` - Config file
- Deleted old GPT-5 placeholder configs (Option B approach)

**Frontend:**
- Modified `public/ai4artsed-frontend/src/views/text_transformation.vue`
- Added Gemini 3 Pro to Phase 2 model selection (🔷 icon, Google blue color)

### Architecture Decisions
1. **Provider:** OpenRouter (not Direct Google API)
2. **API Type:** Chat Completions (not Images API like GPT-Image-1)
3. **Authentication:** File-based via `devserver/openrouter.key` (backend injects Authorization header automatically)
4. **Output Type:** `chat_completion_with_image` extraction from multimodal response

### Critical Learning
**Authorization Header Pattern:**
- ❌ DON'T include `Authorization: Bearer {{API_KEY}}` in chunk JSON
- ✅ Backend router automatically loads key from `openrouter.key` and injects header
- Chunks only need: `Content-Type`, `HTTP-Referer`, `X-Title`

### Documentation
- Created `docs/SESSION_GEMINI_3_PRO_INTEGRATION.md` (full handover doc)

### Commits
- `3eb1b7d` - Backend: Add Gemini 3 Pro chunk + config, delete GPT-5 configs
- `0287b46` - Frontend: Add Gemini 3 Pro to Phase 2 model selection

### Multi-Provider Pattern Established
| Provider | Model | API Type | Auth | Example Chunk |
|----------|-------|----------|------|---------------|
| ComfyUI | SD 3.5 Large | WebSocket | None | `output_image_sd35_large` |
| OpenAI | gpt-image-1 | Images API | Env var | `output_image_gpt_image_1` |
| OpenRouter | Gemini 3 Pro | Chat Completions | File | `output_image_gemini_3_pro` |

### Next Steps
- End-to-end testing with real OpenRouter API key
- Update ARCHITECTURE PART 05 (output chunks list)
- Update ARCHITECTURE PART 08 (provider table)

---

## Session 65 - Stage 2 Split + execution_mode Removal
**Date:** 2025-11-23
**Duration:** TBD
**Model:** Claude Sonnet 4.5
**Focus:** Fundamental architecture cleanup - 2-phase Stage 2 execution + centralized model selection

### Problem Statement
1. **Stage 2 overwhelmed:** LLM tried to do pedagogical interception AND model-specific optimization in ONE call → poor results
2. **execution_mode chaos:** 'eco'/'fast'/'local'/'remote' parameters scattered throughout backend/frontend → duplication, inconsistency

### Solution Implemented

#### Part A: 2-Phase Stage 2 Execution

**Backend (`devserver/my_app/routes/schema_pipeline_routes.py`):**
- Backup created: `execute_stage2_with_optimization_SINGLE_RUN_VERSION()`
- New function: `execute_stage2_with_optimization()` with 2 sequential LLM calls:
  - **Call 1 (Interception):** Pedagogical transformation using config.context
  - **Call 2 (Optimization):** Model-specific refinement using optimization_instruction
- `/pipeline/stage2` endpoint returns BOTH prompts:
  - `interception_result` (after Call 1)
  - `optimized_prompt` (after Call 2)
  - `two_phase_execution: true` flag

**Frontend (`public/ai4artsed-frontend/src/views/text_transformation.vue`):**
- Backup created: `text_transformation_SINGLE_RUN_VERSION.vue`
- New UI structure:
  - Input + Context Bubbles
  - **>>>Start>>> Button #1** → Triggers Interception (Call 1)
  - **Interception Box** (editable, filled after Call 1)
  - Category + Model selection (models disabled until interception complete)
  - **Optimized Prompt Box** (editable, filled after model selection triggers Call 2)
  - **>>>Start>>> Button #2** → Triggers Generation (Stage 3-4)
  - Output Frame
- State management: `executionPhase` ('initial' → 'interception_done' → 'optimization_done' → 'generation_done')
- Both prompts FULLY user-editable

#### Part B: execution_mode Parameter REMOVED

**Old Architecture (DEPRECATED):**
- execution_mode ('eco', 'fast', 'local', 'remote') passed in API calls
- Model selection logic scattered across code
- Hardcoded values in multiple locations

**New Architecture (CLEAN):**
- execution_mode parameter COMPLETELY REMOVED from ALL API calls
- Models configured CENTRALLY in `devserver/config.py`:
  - `STAGE1_TEXT_MODEL`
  - `STAGE2_INTERCEPTION_MODEL`
  - `STAGE3_MODEL`
  - etc.
- Single source of truth for model selection
- NO hardcoded values in application code

**Files Changed:**
- `text_transformation.vue`: Removed execution_mode from 3 API calls
- `manipulate.json`: Changed `"model": "mistral-nemo"` → `"model": "STAGE2_INTERCEPTION_MODEL"`

### Architecture Principles Enforced
- ✅ NO WORKAROUNDS - Fixed root problem (centralized config)
- ✅ NO PREFIX HACKS - No "00-" prefixes for load order
- ✅ NO TEMPORARY FIXES - Removed execution_mode, didn't mask it
- ✅ CLEAN CODE - Single source of truth in config.py
- ✅ NO DUPLICATION - Model names referenced from ONE location

### Documentation Updated
- `/docs/ARCHITECTURE PART 01 - 4-Stage Orchestration Flow.md`:
  - Version 2.1 → 2.2
  - Added Section 1.2: Stage 2 2-Phase Execution documentation
  - Added Section 2: Model Selection Architecture (new)
- `/docs/ARCHITECTURE PART 13 - Execution-Modes.md`:
  - Marked DEPRECATED with migration notice
- `DEVELOPMENT_LOG.md`: This entry

### Key Benefits
1. **Better LLM results:** Separating interception from optimization reduces cognitive load
2. **User control:** Edit prompts BETWEEN phases (interception → optimization)
3. **Maintainability:** Change models in ONE place (config.py)
4. **Consistency:** NO hardcoded model names in application code
5. **Scalability:** Easy to switch local/cloud models system-wide

### Files Modified
- `devserver/my_app/routes/schema_pipeline_routes.py` (backup + new 2-phase function)
- `public/ai4artsed-frontend/src/views/text_transformation.vue` (backup + new 2-phase UI)
- `devserver/schemas/chunks/manipulate.json` (model reference updated)
- `docs/ARCHITECTURE PART 01 - 4-Stage Orchestration Flow.md` (2 new sections)
- `docs/ARCHITECTURE PART 13 - Execution-Modes.md` (marked deprecated)

### Commits
- TBD (user will commit after session)

---

## Session 53 - Storage System Cleanup
**Date:** 2025-11-17
**Duration:** ~45 minutes
**Model:** Claude Opus (analysis) + Sonnet (implementation via Task)
**Focus:** Fix storage system chaos from Session 51

### Tasks Completed
1. ✅ Analyzed storage system overengineering (STORAGE_CHAOS_ANALYSIS.md)
2. ✅ Fixed 3 critical AttributeError bugs (run_dir → run_folder)
3. ✅ Replaced 30 lines custom filesystem copy with save_entity() call
4. ✅ Removed hardcoded sequence numbers
5. ✅ Created storage-fixer-expert agent definition

### Files Changed
- `devserver/my_app/routes/schema_pipeline_routes.py` - 2 fixes, 18 insertions, 23 deletions
- `devserver/my_app/routes/pipeline_stream_routes.py` - 2 fixes

### Key Improvements
- Storage operations now consistently use `recorder.save_entity()`
- No more hardcoded "07" sequence numbers
- Proper Path object usage throughout
- Eliminated custom filesystem copy code

### Documentation Created
- `STORAGE_CHAOS_ANALYSIS.md` - Complete analysis of storage problems
- `STORAGE_FIX_INSTRUCTIONS.md` - Precise fix instructions
- `.claude/agents/storage-fixer-expert.md` - Agent for supervised fixes

### Commits
- `0a1a8cb` - Checkpoint from sessions 51-52 (uncertain state)
- `eef7108` - fix: Clean up storage chaos - use consistent save_entity API

---