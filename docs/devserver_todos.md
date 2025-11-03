# DevServer Implementation TODOs
**Last Updated:** 2025-11-03 Session 17 (Pipeline Rename Complete + Research Data Export Understanding Documented)
**Context:** Current priorities and active TODOs

---

## 🔥 IMMEDIATE PRIORITIES (Session 17+)

### 1. Fix Non-Functioning Research Data Export
**Status:** ARCHITECTURE DOCUMENTED (Session 17) - Ready for Implementation
**Priority:** HIGH (user needs this feature)
**Context:** User reported this is not working

**Understanding Documented:** ✅ See `docs/EXECUTION_HISTORY_UNDERSTANDING_V3.md`

**What Must Be Tracked:**
- **Complete pedagogical journey** from input to output across ALL 4 stages
- **Stage 1**: User input, translation, §86a safety check
- **Stage 2**: Interception iterations (e.g., Stille Post = 8 translations) ← CRITICAL: Can be recursive!
- **Stage 3**: Pre-output safety checks (per output config)
- **Stage 4**: Media generation outputs (per output config)
- **Chronological order** with sequence numbers, timestamps, stage context
- **Two iteration types**: `stage_iteration` (Stage 2 recursive) and `loop_iteration` (Stage 3-4 multi-output)

**Export Formats:** XML, PDF, DOCX (legacy compatibility), JSON (research data)

**TODO:**
- [x] Identify what "research data export" means → **DONE:** V3 understanding document
- [ ] Implement Phase 1: Core data structures (ExecutionItem, ExecutionRecord)
- [ ] Implement Phase 2: Stateful tracker (observer pattern, async events)
- [ ] Implement Phase 3: Integration with pipeline execution
- [ ] Implement Phase 4: Export API (XML, PDF, DOCX, JSON)
- [ ] Test export works correctly
- [ ] Document what was implemented

### 2. Interface Design

**Goal 2: Design Educational Interface**

**Context from User:**
> "Now that the dev system works basically, our priority should be to develop the interface/frontend according to educational purposes. The schema-pipeline-system has been inspired by the idea that ENDUSER may edit or create new configs."

**Key Principles for UI Design:**

1. **Use Stage 2 pipelines as visual guides**
   - `text_transformation.json` shows the flow: input → manipulate → output
   - Pipeline metadata documents what happens at each step

2. **Make the 3-part structure visible and editable**
   - Show TASK_INSTRUCTION (from instruction_type)
   - Show CONTEXT (from config.context)
   - Show PROMPT (user input)
   - Allow editing of configs

3. **Educational transparency**
   - Students should see HOW their prompt is transformed
   - Students should be able to edit configs to create new styles
   - Students should understand the prompt interception concept

4. **Reference files for UI design**
   - `devserver/schemas/pipelines/*.json` - Flow structure
   - `devserver/schemas/configs/interception/*.json` - Config examples
   - `docs/ARCHITECTURE.md` Section 6 - instruction_selector.py docs

### 3. GPT-OSS Stage 3 Implementation (Deferred)

**From Session 14:** Replace llama-guard3 with GPT-OSS in Stage 3
**Status:** Deferred - Focus shifted to interface design
**See:** `docs/devserver_todos.md` for details

---

## 📝 Session 16 Completion Notes

**What Was Fixed:**
- ✅ Restored `single_text_media_generation.json` pipeline (accidentally deprecated in Session 15)
- ✅ Fixed Stage 4 error: "Config 'sd35_large' not found"
- ✅ Tested full 4-stage pipeline: Working correctly
- ✅ Committed fix: commit `6f7d30b`
- ✅ Updated SESSION_HANDOVER.md with Session 16→17 context
- ✅ Created PIPELINE_RENAME_PLAN.md (completed in Session 17)

**Key Learnings:**
- Pipeline naming is confusing: "single_prompt_generation" sounds like "generate a prompt" not "generate media FROM a prompt"
- The pipeline was critical for Stage 4 because it provides DIRECT media generation (no text transformation step)
- Output configs (sd35_large, gpt5_image) need this pipeline
- Never deprecate pipeline files without checking all config references first!

**Git Status:**
- Branch: `feature/schema-architecture-v2`
- Commit: `6f7d30b` - "fix: Restore single_prompt_generation pipeline"
- Pushed to remote: ✅

---

## 📁 Archived TODOs

**Archive Policy:** Completed tasks from old sessions archived for reference

