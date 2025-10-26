# Legacy Server Architecture: AI4ArtsEd Webserver

## Dokumentationsziel

Diese Dokumentation analysiert die Architektur des Legacy-Servers (`/server`) mit besonderem Fokus auf die **Verflechtung künstlerisch-pädagogischer Gedanken mit technischen Verfahrensweisen**. Sie dient als Wissenstransfer für neue LLM-Tasks, um das System vollständig zu verstehen, bevor Änderungen vorgenommen werden.

---

## 1. Grundanliegen: Gegenhegemoniale Pädagogik statt Solutionismus

### 1.1 Das Problem: ComfyUI als solutionistisches System

**ComfyUI** ist ein leistungsfähiges Node-basiertes Interface für generative AI, folgt aber einem **linearen, produktorientierten Paradigma**:

- **Linearität**: Workflows laufen von Start bis Ende ohne Unterbrechung
- **Keine Reflexivität**: Keine Eingriffsmöglichkeit während der Ausführung
- **Nutzer-Rolle**: User als "Konsumenten" die Knöpfe drücken und Produkte erhalten
- **Kapitalistischer Rahmen**: Fokus auf Effizienz und Output, nicht auf Prozess und Verständnis

### 1.2 Die Vision: Prozessorientiertes, empowerndes Lernen

Das **AI4ArtsEd-Projekt** verfolgt eine **gegenhegemoniale, prozessorientierte Pädagogik**:

- **Reflexivität**: Lernende sollen AI-Prozesse verstehen, hinterfragen, beeinflussen
- **Transparenz**: Nicht "Black Box", sondern nachvollziehbare Schritte
- **Empowerment**: Nicht passive Nutzer, sondern aktive Gestalter
- **Haltungen statt Stile**: Nicht "male wie Picasso", sondern "male mit dadaistischer Haltung"
- **Zeithistorische Kontextualisierung**: KI-Kunst als Teil kultureller und gesellschaftlicher Diskurse

**Zentrale These**: Generative AI als pädagogisches Medium erfordert **Unterbrechung der Linearität**, **Sichtbarmachung von Prozessen** und **Ermöglichung von Reflexion**.

---

## 2. Der erste Befreiungsschritt: Custom Nodes

### 2.1 Prompt Interception Node - Die Schlüsselinnovation

Die **`ai4artsed_prompt_interception.py`** Custom Node ist der erste technische Ausdruck der pädagogischen Vision.

#### 2.1.1 Was ist Prompt Interception?

**Definition**: Ein LLM "fängt" den User-Prompt ab, verarbeitet ihn nach spezifischen Anweisungen, und gibt einen transformierten Prompt weiter.

**Technische Struktur**:
```python
def run(self, input_prompt, input_context, style_prompt, ...):
    full_prompt = (
        f"Task:\n{style_prompt.strip()}\n\n"
        f"Context:\n{input_context.strip()}\nPrompt:\n{input_prompt.strip()}"
    )
    # LLM-Aufruf (Ollama lokal oder OpenRouter cloud)
    output_text = call_llm(full_prompt, model, ...)
    return output_text
```

**Drei-Schicht-Prompt-Struktur**:
1. **Task** (`style_prompt`): Was soll mit dem Prompt passieren? (z.B. "Übersetze zu Englisch", "Transformiere in Dadaismus")
2. **Context** (`input_context`): Zusatzinformationen (z.B. Zielsprache, kultureller Hintergrund)
3. **Prompt** (`input_prompt`): Der eigentliche User-Input oder Output des vorherigen Nodes

#### 2.1.2 Pädagogische Bedeutung

**Problem gelöst**: ComfyUI würde Prompts direkt an Bildgeneratoren senden. Prompt Interception **unterbricht** diesen Fluss und ermöglicht:

1. **Transformation statt Reproduktion**: Prompts werden nicht 1:1 verwendet, sondern pädagogisch geformt
2. **Sichtbarkeit**: Die Transformation ist explizit definiert im `style_prompt` (nicht hidden in einem Modell)
3. **Verkettbarkeit**: Nodes können hintereinander geschaltet werden → iterative Prozesse
4. **Flexibilität**: Lokale (Ollama) und Cloud-Modelle (OpenRouter) austauschbar

**Beispiel - Dada-Workflow (Haltung statt Stil)**:

**Zentrale pädagogische Unterscheidung**: Es geht **nicht** um Stil-Imitation ("male wie Picasso"), sondern um **künstlerische Haltung** (Dadaismus als Reaktion auf Zeitumstände). Idealerweise würde die Zeitsituation und Ästhetik ohne Label-Verwendung beschrieben.

- Input: "Ein Hund bellt im Garten"
- Context-Prompt (gekürzt):
```
You are an artist working in the spirit of Dadaism. Your best friend gave
you this 'input_prompt'. Do not interpret this as a direct instruction of
what to paint, but rather as a spark, a provocation, a fragment of the
everyday to which you respond.

Reflect on how the Dadaists responded to the absurdities of their time
(war, philistinism, established art forms): with mockery, irony, nonsense,
chance, and provocation — but also with deep playfulness and surprising poetry.

You are inspired by artists such as Hugo Ball, Emmy Hennings, Tristan Tzara,
Hans Arp, Sophie Taeuber-Arp, Hannah Höch, Marcel Duchamp, Man Ray,
Kurt Schwitters, Max Ernst, [...]

Think about their approaches to art! Avoid clichés (including Dada clichés).
Do not automatically use skulls or newspaper collages just because they are
"Dada-esque". Be original in your response to the specific 'input_prompt'.
```

- Output (beispielhaft): "A garden barks at a dog while clouds taste the number seven"

**Pädagogischer Mehrwert**: Lernende entwickeln eigene künstlerische Position durch Auseinandersetzung mit historischen Haltungen, nicht durch Imitation von Stilmerkmalen.

#### 2.1.3 Technische Features

**Multi-Backend Support**:
- **Ollama (lokal)**: `local/model-name` - kostenfrei, Offline, langsam
- **OpenRouter (cloud)**: `openrouter/provider/model` - kostenpflichtig, schnell, große Modelle

**DevServer-Erweiterung**: Weitere API-fähige Backends wie LMStudio, deutsche DS-GVO-konforme Anbieter

**Intelligentes Fallback-System**:
```python
def find_openrouter_fallback(self, failed_model, ...):
    # Priorität 1: Gleicher Provider (anthropic → anthropic)
    # Priorität 2: Ähnliche Größe (70b → 64b)
    # Priorität 3: Allgemeine Fallbacks (claude-3.5-haiku, llama-3.2-1b)
```

**Multi-Format Output**:
- `output_str`: Vollständiger Text
- `output_float`: Extrahierte Zahl (deutsche/englische Formate)
- `output_int`: Ganzzahl
- `output_binary`: Boolean (für Verzweigungen im Workflow)

**Unload-Mechanismus**:
- `unload_model: yes` → Modell nach Nutzung aus VRAM entfernen (wichtig bei GPU-Limits)

### 2.2 Weitere Custom Nodes

#### ai4artsed_switch_promptsafety.py
**Zweck**: Multi-Layer-Sicherheitssystem für Kinder und Jugendliche

