# Development Decisions Log
**AI4ArtsEd DevServer - Chronological Decision History**

> **WICHTIG FÜR ALLE TASKS:**
> Jede bedeutende Entwicklungsentscheidung MUSS hier eingetragen werden.
> Format: Datum, Entscheidung, Begründung, betroffene Dateien

---

## 2025-10-26: REMOVAL of instruction_types System

### Decision
**Instruction_types System komplett entfernt** (instruction_types.json + instruction_resolver.py)

### Reasoning (Joerissen)
> "Instruction type war eine eigenständige Fehlentscheidung des LLM. Sie ist redundant und erzeugt ambivalente Datenverteilung."

**Technisches Problem:**
- Instruction_types beschrieben 6 unterschiedliche Typen von Textmanipulation (Zwecke)
- Das Auslagern führte zu komplizierten und redundanten Informationsverweisen
- Widersprach der sauberen 3-Schichten-Architektur (Chunks → Pipelines → Configs)

**Architektonisches Problem:**
- Instruction_types waren ein viertes Layer zwischen Pipeline (Struktur) und Config (Inhalt)
- Erzeugte Ambivalenz: Gehört die Instruktion zur Struktur oder zum Inhalt?
- Antwort: Zum Inhalt! → `context` field in Config

### What Was Done
1. ✅ `schemas/instruction_types.json` → `.OBSOLETE`
2. ✅ `schemas/engine/instruction_resolver.py` → `.OBSOLETE`
3. ✅ Removed `instruction_type` field from all 34 configs
4. ✅ Removed from `Config` and `ResolvedConfig` dataclasses
5. ✅ Updated `chunk_builder.py`: Now uses `resolved_config.context` directly
6. ✅ Removed from `pipeline_executor.py`, `workflow_routes.py`, tests
7. ✅ All tests passing

### Current Architecture (Post-Removal)
**Three Clean Layers:**
- **Layer 1 - Chunks**: Template primitives (`manipulate.json`, `translate.json`, etc.)
- **Layer 2 - Pipelines**: Structural chunk sequences (no content)
- **Layer 3 - Configs**: User-facing content with `context` field

**What `context` field now does:**
- Contains complete instruction text (former "metaprompt")
- Populates `{{INSTRUCTION}}`, `{{INSTRUCTIONS}}`, `{{TASK}}`, `{{CONTEXT}}` placeholders
- No more indirection via instruction_types.json

### Future Consideration (Joerissen)
> "Wenn wir später jedoch feststellen, dass devserver eine Information über den Character einer pipeline-config-Information in den Metadaten einer config benötigen würde, dann würden wir diesen Klassifikator wieder herstellen. Aber nur als Information in den meta-daten, in keiner Weise als funktionale Referenz für den Code."

**IF we need classification later:**
- ✅ Add as metadata field: `"meta": {"instruction_type": "manipulation"}`
- ✅ For UI display/filtering only
- ❌ NEVER as functional code reference
- ❌ NEVER as indirection to external file

### Files Modified
**Core Engine:**
- `schemas/engine/config_loader.py` (removed instruction_type from dataclasses)
- `schemas/engine/chunk_builder.py` (now uses context directly)
- `schemas/engine/pipeline_executor.py` (removed from metadata)
- `schemas/engine/instruction_resolver.py` → `.OBSOLETE`

**Configs:**
- All 34 files in `schemas/configs/` (removed instruction_type field)

**Routes:**
- `my_app/routes/workflow_routes.py` (removed from API response)

**Tests:**
- `test_refactored_system.py` (removed instruction_resolver tests)

**Obsolete Files:**
- `schemas/instruction_types.json.OBSOLETE`
- `schemas/engine/instruction_resolver.py.OBSOLETE`

---

## 2025-10-26: REMOVAL of Legacy DevServer Code

### Decision
**All legacy engine modules removed** - DevServer no longer needs legacy code from pre-refactoring phase

### Reasoning (Joerissen)
> "der legacy-server läuft auf Port 5000 stabil (und wird nicht angetastet, wird aktuell verwendet). Devserver braucht m.E. keine Legacy-codes mehr. [...] Pipeline-Config-System ist so leistungsfähig dass wir alles 'übersetzen' können. Und zur Not kann legacy immer parallel betrieben werden."

