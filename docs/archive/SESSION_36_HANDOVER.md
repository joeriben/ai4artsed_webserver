# Session 36 - Property Quadrants UI Debugging & Redesign

**Datum:** 2025-11-08
**Status:** Funktionierend, aber Features fehlen
**Branch:** feature/schema-architecture-v2

## Aktueller Stand (nach git checkout)

Die Basis-Funktionalität ist wiederhergestellt:
- Property Bubbles sind sichtbar und funktionieren
- Rubber bands (gerade Linien) verbinden Property-Paare
- Click-to-toggle Selection funktioniert
- Random positioning mit Collision Detection

**ABER:** Alle neuen Anforderungen aus dieser Session sind verloren gegangen.

## Kritische Erkenntnisse dieser Session

### 1. i18n Problem - Root Cause gefunden

**FEHLER:** `useI18n()` direkt in PropertyBubble.vue führt dazu, dass die Component nicht rendert (Bubbles verschwinden komplett).

**LÖSUNG:** ConfigTile-Pattern verwenden:
- Parent (PropertyCanvas) macht die Übersetzung mit `useI18n()`
- Child (PropertyBubble) bekommt `displayText` als Prop
- Nie `useI18n()` in tief verschachtelten Child-Components!

```typescript
// ❌ FALSCH - PropertyBubble.vue
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
const displayText = computed(() => t(`properties.${props.property}`))

// ✅ RICHTIG - PropertyCanvas.vue
const { t } = useI18n()
function getPropertyDisplayText(property: string) {
  return t(`properties.${property}`)
}

// PropertyBubble als Prop
:display-text="getPropertyDisplayText(property)"
```

### 2. CSS >>> Syntax ist deprecated

Vue 3 warnt: "the >>> and /deep/ combinators have been deprecated"

**LÖSUNG:**
```css
/* ❌ ALT */
.property-canvas >>> .property-bubble {
  pointer-events: all;
}

/* ✅ NEU */
.property-canvas :deep(.property-bubble) {
  pointer-events: all;
}
```

### 3. Z-Index Hierarchie

Property Bubbles müssen ÜBER dem SVG liegen:
```css
.property-canvas {
  z-index: 10;
}

.property-canvas :deep(.property-bubble) {
  z-index: 20; /* Höher als SVG */
}
```

### 4. Prof. Rissen's Autorität über Terminologie

**NIEMALS** die deutschen Property-Begriffe ändern ohne explizite Erlaubnis!

Autorisierte Begriffe (src/i18n.ts:57-68):
```typescript
calm: 'chillig'      // NICHT 'ruhig'
chaotic: 'chaotisch'
narrative: 'erzählen'
algorithmic: 'berechnen'
facts: 'fakten'
emotion: 'gefühl'
historical: 'geschichte'      // NICHT 'vergangenheit'
contemporary: 'gegenwart'     // NICHT 'heute'
explore: 'erforschen'         // NICHT 'erkunden'
create: 'erschaffen'          // NICHT 'gestalten'
playful: 'spiel'              // NICHT 'spielerisch'
serious: 'ernst'
```

## Anforderungen für nächste Session

### Priority 1: i18n Implementation (KRITISCH)

- [ ] PropertyCanvas: `useI18n()` + `getPropertyDisplayText()` function
- [ ] PropertyBubble: `displayText: string` als Prop hinzufügen
- [ ] Template: `{{ displayText || property }}` als Fallback
- [ ] Props Interface anpassen: `displayText` required
- [ ] Test mit deutschen Übersetzungen

### Priority 2: Layout Redesign (User Request)

**Aktuelle Implementierung:** Random positioning mit Collision Detection
**Gewünscht:** Vertikale Liste mit Paaren side-by-side

```typescript
// Neue calculatePropertyPositions() Implementierung:
const startX = 120
const startY = 100
const pairSpacingY = 80   // Vertikal zwischen Paaren
const propertySpacingX = 200  // Horizontal innerhalb Paar

props.propertyPairs.forEach((pair, index) => {
  const yPos = startY + index * pairSpacingY

  positions[pair[0]] = { x: startX, y: yPos }
  positions[pair[1]] = { x: startX + propertySpacingX, y: yPos }
})
```

### Priority 3: Rubber Band Optik (User Request)

**Aktuell:** Gerade `<line>` zwischen Properties
**Gewünscht:** Gekrümmte Bezier-Kurven mit "sag"

```typescript
// PropertyCanvas.vue - Template
<path
  :d="getRubberBandPath(pair[0], pair[1])"
  :stroke="propertyColors[index]"
  stroke-width="3"
  stroke-opacity="0.5"
  fill="none"
  stroke-linecap="round"
  class="rubber-band"
/>

// Shadow Layer für Depth
<path
  :d="getRubberBandPath(pair[0], pair[1])"
  :stroke="propertyColors[index]"
  stroke-width="5"
  stroke-opacity="0.15"
  fill="none"
  stroke-linecap="round"
/>

// getRubberBandPath Function
function getRubberBandPath(prop1: string, prop2: string): string {
  const pos1 = getPropertyPosition(prop1)
  const pos2 = getPropertyPosition(prop2)

  const midX = (pos1.x + pos2.x) / 2
  const midY = (pos1.y + pos2.y) / 2
  const controlY = midY + 20  // Sag effect

  return `M ${pos1.x} ${pos1.y} Q ${midX} ${controlY} ${pos2.x} ${pos2.y}`
}
```

