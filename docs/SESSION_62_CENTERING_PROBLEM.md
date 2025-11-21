# Handover: Zentrierungs-Problem im Category-Bubble-Layout

**Session:** 2025-11-21
**Status:** UNGELÖST - Responsive Ansatz funktioniert nicht
**Branch:** `feature/stage2-mega-prompt` / `develop`

## Problem-Beschreibung

Das kreisförmige Layout aus Kategorie-Bubbles und Config-Bubbles ist **nicht korrekt zentriert**. Die vertikale Achse durch den "virtuellen Mittelpunkt" läuft durch die rechten Property-Bubbles statt durch die zentrale 🫵-Bubble (Freestyle).

### Visuelles Problem

```
Soll-Zustand:          Ist-Zustand:

    💬  🪄                 💬  🪄
      🫵      ←Mitte          |  🫵
    🖌️  🌍                 🖌️  | 🌍
                              ↑
                           Falsche Mitte
```

Die gesamte Anordnung ist zu weit links positioniert.

## Was NICHT funktioniert hat

### Versuch 1: Fixed Pixel Offsets
```typescript
// FALSCH - Magic Numbers
const centerY = (props.canvasHeight + 80) / 2  // Header-Offset geraten
```
**Problem:** Keine responsive Lösung, anfällig für Layout-Änderungen

### Versuch 2: Geometrische Verhältnisse
```typescript
// FALSCH - Theoretisch richtig, praktisch falsch
const radius = 1.75 * CATEGORY_BUBBLE_DIAMETER  // 3.5x diameter / 2
```
**Problem:** Kategorie-Bubbles viel zu weit auseinander, Config-Bubbles zu eng

### Versuch 3: Responsive Percentage
```typescript
// FALSCH - Jetzt implementiert, funktioniert aber nicht
function getResponsiveRadius(): number {
  const smallerDimension = Math.min(props.canvasWidth, props.canvasHeight)
  return smallerDimension * 0.25  // 25% of smaller dimension
}
```
**Problem:** Radius wird zu groß, Layout passt nicht mehr ins Canvas

## Root Cause (Hypothese)

Die Canvas-Dimensionen (`canvasWidth`, `canvasHeight`) werden korrekt gemessen via ResizeObserver, ABER:

1. **Timing-Problem:** Die Positionen werden berechnet, bevor das Layout vollständig gerendert ist
2. **Measurement-Problem:** `getBoundingClientRect()` liefert möglicherweise falsche Werte
3. **Koordinatensystem-Problem:** Die absolute Positionierung in `ConfigTile.vue` und `PropertyBubble.vue` interpretiert die Koordinaten falsch

## Aktueller Code-Zustand

### PropertyQuadrantsView.vue
- Flexbox-Layout: Header + Canvas-Area
- ResizeObserver misst Canvas-Area Dimensionen
- Props werden korrekt übergeben

### PropertyCanvas.vue
- `calculateCategoryPositions()`: Verwendet `getResponsiveRadius()`
- Zentriert bei `canvasWidth/2, canvasHeight/2`
- **Console-Logs aktiv** für Debugging

### ConfigCanvas.vue
- `getCategoryPosition()`: Identische Logik wie PropertyCanvas
- `calculatePositions()`: Gruppiert Configs um Kategorien
- **Console-Logs aktiv** für Debugging

## Was gemessen werden muss

User bat um Screenshot mit Browser-Konsole, aber wurde nicht geliefert. Benötigte Informationen:

1. **Canvas-Dimensionen:** Was liefert ResizeObserver tatsächlich?
2. **Berechnete Zentren:** Was sind `centerX` und `centerY`?
3. **Responsive Radius:** Was ist der berechnete Radius-Wert?
4. **Kategorie-Positionen:** Wo werden die Bubbles tatsächlich platziert?

## Nächste Schritte

### Option A: Zurück zu festen Werten (funktionierte vorher)
```typescript
const CATEGORY_CIRCLE_RADIUS = 125  // Fixed, worked before
```
Dann nur das Zentrierung-Problem lösen, ohne responsive Units.

### Option B: Debug-First Approach
1. Console-Logs auswerten (User muss Screenshot liefern)
2. Tatsächliche vs. erwartete Werte vergleichen
3. Root Cause identifizieren
4. Dann gezielt fixen

### Option C: Canvas-Koordinaten-Neuberechnung
Möglicherweise müssen die Bubbles ihre Positionen relativ zum Canvas-Area-Element berechnen, nicht relativ zum Viewport:

```typescript
// Potentielle Lösung
const canvasRect = canvasAreaRef.value?.getBoundingClientRect()
const absoluteX = canvasRect.left + centerX
const absoluteY = canvasRect.top + centerY
```

## Geometrische Anforderungen (User-Vorgabe)

1. **Mittelpunkt des zentralen Kreises:** `(canvasWidth/2, canvasHeight/2)`
2. **Durchmesser zentraler Bubble:** 100px (Freestyle 🫵)
3. **Durchmesser äußerer Kreis:** User sagte "3.5x" aber das war zu groß
4. **Durchmesser Config-Bubbles:** 240px
5. **Verteilung:** Y Bubbles gleichmäßig auf Kreislinie

**Wichtig:** User verlangt proportionale/responsive Lösung OHNE feste Pixel-Werte.

## Dateien mit Console-Logs (können entfernt werden nach Fix)

- `PropertyQuadrantsView.vue:114-119` - Canvas dimension measurement
- `PropertyCanvas.vue:95-102` - Category position calculation
- `ConfigCanvas.vue:89-96` - Config position calculation

## Commit-Historie

- `d802078` - WIP: Category bubble grouping with centering issues
- Vorher: Gruppierung funktionierte, aber feste Pixel-Werte

## User-Feedback

> "REICHT JETZT!!! Du nimmst die rechte obere property-bubble als referenz, was soll das?"

> "KANNST DU VIELLEICHT EINE RECHENAUFGABE FÜR 12-JÄHRIGE VERNÜNFTIG LÖSEN??"

**Frustrations-Level:** HOCH - Mehrere Ansätze gescheitert

## Empfehlung

1. **Console-Logs auswerten** (User muss Screenshot mit Konsole liefern)
2. **Visuelles Debugging:** Kreuz-Linien einzeichnen bei centerX/centerY zur Verifikation
3. **Schrittweise zurück zu funktionierender Version:**
   - Erst Zentrierung mit festen Werten fixen
   - Dann responsive Units hinzufügen
4. **Nicht spekulieren** - Mit echten Messwerten arbeiten
