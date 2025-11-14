# Property Taxonomy - Symbols & Category Naming Discussion

**Date:** 2025-11-09
**Session:** 40
**Status:** Design Discussion - Awaiting Research Project Feedback
**Related Docs:**
- `SESSION_37_PROPERTY_TAXONOMY_REVISION.md` (Pädagogische Bedeutungen)
- `PROPERTY_TAXONOMY_SUMMARY.md` (Config-Zuweisungen)

---

## Context

Die aktuellen Property-Pair-Begriffe (chill/chaotic, narrative/algorithmic, etc.) sind **pädagogisch präzise**, aber **für Jugendliche abstrakt und schwer verständlich**. Diese Diskussion untersucht:

1. **Problem der Kategorie-Kongruenz** (Kat 1 und 6 überlappen)
2. **Symbole als visuelle Anker** für abstraktes Verständnis
3. **Tooltip-Erklärungen** für pädagogischen Hintergrund

---

## Teil 1: Problem - Kategorie-Kongruenz

### Befund: Kat 1 und 6 sind semantisch kongruent

**Kategorie 1: chill ↔ chaotic**
- chill = kontrollierter Kontext, erwartbar, steuerbar
- chaotic = Kontrollverlust, unvorhersagbar

**Kategorie 6: playful ↔ serious**
- playful = mehr Freiheitsgrade
- serious = Genrekonventionen

**Das Problem:**
- chill (erwartbar) → tendenziell serious (strukturiert)
- chaotic (unvorhersagbar) → tendenziell playful (frei)

→ **Die Kategorien messen ähnliche Dimensionen** (Erwartbarkeit/Kontrolle vs. Freiheit/Struktur)

---

## Teil 2: Lösung - Kategorie 1 umbenennen (Option B)

### Vorschlag: Präzisere Begriffe für Kat 1

**ALT:**
- chill ↔ chaotic

**NEU:**
- **vorhersagbar ↔ überraschend**

### Vorteile:
1. **Klarer vom Begriff her**: "vorhersagbar" ist direkter als "chill"
2. **Differenzierung zu Kat 6**:
   - Kat 1 = Erwartbarkeit des **Outputs**
   - Kat 6 = Freiheitsgrade vs. Genrekonventionen (Struktur des **Prozesses**)
3. **Jugendgerechter**: Konkrete Begriffe statt metaphorischer (chill/wild)

### Pädagogische Bedeutung bleibt gleich:
- **vorhersagbar**: Output ist erwartbar, steuerbar, kontrolliert
- **überraschend**: Output ist unvorhersehbar, unerwartete Wendungen

---

## Teil 3: Die 6 Property-Paare mit pädagogischem Hintergrund

| # | Paar | Pädagogische Bedeutung | Beispiel |
|---|------|------------------------|----------|
| **1** | vorhersagbar ↔ überraschend | Erwartbarkeit des Outputs | Bauhaus (vorhersagbar) vs. Dada (überraschend) |
| **2** | narrative ↔ algorithmic | Transformationsprinzip | Expressionismus (erzählt) vs. PigLatin (Regel) |
| **3** | facts ↔ emotion | Gewünschter Bildeindruck (User-Wunsch) | TechnicalDrawing (nüchtern) vs. Surrealization (emotional) |
| **4** | historical ↔ contemporary | Heritage-Typ: museal vs. lebendig | Renaissance (eingefroren) vs. Stille Post (living) |
| **5** | explore ↔ create | Pädagogische Orientierung | ClichéFilter (austesten) vs. Dadaism (artikulieren) |
| **6** | playful ↔ serious | Strukturfreiheit vs. Genrekonventionen | Overdrive (frei) vs. Bauhaus (Genre) |

### Wichtige Klarstellungen:

**Kat 3 (facts/emotion):**
- **User-orientiert**: Welchen Bildeindruck will ich erzielen?
- **Kunstpädagogisch wichtig**: Nüchterner vs. emotionaler visueller Effekt
- **NICHT:** Rational vs. Affektiv als Denkweise

