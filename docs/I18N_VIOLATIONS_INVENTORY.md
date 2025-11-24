# i18n Policy Violations - Complete Inventory

**Date**: 2025-11-23
**Status**: Documentation Complete - Fixes Pending
**Scope**: ~100+ hardcoded German strings across 19 files
**Priority**: Low (technical debt)

## Executive Summary

This document catalogs all violations of the i18n policy established in DEVELOPMENT_DECISIONS.md Session 30, which mandates: **"NEVER Hardcode Language-Specific Strings"**.

The system is designed to be bilingual (German + English) with multilingual readiness. All language-specific content must be externalized to configuration/translation files, never embedded directly in code.

### Policy Requirements

1. **Frontend**: All UI strings must come from i18n translation files
2. **Backend**: Language strings pulled from config with language variants
3. **Code**: All comments and documentation in English only
4. **NO Hardcoding**: Never embed German, English, or any language directly in code

### Violation Statistics

| Category | Count | Priority |
|----------|-------|----------|
| Frontend UI Text | ~20 | High |
| Backend Safety/Error Messages | ~50 | Critical |
| Backend Log/Status Messages | ~30 | Medium |
| German Code Comments | ~10 | Low |
| **TOTAL** | **~100+** | |

---

## 1. Frontend Vue Components

### 1.1 text_transformation.vue

**File**: `/public/ai4artsed-frontend/src/views/text_transformation.vue`
**Violations**: 20+ hardcoded German UI strings

#### UI Labels and Headers

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 13 | `Deine Idee: Worum soll es gehen?` | Input bubble label | Move to i18n |
| 27 | `Bestimme Regeln, Material, Besonderheiten` | Context bubble label | Move to i18n |
| 58 | `Idee + Regeln = Prompt` | Interception result label | Move to i18n |
| 78 | `Wähle ein Medium aus` | Section title | Move to i18n |
| 101 | `wähle ein KI-Modell aus` | Section title | Move to i18n |
| 139 | `Modell-Optimierter Prompt` | Label | Move to i18n |

#### Placeholder Text

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 17 | `Ein Fest in meiner Straße: ...` | Input placeholder | Move to i18n |
| 32 | `Beschreibe alles so, wie es die Vögel auf den Bäumen wahrnehmen!` | Context placeholder | Move to i18n |
| 68 | `Prompt erscheint nach Start-Klick` | Placeholder | Move to i18n |
| 149 | `Der optimierte Prompt erscheint nach Modellauswahl.` | Placeholder | Move to i18n |
| 203 | `Dein Bild erscheint hier` | Placeholder text | Move to i18n |

#### Loading Messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 62 | `Die KI kombiniert jetzt deine Idee mit den Regeln...` | Loading text | Move to i18n |
| 143 | `Der Prompt wird jetzt für das gewählte KI-Modell angepasst...` | Loading text | Move to i18n |

#### Error Messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 503 | `Fehler: ${response.data.error}` | Alert message | Move to i18n |
| 507 | `Fehler: ${error.message}` | Alert message | Move to i18n |
| 540 | `Fehler: ${response.data.error}` | Alert message | Move to i18n |
| 544 | `Fehler: ${error.message}` | Alert message | Move to i18n |
| 622 | `Fehler: ${response.data.error}` | Alert message | Move to i18n |

#### Image Alt Text

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 194 | `Generiertes Bild` | Alt text | Move to i18n |
| 214 | `Dein Bild` | Alt text (fullscreen) | Move to i18n |

#### Code Comments (German)

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 845 | `wird von JS zu 'auto' geändert wenn Text zu lang` | CSS comment | Replace with English |

**Recommended Fix**:
- Create comprehensive i18n entries in `/public/ai4artsed-frontend/src/i18n/de.json` and `/public/ai4artsed-frontend/src/i18n/en.json`
- Replace all hardcoded strings with `$t('key.path')` syntax
- Convert CSS comment to English

---

### 1.2 text_transformation_OLD_TEMP.vue