### Priority 4: Drag & Drop (User Request)

PropertyBubble soll wie ConfigTile draggable sein:

```typescript
// PropertyBubble.vue
const isDragging = ref(false)
const currentX = ref(props.x)
const currentY = ref(props.y)
const hasMoved = ref(false)

function handleMouseDown(event: MouseEvent) {
  event.preventDefault()
  isDragging.value = true
  hasMoved.value = false
  dragStartX.value = event.clientX - currentX.value
  dragStartY.value = event.clientY - currentY.value
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseUp(event: MouseEvent) {
  // Only toggle if NOT moved
  if (!hasMoved.value) {
    emit('toggle', props.property)
  }
}
```

Cursor ändern:
```css
.property-bubble {
  cursor: grab;
}

.property-bubble.dragging {
  cursor: grabbing;
}
```

### Priority 5: Visual Polish

**Bubble Design Improvements:**
```css
.property-bubble {
  padding: 14px 28px;
  background: radial-gradient(ellipse at 30% 30%,
    rgba(40, 40, 40, 0.95),
    rgba(15, 15, 15, 0.98));
  border: 3px solid var(--bubble-color);
  border-radius: 50px;  /* Organischer */
  backdrop-filter: blur(8px);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy */
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.property-bubble:hover {
  transform: translate(-50%, -50%) scale(1.08) rotate(-2deg);
  box-shadow: 0 0 30px var(--bubble-color);
}

.property-bubble.selected {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 60px var(--bubble-color);
  }
  50% {
    box-shadow: 0 0 80px var(--bubble-color);
  }
}
```

**Rubber Band Animations:**
```css
.rubber-band {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}
```

## Bereits Erledigte Tasks (aus vorheriger Session)

✅ Backend config filtering - "deactivated" Ordner wird ausgeschlossen
✅ Short descriptions verbessert (220 chars, vollständige Sätze)
✅ Config tiles ohne properties footer
✅ Config tiles mit 24px border-radius (spielerischer)
✅ clearAllProperties() on mount (keine Tiles ohne Selection)
✅ Property area bounds: 55% × 60% (mehr Platz)

## Wichtige Dateien

**Frontend Components:**
- `src/components/PropertyBubble.vue` - Einzelne Property Bubble
- `src/components/PropertyCanvas.vue` - Container mit SVG rubber bands
- `src/components/ConfigCanvas.vue` - Config Tiles Verteilung
- `src/views/PropertyQuadrantsView.vue` - Main View
- `src/i18n.ts` - Übersetzungen (AUTORITATIVE deutsche Begriffe!)

**Backend:**
- `devserver/my_app/routes/schema_pipeline_routes.py:977` - EXCLUDED_DIRS

## Git Status

```bash
git status
# Modified files:
# - ConfigCanvas.vue
# - ConfigTile.vue
# - PropertyBubble.vue (restored to HEAD)
# - PropertyCanvas.vue (restored to HEAD)
# - i18n.ts (restored to HEAD)
# - PropertyQuadrantsView.vue
```

**Letzte funktionierende Version:** Commit `67bdd57`

## Implementierungs-Reihenfolge für nächste Session

1. **i18n Pattern implementieren** (ConfigTile-Ansatz)
2. **Layout ändern** (vertikale Paare statt random)
3. **Rubber bands verbessern** (Bezier-Kurven)
4. **>>> zu :deep() ändern** (alle .vue Dateien)
5. **Drag & Drop hinzufügen**
6. **Visual Polish** (gradients, animations)

## Testing Checklist

- [ ] Bubbles werden korrekt angezeigt
- [ ] Deutsche Übersetzungen sind sichtbar
- [ ] Property-Paare stehen nebeneinander (nicht random verteilt)
- [ ] Rubber bands sind gekrümmt
- [ ] Bubbles sind draggable
- [ ] Click (ohne drag) toggled Selection
- [ ] XOR Logic funktioniert innerhalb Paare
- [ ] AND Logic funktioniert zwischen Paaren
- [ ] Config tiles erscheinen nur nach Property-Selection
- [ ] Deactivated configs sind ausgeblendet
- [ ] Hard reload funktioniert (Strg+Shift+R)

## Known Issues

1. HMR kann manchmal Components nicht korrekt reloaden → Hard Reload nötig
2. i18n in Child Components verursacht Rendering-Probleme
3. >>> CSS Syntax ist deprecated aber funktioniert (noch)

## Nächste Schritte

**Start hier in Session 37:**
1. Read PropertyBubble.vue und PropertyCanvas.vue
2. Implementiere i18n Pattern (ConfigTile approach)
3. Test: Bubbles mit deutschen Labels sichtbar?
4. Implementiere vertikales Paare-Layout
5. Ersetze gerade Linien mit Bezier-Kurven
6. Test: User sagt "sehr viel besser"? → Weiter mit Drag & Drop

**Bei Problemen:**
- NIEMALS useI18n() in PropertyBubble.vue!
- Immer displayText als Prop übergeben
- Git checkout auf 67bdd57 als Fallback
