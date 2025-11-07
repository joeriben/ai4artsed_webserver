# Property-Taxonomie für Workflow-Configs - Iteration 03 (BRAINSTORMING)

**Status:** WORK IN PROGRESS - Brainstorming-Phase
**Datum:** 2025-11-06
**Iteration:** 03 - Agency-orientierte Spannungsfelder

---

## Paradigmenwechsel: Von Tags zu Agency-Fragen

### Problem mit neutralen Tags
❌ **Falsch:** `[lustig] [verrückt] [künstlerisch] [einfach] [schnell]`
- Konsumistische Haltung: "Ich will jetzt was Lustiges"
- Bedient USER-Subjektmodell
- Vermittelt solutionistische KI-Ideologie

### Lösung: Positionierung fordern
✅ **Richtig:** Interface fordert zur **Positionierung gegenüber der KI** auf
- Keine Mitte, keine Defaults
- Entscheidungen provozieren, nicht Auswahl anbieten
- "Wie verhalte ich mich zur KI-Maschine?"

---

## Zentrale Spannungsfelder (keine Mitte!)

### 1. Kontrolle ←→ Kontrollverlust

**Vorhersehbar/Kontrolliert:**
- ClichéFilter (normativ)
- ConfucianLiterati (regelbasiert)
- Bauhaus (Prinzipien)
- TechnicalDrawing (systematisch)

**Überraschend/Unkontrolliert:**
- Overdrive (Übertreibung)
- TheOpposite (Umkehrung)
- Surrealization (Traumlogik)
- Dada (Nonsens)

**Pädagogisch:**
- Erfahrung von Agency
- Wer bestimmt das Ergebnis?

---

### 2. Semantisch ←→ Algorithmisch

**Bedeutungsbasiert:**
- Jugendsprache (soziolinguistisch)
- Dada (als Kunsthaltung)
- YorubaHeritage (kosmologisch)
- Expressionism (emotional)

**Regelbasiert:**
- PigLatin (Buchstabentausch)
- SplitAndCombine (Vektor-Operationen)
- StillePost (Sprachketten-Algorithmus)
- QuantumTheory (Ontologie-Mapping)

**Pädagogisch:**
- Unterschied zwischen "Verstehen" und "Befolgen"
- Was kann KI wirklich?

---

### 3. KI-Verhältnis: Wie arbeite ich mit der Maschine?

**3.1 KI als Werkzeug** (Ich kontrolliere)
- ClichéFilter
- Bauhaus
- TechnicalDrawing
- Translation
→ "KI soll machen, was ICH will"

**3.2 KI als Überraschung** (Ich gebe Kontrolle ab)
- Overdrive
- TheOpposite
- Surrealization
- Dada
→ "KI soll mich ÜBERRASCHEN"

**3.3 KI als transparenter Prozess** (Ich lerne verstehen)
- StillePost (8 Schritte sichtbar)
- LLM-Comparison (Modellunterschiede)
- ImageComparison
→ "KI soll zeigen, WIE SIE denkt"

**3.4 KI als kritischer Endgegner** (Ich teste Grenzen)
- YorubaHeritage (kulturelle Indifferenz)
- ConfucianLiterati (Bias sichtbar)
- TraditionalChinese (Klischees)
→ "KI soll ihre GRENZEN zeigen"

---

## Interface-Konzept für Phase 1

### Ebene 1: Positionierungs-Frage (vor den Tiles)

```
╭───────────────────────────────────────────────╮
│                                               │
│  Wer bestimmt, was entsteht?                  │
│  Du oder die KI?                              │
│                                               │
│  ◉ Ich will Kontrolle behalten                │
│  ○ Ich will Kontrolle abgeben                 │
│  ○ Ich will verstehen, wie KI denkt           │
│  ○ Ich will sehen, wo KI scheitert            │
│                                               │
╰───────────────────────────────────────────────╯
```

**Wichtig:** Keine neutrale Option! Zwingt zur Positionierung.

---

### Ebene 2: Zweites Spannungsfeld (Slider)

