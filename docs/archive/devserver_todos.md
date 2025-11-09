# DevServer Implementation TODOs
**Last Updated:** 2025-10-26
**Context:** Post-analysis TODOs for completing devserver architecture

---

## ⚠️ IMPORTANT RULES FOR IMPLEMENTATION

### File Management Rules
1. **NEVER delete files directly with `rm`** - always move to docs/tmp/ or .OBSOLETE suffix
2. **Before moving/renaming:** Check if file contains unique information
3. **For consolidation:** Read BOTH files completely, merge content, then move old to tmp/
4. **Recent files (<24h old):** Extra caution, always backup first
5. **Git safety:** Always commit before major refactoring

**Rationale:** Files may contain valuable information not obvious from filename/age. User correctness check needed.

---

## CRITICAL - From !! Comments in ARCHITECTURE.md

### !! Comment 5: Pre-Translation Logic (#notranslate#)
**Status:** NOT IMPLEMENTED
**Priority:** HIGH
**Location:** `my_app/routes/workflow_routes.py` line 276

**Current Behavior:**
```python
# Line ~530: Pre-translation happens ALWAYS
if should_translate:
    translated_prompt = asyncio.run(translator_service.translate(...))
```

**Required Behavior:**
```python
# Check for #notranslate# marker BEFORE translation
if "#notranslate#" in original_prompt:
    translated_prompt = original_prompt.replace("#notranslate#", "")
    # Skip translation entirely
elif should_translate:
    translated_prompt = asyncio.run(translator_service.translate(...))
```

**Files to Modify:**
- `my_app/routes/workflow_routes.py` (~line 530)

**Tests Required:**
- Test with `#notranslate#` marker → no translation
- Test without marker → translation happens as normal
- Test marker position (beginning, middle, end)

---

### !! Comment 2: Task-Type Metadata System
**Status:** PARTIALLY IMPLEMENTED
**Priority:** MEDIUM
**Context:** `model_selector.py` already has 6 task categories

**What Exists:**
```python
# model_selector.py lines 73-130
task_categories = {
    "security": {...},
    "vision": {...},
    "translation": {...},
    "standard": {...},
    "advanced": {...},
    "data_extraction": {...}
}
```

**What's Missing:**
1. Chunks don't declare their `task_type`
2. Configs don't declare their `task_type`
3. Pipeline executor doesn't pass `task_type` to model_selector

**Required Implementation:**

**1. Add task_type to Chunk meta:**
```json
// manipulate.json
{
  "name": "manipulate",
  "template": "{{INSTRUCTION}}...",
  "model": "task:standard",  // Use task-based selection
  "meta": {
    "task_type": "standard",  // Declare task type
    "chunk_type": "manipulation"
  }
}
```

**2. Add task_type to Config meta (optional override):**
```json
// dada.json
{
  "pipeline": "text_transformation",
  "context": "You are a Dadaist artist...",
  "meta": {
    "task_type": "advanced",  // Override chunk's task_type if needed
    "requires_creativity": true
  }
}
```

**3. Modify chunk_builder.py to use task-based model selection:**
```python
# chunk_builder.py
def build_chunk(...):
    # Get task_type from config (override) or chunk (default)
    task_type = resolved_config.meta.get('task_type') or chunk.meta.get('task_type', 'standard')

    # If model uses task: prefix, resolve it
    if chunk.model.startswith('task:'):
        task_name = chunk.model.split(':', 1)[1]
        selected_model = model_selector.select_model(task_name, mode=execution_mode)
    else:
        selected_model = chunk.model
```

**Files to Modify:**
- `schemas/chunks/manipulate.json` (add task_type to meta)
- `schemas/engine/chunk_builder.py` (add task-based model selection)
- `schemas/engine/config_loader.py` (allow task_type in Config.meta)

**Tests Required:**
- Test task-based model selection (eco vs fast mode)
- Test config override of chunk task_type
- Test fallback to 'standard' if no task_type specified

---

## OUTPUT-PIPELINE REFACTORING

### Phase 2A: Rename and Restructure Pipelines
**Status:** NOT STARTED
**Priority:** HIGH
**Depends On:** OUTPUT_PIPELINE_ARCHITECTURE.md design

**Tasks:**

1. **Rename simple_manipulation → text_transformation**
   ```bash
   mv schemas/pipelines/simple_manipulation.json schemas/pipelines/text_transformation.json
   ```
   - Update all 30 configs that reference "simple_manipulation"
   - Update tests

2. **Create single_prompt_generation.json**
   - Merge functionality from: audio_generation, image_generation
   - Generic pipeline for: 1 text prompt → any medium
   - Delegates to backend_router based on config.backend

3. **Rename music_generation → dual_prompt_generation**
   - Generalize for any two-prompt scenario
   - Keep acestep as primary use case
   - Allow future dual-prompt scenarios

4. **Delete unused pipelines:**
   ```bash
   rm schemas/pipelines/simple_interception.json  # 0 configs use it
   rm schemas/pipelines/video_generation.json     # Dummy only
   ```

