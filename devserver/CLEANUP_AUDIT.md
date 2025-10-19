# DevServer Cleanup Audit
**Date:** 2025-10-18
**Purpose:** Identify reusable code vs obsolete files for cleanup

---

## File Inventory (106 total files)

### ✅ KEEP - Core Application Files

#### **Entry Point**
- `server.py` - Main server entry point (Waitress) ✅ **KEEP**
- `config.py` - Central configuration ✅ **KEEP** (may need updates)
- `__init__.py` - Package marker ✅ **KEEP**

#### **Flask Application**
- `my_app/__init__.py` - Flask factory ✅ **KEEP**
- `my_app/routes/` - All route handlers ✅ **KEEP** (need review)
  - `workflow_routes.py` - Main workflow execution ✅ **KEEP** (needs refactor)
  - `workflow_streaming_routes.py` - Streaming support ✅ **KEEP**
  - `schema_pipeline_routes.py` - Schema/config endpoints ✅ **KEEP** (needs refactor)
  - `export_routes.py` - Export functionality ✅ **KEEP**
  - `media_routes.py` - Media serving ✅ **KEEP**
  - `config_routes.py` - Config API ✅ **KEEP**
  - `static_routes.py` - Static files ✅ **KEEP**
  - `sse_routes.py` - Server-sent events ✅ **KEEP**

#### **Services Layer**
- `my_app/services/ollama_service.py` - Ollama backend ✅ **KEEP**
- `my_app/services/comfyui_client.py` - ComfyUI client ✅ **KEEP**
- `my_app/services/comfyui_service.py` - ComfyUI service ✅ **KEEP**
- `my_app/services/export_manager.py` - Export manager ✅ **KEEP**
- `my_app/services/streaming_response.py` - SSE streaming ✅ **KEEP**
- `my_app/services/stable_audio_client.py` - Audio generation ✅ **KEEP**
- `my_app/services/inpainting_service.py` - Inpainting ✅ **KEEP** (check if used)
- `my_app/services/workflow_logic_service.py` - Legacy workflow logic ✅ **KEEP** (legacy compatibility)
- `my_app/services/model_path_resolver.py` - Model paths ✅ **KEEP** (check if used)

#### **Utilities**
- `my_app/utils/helpers.py` - Helper functions ✅ **KEEP** (review contents)
- `my_app/utils/negative_terms.py` - Negative term processing ✅ **KEEP**
- `my_app/utils/workflow_node_injection.py` - Node injection ✅ **KEEP** (check if used)

### ✅ KEEP - Schema Engine (Needs Refactoring)

#### **Core Engine**
- `schemas/engine/schema_registry.py` - Registry system ⚠️ **REFACTOR** (currently wrong architecture)
- `schemas/engine/pipeline_executor.py` - Pipeline executor ⚠️ **REFACTOR** (needs config loader update)
- `schemas/engine/chunk_builder.py` - Chunk building ⚠️ **REFACTOR** (needs JSON config support)
- `schemas/engine/backend_router.py` - Backend routing ✅ **KEEP** (minimal changes)
- `schemas/engine/model_selector.py` - Model selection ✅ **KEEP** (good as-is)
- `schemas/engine/prompt_interception_engine.py` - Prompt interception ✅ **KEEP** (good as-is)
- `schemas/engine/comfyui_workflow_generator.py` - Workflow generation ✅ **KEEP**

### ✅ KEEP - Schema Data (Needs Restructuring)

#### **Chunks (Primitives)** - ✅ **KEEP**
- `schemas/chunks/translate.json`
- `schemas/chunks/manipulate.json`
- `schemas/chunks/prompt_interception.json`
- `schemas/chunks/prompt_interception_lyrics.json`
- `schemas/chunks/prompt_interception_tags.json`
- `schemas/chunks/comfyui_image_generation.json`
- `schemas/chunks/comfyui_audio_generation.json`