**Kat 5 (explore/create):**
- **explore** = prozessorientiert: KI challengen, kritisch diskutieren, reflektieren
- **create** = ergebnisorientiert: Output interessiert als Artikulation, Kreativität
- **NICHT**: explore = Prozess, create = Output (zu simpel)
- **SONDERN**: Beide sind prozessorientiert, aber mit unterschiedlichem Fokus

---

## Teil 4: Symbol-Vorschläge mit Mouseover-Tooltips

### Überlegung: Warum Symbole?

**Problem:** Die pädagogischen Hintergründe sind abstrakt und schwer zu vermitteln.

**Lösung:** Symbole als **visuelle Anker** + **Tooltips** für Erklärung

**Vorteil:**
1. Schnellere visuelle Orientierung im Interface
2. Configs werden sowieso eingeblendet → Symbole helfen beim Filtern
3. Mouseover-Tooltip gibt pädagogischen Kontext für Interessierte

---

### Symbol-Vorschläge (Version 1 - REVIDIERT)

**WICHTIG: "narrative" = semantisch/bedeutungsorientiert, NICHT "Geschichten erzählen"**

| Paar | Links | Symbol | Rechts | Symbol | Tooltip (Links) | Tooltip (Rechts) |
|------|-------|--------|--------|--------|-----------------|------------------|
| **1. vorhersagbar/überraschend** | vorhersagbar | 🎯 | überraschend | 🎲 | "Der Output ist erwartbar und steuerbar" | "Der Output ist unvorhersehbar mit überraschenden Wendungen" |
| **2. narrative/algorithmic** | semantisch | 💭 | syntaktisch | ⚙️ | "Transformation durch Bedeutung und Kontext" | "Transformation durch Regeln und Syntax" |
| **3. facts/emotion** | nüchtern | 🧊 | emotional | 🔥 | "Nüchterner, sachlicher Bildeindruck" | "Emotionaler, atmosphärischer Bildeindruck" |
| **4. historical/contemporary** | museal | 🏛️ | lebendig | 💫 | "Museale Kunstbewegung (eingefroren)" | "Living heritage oder zeitlose Konzepte" |
| **5. explore/create** | austesten | 🔬 | artikulieren | ✍️ | "KI-Modelle challengen, kritisch reflektieren" | "Sich ausdrücken, künstlerisch artikulieren" |
| **6. playful/serious** | frei | 🪁 | strukturiert | 📐 | "Viele Freiheitsgrade, experimentell" | "Klare Genrekonventionen, strukturiert" |

### Änderungen:
- **Kat 2**: 📖 → 💭 (Bedeutung/Sinn statt Buch/Geschichte)
- **Kat 5**: 🎨 → ✍️ (Schreiben/Artikulieren statt Malen, da es um Ausdruck geht, nicht nur visuelle Kunst)

---

### Alternative Symbol-Optionen - Detaillierte Analyse

#### Paar 1: vorhersagbar ↔ überraschend (Erwartbarkeit)

| Option | Links | Rechts | Bewertung |
|--------|-------|--------|-----------|
| **A** | 🎯 (Zielscheibe) | 🎲 (Würfel) | ✅ **Empfohlen**: Klar, intuitiv |
| **B** | ○ (Kreis) | ⚡ (Blitz) | Kreis zu abstrakt |
| **C** | 📍 (Pin) | 🌪️ (Tornado) | Tornado = zu extrem |
| **D** | ▬ (Linie) | ◇ (Raute) | Zu abstrakt |

**Empfehlung: 🎯 ↔ 🎲** (klar, selbsterklärend)

---

#### Paar 2: semantisch ↔ syntaktisch (Transformationsprinzip)

| Option | Links (semantisch) | Rechts (syntaktisch) | Bewertung |
|--------|-------------------|----------------------|-----------|
| **A** | 💭 (Gedankenblase) | ⚙️ (Zahnrad) | ✅ **Empfohlen**: Bedeutung vs. Mechanismus |
| **B** | 💡 (Glühbirne) | 🔢 (Zahlen) | Glühbirne = Idee (passt nicht perfekt) |
| **C** | 🗨️ (Sprechblase) | 📐 (Lineal) | Sprechblase = Kommunikation (zu eng) |
| **D** | 🧠 (Gehirn) | ⚙️ (Zahnrad) | Gehirn = zu allgemein (auch für emotion) |
| **E** | 🌐 (Weltkugel) | 🔡 (ABC) | Nicht intuitiv genug |

