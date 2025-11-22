# Session 64 - Youth Flow Redesign: Korrekte Anforderungen

**Datum**: 2025-11-22
**Status**: 🔴 PLANUNG - Nicht implementiert
**Kontext**: Session 63 hatte falsche Implementierung - dies ist die korrekte Spezifikation

---

## ⚠️ WARNUNG: Was in Session 63/64 FALSCH gemacht wurde

### Fehler 1: Falsche Labels
- ❌ "Details" für Context-Bubble → zu unspezifisch
- ❌ "Welcher Stil?" für Medium-Auswahl → Stile ≠ Output-Medien
- ❌ Stern-Emoji 🌟 für "gpt_image_1" → macht keinen Sinn als Medium

### Fehler 2: Falsche Layout-Struktur
- ❌ Context + Medium nebeneinander (horizontal) → sollte vertikal untereinander sein
- ❌ Nur 3 Medium-Bubbles direkt gezeigt → sollte Kategorie → Configs verschachtelt sein
- ❌ Keine Modal-Editierung für Context/Interception
- ❌ Keine Phase-Umschaltung von vertikal → horizontal

### Fehler 3: Fehlende Verschachtelung
- ❌ Output-Configs direkt angezeigt → sollte erst nach Kategorie-Auswahl erscheinen
- ❌ Keine Kategorie-Ebene (Bild/Sound/Video)

---

## ✅ KORREKTE ANFORDERUNGEN

### Phase 2a - Initial Flow (VERTIKAL)

```
┌─────────────────────────────────────┐
│  INPUT BUBBLE    CONTEXT BUBBLE     │  ← Nebeneinander (wie aktuell bei Kids)
│  (editierbar)    (Preview + Modal)  │
│                  [Edit-Button]      │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│  🖼️ Bild   🔊 Sound   🎬 Video     │  ← Kategorien NEBENEINANDER
│     ▼                               │     (horizontal row)
└─────────────────────────────────────┘
                  ↓ User klickt "Bild"
┌─────────────────────────────────────┐
│  🎨 SD3.5  🌟 GPT Image  🎭 Flux   │  ← Configs NEBENEINANDER
└─────────────────────────────────────┘     (horizontal row UNTERHALB)
                  ↓ User wählt Config
         ┌──────────────────┐
         │  INTERCEPTION    │  ← Füllt sich nach Config-Wahl
         │  RESULT          │     Preview + Modal Edit
         │  (Preview)       │
         │  [Edit-Button]   │
         └──────────────────┘
                  ↓
              [START]
```

### Phase 2b - Nach START (HORIZONTAL)

```
INPUT → INTERCEPT → SAFETY → PRE-OUTPUT → GENERATION → IMAGE
  ●        ●          ○          ○            ○
         (Progressive Filling von links → rechts)
```

---

## 🎯 Detaillierte Anforderungen

### 1. INPUT + CONTEXT (Nebeneinander)

**INPUT Bubble**:
- Editierbares Textarea
- Label: "INPUT" oder sinnvoller deutscher Text
- Placeholder: "Worüber soll dein Bild sein?"

**CONTEXT Bubble**:
- **PREVIEW-Modus**: Zeigt Kurzfassung des Context (z.B. "The scene...")
- **NICHT** direkt editierbar wie Textarea
- **[Edit] Button**: Klick öffnet Modal für Bearbeitung
- Modal zeigt vollen Context mit Textarea
- Ähnlich wie Legacy Server "Context Bubble (Preview)"

### 2. KATEGORIE-BUBBLES (Horizontal nebeneinander)

**Struktur**:
```vue
<div class="category-bubbles">
  <div class="bubble" @click="selectCategory('image')">
    🖼️ Bild
  </div>
  <div class="bubble" @click="selectCategory('sound')">
    🔊 Sound
  </div>
  <div class="bubble" @click="selectCategory('video')">
    🎬 Video
  </div>
</div>
```

**Layout**:
- **Horizontal nebeneinander** in einer Reihe (flexbox row)
- **KEINE** Kreisanordnung wie Phase 1 PropertyQuadrantsView
- **KEINE** Force-based Physics
- **KEINE** vertikale Anordnung untereinander
- Einfaches CSS Flexbox mit `flex-direction: row`