**Context:**
- Legacy-Server (Port 5000) runs independently and stably
- DevServer's new Pipeline-Config-System is fully capable
- No need for code duplication between legacy and devserver
- Parallel operation possible when needed (no integration required)

### What Was Done
1. ✅ `schemas/engine/schema_registry.py` → `.OBSOLETE`
2. ✅ `schemas/engine/chunk_builder_old.py` → `.OBSOLETE`
3. ✅ `schemas/engine/pipeline_executor_old.py` → `.OBSOLETE`
4. ✅ Updated `schemas/__init__.py` - removed SchemaRegistry import
5. ✅ `schemas/schema_data/` → `schemas/schema_data_LEGACY_TESTS/`
6. ✅ All tests still passing (34 configs loaded)

### Files Marked OBSOLETE
**Engine Modules:**
- `schemas/engine/schema_registry.py.OBSOLETE` (pre-refactoring registry)
- `schemas/engine/chunk_builder_old.py.OBSOLETE` (pre-refactoring builder)
- `schemas/engine/pipeline_executor_old.py.OBSOLETE` (pre-refactoring executor)

**Test Data:**
- `schemas/schema_data_LEGACY_TESTS/` (old test configs)

### Active Engine Architecture (Post-Cleanup)
**Core Modules (ONLY):**
- `config_loader.py` - Config + Pipeline loader
- `chunk_builder.py` - Template-based chunk builder
- `pipeline_executor.py` - Pipeline orchestration
- `backend_router.py` - Backend routing (Ollama/ComfyUI/OpenRouter)
- `model_selector.py` - Model selection (eco/fast modes)
- `comfyui_workflow_generator.py` - ComfyUI workflow generation
- `prompt_interception_engine.py` - Legacy bridge for prompt interception

**Status:** Clean, no legacy code dependencies ✅

---

## 2025-10-26: Directory Restructure (configs_new → configs)

### Decision
Renamed `configs_new/` to `configs/` (primary config directory)
Renamed old `configs/` to `configs_old_DELETEME/`

### Reasoning
Previous task created `configs_new` instead of replacing `configs` → caused path reference problems

### What Was Done
```bash
mv configs configs_old_DELETEME
mv configs_new configs
# Updated all Python file references with sed
```

---

## TEMPLATE for Future Entries

## YYYY-MM-DD: [Decision Title]

### Decision
[What was decided]

### Reasoning
[Why - technical, pedagogical, architectural reasons]

### What Was Done
[Concrete changes - files, code, tests]

### Future Considerations
[Important notes for future development]

### Files Modified
[List of affected files]

---

## Development Principles (Standing Decisions)

### Architecture Principles
1. **Three-Layer Architecture (Immutable)**
   - Chunks (primitives) → Pipelines (structure) → Configs (content)
   - NO fourth layer for indirection
   - Content belongs in Config, not external references

2. **Context Field = Complete Instruction**
   - `context` contains full instruction text (former metaprompt)
   - No indirection via external files
   - Direct usage in chunk_builder.py

3. **Terminology (Joerissen)**
   - Avoid terms like "creative" - contradicts theoretical approach
   - Focus: "Haltungen statt Stile" (attitudes not styles)
   - No "solutionistic" language

### Data Management Principles
1. **NO Data Duplication**
   - Single source of truth for each data type
   - Configs in `schemas/configs/*.json` (not in registry/database)
   - Read directly from files

2. **Metadata Philosophy**
   - Metadata = Information ABOUT the data (display, categorization)
   - Metadata ≠ Functional code references
   - Metadata can contain classification for UI purposes only

### Testing Principles
1. **Test Files**
   - `test_refactored_system.py` - Architecture component tests
   - `test_pipeline_execution.py` - Full execution tests (requires Ollama)

2. **Test Coverage Required**
   - Every major architectural change needs test updates
   - Tests must pass before task completion

---

## History of Obsolete Decisions

### ❌ Instruction Types System (Removed 2025-10-26)
**Why it was created:** Previous LLM task tried to create reusable instruction templates
**Why it failed:** Created redundant fourth layer, ambivalent data distribution
**Lesson:** Keep architecture flat - no indirection layers between structure and content

---

**Last Updated:** 2025-10-26
**Next Task:** Continue updating documentation files to reflect removal of instruction_types