**File**: `/public/ai4artsed-frontend/src/views/text_transformation_OLD_TEMP.vue`
**Violations**: Same as text_transformation.vue (legacy file)

**Status**: Legacy file - Consider deleting or fixing if still in use

| Line | German String | Context |
|------|---------------|---------|
| 27, 32, 64, 96 | Various UI strings | Same violations as main file |
| 416, 420, 496 | Error messages | Same pattern |

**Recommended Fix**: Delete if unused, or apply same fixes as text_transformation.vue

---

### 1.3 PropertyQuadrantsView.vue

**File**: `/public/ai4artsed-frontend/src/views/PropertyQuadrantsView.vue`
**Violations**: 3 hardcoded German UI strings

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 6 | `Lade Konfigurationen...` | Loading message | Move to i18n |
| 12 | `Fehler beim Laden` | Error header | Move to i18n |
| 24 | `Konfiguration auswählen` | Button text | Move to i18n |

**Recommended Fix**: Add to i18n files, use `$t()` syntax

---

### 1.4 PropertyCanvas_Vorlage.vue

**File**: `/public/ai4artsed-frontend/src/components/PropertyCanvas_Vorlage.vue`
**Violations**: 2 dynamic German strings

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 68 | `Konfiguration` / `Konfigurationen` | Dynamic text | Move to i18n with plural handling |

**Recommended Fix**: Use i18n pluralization feature

---

### 1.5 NoMatchState.vue

**File**: `/public/ai4artsed-frontend/src/components/NoMatchState.vue`
**Violations**: 2 hardcoded German UI strings

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 19 | `Teilweise Übereinstimmungen` | Section title | Move to i18n |
| 25 | `Diese Konfigurationen entsprechen einigen Ihrer ausgewählten Eigenschaften:` | Description | Move to i18n |

**Recommended Fix**: Add to i18n files

---

## 2. Backend Python - Safety Messages

### 2.1 stage_orchestrator.py

**File**: `/devserver/schemas/engine/stage_orchestrator.py`
**Violations**: 30+ hardcoded German safety messages
**Priority**: CRITICAL (user-facing safety messages)

#### Fallback Safety Message

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 179 | `Dein Prompt wurde aus Sicherheitsgründen blockiert.` | Generic fallback | Move to config with language variants |

#### §86a Law Violation Messages

| Line Range | German String | Context | Fix Required |
|------------|---------------|---------|--------------|
| 386-391 | `⚠️ Dein Prompt wurde blockiert\n\nGRUND: §86a StGB - [symbol]\n\nDein Prompt enthält Begriffe...\n\nWARUM DIESE REGEL?\nDiese Symbole werden benutzt, um Gewalt und Hass zu verbreiten.\nWir schützen dich und andere vor gefährlichen Inhalten.` | Law violation message | Move to safety config with DE/EN variants |

**Full Message Structure**:
```
⚠️ Dein Prompt wurde blockiert

GRUND: §86a StGB - {symbol}

Dein Prompt enthält Begriffe oder Symbole, die in Deutschland gesetzlich verboten sind ({law_reference}):
• {symbol}

WARUM DIESE REGEL?
Diese Symbole werden benutzt, um Gewalt und Hass zu verbreiten.
Wir schützen dich und andere vor gefährlichen Inhalten.

Was kannst du tun?
• Versuche es mit anderen Wörtern, die deine Idee beschreiben
• Wenn du glaubst, das ist ein Fehler, sprich mit deinen Eltern oder Lehrern
```

#### Generic Safety Block Messages

| Line Range | German String | Context | Fix Required |
|------------|---------------|---------|--------------|
| 413-418 | Similar block structure | Generic blocked message | Move to safety config |

#### Kids Filter Messages (6-12 Jahre)

| Line Range | German String | Context | Fix Required |
|------------|---------------|---------|--------------|
| 432-437 | `⚠️ Dein Prompt wurde blockiert\n\nGRUND: Kinder-Schutzfilter (6-12 Jahre)\n\n[Explanation about scary content]` | Kids safety violation | Move to safety config |

