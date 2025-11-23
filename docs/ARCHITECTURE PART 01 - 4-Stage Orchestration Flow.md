# DevServer Architecture
**AI4ArtsEd Development Server - Complete Technical Reference**

> **Last Updated:** 2025-11-09
> **Status:** AUTHORITATIVE - 4-Stage Orchestration Architecture Documented (v2.0.0-alpha.1)
> **Version:** 3.0 (4-Stage Flow + Components Reference - Fully Consolidated)

---
THIS IS A MULTI-PART-DOCUMENTATION:
Pattern: ARCHITECTURE PART XX - SUBJECTMATTER.md

Use it accordingly.

THIS FILE IS ABOUT THE 4-STAGE-ORCHESTRATION.

---

## 🏗️ MANDATORY: File Structure Rules

**⚠️ CRITICAL: NEVER create new directories without consulting these rules.**

### Root Level (`/ai4artsed_webserver/`)

**ONLY these directories are allowed at project root:**
- `server/` - ⚠️ LEGACY - DO NOT TOUCH
- `public/` - ✅ Vue-based frontend (new architecture)
- `docs/` - ✅ Project documentation (authoritative architecture docs)
- `devserver/` - ✅ NEW ARCHITECTURE (work here)
- `exports/` - ✅ Pipeline run storage (`/json/`, `/media/`)
- `workflows/` - ✅ ComfyUI workflows (if applicable)

### DevServer Level (`/devserver/`)

**ONLY these directories are allowed at devserver root:**
- **Core files:** `server.py`, `config.py`, `CLAUDE.md`
- `schemas/` - Pipeline system (chunks, pipelines, configs, engine)
- `my_app/` - Application code (routes, services)
- `tests/` - Test files
- `archive/` - Deprecated code (DO NOT EDIT)

**❌ FORBIDDEN at devserver root:**
- New service modules → Put in `/devserver/my_app/services/`
- New route modules → Put in `/devserver/my_app/routes/`
- Documentation → Use `/docs/` (project root)
- Frontend projects → Use `/public/` (project root)

### Documentation Structure

**ALL documentation MUST go in:** `/docs/` (project root)

**Current structure:**
- `ARCHITECTURE PART XX - *.md` - Technical reference (AUTHORITATIVE)
- `DEVELOPMENT_DECISIONS.md` - Decision history
- `DEVELOPMENT_LOG.md` - Session tracking and costs
- `README_FIRST.md` - Mandatory reading for new sessions (if exists)
- `devserver_todos.md` - Task tracking

**❌ FORBIDDEN:**
- `/devserver/docs/` - Session-specific docs must go in `/docs/`
- Documentation in random locations

### Service Module Location

**ALL service modules MUST go in:** `/devserver/my_app/services/`

**Examples:**
- ✅ `/devserver/my_app/services/ollama_service.py`
- ✅ `/devserver/my_app/services/comfyui_service.py`
- ✅ `/devserver/my_app/services/media_storage.py`
- ✅ `/devserver/my_app/services/pipeline_recorder/` (if directory)
- ❌ `/devserver/pipeline_recorder/` - WRONG LOCATION

### Frontend Location

**Active frontend:** `/public/` (project root)

**Current status:**
- ✅ `/public/` - Vue-based frontend (new architecture)
- ❌ `/devserver/public_dev/` - DEPRECATED (do not use)

**Server configuration:** `config.py` → `PUBLIC_DIR = Path(__file__).parent.parent / "public"`

### Why These Rules?

1. **Consistency:** All sessions follow same structure
2. **Clarity:** No guessing where files belong
3. **Maintainability:** Easy to find and modify code
4. **Documentation:** Single source of truth in `/docs/`
5. **Architecture Transparency:** Structure reflects design decisions

**If you need to create new directories:** Ask the user first.

---

# PART I: ORCHESTRATION

---

## 1. 4-Stage Orchestration Flow

**⭐ AUTHORITATIVE SECTION - Read this first before implementing any flow logic**

**Version:** 2.2 (2025-11-23 - Session 65: Stage 2 Split into 2-Phase Execution)
**Source:** Consolidated from 4_STAGE_ARCHITECTURE.md

### 1.1 Executive Summary

**DevServer orchestrates a 4-stage flow where:**
- **Stage 1** runs once per user input (based on input type, not pipeline declaration)
- **Stage 2** executes the main pipeline (can be complex: loops, branches, multiple outputs)
- **Stage 3-4** run once PER OUTPUT REQUEST from Stage 2 (not once per pipeline)

