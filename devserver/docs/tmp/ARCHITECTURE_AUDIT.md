# DevServer Architecture Audit
**Date:** 2025-10-26
**Purpose:** Technical consistency analysis of actual codebase
**Status:** TEMPORARY - Will be archived after ARCHITECTURE.md update

---

## Executive Summary

**Current State:** Post instruction_types removal (2025-10-26)
- ✅ Core 3-layer architecture functional
- ⚠️ Legacy code still present (_old.py files)
- ⚠️ Two config directories (schema_data vs configs)
- ⚠️ Some engine modules may be obsolete

---

## File System Structure (Actual)

### schemas/ Directory
```
schemas/
├── chunks/                    # Layer 1: Primitives (7 files)
├── pipelines/                 # Layer 2: Structure (7 files)
├── configs/                   # Layer 3: Content (34 files) ✅ ACTIVE
├── schema_data/              # Legacy config location (7 files) ⚠️
├── engine/                    # Core processing modules
│   ├── config_loader.py       ✅ ACTIVE
│   ├── chunk_builder.py       ✅ ACTIVE
│   ├── pipeline_executor.py   ✅ ACTIVE
│   ├── backend_router.py      ✅ ACTIVE
│   ├── model_selector.py      ✅ ACTIVE
│   ├── comfyui_workflow_generator.py  ✅ ACTIVE
│   ├── prompt_interception_engine.py  ✅ ACTIVE
│   ├── schema_registry.py     ⚠️ LEGACY? (pre-refactoring)
│   ├── chunk_builder_old.py   ⚠️ LEGACY
│   ├── pipeline_executor_old.py ⚠️ LEGACY
│   ├── instruction_resolver.py.OBSOLETE ✅ MARKED
│   └── __init__.py
└── instruction_types.json.OBSOLETE  ✅ MARKED
```

### configs/ vs configs_old_DELETEME/
```
configs_old_DELETEME/          # Python-based legacy configs
configs/                       # JSON configs (CURRENT) ✅
```

---

## Layer 1: Chunks (Primitives)

**Location:** `schemas/chunks/`
**Count:** 7 chunk templates

### Inventory
1. ✅ **manipulate.json** - Text manipulation
2. ✅ **translate.json** - Translation
3. ✅ **prompt_interception.json** - Prompt transformation
4. ✅ **prompt_interception_tags.json** - Music tags generation
5. ✅ **prompt_interception_lyrics.json** - Music lyrics generation
6. ✅ **comfyui_image_generation.json** - Image generation
7. ✅ **comfyui_audio_generation.json** - Audio generation

### Chunk Template Structure (Verified)
```json
{
  "name": "manipulate",
  "backend_type": "ollama",
  "model": "llama3.2:latest",
  "template": "{{INSTRUCTION}}\n\nUser Input:\n{{INPUT_TEXT}}",
  "parameters": {
    "temperature": 0.8,
    "max_tokens": 1000
  }
}
```

### Placeholders Used (from code analysis)
- `{{INSTRUCTION}}` - from config.context
- `{{INSTRUCTIONS}}` - alias for INSTRUCTION
- `{{TASK}}` - alias for INSTRUCTION
- `{{CONTEXT}}` - alias for INSTRUCTION
- `{{INPUT_TEXT}}` - user input
- `{{PREVIOUS_OUTPUT}}` - pipeline chain output
- `{{USER_INPUT}}` - original user input

**Finding:** All chunks use template-based placeholder system ✅

---

## Layer 2: Pipelines (Structure)

**Location:** `schemas/pipelines/`
**Count:** 7 pipeline definitions

### Inventory
1. ✅ **simple_manipulation.json** - Single chunk: [manipulate]
2. ✅ **simple_interception.json** - Two chunks: [prompt_interception, manipulate]
3. ✅ **prompt_interception_single.json** - Single: [prompt_interception]
4. ✅ **image_generation.json** - [prompt_interception, comfyui_image_generation]
5. ✅ **audio_generation.json** - [prompt_interception, comfyui_audio_generation]
6. ✅ **music_generation.json** - [prompt_interception_tags, prompt_interception_lyrics, comfyui_music_generation]
7. ✅ **video_generation.json** - [prompt_interception, comfyui_video_generation]

### Pipeline Structure (Verified)
```json
{
  "name": "simple_manipulation",
  "description": "Single manipulation step",
  "chunks": ["manipulate"],
  "required_fields": [],
  "defaults": {},
  "meta": {}
}
```

**Finding:** Pipelines are pure structure (no content) ✅

---

## Layer 3: Configs (Content)

**Location:** `schemas/configs/`
**Count:** 34 config files