**Files Affected:**
- `schemas/pipelines/*.json` (4 files renamed/created/deleted)
- All 30 configs using "simple_manipulation" → update to "text_transformation"
- `test_refactored_system.py` (update pipeline names)

---

### Phase 2B: Create Standard Output-Configs
**Status:** NOT STARTED
**Priority:** HIGH
**Depends On:** Phase 2A completed

**Standard Configs to Create:**

1. **SD3.5 Large Standard** (`schemas/configs/sd35_standard.json`)
   ```json
   {
     "pipeline": "single_prompt_generation",
     "workflow_template": "sd35_standard",
     "parameters": {
       "checkpoint": "sd3.5_large.safetensors",
       "clip_g": "clip_g.safetensors",
       "t5xxl": "t5xxl_enconly.safetensors",
       "steps": 20,
       "cfg": 5.5,
       "sampler": "euler",
       "scheduler": "normal",
       "width": 1024,
       "height": 1024
     },
     "meta": {
       "backend": "comfyui",
       "output_type": "image",
       "purpose": "output_generation"
     }
   }
   ```

2. **Flux1 Dev** (`schemas/configs/flux1_dev.json`)
   ```json
   {
     "pipeline": "single_prompt_generation",
     "workflow_template": "flux1_dev",
     "parameters": {
       "checkpoint": "flux1_dev.safetensors",
       "steps": 25,
       "cfg": 1.0,
       "guidance": 3.5,
       "width": 1024,
       "height": 1024
     },
     "meta": {
       "backend": "comfyui",
       "output_type": "image"
     }
   }
   ```

3. **Flux1 Schnell** (fast variant)

4. **AceStep Standard** (`schemas/configs/acestep_standard.json`)
   ```json
   {
     "pipeline": "dual_prompt_generation",
     "workflow_template": "acestep_music",
     "input_mapping": {
       "prompt_1": "tags_node",
       "prompt_2": "lyrics_node"
     },
     "parameters": {
       "steps": 150,
       "cfg": 7.0,
       "duration": 47.0
     },
     "meta": {
       "backend": "comfyui",
       "output_type": "music"
     }
   }
   ```

5. **Stable Audio Standard** (already exists as stableaudio.json, needs review)

**Files to Create:**
- `schemas/configs/sd35_standard.json`
- `schemas/configs/flux1_dev.json`
- `schemas/configs/flux1_schnell.json`
- `schemas/configs/acestep_standard.json`
- Review/update: `schemas/configs/stableaudio.json`

---

### Phase 2C: Backend Router Enhancement
**Status:** NOT STARTED
**Priority:** MEDIUM
**Depends On:** Phase 2A completed

**Current State:**
- Backend routing exists but is chunk-specific
- No generic "output generation" routing

**Required:**

1. **Add output generation routing in backend_router.py:**
   ```python
   def route_output_generation(config, input_text, execution_mode):
       """Route output generation based on config.backend and workflow_template"""
       backend = config.meta.get('backend', 'comfyui')
       workflow_template = config.workflow_template

       if backend == 'comfyui':
           return self._route_comfyui_output(workflow_template, input_text, config)
       elif backend == 'openrouter':
           return self._route_openrouter_output(config, input_text)
       elif backend == 'ollama':
           return self._route_ollama_output(config, input_text)
       else:
           raise ValueError(f"Unknown backend: {backend}")
   ```

2. **Integrate with pipeline_executor.py:**
   - Detect if pipeline is output-generation type
   - Call backend_router.route_output_generation instead of chunk_builder

**Files to Modify:**
- `schemas/engine/backend_router.py` (add route_output_generation)
- `schemas/engine/pipeline_executor.py` (integrate routing)

---

## DOCUMENTATION

### Rewrite ARCHITECTURE.md
**Status:** NOT STARTED
**Priority:** HIGH
**Reason:** Current ARCHITECTURE.md contains outdated information and !! comments

