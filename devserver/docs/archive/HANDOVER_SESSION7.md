# Session Handover - 2025-11-01

## ⚠️ INSTRUCTIONS FOR NEXT SESSION

**STOP! Before doing ANYTHING:**

1. ✅ Read this HANDOVER.md completely (~15 min)
2. ✅ Read `docs/ARCHITECTURE.md` Section 1 (~20 min) - AUTHORITATIVE 4-stage flow
3. ✅ Read `docs/IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md` (~10 min) - Your roadmap
4. ✅ NEVER start coding without understanding the full context
5. ✅ NEVER use `rm` command without asking user first

**If you don't follow these steps, you WILL break critical features.**

---

## Current Task

**Implement 4-Stage Architecture Refactoring**

Move Stage 1-3 orchestration logic from PipelineExecutor (dumb engine) to DevServer (smart orchestrator).

**Full Plan:** `docs/IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md`

---

## Current Status

### ✅ Completed This Session (2025-11-01)

1. **Documentation Consolidation**
   - ✅ Merged 4_STAGE_ARCHITECTURE.md into ARCHITECTURE.md Section 1
   - ✅ Deleted redundant docs (README.md, 4_STAGE_ARCHITECTURE.md)
   - ✅ Moved historical docs to tmp/ (API_MIGRATION, PRE_INTERCEPTION_DESIGN)
   - ✅ Updated all references in CLAUDE.md, README_FIRST.md
   - ✅ Git committed & pushed: 85bf54d

2. **Architecture Documentation**
   - ✅ Created comprehensive ARCHITECTURE.md v3.0
     - Part I: Orchestration (4-Stage Flow) - AUTHORITATIVE
     - Part II: Components (Implementation Details)
   - ✅ Documented correct vs wrong architecture with diagrams
   - ✅ Explained non-redundant safety rules
   - ✅ Documented current bug with console log evidence

3. **Implementation Plan**
   - ✅ Created IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md
     - Big picture architecture (before/after)
     - 6-phase incremental refactoring strategy
     - Feature flag approach (rollback-able)
     - Detailed step-by-step instructions
     - Testing strategy
     - Timeline: ~10 hours

### ⏳ Ready to Start (Next Session Task)

**Phase 1: Preparation (1 hour)**
- Add `input_requirements` to pipeline JSONs
- Add `output_config: true` flags to output configs
- Test ConfigLoader reads these correctly

**Status:** NOT STARTED - Next session begins here

---

## The Problem (Why This Refactoring Is Needed)

### Console Evidence (2025-11-01)

User ran: "EIne Blume auf der Wiese" with overdrive config (fast mode, kids safety)

**What happened (WRONG):**
```
✅ Stage 1: Translation + Safety (runs once) - GOOD
✅ Stage 2: Overdrive transformation - GOOD
✅ Stage 3: Pre-Output safety - GOOD
❌ AUTO-MEDIA calls execute_pipeline('gpt5_image')
   → Stage 1: Translation runs AGAIN (on already-English text!)
   → Stage 2: GPT5 config processes
   → Stage 3: Safety runs AGAIN
   RESULT: Redundant API calls, wasted time, confusing logs
```

**Log Evidence:**
```
2025-11-01 09:52:25 - Stage 1 for overdrive: Translation + Safety ✓
2025-11-01 09:52:32 - Stage 2 for overdrive: Text transformation ✓
2025-11-01 09:52:32 - Stage 3 for overdrive: Pre-output safety ✓
2025-11-01 09:52:32 - [AUTO-MEDIA] Starting Output-Pipeline: gpt5_image
2025-11-01 09:52:32 - [EXECUTION-MODE] Pipeline for config 'gpt5_image'
2025-11-01 09:52:32 - [4-STAGE] Stage 1: Pre-Interception  ← REDUNDANT!
2025-11-01 09:52:32 - [4-STAGE] Running correction + translation  ← REDUNDANT!
2025-11-01 09:52:46 - Translation complete  ← REDUNDANT!
2025-11-01 09:52:46 - [4-STAGE] Running hybrid safety check  ← REDUNDANT!
```

### Root Cause

**File:** `schemas/engine/pipeline_executor.py`
**Lines:** 308-499
**Problem:** Stage 1-3 logic embedded in execute_pipeline()

