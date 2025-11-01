# Session 5 Recovery - 4-Stage Pipeline System Design

**Status:** Session 5 Docs wurden versehentlich mit git checkout gelöscht. Dies ist eine Rekonstruktion aus dem Conversation Summary.

---

## Das Problem (User's Original Statement)

> "Mir scheint die Bearbeitung des Eingangsprompts VOR den Interception-Pipelines noch nicht ganz konsistent"

**Beobachtungen:**
- Manchmal erscheint die Übersetzung, manchmal nicht
- Ergebnisse innerhalb der Configs mit Single Text-Pipeline inkonsistent
- User-Vermutung: "Reste der legacy-workflow-logik im Code"
- Safety-System teilweise funktionierend, Translation inkonsistent

**Root Cause gefunden:**
- Legacy System hatte: `ollama_service.validate_and_translate_prompt()` mit Translation + Llama-Guard
- Neues System (`schema_pipeline_routes.py`): Direkt zur Pipeline, KEINE Pre-Processing

---

## Die Design-Diskussion

### User's Forderung:
> "Es wäre doch konsistenter und transparenter, wenn pre-interception-Maßnahmen durch pre-interception-pipelinconfigs durchgeführt werden und nicht im Servercode verborgen sind."

**Wichtige Namens-Korrektur:**
> "Verzeihung, wir sollten post-interception besser als pre-output bezeichnen. Denn bei komplexen, iterativen interception-pipelines kommt es dann auch zwischendurch zu output-aktionen. Da muss dann immer eine passende pre-output-sicherheitepipeline vorlaufen."

---

## Q&A Dokument (User's Antworten)

### Frage 1: Pre-Interception Pipeline-Aufteilung?
**User's Antwort:**
- Korrektur+Übersetzung: **Konsolidiert in 1 LLM-Call**
- Llama-Guard: **Separate Pipeline (nach Übersetzung)**

**Rationale:** Performance - 5 Calls (20-30s) zu lang für Workshops

### Frage 2: Llama-Guard obligatorisch oder optional?
**User's Antwort:** **Obligatorisch (nach Übersetzung)**

### Frage 3: Ordnerstruktur?
**User's Antwort:** **Hybrid-Ansatz**
- Neue Ordner: `pre_interception/`, `pre_output/`
- Existierende Configs bleiben in `configs/` (vorerst)

### Frage 4: Pre-Output media-type-spezifisch?
**User's Antwort:** **Ja, aber nur image für Alpha**
- `pre_output/image_safety_refinement.json`
- Audio/Video später

### Frage 5: Pre-Output Output-Format?
**User's Antwort:** **JSON-String**
```json
{
  "safe": true/false,
  "positive_prompt": "...",
  "negative_prompt": "...",
  "abort_reason": "..." (if unsafe)
}
```

### Frage 6: Safety-Failure-Handling?
**User's Antwort:** **Option B - Text-Alternative + Erklärung**
- NICHT abort komplett
- NICHT silent fallback
- Text-Alternative zeigen + Erklärung warum blockiert

### Frage 7: Llama-Guard Codes → German Messages?
**User's Antwort:** **Ja, Mapping-Tabelle**
- `schemas/llama_guard_explanations.json`
- DE + EN messages
- Freundliche Hints über mögliche Missverständnisse

### Frage 8: Console-Logging?
**User's Antwort:** **Ja, für Debug**
- Nicht UI-overload
- Console zeigt alle Stages

### Frage 9: Performance-Ziel?
**User's Antwort:**
- Päd-Ziel: <30s wäre toll
- **Akzeptabel: <60s**
- >60s wird wirklich nervig für Workshops

---

## Das 4-Stage System (Final Design)

```
User Input (German)
  ↓
[STAGE 1: PRE-INTERCEPTION] (System-Layer, 1x pro Request)
  1.1 → correction_translation_de_en (konsolidiert, ~8s)
  1.2 → safety_llamaguard (nach Übersetzung, ~3s)
  ↓
[STAGE 2: INTERCEPTION] (User-selected Config)
  → dada.json / bauhaus.json / etc. (~5s)
  ↓
[STAGE 3: PRE-OUTPUT] (Before EACH media output)
  → image_safety_refinement (safety + negative prompts, ~5s)
  ↓
[STAGE 4: OUTPUT] (Media Generation)
  → sd35_large / flux1 / etc. (~20s)
```

**Total Latency:** ~42s (innerhalb <60s Ziel!)

---

## Configs zu erstellen

### Pre-Interception Configs