**Problem:** Semantik/Syntax schwer in Symbolen darzustellen!

**Alternative Begriffe zur Diskussion:**
- semantisch → **bedeutungsorientiert** → 💭 (Bedeutung denken)
- syntaktisch → **regelbasiert** → ⚙️ (Mechanismus)

**Empfehlung: 💭 ↔ ⚙️** (beste verfügbare Option, aber Tooltip wichtig)

---

#### Paar 3: nüchtern ↔ emotional (Bildeindruck)

| Option | Links (nüchtern) | Rechts (emotional) | Bewertung |
|--------|-----------------|-------------------|-----------|
| **A** | 🧊 (Eiswürfel) | 🔥 (Feuer) | ✅ **Empfohlen**: Kalt vs. Warm, klar |
| **B** | 📊 (Diagramm) | ❤️ (Herz) | Diagramm = zu spezifisch (Daten) |
| **C** | ▪ (Quadrat) | ♥ (Herz) | Quadrat zu abstrakt |
| **D** | 🏔️ (Berg) | 💖 (Herzfunken) | Berg = nicht eindeutig kühl |

**Empfehlung: 🧊 ↔ 🔥** (starke Metapher, intuitiv)

---

#### Paar 4: museal ↔ lebendig (Heritage-Typ)

| Option | Links (museal) | Rechts (lebendig) | Bewertung |
|--------|---------------|------------------|-----------|
| **A** | 🏛️ (Säulen) | 💫 (Funken) | ✅ **Empfohlen**: Museum vs. Lebendigkeit |
| **B** | 🏺 (Vase) | 🌱 (Pflanze) | Vase = zu speziell |
| **C** | 📜 (Schriftrolle) | ⚡ (Blitz) | Schriftrolle = alt, aber nicht museal |
| **D** | ⧗ (Sanduhr) | 🔄 (Kreislauf) | Sanduhr = Zeit, nicht Museum |
| **E** | 🎭 (Theater-Masken) | 🎪 (Zirkuszelt) | Nicht eindeutig genug |

**Empfehlung: 🏛️ ↔ 💫** (klar, aber 💫 könnte auch "magisch" bedeuten)

**Alternative für "lebendig":**
- 🌟 (Stern) - zu allgemein
- ✨ (Funken) - könnte mit create überlappen
- 🔥 (Feuer) - schon für emotion benutzt
- 💡 (Glühbirne) - passt nicht

**Problem:** "Lebendig" ist schwer in Symbol zu fassen, 💫 ist beste Option

---

#### Paar 5: austesten ↔ artikulieren (Pädagogische Orientierung)

| Option | Links (austesten) | Rechts (artikulieren) | Bewertung |
|--------|------------------|---------------------|-----------|
| **A** | 🔬 (Mikroskop) | ✍️ (Schreiben) | ✅ **Empfohlen**: Analyse vs. Ausdruck |
| **B** | 🔍 (Lupe) | 🎨 (Palette) | Lupe = suchen (passt), Palette = visuell (zu eng) |
| **C** | 🧪 (Reagenzglas) | 💬 (Sprechblase) | Reagenzglas = Chemie (zu speziell) |
| **D** | 🧭 (Kompass) | 🖋️ (Feder) | Kompass = Navigation (passt weniger) |
| **E** | 🔬 (Mikroskop) | 🗣️ (Sprechen) | Sprechen = mündlich (zu eng) |

**Empfehlung: 🔬 ↔ ✍️** (Analyse vs. Schreiben/Ausdruck)

**Alternative für "artikulieren":**
- 🗨️ (Sprechblase) - zu kommunikativ
- 📝 (Notiz) - zu allgemein
- 🖊️ (Stift) - ähnlich ✍️
- 💬 (Nachricht) - zu digital

