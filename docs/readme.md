# ⛔ MANDATORY SESSION START PROTOCOL ⛔

**EVERY NEW SESSION MUST START WITH THIS CONFIRMATION:**

```
✅ SESSION START CONFIRMED: [current date/time]
✅ REQUIRED READING: ARCHITECTURE PART 01-20, devserver_todos.md, DEVELOPMENT_DECISIONS.md
✅ DOCUMENTATION COMMITMENT: I will update DEVELOPMENT_LOG.md at end of this session
✅ FILE CREATION POLICY: I will NOT create new .md files without explicit user permission
```

**IF YOU DID NOT OUTPUT THE ABOVE, YOU HAVE NOT READ THIS FILE.**

---

# ⚠️ READ THIS FIRST - Mandatory for All New Tasks/Sessions

**Date Created:** 2025-10-26
**Purpose:** Prevent costly mistakes from incomplete understanding
**Applies to:** ALL Claude Code sessions, ALL new LLM tasks
**Last edit: 2025-11-15** (Session 44: Enforcement mechanisms added)

---

## 🚨 CRITICAL RULES - ZERO TOLERANCE

### Rule 1: Documentation Requirements (MANDATORY)

**✅ REQUIRED EVERY SESSION:**
- Update `DEVELOPMENT_LOG.md` with: date, tasks, files changed, duration, cost
- This is NOT optional. Every session MUST be logged.

**❌ FORBIDDEN WITHOUT USER PERMISSION:**
- Creating new .md documentation files (SESSION_XX_HANDOVER.md, ANALYSIS_*.md, etc.)
- Creating specialized analysis documents
- Creating per-feature documentation files

**WHY:** 30-40% of sessions ignored documentation requirements, creating chaos. ALL findings go in DEVELOPMENT_LOG.md unless user explicitly requests otherwise.

### Rule 2: No Code Changes Before Consultation

YOU MUST NOT EDIT ANY CODE BEFORE CONSULTING USER. ESPECIALLY WHEN FRESHLY STARTED, DO NOT DEVELOP SUPPOSEDLY "GOOD IDEAS" YOURSELF: YOU WILL MOST LIKELY BE WRONG AND MESS UP THE SYSTEM.

**You are about to work on the AI4ArtsEd DevServer.**

This is NOT a typical CRUD app or API server. It implements **pedagogical concepts** about AI art education that are critical to preserve.

**If you start coding without reading the documentation below, you WILL:**
- ❌ Break pedagogical concepts (e.g., Prompt Interception)
- ❌ Propose solutions that already exist
- ❌ Misunderstand fundamental architecture differences (Legacy vs DevServer)
- ❌ Waste time and money (this session cost example: asking questions already documented)

---

## 📚 Required Reading

**Read these documents IN ORDER before any implementation work:**

### 1. `docs/ARCHITECTURE PART *.md` FILES **⭐ AUTHORITATIVE**
You must understand the architecture documentation structure (21 PART files) in order to know WHEN to look up information related to your specific task, instead of "inventing things" that already exist. CONSISTENCY IS CRUCIAL!

**What:** Complete 4-stage orchestration flow (ARCHITECTURE PART 01-19)
**Why:** Understand the CORRECT architecture for implementing flow logic
**How:** The documentation is split into 21 PART files. Use them for orientation. Hold the content structure firmly in your memory at all times, so that you will know when to look things up instead of making things up yourself!

**🚨 CRITICAL for any work involving:**
- Pipeline execution
- Stage 1 (translation + safety)
- Stage 2 (interception)
- Stage 3-4 (pre-output + media generation)
- Output configs (gpt5_image, sd35_large)

**Must understand:**
- DevServer = Smart Orchestrator (schema_pipeline_routes.py)
- PipelineExecutor = Dumb Engine (just runs chunks)
- Non-redundant safety rules (hardcoded in DevServer, not pipelines)
- Stage 3-4 loop (runs once per output request, not per pipeline)

**Critical concepts you MUST understand:**
- **Three-Layer System**: Chunks → Pipelines → Configs
- **Input-Type-Based Pipelines** (not output-type!)
- **Backend Routing**: eco vs fast, local vs remote
- **Backend Transparency**: Same pipeline works with ComfyUI, OpenRouter, etc.
- **Engine Modules**: PipelineExecutor, BackendRouter, ConfigLoader, etc.
- **Frontend Architecture**: Backend-abstracted media handling

#### Architecture Documentation Structure:

**22 PART Files** in `docs/`:

**Part I: Orchestration (How It Works)**
1. ARCHITECTURE PART 01 - 4-Stage Orchestration Flow ⭐ **START HERE**