### Sample Config Structure (Post instruction_types removal)
```json
{
  "name": {
    "en": "Dadaism",
    "de": "Dadaismus"
  },
  "description": {
    "en": "Transform prompts through Dadaist perspective",
    "de": "Transformiert Prompts durch dadaistische Perspektive"
  },
  "category": {
    "en": "Art Movements",
    "de": "Kunstbewegungen"
  },
  "pipeline": "simple_manipulation",
  "context": "You are an artist working in the spirit of Dadaism...",
  "parameters": {
    "temperature": 0.9
  },
  "media_preferences": {
    "preferred_media": ["image"]
  },
  "meta": {
    "tags": ["art", "experimental"]
  }
}
```

### Field Analysis
| Field | Purpose | Status |
|-------|---------|--------|
| `name` | Multilingual display name | ✅ Required |
| `description` | Multilingual description | ✅ Required |
| `category` | UI categorization | ✅ Optional |
| `pipeline` | Pipeline reference | ✅ Required |
| `context` | Complete instruction text | ✅ Core field |
| `parameters` | LLM parameters override | ✅ Optional |
| `media_preferences` | Media type hints | ✅ Optional |
| `meta` | Additional metadata | ✅ Optional |
| ~~`instruction_type`~~ | ❌ REMOVED (2025-10-26) |

**Finding:** Config structure is clean, context contains full instruction ✅

---

## Engine Modules Analysis

### Active Modules (Verified)

#### 1. config_loader.py ✅
**Purpose:** Load and resolve configs + pipelines
**Dataclasses:**
- `Pipeline` - Pipeline definition
- `Config` - Config definition
- `ResolvedConfig` - Merged pipeline + config

**Key Methods:**
- `initialize(schemas_path)` - Load all definitions
- `get_config(name)` - Get resolved config
- `list_configs()` - List all configs
- `list_pipelines()` - List all pipelines

**Status:** ACTIVE, post instruction_types cleanup ✅

#### 2. chunk_builder.py ✅
**Purpose:** Build executable chunks from templates + resolved configs
**Key Changes (2025-10-26):**
- ❌ Removed instruction_resolver import
- ✅ Now uses `resolved_config.context` directly
- ✅ Populates all placeholders from context

**Status:** ACTIVE, refactored ✅

#### 3. pipeline_executor.py ✅
**Purpose:** Orchestrate pipeline execution
**Key Methods:**
- `execute_pipeline(config_name, input_text, execution_mode)`
- `stream_pipeline(...)` - Streaming execution
- `get_config_info(config_name)` - Config metadata

**Status:** ACTIVE, post instruction_types cleanup ✅

#### 4. backend_router.py ✅
**Purpose:** Route requests to Ollama/ComfyUI/OpenRouter
**Status:** ACTIVE ✅

#### 5. model_selector.py ✅
**Purpose:** Select models based on execution_mode (eco/fast)
**Status:** ACTIVE ✅

#### 6. comfyui_workflow_generator.py ✅
**Purpose:** Generate ComfyUI workflows dynamically
**Status:** ACTIVE ✅

#### 7. prompt_interception_engine.py ✅
**Purpose:** Core prompt interception logic (legacy integration)
**Status:** ACTIVE (legacy bridge) ✅

### Potentially Obsolete Modules

#### schema_registry.py ⚠️
**Purpose:** Pre-refactoring config/schema management
**Status:** ⚠️ LIKELY OBSOLETE (replaced by config_loader.py)
**Action Required:** Verify if still used, mark as .OBSOLETE if not

#### chunk_builder_old.py ⚠️
**Purpose:** Pre-refactoring chunk builder
**Status:** ⚠️ LEGACY - Should be marked .OBSOLETE

#### pipeline_executor_old.py ⚠️
**Purpose:** Pre-refactoring executor
**Status:** ⚠️ LEGACY - Should be marked .OBSOLETE

---

## Data Flow (Verified from Code)

### Current Architecture (Post instruction_types removal)

```
1. User Request
   ↓
2. workflow_routes.py receives config_name + input_text
   ↓
3. pipeline_executor.execute_pipeline(config_name, input_text, execution_mode)
   ↓
4. config_loader.get_config(config_name) → ResolvedConfig
   ↓
5. For each chunk in ResolvedConfig.chunks:
   a) chunk_builder.build_chunk(chunk_name, resolved_config, context)
   b) Resolve placeholders:
      - {{INSTRUCTION}} ← resolved_config.context
      - {{INPUT_TEXT}} ← context.input_text
      - {{PREVIOUS_OUTPUT}} ← context.previous_output
   c) Select model based on execution_mode (model_selector)
   d) Build chunk_request with final prompt
   ↓
6. backend_router.process_request(chunk_request)
   ↓
7. Ollama/ComfyUI/OpenRouter execution
   ↓
8. Return result, chain to next chunk
```