---

#### Paar 6: frei ↔ strukturiert (Freiheitsgrade)

| Option | Links (frei) | Rechts (strukturiert) | Bewertung |
|--------|-------------|---------------------|-----------|
| **A** | 🪁 (Drachen) | 📐 (Lineal) | ✅ **Empfohlen**: Freiheit vs. Genauigkeit |
| **B** | 🎈 (Ballon) | 📏 (Maßstab) | Ballon = frei, aber kindisch? |
| **C** | 🦋 (Schmetterling) | ⬛ (Quadrat) | Schmetterling = Natur, passt weniger |
| **D** | 🌊 (Welle) | 🧱 (Ziegelstein) | Welle = zu flüssig |
| **E** | 🎪 (Zirkus) | 🏢 (Gebäude) | Zu konkret, weniger abstrakt |

**Empfehlung: 🪁 ↔ 📐** (gute Metapher, aber 🪁 könnte "kindisch" wirken)

**Alternative für "frei":**
- 🕊️ (Taube) - Frieden, nicht Freiheit
- ☁️ (Wolke) - zu passiv
- 🎭 (Masken) - passt nicht
- 🎨 (Palette) - schon bei create

---

## Finale Symbol-Empfehlung (Version 2)

Nach detaillierter Analyse:

| # | Paar | Links | Symbol | Rechts | Symbol |
|---|------|-------|--------|--------|--------|
| 1 | **vorhersagbar/überraschend** | vorhersagbar | 🎯 | überraschend | 🎲 |
| 2 | **semantisch/syntaktisch** | semantisch | 💭 | syntaktisch | ⚙️ |
| 3 | **nüchtern/emotional** | nüchtern | 🧊 | emotional | 🔥 |
| 4 | **museal/lebendig** | museal | 🏛️ | lebendig | 💫 |
| 5 | **austesten/artikulieren** | austesten | 🔬 | artikulieren | ✍️ |
| 6 | **frei/strukturiert** | frei | 🪁 | strukturiert | 📐 |

### Stärken dieser Wahl:
- ✅ **Paar 1, 3, 5**: Sehr klar und intuitiv
- ⚠️ **Paar 2**: Schwierig (Semantik/Syntax abstrakt), Tooltip essentiell
- ⚠️ **Paar 4**: 💫 nicht perfekt für "lebendig", aber beste Option
- ⚠️ **Paar 6**: 🪁 könnte kindisch wirken (Alternative: 🎈?)

### Kritische Punkte für Testing:
1. **Paar 2 (💭⚙️)**: Verstehen Jugendliche "Bedeutung vs. Regel"?
2. **Paar 4 (💫)**: Wird "Funken" als "lebendig" verstanden?
3. **Paar 6 (🪁)**: Wirkt Drachen zu kindisch für ältere Jugendliche (16+)?

---

## Option: Abstraktere/Minimalistischere Symbole (Version 3)

Falls Emojis zu "bunt" oder plattformabhängig sind:

| Paar | Links | Rechts | Anmerkung |
|------|-------|--------|-----------|
| vorhersagbar/überraschend | ◯ | ◇ | Kreis (regelmäßig) vs. Raute (unregelmäßig) |
| semantisch/syntaktisch | ◐ | ▭ | Halb-gefüllt (Bedeutung) vs. leer (Form) |
| nüchtern/emotional | ▢ | ◈ | Quadrat (kalt) vs. Stern (warm) |
| museal/lebendig | ⌛ | ⚡ | Sanduhr (Zeit) vs. Blitz (Energie) |
| austesten/artikulieren | ◎ | ✎ | Kreis mit Punkt vs. Stift |
| frei/strukturiert | ◠ | ▬ | Bogen vs. Linie |

**Vorteil:** Minimalistisch, plattformunabhängig, professioneller
**Nachteil:** Weniger intuitiv, braucht definitiv Tooltips

---

## Teil 5: Frontend-Integration (Entwurf)

### A) Property-Bubble mit Symbol