#### **Pipelines (formerly workflow_types)** - ✅ **KEEP** (rename folder)
- `schemas/workflow_types/simple_interception.json` → Rename to `pipelines/`
- `schemas/workflow_types/simple_manipulation.json`
- `schemas/workflow_types/prompt_interception_single.json`
- `schemas/workflow_types/image_generation.json`
- `schemas/workflow_types/audio_generation.json`
- `schemas/workflow_types/music_generation.json`
- `schemas/workflow_types/video_generation.json`

#### **Configs (formerly configs/ + schema_data/)** - ⚠️ **NEEDS MAJOR REFACTOR**
Current structure is wrong. Need to:
1. Convert Python configs → JSON
2. Eliminate `schema_data/` layer
3. Merge into single `configs/` directory with JSON files

**Current Python configs (convert to JSON):**
- `schemas/configs/translate/standard.py`
- `schemas/configs/manipulate/TEST_dadaismus.py`
- `schemas/configs/manipulate/TEST_color_grey.py`
- `schemas/configs/manipulate/jugendsprache.py`
- `schemas/configs/prompt_interception/translation_en.py`
- `schemas/configs/media_prompt_optimization/*` (check if used)
- `schemas/configs/image_generation/*` (check if used)

**Current schema_data (merge into configs):**
- `schemas/schema_data/TEST_dadaismus.json`
- `schemas/schema_data/TEST_dadaismus_v2.json`
- `schemas/schema_data/TEST_dadaismus_image.json`
- `schemas/schema_data/jugendsprache.json`
- `schemas/schema_data/translation_en.json`
- `schemas/schema_data/TEST_image_generation.json`

### ❌ DELETE - Test Files (All in root devserver/)

#### **Debug Files**
- `DEBUG_fast_mode_empty_prompt.py` ❌ **DELETE**
- `DEBUG_prompt_content.py` ❌ **DELETE**

#### **Test Files**
- `TEST_audio_generation.py` ❌ **DELETE**
- `TEST_auto_media_generation.py` ❌ **DELETE**
- `test_chunk_system.py` ❌ **DELETE**
- `TEST_comfyui_simple.py` ❌ **DELETE**
- `TEST_comfyui_workflow_only.py` ❌ **DELETE**
- `test_complete_pipeline.py` ❌ **DELETE**
- `TEST_corrected_architecture.py` ❌ **DELETE**
- `TEST_dadaismus_comfyui_workflow.py` ❌ **DELETE**
- `TEST_dadaismus_live.py` ❌ **DELETE**
- `TEST_execution_mode.py` ❌ **DELETE**
- `TEST_full_comfyui_pipeline.py` ❌ **DELETE**
- `TEST_live_translation.py` ❌ **DELETE**
- `TEST_multimedia_pipeline.py` ❌ **DELETE**
- `TEST_ollama_live.py` ❌ **DELETE**
- `test_pipeline_architecture.py` ❌ **DELETE**
- `TEST_server_api.py` ❌ **DELETE**
- `TEST_translation_fixed.py` ❌ **DELETE**
- `TEST_web_interface_integration.py` ❌ **DELETE**

#### **Test Artifacts**
- `TEST_generated_image_1.png` ❌ **DELETE**
- `TEST_generated_workflow.json` ❌ **DELETE**
- `TEST_workflow_output.json` ❌ **DELETE**

### ⚠️ REVIEW - Documentation (Obsolete vs Useful)

#### **Keep - Useful Documentation**
- `ARCHITECTURE.md` ✅ **KEEP** (just created, canonical reference)
- `TASK_BASED_MODEL_SELECTION.md` ✅ **KEEP** (useful reference)
- `AUTO_MEDIA_GENERATION.md` ✅ **KEEP** (useful reference)