**Pädagogische Logik**:
- **Level "off"**: Keine Manipulation (für Erwachsene/Expert Mode)
- **Level "youth"**: Prompt wird entschärft, abstrakt umformuliert
- **Level "kids"**: Bei problematischen Inhalten → Prompt komplett ersetzt durch Katze + Text "Sorry too scary!"

**Technische Umsetzung**: Nutzt eigenes LLM zur Prompt-Analyse und -Transformation

**DevServer-Optimierung**: Effizienter durch Image-Analyse am Ende der Pipeline (nicht nur Prompt-Check)

#### ai4artsed_random_language_selector.py
**Zweck**: Wählt zufällige Sprache aus einer Liste

**Pädagogische Funktion**: Ermöglicht "Stille Post" (siehe unten) - semantischer Drift durch Mehrfachübersetzung

#### ai4artsed_image_analysis.py
**Zweck**: Vision-LLM analysiert hochgeladenes Bild und gibt Beschreibung zurück

**Pädagogische Funktion**: Reflexion über AI-Wahrnehmung - "Wie sieht die KI mein Bild?"

---

## 3. Legacy-Server Architektur

### 3.1 Technologie-Stack

```
┌─────────────────────────────────────────┐
│         Frontend (public/)              │
│    HTML + CSS + JavaScript              │
│    (Server-Side Rendered)               │
│  Mehrsprachigkeit: DE/EN (partiell)     │
│  Limitation: Nicht alle UI-Elemente     │
│  und Meldungen übersetzt                │
└────────────────┬────────────────────────┘

                 │ HTTP Requests
┌────────────────▼────────────────────────┐
│      Flask + Waitress Server            │
│         (server/server.py)              │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     Application Factory Pattern         │
│      (server/my_app/__init__.py)        │
│  • Blueprint Registration               │
│  • CORS Configuration                   │
│  • Logging Setup                        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│          Blueprints (Routes)            │
│   (server/my_app/routes/)               │
│                                         │
│  • workflow_routes.py (⭐ ZENTRAL)      │
│  • comfyui_proxy (Medien-Download)      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Services (Business Logic)        │
│    (server/my_app/services/)            │
│                                         │
│  • workflow_logic_service.py            │
│  • comfyui_service.py                   │
│  • ollama_service.py                    │
│  • export_manager.py                    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         External Systems                │
│                                         │
│  ┌─────────────┐  ┌──────────────┐     │
│  │   ComfyUI   │  │   Ollama     │     │
│  │  (Workflows)│  │   (LLMs)     │     │
│  └─────────────┘  └──────────────┘     │
│  ┌─────────────┐                       │
│  │ OpenRouter  │                       │
│  │ (Cloud LLMs)│                       │
│  └─────────────┘                       │
└─────────────────────────────────────────┘
```

### 3.2 Zentrale Komponente: workflow_routes.py

**Hauptendpoint**: `/run_workflow`

**Ablauf bei einem Request**:

```
1. User sendet Prompt + Workflow-Auswahl + Settings
                ↓
2. [PRE-PIPELINE] ollama_service.validate_and_translate_prompt()
   ├─ Schritt 1: Übersetzung zu Englisch (TRANSLATION_MODEL)
   ├─ Schritt 2: Safety Check (SAFETY_MODEL - llama-guard-3:8b)
   └─ Bei Ablehnung: STOP, Fehler an User
                ↓
3. workflow_logic_service.py lädt JSON aus /workflows
                ↓
4. Runtime-Manipulation des Workflows:
   ├─ apply_eco_or_fast_mode() → Modelle austauschen
   ├─ inject_prompt() → User-Prompt in Node schreiben
   ├─ set_image_dimensions() → Aspekt-Ratio anpassen
   ├─ set_seed() → Zufalls-Seed setzen
   ├─ configure_safety_node() → Safety-Level an Custom Node übergeben
   ├─ enhance_negative_prompts() → Sicherheitsterme hinzufügen
   ├─ resolve_model_paths() → Modelle finden (auch wenn verschoben)
   └─ apply_hidden_commands() → #notranslate#, #cfg:x#, #steps:x# etc.
                ↓
5. comfyui_service.submit_workflow() → JSON an ComfyUI senden
                ↓
6. ComfyUI führt Workflow aus:
   ├─ Custom Nodes werden aktiviert (z.B. Prompt Interception)
   ├─ Bildgenerierung erfolgt
   └─ Ergebnis wird in ComfyUI gespeichert
                ↓
7. Frontend pollt /workflow-status/<prompt_id>
                ↓
8. Bei Fertigstellung: Medien-URL(s) zurück an Frontend
   Mediensorten: Bilder (Standard), Text, Audio, mehrere Bilder
   Theoretisch möglich: Video (in Legacy nicht implementiert)
                ↓
9. export_manager.py speichert Ergebnis + Metadaten
   **Forschungsdaten** (zentral für Projektevaluation)
```

### 3.3 Hidden Commands - Power-User-Features

**Problemstellung**: UI soll einfach bleiben (für Kinder), aber Experten brauchen Kontrolle.

**Lösung**: Commands direkt in den Prompt schreiben, Server parst sie vor Verarbeitung.

**Implementiert** (helpers.py: `parse_hidden_commands`):

| Command | Funktion | Beispiel |
|---------|----------|----------|
| `#notranslate#` | Überspringt PRE-PIPELINE Translation | `#notranslate# A cat on a mat` |
| `#cfg:x#` | Überschreibt CFG-Wert aller KSampler | `#cfg:7.5# Dramatic sunset` |
| `#steps:x#` | Überschreibt Steps aller KSampler | `#steps:50# High detail portrait` |
| `#seed:x#` | Setzt fixen Seed | `#seed:42# Reproducible result` |
| `#negative:terms#` | Fügt Terms zu allen Negative Prompts | `#negative:cartoon, anime# Photorealistic scene` |

**Pädagogische Bedeutung**:
- **Transparenz**: Funktionen sind dokumentiert, nicht versteckt
- **Opt-In Komplexität**: Anfänger ignorieren sie, Experten nutzen sie
- **Debugging**: Lehrer können Fehler schneller eingrenzen

---

## 4. Pädagogische Workflows - Beispiele

**Hinweis**: "Stille Post" wird hier ausführlich behandelt, da es Pseudo-Rekursivität gut illustriert. Die Basis aller pädagogischen Workflows ist jedoch **Prompt Interception** - diese Idee bildet sich auch in einfacheren Workflows ab. Weitere wichtige Workflow-Typen:
- **Ästhetisch-komparative Workflows**: Image-to-Sound (medienübergreifend)
- **Technisch-dekonstruktive Workflows**: "Surrealization" (Sichtbarmachung von AI-Prozessen)

### 4.1 "Stille Post" - Konzept

**"Stille Post"** (Englisch: "Telephone Game") ist ein Kinderspiel: Eine Nachricht wird von Person zu Person geflüstert und verändert sich dabei.

**Pädagogische Ziele**:
- **Semantischer Drift**: Verständnis für Bedeutungsverschiebungen in AI-Systemen
- **Kulturelle Hegemonie**: Fehlende Sprachen offenbaren anglozentrische/west-zentrische Bias in LLMs
- **Übersetzung als Interpretation**: Nicht neutrale Abbildung, sondern aktive Konstruktion
- **"Lost in Translation"**: Sichtbarmachung von Bedeutungsverlust und -wandel
- **Spielerische Subversion**: Spaßfaktor im absichtlichen Misslingen/Verschieben

