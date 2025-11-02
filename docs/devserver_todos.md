# DevServer Implementation TODOs
**Last Updated:** 2025-11-02 Session 14 (GPT-OSS Unified Stage 1 Activation)
**Context:** Current priorities and active TODOs

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
