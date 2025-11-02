# DevServer Implementation TODOs
**Last Updated:** 2025-11-02 Session 12 (Structure Cleanup + Export Sync)
**Context:** Post-analysis TODOs for completing devserver architecture

---

## 🎯 PRIORITY 1 (Next Session): GPT-OSS-20b Model Integration

**Status:** RESEARCH COMPLETE → READY FOR IMPLEMENTATION
**Context Window:** Postponed from Session 12 (80% usage)
**Prerequisites:** Model must be loaded locally first (`ollama pull openai/gpt-oss-safeguard-20b`)

---

## ✅ COMPLETED (2025-11-02 Session 12): Project Structure Cleanup + Export Sync

### Structure Cleanup
**Status:** COMMITTED (`fe3b3c4`)
**What Was Done:**
- ✅ Archived LoRA experiment (failed): 5 files → `archive/lora_experiment/`
- ✅ Archived legacy docs: 3 files + workflows_legacy/ → `archive/legacy_docs/`
- ✅ Moved docs/ to project root (was: devserver/docs/)
- ✅ Moved public_dev/ to project root (was: devserver/public_dev/)
- ✅ Robust start_devserver.sh (243 lines, bulletproof)
- **Result:** Root directory clean, devserver/ contains only server code

### Export Data Sync
**Status:** COMPLETED ✅
**What Was Done:**
- ✅ Synced 109 export files from legacy (73 MB, dated 31. Okt)
- ✅ Updated sessions.js (271 lines, research data)
- ✅ Verified export_manager.py + export_routes.py functional
- ✅ Backend API: `/api/download-session` exists (creates ZIP)
- ❌ Frontend UI: Not integrated yet (planned for redesign)

**Export Structure:**
```
exports/
├── sessions.js        # 271 sessions (15K, 31. Okt)
├── docx/             # 236K research exports
├── html/             # 125K
├── pdf/              # 234K
└── xml/              # 234K
```

**TODO (During UI Redesign):**
- [ ] Add "Download Session" button to frontend
- [ ] Wire up to `/api/download-session` API endpoint
- [ ] Test ZIP creation with all formats

---

## 🚨 NEW (2025-11-02 Session 11): GPT-OSS-20b Model Integration + Safety Enhancement

### ✅ COMPLETED: Safety Filter Enhancement (§86a StGB Compliance)
**Status:** COMMITTED (`ede724d`)
**Files:** `stage1_safety_filters.json`, `DEVELOPMENT_DECISIONS.md`

**What Was Done:**
- ✅ Added ~20 German §86a StGB terms (Nazi symbols, extremist orgs, codes: 88, HH)
- ✅ Simplified ambiguous terms (removed context qualifiers: "isis" not "isis flag")
- ✅ Hybrid system understood: String filter triggers LLM review, not immediate block
- ✅ Updated documentation with hybrid filtering rationale

### 🔬 RESEARCH COMPLETED: openai/gpt-oss-safeguard-20b Testing
**Status:** READY FOR IMPLEMENTATION
**Test Results:** `/tmp/test_gpt_oss_*.py` (3 test scripts)