### 4.2 Technische Umsetzung im Legacy-Server

**Workflow**: `/workflows/semantics/ai4artsed_StillePost_2506232347.json`

**Struktur** (vereinfacht):
```
User-Input: "Ein Hund bellt im Garten"
     ↓
[ai4artsed_random_language_selector] → Wählt z.B. ["French", "Japanese", "Spanish", "Russian"]
     ↓
[ai4artsed_prompt_interception #1]
  style_prompt: "Translate to French. Only translate, no comments."
  → Output: "Un chien aboie dans le jardin"
     ↓
[ai4artsed_prompt_interception #2]
  style_prompt: "Translate to Japanese. Only translate, no comments."
  → Output: "犬が庭で吠えています"
     ↓
[ai4artsed_prompt_interception #3]
  style_prompt: "Translate to Spanish. Only translate, no comments."
  → Output: "Un perro está ladrando en el jardín"
     ↓
[ai4artsed_prompt_interception #4]
  style_prompt: "Translate to Russian. Only translate, no comments."
  → Output: "Собака лает в саду"
     ↓
[ai4artsed_prompt_interception #5]
  style_prompt: "Translate to English. Only translate, no comments."
  → Output: "A dog is barking in the garden" (leicht verändert!)
     ↓
[Bildgenerierung mit finalem Prompt]
```

**Verkettung im JSON**:
```json
"105": {
  "inputs": {
    "input_prompt": ["92", 0],  // User-Input
    "input_context": ["58", 0],  // Language 1
    "style_prompt": "Only translate to the given language..."
  }
},
"106": {
  "inputs": {
    "input_prompt": ["105", 0],  // Output von Node 105!
    "input_context": ["58", 1],  // Language 2
    "style_prompt": "Only translate to the given language..."
  }
}
```

### 4.3 Limitation in ComfyUI

**Problem**: Die Kette ist **statisch und linear** (Prinzip: Vermeidung von Rekursion/Loops im Prozessfluss). Man kann nicht:

- Zwischenergebnisse anzeigen lassen
- Die Kette unterbrechen und manuell eingreifen
- Anzahl der Schritte dynamisch ändern
- Eine Schleife bauen (nur durch Copy-Paste von Nodes)

**Workaround**: 9 Prompt Interception Nodes manuell verketten = **Pseudo-Rekursivität**

**Erkenntnis**: Dies ist **ein** Grund für den DevServer - aber nicht der Hauptgrund!

### 4.4 Hauptmotivation für DevServer: Empirische Befunde

**Kritisches Problem** aus Workshop-Evaluationen:

**Befund**: Der Legacy-Werkraum verleitet Kunstpädagog*innen dazu, den **Weg des geringsten Widerstands** zu gehen:
- Nutzung von SD 3.5 large **ohne** Prompt Interception
- Solutionistische Verwendung statt reflexive Aneignung
- Keine Meta-Prompt-Gestaltung (die das "Material" des Kunstkurses definieren würde)

**Erforderliche Lösung - DevServer Edit-Interface**:

1. **Für Klientel (Lernende)**:
   - Selbst Meta-Prompts schreiben
   - Urteile formulieren über das, was erreicht werden soll
   - LLM-Dialog-Unterstützung beim Meta-Prompt-Schreiben
   - **Aktive Aneignung als Standard**, nicht als Option

2. **Für Kunstpädagog*innen**:
   - Meta-Prompts als "vorbereitetes Material" verstehen (analog zu Papier, Farben im klassischen Kunstunterricht)
   - Pädagogische Intentionen explizit formulieren
   - Keine Umgehung der reflexiven Ebene mehr möglich

**Ziel**: Solutionistische Nutzung strukturell verhindern, prozessorientiertes Lernen als Default.

---

## 5. Multi-Layer Security Pipeline

### 5.1 Warum Multi-Layer?

**Problem**: Einfache Filter können umgangen werden ("Jailbreaking").

**Lösung**: Mehrere Sicherheitsebenen, die sich gegenseitig ergänzen.

**Pädagogische Dimension**: Sicherheit nicht als Zensur, sondern als **Schutzraum für reflexives Lernen**.

>> BLeibt grundlegend erhalten, kann aber ggf. eleganter konsolidiert werden; ggf. auch durch abschließenden kombinierten Text-Bild-Sicherheitscheck. <<

### 5.2 Die drei Layers

#### Layer 1: Server-Side Pre-Processing (ollama_service.py)

**Schritt 1.1 - Translation**:
```python
TRANSLATION_PROMPT = """Translate to English. CRITICAL RULES:
1. Preserve ALL brackets exactly: (), [], {{}}, ((()))
2. Do NOT remove or modify any brackets
3. Maximal semantic preservation
4. Do not paraphrase, interpret, or summarize
..."""
translated_prompt = ollama_service.translate_text(user_prompt)
```

**Warum zuerst Übersetzen?**
- Safety-Modelle sind primär auf Englisch trainiert
- Deutsche Umgehungsversuche würden sonst funktionieren

**Schritt 1.2 - Guard Model Check**:
```python
SAFETY_MODEL = "llama-guard-3:8b"
result = ollama_service.check_safety(translated_prompt)
if not result["is_safe"]:
    return ERROR  # Request wird HIER gestoppt!
```

**Spezialisiertes Modell**: `llama-guard-3` ist für Safety-Checks trainiert.

#### Layer 2: Server-Side Workflow Manipulation

**Schritt 2.1 - Safety Node Konfiguration**:
```python
def configure_safety_node(workflow_json, safety_level):
    # Findet ai4artsed_switch_promptsafety Node
    # Setzt filter_level: "off" / "youth" / "kids"
```

**Schritt 2.2 - Negative Prompt Injection**:
```python
DEFAULT_NEGATIVE_TERMS = "blurry, bad quality, distorted, ..."

SAFETY_NEGATIVE_TERMS = {
    "kids": [
        "violence, blood, weapons, death, injury",
        "scary, horror, frightening, dark atmosphere",
        "sexual content, nudity, intimate situations",
        "psychological distress, anxiety, fear",
        ...
    ],
    "youth": [...]  # Weniger strikt
}

def enhance_negative_prompts(workflow_json, safety_level):
    for node in find_all_ksampler_nodes(workflow_json):
        node["negative_prompt"] += DEFAULT_NEGATIVE_TERMS
        if safety_level in ["kids", "youth"]:
            node["negative_prompt"] += SAFETY_NEGATIVE_TERMS[safety_level]
```

**Pädagogische Logik**:
- **Proaktiv**: Verhindert problematische Inhalte, bevor sie entstehen
- **Nicht-invasiv**: User-Prompt wird nicht verändert, nur Negative Prompts erweitert
- **Transparent**: In Docs erklärt, nicht hidden

**Technisches Problem**: Negative-Prompt-Injection kann zu optischer Verzerrung/Qualitätsreduktion führen (Trade-off: Sicherheit vs. Bildqualität)

#### Layer 3: In-Workflow Prompt Manipulation (Custom Node)

**Custom Node**: `ai4artsed_switch_promptsafety.py`

**Ausführung in ComfyUI** (nachdem Workflow submitted wurde):