#### **Obsolete - Old Documentation**
- `TECHNICAL_ANALYSIS.md` ❌ **DELETE** (describes old architecture)
- `AUTO_AUDIO_GENERATION_PLAN.md` ❌ **DELETE** (planning doc, already implemented)
- `SCHEMA_PIPELINE_EXPORT_DESIGN.md` ⚠️ **REVIEW** (future feature, maybe keep for reference)
- `TASK_REPORT_AUTO_MEDIA_GENERATION.md` ❌ **DELETE** (old task report)
- `TESTING.md` ❌ **DELETE** (describes obsolete test files)
- `TODO_AUTO_MEDIA_DEBUG.md` ❌ **DELETE** (old TODO)

### ❌ DELETE - Miscellaneous

#### **Demo/Template Files**
- `demo.sh` ❌ **DELETE** (demo script, not needed)
- `comfyui.config` ⚠️ **REVIEW** (check if used by anything)
- `openrouter.key` ✅ **KEEP** (API key)
- `openrouter.key.template` ✅ **KEEP** (template)
- `stability.key.template` ✅ **KEEP** (template)

---

## Summary

### Files to Delete (34 files)

**Test Files (20):**
- All `TEST_*.py` files
- All `test_*.py` files
- All `DEBUG_*.py` files
- Test artifacts (PNG, JSON)

**Documentation (5-6):**
- `TECHNICAL_ANALYSIS.md`
- `AUTO_AUDIO_GENERATION_PLAN.md`
- `TASK_REPORT_AUTO_MEDIA_GENERATION.md`
- `TESTING.md`
- `TODO_AUTO_MEDIA_DEBUG.md`
- Possibly `SCHEMA_PIPELINE_EXPORT_DESIGN.md` (future feature doc)

**Miscellaneous (1):**
- `demo.sh`

### Files to Keep & Use As-Is (40+)

**Core Application:**
- `server.py`, `config.py`
- `my_app/` (all routes, services, utils)
- `schemas/engine/backend_router.py`
- `schemas/engine/model_selector.py`
- `schemas/engine/prompt_interception_engine.py`
- `schemas/engine/comfyui_workflow_generator.py`

**Schema Data:**
- `schemas/chunks/*.json` (all 7 chunks)

### Files to Refactor (10)

**Engine Code:**
- `schemas/engine/schema_registry.py` → New `config_loader.py`
- `schemas/engine/chunk_builder.py` → Update for JSON configs
- `schemas/engine/pipeline_executor.py` → Update for new config flow

**Schema Data:**
- `schemas/workflow_types/*.json` → Rename to `pipelines/`
- `schemas/configs/**/*.py` → Convert to JSON
- `schemas/schema_data/*.json` → Eliminate, merge into configs

**Routes:**
- `my_app/routes/workflow_routes.py` → Update config loading
- `my_app/routes/schema_pipeline_routes.py` → Update API

---

## Detailed Analysis by Component

### my_app/routes/ Analysis

#### `workflow_routes.py` (Lines 1-800+)
**Purpose:** Main workflow execution endpoint
**Status:** ✅ **KEEP**, needs refactoring
**Issues:**
- Lines 388-553: Schema pipeline handling (needs config loader update)
- Currently loads `schema_data/`, needs to load `configs/` directly
**Action:** Update config loading logic after refactoring engine

#### `schema_pipeline_routes.py`
**Purpose:** Schema/config API endpoints (list, info, etc.)
**Status:** ✅ **KEEP**, needs refactoring
**Issues:**
- Returns "schema" in API responses, should return "config"
- Needs to adapt to new architecture
**Action:** Update after config_loader.py is created

#### All Other Routes
**Status:** ✅ **KEEP AS-IS**
- `workflow_streaming_routes.py` - Streaming works independently
- `export_routes.py` - Export works independently
- `media_routes.py` - Media serving works independently
- `config_routes.py` - General config API
- `static_routes.py` - Static file serving
- `sse_routes.py` - SSE infrastructure

### my_app/services/ Analysis