**Why this is wrong:**
- execute_pipeline() is called for EVERY config (overdrive, gpt5_image, etc.)
- When AUTO-MEDIA calls execute_pipeline('gpt5_image'), it triggers Stage 1-3 again
- Stage 1-3 should run ONCE per user request, not ONCE per pipeline call

**Architectural Principle (from user):**
> "Pipelines are orchestrators, but devserver is the orchestrator of pipelines."

---

## The Solution (What You Need to Build)

### Target Architecture

```
User Request
    ↓
schema_pipeline_routes.py (SMART ORCHESTRATOR)
    ↓
    [Stage 1: Pre-Interception]
    │   Read: pipeline.input_requirements = {texts: 1}
    │   → execute_pipeline('translation', text)        [DUMB - no stages]
    │   → run_hybrid_safety_check(text, 'stage1')     [DUMB - no stages]
    ↓
    [Stage 2: Interception]
    │   → execute_pipeline('overdrive', prepared_text) [DUMB - no stages]
    │   Returns: {
    │     final_output: "transformed text",
    │     output_requests: [{type: "image", prompt: "..."}]
    │   }
    ↓
    [Stage 3-4: For EACH output request]
    │   FOR request in output_requests:
    │       [Stage 3: Pre-Output Safety]
    │       → run_hybrid_safety_check(request.prompt, 'kids')
    │
    │       [Stage 4: Media Generation]
    │       → execute_pipeline('gpt5_image', request.prompt) [DUMB - no stages]
    │       Returns: prompt_id
    ↓
    Return: {final_output, media_output}
```

**Key Changes:**
1. **DevServer orchestrates** all 4 stages (schema_pipeline_routes.py)
2. **PipelineExecutor is DUMB** (just executes chunks, no Stage 1-3)
3. **Output configs skip stages** (meta.output_config = true flag)
4. **Non-redundant safety** (rules hardcoded in DevServer, not in 37+ configs)

---

## What Needs to Happen Next

### Immediate: Phase 1 - Preparation (1 hour)

**Goal:** Add metadata to pipelines/configs so DevServer can orchestrate

#### Step 1.1: Add input_requirements to pipelines

**Files to modify:**

1. `schemas/pipelines/text_transformation.json`
```json
{
  "name": "text_transformation",
  "input_requirements": {
    "texts": 1
  },
  "chunks": ["manipulate"]
}
```

2. `schemas/pipelines/single_prompt_generation.json`
```json
{
  "name": "single_prompt_generation",
  "input_requirements": {
    "texts": 1
  },
  "chunks": ["output_image"]
}
```

3. `schemas/pipelines/dual_prompt_generation.json`
```json
{
  "name": "dual_prompt_generation",
  "input_requirements": {
    "texts": 2
  },
  "chunks": ["output_music"]
}
```

**Test:**
```python
# Test in Python shell
from schemas.engine.config_loader import ConfigLoader
loader = ConfigLoader('schemas')
pipeline = loader.get_pipeline('text_transformation')
assert pipeline.get('input_requirements') == {'texts': 1}
print("✓ input_requirements added successfully")
```

#### Step 1.2: Add output_config flag to output configs

**Files to modify:**

1. `schemas/configs/gpt5_image.json`
```json
{
  "meta": {
    "output_config": true,
    "skip_pre_stages": true,
    // ... existing meta fields ...
  }
}
```

2. `schemas/configs/sd35_large.json`
```json
{
  "meta": {
    "output_config": true,
    "skip_pre_stages": true,
    // ... existing meta fields ...
  }
}
```

**Test:**
```python
# Test in Python shell
config = loader.get_config('gpt5_image')
assert config.meta.get('output_config') == True
print("✓ output_config flag added successfully")
```

#### Success Criteria for Phase 1

- [ ] All 3 pipeline JSONs have input_requirements
- [ ] ConfigLoader reads input_requirements correctly
- [ ] Both output configs have output_config flag
- [ ] ConfigLoader reads output_config flag correctly
- [ ] No breaking changes (backward compatible)
- [ ] Git commit: "feat: Add metadata for 4-stage orchestration (Phase 1)"

**After Phase 1 completion:**
→ Move to Phase 2 (Extract helper functions)
→ See IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md for Phase 2 details

---

## Critical Context

### What You MUST Understand

1. **PipelineExecutor Should Be DUMB**
   - Current: Has Stage 1-3 logic (lines 308-499) - WRONG
   - Target: Just executes chunks, no pre/post processing - RIGHT

