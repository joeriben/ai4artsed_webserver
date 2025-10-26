# DevServer TODO-Liste

Extrahiert aus der Legacy-Server-Architektur-Dokumentation - Anforderungen basierend auf empirischen Befunden und erkannten Limitationen.

---

## 1. Backend-Erweiterungen

### 1.1 Multi-Backend-Support erweitern
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 105

**Anforderung**: Über Ollama und OpenRouter hinaus weitere API-fähige Backends unterstützen

**Spezifikationen**:
- **LMStudio**: Lokale Inference mit GUI
- **Deutsche DS-GVO-konforme Anbieter**: z.B. Aleph Alpha, HuggingFace Inference (EU-hosted)
- **Backend-Kennzeichnung**: Metadaten ob DS-GVO-konform (wichtig für Bild-Upload-Policy)

**Priorität**: Mittel
**Begründung**: Bildungsgerechtigkeit + Datenschutz

---

## 2. Safety-System Optimierungen

### 2.1 Effizienzsteigerung Safety-Checks
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 136

**Problem Legacy**:
- Drei separate LLM-Calls (Translation, Guard Model, Safety Node)
- Sequentielle Ausführung → lange Wartezeiten
- Negative-Prompt-Injection reduziert Bildqualität

**DevServer-Lösung**:
- **Konsolidierung**: Weniger LLM-Calls durch intelligentere Orchestrierung
- **Parallelisierung**: Safety-Checks parallel zu anderen Vorbereitungen
- **Image-Analyse am Ende**: Post-Generation-Check statt nur Pre-Prompt-Check
  - Kombinierter Text+Bild-Safety-Check
  - Falls Bild problematisch: Regenerierung mit angepasstem Prompt

**Priorität**: Hoch
**Begründung**: Kernproblem aus Workshops - zu lange Wartezeiten

### 2.2 Verbesserte False-Positive-Behandlung
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 507

**Problem Legacy**:
- Wort "player" löst Kids-Filter aus (False Positive)
- Filter reagiert teilweise unverständlich

**DevServer-Lösung**:
- Fine-Tuning auf deutschsprachige Prompts
- Whitelisting harmloser Begriffe
- Erklär-Funktion: "Dieses Wort wurde gefiltert weil..."

**Priorität**: Mittel
**Begründung**: Frustration bei Lernenden minimieren

### 2.3 Ausführliche Begründungen
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 551

**Anforderung**: LLM artikuliert **warum** ein Prompt problematisch ist

**Spezifikationen**:
- **Ebenen**: Rechtlich, ethisch, ästhetisch, entwicklungspsychologisch
- **Formulierung**: Altersgerecht (Kids vs. Youth vs. Expert Mode)
- **Lerneffekt**: Reflexion über AI-Safety als Lerngegenstand

**Priorität**: Mittel-Hoch
**Begründung**: Pädagogischer Kern - Transparenz statt Black Box

---

## 3. Datenschutz (DS-GVO)

### 3.1 Bild-Upload-Policy bei externen Backends
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 626-628

**Problem**: Flexible Backends + Input-Bild-Verarbeitung → Risiko, Selbstportraits von Kindern an externe APIs zu senden

**Lösungsoptionen**:
- **Option A (empfohlen)**: DS-GVO-kompatible Backends hartcodiert kennzeichnen
  - Metadaten-Feld: `gdpr_compliant: true/false`
  - System erlaubt Bild-Upload nur bei `true` oder lokalem Backend
  - Bei `false`: Fehlermeldung + Hinweis auf Datenschutz

- **Option B**: Bild-Verarbeitung nur lokal
  - Ollama Vision Models (llava, bakllava, etc.)
  - Keine Bild-Daten an externe APIs
  - Einschränkung: Geringere Qualität als Cloud-Vision-Models

**Priorität**: **Kritisch**
**Begründung**: Rechtliche Compliance (DS-GVO), Schutz von Kindern

---

## 4. Hauptmotivation: Edit-Interface für Meta-Prompts

### 4.1 Problem aus empirischen Befunden
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 357-379