#### **Keep As-Is:**
- `ollama_service.py` - Ollama backend (good)
- `comfyui_client.py` - ComfyUI client (good)
- `comfyui_service.py` - ComfyUI service (good)
- `export_manager.py` - Export functionality (good)
- `streaming_response.py` - SSE streaming (good)
- `stable_audio_client.py` - Audio generation (good)
- `workflow_logic_service.py` - Legacy workflow support (needed for compatibility)

#### **Review & Possibly Remove:**
- `inpainting_service.py` - Check if used anywhere
- `model_path_resolver.py` - Check if used anywhere

### my_app/utils/ Analysis

#### **Keep:**
- `helpers.py` - Contains `parse_hidden_commands()` and other utils (good)
- `negative_terms.py` - Negative term normalization (good)

#### **Review:**
- `workflow_node_injection.py` - Check if used anywhere

### schemas/engine/ Analysis

#### **Keep & Use As-Is:**
- `backend_router.py` ✅ **EXCELLENT** - Backend routing logic is solid
- `model_selector.py` ✅ **EXCELLENT** - Task-based model selection works well
- `prompt_interception_engine.py` ✅ **GOOD** - Prompt interception works
- `comfyui_workflow_generator.py` ✅ **GOOD** - Workflow generation works

#### **Refactor:**
- `schema_registry.py` → Create new `config_loader.py`
  - Current: Loads schema_data + workflow_types, resolves mappings
  - New: Load configs + pipelines directly, resolve instruction types

- `chunk_builder.py` → Update for JSON configs
  - Current: Loads Python configs with `importlib`, expects INSTRUCTIONS/PARAMETERS/METADATA
  - New: Load JSON configs, support arbitrary fields

- `pipeline_executor.py` → Minimal updates
  - Current: Uses schema_registry
  - New: Use config_loader
  - Keep execution logic mostly as-is

---

## Cleanup Plan

### Phase 1: Delete Obsolete Files ✅
1. Delete all TEST_*.py and test_*.py files (20 files)
2. Delete DEBUG_*.py files (2 files)
3. Delete obsolete documentation (5-6 files)
4. Delete demo.sh
5. Delete test artifacts (PNG, JSON)

**Total to delete: ~28-30 files**

### Phase 2: Restructure Schema Directories ✅
1. Rename `schemas/workflow_types/` → `schemas/pipelines/`
2. Delete `schemas/schema_data/` (will be replaced by new configs)
3. Keep `schemas/chunks/` as-is
4. Prepare `schemas/configs/` for JSON files (delete old .py files later)

### Phase 3: Create New Architecture Files ✅
1. Create `schemas/instruction_types.json`
2. Create `schemas/engine/config_loader.py` (replaces schema_registry.py)
3. Create `schemas/engine/instruction_resolver.py`
4. Create example configs in JSON format

### Phase 4: Refactor Existing Engine Code ✅
1. Update `chunk_builder.py` for JSON configs
2. Update `pipeline_executor.py` to use config_loader
3. Update `workflow_routes.py` for new config loading
4. Update `schema_pipeline_routes.py` for new API

### Phase 5: Testing ✅
1. Create new test suite (in separate tests/ directory, not root)
2. Test config loading
3. Test pipeline execution
4. Test end-to-end flow

---

## Questions for User

1. **inpainting_service.py** - Is inpainting functionality still used? Should we keep it?
2. **model_path_resolver.py** - Is this used anywhere? Grep shows minimal references.
3. **workflow_node_injection.py** - Still needed?
4. **SCHEMA_PIPELINE_EXPORT_DESIGN.md** - Keep as future feature reference or delete?
5. **comfyui.config** - Still used?

---

## Next Steps

Waiting for user approval to proceed with cleanup:
1. Confirm files to delete
2. Execute Phase 1 cleanup (delete obsolete files)
3. Execute Phase 2 restructuring (rename/reorganize directories)
4. Create new architecture files (Phase 3)
5. Refactor core code (Phase 4)
