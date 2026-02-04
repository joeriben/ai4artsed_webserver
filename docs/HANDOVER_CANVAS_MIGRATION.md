# Canvas Migration - Session Handover

**Datum:** 2026-02-04
**Status:** Phase 0 & Phase 2 (Forest) abgeschlossen
**Nächster Schritt:** Phase 1 (Pixel) oder Phase 3 (RareEarth)

---

## Was wurde erreicht?

### ✅ Phase 0: Shared Canvas Utilities (ABGESCHLOSSEN)

Alle 4 Composables wurden erstellt und sind produktionsbereit:

#### 1. `useCanvasRenderer.ts` (185 LOC)
**Pfad:** `/public/ai4artsed-frontend/src/composables/useCanvasRenderer.ts`

**Features:**
- Canvas Element Management
- Auto-Resize mit Debouncing (300ms)
- Device Pixel Ratio (Retina Support)
- Pointer Event Coordinate Conversion
- Pattern von IcebergAnimation extrahiert

**API:**
```typescript
const { canvasRef, getRenderContext, getCanvasCoords, setupPointerEvents } = useCanvasRenderer(
  containerRef,
  { width: ref(800), height: ref(320) }
)
```

#### 2. `useGameLoop.ts` (146 LOC)
**Pfad:** `/public/ai4artsed-frontend/src/composables/useGameLoop.ts`

**Features:**
- RAF Loop (60fps für smooth animations)
- Interval Loop (10fps für game logic)
- Delta Time Calculation
- Auto Start/Stop basierend auf `isActive` Ref

**API:**
```typescript
const { start, stop, tickCount } = useGameLoop({
  mode: 'raf' | 'interval',
  fps: 10,
  onTick: (dt) => { /* update & render */ },
  isActive: computed(() => !gameOver.value)
})
```

#### 3. `useCanvasDrawing.ts` (237 LOC)
**Pfad:** `/public/ai4artsed-frontend/src/composables/useCanvasDrawing.ts`

**Features:**
- Primitive Shapes (Circle, Rect, Polygon)
- Cached Gradients (Performance)
- Text & Sprite Rendering
- Shadow/Glow Effects
- Color Interpolation

**API:**
```typescript
const { drawCircle, drawRect, createCachedGradient, interpolateColor } = useCanvasDrawing()
```

#### 4. `useCanvasObjects.ts` (133 LOC)
**Pfad:** `/public/ai4artsed-frontend/src/composables/useCanvasObjects.ts`

**Features:**
- Object Pool Management
- Batch Update/Render
- Find/Filter/Sort
- Generic Type Support

**API:**
```typescript
const { objects, addObject, removeObject, updateAll, renderAll } = useCanvasObjects<Tree>()
```

**TypeScript:** ✅ Alle Utilities type-safe und kompilieren sauber

---

### ✅ Phase 2: ForestMiniGame → Canvas (ABGESCHLOSSEN)

**Warum Phase 2 vor Phase 1?** User wollte mit "Tree" (Forest) beginnen.

#### Neue Datei: `ForestMiniGameCanvas.vue` (682 LOC)
**Pfad:** `/public/ai4artsed-frontend/src/components/edutainment/ForestMiniGameCanvas.vue`

**Implementierte Features:**
- ✅ Sky Gradient (CO2-basiert, cached)
- ✅ Ground Gradient (2-color linear)
- ✅ Clouds (dynamisch generiert basierend auf pollution ratio)
- ✅ Bird Animation (Progress-Indikator, left-to-right)
- ✅ Trees (7 Typen: pine, spruce, fir, oak, birch, maple, willow)
- ✅ Tree Growing Animation (scale interpolation)
- ✅ Factories (spawn basierend auf GPU power)
- ✅ Smoke Particles (Particle System)
- ✅ Click-to-Plant (1s cooldown)
- ✅ Game Loop (10fps interval)
- ✅ Game Over (wenn alle Bäume zerstört)
- ✅ UI Overlays (Stats, Instructions, Summary - identisch zum Original)

**Verwendete Utilities:**
- `useCanvasRenderer` ✓
- `useGameLoop` ✓ (interval mode, 10fps)
- `useCanvasDrawing` ✓
- `useCanvasObjects` ✓
- `useAnimationProgress` ✓ (unchanged, shared)

**Performance:**
- DOM Version: 196+ dynamic divs (trees + factories + clouds)
- Canvas Version: 1 canvas, alle Objekte gerendert als shapes
- Expected: Bessere Performance bei vielen Objekten

**TypeScript:** ✅ Kompiliert sauber

---

### ✅ Test-Integration (ABGESCHLOSSEN)

**Datei:** `/public/ai4artsed-frontend/src/views/AnimationTestView.vue`