**Archives:**
- **Sessions 1-14 (Full History):** `docs/archive/devserver_todos_sessions_1-14.md` (1406 lines)
  - Sessions 1-8: Various architecture work
  - Session 9: 4-Stage Architecture Refactoring
  - Session 10: Config Folder Restructuring
  - Session 11: Recursive Pipeline + Multi-Output Support
  - Session 12: Project Structure Cleanup + Export Sync
  - Session 13: GPT-OSS Model Research
  - Session 14: GPT-OSS Unified Stage 1 Activation

**See also:** `docs/DEVELOPMENT_LOG.md` for chronological session tracking with costs

---

## 🎯 PRIORITY 1 (Next Session): GPT-OSS for Stage 3 + Memory Efficiency

**Status:** NEW TODO (from Session 14)
**Context:** Keep GPT-OSS:20b in Ollama memory throughout Stages 1-3 for efficiency
**Priority:** HIGH (performance optimization + consistency)

**Current State:**
- Stage 1: Uses GPT-OSS:20b (Translation + §86a Safety) ✅ COMPLETED Session 14
- Stage 2: User-selected config (e.g., Dada, Bauhaus) ✅ WORKS
- Stage 3: Uses llama-guard3:1b (age-appropriate content) ❌ TODO: Replace with GPT-OSS
- Stage 4: Output generation (ComfyUI/API) ✅ WORKS

**Problem:**
Model switching between Stage 1 (GPT-OSS) and Stage 3 (llama-guard3) causes:
- Performance overhead (~2-3s to load/unload models)
- Inconsistent safety approach (two different models)
- Increased VRAM usage (16GB GPT-OSS + 8GB llama-guard3 at different times)

**Proposed Solution:**
```
Stages 1-3 (local/eco mode):
  ├─ Stage 1: GPT-OSS:20b (Translation + §86a Safety) ✅ Done
  ├─ Stage 2: User-selected config (e.g., Dada, Bauhaus)
  └─ Stage 3: GPT-OSS:20b (Pre-Output Safety) ← TODO

Stage 4: Unload GPT-OSS before ComfyUI (if media generation)
  └─ API-based outputs (GPT-5 Image): Keep GPT-OSS loaded
```

**Benefits:**
- ✅ Single model for all safety checks (consistency)
- ✅ Keep GPT-OSS in Ollama memory (`keep_alive: "10m"`)
- ✅ No model switching overhead between stages (~2-3s saved per request)
- ✅ Unified safety approach (§86a + age-appropriate in one model)
- ✅ Better VRAM usage (single 16GB model vs switching)

**Implementation Tasks:**

### 1. Create GPT-OSS Stage 3 Configs
- `devserver/schemas/configs/pre_output/gpt_oss_preoutput_kids.json`
- `devserver/schemas/configs/pre_output/gpt_oss_preoutput_youth.json`
- Similar structure to current llama-guard3 configs
- Add §86a context + age-appropriate content rules
- Use JSON response format (same as current Stage 3)

### 2. Update `stage_orchestrator.py`
- Modify `execute_stage3_safety()` to use GPT-OSS configs instead of llama-guard3
- Keep hybrid approach (fast string-match → LLM verification if terms found)
- Parse GPT-OSS JSON response: `{safe, positive_prompt, negative_prompt, abort_reason}`

### 3. Add keep_alive Management
- Stage 1-3: Set `keep_alive: "10m"` for GPT-OSS (stays in VRAM)
- Before Stage 4 ComfyUI: Unload GPT-OSS explicitly if local media generation
- API-based Stage 4: Keep GPT-OSS loaded (no ComfyUI conflict)

### 4. Testing
- Verify Stage 3 safety checks still work correctly
- Test hybrid fast-path (95% of requests should be instant)
- Measure performance gain (expect 2-3s improvement)
- Confirm VRAM usage stays within limits (16GB total)

**Timeline:** Next session (Priority 1)
**Estimated Time:** 2-3 hours

---

## 🎯 PRIORITY 2 (Future): Internationalization - Primary Language Selector

**Status:** NEW TODO (from Session 14)
**Context:** German language is currently hardcoded in educational error messages
**Priority:** MEDIUM (works for German deployment, blocks international use)

**Current Issue:**
- Educational blocking messages hardcoded in German (stage_orchestrator.py:330-336)
- §86a StGB error template only in German
- System assumes German as primary language

**Proposed Solution:**

### 1. Add to `config.py`
```python
# Primary language for educational content and error messages
PRIMARY_LANGUAGE = "de"  # ISO 639-1 code: de, en, fr, es, etc.

# Supported languages for UI and error messages
SUPPORTED_LANGUAGES = ["de", "en"]
```

### 2. Create Language Templates Directory
```
devserver/schemas/language_templates/
├── de.json  # German templates (default)
├── en.json  # English templates
└── ...
```