```
Bedeutung zählt ←─────────────────→ Regeln zählen
(Semantisch)                         (Algorithmisch)

[Dada]  [Jugendsprache]    [StillePost]  [PigLatin]
```

**Keine Mitte-Position!** Slider muss zu einem der Pole gezogen werden.

---

### Ebene 3: Gefilterte Tiles mit Haltungs-Beschreibung

**Statt neutraler Beschreibung:**
❌ "Transformiert Text nach Dada-Prinzipien"

**Agency-orientierte Beschreibung:**
✅ "Zerstört Bedeutung. Du verlierst Kontrolle. KI produziert Nonsens."

**Beispiele:**

**Dada-Card:**
```
╭─────────────────────────────────╮
│  🎨 Dada-Transformation          │
│                                  │
│  Zerstört Bedeutung.             │
│  Du verlierst Kontrolle.         │
│  KI produziert Nonsens.          │
│                                  │
│  ⭐⭐⭐                         │
│  [Wählen]                        │
╰─────────────────────────────────╯
```

**YorubaHeritage-Card:**
```
╭─────────────────────────────────╮
│  🎨 Yoruba-Kosmologie            │
│                                  │
│  Verlangt nicht-westliches       │
│  Denken. KI wird scheitern       │
│  (Klischees, Bias).              │
│                                  │
│  ⭐⭐⭐⭐                       │
│  [Wählen]                        │
╰─────────────────────────────────╯
```

**StillePost-Card:**
```
╭─────────────────────────────────╮
│  💬 Stille Post                  │
│                                  │
│  Du siehst jeden Schritt.        │
│  8 Sprachen. Bedeutung driftet.  │
│  KI zeigt, wie sie arbeitet.     │
│                                  │
│  ⭐⭐⭐                         │
│  [Wählen]                        │
╰─────────────────────────────────╯
```

---

## Property-Schema für Configs (Backend)

### Minimalschema

```json
"properties": {
  "kontrolle": "vorhersehbar" | "unkontrolliert",
  "modus": "semantisch" | "algorithmisch",
  "ki_verhaeltnis": "werkzeug" | "ueberraschung" | "transparenz" | "grenze"
}
```

### Beispiele

**Dada:**
```json
{
  "id": "dada",
  "name": { "de": "Dadaismus", "en": "Dadaism" },
  "properties": {
    "kontrolle": "unkontrolliert",
    "modus": "semantisch",
    "ki_verhaeltnis": "ueberraschung"
  },
  "display": {
    "phase1_description": {
      "de": "Zerstört Bedeutung. Du verlierst Kontrolle. KI produziert Nonsens.",
      "en": "Destroys meaning. You lose control. AI produces nonsense."
    }
  }
}
```

**YorubaHeritage:**
```json
{
  "id": "yorubaheritage",
  "name": { "de": "Yoruba-Kosmologie", "en": "Yoruba Cosmology" },
  "properties": {
    "kontrolle": "vorhersehbar",
    "modus": "semantisch",
    "ki_verhaeltnis": "grenze"
  },
  "display": {
    "phase1_description": {
      "de": "Verlangt nicht-westliches Denken. KI wird scheitern (Klischees, Bias).",
      "en": "Demands non-Western thinking. AI will fail (clichés, bias)."
    }
  }
}
```

**StillePost:**
```json
{
  "id": "stillepost",
  "name": { "de": "Stille Post", "en": "Chinese Whispers" },
  "properties": {
    "kontrolle": "unkontrolliert",
    "modus": "algorithmisch",
    "ki_verhaeltnis": "transparenz"
  },
  "display": {
    "phase1_description": {
      "de": "Du siehst jeden Schritt. 8 Sprachen. Bedeutung driftet. KI zeigt, wie sie arbeitet.",
      "en": "You see every step. 8 languages. Meaning drifts. AI shows how it works."
    }
  }
}
```