**1. `schemas/configs/pre_interception/correction_translation_de_en.json`**
```json
{
  "pipeline": "text_transformation",
  "name": {
    "en": "Pre-Interception: Correction + Translation (DE → EN)",
    "de": "Vor-Interception: Korrektur + Übersetzung (DE → EN)"
  },
  "context": "You are processing German text input from children and youth (ages 6-17) in arts education courses.\n\nYour tasks:\n\n1. CORRECT SPELLING AND GRAMMAR:\n   - Fix common spelling mistakes (typos, phonetic errors)\n   - Fix grammar errors typical for young learners\n   - Context: Children/youth with varying language skills\n   - IMPORTANT: Do NOT over-correct artistic word combinations!\n   - IMPORTANT: Preserve unusual phrasing if it appears intentional\n   - IMPORTANT: Keep line breaks, special characters, brackets intact\n\n2. TRANSLATE TO ENGLISH:\n   - Culture-sensitive translation\n   - Preserve artistic intent and emotional tone\n   - Maintain structure (line breaks, punctuation)\n   - Context: This is input for AI art generation\n\nOutput ONLY the corrected and translated text. No explanations, no meta-comments.",
  "parameters": {
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 2048
  },
  "meta": {
    "system_pipeline": true,
    "pre_interception": true,
    "skip_pre_translation": true,
    "skip_safety_check": false,
    "visible_in_browser": false
  }
}
```

**2. `schemas/configs/pre_interception/safety_llamaguard.json`**
```json
{
  "pipeline": "text_transformation",
  "name": {
    "en": "Pre-Interception: Llama-Guard-3 Safety Check",
    "de": "Vor-Interception: Llama-Guard-3 Sicherheitsprüfung"
  },
  "context": "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\nTask: Check if there is unsafe content in 'User' messages in conversations according our safety policy with the below categories.\n\n<BEGIN UNSAFE CONTENT CATEGORIES>\nS1: Violent Crimes.\n[... full Llama-Guard prompt with all 13 categories ...]\n<END UNSAFE CONTENT CATEGORIES>\n\n<BEGIN CONVERSATION>\n\nUser: {{PREVIOUS_OUTPUT}}\n\n<END CONVERSATION>\n\nProvide your safety assessment for ONLY THE LAST User message in the above conversation:\n - First line must read 'safe' or 'unsafe'.\n - If unsafe, a second line must include a comma-separated list of violated categories.<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
  "parameters": {
    "temperature": 0.0,
    "top_p": 1.0,
    "max_tokens": 512
  },
  "meta": {
    "system_pipeline": true,
    "pre_interception": true,
    "llama_guard": true,
    "skip_pre_translation": true,
    "skip_safety_check": true,
    "model_override": "llama-guard-3:8b",
    "visible_in_browser": false
  }
}
```

### Pre-Output Config

**`schemas/configs/pre_output/image_safety_refinement.json`**
```json
{
  "pipeline": "text_transformation",
  "name": {
    "en": "Pre-Output: Image Safety & Refinement",
    "de": "Vor-Output: Bild-Sicherheit & Verfeinerung"
  },
  "context": "You are preparing a text prompt for AI image generation. This prompt has already been artistically transformed.\n\nYour tasks:\n\n1. SAFETY CHECK:\nDoes this prompt contain ANY unsafe elements?\n- Violence, weapons, blood, death, injury\n- Sexual content, nudity, innuendo\n- Frightening, horror, disturbing imagery\n- Hate symbols, discrimination\n- Drug/alcohol references\n\nIf UNSAFE: Output JSON with \"safe\": false and \"abort_reason\": \"[specific reason]\"\nIf SAFE: Continue to step 2.\n\n2. NEGATIVE PROMPT GENERATION:\nGenerate appropriate negative prompts to exclude:\n- Quality issues: blurry, low quality, bad anatomy, distorted, deformed, ugly\n- Technical issues: text, watermark, signature, artist name, copyright\n- Safety exclusions based on context:\n  * For kids (6-12): scary, dark, violent, disturbing, frightening, horror, sexual, nude\n  * For youth (13-17): sexual, nude, extreme violence, disturbing\n\n3. PROMPT REFINEMENT:\nSlightly refine the prompt for better image quality\n\n4. OUTPUT FORMAT (MANDATORY JSON):\n{\n  \"safe\": true,\n  \"positive_prompt\": \"[refined prompt]\",\n  \"negative_prompt\": \"[comma-separated negative tags]\",\n  \"abort_reason\": null\n}\n\nOr if unsafe:\n{\n  \"safe\": false,\n  \"positive_prompt\": null,\n  \"negative_prompt\": null,\n  \"abort_reason\": \"[specific reason]\"\n}\n\nIMPORTANT: Output ONLY valid JSON, nothing else.",
  "parameters": {
    "temperature": 0.3,
    "top_p": 0.9,
    "max_tokens": 1024
  },
  "meta": {
    "system_pipeline": true,
    "pre_output": true,
    "media_type": "image",
    "output_format": "json",
    "safety_level": "youth",
    "skip_pre_translation": true,
    "skip_safety_check": true,
    "visible_in_browser": false
  }
}
```

