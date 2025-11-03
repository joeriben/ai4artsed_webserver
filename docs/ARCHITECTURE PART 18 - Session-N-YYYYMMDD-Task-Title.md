# DevServer Architecture

**Part 18: Session [N]: [YYYY-MM-DD] - [Task Title]**

---

**Duration (Wall):** [Time]
**Duration (API):** [Time]
**Cost:** $[Amount]

### Model Usage
- claude-sonnet: [stats]
- claude-haiku: [stats]

### Tasks Completed
1. ✅ [Task]

### Code Changes
- Lines added: [N]
- Lines removed: [N]
```

**Why:** Cost transparency + ability to analyze development velocity and efficiency

#### 2. **devserver_todos.md** - Task Management
**Purpose:** Current priorities and task status tracking

**When to update:**
- Mark tasks completed with ✅ and timestamp
- Add new tasks discovered during implementation
- Update status: NOT STARTED → IN PROGRESS → COMPLETED
- Reorder priorities when needed

**What to track:**
- Task description
- Status (NOT STARTED/IN PROGRESS/COMPLETED)
- Estimated time
- Priority level
- Dependencies

**Why:** Keeps focus on current priorities, prevents forgetting subtasks

#### 3. **DEVELOPMENT_DECISIONS.md** - Architectural Decisions
**Purpose:** Document WHY decisions were made (not just WHAT)

**When to update:**
- When making architectural decisions
- When choosing between alternatives
- When removing/adding major components
- When changing established patterns

**What to document:**
- Decision made
- Reasoning (technical/pedagogical/architectural)
- Alternatives considered
- Concrete implementation changes
- Files modified
- Future considerations

**Format:**
```markdown