**Bauhaus:**
```json
{
  "id": "bauhaus",
  "name": { "de": "Bauhaus", "en": "Bauhaus" },
  "properties": {
    "kontrolle": "vorhersehbar",
    "modus": "semantisch",
    "ki_verhaeltnis": "werkzeug"
  },
  "display": {
    "phase1_description": {
      "de": "Reduziert auf geometrische Form. Du behältst Kontrolle. KI folgt Prinzipien.",
      "en": "Reduces to geometric form. You keep control. AI follows principles."
    }
  }
}
```

---

## Pädagogische Hintergrund-Logik (nicht im Interface sichtbar)

### YorubaHeritage/ConfucianLiterati sind NICHT "Bewahrung"

**Pädagogisches Ziel:**
- Zeigen **Klischeebildung** westlich trainierter Modelle
- Machen **kulturelle Indifferenz** erfahrbar
- Sind **Endgegner** für die KI (scheitert oft)
- Bias wird durch Nutzung selbst erfahren

**Wichtig:** Das muss nicht explizit gesagt werden. Es wird **erfahren** beim Nutzen.

---

## Offene Fragen

### 1. Medien-Output als Dimension?

**Aktuell:** Nicht als Spannungsfeld modelliert
**Überlegung:** Output-Medium (Text/Bild/Audio) als gleichwertige Eigenschaft?
**UI-Konzept:** Schwebende Bubbles am unteren Rand?

```
[Oben: Eigenschaften]
[Mitte: Workflow-Auswahl]
[Unten: Medien-Bubbles]  [📝 Text]  [🖼️ Bild]  [🔊 Audio]
```

**Frage:** Wie integrieren ohne konsumistische Logik ("Ich will ein Bild")?

---

### 2. Wie viele Ebenen?

**Option A: Zwei Ebenen**
1. KI-Verhältnis (4 Optionen)
2. Semantisch ←→ Algorithmisch (Slider)
→ Ergebnis: Gefilterte Tiles

**Option B: Drei Ebenen**
1. KI-Verhältnis (4 Optionen)
2. Kontrolle ←→ Kontrollverlust (Slider)
3. Semantisch ←→ Algorithmisch (Slider)
→ Ergebnis: Gefilterte Tiles

**Frage:** Zu komplex oder notwendig differenziert?

---

### 3. LLM-Dialog-Modus Integration

**Ursprüngliche Idee:** LLM wählt Workflow + injiziert Meta-Prompt
**Neue Perspektive:** LLM als "Material-Auswahl-Berater"
- Metapher: Künstlerische Materialwahl vor Prozessbeginn
- LLM: Meta-Prompt-Auswahl = Material-Auswahl

**Frage:** Wie wird LLM-Dialog mit Spannungsfeld-UI kombiniert?
**Möglichkeit:** LLM fragt nach Agency-Positionierung, schlägt dann Workflows vor

---

### 4. Nullpunkt / Passthrough

**Problem:** Passthrough = keine Intervention
**Frage:** Wie passt das in Agency-Framework?
**Mögliche Antwort:** "KI als reines Werkzeug, keine Reflexion"
**Oder:** Passthrough ist kein Workflow im eigentlichen Sinne, nur technischer Helper

---

## Nächste Schritte

1. **Vollständige Durchcodierung:** Alle 32 Workflows mit Properties versehen
2. **UI-Mockup:** Phase 1 mit Spannungsfeldern visualisieren
3. **LLM-Integration:** Konzept für Dialog-gestützte Auswahl ausarbeiten
4. **Medien-Output:** Integration ohne Konsumlogik klären
5. **User-Testing:** Mit Zielgruppe (Kinder/Jugendliche) testen

---

## Theoretische Fundierung

### Pädagogische Grundprinzipien (DevServer)

1. **Interception:** Unterbrechung direkten Zugriffs
2. **Transgression:** Grenzüberschreitung
3. **Dekonstruktion:** Zerlegung etablierter Strukturen
4. **Reflexion:** Kritische Distanznahme

→ **Properties müssen diese Bewegungen abbilden, nicht technische Features**

### Gegen Solutionismus

- Kein "User wählt aus" (Konsumlogik)
- Sondern "User positioniert sich" (Agency-Logik)
- KI nicht als Service, sondern als Gegenüber
- Keine Defaults, keine Mitte

