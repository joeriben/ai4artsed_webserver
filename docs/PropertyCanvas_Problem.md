# Property Selection Interface - Funktionale & Visuelle Spezifikation

## 1. ZWECK DER SEITE

Eine **Konfigurations-Auswahl-Oberfläche** für AI-Kunst-Generierung, bei der Nutzer:
1. **EINE Kategorie** auswählen (XOR: nur eine gleichzeitig)
2. Daraufhin passende **Konfigurationen** sehen
3. Eine **Konfiguration** anklicken und zur Pipeline-Ausführung weitergeleitet werden

## 2. VISUELLE STRUKTUR

### 2.1 Layout-Hierarchie
```
VIEWPORT (Vollbild)
├── HEADER (oben, fixiert)
│   ├── Titel: "Konfiguration auswählen" (links)
│   └── Button: "Auswahl löschen" (rechts, nur sichtbar wenn etwas ausgewählt)
│
└── HAUPTBEREICH (restlicher Raum)
    ├── CATEGORY-BUBBLES (5 Kreise, IMMER sichtbar)
    └── CONFIG-BUBBLES (große Kreise mit Bildern, NUR bei Auswahl sichtbar)
```

### 2.2 Category-Bubbles (Zentrale Auswahlkreise)

**Position:** EXAKT im Zentrum des Viewports