**Finding:** Flow is clean, no instruction_types indirection ✅

---

## Inconsistencies Found

### 1. ⚠️ Duplicate Config Locations
**Issue:** Both `schemas/configs/` and `schemas/schema_data/` contain configs
**Current State:**
- `configs/` - 34 JSON configs (ACTIVE)
- `schema_data/` - 7 configs (TEST files + legacy)

**Recommendation:**
- Verify schema_data contents
- Move TEST configs to test directory
- Delete or mark schema_data as obsolete

### 2. ⚠️ Legacy Engine Modules
**Issue:** Three `*_old.py` files still present
**Files:**
- `chunk_builder_old.py`
- `pipeline_executor_old.py`
- `schema_registry.py` (may be obsolete)

**Recommendation:**
- Verify schema_registry.py is not imported anywhere
- Mark all as .OBSOLETE if unused

### 3. ⚠️ Legacy configs_old_DELETEME/
**Issue:** Old Python-based configs still present
**Status:** Marked for deletion but not deleted

**Recommendation:** Delete after final verification

### 4. ⚠️ ComfyUI Integration Unclear
**Issue:** `comfyui_music_generation` chunk referenced but no JSON file
**Files Missing:**
- `schemas/chunks/comfyui_music_generation.json`
- `schemas/chunks/comfyui_video_generation.json`

**Recommendation:**
- Verify if these are generated dynamically
- Document ComfyUI chunk generation pattern

---

## Test Coverage

### Existing Tests
1. ✅ **test_refactored_system.py** - Component tests (passing)
   - Config loader
   - Pipeline executor info methods
2. ⚠️ **test_pipeline_execution.py** - Full execution tests (requires Ollama)

### Test Status (from code)
```bash
python3 test_refactored_system.py
# Result: ✅ ALL TESTS PASSED
# - 34 configs loaded
# - All pipelines resolved
# - No instruction_type errors
```

**Finding:** Core architecture tests passing ✅

---

## API Routes Analysis

### workflow_routes.py

**Key Routes:**
1. `/workflow_metadata` - Legacy workflow metadata
2. `/pipeline_configs_metadata` - Config metadata (JSON read)
3. `/execute_pipeline` - Pipeline execution endpoint

**Recent Changes (2025-10-26):**
- ❌ Removed `instruction_type` from metadata response
- ✅ Now returns clean metadata without obsolete fields

**Status:** ACTIVE, cleaned up ✅

---

## Documentation vs Reality

### ARCHITECTURE.md (Current Root File)
**Issues Found:**
- ❌ Documents instruction_types system (obsolete)
- ❌ Shows instruction_type in config examples
- ❌ References instruction_types.json file
- ❌ Shows instruction_resolver in data flow

**Status:** REQUIRES MAJOR UPDATE

### DEVSERVER_COMPREHENSIVE_DOCUMENTATION.md
**Issues Found:**
- ❌ Documents instruction_types
- ❌ Shows instruction_type in examples

**Status:** REQUIRES UPDATE

---

## Recommendations

### Immediate Actions (Critical)
1. ✅ **DONE:** Remove instruction_types from code
2. ✅ **DONE:** Update test_refactored_system.py
3. ✅ **DONE:** Organize documentation structure
4. 📋 **TODO:** Update ARCHITECTURE.md
5. 📋 **TODO:** Update DEVSERVER_COMPREHENSIVE_DOCUMENTATION.md

### Cleanup Actions (High Priority)
1. 📋 Verify and mark schema_registry.py as .OBSOLETE
2. 📋 Mark chunk_builder_old.py as .OBSOLETE
3. 📋 Mark pipeline_executor_old.py as .OBSOLETE
4. 📋 Verify schema_data/ contents and clean up
5. 📋 Delete configs_old_DELETEME/ after verification

### Missing Documentation
1. 📋 ComfyUI chunk generation pattern
2. 📋 Backend routing logic
3. 📋 Model selection strategy (execution_mode)
4. 📋 Media preferences usage

---

## Conclusion

**Architecture Status:** ✅ Functionally correct post instruction_types removal

**Code Quality:** ✅ Clean 3-layer architecture implemented

**Documentation Status:** ❌ Outdated - requires update

**Legacy Code:** ⚠️ Present but isolated - needs cleanup

**Next Steps:**
1. Update ARCHITECTURE.md based on this audit
2. Update DEVSERVER_COMPREHENSIVE_DOCUMENTATION.md
3. Clean up legacy modules
4. Document missing patterns

---

**Audit Completed:** 2025-10-26
**Next Review:** After documentation updates
**Archive After:** ARCHITECTURE.md update complete