**Part II: Components (What The Parts Are)**
2. ARCHITECTURE PART 02 - Architecture Overview
3. ARCHITECTURE PART 03 - Three-Layer System
4. ARCHITECTURE PART 04 - Pipeline Types
5. ARCHITECTURE PART 05 - Pipeline-Chunk-Backend Routing
6. ARCHITECTURE PART 06 - Data Flow Patterns
7. ARCHITECTURE PART 07 - Engine Modules
8. ARCHITECTURE PART 08 - Backend Routing
9. ARCHITECTURE PART 09 - Model Selection
10. **(No PART 10 - archived)**
11. ARCHITECTURE PART 11 - API Routes
12. ARCHITECTURE PART 12 - Frontend Architecture
13. ARCHITECTURE PART 13 - Execution Modes
14. ARCHITECTURE PART 14 - Testing
15. ARCHITECTURE PART 15 - Key Design Decisions
16. ARCHITECTURE PART 16 - Future Enhancements
17. ARCHITECTURE PART 17 - Documentation-Logging Workflow
18. ARCHITECTURE PART 18 - Data Storage & Persistence
19. ARCHITECTURE PART 19 - Related Documentation
20. ARCHITECTURE PART 20 - Stage 2 Pipeline Capabilities

### 2. `docs/devserver_todos.md` (5 min)
**How:** Descending time order, do not read whole document (too long, probably old content down below)
**What:** Current priorities and tasks
**Why:** Know what needs to be done

### 3. `docs/DEVELOPMENT_DECISIONS.md` (10 min)
**How:** Check TOC or ###Headlines for Intel you need, so not read whole doc (too long)
**What:** Architectural decisions and WHY they were made
**Why:** ONLY WHEN YOU FEEL STUCK! Helps avoiding proposing rejected alternatives.

## 📚 Readings for specific task types

### 1. DEVELOPMENT_LOG.mf
**What:** Implementation history
**Why:** Avoid redundant implementations, understand system in-detail

### 2. `docs/LEGACY_SERVER_ARCHITECTURE.md` (20 min)
**What:** How the Legacy Server worked
**Why:** Understand the pedagogical foundation

**Critical concepts you MUST understand:**
- **Prompt Interception** - What it is and WHY it exists
- **Gegenhegemoniale Pädagogik** - Counter-hegemonic pedagogy (not solutionism!)
- **ComfyUI Custom Nodes** - How Legacy Server used ai4artsed_prompt_interception.py
- **Hidden Commands** (#notranslate#, #cfg:x#, etc.)
- **Pädagogische Workflows** (Stille Post, Dada, etc.)


---

## 🎯 How to Use This Documentation

### Starting a New Task

1. ✅ Read this file (README_FIRST.md)
2. ✅ Check `docs/devserver_todos.md` for current priorities
3. ✅ If you have a continuation prompt (CONTINUE_SESSION_PROMPT.md), read it
4. ✅ NOW you can start implementation
5. Consult README_EXTENDED.md for any further questions! It will be helpful!

### During Implementation

**Documentation details** (see Rule 1 at top for mandatory requirements):

1. **`DEVELOPMENT_LOG.md`** must include:
   - Session start time
   - All tasks completed
   - Files modified (with line counts)
   - Session duration and costs

2. **`DEVELOPMENT_DECISIONS.md`** - Only when making architectural decisions:
   - System architecture changes
   - New technology/library choices
   - Refactoring decisions with rationale

3. **`devserver_todos.md`** - Mark tasks as completed:
   - Move completed tasks from "CURRENT WORK" to previous sections
   - Update task statuses (✅/⏳/❌)
   - Add new tasks discovered during implementation

### Before Context Window Fills

User will say: **"Schreib jetzt alles in .md Dateien"**

1. Stop immediately
2. Update DEVELOPMENT_LOG.md with session stats
3. Create new CONTINUE_SESSION_PROMPT.md for next session
4. Document current state in relevant .md files

---

## 🔍 Quick Reference: Where to Find Information

| Question | Document |
|----------|----------|
| Why does DevServer exist? | LEGACY_SERVER_ARCHITECTURE.md |
| What is Prompt Interception? | LEGACY_SERVER_ARCHITECTURE.md (Section 2.1) |
| How do Pipelines work? | ARCHITECTURE.md (Section "Three-Layer System") |
| What are eco/fast modes? | ARCHITECTURE.md (Section "Backend Routing") |
| What needs to be done next? | devserver_todos.md |
| Why was X decision made? | DEVELOPMENT_DECISIONS.md |
| How much did previous sessions cost? | DEVELOPMENT_LOG.md |

---

## 🎓 Pedagogical Context (TL;DR)

**DevServer is NOT just a technical refactoring of Legacy Server.**

It embodies a **pedagogical philosophy**:

- **Against Solutionism**: AI tools should not be black boxes that produce outputs
- **For Process**: Learning happens through understanding and reflecting on HOW AI works
- **For Empowerment**: Users should be active creators, not passive consumers
- **For Cultural Context**: Art movements (Dada, Bauhaus) are about HALTUNGEN (attitudes), not styles

**Technical Translation:**
- Prompt Interception = Pedagogical intervention in AI process
- Configs (dada.json) = Artistic attitudes/contexts, not just parameters
- Pre-Pipeline = Conscious transformation, not direct consumption
- Hidden Commands = Power-user features without UI complexity

**If you break Prompt Interception or make it "more efficient", you break the pedagogy.**

---