```python
# Pseudo-Code der Custom Node
def run(self, prompt, filter_level):
    if filter_level == "off":
        return prompt  # Keine Änderung

    elif filter_level == "youth":
        instruction = MANIPULATION_INSTRUCTIONS["youth"]
        # LLM transformiert Prompt: Entschärfung, Abstraktion
        transformed = llm_call(prompt, instruction)
        return transformed

    elif filter_level == "kids":
        instruction = MANIPULATION_INSTRUCTIONS["kids"]
        analysis = llm_call(prompt, "Is this scary for kids? Yes/No")

        if analysis == "Yes":
            # HÄRTER FALLBACK - Prompt komplett ersetzen!
            return "A small, frightened kitten finds comfort..."
        else:
            transformed = llm_call(prompt, instruction)
            return transformed
```

**MANIPULATION_INSTRUCTIONS["kids"]** (aus Custom Node):
```
You are a safety filter for children's content (ages 6-12).
Analyze this image prompt and rewrite it to be:
- Completely non-violent
- Non-frightening
- Age-appropriate
- Positive emotional tone

If the prompt contains ANY potentially scary elements, respond with:
"REJECT: [brief reason]"

Otherwise, rewrite the prompt to be child-friendly.
```

**Bekanntes Problem**: Filter reagiert teilweise unverständlich - z.B. löst das harmlose Wort "player" den Filter aus (False Positives). Verbesserungsbedarf für DevServer.

### 5.3 Zusammenspiel der Layers

**Beispiel-Request**: User (Kind, 8 Jahre alt) gibt ein: "Ein gruseliger Zombie mit blutigem Gesicht"

**Layer 1 (Server - Pre-Pipeline)**:
- Translation: "A scary zombie with bloody face"
- Guard Model: ⚠️ "POTENTIALLY UNSAFE" → **Request könnte hier schon gestoppt werden**
- Aber: Angenommen es passiert (um Layer 2+3 zu zeigen)

**Layer 2 (Server - Workflow Manipulation)**:
- Safety Node: `filter_level = "kids"`
- Negative Prompts erweitert um: `"violence, blood, scary, horror, frightening, ..."`
- → Selbst wenn der Prompt durchkommt, versucht das Bildmodell aktiv, Blut/Grusel zu vermeiden

**Layer 3 (ComfyUI - Custom Node)**:
- `ai4artsed_switch_promptsafety` empfängt: "A scary zombie with bloody face"
- Analyse: "Is this scary for kids?" → "Yes, contains violence and fear elements"
- **Kids-Filter-Fallback aktiviert**: Prompt wird **komplett ersetzt** durch:
  - Hartcodierter Katzen-Prompt + Text "Sorry too scary!"

**Ergebnis**: Bild zeigt eine Katze mit Entschuldigungs-Text, kein Zombie.

**Hinweis**: Der **Youth-Filter** würde subtiler vorgehen: Umformulierung zu "A small, friendly creature with green skin playing in a colorful garden"

### 5.4 Pädagogische Reflexion über Safety

**Kritische Frage**: Ist das nicht Zensur?

**Differenzierung**:
- **Zensur** = Unterdrückung von Meinungen/Inhalten durch Machtstrukturen
- **Schutzraum** = Altersgerechte Umgebung für explorativen Umgang mit Technologie

**Pädagogisches Argument**:
1. **Entwicklungspsychologie**: 6-12-Jährige sind noch nicht in der Lage, mit verstörenden Bildern angemessen umzugehen
2. **Empowerment-Paradox**: Echte Handlungsfähigkeit erfordert sichere Experimentierräume
3. **Opt-Out**: Expert Mode erlaubt `safety_level: "off"` für ältere Lernende

**Transparenz**: Das System versteckt die Manipulation nicht, sondern **macht sie zum Lerngegenstand**:
- "Warum hat die KI meinen Prompt verändert?"
- "Wie entscheidet das System, was 'sicher' ist?"
- "Was ist die Rolle von AI-Safety in der Gesellschaft?"

**DevServer-Verbesserung**: Ausführlichere Begründungen durch LLM - Artikulation des Problems auf verschiedenen Ebenen (rechtlich, ethisch, ästhetisch, entwicklungspsychologisch)

---

## 6. Eco vs. Fast Mode - Ökonomie und Zugang

### 6.1 Problemstellung

**Konflikt**:
- **Lokale Modelle** (Ollama): Kostenlos, offline, langsam, begrenzte Qualität
- **Cloud Modelle** (OpenRouter): Teuer (GPT-4: $60/1M tokens), schnell, hohe Qualität

**Pädagogische Frage**: Wie demokratisieren wir Zugang zu guter AI, ohne Budget zu sprengen?

### 6.2 Technische Lösung

**Two-Mode System**:

| Aspekt | Eco Mode | Fast Mode |
|--------|----------|-----------|
| Backend | Ollama (lokal) | OpenRouter (cloud) |
| Kosten | $0 | $0.10-$60/1M tokens |
| Geschwindigkeit | Langsam (30-60s) | Schnell (2-5s) |
| Qualität | Gut (gemma2:9b, mistral-nemo) | Exzellent (GPT-4, Claude) |
| Offline | ✅ Ja | ❌ Nein |
| Use Case | Tägliche Arbeit, Workshops | Demos, finale Ergebnisse |

**Implementierung** (workflow_logic_service.py):

```python
# Model-Mapping in config.py
OLLAMA_TO_OPENROUTER_MAP = {
    "gemma2:9b": "google/gemini-2.5-flash",
    "llama3.2:latest": "meta-llama/llama-3.3-70b-instruct",
    "mistral-nemo:latest": "mistralai/mistral-nemo"
}

OPENROUTER_TO_OLLAMA_MAP = {
    "google/gemini-2.5-flash": "gemma2:9b",
    "meta-llama/llama-3.3-70b-instruct": "llama3.2:latest",
    ...
}

def apply_eco_or_fast_mode(workflow_json, mode):
    if mode == "eco":
        # Durchsuche Workflow nach Cloud-Modellen
        for node in find_all_prompt_interception_nodes(workflow_json):
            old_model = node["model"]
            if old_model.startswith("openrouter/"):
                new_model = OPENROUTER_TO_OLLAMA_MAP.get(old_model, "gemma2:9b")
                node["model"] = f"local/{new_model}"

    elif mode == "fast":
        # Umgekehrt: Lokale Modelle → Cloud
        for node in find_all_prompt_interception_nodes(workflow_json):
            old_model = node["model"]
            if old_model.startswith("local/"):
                new_model = OLLAMA_TO_OPENROUTER_MAP.get(old_model, "google/gemini-2.5-flash")
                node["model"] = f"openrouter/{new_model}"
```

**Fallback-Logik**: Wenn ein Modell nicht verfügbar ist, sucht das System automatisch Alternativen (siehe Prompt Interception Node).

### 6.3 Pädagogische Implikationen

**Bildungsgerechtigkeit**:
- Schulen ohne Budget können Eco Mode nutzen (nur Hardware-Kosten)
- Privilegierte Institutionen können Fast Mode für bessere Ergebnisse nutzen
- **Gleicher Zugang zur Pädagogik**, unterschiedliche Qualität akzeptabel

**DS-GVO-Konformität**:
- **Grundsatz**: Hochgeladene Bilder werden **niemals** nach außen weitergegeben
- Eco Mode (lokal) ist DS-GVO-konform
- Fast Mode (OpenRouter): Nur Text-Prompts, keine Bilder

