# ⚠️ READ THIS FIRST - Mandatory for All New Tasks/Sessions

**Date Created:** 2025-10-26
**Purpose:** Prevent costly mistakes from incomplete understanding
**Applies to:** ALL Claude Code sessions, ALL new LLM tasks

---

## 🚨 STOP - Before You Do Anything

**You are about to work on the AI4ArtsEd DevServer.**

This is NOT a typical CRUD app or API server. It implements **pedagogical concepts** about AI art education that are critical to preserve.

**If you start coding without reading the documentation below, you WILL:**
- ❌ Break pedagogical concepts (e.g., Prompt Interception)
- ❌ Propose solutions that already exist
- ❌ Misunderstand fundamental architecture differences (Legacy vs DevServer)
- ❌ Waste time and money (this session cost example: asking questions already documented)

---

## 📚 Required Reading (Total: ~55 minutes)

**Read these documents IN ORDER before any implementation work:**

### 1. `docs/README.md` (5 min)
**What:** Documentation structure overview
**Why:** Know where to find information

### 2. `docs/LEGACY_SERVER_ARCHITECTURE.md` (20 min)
**What:** How the Legacy Server worked
**Why:** Understand the pedagogical foundation

**Critical concepts you MUST understand:**
- **Prompt Interception** - What it is and WHY it exists
- **Gegenhegemoniale Pädagogik** - Counter-hegemonic pedagogy (not solutionism!)
- **ComfyUI Custom Nodes** - How Legacy Server used ai4artsed_prompt_interception.py
- **Hidden Commands** (#notranslate#, #cfg:x#, etc.)
- **Pädagogische Workflows** (Stille Post, Dada, etc.)

### 3. `docs/ARCHITECTURE.md` (15 min)
**What:** How DevServer works NOW
**Why:** Understand current system architecture

**Critical concepts you MUST understand:**
- **Three-Layer System**: Chunks → Pipelines → Configs
- **Input-Type-Based Pipelines** (not output-type!)
- **Backend Routing**: eco vs fast, local vs remote
- **Pipeline vs Pre-Pipeline**: Text transformation BEFORE media generation
- **Backend Transparency**: Same pipeline works with ComfyUI, OpenRouter, etc.

### 4. `docs/devserver_todos.md` (5 min)
**What:** Current priorities and tasks
**Why:** Know what needs to be done

### 5. `docs/DEVELOPMENT_DECISIONS.md` (10 min)
**What:** Architectural decisions and WHY they were made
**Why:** Avoid proposing rejected alternatives

---

## ✅ Verification - Can You Answer These?

Before proceeding with implementation, you should be able to answer:

1. **What is "Prompt Interception"?**
   - What does it do?
   - Why is it pedagogically important?
   - How does it prevent "solutionistic" usage?

2. **Legacy vs DevServer - Key Difference:**
   - How did Legacy Server implement Prompt Interception? (ComfyUI Custom Node)
   - How does DevServer implement Prompt Interception? (Pipeline Chunk)
   - Why was this change made?

3. **What is `ComfyUIWorkflowGenerator`?**
   - What does it generate?
   - Why does it exist in DevServer?

4. **Pipeline Architecture:**
   - What is a Pre-Pipeline? (Text transformation)
   - What is an Output-Pipeline? (Media generation)
   - Why are they separate?

5. **Input-Type-Based Pipelines:**
   - Why `single_prompt_generation` instead of `image_generation`?
   - What's the difference between input-type and output-type naming?

**If you cannot answer these questions, STOP and read the documentation.**

---

## 🎯 How to Use This Documentation

### Starting a New Task

1. ✅ Read this file (README_FIRST.md)
2. ✅ Read all 5 required documents (in order)
3. ✅ Verify understanding (answer the questions above)
4. ✅ Check `docs/devserver_todos.md` for current priorities
5. ✅ If you have a continuation prompt (CONTINUE_SESSION_PROMPT.md), read it
6. ✅ NOW you can start implementation

### During Implementation

- **Update `DEVELOPMENT_LOG.md`** - Track session progress and costs
- **Update `DEVELOPMENT_DECISIONS.md`** - When making architectural decisions
- **Update `ARCHITECTURE.md`** - When changing system architecture
- **Update `devserver_todos.md`** - Mark tasks as completed

### Before Context Window Fills

User will say: **"Schreib jetzt alles in .md Dateien"**

1. Stop immediately
2. Update DEVELOPMENT_LOG.md with session stats
3. Create new CONTINUE_SESSION_PROMPT.md for next session
4. Document current state in relevant .md files

---

## 📖 Example: What Happens Without Reading Docs

**Real example from this session (2025-10-26):**

**Mistake:**
- I started designing an "implementation strategy for pipeline-based output system"
- I proposed creating JSON template files from ComfyUI exports
- I asked: "What is ComfyUIWorkflowGenerator? Erläutere was das ist."

**Problem:**
- I had NOT read `LEGACY_SERVER_ARCHITECTURE.md`
- I did NOT understand that DevServer replaces ComfyUI Custom Nodes with Pipeline Chunks
- I did NOT know what Prompt Interception was or why it exists

**User Response:**
> "HAST DU DIE DOKUMENTE IN /docs NICHT GELESEN??"

**Result:**
- Wasted time proposing wrong solutions
- Had to backtrack and read documentation
- User had to stop work to correct my misunderstanding

**Cost:** ~15-20 minutes of wasted session time + user frustration

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

## ✅ Checklist Before Starting Work

Copy this into your first message to confirm:

```
✅ I have read README_FIRST.md
✅ I have read LEGACY_SERVER_ARCHITECTURE.md (20 min)
✅ I have read ARCHITECTURE.md (15 min)
✅ I have read devserver_todos.md (5 min)
✅ I have read DEVELOPMENT_DECISIONS.md (10 min)
✅ I can explain what Prompt Interception is and why it matters
✅ I understand the difference between Legacy (Custom Nodes) and DevServer (Pipeline Chunks)
✅ I understand what ComfyUIWorkflowGenerator does
✅ I am ready to start implementation
```

---

**Now go read the documentation. See you in ~55 minutes! 📚**
