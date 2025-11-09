# ⚠️ READ THIS FIRST - Mandatory for All New Tasks/Sessions

**Date Created:** 2025-10-26
**Purpose:** Prevent costly mistakes from incomplete understanding
**Applies to:** ALL Claude Code sessions, ALL new LLM tasks
**Last edit: 2025-11-02**

---

## 🚨 STOP - Before You Do Anything

YOU MUST NOT EDIT ANY CODE BEFORE CONSULTING USER. ESPECIALLY WHEN FRESHLY STARTEd, DO NOT DEVELOP SUPPOSEDLY "GOOD IDEAS" YOURSELF: YOU WILL MOST LIKELY BE WRONG AND MESS UP THE SYSTEM.

AFTER READING THIS FIRST MESSAGE, CONFIRM YOU UNDERSTOOD IT.

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

### 1. `docs/ARCHITECTURE.md` TABLE OF CONTENTS **⭐ AUTHORITATIVE**
You must understand the TOC of architecture.md in order to know WHEN to look up information related to your specific task, instead of "inventing things" that already exist. CONSISTENCY IS CRUCIAL!

**What:** Complete 4-stage orchestration flow (Part I of ARCHITECTURE.md)
**Why:** Understand the CORRECT architecture for implementing flow logic
**How:** The Document is quite long, use it for your orientation in the process. Hold the content structure firmly in your memory at all times, so that you will know when to look things up instead of making thing up yourself!

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

#### Table of Contents of the ARCHITECTURE.md file:

Part I: Orchestration (How It Works)
1. [4-Stage Orchestration Flow](#1-4-stage-orchestration-flow) ⭐ **START HERE**

Part II: Components (What The Parts Are)
2. [Architecture Overview](#2-architecture-overview)
3. [Three-Layer System](#3-three-layer-system)
4. [Pipeline Types](#4-pipeline-types)
5. [Data Flow Patterns](#5-data-flow-patterns)
6. [Engine Modules](#6-engine-modules)
7. [Backend Routing](#7-backend-routing)
8. [Model Selection](#8-model-selection)
9. [File Structure](#9-file-structure)
10. [API Routes](#10-api-routes)
11. [Frontend Architecture](#11-frontend-architecture)
12. [Execution Modes](#12-execution-modes)
13. [Documentation & Logging Workflow](#13-documentation--logging-workflow)

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

**⚠️ MANDATORY DOCUMENTATION - MUST BE DONE:**

1. **Update `DEVELOPMENT_LOG.md`** - REQUIRED for EVERY session
   - Document session start time
   - Track all tasks completed
   - Record code changes (files modified, lines added/removed)
   - Log session duration and costs
   - **WHY:** Lückenlose Dokumentation ist kritisch für Projektverfolgung

2. **Update `DEVELOPMENT_DECISIONS.md`** - When making architectural decisions
   - Any change to system architecture
   - Any new technology/library choices
   - Any refactoring decisions

3. **Update `ARCHITECTURE.md`** - When changing system architecture
   - New components added
   - Component interactions changed
   - API endpoints modified

4. **Update `devserver_todos.md`** - Mark tasks as completed
   - Move completed tasks from "CURRENT WORK" to previous sections
   - Update task statuses (✅/⏳/❌)
   - Add new tasks discovered during implementation

**⚠️ REMEMBER:** Documentation is not optional. Every session MUST be logged in DEVELOPMENT_LOG.md.

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

