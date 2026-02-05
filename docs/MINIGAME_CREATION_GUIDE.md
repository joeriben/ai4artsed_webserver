# Minigame-Erstellungsanleitung

Anleitung zum Erstellen und Einbinden neuer Edutainment-Minigames in AI4ArtsEd.

---

## 1. Interface (Props)

Jedes Minigame bekommt **genau 2 Props**:

```typescript
const props = defineProps<{
  progress?: number         // 0-100, vom Slider oder echter GPU-Generation
  estimatedSeconds?: number // Geschätzte Generierungsdauer (Default: 30)
}>()
```

Das Minigame muss **keine eigene Logik** für Progress, CO₂-Berechnung oder GPU-Daten implementieren — das liefert der `useAnimationProgress`-Composable.

---

## 2. Pflicht-Composable: `useAnimationProgress`

```typescript
import { useAnimationProgress } from '@/composables/useAnimationProgress'

const {
  internalProgress,  // 0-100, loopt automatisch (0→100→0→100...)
  summaryShown,      // true nach 5 Sekunden (für Info-Box)
  totalCo2,          // Kumulierter CO₂-Wert in Gramm
  effectivePower,    // GPU-Watt (simuliert oder echt)
  effectiveTemp,     // GPU-Temperatur in °C
  treeMinutes        // "X Minuten" für CO₂-Vergleichstext
} = useAnimationProgress({
  estimatedSeconds: computed(() => props.estimatedSeconds || 30),
  isActive: computed(() => (props.progress ?? 0) > 0)
})
```

### Was der Composable macht:
- **Progress-Loop**: 0→100→0→100 automatisch (basierend auf `estimatedSeconds`)
- **GPU-Polling**: Holt echte GPU-Daten oder simuliert sie
- **CO₂-Berechnung**: Kumuliert über die gesamte Laufzeit
- **Summary-Timer**: Zeigt Info-Box nach 5 Sekunden

---

## 3. Dimensionen

| Eigenschaft | Wert |
|---|---|
| Container-Breite | `width: 100%` (passt sich an) |
| Container-Höhe | `height: 320px` (fix) |
| Aspect Ratio | ca. 3:1 |
| Border-Radius | `12px` |
| Overflow | `hidden` |

```css
.mein-minigame {
  position: relative;
  width: 100%;
  height: 320px;
  border-radius: 12px;
  overflow: hidden;
}
```

---

## 4. Wiederverwendbare Komponenten & Composables

### ClimateBackground (Vue-Komponente)
Himmel, Sonne, Wolken, Smog — reagiert auf GPU-Daten.

```vue
<ClimateBackground
  :power-watts="effectivePower"
  :power-limit="450"
  :co2-grams="totalCo2"
  :temperature="effectiveTemp"
/>
```

Wird von IcebergAnimation und ForestMiniGameCanvas verwendet. Einfach in das Template einbauen — positioniert sich absolut im Container.

### Canvas-Composables (optional)

| Composable | Zweck |
|---|---|
| `useCanvasRenderer` | Canvas Setup, Auto-Resize, DPR-Handling |
| `useGameLoop` | RAF- oder Interval-basierte Game-Loops |
| `useCanvasDrawing` | Gradients, Circles, Color-Interpolation |
| `useCanvasObjects` | Objekt-Pool (add/remove/clear) mit Typisierung |

---

## 5. Datei-Struktur

```
src/
  components/edutainment/
    MeinMinigame.vue              ← Neue Komponente hier
    ClimateBackground.vue         ← Wiederverwendbar
    ForestMiniGame.vue            ← Referenz (DOM/CSS)
    ForestMiniGameCanvas.vue      ← Referenz (Canvas)
    IcebergAnimation.vue          ← Referenz (Canvas + DOM-Hybrid)
  composables/
    useAnimationProgress.ts       ← PFLICHT
    useCanvasRenderer.ts          ← Optional
    useGameLoop.ts                ← Optional
    useCanvasDrawing.ts           ← Optional
    useCanvasObjects.ts           ← Optional
  views/
    AnimationTestView.vue         ← Test-Seite mit Tabs
```

---

## 6. Einbindung in AnimationTestView

### 6.1 Import (Script)
```typescript
// In AnimationTestView.vue
import MeinMinigame from '@/components/edutainment/MeinMinigame.vue'
```

