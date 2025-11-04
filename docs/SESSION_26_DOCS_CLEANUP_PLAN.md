# Session 26 - Documentation Cleanup Plan

**Date:** 2025-11-04
**Purpose:** Clean up docs root directory - archive reference/historical documentation

---

## Current Docs Root Analysis

**Active Core Documentation (KEEP IN ROOT):**
- ✅ `readme.md` - Entry point
- ✅ `DEVELOPMENT_LOG.md` - Session tracking
- ✅ `DEVELOPMENT_DECISIONS.md` - Architectural decisions
- ✅ `devserver_todos.md` - Current priorities
- ✅ `ARCHITECTURE PART 01-20.md` - Complete architecture reference
- ✅ `SESSION_21_HANDOVER.md` - Recent session (keep last 5-6)
- ✅ `SESSION_22_HANDOVER.md` - Recent session
- ✅ `SESSION_24_HANDOVER.md` - Recent session
- ✅ `SESSION_25_HANDOVER.md` - Most recent session

**Reference Documentation (MOVE TO archive/reference/):**
- 📋 `ITEM_TYPE_TAXONOMY.md` - Execution tracker data model (Session 18)
- 📋 `EXECUTION_HISTORY_UNDERSTANDING_V3.md` - Requirements context (Session 17)
- 📋 `EXECUTION_TRACKER_ARCHITECTURE.md` - Technical design (Session 19, 1200+ lines)
- 📋 `safety-architecture-matters.md` - §86a safety issue resolved (Session 14)
- 📋 `LEGACY_SERVER_ARCHITECTURE.md` - Old server documentation

**Why Archive These:**
1. **Historical Context** - Valuable reference but not daily-use documents
2. **Resolved Issues** - safety-architecture-matters.md documents a fixed problem
3. **Implementation Reference** - Execution tracker docs are comprehensive blueprints, completed in Sessions 19-24
4. **Reduce Cognitive Load** - Clean docs root makes it easier to find current work

**What Stays in Archive:**
- All archived session handovers (SESSION_18-20)
- Bug reports (FAST_MODE_BUG_REPORT, TESTING_REPORT_SESSION_23)
- Legacy planning documents

---

## Archiving Strategy

### Create New Archive Category
```
docs/archive/reference/
```

This subdirectory will contain reference documentation that is:
- Complete and stable
- Important for understanding implementation details
- Not part of active development
- Consulted occasionally but not daily

### Move Plan

**To `docs/archive/reference/`:**
1. ITEM_TYPE_TAXONOMY.md
2. EXECUTION_HISTORY_UNDERSTANDING_V3.md
3. EXECUTION_TRACKER_ARCHITECTURE.md
4. safety-architecture-matters.md
5. LEGACY_SERVER_ARCHITECTURE.md

### Final Docs Root Structure

**After cleanup, docs/ will contain ONLY:**
```
docs/
├── readme.md (entry point)
├── DEVELOPMENT_LOG.md (session tracking)
├── DEVELOPMENT_DECISIONS.md (decisions)
├── devserver_todos.md (current priorities)
├── ARCHITECTURE PART 01-20.md (architecture)
├── SESSION_21_HANDOVER.md (recent)
├── SESSION_22_HANDOVER.md (recent)
├── SESSION_24_HANDOVER.md (recent)
├── SESSION_25_HANDOVER.md (latest)
├── SESSION_26_DOCUMENTATION_AUDIT.md (this session)
└── archive/
    ├── reference/ (NEW - stable implementation docs)
    │   ├── ITEM_TYPE_TAXONOMY.md
    │   ├── EXECUTION_HISTORY_UNDERSTANDING_V3.md
    │   ├── EXECUTION_TRACKER_ARCHITECTURE.md
    │   ├── safety-architecture-matters.md
    │   └── LEGACY_SERVER_ARCHITECTURE.md
    └── (existing archived sessions and reports)
```

---

## Rationale

**Why This is Better:**
1. **Docs root is scannable** - Only 10-12 files, all current/active
2. **Clear categorization** - Active vs. Reference vs. Historical
3. **Archive preserves everything** - Nothing deleted, just organized
4. **Easy to find** - "Where's the execution tracker design?" → archive/reference/
5. **Follows best practice** - Reference docs separate from working docs

**When to Consult Archived Reference:**
- Implementing new features related to execution tracking
- Understanding why certain design decisions were made
- Debugging execution history issues
- Onboarding new developers (full implementation context)

---

## Execution Plan

1. Create `docs/archive/reference/` directory
2. Move 5 files using `git mv` (preserves history)
3. Update any references in active docs
4. Verify docs root is clean
5. Commit with descriptive message

**Expected Impact:**
- Docs root: 24 files → 14 files (42% reduction)
- All information preserved and accessible
- Clear separation of concerns