**Full Message Structure**:
```
⚠️ Dein Prompt wurde blockiert

GRUND: Kinder-Schutzfilter (6-12 Jahre)

Dein Prompt enthält Begriffe, die für Kinder nicht geeignet sind:
• Gruselige oder beängstigende Inhalte
• Gewalt oder bedrohliche Situationen
• Verstörende Bilder oder Szenen

WARUM DIESE REGEL?
Wir wollen, dass du sicher kreativ sein kannst, ohne Angst haben zu müssen.

Was kannst du tun?
• Denke dir eine freundlichere Version aus
• Frage deine Eltern oder Lehrer um Hilfe
```

#### Youth Filter Messages (13-17 Jahre)

| Line Range | German String | Context | Fix Required |
|------------|---------------|---------|--------------|
| 450-455 | `⚠️ Dein Prompt wurde blockiert\n\nGRUND: Jugendschutzfilter (13-17 Jahre)\n\n[Explanation]` | Youth safety violation | Move to safety config |

#### Unknown Block Type

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 465 | `⚠️ Dein Prompt wurde blockiert\n\nGRUND: Sicherheitsfilter` | Unknown block fallback | Move to safety config |

**Recommended Fix**:
- Create `devserver/config/safety_messages.json` with structure:
```json
{
  "de": {
    "law_violation": {
      "header": "⚠️ Dein Prompt wurde blockiert",
      "reason_prefix": "GRUND:",
      ...
    }
  },
  "en": {
    "law_violation": {
      "header": "⚠️ Your prompt was blocked",
      "reason_prefix": "REASON:",
      ...
    }
  }
}
```
- Load messages based on `user_language` parameter
- Keep legal references (§86a StGB) as-is (language-neutral)

---

### 2.2 ollama_service.py

**File**: `/devserver/my_app/services/ollama_service.py`
**Violations**: 2 hardcoded German messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 267 | `⚠️ Dein Prompt wurde blockiert\n\nGRUND: {law_reference} - {symbol}\n\n{explanation}\n\nWARUM DIESE REGEL?\n...` | Safety violation response | Use safety_messages.json |
| 344 | `Übersetzungs-Service fehlgeschlagen.` | Error message | Move to error messages config |

**Recommended Fix**: Reference centralized safety_messages.json

---

## 3. Backend Python - Status/Log Messages

### 3.1 workflow_logic_service.py

**File**: `/devserver/my_app/services/workflow_logic_service.py`
**Violations**: 10+ hardcoded German status/log messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 305 | `Cloud-Modell '{openrouter_model_name}' durch lokales Modell '{local_model}' ersetzt.` | Status update | i18n or English |
| 310 | `Warnung: Kein lokales Äquivalent für '{openrouter_model_name}' gefunden.` | Warning message | i18n or English |
| 325 | `Schnell-Modus aktiviert. Suche nach Cloud-basierten Modell-Äquivalenten...` | Status message | i18n or English |
| 801 | `Sicherheitsstufe '{safety_level}' aktiviert.` | Status message | i18n or English |
| 819 | `Standard-Negativ-Begriffe` | Status message | i18n or English |
| 822 | `benutzerdefinierte Negativ-Begriffe` | Status message | i18n or English |
| 825 | `Kindersicherheitsbegriffe` | Status message | i18n or English |
| 827 | `Jugendschutzbegriffe` | Status message | i18n or English |
| 846 | `Warnung: Model-Pfad-Auflösung fehlgeschlagen, verwende Original-Pfade.` | Warning message | i18n or English |

**Recommended Fix**:
- Option A: Convert all to English (internal logging)
- Option B: Use logger with i18n support for user-facing messages

---

### 3.2 export_manager.py

**File**: `/devserver/my_app/services/export_manager.py`
**Violations**: 2 hardcoded German strings

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 125 | `Übersetzter Prompt` | HTML header in export | i18n based on user_language |
| 530 | `Export fehlgeschlagen: {str(e)}` | Error message | i18n or English |