**Verfügbare Kategorien**:
- Bild (image)
- Sound (audio) - falls Output-Configs vorhanden
- Video (video) - falls Output-Configs vorhanden

### 3. OUTPUT-CONFIG-BUBBLES (Horizontal unterhalb der Kategorien)

**Verhalten**:
1. User klickt Kategorie-Bubble (z.B. "Bild")
2. Output-Config-Bubbles erscheinen **direkt unterhalb** der Kategorie-Reihe
3. **Horizontal nebeneinander** (flexbox row mit flex-wrap bei Bedarf)
4. **KEINE** Kreisanordnung wie Phase 1
5. **KEINE** vertikale Anordnung untereinander

**Struktur**:
```vue
<transition name="slide-down">
  <div v-if="selectedCategory === 'image'" class="output-configs">
    <div v-for="config in imageConfigs"
         :key="config.id"
         class="config-bubble"
         :class="{ selected: selectedConfig === config.id }"
         @click="selectConfig(config.id)">
      {{ config.emoji }} {{ config.label }}
    </div>
  </div>
</transition>
```

**Mapping Kategorie → Configs**:
```typescript
const configsByCategory = {
  image: [
    { id: 'sd35_large', label: 'SD 3.5', emoji: '🎨' },
    { id: 'gpt_image_1', label: 'GPT Image', emoji: '🌟' },
    { id: 'acestep_simple', label: 'Flux', emoji: '🎭' },
    // ... weitere Bild-Configs
  ],
  sound: [
    { id: 'acenet', label: 'ACENet', emoji: '🔊' },
    { id: 'stable_audio', label: 'Stable Audio', emoji: '🎵' },
    // ... Sound-Configs (falls vorhanden)
  ],
  video: [
    // ... Video-Configs (falls vorhanden)
  ]
}
```

**Hinweis**: Falls nur Kategorie "Bild" existiert, kann man die anderen Kategorien ausgrauen oder ausblenden.

### 4. INTERCEPTION RESULT (Preview + Modal)

**Verhalten**:
1. Erscheint **nach** Config-Auswahl
2. Backend-Call: `/api/schema/pipeline/stage2` mit `schema: 'overdrive'`
3. Zeigt **Preview** des Interception-Results
4. **[Edit] Button** öffnet Modal zur Bearbeitung

**Struktur**:
```vue
<transition name="slide-down">
  <div v-if="interceptionResult" class="interception-bubble">
    <div class="bubble-header">
      <span class="label">Interception Result</span>
      <button @click="editInterception" class="edit-btn">[Edit]</button>
    </div>
    <div class="preview-text">
      {{ interceptionResult.substring(0, 100) }}...
    </div>
  </div>
</transition>

<!-- Modal für Editierung -->
<Modal v-if="showInterceptionModal" @close="showInterceptionModal = false">
  <textarea v-model="interceptionResult" rows="10"></textarea>
  <button @click="saveInterception">Save</button>
</Modal>
```

### 5. START Button

**Verhalten**:
1. Wird aktiv wenn:
   - INPUT vorhanden
   - Config gewählt
   - Interception Result vorhanden
2. Klick triggert **Phase-Umschaltung**:
   - Von Phase 2a (vertikal) → Phase 2b (horizontal)
   - Startet Pipeline-Execution

**Implementierung**:
```vue
<button
  v-if="canStart"
  @click="startPipeline"
  :disabled="pipelineStarted"
  class="start-button">
  🚀 START
</button>

<script setup>
const canStart = computed(() => {
  return inputText.value &&
         selectedConfig.value &&
         interceptionResult.value
})

async function startPipeline() {
  pipelineStarted.value = true
  showPhase2b.value = true  // Umschaltung zu horizontal view
  // ... Pipeline execution
}
</script>
```

### 6. Phase 2b - Horizontal Pipeline View

**Struktur**:
```
INPUT → INTERCEPT → SAFETY → PRE-OUTPUT → GENERATION
  ●        ●          ○          ○            ○
```

