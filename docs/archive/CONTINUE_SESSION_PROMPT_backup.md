# Claude Code Session Continuation Prompt

**Date:** 2025-10-26
**Context:** DevServer architecture refactoring - continuing after tmux restart
**Working Directory:** `/home/joerissen/ai/ai4artsed_webserver/devserver`

---

## Session Status

### What Was Completed (Previous Session):

✅ **Chunk Consolidation** (COMPLETED)
- Deleted redundant chunks (translate, prompt_interception, prompt_interception_lyrics/tags)
- Fixed manipulate.json template (removed duplicate placeholders)
- Updated chunk_builder.py (removed TASK/CONTEXT aliases)
- Updated all pipelines to use manipulate chunk
- All tests passing (34 configs, 6 pipelines)

✅ **Documentation Created:**
- `docs/ARCHITECTURE.md` - Complete rewrite (Version 2.0)
- `docs/OUTPUT_PIPELINE_ARCHITECTURE.md` - Output pipeline design (moved to tmp/)
- `docs/devserver_todos.md` - Comprehensive TODO list with pedagogical requirements
- `docs/tmp/` - Analysis files (CHUNK_ANALYSIS.md, PLACEHOLDER_ANALYSIS.md, PIPELINE_ANALYSIS.md)

✅ **File Recovery:**
- Recovered deleted DEVSERVER_TODOS.md from GitHub
- Merged pedagogical requirements into current devserver_todos.md
- Backup created: `docs/tmp/devserver_todos_merged_backup.md`

✅ **File Management Rules Added:**
- NEVER delete files directly with `rm` - always move to docs/tmp/ or .OBSOLETE suffix
- Check if file contains unique information before moving/deleting
- Recent files (<24h old): extra caution, always backup first

---

## Current Task: Continue Implementation

**CRITICAL: Correct Priority Order**

User clarification: Output-Pipelines müssen ZUERST korrekt benannt werden, sonst gibt es Chaos!

---

### 1. Phase 2A: Rename and Restructure Output-Pipelines - **CRITICAL PRIORITY**
**Estimated Time:** 2 hours
**Status:** NOT STARTED

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

4. **Delete unused pipelines:**
   - `schemas/pipelines/simple_interception.json` (0 configs use it)
   - `schemas/pipelines/video_generation.json` (Dummy only)

---

### 2. !! Comment 5: Pre-Translation Logic (#notranslate#) - **HIGH PRIORITY**
**Estimated Time:** 1 hour
**Status:** NOT IMPLEMENTED

**Location:** `my_app/routes/workflow_routes.py` line ~530

**Required Change:**
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

**Note:** Can be done in parallel with Phase 2A (different files)

---

### 3. Task-Type Metadata System - **MEDIUM PRIORITY**
**Estimated Time:** 2 hours
**Status:** PARTIALLY IMPLEMENTED

**What Exists:**
- `model_selector.py` already has 6 task categories (security, vision, translation, standard, advanced, data_extraction)

**What's Missing:**
1. Chunks don't declare their `task_type`
2. Configs don't declare their `task_type`
3. Pipeline executor doesn't pass `task_type` to model_selector

**Implementation:**
1. Add task_type to `schemas/chunks/manipulate.json` meta
2. Modify `schemas/engine/chunk_builder.py` to use task-based model selection
3. Allow task_type in Config.meta (optional override)

---

## Key Architecture Decisions (Reference)

1. ✅ **Input-Type-Based Pipelines** (not media-type or backend-type)
   - Differentiate by what they consume, not what they produce
   - Example: `single_prompt_generation`, `dual_prompt_generation`

2. ✅ **Backend Transparency**
   - Same pipeline works with ComfyUI, OpenRouter, Ollama
   - Backend declared in config.meta.backend

3. ✅ **Three-Layer Architecture**
   - Layer 1: Chunks (primitives like manipulate.json)
   - Layer 2: Pipelines (structure like text_transformation)
   - Layer 3: Configs (content like dada.json, bauhaus.json)

4. ✅ **One Universal Manipulate Chunk**
   - No more translate, prompt_interception, etc.
   - "Prompt interception ist ein kritisches pädagogisches Konzept das auf dieser Ebene nicht auftauchen sollte"

