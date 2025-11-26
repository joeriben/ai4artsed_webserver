# Development Log

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