**Verhalten**:
- Progressive Filling von links nach rechts
- Jede Stage zeigt:
  - Status: waiting / processing / completed
  - Emoji-Icon
  - Label
  - Hex-Color (wie im Diagram)
  - Optional: Kurzfassung des Outputs

**Implementierung**:
```vue
<div v-if="showPhase2b" class="horizontal-pipeline">
  <div
    v-for="stage in pipelineStages"
    :key="stage.name"
    class="pipeline-stage"
    :class="stage.status">
    <div class="stage-icon">{{ stage.emoji }}</div>
    <div class="stage-label">{{ stage.label }}</div>
    <div class="stage-status">
      <span v-if="stage.status === 'processing'">⏳</span>
      <span v-if="stage.status === 'completed'">✓</span>
    </div>
    <div v-if="stage.output" class="stage-output">
      {{ stage.output }}
    </div>
  </div>
</div>
```

---

## 🔧 Technische Implementierung

### Vue Component Struktur

```vue
<template>
  <div class="youth-flow-view">
    <!-- Phase 2a: Vertical Flow -->
    <div v-if="!showPhase2b" class="phase-2a">
      <!-- 1. INPUT + CONTEXT -->
      <div class="input-context-row">
        <InputBubble v-model="inputText" />
        <ContextBubble v-model="contextPrompt" :preview-mode="true" />
      </div>

      <!-- 2. CATEGORY BUBBLES -->
      <div class="category-bubbles">
        <CategoryBubble
          v-for="cat in categories"
          :key="cat.id"
          :category="cat"
          :selected="selectedCategory === cat.id"
          @click="selectCategory(cat.id)" />
      </div>

      <!-- 3. OUTPUT-CONFIG BUBBLES (unterhalb) -->
      <transition name="slide-down">
        <div v-if="selectedCategory" class="output-configs">
          <ConfigBubble
            v-for="config in configsForCategory(selectedCategory)"
            :key="config.id"
            :config="config"
            :selected="selectedConfig === config.id"
            @click="selectConfig(config.id)" />
        </div>
      </transition>

      <!-- 4. INTERCEPTION RESULT -->
      <transition name="slide-down">
        <InterceptionBubble
          v-if="interceptionResult"
          v-model="interceptionResult"
          :preview-mode="true" />
      </transition>

      <!-- 5. START BUTTON -->
      <button v-if="canStart" @click="startPipeline">
        🚀 START
      </button>
    </div>

    <!-- Phase 2b: Horizontal Pipeline -->
    <HorizontalPipeline
      v-if="showPhase2b"
      :stages="pipelineStages" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// State
const inputText = ref('')
const contextPrompt = ref('')
const selectedCategory = ref<string | null>(null)
const selectedConfig = ref<string | null>(null)
const interceptionResult = ref('')
const showPhase2b = ref(false)

// Categories
const categories = [
  { id: 'image', label: 'Bild', emoji: '🖼️' },
  { id: 'sound', label: 'Sound', emoji: '🔊' },
  { id: 'video', label: 'Video', emoji: '🎬' }
]

// Config mapping
const configsByCategory = {
  image: [
    { id: 'sd35_large', label: 'SD 3.5', emoji: '🎨' },
    { id: 'gpt_image_1', label: 'GPT Image', emoji: '🌟' },
    { id: 'acestep_simple', label: 'Flux', emoji: '🎭' }
  ],
  sound: [],  // Falls Sound-Configs vorhanden
  video: []   // Falls Video-Configs vorhanden
}

function configsForCategory(categoryId: string) {
  return configsByCategory[categoryId] || []
}

const canStart = computed(() => {
  return inputText.value && selectedConfig.value && interceptionResult.value
})

async function selectConfig(configId: string) {
  selectedConfig.value = configId
  // Trigger Interception
  await runInterception()
}

async function runInterception() {
  // Call /api/schema/pipeline/stage2
  const response = await axios.post('/api/schema/pipeline/stage2', {
    schema: 'overdrive',
    input_text: inputText.value,
    context_prompt: contextPrompt.value,
    user_language: 'de',
    execution_mode: 'eco',
    safety_level: 'youth',
    output_config: selectedConfig.value
  })

  interceptionResult.value = response.data.interception_result?.result || ''
}

async function startPipeline() {
  showPhase2b.value = true
  // Start pipeline execution
  // ...
}
</script>
```