### 3. Template Structure
```json
{
  "safety_blocked": {
    "heading": "Dein Prompt wurde blockiert",
    "why_rule": "WARUM DIESE REGEL?",
    "protection": "Wir schützen dich und andere vor gefährlichen Inhalten."
  }
}
```

### 4. Update Error Messages
- `stage_orchestrator.py`: Replace hardcoded strings with template system
- Load templates based on PRIMARY_LANGUAGE setting
- Fall back to English if language not supported

**Benefits:**
- Enables international deployment (UK, US, France, etc.)
- Maintains German compliance for German deployments
- Single config variable controls all language settings
- Easy to add new languages

**Timeline:** Future enhancement (not blocking current deployment)
**Estimated Time:** 3-4 hours

---

## ✅ RECENTLY COMPLETED

### Session 17 (2025-11-03): Pipeline Rename to Input-Type Convention
**Status:** ✅ COMPLETE
**Commit:** `bff5da2` - "refactor: Rename pipelines to input-type naming convention"

**What Was Done:**
- Renamed `single_prompt_generation` → `single_text_media_generation`
- Updated 2 output configs: `sd35_large.json`, `gpt5_image.json`
- Updated 7 documentation files
- Deleted deprecated file: `single_prompt_generation.json.deprecated`
- Split ARCHITECTURE.md → ARCHITECTURE PART I.md + PART II.md

**New Pattern:** `[INPUT_TYPE(S)]_media_generation`
- Clear separation: "text" = input type, "media" = output type
- Scalable: Easy to add `image_text_media_generation`, `video_text_media_generation`, etc.
- Self-documenting: Name explicitly describes data flow

**Testing:**
- ✅ Config loader finds pipeline: single_text_media_generation
- ✅ sd35_large config references correct pipeline
- ✅ gpt5_image config references correct pipeline
- ✅ 7 pipelines loaded, 45 configs loaded

**Files Changed:** 13 files (+429 -90 lines)

### Session 14 (2025-11-02): GPT-OSS Unified Stage 1 Activation
**Status:** ✅ COMPLETE & TESTED
**Commit:** `839dc73`

**What Was Done:**
- Created unified GPT-OSS config with full §86a StGB legal text
- Added `execute_stage1_gpt_oss_unified()` in stage_orchestrator.py
- Updated schema_pipeline_routes.py to use unified function
- Tested successfully: ISIS blocking, Nazi code 88, legitimate prompts

**ISIS Failure Case from Session 13:** ✅ FIXED

**See:** `docs/DEVELOPMENT_LOG.md` Session 14 for full details

### Session 12 (2025-11-02): Project Structure Cleanup
**Status:** ✅ COMPLETE
**Commit:** `fe3b3c4`

**What Was Done:**
- Archived LoRA experiment + legacy docs
- Moved docs/ and public_dev/ to project root
- Robust start_devserver.sh
- Synced 109 export files from legacy

### Sessions 9-11 (2025-11-01): 4-Stage Architecture
**Status:** ✅ COMPLETE & TESTED

**What Was Implemented:**
- 4-Stage Architecture Refactoring (Stage 1-3 orchestration)
- Recursive Pipeline System ("Stille Post")
- Multi-Output Support (model comparison)

**See:** `docs/archive/devserver_todos_sessions_1-14.md` for full details

---

## 📝 Quick Reference

**Current Architecture Status:**
- ✅ 4-Stage Pipeline System (Stages 1-4)
- ✅ Config-based system (Chunks → Pipelines → Configs)
- ✅ Backend abstraction (Ollama, ComfyUI, OpenRouter)
- ✅ GPT-OSS Stage 1 (Translation + §86a Safety)
- ✅ Stage 3 Hybrid Safety (fast string-match + LLM context)
- ✅ Multi-output support
- ✅ Recursive pipelines

**Next Up:**
1. Replace llama-guard3 with GPT-OSS in Stage 3
2. Implement keep_alive memory management
3. Add language template system

**Documentation:**
- Architecture: `docs/ARCHITECTURE.md`
- Development Log: `docs/DEVELOPMENT_LOG.md` (Sessions 12-14)
- Development Decisions: `docs/DEVELOPMENT_DECISIONS.md`
- Safety Architecture: `docs/safety-architecture-matters.md`

**Archived:**
- Old TODOs: `docs/archive/devserver_todos_sessions_1-14.md`
- Old Dev Log: `docs/archive/DEVELOPMENT_LOG_Sessions_1-11.md`

---

**Created:** 2025-10-26
**Last Major Cleanup:** 2025-11-02 Session 14
**Status:** Clean and concise (down from 1406 lines to ~230 lines)