**DevServer-Challenge**: Bei flexiblen Backends + Input-Bild-Verarbeitung besteht Risiko, dass Selbstportraits von Kindern an externe APIs gesendet werden
- **Lösung A**: DS-GVO-kompatible Backends hartcodiert kennzeichnen
- **Lösung B**: Bild-Verarbeitung nur lokal (Ollama Vision Models)

**Reflexion über AI-Ökonomie**:
- "Warum ist Cloud-AI teuer?" → Diskussion über Geschäftsmodelle
- "Wer kann sich AI leisten?" → Kritische Medienbildung
- "Was bedeutet 'Open Source' bei AI-Modellen?" → Technologische Souveränität

---

## 7. Internationalisierung - Sprache als politische Entscheidung

### 7.1 Technische Lösung

**metadata.json** - Manuelle zweisprachige Metadaten:
```json
{
  "ai4artsed_Dada_2506251624.json": {
    "name": {
      "de": "Dada",
      "en": "Dada"
    },
    "description": {
      "de": "Transformiert Prompts im Stil der Dada-Bewegung: absurd, subversiv, anti-rational.",
      "en": "Transforms prompts in the style of the Dada movement: absurd, subversive, anti-rational."
    },
    "category": {
      "de": "Künstlerische Haltungen",
      "en": "Artistic Attitudes"
    }
  }
}
```

**Frontend lädt passende Sprache**:
```javascript
const language = getUserLanguage();  // "de" oder "en"
const workflowName = metadata[workflow].name[language];
```

### 7.2 Warum NICHT automatische Übersetzung?

**Versuchte Ansätze** (laut Dev Log):
1. Automatische LLM-Übersetzung → zu teuer, zu langsam
2. Übersetzungs-API → zusätzliche Abhängigkeit, Kosten
3. Statische Übersetzungs-Files → schwer zu warten bei 30+ Workflows

**Gewählte Lösung**: Manuell, aber zentral in einer Datei.

**Vorteil**: Qualitätskontrolle, kulturelle Angemessenheit (nicht nur wörtliche Übersetzung).

**Hintergrund**: Damaliges LLM (Gemini 2.5 Pro, Claude Opus 4) scheiterte an eleganterer automatischer Lösung ("Vibe-Coding"-Problem). Kosten: ca. 40$, 3h Arbeitszeit.

### 7.3 Politische Dimension

**Frage**: Warum Deutsch + Englisch, nicht mehr Sprachen?

**Kontext**:
- Projekt läuft in Deutschland (BMBF-gefördert)
- Englisch als Wissenschaftssprache
- **Aber**: Mehrsprachigkeit als Feature geplant (siehe "Stille Post")

**Pädagogische Haltung**:
- Sprache ist nicht neutral - sie transportiert Weltbilder
- Übersetzung ist Interpretation, keine Abbildung
- AI-Systeme sind sprachlich vorbelastet (meist Englisch-zentriert)

**Reflexionspotential**:
- "Warum funktioniert das LLM besser auf Englisch?"
- "Was passiert mit deutschen Begriffen ohne englische Entsprechung?" (z.B. "Waldeinsamkeit")
- "Wer bestimmt, welche Sprachen in AI-Systemen repräsentiert sind?"

**Zentrale Design-Entscheidung (Gerechtigkeitsgedanke)**:

**Problem**: CLIP_g versteht Deutsch besser als kleinere Sprachen/Dialekte → würde bevorzugt werden

**Lösung**: **Alle** Prompts werden zu Englisch (lingua franca) übersetzt → gleiche Ausgangsbedingungen

**Trade-off akzeptiert**:
- Wir entgehen dem Anglozentrismus **nicht** (empirische Forschungen zeigen anglo/westzentrische Bias im Bildoutput)
- **Aber**: Wir prolongieren keine **zusätzliche** Ungleichbehandlung durch CLIP
- Kleinere Sprachen stehen nun gleichberechtigt zu Deutsch (alle werden übersetzt)

---

## 8. Export-Funktion - Dokumentation als Reflexionsinstrument

### 8.1 Zweck

**Nicht nur Archivierung**, sondern **pädagogisches Werkzeug und Forschungsdaten**:
- **Primär**: Forschungsdaten für Projektevaluation, wissenschaftliche Publikationen
- Nachvollziehbarkeit: "Wie wurde dieses Bild erzeugt?"
- Vergleichbarkeit: "Was ändert sich, wenn ich den Prompt variiere?"

**Datenschutz-Policy**:
- **Keine IP-Adressen** gespeichert
- Anonymisierte Exports
- Session-IDs statt User-Tracking

### 8.2 Technische Umsetzung

**export_manager.py** sammelt:
- Generiertes Bild (PNG/JPG)
- Original-Prompt (User-Input)
- Transformierter Prompt (nach Interception)
- Workflow-Name
- Timestamp
- Settings (Seed, Steps, CFG, Safety Level, Eco/Fast Mode)

**Export-Formate**:
- **HTML**: Interaktive Galerie mit allen Infos
- **PDF**: Druckbare Dokumentation
- **DOCX**: Editierbar für Berichte
- **XML**: Maschinenlesbar für Analyse

**Speicherort**: `/exports/<session_id>/`

### 8.3 Pädagogisches Potential

**Beispiel Workshop-Ablauf**:
1. Kinder erstellen 10 Bilder mit verschiedenen Prompts
2. Am Ende: Export als HTML-Galerie
3. Gemeinsame Reflexion:
   - "Welches Bild gefällt euch am besten? Warum?"
   - "Welcher Prompt hat zu überraschenden Ergebnissen geführt?"
   - "Was hat die KI anders interpretiert als ihr dachtet?"

**Forschungsdaten**:
- Anonymisierte Exports für wissenschaftliche Studien
- Analyse: Welche Prompts führen zu problematischen Outputs?
- Evaluation: Wie gut funktioniert das Safety-System?

*Hinweis: Workshop-Ablauf-Beispiel dient der Illustration, Kern ist die Forschungsdaten-Funktion*

---

## 9. Grenzen des Legacy-Servers - Warum DevServer?

### 9.1 Fundamentale Beschränkungen durch ComfyUI

**Problem 1: Statische Workflows**
- Jede neue Funktion = neues JSON-File
- 30+ Workflows = massive Redundanz
- Änderungen an gemeinsamen Komponenten = 30x manuelles Editing

**Problem 2: Keine echte Rekursivität**
- "Stille Post" = 9 manuell verkettete Nodes (Pseudo-Rekursivität)
- Anzahl der Iterationen hardcoded, nicht dynamisch
- Keine Abbruchbedingungen möglich

**Problem 3: Keine Runtime-Interaktivität**
- Workflow läuft von Start bis Ende durch
- Keine Unterbrechung für User-Feedback
- Keine Verzweigungen basierend auf Zwischenergebnissen

**Problem 4: Komplexität versteckt in JSONs**
- Workflows sind technisch, nicht pädagogisch lesbar
- Lehrer können Workflows nicht selbst anpassen
- Black Box für Nicht-ComfyUI-Experten

### 9.2 Pädagogische Grenzen

**Vision vs. Realität**:

| Pädagogische Vision | Legacy-Server Status | DevServer Ziel |
|---------------------|----------------------|----------------|
| Reflexive Unterbrechungen | Nicht möglich | Möglich (Pause-Points) |
| User editiert Pipeline | Zu komplex | Visuell/Dialog-basiert |
| Echte Rekursivität | Pseudo (9 Nodes) | Native Loops |
| Prozess-Sichtbarkeit | Nur am Ende | Schritt für Schritt |
| Zielgruppen-Modi | Ein Interface | Play/Dialog/Expert |

**Beispiel - Was DevServer ermöglichen wird**:

**Stille Post 2.0** (DevServer):
```
User: "Ein Hund bellt im Garten"
  → [Pipeline Step 1: Übersetze zu zufälliger Sprache]
    Output: "Un chien aboie dans le jardin"

[PAUSE - Zeige Zwischenergebnis]
System: "Die KI hat übersetzt zu: 'Un chien aboie dans le jardin' (Französisch). Weitermachen?"
User: [Ja] / [Nein] / [Sprache ändern]

  → [Pipeline Step 2: Übersetze zu nächster Sprache]
    Output: "犬が庭で吠えています"

[PAUSE - Zeige Zwischenergebnis]
System: "Jetzt auf Japanisch: '犬が庭で吠えています'. Noch eine Runde?"
User: [Ja, 3 weitere] / [Nein, generiere jetzt Bild]

[Loop für 3 weitere Iterationen]

[ENDE - Vergleich]
System zeigt:
- Original: "Ein Hund bellt im Garten"
- Nach 5 Übersetzungen: "A canine creature vocalizes within an outdoor space"
- Semantischer Drift visualisiert!
```

**Dies ist mit ComfyUI unmöglich**, da Workflows keine User-Interaktion während der Ausführung erlauben.

---

## 10. Lessons Learned - Pragmatische Entwicklungsentscheidungen

### 10.1 Technische Entscheidungen

**1. Waitress statt Flask Dev Server** (Juni 2024)
- **Problem**: Flask dev server instabil bei mehreren gleichzeitigen Usern
- **Lösung**: Production-WSGI-Server Waitress
- **Learning**: "Good enough" production setup früh implementieren

**2. Manuelle Metadaten statt Auto-Translation**
- **Problem**: LLM-Übersetzung zu teuer/langsam, externe APIs zu komplex
- **Lösung**: Zentrale `metadata.json` manuell pflegen
- **Learning**: Einfache, wartbare Lösungen > perfekte, komplexe Lösungen

**3. Hidden Commands statt UI-Überfrachtung**
- **Problem**: Alle Features in UI = überwältigend für Kinder
- **Lösung**: Basis-UI einfach, Power-User nutzen `#commands#`
- **Learning**: Progressive Disclosure - Komplexität opt-in

**4. Multi-Layer Security statt Single Filter**
- **Problem**: Einfache Filter umgehbar
- **Lösung**: 3-Layer-Pipeline mit verschiedenen Ansätzen
- **Learning**: Defense in Depth auch für Content-Safety

### 10.2 Pädagogische Entscheidungen

**1. Haltungen statt Stile**
- **Ursprünglich**: "Male im Stil von Picasso"
- **Jetzt**: "Male mit kubistischer Perspektive" / "Male mit dadaistischer Haltung"
- **Warum**: Künstlerische Eigenständigkeit fördern, nicht Imitation

**2. Prozess über Produkt**
- **Ursprünglich**: Schnell zum fertigen Bild
- **Jetzt**: Zwischenschritte sichtbar machen (Prompt Transformation, Übersetzungen)
- **Warum**: Verständnis für AI-Prozesse wichtiger als perfekte Outputs

**3. Safety als Schutzraum, nicht Zensur**
- **Ursprünglich**: Blocklisten, Keyword-Filter
- **Jetzt**: Intelligente Transformation, Fallback-Prompts
- **Warum**: Ermöglicht Exploration ohne Trauma-Risiko

**4. Open Source mit klarer Lizenz**
- **Entscheidung**: GPL-Lizenz für Custom Nodes, Code öffentlich auf GitHub
- **Warum**: Bildungsgerechtigkeit, Nachnutzbarkeit, Transparenz

### 10.3 Gescheiterte Ansätze (wichtig für DevServer!)

**1. Stateful Server** (verworfen - **für Legacy**)
- **Idee**: Server merkt sich User-Sessions, erlaubt mehrstufige Workflows
- **Problem**: Damaliges Coding-LLM (Gemini 2.5 Pro) scheiterte krachend - Komplexität zu hoch
- **Kosten**: ca. 30-40$, 3+ Stunden Arbeitszeit
- **Learning für Legacy**: Stateless besser, zu komplex für damalige LLMs
- **DevServer-Entscheidung**: **Wird stateful sein** (mit besseren LLMs/mehr Zeit machbar)

**2. Vollautomatische Workflow-Generierung** (verworfen)
- **Idee**: LLM generiert ComfyUI-JSON basierend auf User-Anfrage
- **Problem**: LLMs generieren invalide JSONs, zu fehleranfällig
- **Learning**: Template-basiert robuster, aber unflexibel → DevServer Abstraktion nötig

**DevServer-Perspektive**: Wird einfacher! Keine ComfyUI-JSONs mehr zu generieren, nur noch Orchestrierung auf Basis vordefinierter Pipelines

**3. Embed-Everything in ComfyUI** (verworfen)
- **Idee**: Alle Logik in Custom Nodes
- **Problem**: Debugging schwer, Custom Nodes zu mächtig → Sicherheitsrisiko
- **Learning**: Balance zwischen Server-Logic und Node-Logic

---

## 11. Zentrale Dateien - Detaillierte Referenz

### server/config.py
**Zweck**: Zentrale Konfiguration (Modelle, Prompts, Sicherheitsregeln)

**Wichtige Konstanten**:
```python
# LLM-Modelle
TRANSLATION_MODEL = "mistral-nemo:latest"
SAFETY_MODEL = "llama-guard-3:8b"
ANALYSIS_MODEL = "llava:latest"

# Prompts
TRANSLATION_PROMPT = "..."  # Detaillierte Übersetzungsanweisungen
ANALYSIS_SYSTEM_PROMPT = "..."  # Bildanalyse-Kontext

# Sicherheit
DEFAULT_NEGATIVE_TERMS = "blurry, bad quality, ..."
SAFETY_NEGATIVE_TERMS = {
    "kids": ["violence", "blood", ...],
    "youth": [...]
}

# Mappings
OLLAMA_TO_OPENROUTER_MAP = {...}
OPENROUTER_TO_OLLAMA_MAP = {...}

# Feature Flags
ENABLE_VALIDATION_PIPELINE = True
NO_TRANSLATE = False  # Global toggle für #notranslate#
```

### server/my_app/services/workflow_logic_service.py
**Zweck**: Kern-Logik für Workflow-Manipulation

**Hauptfunktionen**:
- `load_workflow(workflow_name)` - JSON aus /workflows laden
- `apply_eco_or_fast_mode(workflow, mode)` - Modelle austauschen
- `inject_prompt(workflow, prompt)` - User-Input in Node schreiben
- `enhance_negative_prompts(workflow, safety_level)` - Sicherheitsterme hinzufügen
- `apply_hidden_commands(workflow, prompt)` - #commands# parsen und anwenden

### server/my_app/services/ollama_service.py
**Zweck**: LLM-Kommunikation (Ollama + OpenRouter)