**Kritischer Befund aus Workshops**:
- Kunstpädagog*innen nutzen **Weg des geringsten Widerstands**
- SD 3.5 large ohne Prompt Interception → **solutionistische Nutzung**
- Keine Meta-Prompt-Gestaltung → Material-Metapher nicht verstanden

**DevServer-Ziel**: Aktive Aneignung als Standard, solutionistische Nutzung strukturell verhindern

### 4.2 Für Klientel (Lernende)

**Anforderungen**:
1. **Meta-Prompt-Editor**: Visuelles Interface zum Schreiben eigener Meta-Prompts
   - Template-Vorschläge (z.B. "Du bist ein Künstler der...")
   - Live-Preview: Wie wird mein Prompt transformiert?

2. **Urteilsformulierung**: Explizite Aufforderung
   - "Was möchtest du erreichen?"
   - "Welche Haltung soll die KI einnehmen?"
   - Nicht technisch, sondern konzeptuell

3. **LLM-Dialog-Unterstützung**: Geführte Meta-Prompt-Erstellung
   - Dialog-Modus: "Ich helfe dir, deinen Meta-Prompt zu formulieren"
   - Fragen: "Soll das Ergebnis realistisch oder abstrakt sein?"
   - Schrittweise Verfeinerung

4. **Keine Umgehung**: SD 3.5 ohne Interception nicht mehr möglich
   - Minimaler Default-Meta-Prompt wenn User nichts eingibt
   - Aber: Bewusste Entscheidung erforderlich (Button "Mit Standard fortfahren")

**Priorität**: **Kritisch** (Hauptgrund für DevServer)

### 4.3 Für Kunstpädagog*innen

**Anforderungen**:
1. **Material-Metapher**: UI macht explizit, dass Meta-Prompts das "vorbereitete Material" sind
   - Analog zu Papier/Farben im klassischen Kunstunterricht
   - "Was ist das Material, mit dem die Lernenden arbeiten?"

2. **Pädagogische Intentionen formulieren**:
   - "Welche künstlerische/kritische Haltung soll gefördert werden?"
   - "Welche Reflexion soll angeregt werden?"

3. **Template-Bibliothek**: Vorgefertigte Meta-Prompts mit pädagogischer Dokumentation
   - Dada-Haltung, Surrealismus, kritische Medienreflexion, etc.
   - Jedes Template mit Erklärung: "Warum ist das pädagogisch sinnvoll?"

4. **Kursmanagement**: Pädagog*innen können Sets von Meta-Prompts für Workshops vorbereiten

**Priorität**: **Kritisch**

---

## 5. Workflow-Generierung vereinfachen

### 5.1 Orchestrierung statt JSON-Generierung
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 890

**Problem Legacy**: LLMs scheitern an ComfyUI-JSON-Generierung (invalide Syntax, falsche Node-IDs)

**DevServer-Vorteil**: Keine ComfyUI-JSONs mehr nötig!

**Neue Aufgabe**: Orchestrierung vordefinierter Pipelines
- Pipelines = atomare Bausteine (Chunks)
- LLM wählt aus: "Welche Chunks in welcher Reihenfolge?"
- Configs definieren Parameter, nicht Struktur

**Machbarkeit**: Deutlich einfacher als JSON-Generierung → LLMs können das

**Priorität**: Mittel (nice-to-have, nicht kritisch)

---

## 6. Stateful Server implementieren

### 6.1 Session-Management
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 878-883

**Legacy-Status**: Versuch gescheitert (Gemini 2.5 Pro, Kosten 30-40$)

**DevServer-Entscheidung**: **Wird implementiert**
- Mit besseren LLMs (Claude Sonnet 4.5, GPT-4.5) machbar
- Mehr Zeit/Budget eingeplant

**Anforderungen**:
- User-Sessions persistieren (Redis/Memcached)
- Pipeline-Zwischenstände speichern
- Unterbrechung und Fortsetzung ermöglichen
- Mehrere parallele Sessions pro User

**Use Case**:
- "Stille Post" unterbrechen nach Schritt 3, Zwischenstand ansehen, fortfahren
- Iterative Bildbearbeitung (OmniGen2-Style)

