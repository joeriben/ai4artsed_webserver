# DevServer Architecture

**Part 19: YYYY-MM-DD: [Decision Title]**

---

### Decision
[What was decided]
### Reasoning
[Why - with user quotes if applicable]
### What Was Done
[Concrete changes]
### Files Modified
[List]
```

**Why:** Prevents re-litigating old decisions, maintains institutional knowledge

#### 4. **ARCHITECTURE.md** - System Structure (this file)
**Purpose:** Technical reference for how system works

**When to update:**
- When adding new architectural patterns
- When changing system structure
- When updating data flow
- When pipeline/chunk/config inventory changes

**What to document:**
- Three-layer architecture
- Pipeline types and purposes
- Data flow patterns
- Module responsibilities
- File structure

**IMPORTANT:** Create backup before major changes:
```bash
cp docs/ARCHITECTURE.md docs/tmp/ARCHITECTURE_$(date +%Y%m%d_%H%M%S).md
```

**Why:** Central reference for understanding system design

### Logging Frequency

**Real-time (as you work):**
- TodoWrite tool updates
- Track file modifications

**Per Task Completion:**
- Update DEVELOPMENT_LOG.md "Tasks Completed" section
- Update devserver_todos.md with ✅

**Per Implementation Decision:**
- Add entry to DEVELOPMENT_DECISIONS.md
- Document WHY, not just WHAT

**Per Session Start:**
- Create new session entry in DEVELOPMENT_LOG.md

**Per Session End:**
- Fill in session cost data
- Update cumulative statistics
- Create git commit with cost info
- Create continuation prompt if needed

### Git Commit Strategy

**When to commit:**
- After completing major architectural change
- After test suite passes
- Before starting new major task
- At session end (with proper documentation)

**Commit message format:**
```
[type]: [Brief description]

[Detailed changes]
- Change 1
- Change 2

Session cost: $XX.XX
Session duration: Xh XXm
Files changed: +XXX -XXX lines

Related docs:
- Updated DEVELOPMENT_DECISIONS.md
- Updated ARCHITECTURE.md
- Updated devserver_todos.md
```

### Session Recovery

**Before context window fills:**
- User signals: "Schreib jetzt alles in .md Dateien"
- Immediately stop current work
- Update DEVELOPMENT_LOG.md with session stats
- Create CONTINUE_SESSION_PROMPT.md in docs/tmp/
- Document current task progress, next priorities, and key context

**Why:** Claude Code sessions have limited context. Documentation provides continuity.

**See:** `docs/DEVELOPMENT_LOG.md` section "Logging Workflow Rules" for complete procedural details

---