**Aktuell:**
```vue
<div class="property-bubble">
  {{ $t('properties.' + property) }}
</div>
```

**Mit Symbol:**
```vue
<div class="property-bubble" :title="propertyTooltip">
  <span class="property-icon">{{ propertySymbol }}</span>
  <span class="property-label">{{ $t('properties.' + property) }}</span>
</div>
```

---

### B) Tooltip-Mapping (Beispiel)

```typescript
const propertyTooltips = {
  de: {
    vorhersagbar: "Der Output ist erwartbar und steuerbar",
    überraschend: "Der Output ist unvorhersehbar mit überraschenden Wendungen",
    // ...
  },
  en: {
    predictable: "The output is expected and controllable",
    surprising: "The output is unpredictable with surprising turns",
    // ...
  }
}

const propertySymbols = {
  vorhersagbar: "🎯",
  überraschend: "🎲",
  narrative: "📖",
  algorithmic: "⚙️",
  // ...
}
```

---

### C) Darstellungs-Optionen

**Option 1: Nur Symbol**
```
🎯  🎲  📖  ⚙️
```
- Kompakt, aber schwer zu deuten ohne Mouseover

**Option 2: Symbol + Text (nebeneinander)**
```
🎯 vorhersagbar  |  🎲 überraschend
```
- Klarer, aber braucht mehr Platz

**Option 3: Symbol + Text (untereinander)**
```
    🎯
vorhersagbar
```
- Noch klarer, braucht vertikal mehr Platz

---

## Teil 6: Offene Fragen für Forschungsprojekt

### Forschungsfragen:

1. **Kategorie-Struktur:**
   - Reichen 6 Paare oder sollten weniger sein (z.B. 4-5)?
   - Sind manche Paare wichtiger als andere (Kern vs. Zusatz)?

2. **Begriffe:**
   - Ist "vorhersagbar/überraschend" besser als "chill/chaotic"?
   - Sind "Geschichten erzählen" und "nach Regeln gehen" für Jugendliche verständlich?

3. **Symbole:**
   - Helfen Emojis beim Verständnis oder wirken sie zu "verspielt"?
   - Sind abstrakte Symbole (○◇▪) besser als konkrete (🎯🎲)?

4. **UI/UX:**
   - Nur Symbole oder Symbol + Text?
   - Tooltip immer oder nur auf Wunsch?
   - Sollten die Paare visuell verbunden sein (Rubber-Bands)?

---

## Teil 7: Nächste Schritte

### Kurzfristig (Diese Session):
- [x] Diskussionsstand dokumentieren
- [ ] User-Feedback zu Symbol-Vorschlägen einholen
- [ ] Entscheidung: Version 1 (konkret) vs. Option A (abstrakt)?

### Mittelfristig (Forschungsprojekt):
- [ ] User-Testing mit Jugendlichen (12-16 Jahre)
- [ ] A/B-Testing: Mit vs. ohne Symbole
- [ ] Feedback zu Tooltip-Texten (verständlich?)

### Langfristig (Nach Forschung):
- [ ] Finale Symbolwahl basierend auf Forschungsergebnissen
- [ ] i18n-Integration (Symbole + Tooltips in beiden Sprachen)
- [ ] Accessibility-Check (Screen-Reader, Color-Blind-Mode)

---

## Teil 8: Implementierungs-Vorschlag (wenn entschieden)

### Änderungen im Code:

**1. Backend (`schema_pipeline_routes.py`):**

```python
# Aktuell (Zeile 1288-1295):
property_pairs = [
    ["chill", "chaotic"],
    ["narrative", "algorithmic"],
    ["facts", "emotion"],
    ["historical", "contemporary"],
    ["explore", "create"],
    ["playful", "serious"]
]

# NEU mit Symbolen und Tooltips:
property_pairs = [
    {
        "pair": ["predictable", "surprising"],
        "symbols": ["🎯", "🎲"],
        "tooltips": {
            "de": [
                "Der Output ist erwartbar und steuerbar",
                "Der Output ist unvorhersehbar mit überraschenden Wendungen"
            ],
            "en": [
                "The output is expected and controllable",
                "The output is unpredictable with surprising turns"
            ]
        }
    },
    # ... weitere Paare
]
```