**Key Findings:**
1. **Translation:** ⭐⭐⭐⭐⭐ Excellent (auto-corrects children's typos)
2. **Artistic Transformation:** ⭐⭐⭐⭐⭐ Outstanding (Dada, Bauhaus both perfect)
3. **Safety (§86a StGB):** ⭐⭐⭐⭐⭐ WITH explicit German law prompt (US-centric without)
4. **Performance:** MoE architecture (21B total, 3.6B active) → fast as 8B models
5. **VRAM:** 16GB, can stay loaded Stage 1-3 (unload only before ComfyUI Stage 4)

**Critical Discovery:**
- **WITHOUT §86a prompt:** "Hakenkreuz Fahne" → SAFE (neutral mention) ❌
- **WITH §86a prompt:** "Hakenkreuz Fahne" → UNSAFE (§86a violation) ✅
- Model is **highly configurable** via system prompt!

### 📋 TODO: Implement gpt-oss-20b as Unified Stage 1-3 Model

**Architecture Decision:**
```
Stage 1-3: gpt-oss-20b (Translation + Safety + Interception)
  → keep_alive: "10m" (stays in VRAM)
  → Saves 2-3s load time per request

Stage 4 (ComfyUI only): Unload gpt-oss-20b first
  → API-based (GPT-5 Image): Keep loaded
```

**Implementation Tasks:**
- [ ] Update `config.py`: TRANSLATION_MODEL, SAFETY_MODEL, INTERCEPTION_MODEL → "gpt-oss-20b"
- [ ] Add §86a StGB system prompt to `ollama_service.py`
- [ ] Add Arts Education context for typo correction
- [ ] Implement keep_alive management (10m for Stage 1-3, unload before ComfyUI)
- [ ] Add backend detection in Stage 4 (comfyui vs api)
- [ ] Test combined Translation+Safety+Interception flow
- [ ] Benchmark performance vs. current multi-model approach

**System Prompt Template:**
```python
GPT_OSS_STAGE1_SYSTEM = """You assist children/adolescents (ages 8-17) in Arts Education.

TASKS:
1. CORRECT SPELLING for creative image prompts (Haustir→Haustier not Haustür)
2. TRANSLATE German→English (preserve structure)
3. SAFETY CHECK (§86a StGB): Nazi/terrorist/extremist symbols ILLEGAL in Germany

OUTPUT: Translated text OR "BLOCKED: §86a StGB - [reason]"
"""
```

**Expected Performance Gains:**
- Current: 2 models (mistral-nemo 1-2s + llama-guard3 1-2s) = 2-4s Stage 1
- New: 1 model (gpt-oss-20b 2-3s, reused Stage 2-3) = 2-3s total Stage 1-3
- **Savings:** 30-50% faster + better quality + §86a compliant

**Test Scripts Available:**
- `/tmp/test_gpt_oss_safeguard.py` - Full test suite
- `/tmp/test_gpt_oss_german_law.py` - §86a StGB compliance
- `/tmp/test_gpt_oss_context_correction.py` - Arts Education typo correction

---

## ✅ COMPLETED (2025-11-01 Evening): Config Folder Restructuring

**Status:** COMPLETE ✅
**Duration:** ~2h
**Commits:** `de259e6`, `c93a251`, `5e1fd29`

### What Was Done
1. ✅ Created folder structure: `interception/`, `output/`, `user_configs/`
2. ✅ Moved 31 configs to `interception/` (user-facing)
3. ✅ Moved 6 configs to `output/` (system-only)
4. ✅ Implemented user-config naming: `user_configs/doej/test.json` → `u_doej_test`
5. ✅ Auto-inject `meta.owner` field (system or username)
6. ✅ Frontend API: Filter out `meta.stage="output"` configs
7. ✅ Frontend API: Include `meta.owner` in response
8. ✅ Fixed `.gitignore`: `/output/` (root) vs `configs/output/` (tracked)
9. ✅ Created test user-config and verified system
10. ✅ Updated all documentation (DEVELOPMENT_LOG, DEVELOPMENT_DECISIONS, devserver_todos)

### Results
- **37 configs** shown in frontend (output configs filtered)
- **42 configs** loaded by system (all configs available)
- **User-config support** ready for future UI implementation
- **No breaking changes** - system configs work with simple names

### Files Modified
- `schemas/engine/config_loader.py` - User-config naming + owner injection
- `my_app/routes/schema_pipeline_routes.py` - Output filtering + owner in API
- `.gitignore` - Root-level /output/ only
- 37 config files moved to new structure

### Documentation Updated
- ✅ `DEVELOPMENT_LOG.md` - Session 10 entry
- ✅ `DEVELOPMENT_DECISIONS.md` - User-config naming decision
- ✅ `devserver_todos.md` - This file

**See:**
- Full details in `DEVELOPMENT_LOG.md` Session 10
- Design rationale in `DEVELOPMENT_DECISIONS.md` (2025-11-01 Evening)

---

## 🎯 CURRENT WORK (2025-11-01 Evening)

### ✅ COMPLETED: 4-Stage Architecture + Loop Systems (Session 9-11)
**Status:** ✅ **IMPLEMENTATION COMPLETE, TESTED, DOCUMENTED**
**Priority:** CRITICAL (was)
**Duration:** 3 sessions (~5 hours)

**What Was Completed:**

### 1. ✅ 4-Stage Architecture Refactoring (Session 9)
**Problem Solved:**
- Stage 1-3 logic was embedded in `pipeline_executor.py`
- Caused redundant API calls when AUTO-MEDIA executed output configs
- Translation + Safety ran twice (once for main, once for output)

**Solution Implemented:**
- ✅ Moved Stage 1-3 orchestration to DevServer (`schema_pipeline_routes.py`)
- ✅ PipelineExecutor is now DUMB engine (just executes chunks)
- ✅ DevServer is SMART orchestrator (knows 4-stage flow)
- ✅ Non-redundant safety rules (Stage 1 runs once, Stage 3-4 per output)

**Phases Completed:**
- [x] **Phase 1:** Added `input_requirements` to 7 pipelines, `stage` field to 42 configs
- [x] **Phase 2:** Created `stage_orchestrator.py` with Stage 1/3 helper functions
- [x] **Phase 3:** Implemented 4-Stage orchestration in DevServer
- [x] **Phase 4:** SKIPPED (not needed after Phase 3)

**Files Modified:**
- `schema_pipeline_routes.py` (+100 -195 lines) - Smart orchestrator
- `pipeline_executor.py` (-195 lines) - Dumb engine
- `stage_orchestrator.py` (+400 lines) - Helper functions

**Test Results:**
- ✅ Simple config (dada): Stage 1-4 ran once each
- ✅ Logs confirm clean execution (no redundancy)

### 2. ✅ Recursive Pipeline System (Session 11 Part 1, Commit 6f8d064)
**Feature:** Internal loop architecture for "Stille Post" (Chinese Whispers)

**What Was Implemented:**
- ✅ Created `text_transformation_recursive` pipeline
- ✅ Created `random_language_selector.py` helper (15 languages)
- ✅ Updated `stillepost.json` config with loop parameters
- ✅ Loop executes INSIDE Stage 2 pipeline (not recursive calls)

**Config Example:**
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

**Test Results:**
- ✅ Input: "Eine Blume auf der Wiese"
- ✅ 8-iteration translation loop (hi→pl→ko→ar→ko→nl→ar→en)
- ✅ Stage 1 ran ONLY ONCE (not 8x) - **CRITICAL TEST PASSED**
- ✅ Execution time: 210 seconds
- ✅ Validates 4-Stage Architecture is correct

**Pedagogical Goal:**
- Students see prompt degradation over iterations
- Config has full control over loop behavior
- User-editable for different iteration counts

### 3. ✅ Multi-Output Support (Session 11 Part 2, Commit 55bbfca)
**Feature:** Stage 3-4 Loop to generate multiple media outputs from single prompt

**What Was Implemented:**
- ✅ Modified `schema_pipeline_routes.py` to loop over `output_configs[]` array
- ✅ Each output config gets independent Stage 3 safety check + Stage 4 execution
- ✅ Created `image_comparison.json` config (SD3.5 vs GPT-5)
- ✅ Response includes `media_outputs` array for multi-output scenarios
- ✅ Maintained backward compatibility with single `default_output`

**Config Example:**
```json
{
  "media_preferences": {
    "output_configs": ["sd35_large", "gpt5_image"]
  }
}
```

**Test Results:**
- ✅ Input: "Eine Blume auf der Wiese"
- ✅ Stage 1 ran ONCE (not 2x) - no redundant translation
- ✅ Stage 2 ran ONCE (not 2x) - no redundant pipeline
- ✅ Stage 3-4 Loop: Ran 2x (once per output config)
  - Iteration 1: sd35_large → ComfyUI workflow (ComfyUI_06804_.png)
  - Iteration 2: gpt5_image → OpenRouter API (base64 PNG, ~2.1MB)
- ✅ Execution time: ~120 seconds
- ✅ Backward compatibility verified

**Use Cases Enabled:**
- Model comparison (SD3.5 vs GPT-5) - pedagogical goal
- Multi-format output (image + audio) - future
- Multi-resolution output (1024px + 2048px) - future

### Architecture Validation Summary

**4-Stage Architecture is PROVEN CORRECT:**
- ✅ DevServer = Smart Orchestrator (knows when/how to loop)
- ✅ PipelineExecutor = Dumb Engine (no awareness of stages)
- ✅ Non-Redundant Safety Rules (Stage 1 once, Stage 3-4 per output)
- ✅ Scalable to Complex Flows (recursive loops, multi-output, iterative)

**Validation Tests:**
- ✅ Stillepost (8 iterations): Stage 1 ran once (not 8x)
- ✅ Image Comparison (2 outputs): Stage 1 ran once (not 2x)
- ✅ Simple config (dada): Stage 1-4 all ran once
- ✅ Logs confirm clean execution (no redundancy)

**Documentation Complete:**
- ✅ DEVELOPMENT_LOG.md (Session 9, 11 Part 1, 11 Part 2)
- ✅ DEVELOPMENT_DECISIONS.md (4-Stage, Recursive, Multi-Output entries)
- ✅ ARCHITECTURE.md (Section 1.6 updated with all 3 implementations)
- ✅ devserver_todos.md (this file)
- ✅ Git commits: Session 9, 6f8d064, 55bbfca (all pushed)

**Files Created:**
- `stage_orchestrator.py` (400 lines) - Stage helpers
- `random_language_selector.py` (85 lines) - Language helper
- `text_transformation_recursive.json` (37 lines) - Recursive pipeline
- `image_comparison.json` (58 lines) - Multi-output config

**Files Modified:**
- `schema_pipeline_routes.py` (+299 -75 lines total) - Smart orchestrator
- `pipeline_executor.py` (+147 -195 lines) - Dumb engine + recursive support
- `stillepost.json` (updated for recursive pipeline)

**Total Lines Changed:** +800 -270 = +530 net (3 sessions)

---

## 🎯 NEXT PRIORITIES (After Session 11)

### Phase 5: Integration Testing (2-3h) - NEXT
**Status:** NOT STARTED
**Priority:** HIGH

**Tasks:**
- [ ] Create `test_phase5_integration.py` with automated tests
- [ ] Test 10+ configs (text transformation, output, system pipelines)
- [ ] Test different scenarios:
  - Single output (backward compatibility)
  - Multi-output (2+ configs)
  - Recursive pipelines (loops)
  - Safety blocking (Stage 1 + Stage 3)
- [ ] Verify logs show clean execution (no redundant stages)
- [ ] Create `docs/PHASE5_TEST_REPORT.md` with findings
- [ ] Mark any issues discovered

**Documentation:**
- **Phase 5 START HERE:** `docs/HANDOVER.md` - Complete testing guide
- **Architecture Reference:** `docs/ARCHITECTURE.md` Section 1 - 4-Stage flow
- **Test Examples:** See Session 9, 11 logs for successful test patterns

### Phase 6: Final Cleanup (1h) - AFTER PHASE 5
**Status:** NOT STARTED
**Priority:** MEDIUM

**Tasks:**
- [ ] Address any issues found in Phase 5 testing
- [ ] Remove any temporary debug logging
- [ ] Clean up documentation (remove placeholders)
- [ ] Final git commit with Phase 5+6 complete
- [ ] Update DEVELOPMENT_LOG.md with final session stats

**Estimated Time Remaining:** ~3-4 hours (Phase 5+6)

---

## 🎯 PREVIOUS WORK (2025-10-29)

### COMPLETE Frontend Migration: Backend-Abstracted Architecture
**Status:** ⚠️ PARTIALLY COMPLETED - **BLOCKER: Pre-Interception System NOT Implemented**
**Priority:** CRITICAL

**What Was Done:**
1. ✅ **Rebuilt Frontend from scratch** - New architecture, no legacy code
2. ✅ Created `config-browser.js` - Simple card-based config selection
3. ✅ Created `execution-handler.js` - Backend-abstracted execution + media polling
4. ✅ Updated `main.js` - Initialize new architecture
5. ✅ Removed legacy dropdown from `index.html`
6. ✅ Moved ALL legacy files to `.obsolete`:
   - workflow.js.obsolete
   - workflow-classifier.js.obsolete
   - workflow-browser.js.obsolete (incomplete AM migration)
   - workflow-streaming.js.obsolete
   - dual-input-handler.js.obsolete
7. ✅ Replaced gemma2:9b with mistral-nemo (3x faster)
8. ✅ Updated DEVELOPMENT_DECISIONS.md (complete architecture documentation)
9. ✅ Updated ARCHITECTURE.md (added Frontend Architecture section)
10. ✅ Updated devserver_todos.md (this file)
11. ✅ **TESTED:** Dada config → Text transformation → Image generation → Display **WORKS!**
12. ✅ **COMMITTED:** `60f3944` - Complete Frontend migration
13. ✅ **PUSHED** to `feature/schema-architecture-v2`

**New Architecture (100% Backend-Abstracted):**
```
Config Selection:
  Frontend → /pipeline_configs_metadata → Backend

Execution:
  Frontend → /api/schema/pipeline/execute → Backend

Media Polling (NEW!):
  Frontend → /api/media/info/{prompt_id} → Backend checks ComfyUI

Media Display (NEW!):
  Frontend → /api/media/image/{prompt_id} → Backend fetches from ComfyUI
```

**Benefits:**
- ✅ Frontend NEVER accesses ComfyUI directly
- ✅ Backend can replace ComfyUI with any generator
- ✅ Media-type from Config metadata (image/audio/video)
- ✅ Clean separation of concerns
- ✅ Stateless Frontend

**Testing Results:**
- ✅ Config browser loads 37 configs
- ✅ Config selection works
- ✅ Text transformation successful (mistral-nemo fast)
- ✅ Image generation successful (SD3.5 Large)
- ✅ Media polling via Backend API works
- ✅ Image display via Backend API works

**Pre-Interception System Status (2025-10-29 - Verified):**
The **4-Stage Pipeline System** designed in Session 5 is now **IMPLEMENTED AND TESTED**:
- ✅ **Stage 1: Pre-Interception** - Correction + Translation + Llama-Guard **WORKS! (Tested & Verified)**
- ✅ **Stage 2: Interception** - User-selected config (dada.json, etc.) **WORKS! (Tested & Verified)**
- ✅ **Stage 3: Pre-Output (Hybrid)** - Fast string-match + LLM context verification **WORKS! (Implemented & Tested)**
- ✅ **Stage 4: Output** - Media generation with Auto-Media **WORKS! (Integrated)**

**Performance Improvement:**
- Old: gemma2:9b → ~30s+ per text transformation
- New: mistral-nemo → ~10s total (Translation 4s + Safety 1.5s + Dada 4s)
- **3x faster!** ⚡

**What Works Now (Verified 2025-10-29):**
- ✅ German text → Auto-translation → Safety check → Text transformation
- ✅ English text → Safety check → Text transformation (no unnecessary translation)
- ✅ **Unsafe content gets blocked with German error messages (RE-TESTED, CONFIRMED)**
- ✅ Safe content passes through successfully
- ✅ Llama-Guard correctly detects unsafe content (S8 for "How to build a bomb")
- ✅ Parser correctly extracts S-codes from both formats
- ✅ llama-guard3:8b for safety, mistral-nemo for everything else

**Next Steps:**
- [x] **PRIORITY 1**: Implement Stage 3 (Pre-Output safety before image generation) **COMPLETED 2025-10-29**
- [ ] Add Frontend UI for safety_level selection (kids/youth/off) with admin-toggle
- [ ] **Llama-Guard Alternative testen**: Probeweise llama-guard durch GPT OSS Safeguard austauschen
- [ ] Test Audio/Music generation
- [ ] Monitor system performance
- [ ] Future: Implement Inpainting when needed
- [ ] Future: Extend hybrid approach to Stage 1 (comprehensive filter list)

---

### Pre-Interception 4-Stage System Implementation
**Status:** ✅ STAGE 1+2 COMPLETED (2025-10-29)
**Priority:** MEDIUM (Stage 3+4 remaining)
**Design Document:** `docs/PRE_INTERCEPTION_DESIGN.md` (moved from tmp/ for visibility)

**What Was Done (Session 2025-10-29):**
1. ✅ **Created Pre-Interception Configs:**
   - ✅ `schemas/configs/pre_interception/correction_translation_de_en.json`
   - ✅ `schemas/configs/pre_interception/safety_llamaguard.json`
   - ✅ `schemas/configs/pre_output/image_safety_refinement.json` (created, not yet active)
   - ✅ `schemas/llama_guard_explanations.json` (German error messages for all 13 S-codes)

2. ✅ **Implemented Logic in PipelineExecutor:**
   - ✅ `system_pipeline: true` flag prevents loops (NOT skip_pre_translation/skip_safety_check)
   - ✅ Translation runs ALWAYS (no language detection needed - Translation config handles it)
   - ✅ Execute pre-interception configs before main pipeline
   - ✅ Parse Llama-Guard output (both formats: "safe" or "unsafe,S8, Violent Crimes")
   - ✅ Build German error messages from `llama_guard_explanations.json`
   - ✅ Helper functions: `parse_llamaguard_output()`, `build_safety_message()`, `parse_preoutput_json()`

3. ✅ **Fixed config_loader.py:**
   - ✅ Recursive glob (`**/*.json`) to scan subdirectories
   - ✅ Relative paths as config names (e.g., `pre_interception/safety_llamaguard`)

4. ✅ **Fixed chunk_builder.py:**
   - ✅ Respects `config.meta.model_override` (e.g., llama-guard3:8b for safety)

5. ✅ **Performance Optimization:**
   - ✅ Changed `manipulate.json` from gemma2:9b → mistral-nemo:latest (3x faster)

6. ✅ **Pre-Output Logic (HYBRID IMPLEMENTATION COMPLETE - 2025-10-29):**
   - ✅ Execute before EACH media generation
   - ✅ JSON output: `{safe, positive_prompt, negative_prompt, abort_reason}`
   - ✅ If unsafe: Return text alternative + explanation (NOT silent fail)
   - ✅ **HYBRID APPROACH:** Fast string-match (0.001s) → LLM context check if terms found (1-2s)
   - ✅ Two filter levels: **Kids** (strict, 40+ terms) and **Youth** (moderate, 15 terms)
   - ✅ safety_level parameter: 'kids' (default), 'youth', or 'off'
   - ✅ Performance: 95% of safe prompts → instant (fast-path), 5% → LLM verification
   - ✅ Prevents false positives: "CD player", "dark chocolate" pass LLM check
   - ✅ Uses llama-guard3:1b for Stage 3 (vs llama-guard3:8b for Stage 1)

**Important Design Decisions (from Session 5 Q&A):**
- Correction + Translation: **Consolidated in 1 LLM call** (performance)
- Llama-Guard: **Separate pipeline** (after translation)
- Llama-Guard: **Obligatory** (after translation)
- Pre-Output: **Media-type-specific** (image_safety_refinement for Alpha, audio/video later)
- Safety failure: **Text alternative + explanation** (NOT abort, NOT silent)
- Performance target: **<60s acceptable**, <30s ideal

**Where Logic Belongs:**
- ❌ NOT in `schema_pipeline_routes.py` (server routes)
- ✅ In `schemas/engine/pipeline_executor.py` (pipeline orchestration)

**User Quote (Session 5):**
> "Es wäre doch konsistenter und transparenter, wenn pre-interception-Maßnahmen durch pre-interception-pipelinconfigs durchgeführt werden und nicht im Servercode verborgen sind."

---

### API Migration: workflow_routes → schema_pipeline_routes
**Status:** ✅ COMPLETED (2025-10-28)
**Priority:** HIGH (was CRITICAL)

**What Was Done:**
1. ✅ Implemented Auto-Media in schema_pipeline_routes.py
2. ✅ Fixed prompt_id extraction (final_output vs metadata)
3. ✅ Migrated frontend to `/api/schema/pipeline/execute`
4. ✅ Tested Auto-Media with dada config (eco mode) - **WORKS!**
5. ✅ Marked workflow_routes.py as DEPRECATED → `.obsolete`
6. ✅ All Interception-Configs run locally - **HUGE MILESTONE!**
7. ✅ Created API_MIGRATION.md documentation

**Result:** Clean API with proper terminology, all functionality working

**See:** [API_MIGRATION.md](./API_MIGRATION.md) for migration details

---

## 🎯 PREVIOUS WORK (2025-10-27)

### GPT-5 Image OpenRouter Integration
**Status:** ✅ COMPLETED (Code), ⚠️ NEEDS TESTING
**Priority:** HIGH

**What Was Done:**
1. ✅ Created `output_image_gpt5.json` - API Output-Chunk for GPT-5 Image via OpenRouter
2. ✅ Created `gpt5_image.json` - Output Config for cloud image generation (fast mode)
3. ✅ Created `passthrough.json` - Interception Config with NULL-manipulation for direct image generation
4. ✅ Added API Output-Chunk processing to `backend_router.py`
   - `_process_api_output_chunk()` method
   - `_extract_image_from_chat_completion()` method
   - `_load_api_key()` method from `.key` files
5. ✅ Fixed `execution_mode` undefined bug in `workflow_routes.py` (variable was named `mode`)
6. ✅ Created `output_config_selector.py` and `output_config_defaults.json` for auto-media generation
7. ✅ Test scripts: `test_gpt5_image.py`, `test_gpt5_simple.py`
8. ✅ Documentation: `OPENROUTER_SETUP.md`, `docs/tmp/GPT5_IMAGE_OPENROUTER_PLAN.md`

**What Needs Testing:**
- [ ] Test `passthrough.json` in Frontend (direct image generation without prompt modification)
- [ ] Test auto-media generation with eco mode (SD3.5 local)
- [ ] Test auto-media generation with fast mode (GPT-5 cloud)
- [ ] Verify Frontend doesn't show Output Configs (`sd35_large`, `gpt5_image`) - only user-facing configs

**Known Issues:**
1. **Frontend shows Output Configs** - `sd35_large.json` and `gpt5_image.json` appear as user-selectable options, but should only be used by auto-media system
2. **No Config Type Distinction** - System can't distinguish between Interception Configs (user-facing) and Output Configs (system-only)

**Proposed Solution (NOT IMPLEMENTED):**
- Add `meta.system_config: true` flag to Output Configs
- Filter out system configs in Frontend config list endpoint
- OR: Separate directory structure (deferred due to complexity)

**Next Steps:**
1. Test the system with real usage
2. Address Frontend config visibility issue
3. Verify auto-media generation works end-to-end

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

## PEDAGOGICAL REQUIREMENTS (FROM LEGACY ANALYSIS)

### Critical Workshop Findings
**Source:** Legacy server workshops, empirical data

**Main Problem Identified:**
- Kunstpädagog*innen nutzen **Weg des geringsten Widerstands**
- SD 3.5 large ohne Prompt Interception → **solutionistische Nutzung**
- Keine Meta-Prompt-Gestaltung → Material-Metapher nicht verstanden

**DevServer Must Address:**
1. Aktive Aneignung als Standard (not optional)
2. Solutionistische Nutzung strukturell verhindern
3. Meta-Prompts als "vorbereitetes Material" explizit machen

### 4.1 Edit-Interface für Meta-Prompts (CRITICAL)
**Priority:** **CRITICAL** (Hauptgrund für DevServer)
**For:** Lernende

**Required Features:**
1. **Meta-Prompt-Editor**: Visuelles Interface zum Schreiben eigener Meta-Prompts
   - Template-Vorschläge (z.B. "Du bist ein Künstler der...")
   - Live-Preview: Wie wird mein Prompt transformiert?

2. **Urteilsformulierung**: Explizite Aufforderung
   - "Was möchtest du erreichen?"
   - "Welche Haltung soll die KI einnehmen?"
   - Nicht technisch, sondern konzeptuell

3. **LLM-Dialog-Unterstützung**: Geführte Meta-Prompt-Erstellung
   - Dialog-Modus: "Ich helfe dir, deinen Meta-Prompt zu formulieren"
   - Fragen: "Soll das Ergebnis realistisch oder abstrakt sein?"
   - Schrittweise Verfeinerung

4. **Keine Umgehung**: SD 3.5 ohne Interception nicht mehr möglich
   - Minimaler Default-Meta-Prompt wenn User nichts eingibt
   - Aber: Bewusste Entscheidung erforderlich (Button "Mit Standard fortfahren")

### 4.2 Edit-Interface für Kunstpädagog*innen (CRITICAL)
**Priority:** **CRITICAL**

**Required Features:**
1. **Material-Metapher**: UI macht explizit, dass Meta-Prompts das "vorbereitete Material" sind
   - Analog zu Papier/Farben im klassischen Kunstunterricht
   - "Was ist das Material, mit dem die Lernenden arbeiten?"

2. **Pädagogische Intentionen formulieren**:
   - "Welche künstlerische/kritische Haltung soll gefördert werden?"
   - "Welche Reflexion soll angeregt werden?"

3. **Template-Bibliothek**: Vorgefertigte Meta-Prompts mit pädagogischer Dokumentation
   - Dada-Haltung, Surrealismus, kritische Medienreflexion, etc.
   - Jedes Template mit Erklärung: "Warum ist das pädagogisch sinnvoll?"

4. **Kursmanagement**: Pädagog*innen können Sets von Meta-Prompts für Workshops vorbereiten

---

## SAFETY AND PERFORMANCE (FROM LEGACY ANALYSIS)

### 2.1 Timeout-Problem lösen (CRITICAL)
**Priority:** **CRITICAL**
**Problem:** Hauptproblem in realen Workshop-Einsätzen (DSL-Anbindung zu langsam)

**DevServer-Maßnahmen:**
1. **Parallelisierung**: Safety-Checks + Model-Loading + Preprocessing parallel
2. **Caching**:
   - Häufig genutzte Models im VRAM halten
   - Prompt-Translation cachen (PROMPT_CACHE nutzen)
3. **Progressive Loading**:
   - Zwischenstände anzeigen ("Translation läuft...", "Sicherheitscheck...")
   - User-Erwartung managen
4. **Timeout-Konfiguration**:
   - Längere Timeouts für komplexe Workflows
   - Automatische Retry-Logik

### 2.2 Safety-System Optimierungen (HIGH)
**Priority:** HIGH

**Problem Legacy:**
- Drei separate LLM-Calls (Translation, Guard Model, Safety Node)
- Sequentielle Ausführung → lange Wartezeiten
- Negative-Prompt-Injection reduziert Bildqualität

**DevServer-Lösung:**
- **Konsolidierung**: Weniger LLM-Calls durch intelligentere Orchestrierung
- **Parallelisierung**: Safety-Checks parallel zu anderen Vorbereitungen
- **Image-Analyse am Ende**: Post-Generation-Check statt nur Pre-Prompt-Check
  - Kombinierter Text+Bild-Safety-Check
  - Falls Bild problematisch: Regenerierung mit angepasstem Prompt

### 2.3 Ausführliche Safety-Begründungen (MEDIUM-HIGH)
**Priority:** MEDIUM-HIGH
**Pedagogical Core:** Transparenz statt Black Box

**Required:**
- LLM artikuliert **warum** ein Prompt problematisch ist
- **Ebenen**: Rechtlich, ethisch, ästhetisch, entwicklungspsychologisch
- **Formulierung**: Altersgerecht (Kids vs. Youth vs. Expert Mode)
- **Lerneffekt**: Reflexion über AI-Safety als Lerngegenstand

### 2.4 Verbesserte False-Positive-Behandlung (MEDIUM)
**Problem:** Wort "player" löst Kids-Filter aus (False Positive)

**Solution:**
- Fine-Tuning auf deutschsprachige Prompts
- Whitelisting harmloser Begriffe
- Erklär-Funktion: "Dieses Wort wurde gefiltert weil..."

---

## DATENSCHUTZ (DS-GVO) (CRITICAL)

### 3.1 Bild-Upload-Policy bei externen Backends
**Priority:** **CRITICAL**
**Legal:** DS-GVO Compliance, Schutz von Kindern

**Problem:** Flexible Backends + Input-Bild-Verarbeitung → Risiko, Selbstportraits von Kindern an externe APIs zu senden

**Solution (Recommended):**
- DS-GVO-kompatible Backends hartcodiert kennzeichnen
- Metadaten-Feld: `gdpr_compliant: true/false`
- System erlaubt Bild-Upload nur bei `true` oder lokalem Backend
- Bei `false`: Fehlermeldung + Hinweis auf Datenschutz

**Alternative:** Bild-Verarbeitung nur lokal (Ollama Vision Models)

---

## STATEFUL SERVER (HIGH PRIORITY)

### 6.1 Session-Management
**Priority:** HIGH
**Context:** Legacy attempt failed (Gemini 2.5 Pro, cost 30-40$), but now feasible with better LLMs

**Requirements:**
- User-Sessions persistieren (Redis/Memcached)
- Pipeline-Zwischenstände speichern
- Unterbrechung und Fortsetzung ermöglichen
- Mehrere parallele Sessions pro User

**Use Cases:**
- "Stille Post" unterbrechen nach Schritt 3, Zwischenstand ansehen, fortfahren
- Iterative Bildbearbeitung (OmniGen2-Style)

---

## BACKEND EXTENSIONS (MEDIUM)

### 1.1 Multi-Backend-Support erweitern
**Priority:** MEDIUM

**Add Support For:**
- **LMStudio**: Lokale Inference mit GUI
- **Deutsche DS-GVO-konforme Anbieter**: z.B. Aleph Alpha, HuggingFace Inference (EU-hosted)
- **Backend-Kennzeichnung**: Metadaten ob DS-GVO-konform (wichtig für Bild-Upload-Policy)

**Rationale:** Bildungsgerechtigkeit + Datenschutz

---

## FUTURE CONSIDERATIONS

### Phase 3: Advanced Features (Not urgent)
- [ ] Multi-step output pipelines (text → image → video)
- [ ] Batch processing (multiple prompts → multiple images)
- [ ] Streaming output (real-time generation progress)
- [ ] image_plus_text_generation pipeline implementation
- [ ] ControlNet support
- [ ] Inpainting support
- [ ] Workflow-Orchestrierung via LLM (LLM chooses which chunks/pipelines)

### Phase 4: Additional Backends
- [ ] Replicate API integration
- [ ] Stability AI API
- [ ] Midjourney (if API becomes available)
- [ ] LMStudio
- [ ] Aleph Alpha
- [ ] HuggingFace Inference (EU-hosted)

### Phase 5: Advanced Model Selection
- [ ] Cost optimization (choose cheapest model for task)
- [ ] Quality optimization (choose best model regardless of cost)
- [ ] Latency optimization (choose fastest model)
- [ ] Fallback chains (try model A, if fails try model B)

### Phase 6: UX/UI Improvements
- [ ] Vollständige Mehrsprachigkeit (DE/EN for all UI elements)
- [ ] Progressive loading indicators
- [ ] Better error messages (explain WHY, not just WHAT failed)

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

## PRIORISIERTE ROADMAP

### SHORT-TERM: Current Architecture Completion (DevServer Phase 1)
**Estimated Time:** ~14 hours
**Focus:** Complete technical architecture from !! comments

1. **!! Comment 5: #notranslate# logic** (1 hour) - CRITICAL quick fix
2. **Phase 2A: Rename pipelines** (2 hours) - HIGH priority refactoring
3. **Task-type metadata system** (2 hours) - MEDIUM priority architecture
4. **Phase 2B: Create standard configs** (3 hours) - HIGH priority infrastructure
5. **Rewrite ARCHITECTURE.md** (2 hours) - Documentation
6. **Phase 2C: Backend router enhancement** (4 hours) - MEDIUM priority

### MEDIUM-TERM: Workshop-Critical Features (DevServer Phase 2)
**Focus:** Enabling real workshop usage based on empirical findings

**Phase 1 (Kritisch - MVP für Workshops):**
1. ✅ **Edit-Interface für Meta-Prompts** (Klientel + Pädagog*innen)
   - Hauptgrund für DevServer
   - Aktive Aneignung als Standard
   - Template-Bibliothek mit pädagogischer Dokumentation

2. ✅ **DS-GVO-konforme Bild-Upload-Policy**
   - Legal compliance
   - Backend-Kennzeichnung: `gdpr_compliant: true/false`
   - Schutz von Kindern

3. ✅ **Timeout-Optimierung** (Parallelisierung, Caching)
   - Hauptproblem in realen Workshop-Einsätzen
   - Progressive Loading Indicators
   - Bessere User-Erwartungssteuerung

4. ✅ **Stateful Server** (Session-Management)
   - Unterbrechung und Fortsetzung
   - "Stille Post" workflow support
   - Iterative Bildbearbeitung

**Phase 2 (Hoch - Qualitätsverbesserungen):**
1. Safety-System-Effizienz (Konsolidierung, Image-Analyse)
2. Performance-Optimierung Workflow-Zeiten
3. Ausführliche Safety-Begründungen (pedagogical transparency)

**Phase 3 (Mittel - Erweiterungen):**
1. Multi-Backend-Support (LMStudio, deutsche DS-GVO-Anbieter)
2. False-Positive-Behandlung verbessern
3. Workflow-Orchestrierung via LLM

**Phase 4 (Niedrig - Nice-to-Have):**
1. Vollständige Mehrsprachigkeit (DE/EN for all UI)
2. Weitere Play/Dialog-Mode Features

### LONG-TERM: Advanced Features (DevServer Phase 3+)
- Multi-step output pipelines (text → image → video)
- Batch processing
- ControlNet, Inpainting support
- Additional backends (Replicate, Stability AI, Midjourney)
- Advanced model selection (cost/quality/latency optimization)

---

## IMPLEMENTATION ORDER (IMMEDIATE TASKS)

**Next Session Focus:**

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

**Total Estimated Time (Current Sprint):** ~14 hours

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