**Recommended Fix**: Pass user_language through export pipeline, use i18n

---

### 3.3 chunk_builder.py

**File**: `/devserver/schemas/engine/chunk_builder.py`
**Violations**: 2 hardcoded German log messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 48 | `Fehler beim Laden von Template {template_file}: {e}` | Error log | Convert to English |
| 93 | `Fehler beim Parsen von {template_file}: {e}` | Error log | Convert to English |

**Recommended Fix**: Convert to English (internal error logs)

---

### 3.4 backend_router.py

**File**: `/devserver/schemas/engine/backend_router.py`
**Violations**: 6 hardcoded German log messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 85 | `Fehler bei Backend-Verarbeitung: {e}` | Error log | Convert to English |
| 166 | `Prompt Interception Engine Fehler: {e}` | Error log | Convert to English |
| 230 | `Ollama-Backend-Fehler: {e}` | Error log | Convert to English |
| 253 | `Direct-Backend-Fehler: {e}` | Error log | Convert to English |
| 294 | `ComfyUI-Backend-Fehler: {e}` | Error log | Convert to English |
| 987 | `ComfyUI-Legacy-Backend-Fehler: {e}` | Error log | Convert to English |

**Recommended Fix**: Convert all to English (internal error logs)

---

### 3.5 prompt_interception_engine.py

**File**: `/devserver/schemas/engine/prompt_interception_engine.py`
**Violations**: 10+ German comments and log messages

#### German Comments

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 38 | `Request für Prompt Interception Engine` | Dataclass docstring | Convert to English |
| 59 | `Prompt Interception Engine - Zentrale KI-Request-Funktionalität` | Class docstring | Convert to English |
| 75 | `Baut vollständigen Prompt im Custom Node Format` | Method docstring | Convert to English |
| 92 | `Modellnamen extrahieren` | Comment | Convert to English |
| 146 | `WICHTIG: OpenRouter-Modelle (speziell Gemma) ignorieren System-Messages oft` | Comment | Convert to English |
| 174 | `Fallback versuchen` | Comment | Convert to English |
| 188 | `WICHTIG: Kein System-Prompt für Ollama` | Comment | Convert to English |
| 222 | `Fallback versuchen` | Comment | Convert to English |

#### German Log Messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 126 | `Prompt Interception Fehler: {e}` | Error log | Convert to English |
| 172 | `OpenRouter Modell {model} fehlgeschlagen: {e}` | Error log | Convert to English |
| 220 | `Ollama Modell {model} fehlgeschlagen: {e}` | Error log | Convert to English |

**Recommended Fix**: Convert all comments and logs to English

---

### 3.6 export_routes.py

**File**: `/devserver/my_app/routes/export_routes.py`
**Violations**: 3 hardcoded German error messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 47 | `Export fehlgeschlagen` | Error response | i18n or English |
| 74 | `Download-Erstellung fehlgeschlagen` | Error response | i18n or English |
| 91 | `Download fehlgeschlagen` | Error response | i18n or English |

**Recommended Fix**: Use i18n for user-facing errors

---

### 3.7 workflow_streaming_routes.py

**File**: `/devserver/my_app/routes/workflow_streaming_routes.py`
**Violations**: 2 hardcoded German error messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 84 | `Prompt-Validierung fehlgeschlagen.` | Error message | i18n or English |
| 170 | `Workflow-Ausführung fehlgeschlagen: {str(e)}` | Error message | i18n or English |

**Recommended Fix**: Use i18n for user-facing errors

---

### 3.8 schema_pipeline_routes.py

**File**: `/devserver/my_app/routes/schema_pipeline_routes.py`
**Violations**: 4 hardcoded German log messages

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 444 | `Schema-Info Fehler: {e}` | Error log | Convert to English |
| 1628 | `Pipeline-Execution Fehler: {e}` | Error log | Convert to English |
| 1701 | `Test-Pipeline Fehler: {e}` | Error log | Convert to English |
| 1725 | `Schema-List Fehler: {e}` | Error log | Convert to English |

