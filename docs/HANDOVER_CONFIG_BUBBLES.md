# HANDOVER: Config-Bubble Text-Badge Problem

**Status**: UNGELÖST
**Datum**: 2026-02-11
**Kontext**: Session mit Claude Opus 4.6, der sich als unfähig erwiesen hat, ein triviales CSS-Problem zu lösen.

## Das Problem

Config-Bubbles (kreisförmige Vorschaubilder mit Textbeschriftung) haben zwei Probleme:

1. **Kreisform**: Bubbles waren Ovale statt Kreise (GELÖST)
2. **Textbeschriftung**: Namen werden abgeschnitten — "Jugendsla", "Analogfotog", "Daguerreoty", "Im Geg..." (UNGELÖST)

## Betroffene Komponenten

**4 Komponenten mit identischem Code** (gehört konsolidiert in EINE shared Komponente):

- `src/components/PropertyCanvas.vue` — PropertyQuadrantsView (Hauptauswahl)
- `src/components/InterceptionPresetOverlay.vue` — Pipeline-Views (text_transformation, image_transformation, multi_image_transformation)
- `src/components/ConfigTile.vue` — ConfigCanvas
- `src/components/MediumSelectionBubbles.vue` — Medium-Auswahl

## Gescheiterte Versuche (chronologisch)

### 1. `aspect-ratio: 1/1` (Kreisform)
**Idee**: CSS aspect-ratio erzwingt Quadrat.
**Gescheitert weil**: SVG-Icons mit festen Pixel-Minima (`clamp(32px, ...)`) und `flex-shrink: 0` überschrieben aspect-ratio via min-content. Agent hat die Root Cause (Content-Overflow) nicht erkannt und stattdessen immer aggressivere CSS-Workarounds gestapelt.

### 2. `padding-bottom: 18%` Trick (Kreisform)
**Idee**: padding-bottom in % ist per CSS-Spec immer relativ zur Parent-Breite.
**Gescheitert weil**: Noch ein Workaround statt die Ursache (SVG-Overflow) zu fixen.

### 3. CSS Custom Property `--s` (Kreisform)
**Idee**: `calc(var(--s) * 0.18)` für width UND height.
**Gescheitert weil**: Funktionierte für PropertyCanvas (gleiche Komponente), aber PropertyBubble (Child-Komponente) erbte `--s` angeblich nicht — tatsächlich lag es weiterhin am SVG-Overflow.

### 4. Inline Styles (Kreisform) — AKTUELLER STAND
**Idee**: `width` und `height` direkt als inline style im JS-computed.
**Status**: Funktioniert für PropertyBubble, ist aber ein Workaround. Die saubere Lösung wäre `aspect-ratio: 1/1` + `overflow: hidden` + relative SVG-Größen gewesen (3 Zeilen CSS).

### 5. Gradient-Overlay statt schwarzer Bande (Text)
**Idee**: Gradient statt Background auf Text-Badge, damit keine Kanten sichtbar.
**Gescheitert weil**: Text unlesbar ohne Hintergrund. Und `text-overflow: ellipsis` funktioniert nur wenn der TEXT seinen eigenen Container überläuft — nicht wenn ein Großeltern-Element (der Kreis) clippt.

### 6. `white-space: nowrap` + `text-overflow: ellipsis` (Text)
**Idee**: Einzeilig mit "..." bei Überlänge.
**Gescheitert weil**: "Im Geg..." — der Name wird unkenntlich. Und bei `left: 0; right: 0` greift ellipsis nicht, weil der Badge so breit ist wie der Parent. Der Kreis-Clip ist das, was den Text beschneidet, nicht der Badge.

### 7. Schwarze Bande `bottom: 0; left: 0; right: 0` + 2-Zeilen-Clamp (Text)
**Idee**: Bande auf volle Breite, Kreis-Clip rundet die Ecken.
**Status**: AKTUELL. Schwarze Bande ist da, Ecken werden vom Kreis geclipt. ABER: am unteren Kreisrand ist die verfügbare Breite geometrisch begrenzt. Lange Namen ("Jugendslang", "Daguerreotypie", "Analogfotografie") werden am Kreisrand abgeschnitten.

## Das fundamentale Problem

Ein Kreis wird nach unten immer schmaler. Die verfügbare Textbreite am Kreisrand bei einer bestimmten Höhe `y` (gemessen vom Boden, normiert auf Durchmesser 1) ist:

```
Breite(y) = 2 * sqrt(y * (1 - y))
```

| Position vom Boden | Verfügbare Breite |
|--------------------|-------------------|
| 5%                 | 43%               |
| 10%                | 60%               |
| 15%                | 71%               |
| 20%                | 80%               |
| 25%                | 87%               |
| 30%                | 92%               |

Eine Text-Bande, die bei `bottom: 0` beginnt und ~25% hoch ist, hat am oberen Rand 87% Breite, am unteren Rand ~0%. Text in der Mitte der Bande hat ~60-70% des Durchmessers zur Verfügung. Bei einem 100px-Bubble sind das 60-70px — "Jugendslang" bei 14px Font braucht ~100px.

**Kein CSS-Trick kann dieses geometrische Problem lösen.** Der Text muss entweder kleiner sein, die Bubbles größer, oder der Text muss AUSSERHALB des Kreises platziert werden.

## Lösungsvorschläge (nicht implementiert)

### A. Text unterhalb des Kreises (EMPFOHLEN)
```
  ___________
 /           \
|    BILD     |
 \___________/
  Jugendslang
```
Text als separates Element unter dem Kreis, nicht im Kreis. Volle Breite, kein Clipping, kein Geometrie-Problem. Standard-Pattern bei Spotify, iOS, macOS.

### B. Tooltip bei Hover
Kurzer Name im Badge (2-Zeilen-Clamp), voller Name als Tooltip.

### C. Größere Bubbles
Mehr Platz = mehr Text. Braucht Layout-Anpassung.

### D. Kürzere Config-Namen
In den JSON-Configs kürzere Display-Namen definieren, z.B. "Jugendslang" statt "Jugendschutz-Slang".

## Noch zu tun

1. **Text-Badge-Lösung wählen** (A-D oben) und implementieren
2. **4 Komponenten konsolidieren** in eine shared `ConfigBubble.vue`
3. **PropertyBubble inline styles** zurück auf sauberes CSS refactoren (`aspect-ratio: 1/1` + `overflow: hidden` + relative SVG-Größen)
4. **Kreisform in InterceptionPresetOverlay** verifizieren (hat noch `aspect-ratio` ohne `min-height: 0` / `overflow: hidden` auf `.config-bubble`)
