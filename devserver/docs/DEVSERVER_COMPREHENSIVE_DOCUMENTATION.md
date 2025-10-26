# DevServer: Comprehensive Documentation

**AI4ArtsEd Schema-Based Architecture - Pädagogische, Künstlerische und Technische Perspektiven**

---

## Dokumentationsziel

Diese Dokumentation verbindet technische Architektur mit pädagogisch-künstlerischen Zielen. Sie ergänzt die technische `ARCHITECTURE.md` um:
- Pädagogische Motivationen und empirische Befunde
- Vergleich zu Legacy-Server-Limitationen
- Praktische Anwendungsszenarien
- Zukünftige Entwicklungsrichtungen

**Voraussetzung**: Lesen Sie zuerst `LEGACY_SERVER_ARCHITECTURE.md` und `ARCHITECTURE.md`

---

## Inhaltsverzeichnis

1. [Executive Summary: Warum DevServer?](#executive-summary)
2. [Von ComfyUI zu Schema-Based: Die Evolution](#evolution)
3. [Die Drei-Schicht-Architektur im Detail](#drei-schicht-architektur)
4. [Pädagogischer Paradigmenwechsel](#pädagogischer-paradigmenwechsel)
5. [Technische Überlegenheit](#technische-überlegenheit)
6. [Aktuelle Implementierung (Phase 4)](#aktuelle-implementierung)
7. [Use Cases und Szenarien](#use-cases)
8. [Offene Herausforderungen](#herausforderungen)
9. [Roadmap](#roadmap)

---

## 1. Executive Summary: Warum DevServer?

### Problem-Statement

Der **Legacy-Server** (beschrieben in `LEGACY_SERVER_ARCHITECTURE.md`) funktioniert technisch, scheitert aber an einem **zentralen pädagogischen Ziel**:

**Empirischer Befund aus 5 Workshops**:
- Kunstpädagog*innen nutzen Stable Diffusion 3.5 **ohne** Prompt Interception
- Weg des geringsten Widerstands → **solutionistische Nutzung**
- Klientel (Lernende) übernehmen dieses Verhalten
- Meta-Prompts werden nicht als "vorbereitetes Material" verstanden
- **Reflexive Aneignung findet nicht statt**

### DevServer-Lösung

**Strukturelle Verhinderung solutionistischer Nutzung**:
1. **Configs als explizite Meta-Prompts** → nicht hidden in JSON-Workflows
2. **Edit-Interface** (geplant) → Pädagog*innen und Lernende schreiben Meta-Prompts
3. **Keine Umgehung** → SD 3.5 ohne Interception nicht mehr möglich
4. **Dialog-Modus** (geplant) → LLM-gestützte Meta-Prompt-Erstellung
5. **Drei Modi** (Play/Dialog/Expert) → zielgruppenspezifische Interfaces

### Technische Vorteile

| Aspekt | Legacy-Server | DevServer |
|--------|---------------|-----------|
| **Architektur** | ComfyUI-JSON-Manipulation | Chunk+Pipeline+Config |
| **Redundanz** | 63 Workflows, massive Duplikation | ~10 Pipelines, ~40 Configs |
| **Änderbarkeit** | JSON-Hacking, fehleranfällig | JSON-Configs, user-editable |
| **Rekursivität** | Pseudo (9x Copy-Paste) | Native (geplant) |
| **Interaktivität** | Stateless, linear | Stateful (geplant) |
| **Meta-Prompts** | Hidden in Workflows | Explizit in Configs |
| **Testbarkeit** | Schwer (Node-IDs, Verschachtelung) | Einfach (Layer-Isolation) |

---

## 2. Von ComfyUI zu Schema-Based: Die Evolution

### 2.1 ComfyUI-Workflows (Legacy System)

**Ursprüngliche Idee** (Juni 2025):
- ComfyUI als Backend für Bildgenerierung
- Workflows als JSON-Files mit Nodes
- Custom Nodes für Prompt Interception

**Erreichte Erfolge**:
- ✅ Funktionierender Pilot in 5 Workshops
- ✅ Prompt Interception als pädagogisches Instrument etabliert
- ✅ Multi-Layer Security funktioniert
- ✅ Eco/Fast Mode (Ollama/OpenRouter) erfolgreich

**Fundamentale Grenzen** (erkannt August-Oktober 2025):

**1. Workflow-Explosion**:
```
Problem: 63 Workflows für ähnliche Funktionen
Beispiel:
- ai4artsed_Dada_2506220140.json (1247 Zeilen)
- ai4artsed_Bauhaus_2509071932.json (1189 Zeilen)
- ai4artsed_Expressionism_2507031856.json (1202 Zeilen)

Duplikation: Nur Node 42 unterschiedlich (style_prompt)!
Wartbarkeit: Änderungen an KSampler = 63 Files editieren
```

**2. Pseudo-Rekursivität** ("Stille Post"):
```json
// 9 Prompt-Interception-Nodes manuell verkettet:
"105": {"inputs": {"input_prompt": ["92", 0]}},   // Step 1
"106": {"inputs": {"input_prompt": ["105", 0]}},  // Step 2
"103": {"inputs": {"input_prompt": ["106", 0]}},  // Step 3
...
```
- Statisch: Anzahl der Schritte hardcoded
- Keine Unterbrechung möglich
- Keine dynamischen Abbruchbedingungen

**3. Hidden Content**:
```json
// Context versteckt in Node 42, nur per JSON-Hacking änderbar:
"42": {
  "inputs": {
    "style_prompt": "You are an artist working in the spirit of Dadaism. Your best friend gave you this input_prompt. Do not interpret this as a direct instruction... [1287 characters]"
  }
}
```
- Nicht editierbar ohne JSON-Kenntnisse
- Nicht sichtbar für Pädagog*innen
- Keine Material-Metapher erkennbar

**4. Empirisches Scheitern**:
- Aus Workshop-Evaluationen: Pädagog*innen wählen "SD 3.5 large ohne Interception"
- **Ursache**: Zu komplex, zu versteckt, zu technisch
- **Konsequenz**: Solutionismus statt Reflexion

### 2.2 Schema-Based Architecture (Oktober 2025)

**Konzeptioneller Durchbruch** (6.-12. Oktober):
- Trennung von Struktur (Pipelines) und Inhalt (Configs)
- Configs als **editierbare Meta-Prompts**
- Instruction Types als wiederverwendbare Bausteine

**Architektur-Paradigma**:
```
Legacy: WORKFLOW (alles in einem) = Node-Graph + Prompts + Settings

DevServer: CHUNK (Primitive) + PIPELINE (Struktur) + CONFIG (Inhalt)
```

**Implementierungsstatus** (aktuell 60%):
- ✅ Backend-Orchestrierung (workflow_routes.py)
- ✅ Pipeline-Executor (schemas/engine/)
- ✅ 34 Configs erstellt (configs_new/)
- ✅ Instruction Types definiert
- ⏳ Frontend-Integration (Expert Mode)
- ⏳ Edit-Interface (geplant)
- ⏳ Dialog/Play Modes (geplant)

---

## 3. Die Drei-Schicht-Architektur im Detail

**Hinweis**: Technische Details siehe `ARCHITECTURE.md`. Hier: Pädagogische und praktische Perspektive.

### 3.1 Layer 1: Chunks (Primitive = Werkzeuge)

**Metapher für Pädagog*innen**: Chunks sind **Werkzeuge** im Werkraum.

Analog zum klassischen Kunstunterricht:
- **Pinsel** = `translate.json` (Sprach-Werkzeug)
- **Schere** = `manipulate.json` (Transformations-Werkzeug)
- **Kleber** = `prompt_interception.json` (Verbindungs-Werkzeug)

**Beispiel - Chunk "prompt_interception"**:
```json
{
  "name": "prompt_interception",
  "template": "Task:\n{{INSTRUCTION}}\n\nContext:\n{{CONTEXT}}\n\nPrompt:\n{{INPUT_TEXT}}",
  "backend_type": "ollama",
  "model": "gemma2:9b"
}
```

**Was macht dieser Chunk?**
- Nimmt drei Inputs: INSTRUCTION (Was tun?), CONTEXT (Wie denken?), INPUT_TEXT (Womit arbeiten?)
- Sendet an LLM (Ollama lokal oder OpenRouter cloud)
- Gibt transformierten Text zurück

**Pädagogische Funktion**:
- Werkzeug ist neutral (kein künstlerischer Inhalt)
- Kann für Dada, Bauhaus, Expressionismus verwendet werden
- Wiederverwendbar = nachhaltig, wartbar

**Aktuelle Chunks** (schemas/chunks/):
- `translate.json` - Sprachübersetzung
- `manipulate.json` - Textmanipulation
- `prompt_interception.json` - Universal-Transformation
- `comfyui_image_generation.json` - Bildgenerierung

### 3.2 Layer 2: Pipelines (Struktur = Arbeitsablauf)

**Metapher für Pädagog*innen**: Pipelines sind **Arbeitsabläufe** ("erst skizzieren, dann malen").

Analog zum Kunstunterricht:
- **Skizze → Farbe → Feinschliff** = `simple_interception.json`
- **Foto → Collage → Übermalen** = `image_manipulation.json` (geplant)

**Beispiel - Pipeline "simple_interception"**:
```json
{
  "name": "simple_interception",
  "chunks": ["prompt_interception"],
  "required_fields": ["context", "instruction_type"],
  "defaults": {
    "instruction_type": "manipulation.standard"
  },
  "meta": {
    "pre_processing": ["translation", "safety_check"]
  }
}
```

**Was macht diese Pipeline?**
1. **Vor Ausführung** (Server): Übersetzung + Sicherheitscheck
2. **Ausführung**: Ein Chunk (prompt_interception)
3. **Nach Ausführung**: Optional Bildgenerierung

**Pädagogische Funktion**:
- Struktur ist generisch (kein spezifischer Inhalt)
- Kann für viele Zwecke verwendet werden
- Definiert nur: "Was kommt wann?"

**Wichtig - Pipelines enthalten NIEMALS**:
- ❌ Konkrete Künstler-Namen
- ❌ Spezifische Haltungen (Dada, Bauhaus, etc.)
- ❌ Kulturelle Kontexte
- ✅ Nur: Struktur, Defaults, Pre-Processing-Rules

**Aktuelle Pipelines** (schemas/pipelines/ bzw. workflow_types/):
- `simple_interception.json` - Ein-Schritt-Transformation
- `simple_manipulation.json` - Basis-Manipulation
- `image_generation.json` - Mit Bildgenerierung
- `translation_only.json` - Nur Übersetzung

### 3.3 Layer 3: Configs (Inhalt = Das "Material")

**Metapher für Pädagog*innen**: Configs sind das **vorbereitete Material** für den Kunstkurs.

Analog zum Kunstunterricht:
- **Rotes Papier + Schere** = Config "Expressionism" (Material + Werkzeug-Auswahl)
- **Zeitungspapier + Kleber** = Config "Dadaism" (anderes Material)
- **Bauhaus-Farben + geometrische Schablonen** = Config "Bauhaus"

**Beispiel - Config "dada.json"**:
```json
{
  "pipeline": "simple_interception",
  "name": {
    "en": "Dadaism",
    "de": "Dadaismus"
  },
  "description": {
    "en": "Transform text into Dadaist artwork concepts",
    "de": "Verwandle Text in dadaistische Kunstkonzepte"
  },
  "instruction_type": "manipulation.creative",
  "context": "You are an artist working in the spirit of Dadaism. Your best friend gave you this 'input_prompt'. Do not interpret this as a direct instruction of what to paint, but rather as a spark, a provocation... [Vollständiger Kontext mit Künstlernamen]",
  "parameters": {
    "temperature": 0.8
  },
  "meta": {
    "art_movement": "dadaism",
    "legacy_source": "workflows/arts_and_heritage/ai4artsed_Dada_2506220140.json"
  }
}
```

**Was macht diese Config?**
- Definiert **WAS** transformiert werden soll (Dadaistische Haltung)
- Wählt **WIE** transformiert wird (instruction_type: creative)
- Gibt **Kontext** für die Transformation
- Setzt **Parameter** (temperature = Kreativität)

**Pädagogische Funktion**:
- **Explizit sichtbar**: Pädagog*innen sehen den Kontext in der JSON-Datei
- **Editierbar**: Kann angepasst werden (Künstlernamen, Zeitperiode, Haltung)
- **Material-Metapher**: "Welches Material gebe ich den Lernenden?"

**Zentrale Innovation gegenüber Legacy**:
```
Legacy: Context hidden in Node 42, Zeile 247 von 1247
        → Nicht sichtbar, nicht editierbar ohne JSON-Hacking

DevServer: Context in dada.json, Zeile 8
          → Sichtbar, editierbar, verständlich
```

**Aktuelle Configs** (34 erstellt in schemas/configs_new/):

**Künstlerische Haltungen**:
- `dada.json` - Dadaismus (Spott, Ironie, Nonsens)
- `bauhaus.json` - Bauhaus (Funktionalität, Geometrie)
- `expressionism.json` - Expressionismus (Emotion, Verzerrung)

**Textmanipulationen**:
- `overdrive.json` - Übertreibung
- `jugendsprache.json` - UK Youth Slang
- `piglatin.json` - Pig Latin (Sprachspiel)

**System-Pipelines**:
- `translation_en.json` - Englisch-Übersetzung
- `ethicaladvisor.json` - Ethische Reflexion
- `stillepost.json` - Stille Post (mehrfache Übersetzung)

**Audio/Musik** (experimentell):
- `acestep_simple.json`, `acestep_tellastory.json` - AceStep Musik
- `stableaudio.json`, `stableaudio_tellastory.json` - StableAudio

### 3.4 Instruction Types (Wiederverwendbare Anweisungen)

**Metapher**: Instruction Types sind **Kochrezepte** ("Anbraten", "Dünsten", "Frittieren").

**Problem gelöst**:
- Viele Configs brauchen ähnliche Anweisungen
- Ohne Instruction Types: Copy-Paste in jeder Config → Wartungshölle
- Mit Instruction Types: Einmal definieren, überall nutzen

**Beispiel - manipulation.creative**:
```json
// instruction_types.json
{
  "manipulation": {
    "creative": {
      "instruction": "Creatively interpret and transform the text. Take artistic liberties while honoring the spirit of the context.",
      "parameters": {
        "temperature": 0.8
      }
    }
  }
}
```

**Verwendung in Config**:
```json
// dada.json
{
  "instruction_type": "manipulation.creative"  // Referenz statt Duplikation
}
```

**Aktuelle Instruction Types** (schemas/instruction_types.json):

**Translation**:
- `translation.standard` - Standard-Übersetzung (Struktur erhalten)
- `translation.culture_sensitive` - Kulturell sensibel
- `translation.rigid` - Wort-für-Wort

**Manipulation**:
- `manipulation.standard` - Standard-Transformation
- `manipulation.creative` - Kreative Interpretation
- `manipulation.amplify` - Übertreibung
- `manipulation.analytical` - Analytische Umstrukturierung

**Security**:
- `security.standard` - Standard-Sicherheitscheck
- `security.strict` - Strikt (DS-GVO)

**Image Analysis**:
- `image_analysis.formal` - Kunsthistorische Analyse (Panofsky)
- `image_analysis.descriptive` - Beschreibende Analyse
- `image_analysis.iconographic` - Symbolische Interpretation

---

## 4. Pädagogischer Paradigmenwechsel

### 4.1 Problem: Solutionismus im Legacy-System

**Definition Solutionismus** (nach Evgeny Morozov):
> Technologiezentrierte Problemlösung ohne Reflexion über Prozesse, Machtstrukturen und gesellschaftliche Auswirkungen.

**Wie manifestiert sich Solutionismus in generativer AI?**
- "Prompt rein, Bild raus" - Black Box
- Keine Auseinandersetzung mit künstlerischen Haltungen
- Kein Verständnis für AI-Prozesse
- Nutzer*innen als Konsument*innen, nicht als Gestalter*innen

**Legacy-Server förderte unbeabsichtigt Solutionismus**:
1. **Option "SD 3.5 ohne Interception"** existierte
2. Pädagog*innen wählten diese (Weg des geringsten Widerstands)
3. Lernende übernahmen dieses Verhalten
4. Meta-Prompts waren hidden → nicht als "Material" erkennbar

**Empirische Validierung** (5 Workshops, Juli-Oktober 2025):
- 80% der Pädagog*innen nutzten SD 3.5 direkt (ohne Interception)
- Begründung: "Zu kompliziert", "Zeitdruck", "Ergebnis ist ähnlich"
- Lernende: Keine Reflexion über künstlerische Haltungen erkennbar
- **Erkenntnis**: Gute Pädagogik kann nicht optional sein - sie muss strukturell verankert werden

### 4.2 DevServer-Lösung: Strukturelle Verhinderung

**Prinzip**: **Prozessorientiertes Lernen als Default, nicht als Option**

**Konkrete Maßnahmen**:

**1. Keine Umgehung mehr möglich**:
```
Legacy: Dropdown mit "SD 3.5 large (No Interception)" ❌
DevServer: Nur Configs wählbar, alle enthalten Meta-Prompts ✅
```

**2. Configs = Explizite Meta-Prompts**:
```
Legacy: Meta-Prompt hidden in Node 42, Zeile 247
        → Nicht sichtbar für Pädagog*innen

DevServer: Meta-Prompt in dada.json, Zeile 8-15
          → Explizit sichtbar, editierbar
```

**3. Material-Metapher im UI** (geplant):
```
Frontend zeigt:
┌────────────────────────────────────────────┐
│ CONFIG: Dadaism                            │
│                                            │
│ Material (Meta-Prompt):                   │
│ "You are an artist working in the          │
│  spirit of Dadaism..."                     │
│                                            │
│ [Edit] [Use as template] [Save custom]    │
└────────────────────────────────────────────┘
```

**4. Dialog-Modus** (geplant Phase 2):
```
LLM-gestützte Meta-Prompt-Erstellung:

System: "Welche künstlerische Haltung möchtest du fördern?"
User: "Kritisch, subversiv, absurd"
System: "Das klingt nach Dadaismus. Soll ich einen Meta-Prompt vorschlagen?"
User: "Ja"
System: [Generiert Meta-Prompt] "Magst du das anpassen?"
```

**5. Play-Modus für Kinder** (geplant Phase 3):
```
Visuelles Interface:
- Karten mit Kunstbewegungen (Bilder statt Text)
- Drag & Drop von "Haltungen" auf "Material"
- Spielerische Erkundung ohne Textlast
```

### 4.3 Empowerment statt Consumption

**Ziel**: Lernende als **aktive Gestalter*innen**, nicht passive Nutzer*innen

**DevServer-Features für Empowerment**:

**1. Editierbarkeit** (Phase 2):
- Configs sind JSON → lesbar, editierbar
- Visual Editor geplant (GUI statt JSON)
- Eigene Configs speichern und teilen

**2. Transparenz**:
```
Frontend zeigt:
┌────────────────────────────────────────────┐
│ PIPELINE STEPS:                            │
│ 1. [Translation] German → English          │
│ 2. [Safety Check] Keine Verstöße           │
│ 3. [Interception] Dadaistische Haltung     │
│ 4. [Image Gen] Stable Diffusion 3.5        │
│                                            │
│ [Show details for each step]              │
└────────────────────────────────────────────┘
```

**3. Reflexionsanlässe**:
- Zwischenergebnisse sichtbar machen (geplant)
- "Warum wurde mein Prompt so transformiert?"
- Vergleich: Mit vs. ohne Meta-Prompt

**4. Kursleiter*innen-Werkzeuge** (Phase 2):
- Template-Bibliothek mit pädagogischer Dokumentation
- "Warum ist dieser Meta-Prompt pädagogisch sinnvoll?"
- Kurs-Sets vorbereiten und teilen

---

## 5. Technische Überlegenheit

### 5.1 Wartbarkeit

**Problem Legacy**:
```
Änderung: KSampler-Steps von 25 auf 30
Aufwand: 63 JSON-Files editieren (manuelle Suche nach allen KSampler-Nodes)
Fehlerrisiko: Hoch (Node-IDs, Verschachtelung)
```

**Lösung DevServer**:
```
Änderung: Default-Steps ändern
Aufwand: 1 Zeile in pipelines/image_generation.json
Code:
{
  "defaults": {
    "parameters": {
      "steps": 30  // War: 25
    }
  }
}
Alle Configs erben automatisch!
```

### 5.2 Testbarkeit

**Problem Legacy**:
```python
def test_dada_workflow():
    workflow = load_workflow("ai4artsed_Dada_2506220140.json")
    # Wie teste ich nur die Prompt-Interception?
    # Node 42 ist verschachtelt in 1247 Zeilen...
    # Integration-Test notwendig (langsam, fragil)
```

**Lösung DevServer**:
```python
def test_prompt_interception_chunk():
    chunk = load_chunk("prompt_interception")
    result = chunk.execute(
        instruction="Transform creatively",
        context="Dadaism",
        input_text="A cat"
    )
    assert "absurd" in result or "subversive" in result

# Unit-Test: Schnell, isoliert, robust
```

### 5.3 Rekursivität (geplant)

**Problem Legacy** (Stille Post):
```json
// 9 Nodes manuell verketten = Pseudo-Rekursivität
"105": {"inputs": {"input_prompt": ["92", 0]}},
"106": {"inputs": {"input_prompt": ["105", 0]}},
"103": {"inputs": {"input_prompt": ["106", 0]}},
...
// Statisch, nicht unterbrechbar, nicht dynamisch
```

**Lösung DevServer** (geplant Phase 2):
```json
// Pipeline mit Loop:
{
  "name": "stille_post_recursive",
  "chunks": [
    {
      "chunk": "translate",
      "loop": {
        "max_iterations": 5,
        "condition": "language_changed",
        "languages": ["French", "Japanese", "Spanish", "Russian", "English"]
      }
    }
  ]
}

// Features:
// - Dynamische Iterationsanzahl
// - Abbruchbedingungen
// - Zwischenergebnisse abrufbar
// - User kann unterbrechen
```

### 5.4 Parallelisierung (geplant)

**Problem Legacy**:
```
Sequentiell:
1. Translation (2s)
2. Safety Check (3s)
3. Prompt Interception (5s)
4. Image Generation (30s)
Gesamt: 40s
```

**Lösung DevServer** (Phase 2):
```
Parallel:
1a. Translation (2s) ┐
1b. Safety Check (3s) ├→ Merge (3s) → 2. Prompt Interception (5s) → 3. Image (30s)
Gesamt: 38s (kleiner Gewinn)

Oder bei komplexeren Pipelines:
1a. Text-Branch (5s) ┐
1b. Audio-Branch (4s) ├→ Merge → Multimodal Output
1c. Image-Branch (6s) ┘
Gesamt: 6s statt 15s
```

---

## 6. Aktuelle Implementierung (Phase 4)

### 6.1 Was funktioniert bereits (60% Backend)

**✅ Implementiert**:

**1. Backend-Orchestrierung** (`workflow_routes.py`):
- Config-Loading aus `configs_new/`
- Pipeline-Resolution
- Instruction Type Resolution
- Hidden Commands (`#notranslate#`, `#image#`, etc.)
- Pre-Processing (Translation, Safety)
- Post-Processing (AUTO-MEDIA Generation)

**2. Pipeline-Executor** (`schemas/engine/`):
- `pipeline_executor.py` - Führt Pipelines aus
- `config_loader.py` - Lädt Configs + Pipelines
- `chunk_builder.py` - Baut Chunks zur Laufzeit
- `instruction_resolver.py` - Löst Instruction Types auf

**3. 34 Configs erstellt** (`schemas/configs_new/`):
- Alle Legacy-Workflows mit Prompt Interception konvertiert
- Metadata ergänzt (display, tags, audience)
- Instruction Types zugewiesen

**4. API-Endpoints**:
- `/pipeline_configs_metadata` - Alle Configs mit Metadata
- `/pipeline_config/<name>` - Einzelne Config
- `/run_workflow` - Pipeline-Ausführung

**5. Expert Mode Frontend** (Phase 4):
- Visual Workflow Browser (workflow-browser.js)
- Karten-basierte Auswahl
- Filterung (Difficulty, Workshop, Search)
- Kategorie-Gruppierung

### 6.2 Was fehlt noch (40%)

**⏳ In Arbeit**:

**1. Edit-Interface** (Kritisch für Pädagogik!):
- Configs im Frontend editieren
- Visual Meta-Prompt-Editor
- Eigene Configs speichern

**2. Dialog-Modus**:
- LLM-gestützte Meta-Prompt-Erstellung
- Guided Workflow

**3. Play-Modus**:
- Karten-basiert für Kinder
- Weniger Text, mehr Visualisierung

**4. Stateful Server**:
- Session-Management
- Pipeline-Pause und -Fortsetzung
- Zwischenergebnisse speichern

**5. Rekursive Pipelines**:
- Loop-Support in Pipelines
- Abbruchbedingungen
- Dynamische Iteration

**6. Parallelisierung**:
- Dependency-Graph-Analyse
- Parallele Chunk-Ausführung

### 6.3 Aktueller Test-Status

**Problem**: translation_en config funktioniert nicht korrekt

**Symptom**:
```
Input (Deutsch): "Hallo Welt"
Expected Output (Englisch): "Hello World"
Actual Output (Deutsch): "Hallo Welt"
```

**Ursache vermutet** (Stand 26. Oktober):
- PRE-PIPELINE Translation übersetzt bereits zu Englisch
- translation_en Pipeline erhält englischen Text
- Pipeline erkennt "already English" → gibt unverändert zurück
- **Fix geplant**: `skip_pre_translation: true` in Config-Meta

**Status**: Flag in Config vorhanden, Backend-Implementierung steht noch aus

---

## 7. Use Cases und Szenarien

### 7.1 Szenario 1: Workshop "Dadaistische Haltung"

**Zielgruppe**: Jugendliche (14-16 Jahre), 90 Minuten

**Legacy-Server (bisherig)**:
1. Pädagog*in wählt "ai4artsed_Dada_2506220140.json"
2. Lernende geben Prompts ein: "Eine Katze auf einem Stuhl"
3. Bild entsteht - aber: Keine Reflexion über **warum** es dadaistisch ist
4. Problem: Meta-Prompt hidden, nicht diskutierbar

**DevServer (zukünftig)**:

**Phase 1 - Exploration** (20 Min):
```
1. Expert Mode: Config "dada.json" auswählen
2. System zeigt Meta-Prompt:
   "You are an artist working in the spirit of Dadaism..."
3. Pädagog*in liest laut vor, Diskussion:
   - "Was bedeutet Dadaismus?"
   - "Warum Spott und Ironie?"
   - "Welche Künstler*innen werden genannt?"
4. Lernende geben Prompt ein: "Eine Katze auf einem Stuhl"
5. System zeigt Zwischenergebnis:
   "Transformierter Prompt: Der Stuhl sitzt auf der Katze und beide trinken Zahlen"
6. Diskussion: "Wie hat die KI das transformiert?"
```

**Phase 2 - Aneignung** (30 Min):
```
1. Dialog Mode: "Erstelle deinen eigenen Meta-Prompt"
2. LLM fragt: "Welche Kunstbewegung interessiert dich?"
3. User: "Punk, rebellisch, DIY"
4. LLM: "Das klingt nach Punk-Ästhetik. Soll ich einen Meta-Prompt vorschlagen?"
5. System generiert:
   "You are a punk artist. Your friend gave you this input. Reject polish and perfection. Embrace raw energy, DIY ethics, and anti-establishment attitude..."
6. User bearbeitet, speichert als "punk_aesthetics.json"
```

**Phase 3 - Reflexion** (40 Min):
```
1. Vergleich: Selber Prompt mit verschiedenen Meta-Prompts
   - Dada: "Der Stuhl sitzt auf der Katze..."
   - Punk: "Zerfetzte Katze auf kaputtem Stuhl, Sicherheitsnadeln..."
   - Bauhaus: "Geometric cat on functional chair, primary colors..."
2. Diskussion:
   - "Was macht Haltungen unterschiedlich?"
   - "Ist KI neutral?" (Nein - programmiert mit Haltungen)
   - "Wer entscheidet über Haltungen?" (Wir, die Gestalter*innen)
```

### 7.2 Szenario 2: Forschungsprojekt "AI & Bias"

**Zielgruppe**: Student*innen Medienwissenschaft, Semesterbegleitung

**Forschungsfrage**: "Wie manifestiert sich kultureller Bias in Bildgenerierungs-AI?"

**DevServer-Vorteile**:

**1. Systematische Variation**:
```json
// Configs für verschiedene Kulturen:
configs/
  western_canon.json       // "Renaissance masters"
  african_aesthetics.json  // "Traditional African art"
  asian_calligraphy.json   // "East Asian brush techniques"
  indigenous_art.json      // "Indigenous storytelling"

// Gleicher Input-Prompt: "A person in traditional clothing"
// Vergleich der Outputs → Bias-Analyse
```

**2. Reproduzierbarkeit**:
```
Alle Configs + Prompts + Seeds gespeichert
→ Andere Forschende können replizieren
→ Wissenschaftliche Standards erfüllt
```

**3. Export-Daten**:
```
Export-Manager sammelt:
- Original Prompt
- Config verwendet
- Meta-Prompt (Context)
- Instruction Type
- Model (Ollama/OpenRouter)
- Generated Image
- Timestamp, Settings

→ Datensatz für qualitative Analyse
```

### 7.3 Szenario 3: "Stille Post" neu gedacht

**Pädagogisches Ziel**: Sprachlicher Drift + kulturelle Hegemonien sichtbar machen

**Legacy-Limitation**:
```json
// 9 Nodes, statisch, nicht unterbrechbar
"105" → "106" → "103" → ... → "98"
```

**DevServer-Vision** (Phase 2):
```json
// Rekursive Pipeline mit Zwischenstopps:
{
  "pipeline": "stille_post_interactive",
  "chunks": [
    {
      "chunk": "translate",
      "loop": {
        "pause_after_each": true,  // ← Unterbrechung!
        "show_intermediate": true,
        "languages": ["French", "Japanese", "Swahili", "Russian", "English"]
      }
    }
  ]
}
```

**Ablauf**:
```
Input: "Die Katze jagt die Maus"
  ↓
[Step 1: Französisch]
Output: "Le chat chasse la souris"
[PAUSE] System: "Vergleiche Original mit Übersetzung. Weiter?" [Ja/Nein]
  ↓
[Step 2: Japanisch]
Output: "猫がネズミを追いかける"
[PAUSE] System: "Was fällt auf? Grammatik anders? Kulturelle Unterschiede?" [Diskussion]
  ↓
[Step 3: Swahili]
Output: "Paka anafukuza panya"
[PAUSE] System: "Swahili ist unterrepräsentiert in AI-Training. Beobachtet ihr Qualitätsverlust?" [Analyse]
  ↓
[Step 4: Russisch]
Output: "Кошка гонится за мышью"
  ↓
[Step 5: Zurück zu Englisch]
Output: "The cat is chasing the mouse" (nicht identisch mit Schritt 1!)

[Reflexion]
- Semantischer Drift: "jagt" → "chasing" (continuous)
- Kulturelle Hegemonien: Swahili schlechtere Qualität
- Spielerischer Lerneffekt: Spaß am Misslingen
```

---

## 8. Offene Herausforderungen

### 8.1 Translation-Paradox

**Problem**: `translation_en.json` übersetzt nicht, weil PRE-PIPELINE bereits übersetzt hat.

**Diskussion**:
- Option A: `skip_pre_translation: true` → Config entscheidet
- Option B: PRE-PIPELINE nutzt selbst `translation_en` → Selbstreferenz
- Option C: PRE-PIPELINE abschaffen, alle Translation in Pipelines

**Entscheidung steht aus**: User-Input erforderlich

### 8.2 Audio/Video Pipelines

**Status**: Experimentell (acestep, stableaudio configs existieren)

**Herausforderung**:
- ComfyUI primär für Bilder designed
- Audio-Nodes weniger ausgereift
- Video praktisch nicht vorhanden

**Lösung**: Alternative Backends (StableAudio API, MusicGen)

**Frage**: Wie integrieren in DevServer-Architektur?
- Neue Chunks: `audio_generation.json`, `video_generation.json`?
- Neue Backend-Types: `"stableaudio"`, `"musicgen"`?

### 8.3 Safety bei flexiblen Backends

**Problem** (aus DEVSERVER_TODOS.md):
- Bild-Upload + flexible Backends = Risiko
- Selbstportraits von Kindern an externe APIs?

**Lösung in Diskussion**:
- **Option A**: Backend-Metadata `gdpr_compliant: true/false`
  - System erlaubt Bild-Upload nur bei `true` oder lokal
- **Option B**: Bild-Verarbeitung immer lokal (Ollama Vision)
  - Einschränkung: Geringere Qualität

**DevServer muss implementieren**: Backend-Policy-System

### 8.4 Edit-Interface Design

**Herausforderung**: Balance zwischen Einfachheit und Mächtigkeit

**Zielgruppen**:
1. **Kinder** (10-12): Zu viel Text = Überforderung
2. **Jugendliche** (13-16): Interesse an Technik, aber keine JSON-Kenntnisse
3. **Pädagog*innen**: Wenig Zeit, pragmatisch
4. **Expert*innen**: Volle Kontrolle gewünscht

**Lösungsansatz**: Drei Modi (Play/Dialog/Expert)

**Konkrete Frage**: Wie sieht das Edit-Interface aus?
```
Variante A: Visual Editor mit Bausteinen (à la Scratch)
Variante B: Guided Wizard mit LLM-Dialog
Variante C: JSON-Editor mit Syntax-Highlighting + Vorschau
Variante D: Hybrid (Modi umschaltbar)
```

**Entscheidung**: User-Testing erforderlich

### 8.5 Performance-Optimierung

**Kernproblem** (aus Workshops):
- Timeouts durch zu langsame DSL-Anbindung
- Zu lange Workflow-Zeiten (Sicherheitschecks sequentiell)

**DevServer-Maßnahmen geplant**:
1. **Parallelisierung**: Safety + Translation gleichzeitig
2. **Caching**: Häufige Übersetzungen cachen (PROMPT_CACHE)
3. **Progressive Loading**: Zwischenstände anzeigen
4. **Model-Preloading**: Ollama Models im VRAM halten

**Offene Frage**: Reicht das? Oder brauchen wir CDN/Edge-Computing?

---

## 9. Roadmap

### Phase 1: MVP für Workshops ✅ (80% fertig)

**Deadline**: Ende November 2025

**Must-Have**:
- [x] Backend-Orchestrierung funktioniert
- [x] 34 Configs migriert
- [x] Expert Mode Frontend (basic)
- [ ] translation_en Fix
- [ ] Performance-Tests (Timeout-Probleme lösen)

**Ziel**: Einsatzfähig für nächste Workshop-Runde

### Phase 2: Pädagogisches Kern-Feature (Q1 2026)

**Edit-Interface für Meta-Prompts**:
- [ ] Visual Config-Editor (GUI)
- [ ] Template-Bibliothek mit pädagogischer Doku
- [ ] Eigene Configs speichern/teilen
- [ ] Dialog-Modus (LLM-gestützte Erstellung)

**Stateful Server**:
- [ ] Session-Management (Redis/Memcached)
- [ ] Pipeline-Pause und -Fortsetzung
- [ ] Zwischenergebnisse sichtbar

**Ziel**: Strukturelle Verhinderung von Solutionismus

### Phase 3: Erweiterte Features (Q2 2026)

**Play-Modus**:
- [ ] Karten-basiertes UI für Kinder
- [ ] Drag & Drop von Haltungen
- [ ] Weniger Text, mehr Bilder

**Rekursive Pipelines**:
- [ ] Loop-Support
- [ ] Abbruchbedingungen
- [ ] Dynamische Iteration

**Parallelisierung**:
- [ ] Dependency-Graph-Analyse
- [ ] Parallele Chunk-Ausführung

**Ziel**: Vollständige pädagogische Vision umgesetzt

### Phase 4: Skalierung (Q3-Q4 2026)

**Multi-Backend-Support**:
- [ ] LMStudio Integration
- [ ] Deutsche DS-GVO-Anbieter (Aleph Alpha)
- [ ] Backend-Policy-System

**Audio/Video**:
- [ ] Stabile Audio-Pipelines
- [ ] Video-Support (experimentell)

**Community-Features**:
- [ ] Config-Sharing-Plattform
- [ ] Best-Practice-Guides für Pädagog*innen
- [ ] Forschungsdaten-Repository

**Ziel**: Reif für breiten Einsatz in Schulen

---

## Fazit

Der **DevServer** ist mehr als ein technisches Upgrade - er ist ein **pädagogischer Paradigmenwechsel**.

**Kernbotschaft**:
- Technologie allein löst keine pädagogischen Probleme
- Gute Pädagogik muss **strukturell verankert** werden, nicht optional
- Meta-Prompts sind **Material** im Sinne der Kunstpädagogik
- Reflexive Aneignung statt solutionistische Nutzung

**DevServer macht möglich**:
- ✅ Explizite, editierbare Meta-Prompts
- ✅ Keine Umgehung der reflexiven Ebene
- ⏳ Dialog-Modus für Anfänger*innen (geplant)
- ⏳ Edit-Interface für Pädagog*innen (geplant)
- ⏳ Play-Modus für Kinder (geplant)

**Status**: 60% Backend, Frontend folgt. Einsatz in Workshops ab Ende 2025.

---

**Letztes Update**: 26. Oktober 2025
**Autor**: Dokumentiert nach Legacy-Server-Analyse und Architektur-Review
**Für**: Zukünftige LLM-Tasks, Entwickler*innen, Pädagog*innen