### 6.2 Tab-Eintrag
```typescript
const animations = [
  { id: 'pixel', name: '1. Pixel + Bubbles' },
  { id: 'iceberg', name: '2. Klima-Eisberg' },
  { id: 'forest', name: '3. Wald-Spiel' },
  { id: 'forest-canvas', name: '3b. Wald-Spiel (Canvas)' },
  { id: 'mein-spiel', name: '5. Mein Spiel' },  // ← NEU
]
```

### 6.3 Template-Block
```vue
<div v-if="selectedAnimation === 'mein-spiel'" class="animation-wrapper">
  <MeinMinigame :progress="progress" />
</div>
```

### 6.4 Live-Stats ausblenden (wenn eigene Stats vorhanden)
```vue
<!-- In der v-if Bedingung ergänzen: -->
<div v-if="... && selectedAnimation !== 'mein-spiel'" class="live-stats">
```

---

## 7. Minimales Beispiel

```vue
<template>
  <div class="mein-minigame">
    <ClimateBackground
      :power-watts="effectivePower"
      :power-limit="450"
      :co2-grams="totalCo2"
      :temperature="effectiveTemp"
    />

    <canvas ref="canvasRef" @click="handleClick"></canvas>

    <!-- Stats Bar -->
    <div class="stats-bar">
      <span>{{ Math.round(effectivePower) }}W</span>
      <span>{{ totalCo2.toFixed(1) }}g CO₂</span>
    </div>

    <!-- Summary -->
    <Transition name="fade">
      <div v-if="isShowingSummary" class="summary-box">
        {{ totalCo2.toFixed(2) }}g CO₂
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAnimationProgress } from '@/composables/useAnimationProgress'
import ClimateBackground from './ClimateBackground.vue'

const props = defineProps<{
  progress?: number
  estimatedSeconds?: number
}>()

const {
  internalProgress, summaryShown, totalCo2,
  effectivePower, effectiveTemp, treeMinutes
} = useAnimationProgress({
  estimatedSeconds: computed(() => props.estimatedSeconds || 30),
  isActive: computed(() => (props.progress ?? 0) > 0)
})

const isShowingSummary = computed(() => summaryShown.value)

// ... Game-Logik hier ...
</script>

<style scoped>
.mein-minigame {
  position: relative;
  width: 100%;
  height: 320px;
  border-radius: 12px;
  overflow: hidden;
}

canvas {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  z-index: 10;
}
</style>
```

---

## 8. Empfehlungen

### DOM/CSS vs. Canvas
| Ansatz | Vorteile | Nachteile |
|---|---|---|
| **DOM/CSS** (wie ForestMiniGame) | Einfacher, CSS-Animationen, i18n direkt | Viele DOM-Elemente bei vielen Objekten |
| **Canvas** (wie ForestMiniGameCanvas) | Performant bei vielen Objekten, Pixel-Kontrolle | Komplexer, kein CSS, Text-Rendering manuell |
| **Hybrid** (wie IcebergAnimation) | Best of both: DOM für UI, Canvas für Grafik | Zwei Rendering-Systeme |

**Empfehlung**: Hybrid — `ClimateBackground` (DOM) für Himmel/Wolken, Canvas für Game-Objekte, DOM für UI-Overlays (Stats, Summary).

### Assets
- **Google Material Icons SVGs** funktionieren gut auf Canvas (via `Path2D`)
- **Achtung bei FILL0-Icons**: Nur den äußeren Pfad (erste Subpath bis zum ersten `Z`) verwenden, sonst entstehen transparente Löcher
- **Sprite-Sheets**: Über `ctx.drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh)` animierbar

### Perspektive (Tiefeneffekt)
```typescript
// Y-Position bestimmt Größe: vorne groß, Horizont klein
const scale = 1.0 - (objectY / maxY) * 0.45
// Rendering: back-to-front (Painter's Algorithm)
objects.sort((a, b) => b.y - a.y).forEach(obj => obj.render(ctx))
```

---

## 9. Referenz-Implementierungen

| Datei | Typ | Beschreibung |
|---|---|---|
| `ForestMiniGame.vue` | DOM/CSS | Wald-Spiel mit CSS-Bäumen, Fabriken, Vogel-Sprite |
| `ForestMiniGameCanvas.vue` | Canvas+DOM | Canvas-Version mit SVG-Icons, ClimateBackground |
| `IcebergAnimation.vue` | Canvas+DOM | Eisberg-Zeichnung, Schiff, ClimateBackground |
| `EdutainmentProgressAnimation.vue` | DOM/CSS | Pixel-Animation mit Bubbles |