---

## ERGÄNZUNG: Vollständige Property-Zuordnungen (21 aktive Configs)

**Finales Property-Set (6 Paare):**

1. `calm` ←→ `chaotic` (chillig - chaotisch)
2. `narrative` ←→ `algorithmic` (erzählen - berechnen)
3. `facts` ←→ `emotion` (fakten - gefühl)
4. `historical` ←→ `contemporary` (geschichte - gegenwart)
5. `explore` ←→ `create` (erforschen - erschaffen)
6. `playful` ←→ `serious` (spiel - ernst)

---

### 1. bauhaus.json
```json
"properties": ["calm", "narrative", "facts", "historical", "create", "serious"]
```

### 2. clichéfilter_v2.json
```json
"properties": ["calm", "narrative", "facts", "contemporary", "explore", "serious"]
```

### 3. confucianliterati.json
```json
"properties": ["calm", "narrative", "emotion", "historical", "explore", "serious"]
```

### 4. dada.json
```json
"properties": ["chaotic", "narrative", "emotion", "historical", "create", "playful"]
```

### 5. expressionism.json
```json
"properties": ["chaotic", "narrative", "emotion", "historical", "create", "serious"]
```

### 6. hunkydoryharmonizer.json
```json
"properties": ["calm", "emotion", "contemporary", "create", "playful"]
```

### 7. imageandsound.json
```json
"properties": ["algorithmic", "contemporary", "create", "serious"]
```

### 8. image_comparison.json
```json
"properties": ["algorithmic", "facts", "contemporary", "explore", "serious"]
```

### 9. imagetosound.json
```json
"properties": ["algorithmic", "contemporary", "create", "serious"]
```

### 10. jugendsprache.json
```json
"properties": ["chaotic", "narrative", "emotion", "contemporary", "create", "playful"]
```

### 11. overdrive.json
```json
"properties": ["chaotic", "narrative", "emotion", "contemporary", "create", "playful"]
```

### 12. piglatin.json
```json
"properties": ["calm", "algorithmic", "facts", "playful"]
```

### 13. quantumtheory.json
```json
"properties": ["chaotic", "algorithmic", "facts", "create", "serious"]
```

### 14. renaissance.json
```json
"properties": ["calm", "narrative", "historical", "create", "serious"]
```

### 15. splitandcombinespherical.json
```json
"properties": ["chaotic", "algorithmic", "facts", "serious"]
```

### 16. stable-diffusion_3.5_tellastory.json
```json
"properties": ["calm", "narrative", "contemporary", "create"]
```

### 17. stillepost.json
```json
"properties": ["chaotic", "algorithmic", "explore", "playful"]
```

### 18. surrealization.json
```json
"properties": ["chaotic", "narrative", "emotion", "historical", "create"]
```
*Hinweis: Keine Zuordnung spiel/ernst (Traum/Unbewusstes)*

### 19. technicaldrawing.json
```json
"properties": ["calm", "algorithmic", "facts", "create", "serious"]
```

### 20. theopposite.json
```json
"properties": ["chaotic", "algorithmic", "contemporary", "create", "playful"]
```

### 21. yorubaheritage.json
```json
"properties": ["calm", "narrative", "emotion", "historical", "explore", "serious"]
```

---

## Statistik: Property-Verteilung

**Paar 1 (chillig - chaotisch):**
- calm: 10
- chaotic: 11

**Paar 2 (erzählen - berechnen):**
- narrative: 13
- algorithmic: 8

**Paar 3 (fakten - gefühl):**
- facts: 9
- emotion: 9

**Paar 4 (geschichte - gegenwart):**
- historical: 8
- contemporary: 10
- keine Zuordnung: 3

**Paar 5 (erforschen - erschaffen):**
- explore: 5
- create: 14
- keine Zuordnung: 2

**Paar 6 (spiel - ernst):**
- playful: 7
- serious: 11
- keine Zuordnung: 3

**Ausgewogene Verteilung über alle Paare** ✅

---

**Nächste Iteration:** UI-Mockup mit 6 Rubberband-Paaren erstellen