2. **DevServer Should Be SMART**
   - Current: Calls execute_pipeline() blindly - WRONG
   - Target: Orchestrates Stage 1 → 2 → 3 → 4 - RIGHT

3. **Non-Redundant Safety Rules**
   - Pipelines declare: `input_requirements: {texts: 1}`
   - DevServer knows: text → translation + safety
   - NO duplication in 37+ configs

4. **Output Configs Are Special**
   - gpt5_image, sd35_large, etc.
   - Should skip Stage 1-3 (already done by main pipeline)
   - Flag: `meta.output_config = true`

### What NOT to Do

- ❌ Don't delete 400 lines from pipeline_executor.py immediately (big bang = risky)
- ❌ Don't rewrite everything without feature flag (no rollback)
- ❌ Don't skip testing each phase
- ❌ Don't use `rm` command without asking user
- ❌ Don't start coding without reading ARCHITECTURE.md Section 1

### Incremental Strategy (SAFE)

```python
# Add feature flag in schema_pipeline_routes.py
USE_NEW_4_STAGE_ARCHITECTURE = False  # Start with False

if USE_NEW_4_STAGE_ARCHITECTURE:
    result = await execute_4_stage_flow(...)  # New path (build this)
else:
    result = await pipeline_executor.execute_pipeline(...)  # Old path (keep working)
```

**Benefits:**
- Instant rollback (just flip flag)
- Test new path without breaking old
- Remove old code only after new is proven

---

## Files Currently Being Modified

**Not yet modified - Next session will modify:**

### Phase 1 Files:
- `schemas/pipelines/text_transformation.json` - Add input_requirements
- `schemas/pipelines/single_prompt_generation.json` - Add input_requirements
- `schemas/pipelines/dual_prompt_generation.json` - Add input_requirements
- `schemas/configs/gpt5_image.json` - Add output_config flag
- `schemas/configs/sd35_large.json` - Add output_config flag

### Phase 2+ Files (later):
- `schemas/engine/stage_orchestrator.py` - NEW FILE (extract Stage 1/3 helpers)
- `my_app/routes/schema_pipeline_routes.py` - Add execute_4_stage_flow()
- `schemas/engine/pipeline_executor.py` - Add skip_stages parameter, later remove lines 308-499

---

## Key Documents (Read These!)

### Must Read Before Coding

1. **`docs/ARCHITECTURE.md` Section 1** (20 min)
   - Part I: Orchestration - Complete 4-stage flow
   - AUTHORITATIVE reference for correct architecture
   - Examples: Simple, Looping, Multi-Output flows
   - Current bug documented with console logs

2. **`docs/IMPLEMENTATION_PLAN_4_STAGE_REFACTORING.md`** (10 min)
   - Your complete roadmap (6 phases)
   - Step-by-step instructions for each phase
   - Code examples, test cases, success criteria
   - Timeline: ~10 hours total

3. **`docs/DEVELOPMENT_DECISIONS.md`** (5 min)
   - Read 2025-11-01 entries (AM & PM)
   - Understand WHY this refactoring is needed
   - User quotes about architecture

### Reference Documents

- `docs/README_FIRST.md` - Entry point, reading list
- `docs/LEGACY_SERVER_ARCHITECTURE.md` - Historical context
- `docs/devserver_todos.md` - Current task list
- `CLAUDE.md` - Rules and protocols

---

## Testing Instructions

### After Each Phase

**Phase 1 Test:**
```bash
# Start Python shell
cd /home/joerissen/ai/ai4artsed_webserver/devserver
python3

# Test ConfigLoader
from schemas.engine.config_loader import ConfigLoader
loader = ConfigLoader('schemas')

# Test input_requirements
pipeline = loader.get_pipeline('text_transformation')
print(pipeline.get('input_requirements'))  # Should: {'texts': 1}

# Test output_config flag
config = loader.get_config('gpt5_image')
print(config.meta.get('output_config'))  # Should: True
```

### Full Integration Test (After Phase 5)

**Test Case:** overdrive → gpt5_image (fast mode)

**Start server:**
```bash
python3 server.py
```

**Submit request via Frontend:**
- Config: overdrive
- Input: "EIne Blume auf der Wiese"
- Mode: fast
- Safety: kids