**Anordnung:**
- **Mitte:** Freestyle (🫵) - goldgelb (#FFC107)
- **Drumherum in X-Formation (45° versetzt):**
  - Oben-rechts: Semantics (💬) - blau (#2196F3)
  - Unten-rechts: Aesthetics (🪄) - lila (#9C27B0)
  - Unten-links: Arts (🖌️) - pink (#E91E63)
  - Oben-links: Heritage (🌍) - grün (#4CAF50)

**Größe:** Proportional zum Viewport (ca. 12% der kleineren Dimension)

**Verhalten:**
- Hover: Leicht vergrößern, heller
- Klick: Toggle-Auswahl (an/aus) - **DESELEKTIERT alle anderen (XOR)**
- Ausgewählt: Farbfüllung statt nur Rand
- Draggable: Innerhalb eines unsichtbaren Kreises bewegbar

### 2.3 Config-Bubbles (Konfigurationskreise)

**Erscheinen:** NUR wenn GENAU EINE Category ausgewählt

**Position:** Gruppiert um die jeweils zugehörige Category-Bubble
- Jede Config "gehört" zu einer Category
- Bilden einen Kranz um ihre Category
- Abstand proportional zum Viewport

**Aussehen:**
- Größer als Category-Bubbles (ca. 2x)
- Enthalten Vorschaubild der Konfiguration
- Label unten (z.B. "Bauhaus", "Expressionismus")

**Verhalten:**
- Hover: Leicht vergrößern
- Klick: Navigiert zur Pipeline-Ausführung

## 3. FUNKTIONALE ANFORDERUNGEN

### 3.1 Initialer Zustand
- Alle Category-Bubbles sichtbar, keine ausgewählt
- Keine Config-Bubbles sichtbar
- Header zeigt nur Titel

### 3.2 Interaktionsflow (XOR-LOGIK)

1. **User klickt Category** (z.B. "Arts")
   - Arts wird hervorgehoben (gefüllt)
   - **ALLE ANDEREN Categories werden automatisch deselektiert**
   - NUR Arts-Configs erscheinen
   - "Auswahl löschen" Button erscheint

2. **User klickt andere Category** (z.B. "Heritage")
   - Arts wird automatisch deselektiert
   - Heritage wird selektiert
   - Arts-Configs verschwinden
   - Heritage-Configs erscheinen
   - **Immer nur EINE Category aktiv**

3. **User klickt gleiche Category nochmal**
   - Category wird deselektiert
   - Alle Configs verschwinden
   - Zurück zum Ausgangszustand

4. **User klickt Config** (z.B. "Bauhaus")
   - Navigation zu `/pipeline-execution/bauhaus`
   - Store wird geleert für frischen Start

### 3.3 XOR-Regel (KRITISCH)
- **NIEMALS** mehr als eine Category gleichzeitig aktiv
- Klick auf neue Category = automatisch alte deselektieren
- Keine Mehrfachauswahl
- Keine komplexe Filterung (immer nur 1 Category-Set)

## 4. RESPONSIVE ANFORDERUNGEN

**Desktop (1920x1080):**
- Volle Kreisanordnung sichtbar
- Alle Elemente gut verteilt

**Tablet (iPad, 1024x768):**
- Proportional skaliert
- Gleiche Anordnung, kleinere Bubbles

**Keine Mobile-Unterstützung** (nur Desktop/Tablet)

## 5. TECHNISCHE CONSTRAINTS

### 5.1 Zentrierung (ABSOLUT KRITISCH)
- **MUSS** viewport-zentriert sein
- NICHT abhängig von Container-Dimensionen
- Freestyle-Bubble EXAKT in Bildschirmmitte
- Unabhängig von Header-Höhe

### 5.2 Skalierung
- Alle Größen **proportional zum Viewport**
- KEINE festen Pixel-Werte für Positionen
- Basis: `min(viewport-width, viewport-height)`
- Prozentuale Positionierung innerhalb quadratischem Container

### 5.3 Performance
- Smooth animations (60fps)
- Keine Layout-Shifts beim Toggle
- Configs lazy-loaden wenn möglich

## 6. DATENSTRUKTUR

**Categories:**
```
- semantics: { symbol: '💬', color: '#2196F3' }
- aesthetics: { symbol: '🪄', color: '#9C27B0' }
- arts: { symbol: '🖌️', color: '#E91E63' }
- heritage: { symbol: '🌍', color: '#4CAF50' }
- freestyle: { symbol: '🫵', color: '#FFC107' }
```

**Configs:**
```
Beispiel:
{
  id: 'bauhaus',
  name: 'Bauhaus',
  imageUrl: '/images/bauhaus.jpg',
  category: 'arts'  // Gehört zu EINER Category
}
```

**Selection State:**
```
selectedCategory: 'arts' | 'heritage' | ... | null
```
- **Single Value** (nicht Array/Set!)
- null = nichts ausgewählt

## 7. KRITISCHE ERFOLGSFAKTOREN

1. **PERFEKTE ZENTRIERUNG** - Freestyle-Bubble EXAKT in Viewport-Mitte
2. **XOR-LOGIK** - Nur EINE Category gleichzeitig
3. **PROPORTIONALE SKALIERUNG** - Identisches Layout auf allen Screens
4. **KLARE SELEKTION** - User sieht sofort was ausgewählt ist
5. **SMOOTH TRANSITIONS** - Configs erscheinen/verschwinden elegant

## 8. BEKANNTE PROBLEME (MUSS VERMIEDEN WERDEN)

### 8.1 Zentrierung
- ❌ Container-basierte Zentrierung → Verschiebung nach rechts
- ❌ Vermischung von viewport- und container-Units
- ❌ Abhängigkeit von Parent-Dimensionen

### 8.2 Positionierung
- ❌ Pixel-basierte Positionen → nicht responsive
- ❌ Absolute Positionen ohne richtigen Bezugspunkt
- ❌ Z-Index-Konflikte zwischen Layern

### 8.3 Vue/Vite-spezifisch
- ❌ HMR-Cache hält gelöschte Components im Speicher
- ❌ Development vs Production Ports verwechseln
- ❌ Component-Updates werden nicht reflektiert

## 9. IMPLEMENTATION-STRATEGIE (HIGH LEVEL)

### 9.1 DOM-Struktur
```
<div id="app">                           // Fullscreen
  <div class="selection-view">           // Fullscreen
    <header>...</header>                 // Fixed height
    <div class="bubble-container">       // Centered square
      <CategoryBubble v-for="..." />     // %-positioned
      <ConfigBubble v-for="..." />       // %-positioned
    </div>
  </div>
</div>
```

### 9.2 CSS-Strategie
- Container: `position: fixed; inset: 0;` für Fullscreen
- Zentrierung: `display: flex; align-items: center; justify-content: center;`
- Quadrat: `width: min(70vw, 70vh); aspect-ratio: 1/1;`
- Bubbles: `position: absolute; left: X%; top: Y%;`

### 9.3 State Management
- Single source of truth für `selectedCategory`
- Computed property für sichtbare Configs
- Clear separation zwischen UI und Business Logic

## 10. ACCEPTANCE CRITERIA

✅ Freestyle-Bubble ist EXAKT in Viewport-Mitte
✅ Nur EINE Category kann ausgewählt sein (XOR)
✅ Config-Bubbles erscheinen nur bei Auswahl
✅ Responsive auf Desktop und Tablet
✅ Smooth animations ohne Flackern
✅ Navigation zu Pipeline funktioniert
✅ "Auswahl löschen" resettet alles

---

**DIESE SPEZIFIKATION IST DIE ABSOLUTE WAHRHEIT. JEDE IMPLEMENTATION MUSS DIESE EXAKT ERFÜLLEN.**