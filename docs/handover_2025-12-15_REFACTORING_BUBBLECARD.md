# BubbleCard Refactoring Handover

**Status:** Ready to implement
**Context:** 62% used, new session recommended
**Commit:** 9d54fec (all changes saved)

## Was bereits gemacht wurde

1. ✅ **Flux2 IMG2IMG vollständig funktionsfähig**
   - Config erstellt: `/devserver/schemas/configs/output/flux2_img2img.json`
   - Chunk gefixt: `/devserver/schemas/chunks/output_image_flux2_img2img.json`
   - Verwendet Standard-ComfyUI-Nodes (CheckpointLoaderSimple, KSampler)

2. ✅ **Resolutionen optimiert**
   - Upload-Limit: 1024px → 2048px (media_routes.py Zeile 90, 177)
   - QWEN IMG2IMG: 1.7 MP (~1300x1300)
   - Flux2 IMG2IMG: 2.5 MP (~1600x1600)

3. ✅ **Mask-Code deprecated** (Frontend + Backend)
   - SimpleMaskEditor.vue - Header-Notice
   - ImageUploadWidget.vue - Alle mask-Features auskommentiert
   - media_routes.py - mask-Processing deprecated

4. ✅ **UI-Texte aktualisiert**
   - "Dein kreatives Bild" → "Dein Bild"
   - Context: "Sage was Du an dem Bild verändern möchtest"

5. ✅ **BubbleCard.vue Komponente erstellt**
   - Location: `/public/ai4artsed-frontend/src/components/BubbleCard.vue`
   - Wiederverwendbare Bubble-Komponente mit icon, label, actions, slot

---

## Was noch zu tun ist: BubbleCard Refactoring

### Ziel
Alle Bubble-Strukturen in `text_transformation.vue` und `image_transformation.vue` durch die neue `BubbleCard`-Komponente ersetzen, um Code-Duplikation zu vermeiden.

### Dateien zu ändern

1. **text_transformation.vue** (ca. 40 Zeilen Code-Reduktion)
2. **image_transformation.vue** (ca. 30 Zeilen Code-Reduktion)

---

## Schritt-für-Schritt Anleitung

### 1. text_transformation.vue refactoren

**Aktuelle Struktur (Zeilen 10-26):**
```vue
<div class="input-bubble bubble-card" :class="{ filled: inputText }">
  <div class="bubble-header">
    <span class="bubble-icon">💡</span>
    <span class="bubble-label">Deine Idee: Worum soll es gehen?</span>
    <div class="bubble-actions">
      <button @click="copyInputText" class="action-btn" title="Kopieren">📋</button>
      <button @click="pasteInputText" class="action-btn" title="Einfügen">📄</button>
      <button @click="clearInputText" class="action-btn" title="Löschen">🗑️</button>
    </div>
  </div>
  <textarea v-model="inputText" ...></textarea>
</div>
```

**Neue Struktur mit BubbleCard:**
```vue
<BubbleCard
  icon="💡"
  label="Deine Idee: Worum soll es gehen?"
  :filled="!!inputText"
  :actions="inputTextActions"
>
  <textarea
    v-model="inputText"
    placeholder="Ein Fest in meiner Straße: ..."
    class="bubble-textarea"
    rows="6"
  ></textarea>
</BubbleCard>
```

**Actions definieren (im <script setup>):**
```typescript
import BubbleCard from '@/components/BubbleCard.vue'

const inputTextActions = [
  { icon: '📋', title: 'Kopieren', handler: copyInputText },
  { icon: '📄', title: 'Einfügen', handler: pasteInputText },
  { icon: '🗑️', title: 'Löschen', handler: clearInputText }
]
```

**Gleiches Muster für Context Bubble (Zeilen 29-46):**
```vue
<BubbleCard
  icon="📋"
  label="Bestimme Regeln, Material, Besonderheiten"
  :filled="!!contextPrompt"
  :required="!contextPrompt"
  :actions="contextPromptActions"
>
  <textarea v-model="contextPrompt" ...></textarea>
</BubbleCard>
```

```typescript
const contextPromptActions = [
  { icon: '📋', title: 'Kopieren', handler: copyContextPrompt },
  { icon: '📄', title: 'Einfügen', handler: pasteContextPrompt },
  { icon: '🗑️', title: 'Löschen', handler: clearContextPrompt }
]
```

---

### 2. image_transformation.vue refactoren