**2. Frontend (`i18n.ts`):**

```typescript
// Neue Begriffe für Kat 1
properties: {
  // ALT: chill, chaotic
  vorhersagbar: 'vorhersagbar', // oder 'predictable'
  überraschend: 'überraschend', // oder 'surprising'

  narrative: 'Geschichten erzählen',
  algorithmic: 'nach Regeln gehen',
  // ...
}

// Neue Tooltips
propertyTooltips: {
  vorhersagbar: 'Der Output ist erwartbar und steuerbar',
  überraschend: 'Der Output ist unvorhersehbar mit überraschenden Wendungen',
  // ...
}

// Symbol-Mapping
propertySymbols: {
  vorhersagbar: '🎯',
  überraschend: '🎲',
  narrative: '📖',
  algorithmic: '⚙️',
  facts: '🧊',
  emotion: '🔥',
  historical: '🏛️',
  contemporary: '💫',
  explore: '🔬',
  create: '🎨',
  playful: '🪁',
  serious: '📐'
}
```

**3. Config-Files:**

Alle Configs mit `chill` oder `chaotic` müssen umbenannt werden:
- `"chill"` → `"predictable"` (oder `"vorhersagbar"`)
- `"chaotic"` → `"surprising"` (oder `"überraschend"`)

**Betroffene Configs (ca. 18):**
- Bauhaus, ClichéFilter V2, ConfucianLiterati, Dadaism, Expressionism, HunkyDoryHarmonizer, Jugendsprache, Overdrive, PigLatin, Renaissance, SD 3.5 TellAStory, SplitAndCombineSpherical, StillePost, Surrealization, TechnicalDrawing, TheOpposite

---

## Teil 9: Entscheidungs-Matrix

### Frage 1: Welche Symbol-Option?

| Option | Vorteile | Nachteile | Empfehlung |
|--------|----------|-----------|------------|
| **Version 1 (Konkret)** | Selbsterklärend, visuell ansprechend | Emoji-Darstellung plattformabhängig | **Empfohlen für MVP** |
| **Option A (Abstrakt)** | Minimalistisch, plattformunabhängig | Schwerer zu deuten ohne Tooltip | Für spätere Iteration |

### Frage 2: Darstellung im Frontend?

| Option | Vorteile | Nachteile | Empfehlung |
|--------|----------|-----------|------------|
| **Nur Symbol** | Sehr kompakt, clean | Schwer zu deuten | Nein |
| **Symbol + Text** | Klar, selbsterklärend | Braucht Platz | **Empfohlen** |
| **Symbol oben, Text unten** | Sehr klar, gute Lesbarkeit | Braucht vertikal viel Platz | Für Desktop-Version |

### Frage 3: Tooltips?

| Option | Vorteile | Nachteile | Empfehlung |
|--------|----------|-----------|------------|
| **Immer sichtbar** | Maximal informativ | Überfüllt UI | Nein |
| **Mouseover** | Informativ für Interessierte, clean | Nicht auf Touch-Geräten | **Empfohlen mit Touch-Alternative** |
| **Click für Info** | Überall verfügbar | Extra Interaktion nötig | Touch-Alternative |

---

## Teil 10: Zusammenfassung & Entscheidung

### Konsens aus Diskussion:

1. **Kat 1 umbenennen:** chill/chaotic → **vorhersagbar/überraschend** ✅
2. **Symbole verwenden:** Version 1 (konkrete Emojis) ✅
3. **Darstellung:** Symbol + Text nebeneinander ✅
4. **Tooltips:** Mouseover-Erklärungen (mit Touch-Alternative) ✅

### Nächster Schritt:

**Warten auf Forschungsprojekt-Diskussion**, dann:
- User-Feedback zu finalen Symbolen einholen
- Begriffe testen (vorhersagbar vs. chill)
- Implementierung starten

---

