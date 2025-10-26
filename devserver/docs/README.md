# DevServer Documentation Structure

## ⚠️ NEW TO THIS PROJECT? START HERE

**→ Read `README_FIRST.md` before doing ANYTHING else! ←**

That file contains mandatory reading requirements and verification questions you must answer before starting work.

**Why?** This project implements pedagogical concepts (Prompt Interception, Gegenhegemoniale Pädagogik) that are NOT obvious from code alone. Without reading documentation, you WILL break critical features.

---

## Documentation Organization

### Core Documentation (Permanent)
Located in `/docs/`:
- **ARCHITECTURE.md** - Current technical architecture (canonical reference)
- **DEVELOPMENT_DECISIONS.md** - Chronological decision log (updated by every task)
- **LEGACY_SERVER_ARCHITECTURE.md** - Legacy system documentation (historical reference)

### Temporary Documentation
Located in `/docs/tmp/`:
- Task-specific summaries (REFACTORING_SUMMARY.md, etc.)
- Audit reports (ARCHITECTURE_AUDIT.md)
- Phase reports (PHASE4_*, CLEANUP_AUDIT.md, etc.)
- Implementation notes (EXPERT_MODE_IMPLEMENTATION.md, etc.)

**Lifecycle:** Temporary docs are created during tasks, reviewed, then archived or deleted.

### Example Documentation
Located in `/docs/examples/`:
- API usage examples
- Configuration examples
- Integration examples

---

## Current Documentation Inventory

### ✅ Permanent (in /docs/)
1. **DEVELOPMENT_DECISIONS.md** - Decision log (NEWLY CREATED, CURRENT)
2. **LEGACY_SERVER_ARCHITECTURE.md** - Legacy system (REVIEWED, CURRENT)

### 📦 To Be Organized (currently in root)

**Architecture/Technical:**
- ARCHITECTURE.md → Keep in /docs/ (needs update)
- DEVSERVER_COMPREHENSIVE_DOCUMENTATION.md → Keep in /docs/ (needs update)

**Temporary Task Reports (→ /docs/tmp/):**
- REFACTORING_SUMMARY.md (from Phase 3 refactoring task)
- REFACTORING_COMPLETION_REPORT.md (from Phase 3 refactoring task)
- CLEANUP_AUDIT.md (from cleanup task)
- CONFIG_FIXES_SUMMARY.md (from config fixes task)
- PHASE4_EXPERT_MODE_API_SUMMARY.md (from Phase 4 task)
- EXPERT_MODE_IMPLEMENTATION.md (from Phase 4 task)

**Design Documents (→ /docs/tmp/ or delete if implemented):**
- SCHEMA_PIPELINE_EXPORT_DESIGN.md
- TASK_BASED_MODEL_SELECTION.md
- AUTO_MEDIA_GENERATION.md

**Examples (→ /docs/examples/):**
- API_USAGE_EXAMPLE.md

**Todos (→ /docs/):**
- DEVSERVER_TODOS.md (keep updated)

**Duplicates/Obsolete:**
- LEGACY_SERVER_ARCHITECTURE (Copy).md → DELETE

---

## Documentation Maintenance Rules

### For Every Task
1. **Update DEVELOPMENT_DECISIONS.md** if you make architectural changes
2. **Update ARCHITECTURE.md** if you change core architecture
3. **Create temporary reports in /docs/tmp/** for task summaries
4. **Do NOT create root-level .md files** (use /docs/ or /docs/tmp/)

### Cleanup Policy
- Review /docs/tmp/ quarterly
- Archive completed phase reports
- Delete obsolete task summaries

---

**Created:** 2025-10-26
**Purpose:** Prevent documentation chaos, establish clear structure