### Llama-Guard Mapping Table

**`schemas/llama_guard_explanations.json`**
```json
{
  "version": "1.0",
  "description": "German explanations for Llama-Guard-3 safety codes with friendly hints about possible misunderstandings",
  "base_message": {
    "de": "Dein Prompt wurde blockiert:",
    "en": "Your prompt was blocked:"
  },
  "hint_message": {
    "de": "\n\nℹ️ Hinweis: Es kann sich auch um ein Missverständnis handeln.\n\nBeispiel: Das Wort \"Cdspieler\" wurde als \"Cdplayer\" übersetzt und blockiert, weil \"player\" in manchen Kontexten problematisch sein kann.\n\nFalls du denkst, dass dein Prompt harmlos ist, sprich mit dem Kursleiter oder der Kursleiterin.",
    "en": "\n\nℹ️ Note: This might be a misunderstanding.\n\nExample: The word \"Cdspieler\" was translated to \"Cdplayer\" and blocked because \"player\" can be problematic in some contexts.\n\nIf you think your prompt is harmless, talk to your course instructor."
  },
  "codes": {
    "S1": {
      "de": "Dein Prompt enthält Hinweise auf Gewaltverbrechen (z.B. Terrorismus, Mord, Körperverletzung, Kindesmissbrauch).",
      "en": "Your prompt contains references to violent crimes (e.g., terrorism, murder, assault, child abuse)."
    },
    "S2": {
      "de": "Dein Prompt enthält Hinweise auf nicht-gewalttätige Verbrechen (z.B. Betrug, Einbruch, Drogenhandel, Hacking).",
      "en": "Your prompt contains references to non-violent crimes (e.g., fraud, burglary, drug trafficking, hacking)."
    },
    [... all 13 codes S1-S13 with German + English explanations ...]
  },
  "fallback": {
    "de": "Dein Prompt wurde aus Sicherheitsgründen blockiert. Bitte sprich mit dem Kursleiter oder der Kursleiterin.",
    "en": "Your prompt was blocked for safety reasons. Please talk to your course instructor."
  }
}
```

---

## Implementation (WO es hingehört)

**NICHT im Server-Code (`schema_pipeline_routes.py`)**

**SONDERN:**

Die Pre-Interception Logik gehört in den **PipelineExecutor** (`schemas/engine/pipeline_executor.py`):

```python
async def execute_pipeline(self, config_name: str, input_text: str, ...):
    config = self.config_loader.get_config(config_name)

    # Check meta flags
    skip_pre_translation = config.meta.get('skip_pre_translation', False)
    skip_safety_check = config.meta.get('skip_safety_check', False)

    current_text = input_text

    # STAGE 1: Pre-Interception (if not system config itself)
    if not skip_pre_translation:
        if is_german_text(current_text):
            # Execute correction_translation_de_en config
            pre_result = await self.execute_pipeline(
                'pre_interception/correction_translation_de_en',
                current_text
            )
            current_text = pre_result.final_output

    if not skip_safety_check:
        # Execute safety_llamaguard config
        safety_result = await self.execute_pipeline(
            'pre_interception/safety_llamaguard',
            current_text
        )

        # Parse Llama-Guard output
        if safety_result.final_output.startswith('unsafe'):
            codes = parse_safety_codes(safety_result.final_output)
            message = build_safety_message(codes, lang='de')
            raise SafetyViolationError(message, codes)

        current_text = safety_result.final_output

    # STAGE 2: Execute actual pipeline
    result = await self._execute_chunks(config, current_text)

    return result
```

**Pre-Output Logic:**
Gehört auch in `PipelineExecutor` oder in `backend_router.py` - wird VOR Media-Generation aufgerufen.

---

## Was NICHT mehr gemacht werden sollte

❌ Loops über `pre_chain` Arrays im Server-Code
❌ Manuelle Execution von Pre-Configs in `schema_pipeline_routes.py`
❌ `pre_chain_results` sammeln im Server

✅ PipelineExecutor ruft automatisch Pre-Configs auf
✅ Meta-Flags in Configs steuern Verhalten
✅ Pipeline-basierte Lösung (nicht Server-Code)

---

## Status

- [ ] Docs geschrieben (diese Recovery)
- [ ] Configs erstellt
- [ ] PipelineExecutor erweitert
- [ ] Testing

---

**Erstellt:** Recovery aus Session 5 Summary nach versehentlichem git checkout