**Image Bubble (Zeilen 9-22):**
```vue
<BubbleCard
  icon="💡"
  label="Dein Bild"
  :filled="!!uploadedImage"
  :actions="imageActions"
>
  <ImageUploadWidget
    :initial-image="uploadedImage"
    @image-uploaded="handleImageUpload"
    @image-removed="handleImageRemove"
  />
</BubbleCard>
```

```typescript
import BubbleCard from '@/components/BubbleCard.vue'

const imageActions = [
  { icon: '🗑️', title: 'Löschen', handler: clearImage }
]
```

**Context Bubble (Zeilen 25-40):**
```vue
<BubbleCard
  icon="📋"
  label="Sage was Du an dem Bild verändern möchtest"
  :filled="!!contextPrompt"
  :required="!contextPrompt"
  :actions="contextPromptActions"
>
  <textarea
    v-model="contextPrompt"
    @input="handleContextPromptEdit"
    placeholder="Verwandle es in ein Ölgemälde... Mache es bunter... Füge einen Sonnenuntergang hinzu..."
    class="bubble-textarea"
    rows="6"
  ></textarea>
</BubbleCard>
```

```typescript
const contextPromptActions = [
  { icon: '📋', title: 'Kopieren', handler: copyContextPrompt },
  { icon: '📄', title: 'Einfügen', handler: pasteContextPrompt },
  { icon: '🗑️', title: 'Löschen', handler: clearContextPrompt }
]
```

---

### 3. CSS cleanup (NACH dem Refactoring)

**Entfernen aus beiden Views:**
- `.bubble-card` Styles (jetzt in BubbleCard.vue)
- `.bubble-header` Styles
- `.bubble-icon` Styles
- `.bubble-label` Styles
- `.bubble-actions` Styles
- `.action-btn` Styles

**Behalten:**
- `.bubble-textarea` Styles (spezifisch für Textarea-Content)
- View-spezifische Styles wie `.input-context-section`, `.config-bubble`, etc.

---

## Testing Checklist

### Text Transformation View
- [ ] Input Bubble zeigt Icon, Label, Actions korrekt
- [ ] Copy/Paste/Clear Buttons funktionieren
- [ ] Filled State (blauer Border) bei Text-Eingabe
- [ ] Context Bubble zeigt Required State (roter Border) wenn leer
- [ ] Alle Animationen funktionieren (pulse, hover)

### Image Transformation View
- [ ] Image Bubble zeigt Icon, Label, Clear Button
- [ ] Image Upload funktioniert
- [ ] Clear Button entfernt Bild korrekt
- [ ] Filled State bei hochgeladenem Bild
- [ ] Context Bubble Required State funktioniert

### Beide Views
- [ ] Responsive Design funktioniert (mobile, tablet, desktop)
- [ ] Keine visuellen Regression (Screenshots vergleichen)
- [ ] Console Errors prüfen (F12)
- [ ] Accessibility: Keyboard Navigation, Screen Reader

---

## Rollback bei Problemen

```bash
git revert 9d54fec
# Oder nur BubbleCard.vue löschen:
rm public/ai4artsed-frontend/src/components/BubbleCard.vue
git checkout -- public/ai4artsed-frontend/src/views/*.vue
```

---

## Weitere Optimierungen (Optional, später)

1. **Interception Bubble** auch mit BubbleCard
2. **Config Selection Bubbles** (die Modell-Auswahl-Kreise) - separate Komponente?
3. **i18n** für Labels und Tooltips
4. **Dark/Light Theme Support** in BubbleCard
5. **Animation Presets** als Props (z.B. `animation="pulse"`)

---

## Notizen

- **BubbleCard ist generic** - funktioniert für Text, Image, oder beliebigen Content via Slot
- **Actions sind optional** - wenn keine Actions übergeben werden, wird der Actions-Bereich ausgeblendet
- **CSS ist scoped** - keine Konflikte mit existing Styles
- **TypeScript typed** - Props und Actions haben klare Interfaces

---

## Kontakt bei Fragen

- Code Location: `/home/joerissen/ai/ai4artsed_development`
- Component: `/public/ai4artsed-frontend/src/components/BubbleCard.vue`
- Last Commit: `9d54fec` (2025-12-15)
- Session Context: 62% (neuer Agent/Session empfohlen für Refactoring)

**Estimated Refactoring Time:** 30-45 Minuten
**Risk Level:** Low (alle Changes committet, easy rollback)
**Priority:** Medium (funktioniert auch ohne, aber sauberer Code)
