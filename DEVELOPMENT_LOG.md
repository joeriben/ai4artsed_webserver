# Development Log

## Session 152 - Tone.js Browser-Based Music Generation
**Date:** 2026-01-31
**Focus:** Add Tone.js as new output option for browser-based music synthesis
**Status:** COMPLETED

### Overview

Following the p5.js pattern for generative graphics, Tone.js enables browser-based music generation. The LLM generates Tone.js JavaScript code that runs directly in the frontend via iframe.

### Architecture Pattern: Code Generation Output

| Component | p5.js (Graphics) | Tone.js (Audio) |
|-----------|------------------|-----------------|
| Chunk Type | `text_passthrough` | `text_passthrough` |
| Backend Type | `vue_p5js` | `vue_tonejs` |
| Media Type | `code` | `code` |
| Language | JavaScript | JavaScript |
| Execution | Browser Canvas | Web Audio API |

**Key Difference from Binary Media:**
- No ComfyUI/SwarmUI workflow execution
- LLM generates code directly (Claude Sonnet 4.5 via OpenRouter)
- Code passed through to frontend for browser execution
- No server-side rendering required

### New Files

| File | Description |
|------|-------------|
| `schemas/chunks/output_code_tonejs.json` | Passthrough chunk for Tone.js code |
| `schemas/configs/output/tonejs_code.json` | Output config with LLM prompt |
| `schemas/configs/interception/tonejs_composer.json` | Stage 2: Text → Musical structure |

### Modified Files

| File | Change |
|------|--------|
| `routes/schema_pipeline_routes.py` | Media type detection for 'tonejs' (4 locations) |
| `routes/media_routes.py` | New route `/api/media/tonejs/<run_id>` |
| `text_transformation.vue` | Tone.js config bubble, iframe with Play/Stop |
| `text_transformation.css` | Styles for `.tonejs-iframe` |
| `canvas.ts` | `tonejs_composer` in InterceptionPresets |
| `THIRD_PARTY_CREDITS.md` | p5.js (LGPL-2.1) and Tone.js (MIT) licenses |

### Stage 2 Interception: Music Composer

Transforms text descriptions into layered musical structure:
```
RHYTHM: [Drums, percussion patterns]
BASS: [Bass line characteristics]
HARMONY: [Chord progressions, pads]
MELODY: [Lead lines, hooks]
TEXTURE: [Ambient elements, effects]
```

### Frontend: Tone.js Player

- Play/Stop buttons (required due to browser audio policy)
- Visual feedback (animated bars visualizer)
- Status indicator (German: "Klicke Play um die Musik zu starten")
- Code editor for viewing/editing generated code

### Third-Party Libraries (CDN)

- **p5.js** v1.7.0 - LGPL-2.1 - Creative coding for graphics
- **Tone.js** v14.8.49 - MIT - Web Audio framework for music

### Commit

`0e7bd45` - feat(audio): Add Tone.js browser-based music generation

---

## Session 151 - Edutainment Animations: Environmental Impact Visualization
**Date:** 2026-01-31
**Focus:** Wissenschaftlich fundierte CO2-Visualisierungen für AI-Generierung
**Status:** IN PROGRESS

### Neue Features

**1. IcebergAnimation - Arktis-Eis-Schmelze**
- Zeichne Eisberge, beobachte Schmelzen während GPU arbeitet
- Segelschiff als Fortschrittsanzeige (links→rechts)
- Abschluss-Info: CO2-Menge → cm³ geschmolzenes Arktis-Eis
- Berechnung: 1g CO2 = 6 cm³ Eis (basierend auf Notz & Stroeve 2016)

**2. ForestMiniGame - Interaktives Baumpflanzen**
- Spiel: Pflanze Bäume gegen Fabriken (GPU-Power = Fabrik-Spawn-Rate)
- 7 Baumtypen (Kiefer, Fichte, Tanne, Eiche, Birke, Ahorn, Weide)
- Vogel als Fortschrittsanzeige (Sprite-Animation, Open Source)
- Fabrik auf Baum → Fabrik verschwindet
- Abschluss: Baum-CO2-Absorption (22kg/Jahr = 2.51g/Stunde)

**3. PixelAnimation - GPU-Stats + Smartphone-Vergleich**
- Echtzeit GPU-Werte: Grafikkarte, Energieverbrauch, CO2
- Abschluss: "Du müsstest Dein Handy X Minuten ausschalten"
- Berechnung: 5W Smartphone × 400g CO2/kWh = 30 min pro g CO2

### Wissenschaftliche Grundlagen

| Metrik | Wert | Quelle |
|--------|------|--------|
| Baum CO2-Absorption | 22 kg/Jahr | EPA, Arbor Day Foundation |
| Arktis-Eisverlust | 3 m²/Tonne CO2 | Notz & Stroeve, Science 2016 |
| Eisdicke (Durchschnitt) | ~2m | → 6 m³/Tonne = 6 cm³/g |
| Smartphone Standby | ~5W | Energiestudien |
| Deutscher Strommix | ~400g CO2/kWh | Umweltbundesamt |

### Pädagogische Intention

**Sichtbarmachung unsichtbarer Kosten:**
- Abstrakte Zahlen (Watt, Gramm) → greifbare Metaphern
- Eisschmelze → globale Klimafolgen
- Bäume → lokale Ökosysteme
- Smartphone → persönlicher Alltag

**Handlungsbezug (ForestMiniGame):**
- Aktives Gegenhandeln während Verbrauch läuft
- Spielerische Reflexion: "Kann ich schneller pflanzen?"
- Nicht moralisierend, sondern informierend

### Modified Files

| File | Change |
|------|--------|
| `IcebergAnimation.vue` | Neuer Vergleich (cm³ Eis statt Baum-Stunden) |
| `ForestMiniGame.vue` | Vogel-Animation, Abschluss-Overlay |
| `SpriteProgressAnimation.vue` | GPU-Stats, Smartphone-Vergleich |
| `i18n.ts` | Neue Übersetzungen (iceberg, forest) |
| `ARCHITECTURE PART 15.md` | Design Decision #9 |
| `THIRD_PARTY_CREDITS.md` | Vogel-Sprite Lizenz |

### Integration in MediaOutputBox

**RandomEdutainmentAnimation.vue** - Wrapper-Komponente:
- Wählt zufällig eine der 3 Animationen bei Mount
- Bleibt während gesamter Generation konstant
- Empfängt nur `progress` prop

**Änderung in MediaOutputBox:**
- Ersetzt `SpriteProgressAnimation` durch `RandomEdutainmentAnimation`
- Alle Views die MediaOutputBox nutzen erhalten automatisch die neuen Animationen

### Fixes
- **Fehlende Eis-Zahl:** IcebergAnimation startet jetzt Energy-Tracking automatisch wenn progress > 0
- **Falsche Vergleiche:** ForestMiniGame nutzt jetzt `forest.comparison` (Baum), nicht `iceberg.comparison` (Eis)

### Commits
- `4d70f26` feat(forest): Add bird progress indicator and summary overlay

---

## Session 148 - "Translated" Badge mit SSE-Streaming
**Date:** 2026-01-30
**Focus:** Echtzeit-Badge via SSE wenn Prompt übersetzt wird (vor Bildgenerierung)
**Status:** COMPLETED

### Feature
Neues "Translated" Badge (→ EN) neben dem Safety-Approved Badge. Erscheint in **Echtzeit** nach Stage 3, **bevor** die Bildgenerierung beginnt. Ermöglicht durch SSE-Streaming des `/generation` Endpoints.

### Architektur: SSE für `/generation`

**Problem (ursprünglich):**
- Badge erschien erst nach kompletter Generation (zu spät)
- Safety-Badge wurde mit Fake-300ms-Delay gezeigt (nicht akkurat)

**Lösung:**
- Neuer SSE-Modus für `/generation` Endpoint
- Backend emittiert Events stage-by-stage
- Frontend zeigt Badges sobald `stage3_complete` Event eintrifft

### Backend Änderungen

**`schema_pipeline_routes.py`:**

1. **Neue Generator-Funktion** `execute_generation_streaming()`:
   - Emittiert: `connected`, `stage3_start`, `stage3_complete`, `stage4_start`, `complete`, `error`, `blocked`
   - `stage3_complete` enthält `{safe: bool, was_translated: bool}`

2. **Endpoint erweitert** (`/pipeline/generation`):
   - Unterstützt jetzt GET + POST
   - `enable_streaming=true` → SSE Response
   - Fallback: Original JSON Response

### Frontend Änderungen