**Recommended Fix**: Convert to English (internal logs)

---

## 4. Reference/Legacy Code

### 4.1 ComfyUI Custom Node

**File**: `/docs/reference/fyi_comfyui-customnodes_ai4artsed_comfyui/ai4artsed_switch_promptsafety.py`
**Violations**: 5 German comments
**Status**: Reference file in docs folder

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 120 | `Verwende model_override wenn vorhanden, sonst den Dropdown-Wert` | Comment | Convert to English |
| 133 | `KRITISCH: Unterschiedliche Prompt-Zusammensetzung je nach Filter-Level` | Comment | Convert to English |
| 135-136 | `Für Kids: NUR die Filteranweisung, KEINE Transformation` + `Das LLM soll nur prüfen...` | Comments | Convert to English |
| 142 | `Für Youth: Direkte Anweisung mit bedingter Transformation` | Comment | Convert to English |
| 195 | `KRITISCH: System message und temperature wie im Original` | Comment | Convert to English |

**Recommended Fix**: Convert to English (documentation reference)

---

## 5. Test Files

### 5.1 test_e2e_stage123.py

**File**: `/devserver/testfiles/test_e2e_stage123.py`
**Violations**: 1 German docstring

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 64 | `Stage 3 sollte Kids-Filter-Begriffe blocken` | Test docstring | Convert to English |

**Recommended Fix**: Convert to English

---

### 5.2 test_context_aware_safety.py

**File**: `/devserver/testfiles/test_context_aware_safety.py`
**Violations**: 1 German test case description

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 19 | `Kinderbuch 'Der kleine Vampir'` | Test case description | Keep (test data) or convert |

**Recommended Fix**: Could remain as test data, or convert to English description

---

### 5.3 test_stage_orchestrator_phase2.py

**File**: `/devserver/testfiles/test_stage_orchestrator_phase2.py`
**Violations**: 1 German assertion string

| Line | German String | Context | Fix Required |
|------|---------------|---------|--------------|
| 80 | `blockiert` | Test assertion | Convert to English |

**Recommended Fix**: Convert to English

---

## 6. Migration Strategy

### Phase 1: Critical User-Facing Messages (Priority: CRITICAL)

1. **Safety Messages** (`stage_orchestrator.py`, `ollama_service.py`)
   - Create `devserver/config/safety_messages.json`
   - Implement bilingual message loading based on `user_language`
   - Update all safety block message generation

2. **Frontend Error Messages** (Vue components)
   - Add error messages to i18n files
   - Replace hardcoded `Fehler:` with `$t('error.prefix')`

### Phase 2: Frontend UI (Priority: HIGH)

1. **text_transformation.vue**
   - Comprehensive i18n file entries
   - Replace all ~20 hardcoded strings
   - Test both DE and EN language switching

2. **Other Vue Components**
   - PropertyQuadrantsView.vue
   - NoMatchState.vue
   - PropertyCanvas_Vorlage.vue

### Phase 3: Backend Status Messages (Priority: MEDIUM)

1. **Decision Required**: Choose strategy
   - Option A: Convert all to English (simpler, internal logs)
   - Option B: Implement logger with i18n (more complex, better UX)

2. **Files to update**:
   - workflow_logic_service.py
   - export_manager.py
   - Various route files

### Phase 4: Code Comments (Priority: LOW)

1. **Systematic conversion to English**
   - prompt_interception_engine.py
   - All other files with German comments
   - Update coding standards documentation

### Phase 5: Test Files (Priority: LOW)

1. **Convert test documentation to English**
   - Test docstrings
   - Test case descriptions
   - Consider keeping German test data strings (valid test scenario)

---

## 7. Implementation Checklist

### Prerequisites
- [ ] Decide on backend logging strategy (English vs i18n)
- [ ] Create `devserver/config/safety_messages.json` structure
- [ ] Set up i18n migration tracking system