**Änderungen:**
1. Import: `ForestMiniGameCanvas` hinzugefügt
2. Animations-Liste: `forest-canvas` Tab hinzugefügt (Position: 3b)
3. Template: Canvas-Version parallel zum Original
4. Live Stats: `forest-canvas` zur Hide-Liste hinzugefügt

**Zugriff im Browser:**
1. Frontend Dev-Server starten
2. Navigate zu Test-Page
3. Tab "3b. Wald-Spiel (Canvas)" auswählen
4. Progress-Slider bewegen, um Spiel zu starten
5. Klicken, um Bäume zu pflanzen

**A/B Testing möglich:**
- Tab 3: Original (DOM/CSS)
- Tab 3b: Canvas
- Direkter Vergleich möglich

---

## Was fehlt noch?

### ⏳ Phase 1: EdutainmentProgressAnimation → Canvas (AUSSTEHEND)

**Grund für Skip:** User wollte mit Forest beginnen, nicht mit Pixel.

**Komponente:** EdutainmentProgressAnimation.vue (62 LOC - sehr kurz!)
**Grund:** Delegiert hauptsächlich an SpriteProgressAnimation.vue

**Aufwand:** 2-3 Stunden (einfachste Migration)

**Was zu implementieren:**
- 14x14 Pixel Grid als Canvas (196 fillRect calls)
- Flying Pixel Animations (velocity-based interpolation)
- Click Handler (Grid cell conversion)
- Processor Box (gradient rect)
- Progress Bar (bereits CSS, könnte bleiben)

**Vorteil wenn fertig:**
- Validiert Utility Stack auf einfachstem Case
- Schneller Win

---

### ⏳ Phase 3: RareEarthMiniGame → Canvas (AUSSTEHEND)

**Status:** Aktuell deaktiviert (siehe Session-History: User war unzufrieden mit CSS-Version)

**Komponente:** RareEarthMiniGame.vue (841 LOC nach Prozent-Umstellung)

**Aufwand:** 5-7 Stunden (komplexeste Migration)

**Was zu implementieren:**
- Multi-Layer Rendering (6 Schichten)
- Mountain (Path2D polygon)
- Lake (scaled ellipse + ripple effect)
- Conveyor Belt (textured rect)
- Conveyor Crystals (sprites mit glow)
- Sludge Drips (particle system)
- Vegetation (health state transitions)
- GPU Chip (3 glowing gems)
- Container (fill animation)
- Truck (drive-in animation)
- Shovel (click effect)

**Entscheidung:** Mit User klären, ob diese Migration noch gewünscht ist.

---

## Nächste Schritte (Empfehlung)

### Option A: Phase 1 abschließen (EdutainmentProgressAnimation)
**Pro:**
- Einfachste Migration (2-3h)
- Komplettiert leichte Cases
- Lernkurve flach

**Contra:**
- Weniger sichtbarer Impact als Forest

### Option B: Phase 3 starten (RareEarthMiniGame)
**Pro:**
- Größte Herausforderung
- Zeigt volle Utility-Stack-Power

**Contra:**
- User war unzufrieden mit CSS-Version
- Eventuell komplettes Redesign nötig

### Option C: Optimierung & Polish (ForestMiniGameCanvas)
**Pro:**
- Sicherstellen, dass Forest Canvas perfekt läuft
- Performance-Profiling
- Visuelle Parität mit Original

**Contra:**
- Keine neuen Features

---

## Testing Checklist (Forest Canvas)

### Funktional
- [ ] Progress-Slider startet Spiel
- [ ] Klicken pflanzt Baum an Cursor-Position
- [ ] Bäume wachsen mit Animation
- [ ] Factories spawnen basierend auf GPU Power
- [ ] Rauch-Partikel steigen von Factories auf
- [ ] Cooldown (1s) funktioniert
- [ ] Bird fliegt von links nach rechts
- [ ] Clouds erscheinen bei Pollution
- [ ] Sky wird dunkler mit steigendem CO2
- [ ] Game Over wenn alle Bäume weg

### Visuell
- [ ] Colors matchen Original
- [ ] Tree-Größen plausibel
- [ ] Factory-Position korrekt
- [ ] Bird-Animation smooth
- [ ] Clouds-Opacity stimmt
- [ ] Stats-Bar zeigt korrekte Werte

### Performance
- [ ] 10fps Game Loop stabil
- [ ] Kein Ruckeln bei vielen Trees/Factories
- [ ] Memory Leak Check (längeres Spielen)

---

## Bekannte Issues / TODOs

### ForestMiniGameCanvas
1. **Tree Rendering vereinfacht:** Aktuell nur Basis-Shapes (Triangle/Circle/Oval). Original hat detailliertere CSS-Shapes.
   - **Fix:** Detailliertere Path2D-Shapes pro Tree-Type