**Key Principle:** Pipelines are DUMB (declare inputs/outputs), DevServer is SMART (knows safety rules).

### 1.2 Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ DevServer (schema_pipeline_routes.py)                          │
│ ROLE: Smart Orchestrator - Knows 4-Stage Flow & Safety Rules   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STAGE 1: Pre-Interception (Safety Only - Original Language)    │
│ ════════════════════════════════════════════════════════════   │
│   DevServer reads: pipeline.input_requirements                 │
│   - texts: N  → Run text_safety for each (NO translation!)    │
│   - images: M → Run image_safety for each                      │
│   - Bilingual: Works in DE or EN (§86a filters both)          │
│                                                                 │
│   Example: {"texts": 2, "images": 1}                           │
│   → text_safety(text1_in_original_language)                   │
│   → text_safety(text2_in_original_language)                   │
│   → image_safety(image1)                                       │
│   Text stays in original language (DE/EN) for Stage 2!        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STAGE 2: Interception + Optimization (Main Pipeline)           │
│ ════════════════════════════════════════════════════════════   │
│   **2-PHASE EXECUTION** (Session 65, 2025-11-23):             │
│                                                                 │
│   Phase 1: INTERCEPTION (Pedagogical Transformation)          │
│     execute_stage2_with_optimization() → Call 1               │
│     - Uses: config.context (pädagogischer Context)            │
│     - Model: STAGE2_INTERCEPTION_MODEL (from config.py)       │
│     - Output: interception_result (editierbar)                │
│                                                                 │
│   Phase 2: OPTIMIZATION (Model-specific Refinement)           │
│     execute_stage2_with_optimization() → Call 2               │
│     - Uses: output_config.optimization_instruction            │
│     - Model: STAGE2_INTERCEPTION_MODEL (from config.py)       │
│     - Input: interception_result (from Phase 1)               │
│     - Output: optimized_prompt (editierbar)                   │
│                                                                 │
│   Why Split?                                                   │
│   - LLM was overwhelmed by dual task (pedagogy + optimization)│
│   - User needs editability BETWEEN phases                     │
│   - Model selection happens BEFORE optimization               │
│                                                                 │
│   PipelineExecutor.execute_pipeline(config, inputs)            │
│   - DUMB: Just executes chunks                                 │
│   - NO pre-processing, NO safety checks, NO translation       │
│   - CAN: loop, branch, request multiple outputs               │
│                                                                 │

#### Media-Specific Optimization (Config Override Pattern)

**Feature:** Extend Stage 2 context with output-specific optimization instructions

**Use Case:** SD3.5 Large uses Dual CLIP architecture (clip_g + t5xxl) requiring specialized prompt optimization

**Implementation Pattern:**
1. Output config declares `OUTPUT_CHUNK` parameter pointing to chunk name
2. DevServer loads chunk JSON directly from filesystem
3. Extract `meta.optimization_instruction` from output chunk
4. Use `dataclasses.replace()` to create modified config with extended context
5. Pass `config_override` to pipeline executor

**Code Example:**
```python
from dataclasses import replace

# Load optimization instruction from output chunk metadata
optimization_instruction = output_chunk['meta'].get('optimization_instruction')

if optimization_instruction:
    # Get original context
    original_context = config.context if hasattr(config, 'context') else ""
    new_context = original_context + "\n\n" + optimization_instruction

    # Create modified config using dataclasses.replace()
    stage2_config = replace(
        config,
        context=new_context,
        meta={**config.meta, 'optimization_added': True}
    )

    # Execute pipeline with overridden config
    result = await pipeline_executor.execute_pipeline(
        config_name=schema_name,
        input_text=input_text,
        config_override=stage2_config
    )
```

**Why This Pattern:**
- ✅ Single LLM call combines interception + optimization (pedagogical constraint)
- ✅ Optimization instruction stored in output chunk where model config lives
- ✅ Fetched at runtime based on selected output config
- ✅ Non-invasive: Original config unchanged, override applied dynamically