**Neuer Composable** `useGenerationStream.ts`:
- Shared SSE-Handler für alle 3 Views
- Exponiert: `showSafetyApprovedStamp`, `showTranslatedStamp`, `generationProgress`, `currentStage`
- Methode: `executeWithStreaming(params)` → Promise\<GenerationResult\>
- Progress-Animation startet bei `stage4_start` Event

**Aktualisierte Views:**
- `text_transformation.vue`
- `image_transformation.vue`
- `multi_image_transformation.vue`

Alle nutzen jetzt den Composable statt lokaler Refs.

### Design-Entscheidungen
- **Icon**: `→ EN` (Pfeil + Text) - neutral, keine politische Konnotation
- **Farbe**: Teal (#009688) - unterscheidet sich von Grün (Safety), Lila (LoRA), Blau (Wikipedia)
- **Timing**: Badges erscheinen nach Stage 3, bevor Stage 4 startet

### Scope

| View | Endpoint | Badge |
|------|----------|-------|
| text_transformation | `/generation` | ✅ SSE |
| image_transformation | `/generation` | ✅ SSE |
| multi_image_transformation | `/generation` | ✅ SSE |
| surrealizer | `/legacy` | ❌ (kein Stage 3) |
| split_and_combine | `/legacy` | ❌ (kein Stage 3) |
| canvas_workflow | eigene Architektur | ❌ (separat) |

### Modified Files
| File | Change |
|------|--------|
| `devserver/my_app/routes/schema_pipeline_routes.py` | SSE-Modus für /generation |
| `public/.../composables/useGenerationStream.ts` | NEU - Shared SSE Composable |
| `public/.../views/text_transformation.vue` | Composable + Icon "→ EN" |
| `public/.../views/text_transformation.css` | `.translated-stamp` Styling |
| `public/.../views/image_transformation.vue` | Composable + Badge |
| `public/.../views/multi_image_transformation.vue` | Composable + Badge |

---

## Session 147 - Documentation Updates: Canvas & Pedagogical Framework
**Date:** 2026-01-29
**Focus:** Vollständige Canvas-Dokumentation, pädagogisches Framework, DokumentationModal-Erweiterungen
**Status:** COMPLETED

### Neue Dokumentation

**ARCHITECTURE PART 26 - Canvas-Workflow-System.md**
- Vollständige technische Dokumentation des Canvas Workflow Systems
- Alle 10 Node-Typen (inkl. neu: Comparison Evaluator)
- Connection Rules, Workflow Execution, Presets
- **Pedagogical Framework**: Lehrforschung, Dekonstruktion des Kontroll-Paradigmas, Prompt Interception, rekursiv-reflexive Workflows
- Zielgruppen, Verhältnis zu anderen Views

### DokumentationModal Änderungen

**Tabs neu organisiert:**
- FAQ-Tab aufgelöst und Inhalte verteilt
- Neue Reihenfolge: Willkommen, Anleitung, Pädagogik, Workshop, Experimente, Canvas

**Neue Inhalte:**
- **Canvas-Tab**: Pädagogisches Framework, Node-Typen mit Stage-Farbcodierung
- **Workshop-Tab**: LLM-Konfiguration (lokal/extern/DSGVO)
- **Pädagogik-Tab**: Prinzip 2 erweitert um "Prompt Interception"
- **Willkommen-Tab**: Datenschutz-Info, Kontakt

**Icons:**
- Canvas-Icon in Navigation: account_tree (korrekter Material Icons Pfad)
- Select-Icon in Anleitung: apps Icon (48px)

### Modified Files
| File | Change |
|------|--------|
| `docs/ARCHITECTURE PART 26 - Canvas-Workflow-System.md` | NEU - Vollständige Canvas-Dokumentation |
| `docs/00_MAIN_DOCUMENTATION_INDEX.md` | Part 26 hinzugefügt |
| `public/.../components/DokumentationModal.vue` | Canvas-Tab, Tab-Reorganisation, Icons |
| `public/.../src/App.vue` | Canvas-Icon (account_tree) |
| `public/.../composables/usePageContext.ts` | Träshy x: 2→8 (ungelöst) |
| `public/.../views/canvas_workflow.vue` | height: 100vh→100% |

---

## Session 144 - Interception Config Revision: Analog Photography 1970s
**Date:** 2026-01-28
**Focus:** Config-Text für detailliertere Objektbeschreibung optimiert
**Status:** COMPLETED

### Änderungstyp: Prompt-Strategie für Wikipedia-Integration

Die Analogfotografie-Config wurde überarbeitet, um die **Objektbeschreibungs-Qualität** zu verbessern - relevant für die neue Wikipedia-Suchfunktion (Session 142/143).

**Kernänderungen:**
1. **Neuer Fokus auf Recherche**: "Du arbeitest sorgfältig und informierst dich sehr genau über Deine Gegenstände. Du beschriebst sie extrem detailliert als fotografische Visualisierung"
2. **Entfernt**: Detaillierte Dunkelkammer-Terminologie (Zonenfokussierung, Push/Pull-Entwicklung, Papiergradwahl etc.) - diese technischen Details sind für die Bildgenerierung weniger relevant als präzise Objektbeschreibungen
3. **Vereinfacht**: Verbotene Sprache auf Kernpunkte reduziert

### Implikation für Config-Revision
Diese Änderung zeigt ein Muster für die Überarbeitung anderer Interception-Configs:
- **Weniger**: Stilistische/technische Detailverliebtheit im Prompt
- **Mehr**: Explizite Anweisung zur genauen Recherche und Beschreibung der Eingabe-Objekte
- **Ziel**: Bessere Wikipedia-Suchbegriffe durch detailliertere Objektnennung im Output

### Modified Files
| File | Change |
|------|--------|
| `devserver/schemas/configs/interception/analog_photography_1970s.json` | `context.de` neu formuliert |

---

## Session 143 - Wikipedia Opensearch API + Transparency
**Date:** 2026-01-28
**Focus:** Fix Wikipedia badge not appearing due to failed lookups
**Status:** COMPLETED

### Problem
Wikipedia badge never appeared because all lookups returned 404:
```
[WIKI] Looking up 'Igbo New Yam Festival' on en.wikipedia.org
[WIKI] Not found: 'Igbo New Yam Festival'
```

**Root Cause:**
- LLM generated search terms (e.g., "Igbo New Yam Festival") that don't match exact Wikipedia article titles
- Backend used direct Page Summary API (`/page/summary/{term}`) which requires exact title
- The actual article exists as "New Yam Festival" but wasn't found

### Solution
**1. Backend: Opensearch API as primary search**

Query construction:
```
https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={term}&limit=1&format=json
```

Response format:
```json
[searchTerm, [titles], [descriptions], [urls]]
["Igbo New Yam", ["New Yam Festival"], ["The New Yam Festival..."], ["https://en.wikipedia.org/wiki/New_Yam_Festival"]]
```

Flow:
1. Opensearch finds best matching article title (fuzzy matching)
2. Page Summary API fetches full content using found title
3. Returns real Wikipedia URL and title

**2. Backend: Send ALL terms (transparency)**
- Removed `if r.success` filter in `pipeline_executor.py`
- All lookup attempts are now sent to frontend
- Frontend knows what was searched, even if not found

**3. Frontend: Visual distinction**
- Found articles: Blue link (clickable)
- Not found: Gray italic text with "(nicht gefunden)"
- Badge shows total count as "N Begriff(e)" instead of "N Artikel"

### Modified Files
| File | Change |
|------|--------|
| `devserver/my_app/services/wikipedia_service.py` | Replaced direct lookup with Opensearch API + Page Summary |
| `devserver/schemas/engine/pipeline_executor.py` | Removed success filter, send all terms |
| `public/.../text_transformation.vue` | Badge shows found/not-found distinction |
| `public/.../text_transformation.css` | Added `.wikipedia-not-found` styling |

### Commits
- `ea9c5cf` - feat(wikipedia): Use Opensearch API for fuzzy matching + show all terms

### Result
- Badge now appears (shows all searched terms)
- Fuzzy matching finds articles even with inexact search terms
- Transparent: User sees what was searched and whether it was found
- Links point to real Wikipedia articles

---

## Session 142 - Wikipedia Badge Position Fix
**Date:** 2026-01-27
**Focus:** Fix disappearing Wikipedia badge by moving to stable UI area
**Status:** COMPLETED

### Problem
Wikipedia badge disappeared after 3 seconds during multiple Wikipedia lookups:
1. First lookup complete: `terms: [{...}]` → Badge appears ✓
2. Second lookup start: `terms: []` → Badge disappears ✗ (SSE event overwrote terms array)
3. Second lookup complete: `terms: [{...}]` → Badge reappears

**Root Cause:**
- Badge positioned in interception section (unstable during SSE streaming)
- `handleWikipediaLookup()` replaced terms array on "start" event: `wikipediaData.value = { active: true, terms: [] }`

### Solution
**Moved badge to stable area** next to Start #1 button:
- No movement during streaming
- Not affected by SSE events
- Visible immediately after first Wikipedia lookup
- Persists during all subsequent lookups

**Fixed data handling:**
- `handleWikipediaLookup()`: Accumulates terms instead of replacing
- `runInterception()`: Full reset only at start of new run

### Modified Files
| File | Change |
|------|--------|
| `public/ai4artsed-frontend/src/views/text_transformation.vue` | Removed badge from interception section (line 83-112); Added badge to Start #1 button container; Fixed handleWikipediaLookup to accumulate terms; wikipediaStatusText shows live status in loading message |

### Commits
- `ab4e37c` - feat(wikipedia): Add status text and dynamic loading message
- `4294bcd` - fix(wikipedia): Move badge to stable area next to Stage 1
- `e1968c0` - fix(wikipedia): Move badge from Start #2 to Start #1

### Result
- Badge appears when first Wikipedia lookup completes
- Badge stays visible during subsequent lookups
- Terms accumulate (e.g., "3 Artikel")
- Badge resets only on new interception run
- Stable position next to Start #1 button

---

## Session 141 - Canvas SSE Streaming for Live Execution Progress
**Date:** 2026-01-27
**Focus:** Real-time progress feedback during canvas workflow execution
**Status:** COMPLETED

### Problem
Users see nothing for 5+ minutes while canvas workflow runs. Terminal shows useful progress info (`[Canvas Tracer] Executing...`) but frontend only updates after everything completes.

### Solution
SSE (Server-Sent Events) streaming endpoint that yields events IMMEDIATELY during execution.

### Key Implementation Detail
**Iterative work-queue instead of recursion** - Critical architectural change:
- Recursive `trace()` function cannot `yield` (nested function limitation)
- Replaced with explicit work-queue loop in generator
- `yield` now happens DIRECTLY in main generator between node executions

### SSE Events
| Event | Data | When |
|-------|------|------|
| `started` | `{total_nodes}` | Execution begins |
| `progress` | `{node_id, node_type, message}` | Before each node |
| `node_complete` | `{node_id, output_preview}` | After each node |
| `complete` | `{results, collectorOutput}` | All done |
| `error` | `{message}` | On failure |

### Modified Files
| File | Change |
|------|--------|
| `devserver/my_app/routes/canvas_routes.py` | New `/api/canvas/execute-stream` endpoint with iterative work-queue |
| `public/ai4artsed-frontend/src/stores/canvas.ts` | `executeWorkflow()` now uses streaming fetch + ReadableStream; added `currentProgress`, `totalNodes`, `completedNodes` refs |
| `public/ai4artsed-frontend/src/views/canvas_workflow.vue` | Progress overlay with spinner, current step message, and node counter |

### Commit
`319313d` - feat(canvas): SSE streaming for live execution progress

---

## Session 136 - Anti-Orientalism Meta-Prompt Enhancement
**Date:** 2026-01-26
**Focus:** Prevent orientalist stereotypes in prompt interception
**Status:** COMPLETED

### Problem
User report: GPT-OSS:120b produced "enormer, furchtbarer exotistischer orientalistischer Kitsch" when processing Nigerian cultural festival prompt. LLM defaulted to orientalist tropes (exotic, mysterious, timeless) despite pedagogical goals.

### Root Cause
Meta-prompt in `instruction_selector.py` lacked explicit anti-stereotype rules. Wikipedia lookup alone insufficient - models need explicit cultural respect principles.

### Solution
Enhanced "transformation" instruction with anti-orientalism rules:
- FORBIDDEN: Exoticizing, romanticizing, mystifying cultural practices
- FORBIDDEN: Orientalist tropes (exotic, mysterious, timeless, ancient wisdom)
- FORBIDDEN: Homogenizing diverse cultures into aesthetic stereotypes
- Equality principle: "Use the same neutral, fact-based approach as for Western contexts"

### Modified Files
| File | Change |
|------|--------|
| `devserver/schemas/engine/instruction_selector.py` | Enhanced "transformation" instruction with CULTURAL RESPECT PRINCIPLES |
| `devserver/schemas/chunks/manipulate.json` | Wikipedia instruction now uses cultural reference language (70+ languages) |
| `devserver/schemas/engine/pipeline_executor.py` | Send REAL Wikipedia results (title, url) to frontend, not just search terms |
| `devserver/my_app/services/wikipedia_service.py` | Expanded SUPPORTED_LANGUAGES from 20 to 70+ (Africa, Asia, Americas, Oceania) |
| `public/ai4artsed-frontend/src/views/text_transformation.vue` | Wikipedia badge uses LoRA design pattern + real URLs; reset on Start button |
| `public/ai4artsed-frontend/src/views/text_transformation.css` | Wikipedia badge reuses lora-stamp classes with color modifier |
| `public/ai4artsed-frontend/src/components/MediaInputBox.vue` | TypeScript types updated for real Wikipedia results |
| `docs/analysis/ORIENTALISM_PROBLEM_2026-01.md` | Complete analysis with test strategy and postcolonial theory references |
| `docs/DEVELOPMENT_DECISIONS.md` | Documented epistemic justice as core architectural principle |

### Key Decisions
1. **Universal application**: Rules apply to ALL configs, not just cultural-specific ones
2. **Explicit FORBIDDEN list**: Concrete examples of prohibited terms
3. **Option A chosen**: Comprehensive instruction (~150 words) for maximum effectiveness
4. **Cultural reference language**: Wikipedia lookup uses cultural context language (not prompt language)
   - **70+ languages** mapped: Africa (15+), Asia (30+), Americas (indigenous languages), Oceania
   - Example: German prompt about Nigeria → uses Hausa/Yoruba/Igbo/English Wikipedia (not German)
   - Example: German prompt about India → uses Hindi/Tamil/Bengali/etc. Wikipedia (not German)
   - Example: German prompt about Peru → uses Spanish/Quechua/Aymara Wikipedia (not German)
   - Rationale: Local Wikipedia communities provide more accurate, less Eurocentric information
5. **No code changes**: Only meta-prompt modifications needed

### Architecture Alignment
- ✅ Supports WAS/WIE principle (anti-stereotype rules are part of "HOW")
- ✅ Reinforces planetarizer/one_world anti-Othering rules
- ✅ Enhances pedagogical goal: visible, criticalizable transformations
- ✅ No conflicts with existing configs

### Testing Status
✅ **PASSED** - Tested with original failing case via `/api/schema/pipeline/stage2`:
- Input: "Das wichtigste Fest im Norden Nigerias" (schema: tellastory)
- Model: GPT-OSS:120b (same as original failing case)
- Result: Factual story about Sallah festival in Kano with:
  - ✅ NO orientalist tropes (exotic, mysterious, timeless)
  - ✅ Specific cultural details (Durbar, Boubou, Kora/Djembe instruments)
  - ✅ Active protagonist (Amina) with agency
  - ✅ Respectful, fact-based tone
- Improvement: From "furchtbarer exotistischer Kitsch" to significantly less orientalist output (though not perfect)

### Theoretical Foundation
Based on postcolonial theory (Said, Fanon, Spivak) - see analysis document for details.

### Additional Fixes (Same Session)

**Wikipedia Badge UI Issues:**
1. **External SVG file caused build errors**
   - Solution: Inline SVG "W" icon (no external file dependency)
2. **Inconsistent design** ("größerer Kasten")
   - Solution: Reuse ALL lora-stamp classes (lora-inner, lora-details, lora-item)
   - Only color modifier: `.wikipedia-lora` for Wikipedia blue (#0066CC)
3. **Badge persisted after Start button**
   - Solution: Reset wikipediaData on runInterception()

**Wikipedia URL Issues:**
1. **Invented links instead of real URLs**
   - Root cause: Backend fetched WikipediaResult but only sent search terms to frontend
   - Solution: Send REAL Wikipedia results (term, lang, title, url, success)
   - Frontend now uses real URLs and displays real article titles
2. **Only 20 languages supported**
   - Root cause: SUPPORTED_LANGUAGES had only 20 codes
   - Solution: Expanded to 70+ languages (ha, yo, ig, qu, ay, mi, etc.)
3. **No debug visibility**
   - Solution: Console logging shows which articles were found with their URLs

**Result:**
- Wikipedia badge matches LoRA badge design exactly
- Links point to REAL Wikipedia articles (no more 404s)
- All 70+ languages now work correctly
- Debug output in console: "Found X Wikipedia articles: lang: title -> url"

### Commits
- `f73bd46` feat(interception): Add anti-orientalism rules and cultural-aware Wikipedia lookup
- `a24fbc0` fix(wikipedia): Use SVG logo and reset data on Start button
- `754b535` docs: Add epistemic justice decision to DEVELOPMENT_DECISIONS.md
- `e929d57` fix(wikipedia): Copy LoRA badge design exactly (inline SVG, shared CSS)
- `4e69051` fix(wikipedia): Use correct language-specific Wikipedia links
- `de32065` fix(wikipedia): Use REAL Wikipedia URLs instead of invented links + 70+ languages

---

## Session 139 - Wikipedia Research Capability
**Date:** 2026-01-26
**Focus:** Enable LLM to fetch Wikipedia content during prompt interception
**Status:** COMPLETED

### Feature Overview
LLM can now request Wikipedia content using `<wiki>term</wiki>` markers in its output. System fetches content and re-executes chunk with enriched context.

### Architecture
- **Chunk-Level Orchestration**: Wikipedia loop in `pipeline_executor._execute_single_step()`
- **NOT a new pipeline** - fundamental capability of ALL interceptions
- **Max 3 iterations** per chunk execution (configurable)

### New Files
| File | Purpose |
|------|---------|
| `my_app/services/wikipedia_service.py` | Secure Wikipedia API client (whitelist-only) |
| `schemas/engine/wikipedia_processor.py` | Marker extraction, content formatting |

### Modified Files
| File | Change |
|------|--------|
| `config.py` | `WIKIPEDIA_MAX_ITERATIONS`, `WIKIPEDIA_FALLBACK_LANGUAGE`, `WIKIPEDIA_CACHE_TTL` |
| `schemas/chunks/manipulate.json` | `{{WIKIPEDIA_CONTEXT}}` placeholder, instruction text |
| `schemas/engine/pipeline_executor.py` | Wikipedia loop, `WIKIPEDIA_STATUS` global for UI |
| `my_app/routes/schema_pipeline_routes.py` | Refactored to use `pipeline_executor` (fixes architecture violation), SSE `wikipedia_lookup` events |
| `MediaInputBox.vue` | Pulsing Wikipedia logo during lookup |

### Trigger Pattern
```
<wiki lang="de">Suchbegriff</wiki>  - German Wikipedia
<wiki lang="en">Search term</wiki>  - English Wikipedia
<wiki>term</wiki>                    - Uses input language
```

### Key Decisions
1. **Language auto-detection**: Uses input language, falls back to `WIKIPEDIA_FALLBACK_LANGUAGE`
2. **Session per-request**: aiohttp session created/closed per lookup (avoids event loop issues with threading)
3. **Architecture fix**: SSE route now uses `pipeline_executor` instead of direct `PromptInterceptionEngine` call

### Commits
- `d66c37f` feat(wikipedia): Core implementation
- `b617273` fix(wikipedia): Import paths
- `277dbf7` fix(wikipedia): Stronger prompt (MUST use when needed)
- `8e03431` feat(wikipedia): Real-time UI feedback
- `761cffa` fix(wikipedia): Session per-request (event loop fix)

---

## Session 138 - Trashy Context-Awareness Fix
**Date:** 2026-01-26
**Focus:** Fix Trashy losing context after pipeline execution
**Status:** COMPLETED

### Problem
Träshy (AI chat helper) was "forgetting" current page context after a pipeline run:

**Root Cause Chain:**
1. User runs pipeline → `runId` gets set via `updateSession()`
2. User changes MediaInputBox content → `runId` stays set (no `clearSession()` call)
3. User opens Träshy → ChatOverlay sees `runId` exists
4. ChatOverlay sends draft_context ONLY if `!runId` (Zeile 213)
5. Backend loads **stale** session context from `exports/json/{runId}/`
6. Träshy doesn't know about current input changes

**Confirmed:** No Vue view calls `clearSession()` → `runId` persists until browser refresh

### Solution: Always Send Draft Context

**Option B (chosen):** Send `draft_context` as separate field, backend combines both contexts.

**Frontend (`ChatOverlay.vue`):**
```javascript
// BEFORE: Conditional logic
if (!currentSession.value.runId && draftContextString.value) {
  messageForBackend = `${draftContextString.value}\n\n${userMessage}`
}

// AFTER: Always send as separate field
const response = await axios.post('/api/chat', {
  message: userMessage,  // Clean message
  run_id: currentSession.value.runId || undefined,
  draft_context: draftContextString.value || undefined,  // NEW: Always send
  history: historyForBackend
})
```

**Backend (`chat_routes.py`):**
```python
draft_context = data.get('draft_context')  # Current page state (transient)

system_prompt = build_system_prompt(context)  # Session context from files

# Append draft_context if provided (NOT saved to exports/)
if draft_context:
    system_prompt += f"\n\n[Aktuelle Eingaben auf der Seite]\n{draft_context}"
```

### Key Points

- `draft_context` is **transient** (LLM context only, not persisted)
- NOT saved to `chat_history.json` or `exports/json/`
- Backend now knows BOTH: session files + current page state
- No changes to exports system

### Result

**Before:**
- Without runId: draft_context sent ✓
- With runId: draft_context ignored ✗

**After:**
- Without runId: draft_context in system prompt ✓
- With runId: BOTH session + draft_context in system prompt ✓

**Commit:** `1fee080` - fix(trashy): Always send draft_context for context-aware chat

---

## Session 137 - Stage 3/4 Separation (Clean Architecture)
**Date:** 2026-01-26
**Focus:** Separate Stage 3 (Translation+Safety) from Stage 4 (Generation) for clean architecture
**Status:** COMPLETED

### Problem
`execute_generation_stage4()` contained **embedded Stage 3 logic**, forcing Canvas to use `skip_translation=True` workaround when it had its own Translation node.

**Old Architecture (problematic):**
```
Canvas: Translation Node → Generation Node (skip_translation=True) → Media
Lab:    execute_generation_stage4() → [Stage 3 embedded] → Stage 4 → Media
```

**Bug Found:** Parameter was `skip_stage3` but code used undefined `skip_translation` variable.

### Solution
Created clean separation with new function `execute_stage4_generation_only()`:

**New Architecture:**
```
Canvas: Translation Node → execute_stage4_generation_only() → Media
Lab:    execute_generation_stage4() → Stage 3 → execute_stage4_generation_only() → Media
```

### Changes

| File | Change |
|------|--------|
| `schema_pipeline_routes.py` | Added `execute_stage4_generation_only()` - pure Stage 4 generation |
| `schema_pipeline_routes.py` | Refactored `execute_generation_stage4()` to call new function internally |
| `canvas_routes.py` | Generation node now calls `execute_stage4_generation_only()` directly |
| `canvas_routes.py` | Removed `skip_translation=True` workaround |

### Key Principle
- `execute_stage4_generation_only()` = Pure generation, expects ready-to-use prompt
- `execute_generation_stage4()` = Legacy wrapper for Lab (handles Stage 3 first)
- Canvas workflows call the clean function directly - no flags needed

**Commit:** `9f34ca2` - refactor(stage4): Separate Stage 3 and Stage 4 for clean architecture

---

## Session 135 - Canvas Cosmetic Fixes & Live Data Flow
**Date:** 2026-01-26
**Focus:** UI polish for Canvas workflow builder + live execution visualization
**Status:** COMPLETED

### Part 1: Initial Fixes

**1. Connection Lines (Initial Attempt - DOM-based)**
- Problem: Lines started from wrong positions (calculated widths didn't match CSS)
- Initial solution: Query DOM positions using `data-node-id` and `data-connector` attributes
- Issue: Vue computed properties don't track DOM changes reactively

**2. Preview/Display Node**
- Made resizable (like Collector)
- Removed 150-char text truncation

**3. Collector Node**
- Removed 200-char text truncation
- Full text display with scrolling

**4. Media Type Icons**
- Google Material icons for Generation node config selection
- Icons based on `mediaType`: image, video, audio/music, text

### Part 2: Connection Line Refactor (Data-Based)

**Problem:** DOM-based approach had timing issues - computed properties run before DOM updates.

**Solution:** Pure data-based connector positioning:
```typescript
const HEADER_CONNECTOR_Y = 24  // Fixed offset from top

function getConnectorPosition(node, connectorType) {
  const width = getNodeWidth(node)  // 280px wide, 180px narrow
  if (connectorType === 'input') {
    return { x: node.x, y: node.y + HEADER_CONNECTOR_Y }
  }
  return { x: node.x + width, y: node.y + HEADER_CONNECTOR_Y }
}
```

**Key insight:** Connectors in HEADER area (fixed Y=24px) don't move when nodes resize.

### Part 3: Evaluation Metadata in Collector

**Problem:** Evaluation score/binary not showing in Collector.

**Solution:** Backend now wraps evaluation output with metadata:
```python
if source_node_type == 'evaluation' and source_metadata:
    collector_item['output'] = {
        'text': input_data,
        'metadata': source_metadata  # { score, binary, active_path }
    }
```

Frontend displays: `Score: 7/10 ✓ Pass`

### Part 4: Output Bubbles (Live Data Flow)

**Feature:** Every node shows a temporary bubble when it produces output.

- Blue speech bubble appears near output connector
- Shows truncated content (60 chars text, icons for media, score for evaluation)
- Animated appearance with scale/fade effect
- Excluded from terminal nodes (collector, display)

### Files Changed

| File | Change |
|------|--------|
| `CanvasWorkspace.vue` | Pure data-based connector positions, node width by type |
| `StageModule.vue` | Header connector CSS (top: 24px), output bubbles, evaluation display |
| `ConfigSelectorModal.vue` | Media type icons |
| `canvas_workflow.vue` | Pass outputConfigs prop |
| `canvas_routes.py` | Evaluation metadata in collector items |

### Commits

- `a4219c2` - feat(canvas): Session 135 - Cosmetic fixes and media type icons
- `b9b692a` - fix(canvas): Data-based connector positioning with header alignment
- `f770405` - fix(canvas): Evaluation metadata handling and display improvements
- `3c58672` - feat(canvas): Output bubbles show data flowing through nodes

---

## Session 134 - Canvas Decision & Evaluation Nodes (Unified Architecture)
**Date:** 2026-01-25 → 2026-01-26
**Focus:** Implement evaluation nodes with 3-output branching logic + Tracer-Pattern execution
**Status:** COMPLETED (Phase 1-4) - Reflexiv agierendes Frontend für genAI

### Pädagogisches Konzept: Evaluation als bewusste Entscheidung

**Kernidee:** Evaluation = EINE konzeptionelle Entscheidung mit 3 Text-Outputs, nicht 7 separate Node-Typen.

**Warum 3 Outputs?**
1. **Passthrough (P)** - Evaluation bestanden → unverändert weiter
2. **Commented (C)** - Evaluation nicht bestanden → mit Feedback zurück
3. **Commentary (→)** - Immer → für User-Transparenz/Display

**Pädagogischer Vorteil:**
- Explizite Entscheidungspunkte im Workflow
- Sichtbares Feedback (nicht "black box")
- Ermöglicht iterative Verbesserung (Feedback Loops)

### Architekturentscheidung: Von 7 Nodes → 1 Node

**Ursprünglicher Plan (verworfen):**
- 5 Evaluation-Types (fairness, creativity, equity, quality, custom)
- 2 Fork-Types (binary_fork, threshold_fork)
= 7 separate Node-Typen

**Problem (User Feedback):**
- Evaluation + Fork = konzeptuell EINE Entscheidung, nicht zwei
- Datenfluss unklar: Was fließt durch Fork? Input? Commentary? Beides?
- UI-Komplexität: 7 Nodes für eine logische Operation

**Lösung: Unified Evaluation Node**
- 1 Node-Typ mit Dropdown für Evaluation-Type
- Optional branching (Checkbox)
- 3 separate TEXT-Outputs (nicht kombiniertes Objekt)

### Implementation - Phase 1: Evaluation Nodes (COMPLETED)

**Frontend (canvas.ts):**
- Node-Type: `'evaluation'`
- Properties: `evaluationType`, `evaluationPrompt`, `outputType`, `enableBranching`, `branchCondition`, `thresholdValue`, `trueLabel`, `falseLabel`

**UI (StageModule.vue):**
```vue
Evaluation Type: [Fairness ▼] (fairness, creativity, equity, quality, custom)
LLM: [gpt-4o-mini ▼]
Criteria: [Textarea mit Pre-fill Templates]
Output: [Commentary+Score ▼]
☑ Enable Branching
  Condition: [Binary/Threshold]
  Threshold: [5.0] (if threshold selected)
  True Label: [Approved]
  False Label: [Needs Revision]
```

**Backend (canvas_routes.py):**
```python
# 3 separate TEXT outputs
outputs = {
  'passthrough': input_text,  # Original unchanged
  'commented': f"{input_text}\n\nFEEDBACK: {commentary}",  # Input + feedback
  'commentary': commentary  # Just commentary
}
metadata = {
  'binary': True/False,
  'score': 0-10,
  'active_path': 'passthrough' | 'commented'
}
```

**Binary Logic (Fixed):**
- LLM-Prompt: "Answer ONLY 'true' or 'false'. If issues or score < 5, answer 'false'"
- Fallback: No binary → use score threshold (< 5.0 = fail)
- Smart parsing: Case-insensitive, multiple variations (true/yes/pass/bestanden)

### Implementation - Phase 2: Display → Preview Node (COMPLETED)

**Problem:** Display-Node zeigte nichts an, hatte nutzloses Dropdown.

**Lösung:** Umbenennung + Inline-Preview
- Label: "Display" → "Preview/Vorschau"
- Removed: title input, displayMode dropdown
- Added: Inline content visualization
  - Text: First 150 chars
  - Images: Inline preview (max 150px)
  - Media: Type + URL display

**UI:**
```
┌──────────────┐
│ 🔍 PREVIEW   │
├──────────────┤
│ [Content...] │ ← Shows execution result
│ [truncated]  │
└──────────────┘
```

### Implementation - Phase 3a: UI for Branching (COMPLETED)

**3 Output Connectors:**
```
┌────────────────┐
│ 📋 EVALUATION  │
└────────────────┘
       ├─ P (🟢 green - Passthrough)
       ├─ C (🟠 orange - Commented)
       └─ → (🔵 cyan - Commentary)
```

**Connection Labels:** `'passthrough'`, `'commented'`, `'commentary'`

**Collector Display:**
- Shows: Binary (✅/❌), Score, Active Path, Commentary, Output Text
- Separate sections for metadata vs. outputs

### Connection Rules (Fixed Multiple Times)

**Problem:** Nodes couldn't connect (e.g., Input → Evaluation).

**Solution:** Extended `acceptsFrom` and `outputsTo` for all nodes:
- Input → can output to: interception, translation, evaluation, display
- Evaluation → accepts from: input, interception, translation, generation, display, evaluation
- All nodes → can connect to evaluation/display

### Technical Debt & Next Steps

**Phase 3b: Conditional Execution (IMPLEMENTED)**
- Connection labels track active path ('passthrough', 'commented', 'commentary', 'feedback')
- Tracer filters connections based on `active_path` metadata
- Only active path executes downstream (commentary always active)

**Phase 4: Feedback Loops (IMPLEMENTED - Tracer Pattern)**

*Ursprünglicher Plan (verworfen):*
- Loop Controller Node + Kahn's Algorithm
- "Scheinlösung" - über-engineered

*Implementierte Lösung:*
- **Tracer Pattern**: Simples rekursives Graph-Tracing
- Feedback-Input-Connector an Interception/Translation Nodes
- Feedback-Connections mit Label `'feedback'`
- Safety-Limit: MAX_TOTAL_EXECUTIONS = 50
- Kein separater Loop Controller Node nötig

*Design Decision:*
> "Wir haben hier keine unkontrollierte Schleifen-Situation im Graph, sondern nichts anderes als eine Loop-End-Konstellation."

Das System ist ein **reflexiv agierendes Frontend für genAI**:
```
Input → Interception → Evaluation → [Score < 5?]
                            ↓ feedback     ↓ pass
                       Interception    Collector
```

### Files Changed

| File | Change |
|------|--------|
| `public/.../types/canvas.ts` | Unified evaluation type, 3-output structure, connection labels, maxFeedbackIterations |
| `public/.../stores/canvas.ts` | Connection label handling, feedback completion functions |
| `public/.../StageModule.vue` | Evaluation UI, 3 connectors, Feedback-Input connector, Preview inline display |
| `public/.../CanvasWorkspace.vue` | Feedback connection handling, event forwarding |
| `public/.../canvas_workflow.vue` | Handler functions for evaluation config |
| `public/.../ModulePalette.vue` | Removed 7 nodes → 1 evaluation node |
| `devserver/.../canvas_routes.py` | **Complete rewrite**: Tracer pattern statt Kahn's Algorithm |

### Commits

1. `feat(session-134): Add Evaluation node types (Phase 1)` - Initial 5 evaluation types
2. `feat(session-134): Add Display node (Phase 2)` - Display node with config
3. `feat(session-134): Add Fork node UI (Phase 3a)` - Binary/Threshold fork UI
4. `fix(session-134): Add new node types to Palette menu` - Palette integration
5. `fix(session-134): Fix connections and enforce binary output` - Binary always enabled
6. `refactor(session-134): Unified Evaluation node (Option A)` - 7 nodes → 1 node
7. `fix(session-134): Enable all nodes to connect to evaluation/display` - Connection rules
8. `feat(session-134): 3 separate TEXT outputs for Evaluation nodes` - 3-output architecture
9. `fix(session-134): Improve binary evaluation logic` - Score threshold fallback
10. `refactor(session-134): Display → Preview with inline content display` - Preview node
11. `fix(session-134): Score-based override for binary evaluation` - Score fallback
12. `refactor(session-134): Simplify evaluation to score-only logic` - Clean score logic
13. `feat(session-134): Phase 3b - Conditional execution for evaluation nodes` - Path filtering
14. `feat(session-134): Phase 4 - Loop Controller with feedback iterations` - Tracer pattern
15. `fix(session-134): TypeScript errors in Phase 4 Loop Controller` - Type fixes

### Testing Results

✅ **Working:**
- Evaluation node with LLM selection
- Type-specific prompt templates (fairness, creativity, equity, quality, custom)
- Binary + Score + Commentary output
- 3 output connectors (P, C, →)
- Preview shows inline content
- Collector displays evaluation results with metadata
- Conditional execution (only active path executes)
- Feedback loops (Evaluation → Interception)
- Safety limit prevents infinite loops

⚠️ **Known Issues (fixed):**
- Binary logic fallback bug → Score-based override
- Conditional execution → Tracer pattern with path filtering

### Architecture Documentation

See: `docs/ARCHITECTURE_CANVAS_EVALUATION_NODES.md` (created this session)

---

## Session 136 - Träshy UX Enhancement: Living Assistant Interface
**Date:** 2026-01-25
**Focus:** Transform Träshy from static icon to living, context-aware assistant
**Status:** COMPLETED

### Pädagogisches Konzept

Träshy ist nicht nur ein Chat-Button, sondern ein **aktiver Begleiter** im kreativen Prozess:
- **Präsenz**: Immer sichtbar, aber nicht störend
- **Aufmerksamkeit**: Folgt dem Fokus des Users (welches Feld aktiv ist)
- **Lebendigkeit**: Sanfte Animationen signalisieren "Ich bin da und bereit zu helfen"
- **Kontext-Bewusstsein**: Weiß was der User gerade tut (Page Context + Focus Tracking)

### Features implementiert

#### 1. Dynamische Positionierung (Y-Achse)
- Träshy folgt dem fokussierten Eingabefeld
- Position berechnet aus `element.getBoundingClientRect()`
- Viewport-Clamping: Bleibt immer sichtbar (nie über oberen/unteren Rand)

#### 2. Focus-Tracking
- `@focus` Events in MediaInputBox
- `focusedField` State: 'input' | 'context' | 'interception' | 'optimization'
- Sofortige Reaktion auf Feldwechsel

#### 3. Pinia Store statt provide/inject
- Problem: ChatOverlay ist Sibling von router-view, nicht Child
- Lösung: `pageContextStore` für komponentenübergreifende Kommunikation
- Views schreiben via `watch()`, ChatOverlay liest

#### 4. Lebendige Animationen
- **Idle-Schweben**: `trashy-idle` (4s) - translate + rotate
- **Atmen**: `trashy-breathe` (3s) - subtle scale pulse
- **Bewegung**: cubic-bezier mit Überschwingen für organisches Gefühl
- Hover pausiert Animation (präzises Klicken)

#### 5. Chat-Fenster Verbesserungen
- Öffnet nach links/unten statt nach oben
- Viewport-Clamping beim Öffnen
- Auto-Focus auf Input nach Antwort

### Technische Änderungen

| Datei | Änderung |
|-------|----------|
| `src/stores/pageContext.ts` | **NEU** - Pinia Store für Page Context |
| `src/composables/usePageContext.ts` | FocusHint Interface hinzugefügt |
| `src/components/ChatOverlay.vue` | Dynamische Positionierung + Animationen |
| `src/components/MediaInputBox.vue` | @focus Event hinzugefügt |
| `src/views/text_transformation.vue` | Focus-Tracking + Element-Refs |
| `src/assets/base.css` | CSS Custom Properties für Layout |

### CSS Custom Properties (base.css)
```css
--footer-collapsed-height: 36px;
--funding-logo-width: 126px;
--layout-gap-small: 8px;
```

### Commits
- `8bb0f96` fix(ui): Remove lightbulb context indicator
- `7f34bfd` feat(ui): Floating Träshy - smooth position transitions
- `a1169c0` fix(ui): Use Pinia store instead of provide/inject
- `1a11637` feat(ui): Dynamic positioning based on element positions
- `54be78d` feat(ui): Träshy follows focused field
- `ed67488` feat(ui): Träshy follows optimization section
- `78c9725` fix(ui): Top positioning when expanded
- `000d8f0` fix(ui): Clamp position to stay within viewport
- `1de7d4e` refactor(css): CSS custom properties for layout
- `bc65f2c` feat(ui): Idle animation - living assistant

---

## Session 135 - Prompt Optimization META-Instruction Fix
**Date:** 2026-01-24
**Focus:** Fix prompt_optimization breaking on certain models
**Status:** COMPLETED

### Problem
The `prompt_optimization` chunk was failing with certain LLM models because the META-instruction was too complex and model-specific variations weren't working consistently.

### Solution
Simplified the META-instruction in `prompt_optimization` to be more universal and less dependent on model-specific quirks.

### Files Changed
- `devserver/my_app/config/chunks/prompt_optimization.json` - Simplified META-instruction

### Commits
- `1261c4a` fix(session-135): Simplify prompt_optimization META-instruction

---

## Session 134 - GPU Auto-Detection & Analog Photography Fixes
**Date:** 2026-01-24
**Focus:** Settings UI improvements, config fixes, instruction injection architecture
**Status:** COMPLETED

### Features
1. **GPU Auto-Detection in Settings UI** - Automatically detects available GPUs
2. **Analog Photography Config Fixes** - Fixed typos in interception configs
3. **Model Evaluation Criteria** - Documented proper evaluation methodology
4. **Instruction Injection Architecture** - Refactored HARDWARE_MATRIX handling

### Files Changed
- `public/ai4artsed-frontend/src/views/SettingsView.vue` - GPU auto-detection
- `devserver/my_app/config/interception_configs/*.json` - Typo fixes
- `docs/HANDOVER_ModelEvaluation_Criteria.md` - Evaluation methodology

### Commits
- `cea6685` feat(session-134): Add GPU auto-detection to Settings UI
- `12a59bf` fix(session-134): Analog photography config typos + evaluation criteria
- `e50bcc7` fix(session-134): Instruction injection architecture + HARDWARE_MATRIX

---

## Session 133 - Träshy Page Context & Canvas Node Improvements
**Date:** 2026-01-24
**Focus:** Chat assistant context awareness, Canvas workflow enhancements
**Status:** COMPLETED

### Major Features

#### 1. Träshy Page Context (provide/inject Pattern)
Träshy (chat assistant) now knows the current page state even before pipeline execution:
- **Composable**: `usePageContext.ts` with `PageContext` interface and `formatPageContextForLLM()` helper
- **Injection Key**: `PAGE_CONTEXT_KEY` for type-safe provide/inject
- **8 Views Updated**: All major views now provide their page context

**Implementation Pattern:**
```typescript
// In views (e.g., text_transformation.vue)
const pageContext = computed(() => ({
  activeViewType: 'text_transformation',
  pageContent: {
    inputText: inputText.value,
    contextPrompt: contextPrompt.value,
    selectedCategory: selectedCategory.value,
    selectedConfig: selectedConfig.value
  }
}))
provide(PAGE_CONTEXT_KEY, pageContext)

// In ChatOverlay.vue
const pageContext = inject(PAGE_CONTEXT_KEY, null)
const draftContextString = computed(() => formatPageContextForLLM(pageContext?.value, route.path))
```

**Priority Logic:**
1. Session context (run_id files) - highest priority
2. Draft page context (from provide/inject) - if no session
3. Route-only fallback - minimal context

#### 2. Canvas Workflow Improvements
- **Collector Node** - Now accepts text from LLM nodes
- **Input Node** - Now accepts prompt text input
- **LLM Endpoint** - Curated model selection for canvas nodes

#### 3. Additional Fixes
- **Ollama Models Dropdown** - `/api/settings/ollama-models` endpoint + `<datalist>` in SettingsView
- **Model Name Trimming** - `.strip()` in chat_routes.py prevents whitespace issues
- **Log String Cleanup** - "STAGE1-GPT-OSS" → "STAGE1-SAFETY", "gpt-oss:" → "llm:"

### Files Changed
- 📝 `src/composables/usePageContext.ts` - **NEW** - Type definitions & formatting
- 📝 `src/components/ChatOverlay.vue` - inject() + context-prepending
- 📝 `src/views/text_transformation.vue` - provide(PAGE_CONTEXT_KEY)
- 📝 `src/views/image_transformation.vue` - provide(PAGE_CONTEXT_KEY)
- 📝 `src/views/canvas_workflow.vue` - provide(PAGE_CONTEXT_KEY)
- 📝 `src/views/direct.vue` - provide(PAGE_CONTEXT_KEY)
- 📝 `src/views/surrealizer.vue` - provide(PAGE_CONTEXT_KEY)
- 📝 `src/views/multi_image_transformation.vue` - provide(PAGE_CONTEXT_KEY)
- 📝 `src/views/partial_elimination.vue` - provide(PAGE_CONTEXT_KEY)
- 📝 `src/views/split_and_combine.vue` - provide(PAGE_CONTEXT_KEY)
- 📝 `devserver/my_app/routes/settings_routes.py` - Ollama models endpoint
- 📝 `devserver/my_app/routes/chat_routes.py` - Model name trimming

### Commits
- `833428b` forgotten commits (includes all page context changes)
- `5221b36` feat(session-133): Collector accepts text from LLM nodes
- `26e1f4a` feat(session-133): Input node accepts prompt text
- `9bda8e5` fix(session-133): LLM endpoint with curated model selection

---

## Session 130 - Research Data Architecture: 1 Run = 1 Media Output
**Date:** 2026-01-23
**Duration:** ~3 hours
**Focus:** Clean folder structure for research data, immediate prompt persistence
**Status:** PARTIAL - Core features working, sticky UI TODO

### Goals
1. Implement "1 Run = 1 Media Output" principle
2. Save prompts immediately after LLM generation (not only on user action)
3. Stop logging changes after media generation (run is complete)

### Key Principle: 1 Run = 1 Media Output
Each run folder should contain exactly ONE media product. This prevents:
- Favorites system confusion (multiple images in same folder)
- Research data mixing (different generation contexts in same folder)

**Folder Logic:**
```
Interception (Start1)     → run_001/ created
Generate (FIRST)          → run_001/ continues (no output yet)
Generate (SECOND)         → run_002/ NEW (run_001 has output_*)
Generate (THIRD)          → run_003/ NEW
```

### Implementation

**1. Generation Endpoint - Output Check (`schema_pipeline_routes.py:2038-2066`)**
```python
has_output = any(
    e.get('type', '').startswith('output_')
    for e in existing_recorder.metadata.get('entities', [])
)
if has_output:
    run_id = new_run_id()  # NEW folder
else:
    run_id = provided_run_id  # CONTINUE existing
```

**2. Immediate Prompt Persistence (`schema_pipeline_routes.py:1584-1660`)**
- Optimization streaming now loads recorder at START (same pattern as interception)
- Saves `optimized_prompt` immediately after LLM generation
- Frontend passes `run_id` and `device_id` to optimization endpoint

**3. Stop Logging After Generation (TODO - not working yet)**
- Added `currentRunHasOutput` flag in frontend
- Set to `true` after successful generation
- `logPromptChange()` should skip if flag is true
- Reset on new interception

### Files Changed
- 📝 `devserver/my_app/routes/schema_pipeline_routes.py`
  - Generation endpoint: has_output check for new folder
  - Optimization streaming: recorder at start, immediate save
  - Optimize endpoint: run_id/device_id parameters
- 📝 `public/ai4artsed-frontend/src/views/text_transformation.vue`
  - `optimizationStreamingParams`: added run_id, device_id
  - `currentRunHasOutput` flag (TODO: not working)
  - `logPromptChange()`: skip if run has output

### TODO
- [ ] Fix `currentRunHasOutput` flag not preventing logging after generation
- [ ] Implement "sticky" UI: restore prompts/image when switching modes

### Commits
- `bed0c2c` feat(session-130): 1 Run = 1 Media Output
- `8d07c33` feat(session-130): Save optimized_prompt immediately after LLM generation

---

## Session 117 - LoRA Strength Tuning for Interception Configs
**Date:** 2026-01-17
**Duration:** ~30 minutes
**Focus:** Finding optimal LoRA strength for prompt/style balance
**Status:** SUCCESS - Strength calibrated

### Problem
LoRA injection was working (since Session 114/116), but at strength 1.0 the LoRA effect completely overrode the user's prompt content. Generated images showed only the LoRA style (e.g., film artifacts for Cooked Negatives) with no relevance to the actual prompt.

### Investigation
Compared generations with "Cooked Negatives" interception config:
- **Strength 1.0:** Full film artifact effect, but prompt completely ignored
- **Strength 0.5:** Effect barely visible
- **Strength 0.6:** Good balance - film artifacts visible AND prompt content preserved

### Solution
Adjusted LoRA strength in interception config:
```json
{
  "meta": {
    "loras": [
      {"name": "sd3.5-large_cooked_negatives.safetensors", "strength": 0.6}
    ]
  }
}
```

### Key Insight
**LoRA Strength Trade-off:**
- High strength (0.8-1.0): Style dominates, prompt ignored
- Low strength (0.3-0.5): Style barely visible
- Sweet spot (0.5-0.7): Balance between style and prompt adherence

This varies per LoRA - some are stronger than others. Each interception config should test and calibrate its LoRA strength individually.

### Files Changed
- 📝 `devserver/schemas/configs/interception/cooked_negatives.json` (strength: 1.0 → 0.6)

---

## Session 114 - LoRA Injection for Stage 4 Workflows
**Date:** 2026-01-11
**Duration:** ~2 hours
**Focus:** Dynamic LoRA injection into ComfyUI workflows
**Status:** SUCCESS - LoRA injection working

### Goal
Enable LoRA models (e.g., face LoRAs, style LoRAs) to be automatically injected into Stage 4 image generation workflows.

### Background
Previous Cline session attempted "Dual-Parse" architecture (parsing `<lora:name:strength>` tags from prompts) but failed due to architectural issues. This session took a simpler approach: implement the injection mechanism first, decide WHERE the LoRA list comes from later.

### Solution: Workflow-Based LoRA Injection

**Key Insight:** Separate the injection mechanism from the data source.
1. Define LoRA list in `config.py` (temporary hardcoded)
2. Inject LoRALoader nodes into workflow at runtime
3. Later: connect to Stage2-Configs (Meta-Prompt + optimal LoRAs)

### Implementation

#### 1. Config (`config.py`)
```python
LORA_TRIGGERS = [
    {"name": "SD3.5-Large-Anime-LoRA.safetensors", "strength": 1.0},
    {"name": "bejo_face.safetensors", "strength": 1.0},
]
```

#### 2. Injection Logic (`backend_router.py`)
New method `_inject_lora_nodes()`:
- Finds CheckpointLoaderSimple node (model source)
- Finds model consumers (KSampler)
- Inserts LoRALoader nodes in chain: Checkpoint → LoRA1 → LoRA2 → KSampler
- Updates node connections automatically

#### 3. Routing Change
When `LORA_TRIGGERS` is configured, images use workflow mode instead of simple SwarmUI API:
```python
if LORA_TRIGGERS:
    return await self._process_workflow_chunk(...)
else:
    return await self._process_image_chunk_simple(...)
```

### Log Output (Success)
```
[LORA] Using workflow mode for image generation (LoRAs configured)
[LORA] Injected LoraLoader node 12: SD3.5-Large-Anime-LoRA.safetensors
[LORA] Injected LoraLoader node 13: bejo_face.safetensors
[LORA] Updated node 8 to receive model from LoRA chain
```

### Test Results
- ✅ Face LoRA (bejo_face) visible in output - works WITHOUT trigger word
- ✅ Multiple LoRAs chain correctly
- ✅ Workflow submission successful
- ⚠️ Style LoRA may need trigger word in prompt for visible effect

### Next Steps
**Connect to Stage2-Configs:** Each interception config (Meta-Prompt) can define optimal LoRAs:
```json
{
  "name": "jugendsprache",
  "context_prompt": "...",
  "loras": [
    {"name": "anime_style.safetensors", "strength": 0.8}
  ]
}
```

### Files Changed
- 📝 `devserver/config.py` (+10 lines - LORA_TRIGGERS config)
- 🔧 `devserver/schemas/engine/backend_router.py` (+80 lines - injection logic)

---

## Session 113 - SwarmUI Auto-Recovery System
**Date:** 2026-01-11
**Duration:** ~2 hours
**Focus:** Automatic SwarmUI lifecycle management
**Status:** SUCCESS - Full auto-recovery implemented

### Problem
DevServer crashed when SwarmUI was not running:
```
ClientConnectorError: Cannot connect to host 127.0.0.1:7821
```
**User Requirement:** DevServer should automatically detect and start SwarmUI when needed.

### Solution: SwarmUI Manager Service
Created new singleton service `swarmui_manager.py` for lifecycle management:

**Architecture Pattern:** Lazy Recovery (On-Demand)
- SwarmUI starts **only when needed** (not at DevServer startup)
- Handles both startup scenarios AND runtime crashes
- Faster DevServer startup
- Race-condition safe with `asyncio.Lock`

### Implementation

#### 1. SwarmUI Manager Service (`devserver/my_app/services/swarmui_manager.py`)
**Core Methods:**
- `ensure_swarmui_available()` - Main entry point, guarantees SwarmUI is running
- `is_healthy()` - Checks both ports (7801 REST API + 7821 ComfyUI backend)
- `_start_swarmui()` - Executes `2_start_swarmui.sh` via subprocess.Popen
- `_wait_for_ready()` - Polls health endpoints until ready or timeout (120s)

**Concurrency Safety:**
- `asyncio.Lock` prevents multiple threads from starting SwarmUI simultaneously
- Double-check pattern after acquiring lock

#### 2. Integration Points (5 locations)
**LegacyWorkflowService** (`legacy_workflow_service.py:95`):
- `ensure_swarmui_available()` before workflow submission

**BackendRouter** (`backend_router.py`):
- Line 150: Manager initialization in constructor
- Line 550: Before SwarmUI Text2Image generation
- Line 684: Before SwarmUI workflow submission
- Line 893: Before single image upload
- Line 941: Before multi-image upload

#### 3. Configuration (`config.py`)
```python
SWARMUI_AUTO_START = os.environ.get("SWARMUI_AUTO_START", "true").lower() == "true"
SWARMUI_STARTUP_TIMEOUT = int(os.environ.get("SWARMUI_STARTUP_TIMEOUT", "120"))  # seconds
SWARMUI_HEALTH_CHECK_INTERVAL = float(os.environ.get("SWARMUI_HEALTH_CHECK_INTERVAL", "2.0"))  # seconds
```

#### 4. Browser Tab Prevention
**Problem:** SwarmUI opened browser tab on startup, hiding the frontend.

**Solution:** Command-line override in `2_start_swarmui.sh`:
```bash
./launch-linux.sh --launch_mode none
```

**Why This Works:**
- SwarmUI supports `--launch_mode` command-line argument
- Overrides `LaunchMode: web` setting in `Settings.fds`
- Works on ANY SwarmUI installation (no settings file modification needed)

### Expected Behavior
**Before:**
```
[ERROR] Cannot connect to host 127.0.0.1:7821
[ERROR] Workflow execution failed
```

**After:**
```
[SWARMUI-TEXT2IMAGE] Ensuring SwarmUI is available...
[SWARMUI-MANAGER] SwarmUI not available, starting...
[SWARMUI-MANAGER] Starting SwarmUI via: /path/to/2_start_swarmui.sh
[SWARMUI-MANAGER] SwarmUI process started (PID: 12345)
[SWARMUI-MANAGER] Waiting for SwarmUI (timeout: 120s)...
[SWARMUI-MANAGER] ✓ SwarmUI ready! (took 45.2s)
[SWARMUI] ✓ Generated 1 image(s)
```

### Benefits
- ✅ DevServer starts independently of SwarmUI
- ✅ Automatic crash recovery at runtime
- ✅ No manual intervention needed
- ✅ Frontend stays in focus (no SwarmUI UI popup)
- ✅ Works with any SwarmUI installation
- ✅ Configurable via environment variables

### Files Changed
- ✨ `devserver/my_app/services/swarmui_manager.py` (NEW - 247 lines)
- 📝 `devserver/config.py` (+7 lines - Auto-recovery configuration)
- 🔧 `devserver/my_app/services/legacy_workflow_service.py` (+9 lines - Manager integration)
- 🔧 `devserver/schemas/engine/backend_router.py` (+41 lines - Manager integration)
- 🚀 `2_start_swarmui.sh` (+3 lines - `--launch_mode none`)

**Commit:** `bbe04d8` - feat(swarmui): Add auto-recovery with SwarmUI Manager service

### Architecture Updates
- Updated ARCHITECTURE PART 07 - Engine-Modules.md (SwarmUI Manager)
- Updated ARCHITECTURE PART 08 - Backend-Routing.md (Auto-recovery integration)

---

## Session 112 - CRITICAL: Fix Streaming Connection Leak (CLOSE_WAIT) & Queue Implementation
**Date:** 2026-01-08
**Duration:** ~2 hours
**Focus:** Fix connection leak and concurrent request overload (Ollama)
**Status:** SUCCESS - Connection cleanup implemented, Queue implemented

### Problem 1: Connection Leak (CLOSE_WAIT)
Production system (lab.ai4artsed.org) experiencing streaming failures:
- Cloudflared tunnel logs: "stream X canceled by remote with error code 0"
- Backend accumulating connections in CLOSE_WAIT state
- Eventually all streaming requests failing

### Fix 1: Streaming Cleanup
Implemented `GeneratorExit` handling and explicit `response.close()` in streaming generators:
1. `/devserver/schemas/engine/prompt_interception_engine.py:381`
2. `/devserver/my_app/services/ollama_service.py:366`
3. `/devserver/my_app/routes/schema_pipeline_routes.py:1278`

Result: CLOSE_WAIT connections now clear properly (tested with load test).

### Problem 2: Ollama Overload (Timeouts)
Under load (e.g. 10 parallel requests), Ollama (120b model) gets overloaded.
- Requests time out after 90s (default `OLLAMA_TIMEOUT`)
- Model execution takes 100-260s
- Parallel requests cause congestion and failures

### Fix 2: Request Queueing & Timeouts
1. **Request Queue:**
   - Implemented `threading.Semaphore(3)` in `schema_pipeline_routes.py`.
   - Limits concurrent heavy model executions to 3 (others wait).
   - Applied to Stage 1 safety checks in `execute_pipeline_streaming`, `execute_pipeline` (POST), and `execute_stage2`.

2. **Timeout Increase:**
   - Increased `OLLAMA_TIMEOUT` in `config.py` from 90s to 300s.

3. **Bug Fix:**
   - Fixed `SyntaxError` in `streaming_response.py` (f-string syntax) that prevented backend startup.

### Test Results
**Load Test (10 concurrent requests):**
- Backend: Running on port 17802 (Dev script)
- Queue Logic: Verified in logs
  ```
  [OLLAMA-QUEUE] Initialized with max concurrent requests: 3
  [OLLAMA-QUEUE] Stream ...: Waiting for queue slot...
  [OLLAMA-QUEUE] Stream ...: Acquired slot...
  [OLLAMA-QUEUE] Stream ...: Released slot
  ```
- All requests queued and processed sequentially without timeout errors.

### Fix 3: User Feedback (Queue Visualization)
1. **Backend (SSE):**
   - Updated `execute_pipeline_streaming` to yield `queue_status` events while waiting in queue.
   - Frequency: Every 1 second.
   - Payload: `{'status': 'waiting', 'message': 'Warte auf freien Slot... (Xs)'}`.

2. **Frontend (MediaInputBox.vue):**
   - Added listener for `queue_status` event.
   - Visual Feedback:
     - Spinner turns **RED** (`.spinner-large.queued`) when status is 'waiting'.
     - Loading text pulses red and shows queue message.
     - Automatically resets to normal (blue) when slot is acquired.

### Next Steps
- Monitor production after deployment.

---

## Session 111 - CRITICAL: Unified Streaming Architecture Refactoring
**Date:** 2025-12-28
**Duration:** ~4 hours
- Supports both emoji and string icon names ('lightbulb', 'clipboard', etc.)
