# Development Decisions Log
**AI4ArtsEd DevServer - Chronological Decision History**

> **WICHTIG FÜR ALLE TASKS:**
> Jede bedeutende Entwicklungsentscheidung MUSS hier eingetragen werden.
> Format: Datum, Entscheidung, Begründung, betroffene Dateien

---

## 2025-10-27: AUTO-MEDIA GENERATION - Output-Config Defaults System

### Decision
**Centralized default Output-Config mapping via `output_config_defaults.json`**
- Pre-pipeline configs (dada.json) suggest media type via `media_preferences.default_output`
- Pre-pipeline configs DO NOT choose specific models
- DevServer uses `output_config_defaults.json` to map `media_type + execution_mode → output_config`

### Reasoning

**Separation of Concerns:**
- Text manipulation configs should not dictate which image/audio model to use
- Dada says "I produce visual content" not "I use SD3.5 Large"
- Content transformation is separate from media generation

**Problem with Alternative Approaches:**

❌ **Adding `output_configs` to pre-pipeline configs (dada.json):**
```json
{
  "output_configs": {
    "image": {"eco": "sd35_large", "fast": "flux1"}
  }
}
```
- Violates separation of concerns
- Text manipulation shouldn't know about specific models
- 34+ configs would all need to specify output models
- Changes to default image model require editing 34+ files

✅ **Centralized `output_config_defaults.json`:**
```json
{
  "image": {"eco": "sd35_large", "fast": "flux1_openrouter"},
  "audio": {"eco": "stable_audio", "fast": "stable_audio_api"},
  "music": {"eco": "acestep", "fast": null},
  "video": {"eco": "animatediff", "fast": null}
}
```
- One central place defines defaults
- Pre-pipeline configs stay focused on text transformation
- Change default image model: edit one line
- Pedagogically clear: separation between content and generation

**Data Flow:**
```
1. User runs dada.json config
2. Dada outputs optimized text
3. DevServer reads: media_preferences.default_output = "image"
4. DevServer reads: execution_mode = "eco"
5. DevServer lookup: output_config_defaults["image"]["eco"] → "sd35_large"
6. DevServer executes: single_prompt_generation with sd35_large config
7. Image generated via Output-Chunk system
```

**User Override Options:**
- `#image#`, `#audio#`, `#music#`, `#video#` tags override default
- `default_output = "text"` → no auto-media generation

### Files Affected
- **Created:**
  - `schemas/output_config_defaults.json` (central mapping)
  - `schemas/engine/output_config_selector.py` (loader/selector)
  - `ExecutionContext` class (media tracking throughout execution)
  - `MediaOutput` dataclass (structured media output tracking)
- **Updated:**
  - `my_app/routes/workflow_routes.py` (replace deprecated generate_image_from_text)
  - `docs/ARCHITECTURE.md` (Pattern 5: Auto-Media Generation + DevServer awareness)

### DevServer Media Awareness
**Decision:** DevServer must track expected and actual media types throughout execution

**Why:**
1. **Media Collection** - Track all media in multi-step processes (text → image → audio)
2. **Presentation Logic** - Format API response based on media type
3. **Pipeline Chaining** - Reuse execution context for multiple generations
4. **Error Handling** - Validate expected vs actual media type
5. **Frontend Communication** - Tell UI what media to expect/display

**Implementation:**
- `ExecutionContext` tracks: expected_media_type, generated_media[], text_outputs[]
- `MediaOutput` tracks: media_type, prompt_id, output_mapping, config_name, status
- Validation: Output-Chunk.media_type matches expected type

### Implementation Status
- ✅ **Design:** Documented in ARCHITECTURE.md + DEVELOPMENT_DECISIONS.md
- ⚠️ **Implementation:** READY TO BEGIN

---

## 2025-10-26: OUTPUT-CHUNK ARCHITECTURE - Embedded ComfyUI Workflows

### Decision
**Output-Chunks now contain complete ComfyUI API workflows embedded in JSON**
- ComfyUI workflows are stored directly in chunk files (not generated dynamically)
- Each Output-Chunk includes: `workflow`, `input_mappings`, `output_mapping`, `meta`
- Deprecate: `comfyui_workflow_generator.py` (will be removed in future cleanup)

### Reasoning

**Problem with Dynamic Generation:**
- `comfyui_workflow_generator.py` hardcoded workflows in Python code
- Workflows were generated at runtime from templates
- Separated workflow structure from data (against "data over code" principle)
- Made workflows harder to edit for non-programmers

**New Approach - Embedded Workflows:**
```json
{
  "name": "output_audio_stable_audio",
  "type": "output_chunk",
  "workflow": {
    "3": { "class_type": "KSampler", "inputs": {...} },
    "4": { "class_type": "CheckpointLoaderSimple", ... },
    ...
  },
  "input_mappings": {
    "prompt": {"node_id": "6", "field": "inputs.text"},
    ...
  },
  "output_mapping": {
    "node_id": "19", "output_type": "audio", "format": "mp3"
  }
}
```