### Frontend
- [ ] Audit current i18n file structure
- [ ] Add all missing German strings to `de.json`
- [ ] Add all English translations to `en.json`
- [ ] Update text_transformation.vue
- [ ] Update PropertyQuadrantsView.vue
- [ ] Update NoMatchState.vue
- [ ] Update PropertyCanvas_Vorlage.vue
- [ ] Remove text_transformation_OLD_TEMP.vue if unused
- [ ] Test language switching functionality

### Backend - Safety Messages
- [ ] Create safety_messages.json with DE/EN variants
- [ ] Update stage_orchestrator.py to use config
- [ ] Update ollama_service.py to use config
- [ ] Test all safety block scenarios

### Backend - Logging/Status
- [ ] Convert chunk_builder.py logs to English
- [ ] Convert backend_router.py logs to English
- [ ] Convert prompt_interception_engine.py logs to English
- [ ] Convert schema_pipeline_routes.py logs to English
- [ ] Update workflow_logic_service.py (strategy-dependent)
- [ ] Update export_manager.py (strategy-dependent)
- [ ] Update export_routes.py (strategy-dependent)
- [ ] Update workflow_streaming_routes.py (strategy-dependent)

### Backend - Comments/Documentation
- [ ] Convert prompt_interception_engine.py comments to English
- [ ] Convert ai4artsed_switch_promptsafety.py comments to English
- [ ] Update test file docstrings to English

### Validation
- [ ] Run grep search to verify no remaining violations
- [ ] Test both German and English user flows
- [ ] Verify all safety messages work in both languages
- [ ] Update i18n policy documentation
- [ ] Add pre-commit hook to prevent future violations

---

## 8. Automated Detection

### Grep Pattern for Future Violations

```bash
# Search for German-specific characters in code (excluding docs/)
grep -r "[äöüß]" --include="*.py" --include="*.vue" --include="*.js" --include="*.ts" \
  --exclude-dir="docs" --exclude-dir="node_modules" --exclude-dir=".git" .

# Search for common German words in code
grep -r "\b(wird\|ist\|sind\|das\|die\|der\|und\|für\|mit\|von\|zu\|Fehler\|Warnung)\b" \
  --include="*.py" --include="*.vue" --include="*.js" --include="*.ts" \
  --exclude-dir="docs" --exclude-dir="node_modules" --exclude-dir=".git" .
```

### Pre-commit Hook (Proposed)

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Prevent committing German strings in code

GERMAN_CHARS=$(git diff --cached --name-only --diff-filter=ACM | \
  grep -E '\.(py|vue|js|ts)$' | \
  xargs grep -l "[äöüß]" 2>/dev/null || true)

if [ -n "$GERMAN_CHARS" ]; then
  echo "ERROR: German characters found in code files:"
  echo "$GERMAN_CHARS"
  echo "Please use i18n system for language-specific strings."
  exit 1
fi

exit 0
```

---

## 9. Related Documentation

- **i18n Policy**: `docs/DEVELOPMENT_DECISIONS.md` - Session 30
- **Frontend i18n System**: `docs/ARCHITECTURE PART 12 - Frontend-Architecture.md`
- **Migration Decisions**: This document serves as the implementation guide

---

## Appendix A: Example i18n Structures

### Frontend i18n Example

```javascript
// public/ai4artsed-frontend/src/i18n/de.json
{
  "textTransformation": {
    "inputLabel": "Deine Idee: Worum soll es gehen?",
    "inputPlaceholder": "Ein Fest in meiner Straße: ...",
    "contextLabel": "Bestimme Regeln, Material, Besonderheiten",
    "contextPlaceholder": "Beschreibe alles so, wie es die Vögel auf den Bäumen wahrnehmen!",
    "interceptionLabel": "Idee + Regeln = Prompt",
    "loadingInterception": "Die KI kombiniert jetzt deine Idee mit den Regeln...",
    "mediaSelectionTitle": "Wähle ein Medium aus",
    "modelSelectionTitle": "wähle ein KI-Modell aus"
  },
  "error": {
    "prefix": "Fehler:",
    "generic": "Ein Fehler ist aufgetreten"
  }
}