5. ✅ **Task-Based Model Selection**
   - Chunks declare task_type (security, vision, translation, standard, advanced, data_extraction)
   - Execution modes: eco (local, free) vs fast (cloud, paid)

---

## Important Files to Reference

### Documentation:
- `docs/devserver_todos.md` - Complete TODO list with all tasks
- `docs/ARCHITECTURE.md` - Technical architecture documentation (Version 2.0)
- `docs/tmp/OUTPUT_PIPELINE_ARCHITECTURE.md` - Output pipeline design

### Code:
- `schemas/chunks/manipulate.json` - Universal text transformation chunk
- `schemas/engine/chunk_builder.py` - Chunk execution logic
- `schemas/engine/model_selector.py` - Task-based LLM selection (lines 73-130)
- `schemas/engine/backend_router.py` - Backend routing logic
- `my_app/routes/workflow_routes.py` - Main workflow routes (needs #notranslate# fix)

### Tests:
- `test_refactored_system.py` - System tests (34 configs, 6 pipelines)
- All tests currently passing ✅

---

## Recommended Next Steps

**PRIORITY 1 (CRITICAL): Phase 2A - Pipeline Renaming**
**Why first:** User says "Output-Pipelines müssen ZUERST korrekt benannt werden, sonst gibt es Chaos!"

Start with **Phase 2A: Rename Output-Pipelines** (2 hours)
- Rename based on INPUT-type (not output-type)
- `image_generation` → `single_prompt_generation`
- `music_generation` → `dual_prompt_generation`
- `simple_manipulation` → `text_transformation`
- Affects 30+ config files
- Foundation for clean architecture

**PRIORITY 2 (HIGH): #notranslate# logic**
Can be done **in parallel** with Phase 2A (different files)

Start with **!! Comment 5: #notranslate# logic** (1 hour)
- Single file modification (`my_app/routes/workflow_routes.py`)
- High priority
- Easy to test
- Independent from pipeline renaming

**PRIORITY 3 (MEDIUM): Task-Type Metadata**
After pipelines are renamed

Start with **Task-Type Metadata System** (2 hours)
- Enhances model selection
- Builds on clean architecture

---

## Commands to Get Started

```bash
# Verify current status
python3 test_refactored_system.py

# Read the TODO list
cat docs/devserver_todos.md | less

# Read current architecture
cat docs/ARCHITECTURE.md | less

# Check for #notranslate# implementation location
grep -n "should_translate" my_app/routes/workflow_routes.py

# List all pipelines
ls -la schemas/pipelines/

# List all configs
ls -la schemas/configs/
```

---

## Context Notes

- **System is functional**: 34 configs load, all tests pass
- **Git repo**: Not a git repo (yet), but should commit before major refactoring
- **Execution modes**: eco (Ollama local) vs fast (OpenRouter cloud)
- **Pedagogical focus**: DevServer must prevent "solutionistische Nutzung" - active appropriation is mandatory

---

## IMPORTANT: Documentation Workflow

**⚠️ CRITICAL RULE: Keep Documentation Updated**

Whenever you make implementation changes:

### Required Documentation Files (4 Types)

1. **`docs/DEVELOPMENT_LOG.md`** - **Session Tracking & Costs** (NEW!)
   - **When:** At START, DURING, and END of each session
   - **What:** Session duration, costs, model usage, tasks completed, code changes
   - **At Session Start:** Create new session entry with "In Progress" status
   - **During Session:** Update "Tasks Completed" as you finish tasks (real-time)
   - **At Session End:** Fill in cost data from Claude Code stats
   - **Purpose:** Linear chronological log + cost accounting

2. **`docs/devserver_todos.md`** - **Task Management**
   - **When:** Real-time as tasks progress
   - **What:** Mark completed tasks with ✅, add new tasks, update status
   - **Format:** NOT STARTED → IN PROGRESS → COMPLETED
   - **Purpose:** What needs to be done (current priorities)

3. **`docs/DEVELOPMENT_DECISIONS.md`** - **Architectural Decisions**
   - **When:** When making architectural decisions or choosing alternatives
   - **What:** WHY decisions were made (not just WHAT)
   - **Include:** Reasoning, alternatives considered, file paths, line numbers
   - **Purpose:** Document decision rationale for future reference

4. **`docs/ARCHITECTURE.md`** - **System Structure**
   - **When:** When changing system architecture or data flow
   - **What:** How system works, patterns, conventions, data flow diagrams
   - **IMPORTANT:** Create backup before major changes: `docs/tmp/ARCHITECTURE_[YYYYMMDD].md`
   - **Purpose:** Technical reference for system design

### Additional Documentation Rules

5. **For major changes:**
   - Create analysis document in `docs/tmp/` BEFORE implementing
   - Get user confirmation on approach
   - Document findings for future reference

6. **Before context window fills:**
   - User will say: "Schreib jetzt alles in .md Dateien"
   - Immediately stop and document current state
   - Update DEVELOPMENT_LOG.md with session end stats
   - Create continuation prompt like this one

7. **Git commits:**
   - Include session cost in commit message footer
   - Reference all updated documentation files
   - Format: `Session cost: $XX.XX | Duration: Xh XXm | Files: +XXX -XXX`

**Rationale:** Claude Code sessions reset when context fills. Documentation is the only persistent memory across sessions.

**See:** `docs/DEVELOPMENT_LOG.md` section "Logging Workflow Rules" for complete details

---

## ⚠️ MANDATORY: Documentation Review Before Any Task

**CRITICAL RULE FOR ALL NEW TASKS/SESSIONS:**

Before starting **ANY** implementation work, you **MUST** read and understand:

### Required Reading (in this order):

1. **`docs/README.md`** (5 min)
   - Overview of documentation structure
   - Where to find what information

2. **`docs/LEGACY_SERVER_ARCHITECTURE.md`** (20 min)
   - **WHY** the system was built this way
   - Pedagogical concepts (Prompt Interception, Gegenhegemoniale Pädagogik)
   - How Legacy Server worked (ComfyUI Custom Nodes)
   - Critical difference: Legacy vs DevServer

3. **`docs/ARCHITECTURE.md`** (15 min)
   - **HOW** DevServer works now
   - Three-layer system (Chunks → Pipelines → Configs)
   - Backend routing (eco/fast, local/remote)
   - Data flow patterns

4. **`docs/devserver_todos.md`** (5 min)
   - Current priorities
   - What needs to be done next

5. **`docs/DEVELOPMENT_DECISIONS.md`** (10 min)
   - WHY architectural decisions were made
   - Alternatives that were rejected

### Why This Matters:

**Without reading the documentation, you will:**
- ❌ Propose solutions that already exist
- ❌ Break pedagogical concepts (e.g., Prompt Interception)
- ❌ Misunderstand the difference between Legacy (ComfyUI Custom Nodes) and DevServer (Pipeline-based)
- ❌ Ask questions already answered in docs
- ❌ Waste time and money on wrong approaches

**Example from this session:**
- I proposed an implementation strategy **without** reading `LEGACY_SERVER_ARCHITECTURE.md`
- I didn't understand that DevServer replaces ComfyUI Custom Nodes with Pipeline Chunks
- User had to stop me and ask: "HAST DU DIE DOKUMENTE IN /docs NICHT GELESEN??"

### Verification:

Before proceeding with implementation, you should be able to answer:
1. What is "Prompt Interception" and why is it pedagogically important?
2. How did Legacy Server implement Prompt Interception (ComfyUI Custom Node)?
3. How does DevServer implement Prompt Interception (Pipeline Chunk)?
4. What is `ComfyUIWorkflowGenerator` and why does it exist?
5. What is the difference between Pre-Pipeline and Output-Pipeline?

**If you cannot answer these questions, STOP and read the documentation first.**

---

**Ready to continue!**

Please start with one of the recommended next steps. All necessary documentation is in `docs/devserver_todos.md`.

**First action in new session:**
1. ✅ Read **ALL** required documentation (above)
2. ✅ Verify understanding
3. ✅ Then read `docs/devserver_todos.md` for current priorities