**Hauptfunktionen**:
- `translate_text(text)` - Übersetzung mit TRANSLATION_MODEL
- `check_safety(text)` - Guard-Model-Check
- `validate_and_translate_prompt(prompt)` - PRE-PIPELINE kombiniert
- `analyze_image(image_data)` - Vision-Model für Bildanalyse

### server/my_app/routes/workflow_routes.py
**Zweck**: API-Endpunkte

**Hauptendpoints**:
- `POST /run_workflow` - Hauptfunktion (siehe Ablauf Abschnitt 3.2)
- `GET /workflow-status/<prompt_id>` - Polling für ComfyUI-Status
- `GET /workflow_metadata` - Metadaten für Frontend
- `GET /comfyui/<path>` - Proxy für Medien-Download

---

## 12. Zusammenfassung - Von Legacy zu DevServer

### 12.1 Was der Legacy-Server erreicht hat

✅ **Technisch**:
- Funktionierende Abstraktion über ComfyUI
- Multi-Backend-Support (Ollama, OpenRouter, ComfyUI)
- Robuste Security-Pipeline
- Export-System für Forschungsdaten

✅ **Pädagogisch**:
- Prompt Interception als Reflexionsinstrument
- Hidden Commands für progressive Disclosure
- Safety als Schutzraum statt Zensur
- "Stille Post" als Beispiel für Pseudo-Rekursivität

**Empirische Validierung**:
- **Funktionierender Pilot-Einsatz**: 5 halbtägige Workshops mit Kunstpädagog*innen + Klientel-Kurse
- **Kernproblem 1 - Timeouts**: Vermutlich durch zu langsame DSL-Anbindung (lokal praktisch nie)
- **Kernproblem 2 - Workflow-Zeiten**: Zu lang (Sicherheitschecks, LLM-Calls, Bildgenerierung sequentiell)
- **Lösung**: Flexibleres, modulares Server-System (DevServer) mit besserer Parallelisierung

### 12.2 Warum DevServer notwendig ist

❌ **Fundamentale Grenzen**:
- ComfyUI-Linearität nicht überwindbar
- Workflow-Redundanz nicht wartbar (30+ JSONs)
- Keine echte Rekursivität/Interaktivität
- Workflows zu technisch für Lehrer/Lernende

✨ **DevServer Vision**:
- **3-Schicht-Architektur**: Chunks (Primitives) → Pipelines (Structure) → Configs (Content)
- **Echte Rekursivität**: Native Loops, Abbruchbedingungen
- **Runtime-Interaktivität**: Pause-Points, User-Feedback
- **Zielgruppen-Modi**: Play (Kinder), Dialog (LLM-geführt), Expert (volle Kontrolle)
- **Pipeline-Editierbarkeit**: Lehrer können Configs anpassen ohne JSON-Kenntnisse

### 12.3 Kontinuität zwischen Legacy und DevServer