**Priorität**: Hoch
**Begründung**: Ermöglicht echte Interaktivität

---

## 7. Timeout-Problem lösen

### 7.1 Netzwerk-Optimierung
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 978-981

**Problem Legacy**:
- Timeouts in Workshops (vermutlich DSL-Anbindung zu langsam)
- Lokal praktisch nie Timeouts

**DevServer-Maßnahmen**:
1. **Parallelisierung**: Safety-Checks + Model-Loading + Preprocessing parallel
2. **Caching**:
   - Häufig genutzte Models im VRAM halten
   - Prompt-Translation cachen (PROMPT_CACHE nutzen)
3. **Progressive Loading**:
   - Zwischenstände anzeigen ("Translation läuft...", "Sicherheitscheck...")
   - User-Erwartung managen
4. **Timeout-Konfiguration**:
   - Längere Timeouts für komplexe Workflows
   - Automatische Retry-Logik

**Priorität**: **Kritisch**
**Begründung**: Hauptproblem in realen Workshop-Einsätzen

---

## 8. Sonstige Verbesserungen

### 8.1 Vollständige Mehrsprachigkeit
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 159-161

**Problem Legacy**: DE/EN nur partiell, nicht alle UI-Elemente + Meldungen übersetzt

**DevServer-Ziel**: Vollständige i18n-Unterstützung
- Alle UI-Elemente
- Alle Fehlermeldungen
- Dynamische Sprachwahl (nicht nur beim Start)

**Priorität**: Niedrig (funktioniert ausreichend)

### 8.2 Performance-Optimierung Workflow-Zeiten
**Quelle**: LEGACY_SERVER_ARCHITECTURE.md, Zeile 980

**Problem Legacy**: Zu lang (Sicherheitschecks, LLM-Calls, Bildgenerierung sequentiell)

**DevServer-Strategie**:
- Modulares System erlaubt flexiblere Parallelisierung
- Chunks können parallel ausgeführt werden wenn keine Abhängigkeiten
- Pipeline-Optimizer analysiert Dependency-Graph

**Priorität**: Hoch

---

## Priorisierte Roadmap

### Phase 1 (Kritisch - MVP für Workshops)
1. ✅ Stateful Server (Session-Management)
2. ✅ Edit-Interface für Meta-Prompts (Klientel + Pädagog*innen)
3. ✅ DS-GVO-konforme Bild-Upload-Policy
4. ✅ Timeout-Optimierung (Parallelisierung, Caching)

### Phase 2 (Hoch - Qualitätsverbesserungen)
1. Safety-System-Effizienz (Konsolidierung, Image-Analyse)
2. Performance-Optimierung Workflow-Zeiten
3. Ausführliche Safety-Begründungen

### Phase 3 (Mittel - Erweiterungen)
1. Multi-Backend-Support (LMStudio, deutsche Anbieter)
2. False-Positive-Behandlung verbessern
3. Workflow-Orchestrierung via LLM

### Phase 4 (Niedrig - Nice-to-Have)
1. Vollständige Mehrsprachigkeit
2. Weitere Play/Dialog-Mode-Features

---

## Zusammenfassung: DevServer vs. Legacy

| Aspekt | Legacy-Server | DevServer |
|--------|---------------|-----------|
| **Architektur** | ComfyUI-JSON-Manipulation | Chunk+Pipeline+Config |
| **Interaktivität** | Stateless, linear | Stateful, interaktiv |
| **Meta-Prompts** | Hidden in Workflows | Explizit editierbar |
| **Default-Modus** | SD 3.5 ohne Interception möglich | Aktive Aneignung forced |
| **Safety** | 3-Layer, sequentiell | Konsolidiert, parallel |
| **Performance** | Timeouts in Workshops | Optimiert für Echtzeit |
| **DS-GVO** | Bilder nie extern (hardcoded) | Flexible Policy per Backend |
| **Pädagogik** | Weg des geringsten Widerstands | Reflexion als Standard |

---

**Letztes Update**: 26. Oktober 2025 (nach Legacy-Dokumentation)