**Critical Implementation Notes:**
- ⚠️ MUST use `dataclasses.replace()`, NOT `Config.from_dict()` (doesn't exist)
- ⚠️ MUST load chunks directly from filesystem, NOT via `ConfigLoader.get_chunk()` (doesn't exist)
- ⚠️ MUST use `await` for pipeline execution, NOT `asyncio.run()` (can't nest event loops)

**Bug History:** Session 64 Part 3 (2025-11-22) - Fixed 3 critical implementation bugs that prevented this feature from working

│   Pipeline returns: PipelineResult {                           │
│     final_output: "transformed + optimized text (orig lang)",  │
│     output_requests: [                                         │
│       {type: "image", prompt: "...", params: {...}},          │
│       {type: "audio", prompt: "...", params: {...}}           │
│     ]                                                          │
│   }                                                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ STAGE 3-4: For EACH output_request from Stage 2                │
│ ════════════════════════════════════════════════════════════   │
│   FOR EACH request in pipeline_result.output_requests:         │
│                                                                 │
│     STAGE 3a: Translation (if needed)                          │
│       - IF source_language != 'en': Translate DE → EN         │
│       - Media generation requires English prompts             │
│       - User can edit BEFORE this stage (in original lang)    │
│                                                                 │
│     STAGE 3b: Pre-Output Safety                                │
│       - Hybrid: Fast string-match → LLM if needed             │
│       - Check: translated_prompt against safety_level         │
│       - If blocked: Skip Stage 4, return text alternative     │
│                                                                 │
│     STAGE 4: Media Generation                                  │
│       - Execute output config (e.g., gpt5_image)              │
│       - Generate media with English prompt                     │
│       - Return media reference (prompt_id, URL, etc.)         │
│                                                                 │
│   Collect all generated media + metadata                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Separation of Concerns

#### What Pipelines Declare (DUMB)

**Pipeline configs declare ONLY input/output structure:**

```json
{
  "name": "complex_interception",
  "input_requirements": {
    "texts": 2,           // "I need 2 text inputs"
    "images": 1           // "I need 1 image input"
  },
  "chunks": ["manipulate", "translate", ...],
  "control_flow": "iterative",
  "meta": {
    "max_iterations": 8,
    "supports_multiple_outputs": true
  }
}
```

**Pipelines DO NOT declare:**
- ❌ Safety requirements (DevServer knows this)
- ❌ Translation needs (DevServer knows: text → translate)
- ❌ Pre-processing steps (DevServer orchestrates Stage 1)
- ❌ When to run safety checks (DevServer orchestrates Stage 3)

#### What DevServer Knows (SMART)

**DevServer has hardcoded safety rules:**

```python
# schema_pipeline_routes.py

STAGE1_RULES = {
    "text": ["translation", "text_safety_stage1"],
    "image": ["image_safety_stage1"],
    "audio": ["audio_safety_stage1"]  # Future
}

STAGE3_RULES = {
    "image": "text_safety_check_{safety_level}",  # kids/youth/off
    "audio": "audio_safety_check_{safety_level}",  # Future
    "video": "video_safety_check_{safety_level}"   # Future
}
```

**Why non-redundant?**
- If pipeline says `"texts": 2`, DevServer runs Stage 1 safety for BOTH texts
- No duplication in pipeline configs
- Change safety rules in ONE place (DevServer)
- Prevents inconsistencies

### 1.4 Stage-by-Stage Flow

[See above, 1.2 Core Architecture and IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md]

### 1.5 Complex Pipeline Examples

#### Example 1: Simple Text Transformation + Image

**User Input:** "EIne Blume auf der Wiese"
**Config:** overdrive.json
**Execution Mode:** fast
**Safety Level:** kids

**Flow:**
```
┌─ STAGE 1 (Run ONCE) ─────────────────────────────────────────┐
│ Input: "EIne Blume auf der Wiese"                            │
│ → Translation: "One flower on the meadow"                    │
│ → Stage 1 Safety: PASSED (fast-path, no unsafe terms)       │
└──────────────────────────────────────────────────────────────┘

┌─ STAGE 2 (Main Pipeline) ────────────────────────────────────┐
│ Pipeline: overdrive (text_transformation)                    │
│ Input: "One flower on the meadow"                            │
│ → manipulate chunk with overdrive context                    │
│ Output: "In the vast, undulating sea of emerald..."         │
│                                                              │
│ Output Requests: [                                           │
│   {type: "image", prompt: "In the vast, undulating..."}     │
│ ]                                                            │
└──────────────────────────────────────────────────────────────┘

┌─ STAGE 3-4 (Run ONCE per output request) ───────────────────┐
│ Request #1: image                                            │
│                                                              │
│ STAGE 3: Pre-Output Safety                                  │
│   Prompt: "In the vast, undulating..."                      │
│   → Fast-path check: No unsafe terms → PASSED (0.1ms)       │
│                                                              │
│ STAGE 4: Media Generation                                   │
│   Lookup: image/fast → gpt5_image                           │
│   → execute_pipeline('gpt5_image', prompt) [NO STAGE 1-3!]  │
│   → Returns: prompt_id "abc123"                             │
└──────────────────────────────────────────────────────────────┘
```

**Current Bug (What Happens Now):**
```
✅ Stage 1 runs once → Good
✅ Stage 2 runs once → Good
✅ Stage 3 runs once → Good
❌ Stage 4 calls execute_pipeline('gpt5_image', ...)
   → execute_pipeline() runs Stage 1-3 AGAIN! → BAD
   → Translation runs on already-English text
   → Safety runs twice
   → Wasted time + API calls
```

#### Example 3: Multi-Output (Model Comparison)

**Scenario:** Generate same prompt with multiple models for comparison

**Config:** `image_comparison.json`
```json
{
  "pipeline": "text_transformation",
  "context": "Pass through unchanged",
  "media_preferences": {
    "output_configs": ["sd35_large", "gpt5_image"]
  }
}
```

**Flow:**
```
Input: "Eine Blume auf der Wiese"
  ↓
Stage 1: translation + text_safety (once)
  → "A flower on the meadow" + PASSED
  ↓
Stage 2: text_transformation (once)
  → "A flower on the meadow" (pass-through)
  ↓
Stage 3-4 Loop: FOR EACH output_config
  ├─ Iteration 1: sd35_large
  │  ├─ Stage 3: Pre-Output Safety ✅
  │  └─ Stage 4: ComfyUI workflow → image_1.png
  └─ Iteration 2: gpt5_image
     ├─ Stage 3: Pre-Output Safety ✅
     └─ Stage 4: OpenRouter API → image_2.png

Response: {
  "media_outputs": [
    {"config": "sd35_large", "output": "prompt_id_1"},
    {"config": "gpt5_image", "output": "base64_data"}
  ]
}
```

**Key Points:**
✅ Stage 1 runs once (not 2x) - no redundant translation
✅ Stage 2 runs once (not 2x) - no redundant pipeline
✅ Stage 3-4 loop per output - each gets independent safety check
✅ Efficient: Only outputs require duplication, not inputs

**Use Cases:**
- Model comparison (SD3.5 vs GPT-5)
- Multi-format output (image + audio)
- Multi-resolution output (1024px + 2048px)

**Implementation:** See `schema_pipeline_routes.py` Stage 3-4 Loop

#### Example 4: Recursive Pipeline (Stille Post)

**Scenario:** 8-iteration translation loop (Chinese Whispers)

**Config:** `stillepost.json`
```json
{
  "pipeline": "text_transformation_recursive",
  "parameters": {
    "iterations": 8,
    "use_random_languages": true,
    "final_language": "en"
  }
}
```

**Flow:**
```
Input: "Eine Blume auf der Wiese"
  ↓
Stage 1: translation + text_safety (once)
  → "A flower on the meadow" + PASSED
  ↓
Stage 2: text_transformation_recursive (once, loops internally)
  Iteration 1: translate to Hindi
  Iteration 2: translate to Polish
  ...
  Iteration 8: translate to English
  → "The Dutch translation of..." (mangled text)
  ↓
Stage 3: Pre-Output Safety ✅
  ↓
Stage 4: Media Generation → image.png
```

**Key Points:**
✅ Stage 1 runs once (not 8x) - Critical test PASSED
✅ Loop runs INSIDE Stage 2 pipeline
✅ Config controls loop behavior (iterations, languages, final_language)
❌ Does NOT call execute_pipeline() recursively (would trigger Stage 1-3 redundancy)

**Pedagogical Goal:**
- Students see prompt degradation over iterations
- "Stille Post" (Chinese Whispers) workflow
- User-editable configs for different iteration counts

**Implementation:** See `pipeline_executor.py` _execute_recursive_pipeline_steps()

### 1.6 Implementation Status

**Current (v2.0.0-alpha.1 - 2025-11-09):**
- ✅ Stage 1-3 logic in `schema_pipeline_routes.py` - CORRECT (Session 9)
- ✅ PipelineExecutor is DUMB engine - CORRECT (Session 9)
- ✅ Non-redundant safety rules - IMPLEMENTED (Session 9)
- ✅ Recursive Pipeline System - IMPLEMENTED (Session 11 Part 1)
- ✅ Multi-Output Support - IMPLEMENTED (Session 11 Part 2)
- ✅ LivePipelineRecorder as single source of truth - IMPLEMENTED (Session 37)
- ✅ stage4_only feature for fast regeneration - FIXED (Session 39)
- ✅ Stage 2 split into 2-phase execution - IMPLEMENTED (Session 65)
- ✅ execution_mode parameter REMOVED - REFACTORED (Session 65)
- ✅ Centralized model selection via config.py - IMPLEMENTED (Session 65)

**Validation Tests:**
- ✅ Stillepost (8 iterations): Stage 1 ran once (not 8x) - PASSED
- ✅ Image Comparison (2 outputs): Stage 1 ran once (not 2x) - PASSED
- ✅ Simple config (dada): Stage 1-4 all ran once - PASSED
- ✅ Logs confirm clean execution (no redundancy) - PASSED
- ✅ media_type UnboundLocalError fixed (Session 39) - PASSED

**Architecture Proven Correct:**
- DevServer = Smart Orchestrator ✅
- PipelineExecutor = Dumb Engine ✅
- Non-Redundant Safety Rules ✅
- Scalable to Complex Flows ✅
- LivePipelineRecorder = Single Source of Truth ✅

**See:**
- `docs/DEVELOPMENT_DECISIONS.md` for design rationale
- `docs/DEVELOPMENT_LOG.md` (Sessions 9, 11, 37, 39, 65) for implementation details
- `schema_pipeline_routes.py` for orchestration code
- `pipeline_executor.py` for execution engine

---

## 2. Model Selection Architecture (Session 65 Refactoring)

**⭐ AUTHORITATIVE SECTION - Centralized model configuration**

**Version:** 1.0 (2025-11-23 - Session 65: execution_mode removal)

### 2.1 Executive Summary

**DEPRECATED Architecture (Pre-Session 65):**
- execution_mode parameter ('eco', 'fast', 'local', 'remote') passed in API calls
- Model selection logic scattered across backend/frontend
- Hardcoded values in multiple locations
- Code duplication and inconsistency

**NEW Architecture (Session 65+):**
- **execution_mode parameter COMPLETELY REMOVED**
- All models configured CENTRALLY in `devserver/config.py`
- NO hardcoded model names in Vue components or API routes
- Single source of truth for model selection

### 2.2 Centralized Model Configuration

**Location:** `/home/joerissen/ai/ai4artsed_webserver/devserver/config.py`

**Model Constants:**
```python
# Stage-specific model assignments
STAGE1_TEXT_MODEL = "llama-guard-3-8b"           # Safety check (local only)
STAGE2_INTERCEPTION_MODEL = "mistral-nemo"       # Pedagogical transformation
STAGE3_MODEL = "llama-guard-3-8b"                # Pre-output safety
# ... etc
```

**Why This Pattern:**
- ✅ Change models in ONE location (config.py)
- ✅ NO hardcoded values in application code
- ✅ Consistent model usage across all flows
- ✅ Easy to switch between local/cloud models
- ✅ Follows "NO WORKAROUNDS" principle

### 2.3 Migration Summary

**Removed from API Calls:**
- `/pipeline/stage2` endpoint: No longer accepts execution_mode
- Frontend (text_transformation.vue): Removed execution_mode from 3 API calls
- Backend routes: Model selection via config.py constants ONLY

**Chunk Configuration:**
- OLD: `"model": "mistral-nemo"` (hardcoded)
- NEW: `"model": "STAGE2_INTERCEPTION_MODEL"` (references config.py)

**Example: manipulate.json**
```json
{
  "chunk_name": "manipulate",
  "model": "STAGE2_INTERCEPTION_MODEL",
  "meta": {
    "task_type": "standard"
  }
}
```

### 2.4 Future Model Switching

**To change models system-wide:**
1. Edit `devserver/config.py`
2. Change constant value (e.g., `STAGE2_INTERCEPTION_MODEL = "claude-3.5-haiku"`)
3. NO code changes required in routes, Vue components, or chunks
4. Restart devserver

**To switch between local/cloud:**
- Update config.py constants to point to cloud models
- Ensure API keys configured in environment
- NO architectural changes required

### 2.5 Architectural Principles

This refactoring follows the project's core principles:
- ❌ **NO prefix hacks** - Model names not prefixed with "00-" for load order
- ❌ **NO temporary fixes** - execution_mode removed, not "improved"
- ✅ **Fix root problems** - Centralized configuration eliminates duplication
- ✅ **Clean, maintainable code** - Single source of truth in config.py

**See:** `/home/joerissen/.claude/CLAUDE.md` - Project instructions enforcing this pattern

---

**Document Version:** 2.2
**Last Updated:** 2025-11-23 (Session 65)
**Status:** v2.1.0-alpha - 2-Phase Stage 2 Execution + Centralized Model Selection
**Authors:** Joerissen + Claude collaborative design