---

## 🎨 Layout-Spezifikation

### Phase 2a Container
```css
.phase-2a {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}
```

### Input + Context Row
```css
.input-context-row {
  display: flex;
  gap: 2rem;
  width: 100%;
  justify-content: center;
}

.input-context-row > * {
  flex: 1;
  max-width: 400px;
}
```

### Category Bubbles (Horizontal nebeneinander)
```css
.category-bubbles {
  display: flex;
  flex-direction: row;  /* ← HORIZONTAL, nicht column! */
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.category-bubble {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-bubble:hover {
  transform: scale(1.1);
}

.category-bubble.selected {
  border: 3px solid #4CAF50;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.5);
}
```

### Output-Config Bubbles (Horizontal unterhalb, nebeneinander)
```css
.output-configs {
  display: flex;
  flex-direction: row;  /* ← HORIZONTAL, nicht column! */
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;  /* Falls mehr als passen in eine Reihe */
  margin-top: 1rem;
}

.config-bubble {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  /* ... ähnlich wie category-bubble */
}
```

---

## 📋 API Integration

### Interception Endpoint
```typescript
POST /api/schema/pipeline/stage2
{
  "schema": "overdrive",
  "input_text": "Ein Haus in der Landschaft",
  "context_prompt": "mit Bergen im Hintergrund",  // optional
  "user_language": "de",
  "execution_mode": "eco",
  "safety_level": "youth",
  "output_config": "sd35_large"
}

Response:
{
  "success": true,
  "interception_result": {
    "result": "A house stands in a landscape, surrounded by..."
  }
}
```

### Pipeline Execution Endpoint
```typescript
POST /api/schema/pipeline/execute
{
  "schema": "overdrive",
  "input_text": "Ein Haus",
  "interception_result": "A house stands in a landscape...",
  "context_prompt": "mit Bergen",
  "user_language": "de",
  "execution_mode": "eco",
  "safety_level": "youth",
  "output_config": "sd35_large"
}

Response:
{
  "status": "success",
  "run_id": "abc123",
  "outputs": ["/media/runs/abc123/output_0.png"]
}
```

---

## ✅ Checkliste für nächste Session

### Vor Implementierung:
- [ ] Diese Handover komplett gelesen
- [ ] ASCII-Diagram verstanden (Phase 2a vertikal, Phase 2b horizontal)
- [ ] Unterschied zu Phase 1 verstanden (linear vs. kreisförmig)
- [ ] Modal-Editierung für Context + Interception verstanden

### Implementierung:
- [ ] INPUT + CONTEXT nebeneinander (Preview-Modus für Context)
- [ ] Category-Bubbles linear angeordnet (NICHT kreisförmig)
- [ ] Output-Config-Bubbles erscheinen unterhalb (linear, NICHT kreisförmig)
- [ ] Interception Result als Preview mit Modal-Edit
- [ ] START Button mit Phase-Umschaltung
- [ ] Phase 2b: Horizontal Pipeline View

### Testing:
- [ ] Layout passt auf iPad 1024×768
- [ ] Category → Config Navigation funktioniert
- [ ] Interception API Call funktioniert
- [ ] Modal-Editierung funktioniert
- [ ] Phase-Umschaltung funktioniert
- [ ] Pipeline Execution funktioniert

---

## 🚨 WICHTIG: Was NICHT tun

1. **KEINE** Kreisanordnung / Force-based Physics wie Phase 1
2. **KEINE** direkten Textareas für Context/Interception → Preview + Modal!
3. **KEINE** flache Config-Liste → Kategorie → Config verschachtelt!
4. **KEINE** erfundenen Labels wie "Details", "Welcher Stil?" → korrekte Beschriftung!
5. **KEINE** Implementierung ohne diese Handover gelesen zu haben!

---

**Ende Handover Session 64**