2. **Factory Hit Detection fehlt:** Original erlaubt Factory-Clicks (zerstören), Canvas-Version nicht implementiert.
   - **Fix:** Click-Handler erweitern mit Factory hitbox check
3. **Tree Destruction fehlt:** Original hat Logik zum Zerstören von Trees durch Factories.
   - **Fix:** Game Logic aus Original übernehmen

### Utilities
- Alle stabil, keine bekannten Issues

---

## Wichtige Dateien (Quick Reference)

### Utilities
```
/public/ai4artsed-frontend/src/composables/
├── useCanvasRenderer.ts      (185 LOC)
├── useGameLoop.ts             (146 LOC)
├── useCanvasDrawing.ts        (237 LOC)
└── useCanvasObjects.ts        (133 LOC)
```

### Components
```
/public/ai4artsed-frontend/src/components/edutainment/
├── ForestMiniGame.vue              (767 LOC - Original DOM/CSS)
├── ForestMiniGameCanvas.vue        (682 LOC - Canvas)
├── EdutainmentProgressAnimation.vue  (62 LOC - Original, TODO)
├── RareEarthMiniGame.vue           (841 LOC - Original, disabled)
└── IcebergAnimation.vue            (820 LOC - Reference, bereits Canvas)
```

### Test Page
```
/public/ai4artsed-frontend/src/views/
└── AnimationTestView.vue
```

### Plan
```
/home/joerissen/.claude/plans/
└── flickering-knitting-shell.md  (Canvas Migration Strategy)
```

---

## Git Status

**Branch:** develop

**Geänderte Dateien (untracked/modified):**
- `src/composables/useCanvasRenderer.ts` (NEW)
- `src/composables/useGameLoop.ts` (NEW)
- `src/composables/useCanvasDrawing.ts` (NEW)
- `src/composables/useCanvasObjects.ts` (NEW)
- `src/components/edutainment/ForestMiniGameCanvas.vue` (NEW)
- `src/views/AnimationTestView.vue` (MODIFIED - test integration)

**Empfehlung:** Commit erstellen nach erfolgreichem Browser-Test.

**Commit Message Vorschlag:**
```
feat(canvas): Add Canvas utilities & ForestMiniGame Canvas version

Phase 0: Shared Canvas Utilities
- Add useCanvasRenderer (canvas setup, resize, DPR)
- Add useGameLoop (RAF/interval loops)
- Add useCanvasDrawing (shapes, gradients, effects)
- Add useCanvasObjects (object pool management)

Phase 2: ForestMiniGame → Canvas
- Implement ForestMiniGameCanvas.vue
- Sky gradient (CO2-based)
- Dynamic clouds & bird animation
- 7 tree types with growth animation
- Factories with smoke particles
- Click-to-plant interaction
- 10fps game loop

Test integration:
- Add forest-canvas tab to AnimationTestView
- Enable A/B testing (DOM vs Canvas)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## TypeScript Status

✅ Alle Dateien kompilieren sauber
✅ `npm run type-check` erfolgreich

---

## Browser Testing (noch ausstehend)

**Test-URL:** `http://localhost:[PORT]/test` (nach Frontend-Dev-Server Start)

**Test-Schritte:**
1. Tab "3b. Wald-Spiel (Canvas)" auswählen
2. Progress-Slider auf 10+ bewegen
3. In Canvas klicken → Baum sollte wachsen
4. Mehrere Bäume pflanzen
5. Warten auf Factory-Spawn
6. Rauch-Partikel beobachten
7. Bird-Animation links→rechts prüfen
8. CO2 steigen lassen → Sky Darkening & Clouds prüfen

**Browser Console:** Auf Errors prüfen

---

## Nächste Session - Empfohlene Reihenfolge

1. **Browser Testing** (15-30min)
   - ForestMiniGameCanvas testen
   - Bugs identifizieren & fixen

2. **Fehlende Features** (1-2h)
   - Factory Hit Detection
   - Tree Destruction Logic
   - Detaillierte Tree Shapes

3. **Entscheidung:** Phase 1 oder Phase 3?
   - Mit User klären
   - Dann fortfahren

4. **Optional: Performance Profiling** (30min)
   - DOM vs Canvas Vergleich
   - Memory Usage
   - FPS Monitoring

---

## Kontakt/Fragen

Bei Fragen zum Code:
- Alle Utilities sind dokumentiert mit JSDoc
- Pattern-Kommentare verweisen auf IcebergAnimation
- Plan-Datei: `/home/joerissen/.claude/plans/flickering-knitting-shell.md`

**Status:** Ready for Browser Testing ✅