**Was bleibt** (Konzepte):
- Prompt Interception (jetzt als Chunk/Pipeline)
- Multi-Layer Security (noch relevanter bei Editierbarkeit)
- Eco/Fast Mode (noch wichtiger bei mehr Flexibilität)
- Hidden Commands (#notranslate# etc.)
- Export-System

**Was sich ändert** (Technik):
- JSON Workflows → deklarative Configs
- ComfyUI-abhängig → Backend-agnostisch
- Statische Ketten → dynamische Pipelines
- Ein Frontend → drei Modi (Play/Dialog/Expert)

---

---

## Appendix: Detaillierte Development-History

Diese chronologische Übersicht zeigt die iterative, pragmatische Entwicklung des Legacy-Servers mit **Kosten und Arbeitszeiten** - wichtig zum Verständnis von Entscheidungen und gescheiterten Ansätzen.

### Juni 2025

**29.6.**: Production-Server-Migration
- Von Flask Development Server auf **Waitress Production Server** umgestellt
- Grund: Instabilität bei Multi-User-Betrieb
- Learning: Production-Setup frühzeitig implementieren

**29.6.**: Bild-Upload-Feature
- Drag & Drop, +Symbol, Smart Device Foto-Aufnahme
- **LLM analysiert Bild** (modifiziert nach Panofsky) lokal
- **Nur Text-Ergebnis** wird an Workflows weitergegeben (nicht das Bild selbst!)
- DS-GVO-konform: Bilder verlassen nie den Server

### Juli 2025

**1.7.**: Stateful Server - **GESCHEITERT**
- Versuch: Server mit Session-State für nichtlineare Workflows
- LLM: Gemini 2.5 Pro
- **Ergebnis**: Krachend gescheitert, Komplexität zu hoch
- **Kosten**: 30-40$, 3+ Stunden
- Learning: Zu komplex für damalige LLMs

**2.7.**: Eco vs. Fast Mode
- Dynamischer Wechsel zwischen Ollama (lokal) und OpenRouter (cloud)
- Intelligenter Failsafe-Algorithmus für Model-Replacement
- Pädagogischer Mehrwert: Bildungsgerechtigkeit

**2.7.**: Deutsche Sprachversion
- UI-Elemente teilweise übersetzt (nicht vollständig)

**5.7.**: Export-Funktion V1
- Automatische Speicherung: TimeCode, User-ID, Session-ID
- Statische Website + PC-Download-Option

**5.7.**: Bilinguale Version - **GESCHEITERT**
- Versuch: Umschaltbare DE/EN-Version mit Platzhaltern
- LLMs: Claude Opus 4 + Gemini 2.5 Pro
- **Problem**: Scheitern an einfacher i18n-Javascript-Aufgabe
- **Kosten**: ca. 40$, 3 Stunden
- Learning: Manuelle Lösung robuster (siehe 19.7.)

**6.7.**: Übersetzungs-Model Update
- Wechsel zu `ollama run thinkverse/towerinstruct`

**6.7.**: Refaktorierung server.py + index.html
- Zu viele Funktionen akkumuliert → Wartbarkeit litt
- **Kosten**: ca. 60$, 4 Stunden
- Learning: Regelmäßige Refaktorierung wichtig (auch für LLMs!)

**7.7.**: Seed-Kontrolle
- Drei Modi: Projekt-Standard (123456789), Zufallszahl, Fixiert
- **Bewusste Entscheidung**: Keine Zahleneingabe (zu technisch, nicht pädagogisch relevant)
- **Kosten**: ca. 5$

**10.7.**: Load-Fail-Problem
- Leichte Verbesserung implementiert
- **Kosten**: ca. 6,50$

**12.7.**: Negations-Problem entdeckt
- Kritischer Bug: Prompts mit "no ..." führen zu unerwarteten Ergebnissen
- Hinweis: TPinf (Forschungspartner) hatte dies nicht gemeldet

**12.7.**: Safety-Filter V1 - **GESCHEITERT**
- Versuch: Kids/Youth-Filter per Radiobutton vor CLIP-Encoder
- LLM: Claude Opus 4
- **Problem**: Starre ComfyUI-Workflow-Logik, nur schwer gezielt manipulierbar
- **Kosten**: 33$, ca. 4 Stunden

**12.7.**: Safety-Filter V2 - **ERFOLG via Custom Node**
- Custom Node `ai4artsed_switch_promptsafety.py` entwickelt
- In alle Workflows integrierbar, vom Werkraum-Interface steuerbar
- **Kosten**: ca. 25$, 3 Stunden
- Learning: Custom Nodes flexibler als Server-Side-Manipulation

**14.7.**: Export-Funktion V2
- Seed + Filter-Status hinzugefügt
- Export-Homepage mit Thumbnails

**14.7.**: Forschungsdaten-Export
- Formate: HTML, PDF, DOCX, XML
- Speicherort: `/server/exports`
- **Kosten**: ca. 25$, 2,5 Stunden

**14.7.**: User-Anzeige (Wartezeit)
- Macht lange Generierungszeiten verständlicher
- **Kosten**: ca. 3$, 10 Minuten

**14.7.**: Kids-Filter Erweiterung
- Kindgerechte Prompt-Manipulation auch bei nicht-explizit-problematischen Prompts

**14.7.**: Negative-Prompt-Injection (Kids-Level)
- Alle Negative Prompts bei Kids-Setting mit Sicherheitsliste befüllt
- Begriffe: Gewalt, Horror, Pornografie
- **Kosten**: ca. 15$, 1,5 Stunden

**15.7.**: Youth-Filter
- Analog zu Kids, aber weniger strikt

**17.7.**: Sicherheit weiter optimiert
- **Kosten**: 20$

**17.7.**: Interface-Verbesserungen
- **Kosten**: 7,50$, 40 Minuten

**17.7.**: Parallele Text+Bild-Eingabe
- Beide gleichzeitig möglich → Bild-Analyse wird an Prompt angehängt
- **Kosten**: 20$

**17.7.**: Automatische Inpaint-Erkennung
- Bei Inpaint-Model: Bild wird als Basis verwendet, nicht analysiert
- Voraussetzung: Bild mit Maskierung im Alpha-Kanal
- Outpainting ebenfalls möglich (Nutzen fraglich)
- **Kosten**: 20$

**17.7.**: OmniGen2 Integration
- Installation + Interface
- **Sicherheitstest**: Nicht Safe by Design!
- Ermöglicht: Bilder verbal bearbeiten

**17.7.**: Intelligente Model-Suchroutine
- Resilienz bei falsch angegebenen Modell-Pfaden
- Findet Modelle auch bei SwarmUI vs. ComfyUI Unterschieden
- **Kosten**: ca. 5$

**17.7.**: Bilinguale Workflow-Anzeige
- User-freundliche Namen statt technischer Bezeichnungen
- Kategorien (änderbar während Theoriebildung)
- Hover-Kurzbeschreibungen + längere Beschreibungen
- **Nebeneffekt**: Export-Funktion "zerschossen" → aufwändiges Debugging
- Workflow-Manual DE/EN erstellt
- **Kosten**: ca. 60$, 5-6 Stunden

**19.7.**: Bilingualität Website
- Erweitert auf Website-Anzeigen (nicht nur Workflows)
- System jetzt international einsatzfähig
- Fehlende Note-Nodes ergänzt, Text-Extraktion korrigiert
- **Kosten**: 153k/200k tokens (76%), ca. 25$, 2,5 Stunden
- **Ergebnis**: Alle 34 Workflows zeigen bilinguale Namen

**19.7.**: Hidden Commands
- **Motivation**: Funktionserweiterung ohne UI-Überlastung/Literacy-Überlastung
- Implementiert:
  - `#notranslate#` → Skip translation
  - `#cfg:x#`, `#seed:x#`, `#steps:x#` → Überschreibt **alle** KSampler im Workflow
  - `#negative:terms#` → Anhängen an alle Negative Prompts
  - `#loop:x#` → **NICHT implementiert** (geplant: Workflow x-mal ausführen)
- **Pädagogisches Ziel**: Progressive Disclosure - Komplexität opt-in

**21.7.**: Workflow-Metadata neu programmiert
- Automatische Lösung war inkonsistent und nicht enduser-sicher
- **Neue Lösung**: Manuelle Einträge in `workflows/metadata.json`
- Fallback: Dateiname wenn kein Eintrag vorhanden
- Learning: Robustheit > Automatisierung

**21.7.**: Hidden Commands teilweise implementiert
- Funktionieren: `#notranslate#`, `#cfg:x#`, `#seed:x#`, `#steps:x#`
- Überschreiben Interface-Einstellungen

**22.7.**: Warteschlangenanzeige - **FEHLGESCHLAGEN**
- Idee: User zeigen, wenn sie warten müssen
- **Problem**: Funktion nicht stabil
- **Kosten**: ca. 10$
- **Ergebnis**: Wieder entfernt

**22.7.**: REUSE IMAGE-Funktion
- Hover-Effekt mit Recycle-Symbol
- Klick → Bild wird oben geladen
- Bei mehreren Bildern: Letztes angeklicktes bleibt

**22.7.**: REUSE TEXT-Funktion
- Jeder erzeugte Text kann ins Promptfeld gesendet werden

**23.7.**: Endnutzer-Anleitung + Developer Documentation
- DE/EN-Versionen halbautomatisiert erstellt
- Verlinkt in Fußzeile
- **Kosten**: 15$ (Gemini Pro 2.5)

### August 2025

**16.8.**: Serverseitige Workflow-Auswahl-Modi
- Konfiguriert in `/server/config.py`, nicht vom Frontend kontrollierbar
- **Drei Modi**:
  1. **USER**: Zufalls-Default aus kategorisierten Workflows (statt erzwungener Auswahl)
  2. **SYSTEM**: Automatische Zufallsauswahl nach Kategorien (später: LLM-basiert auf Prompt reagierend) → System reagiert "unerwartet"
  3. **FIXED**: Server-konfigurierte feste Auswahl (z.B. nur SD 3.5)
- **Kosten**: ca. 6$ (Claude Sonnet 4), ca. 2 Stunden

### Oktober 2025

**6.10.**: Neue Architektur-Versuch - **GESCHEITERT**
- Versuch: Interne Ollama-Textverarbeitung statt ComfyUI-Nodes
- ComfyUI erst am Ende für Bildgenerierung
- LLM: Claude Sonnet 4.1
- **Ergebnis**: Krachend gescheitert
- **Kosten**: ca. 45$, ca. 4 Stunden
- **Erkenntnis**: Notwendigkeit für vollständigen DevServer-Neuansatz

**8.-12.10.**: Schema-Based Server - **ERFOLG**
- Neuer Ansatz: Backend-Implementation 60%
- Workflows noch zu übersetzen
- **Ziel**: Schlankeres, flexibleres Interface (Reaktion auf Workshop-Feedback)
- **Kosten/Zeit**: 8 Stunden
- **Status**: Weg frei für neue UI-Paradigmen

### Gesamtkosten-Übersicht (geschätzt)

**Erfolgreiche Features**: ca. 200-250$, ca. 25-30 Stunden
**Gescheiterte Versuche**: ca. 150-200$, ca. 15-20 Stunden
**Gesamt**: ca. 350-450$, ca. 40-50 Stunden Entwicklungszeit

**Learning**: Iterative Entwicklung mit vielen Fehlversuchen - LLMs (Stand 2025) benötigen menschliche Guidance bei komplexen Architektur-Entscheidungen.

---

## Ende der Legacy-Server-Dokumentation

**Nächster Schritt**: DevServer-Architektur analysieren und dokumentieren.

**Status**: Legacy-Server vollständig verstanden, bereit für Vergleich mit DevServer.