**Advantages:**
1. **Workflows are Data:** JSON format, not Python code
2. **Easier to Edit:** Can be modified without code changes
3. **Transparency:** Complete workflow visible in chunk file
4. **No Generation:** Server fills placeholders and submits directly to ComfyUI
5. **Backend Agnostic:** Same format works with ComfyUI, SwarmUI, etc.

**Migration Strategy:**
- Extract existing workflows from `comfyui_workflow_generator.py`
- Convert to Output-Chunk JSON format
- Add `input_mappings` metadata (server needs to know where to inject prompts)
- Add `output_mapping` metadata (server needs to know where to extract media)
- Update `backend_router.py` to process Output-Chunks directly

### Files Affected
- **Deprecated:**
  - `schemas/engine/comfyui_workflow_generator.py` (marked for removal)
- **To Create:**
  - `schemas/chunks/output_image_sd35_standard.json`
  - `schemas/chunks/output_audio_stable_audio.json`
  - `schemas/chunks/output_music_acestep.json`
- **To Update:**
  - `schemas/engine/backend_router.py` (process Output-Chunks)
  - `docs/ARCHITECTURE.md` (document Output-Chunk structure)

### Implementation Status
- ⚠️ **Design:** Documented in ARCHITECTURE.md
- ⚠️ **Implementation:** NOT YET IMPLEMENTED
- ⚠️ **Migration:** Old system still in place (comfyui_workflow_generator.py still used)

---

## 2025-10-26: CHUNK CONSOLIDATION - Single manipulate Chunk

### Decision
**Consolidated all text transformation chunks into ONE `manipulate.json` chunk**
- Deleted: `translate.json`, `prompt_interception.json`, `prompt_interception_lyrics.json`, `prompt_interception_tags.json`
- Fixed: `manipulate.json` template (removed duplicate placeholder)
- Updated: All pipelines to use `manipulate` chunk only

### Reasoning (Joerissen)
> "Dann reicht ein manipulate-Chunk [...] 'Prompt interception' ist ein kritisches pädagogisches Konzept das auf dieser Ebene nicht auftauchen sollte"

**Technical Problem:**
- Multiple chunks (translate, prompt_interception, manipulate) were functionally identical
- Only difference: placeholder naming and temperature settings
- `translate` = `manipulate` with translation context + low temperature
- `prompt_interception` = `manipulate` with explicit Task/Context structure
- Content belongs in Configs, not in separate chunks

**Placeholder Redundancy:**
```python
# Before:
replacement_context = {
    'INSTRUCTION': instruction_text,
    'INSTRUCTIONS': instruction_text,  # Duplicate!
    'TASK': instruction_text,          # Duplicate!
    'CONTEXT': instruction_text,       # Duplicate!
}
```
All four resolved to same value (config.context) → caused duplication in rendered prompts

**Template Duplication Example:**
```
# manipulate.json before:
{{INSTRUCTIONS}}

{{CONTEXT}}      ← Duplicate!

Text to manipulate:
{{PREVIOUS_OUTPUT}}
```
Instruction appeared TWICE in all 29 configs using simple_manipulation pipeline!

### What Was Done

**Deleted Chunks:**
1. ✅ `translate.json` - Unused (0 configs), redundant
2. ✅ `prompt_interception.json` - Only 1 config used it, now uses simple_manipulation
3. ✅ `prompt_interception_lyrics.json` - BROKEN (invalid structure)
4. ✅ `prompt_interception_tags.json` - BROKEN (invalid structure)

**Fixed Template:**
```json
// manipulate.json - BEFORE
{
  "template": "{{INSTRUCTIONS}}\n\n{{CONTEXT}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}"
}

// manipulate.json - AFTER
{
  "template": "{{INSTRUCTION}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}"
}
```

**Updated chunk_builder.py:**
```python
# Removed TASK and CONTEXT aliases
replacement_context = {
    'INSTRUCTION': instruction_text,
    'INSTRUCTIONS': instruction_text,  # Backward compatibility only
    'INPUT_TEXT': context.get('input_text', ''),
    'PREVIOUS_OUTPUT': context.get('previous_output', ''),
    'USER_INPUT': context.get('user_input', ''),
    **context.get('custom_placeholders', {})
}
```

**Updated Pipelines:**
- `audio_generation.json`: prompt_interception → manipulate
- `image_generation.json`: prompt_interception → manipulate
- `music_generation.json`: [prompt_interception_tags, prompt_interception_lyrics] → [manipulate]
- `simple_interception.json`: [translate, manipulate] → [manipulate, manipulate]
- Deleted: `prompt_interception_single.json`

**Updated Configs:**
- `translation_en.json`: prompt_interception_single → simple_manipulation

### Current Architecture (Post-Consolidation)