**Approach:**
1. Read current ARCHITECTURE.md
2. Extract valid architectural principles
3. Rewrite from scratch based on current understanding
4. Incorporate OUTPUT_PIPELINE_ARCHITECTURE.md
5. Remove all !! comments (they're resolved now)
6. Add clear data flow diagrams

**Structure:**
```markdown
# DevServer Architecture

## Overview
- Three-Layer Architecture (Chunks → Pipelines → Configs)
- Input-Type-Based Pipeline Design
- Backend-Transparent Media Generation

## Layer 1: Chunks
- manipulate.json (universal text transformation)
- comfyui_image_generation.json
- comfyui_audio_generation.json

## Layer 2: Pipelines
- text_transformation (1 text → transformed text)
- single_prompt_generation (1 text → media)
- dual_prompt_generation (2 texts → media)
- image_plus_text_generation (image + text → media)

## Layer 3: Configs
- Text Transformation Configs (dada, bauhaus, etc.)
- Output Generation Configs (sd35_standard, flux1, etc.)

## Data Flow
- Text-only: input → text_transformation → output
- Text→Media: input → [text_transformation] → single_prompt_generation → media
- Direct Media: input → single_prompt_generation → media

## Backend Routing
- ComfyUI (local)
- OpenRouter (cloud)
- Ollama (local)

## Model Selection
- Task-based selection (security, vision, translation, standard, advanced)
- Execution modes (eco vs fast)
```

**Files:**
- `docs/ARCHITECTURE.md` (rewrite from scratch)

---

## CHUNK CONSOLIDATION (COMPLETED ✅)

### Completed Tasks:
- ✅ Deleted redundant chunks (translate, prompt_interception, prompt_interception_lyrics/tags)
- ✅ Fixed manipulate.json template (removed duplicate placeholders)
- ✅ Updated chunk_builder.py (removed TASK/CONTEXT aliases)
- ✅ Updated all pipelines to use manipulate chunk
- ✅ Updated translation_en.json to use simple_manipulation
- ✅ Deleted prompt_interception_single pipeline
- ✅ All tests passing (34 configs, 6 pipelines)
- ✅ Documented in DEVELOPMENT_DECISIONS.md

**Result:** Clean, minimal chunk architecture ✅

---

## TESTING REQUIREMENTS

### Unit Tests
- [ ] Test #notranslate# marker detection
- [ ] Test task-based model selection
- [ ] Test output pipeline routing
- [ ] Test config override of task_type

### Integration Tests
- [ ] Test text_transformation → single_prompt_generation chain
- [ ] Test dual_prompt_generation with AceStep
- [ ] Test different backends (ComfyUI, OpenRouter)
- [ ] Test execution modes (eco vs fast)

### End-to-End Tests
- [ ] Frontend → devserver → ComfyUI → result
- [ ] Test with all standard output configs
- [ ] Test error handling and fallbacks

---

## FUTURE CONSIDERATIONS

### Phase 3: Advanced Features (Not urgent)
- [ ] Multi-step output pipelines (text → image → video)
- [ ] Batch processing (multiple prompts → multiple images)
- [ ] Streaming output (real-time generation progress)
- [ ] image_plus_text_generation pipeline implementation
- [ ] ControlNet support
- [ ] Inpainting support

### Phase 4: Additional Backends
- [ ] Replicate API integration
- [ ] Stability AI API
- [ ] Midjourney (if API becomes available)

### Phase 5: Advanced Model Selection
- [ ] Cost optimization (choose cheapest model for task)
- [ ] Quality optimization (choose best model regardless of cost)
- [ ] Latency optimization (choose fastest model)
- [ ] Fallback chains (try model A, if fails try model B)

---

## DECISION LOG

### Resolved Decisions:
1. ✅ Keep only one manipulate chunk (delete translate, prompt_interception)
2. ✅ Use input-type-based pipelines (not media-type or backend-type)
3. ✅ Keep ComfyUI workflows in Python (not JSON)
4. ✅ Configs declare backend and workflow_template
5. ✅ Backend Router handles all backend-specific logic
6. ✅ simple_interception and video_generation pipelines: DELETE (unused)

### Pending Decisions:
- [ ] Should configs be organized in subdirectories (text_transformation/ output_generation/) or flat?
- [ ] Should we add config.input_type field explicitly or infer from pipeline?
- [ ] How to handle workflow versioning (sd35_v1, sd35_v2)?

---

## BLOCKERS / DEPENDENCIES

### Current Blockers:
- None (ready to implement)

### Dependencies:
- Phase 2B depends on Phase 2A (pipelines must exist before configs reference them)
- Testing depends on Ollama running (for full pipeline tests)
- ComfyUI integration depends on ComfyUI server running

---

## IMPLEMENTATION ORDER

**Recommended sequence:**

1. **!! Comment 5: #notranslate# logic** (1 hour)
   - Quick fix, high priority
   - Single file modification

2. **Phase 2A: Rename pipelines** (2 hours)
   - Rename files
   - Update 30 config references
   - Update tests

3. **Task-type metadata system** (2 hours)
   - Add task_type to chunk meta
   - Modify chunk_builder.py
   - Test task-based selection

4. **Phase 2B: Create standard configs** (3 hours)
   - SD3.5, Flux1, AceStep configs
   - Test each config individually

5. **Rewrite ARCHITECTURE.md** (2 hours)
   - Clean documentation
   - Remove !! comments

6. **Phase 2C: Backend router enhancement** (4 hours)
   - Add output generation routing
   - Integrate with pipeline_executor
   - Testing

**Total Estimated Time:** ~14 hours

---

## NOTES

- All !! comments from ARCHITECTURE.md are now tracked here
- Output-Pipeline design is finalized in OUTPUT_PIPELINE_ARCHITECTURE.md
- Chunk consolidation is complete and documented
- System is functional and tested (34 configs load, all tests pass)

**Next Session:** Start with #notranslate# implementation (quick win)

---

**Created:** 2025-10-26
**Status:** Ready for implementation
**Priority Tasks:** #notranslate#, Pipeline renaming, Task-type metadata