// public/ai4artsed-frontend/src/i18n/en.json
{
  "textTransformation": {
    "inputLabel": "Your idea: What should it be about?",
    "inputPlaceholder": "A festival on my street: ...",
    "contextLabel": "Define rules, materials, special features",
    "contextPlaceholder": "Describe everything as the birds in the trees perceive it!",
    "interceptionLabel": "Idea + Rules = Prompt",
    "loadingInterception": "The AI is now combining your idea with the rules...",
    "mediaSelectionTitle": "Choose a medium",
    "modelSelectionTitle": "choose an AI model"
  },
  "error": {
    "prefix": "Error:",
    "generic": "An error occurred"
  }
}
```

### Backend Safety Messages Example

```json
// devserver/config/safety_messages.json
{
  "de": {
    "law_violation": {
      "header": "⚠️ Dein Prompt wurde blockiert",
      "reason_prefix": "GRUND:",
      "law_reference_text": "Dein Prompt enthält Begriffe oder Symbole, die in Deutschland gesetzlich verboten sind",
      "why_header": "WARUM DIESE REGEL?",
      "why_text": "Diese Symbole werden benutzt, um Gewalt und Hass zu verbreiten. Wir schützen dich und andere vor gefährlichen Inhalten.",
      "what_todo_header": "Was kannst du tun?",
      "what_todo_bullets": [
        "Versuche es mit anderen Wörtern, die deine Idee beschreiben",
        "Wenn du glaubst, das ist ein Fehler, sprich mit deinen Eltern oder Lehrern"
      ]
    },
    "kids_filter": {
      "header": "⚠️ Dein Prompt wurde blockiert",
      "reason": "Kinder-Schutzfilter (6-12 Jahre)",
      "content_issues": [
        "Gruselige oder beängstigende Inhalte",
        "Gewalt oder bedrohliche Situationen",
        "Verstörende Bilder oder Szenen"
      ],
      "why_text": "Wir wollen, dass du sicher kreativ sein kannst, ohne Angst haben zu müssen.",
      "what_todo_bullets": [
        "Denke dir eine freundlichere Version aus",
        "Frage deine Eltern oder Lehrer um Hilfe"
      ]
    },
    "youth_filter": {
      "header": "⚠️ Dein Prompt wurde blockiert",
      "reason": "Jugendschutzfilter (13-17 Jahre)",
      "explanation": "Dein Prompt enthält Inhalte, die für Jugendliche unter 18 Jahren nicht geeignet sind."
    }
  },
  "en": {
    "law_violation": {
      "header": "⚠️ Your prompt was blocked",
      "reason_prefix": "REASON:",
      "law_reference_text": "Your prompt contains terms or symbols that are legally prohibited in Germany",
      "why_header": "WHY THIS RULE?",
      "why_text": "These symbols are used to spread violence and hate. We protect you and others from dangerous content.",
      "what_todo_header": "What can you do?",
      "what_todo_bullets": [
        "Try using different words that describe your idea",
        "If you think this is an error, talk to your parents or teachers"
      ]
    },
    "kids_filter": {
      "header": "⚠️ Your prompt was blocked",
      "reason": "Kids Protection Filter (6-12 years)",
      "content_issues": [
        "Scary or frightening content",
        "Violence or threatening situations",
        "Disturbing images or scenes"
      ],
      "why_text": "We want you to be safely creative without having to be afraid.",
      "what_todo_bullets": [
        "Think of a friendlier version",
        "Ask your parents or teachers for help"
      ]
    },
    "youth_filter": {
      "header": "⚠️ Your prompt was blocked",
      "reason": "Youth Protection Filter (13-17 years)",
      "explanation": "Your prompt contains content that is not suitable for youth under 18."
    }
  }
}
```

---

**END OF DOCUMENT**