**Chunk Inventory:**
1. ✅ `manipulate.json` - Universal text transformation
2. ✅ `comfyui_image_generation.json` - Image generation
3. ✅ `comfyui_audio_generation.json` - Audio generation

**Pipeline Structure:**
- 6 pipelines (down from 7)
- All text operations use `manipulate` chunk
- Content differentiation via `config.context` field

**Test Results:**
- ✅ 34 configs loaded successfully
- ✅ 6 pipelines loaded successfully
- ✅ All tests passing
- ✅ No duplication in rendered prompts
- ✅ Token efficiency improved (instruction appears once, not twice)

### Impact Analysis

**Affected Configs:**
- 29 configs using `simple_manipulation` → Cleaner prompts, no duplication
- 2 configs using `music_generation` → Simplified pipeline structure
- 2 configs using `audio_generation` → Updated to manipulate chunk
- 1 config using `prompt_interception_single` → Now uses simple_manipulation

**Token Savings:**
- Removed ~50-200 tokens per request (instruction no longer duplicated)
- Affects 30 configs

**Pedagogical Clarity:**
- "Prompt interception" remains a pedagogical concept at Config level
- Chunk level now purely technical (manipulate = transform text)
- No semantic confusion between chunk names and content

### Future Considerations

**Prompt Interception as Pedagogical Concept:**
- Configs can still use "Task / Context / Prompt" structure in their `config.context` field
- Example:
```json
{
  "context": "Task:\nTransform this prompt...\n\nContext:\nYou are a Dadaist artist...\n\nPrompt:"
}
```
- The structure is content, not template architecture

**Task-Type Metadata (Next Phase):**
- Add `task_type` to chunk metadata
- Link to model_selector.py categories (translation, vision, etc.)
- Enable task-based LLM selection

### Files Modified

**Chunks (Deleted):**
- `schemas/chunks/translate.json` ❌
- `schemas/chunks/prompt_interception.json` ❌
- `schemas/chunks/prompt_interception_lyrics.json` ❌
- `schemas/chunks/prompt_interception_tags.json` ❌

**Chunks (Modified):**
- `schemas/chunks/manipulate.json` (fixed template)

**Pipelines (Deleted):**
- `schemas/pipelines/prompt_interception_single.json` ❌

**Pipelines (Modified):**
- `schemas/pipelines/audio_generation.json`
- `schemas/pipelines/image_generation.json`
- `schemas/pipelines/music_generation.json`
- `schemas/pipelines/simple_interception.json`

**Configs (Modified):**
- `schemas/configs/translation_en.json`

**Engine (Modified):**
- `schemas/engine/chunk_builder.py` (removed TASK/CONTEXT aliases)

---

## 2025-10-26: REMOVAL of instruction_types System

### Decision
**Instruction_types System komplett entfernt** (instruction_types.json + instruction_resolver.py)

### Reasoning (Joerissen)
> "Instruction type war eine eigenständige Fehlentscheidung des LLM. Sie ist redundant und erzeugt ambivalente Datenverteilung."

**Technisches Problem:**
- Instruction_types beschrieben 6 Kategorien mit 17 Varianten von Textmanipulation/Analyse
- Das Auslagern führte zu komplizierten und redundanten Informationsverweisen
- Widersprach der sauberen 3-Schichten-Architektur (Chunks → Pipelines → Configs)

**Die 6 Kategorien waren:**
1. **translation** (3 variants: standard, culture_sensitive, rigid)
   - Zweck: Übersetzung mit unterschiedlichen Ansätzen
   - Problem: Übersetzungs-Nuancen gehören in Config-context, nicht in externes System

2. **manipulation** (5 variants: standard, creative, amplify, analytical, poetic)
   - Zweck: Texttransformation mit verschiedenen Stilen
   - Problem: "Creative" widerspricht theoretischem Ansatz (Haltungen statt Stile)
   - Problem: Diese "Stile" sind eigentlich Inhalte und gehören in Configs

3. **security** (2 variants: standard, strict)
   - Zweck: Content-Filtering unterschiedlicher Strenge
   - Problem: Sicherheits-Policy gehört in Config-Parameter, nicht in separate Typen

4. **image_analysis** (4 variants: formal, descriptive, iconographic, non_western)
   - Zweck: Bildanalyse-Methoden (Panofsky etc.)
   - Problem: Analyse-Methode ist Inhalt (gehört in Config), nicht Struktur

5. **prompt_optimization** (3 variants: image_generation, audio_generation, music_generation)
   - Zweck: Optimierung für verschiedene Medien-Backends
   - Problem: Media-spezifische Optimierung gehört in Chunk-Templates, nicht in Typen

6. **[weitere ungenutzte Kategorien]**
   - Viele instruction_types wurden in keinem Config referenziert
   - Redundanz: Configs enthielten bereits komplette instruction-Texte im context-Feld

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