**Expected Console Output:**
```
[Stage 1] Translation: 1x
[Stage 1] Safety: 1x
[Stage 2] Overdrive: 1x
[Stage 3] Pre-output safety: 1x
[Stage 4] GPT5 image: 1x
Total: 5 operations (no redundancy)
```

**OLD OUTPUT (before refactoring) had ~10 operations (redundant Stage 1-3 for gpt5_image)**

---

## Session Metrics

### This Session (2025-11-01)

- **Session duration:** ~3 hours
- **Files modified:** 7 (documentation)
- **Lines changed:** +615 -115
- **Cost:** [To be calculated from Claude Code stats]
- **Git commits:** 1 (85bf54d)

### Documentation Updates

- ✅ ARCHITECTURE.md updated (v2.1 → v3.0, consolidated)
- ✅ DEVELOPMENT_DECISIONS.md updated (2 entries: architecture + consolidation)
- ✅ DEVELOPMENT_LOG.md needs update (pending)
- ✅ devserver_todos.md needs update (pending)
- ✅ CLAUDE.md updated (references to ARCHITECTURE.md)
- ✅ README_FIRST.md updated (reading list)

### Git Status

```
Branch: feature/schema-architecture-v2
Last commit: 85bf54d (docs: Consolidate documentation)
Status: Clean, pushed to remote
```

---

## Success Criteria (How You Know You're Done)

### Phase 1 Success

- [ ] 3 pipeline JSONs have input_requirements
- [ ] 2 output configs have output_config flag
- [ ] ConfigLoader tests pass
- [ ] Git committed & pushed

### Full Refactoring Success (All Phases)

- [ ] No redundant API calls (Stage 1-3 run once per request)
- [ ] Console logs clean and linear
- [ ] overdrive → gpt5_image: ~5 operations (was ~10)
- [ ] All integration tests pass
- [ ] Old code removed from pipeline_executor.py (lines 308-499)
- [ ] Feature flag removed
- [ ] Documentation updated (DEVELOPMENT_LOG, DEVELOPMENT_DECISIONS, devserver_todos)

---

## Rollback Plan (If Things Break)

### Instant Rollback (Feature Flag)

```python
# In schema_pipeline_routes.py
USE_NEW_4_STAGE_ARCHITECTURE = False  # Set to False
# Restart server → Old path resumes
```

### Git Rollback (If Committed)

```bash
# Reset to last working commit
git reset --hard 85bf54d

# Force push (if needed)
git push --force origin feature/schema-architecture-v2
```

**Ask user before force pushing!**

---

## Questions to Ask User (If Unclear)

1. **Multi-input support:** How should dual_prompt_generation work with Stage 1?
   - Run Stage 1 for EACH text input separately?
   - Pass both texts as array to Stage 1?

2. **Output request mechanism:**
   - Option A: Auto-media (current) - config declares default_output
   - Option B: Dynamic - pipeline returns output_requests array
   - Option C: Hybrid (recommended)

3. **Feature flag location:**
   - In config.py (global)?
   - In schema_pipeline_routes.py (local)?

4. **Testing approach:**
   - Unit tests first, then integration?
   - Or integration tests with real server?

---

## Summary for Next Session

**YOU ARE HERE:**
- Documentation complete and authoritative
- Implementation plan complete with 6 phases
- Git clean state, all docs pushed
- Ready to start Phase 1 (Preparation)

**YOUR FIRST TASK:**
- Read ARCHITECTURE.md Section 1 (20 min)
- Read IMPLEMENTATION_PLAN (10 min)
- Start Phase 1: Add input_requirements to 3 pipeline JSONs
- Add output_config flags to 2 output configs
- Test with ConfigLoader
- Git commit Phase 1

**ESTIMATED TIME:**
- Phase 1: 1 hour
- Remaining phases: 9 hours
- Total refactoring: ~10 hours

**YOU WILL KNOW YOU'RE SUCCESSFUL WHEN:**
- Console shows: Stage 1 → 2 → 3 → 4 (linear, no redundancy)
- overdrive → gpt5_image: 5 operations (not 10)
- Logs clean, tests pass, documentation updated

---

**Created:** 2025-11-01 ~17:00 CET
**Next Session:** Start with Phase 1 (Preparation)
**Context Window:** ~75k tokens remaining (next session starts fresh)
**Branch:** feature/schema-architecture-v2
**Last Commit:** 85bf54d

**Good luck! You have everything you need. Read the docs first, then code. 🚀**