## Anhang: Vollständige Symbol-Übersicht (Vorschlag 1)

```typescript
// Vollständige Property-Taxonomie mit Symbolen und Tooltips

export const PROPERTY_PAIRS = [
  {
    id: 1,
    pair: ["predictable", "surprising"],
    symbols: ["🎯", "🎲"],
    labels: {
      de: ["vorhersagbar", "überraschend"],
      en: ["predictable", "surprising"]
    },
    tooltips: {
      de: [
        "Der Output ist erwartbar und steuerbar",
        "Der Output ist unvorhersehbar mit überraschenden Wendungen"
      ],
      en: [
        "The output is expected and controllable",
        "The output is unpredictable with surprising turns"
      ]
    },
    colors: ["#9b87f5", "#9b87f5"] // purple (gleiche Farbe für Paar)
  },
  {
    id: 2,
    pair: ["narrative", "algorithmic"],
    symbols: ["📖", "⚙️"],
    labels: {
      de: ["Geschichten erzählen", "nach Regeln gehen"],
      en: ["tell stories", "follow rules"]
    },
    tooltips: {
      de: [
        "Transformation durch Bedeutung und Kontext",
        "Transformation durch Regeln und Schritte"
      ],
      en: [
        "Transformation through meaning and context",
        "Transformation through rules and steps"
      ]
    },
    colors: ["#60a5fa", "#60a5fa"] // blue
  },
  {
    id: 3,
    pair: ["facts", "emotion"],
    symbols: ["🧊", "🔥"],
    labels: {
      de: ["harte Fakten", "weiche Gefühle"],
      en: ["hard facts", "soft feelings"]
    },
    tooltips: {
      de: [
        "Nüchterner, sachlicher Bildeindruck",
        "Emotionaler, atmosphärischer Bildeindruck"
      ],
      en: [
        "Sober, factual image impression",
        "Emotional, atmospheric image impression"
      ]
    },
    colors: ["#f87171", "#f87171"] // red
  },
  {
    id: 4,
    pair: ["historical", "contemporary"],
    symbols: ["🏛️", "💫"],
    labels: {
      de: ["Geschichte", "Gegenwart"],
      en: ["history", "present"]
    },
    tooltips: {
      de: [
        "Museale Kunstbewegung (eingefroren, historisch)",
        "Living heritage oder zeitlose Konzepte"
      ],
      en: [
        "Museum art movement (frozen, historical)",
        "Living heritage or timeless concepts"
      ]
    },
    colors: ["#fb923c", "#fb923c"] // orange
  },
  {
    id: 5,
    pair: ["explore", "create"],
    symbols: ["🔬", "🎨"],
    labels: {
      de: ["KI austesten", "Kunst machen"],
      en: ["test AI", "make art"]
    },
    tooltips: {
      de: [
        "KI-Modelle challengen, kritisch reflektieren (prozessorientiert)",
        "Output als Artikulation, Kreativität (ergebnisorientiert)"
      ],
      en: [
        "Challenge AI models, critically reflect (process-oriented)",
        "Output as articulation, creativity (result-oriented)"
      ]
    },
    colors: ["#4ade80", "#4ade80"] // green
  },
  {
    id: 6,
    pair: ["playful", "serious"],
    symbols: ["🪁", "📐"],
    labels: {
      de: ["bisschen verrückt", "eher ernst"],
      en: ["playful", "serious"]
    },
    tooltips: {
      de: [
        "Viele Freiheitsgrade, experimentell, spielerisch",
        "Klare Genrekonventionen, strukturiert, ernsthaft"
      ],
      en: [
        "Many degrees of freedom, experimental, playful",
        "Clear genre conventions, structured, serious"
      ]
    },
    colors: ["#fbbf24", "#fbbf24"] // yellow
  }
]
```

---

**Status:** Dokumentiert und bereit für Diskussion im Forschungsprojekt
**Nächster Schritt:** User-Feedback zu Symbolen und Begriff-Änderung (chill→vorhersagbar)
**Implementierung:** Auf Entscheidung wartend

---

**Session 40 - Ende der Diskussion**
