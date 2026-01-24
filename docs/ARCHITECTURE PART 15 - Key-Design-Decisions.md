# DevServer Architecture

**Part 15: Key Design Decisions**

---


### 1. Input-Type-Based Pipelines ✅

**Decision:** Pipelines categorized by INPUT structure, not output medium or backend

**Rationale:**
- Same input structure = same pipeline logic
- Output medium determined by config, not pipeline
- Backend determined by config, not pipeline
- Scalable (easy to add new media types without new pipelines)

**Example:**
- `single_text_media_generation` can output Image (SD3.5), Audio (Stable Audio), or Music
- Pipeline doesn't care about output type

---

### 2. Chunk Consolidation ✅

**Decision:** One universal `manipulate` chunk instead of multiple redundant chunks

**Removed:**
- translate.json (redundant with manipulate + translation context)
- prompt_interception.json (redundant with manipulate + different placeholder names)
- prompt_interception_lyrics.json (broken, invalid structure)
- prompt_interception_tags.json (broken, invalid structure)

**Rationale:**
- Content belongs in configs, not chunk names
- Reduces duplication (instruction appeared twice in rendered prompts)
- Cleaner architecture (3 chunks instead of 7)

---

### 3. Task-Based Model Selection ✅

**Decision:** Chunks declare `task_type`, model_selector.py maps to optimal LLM

**Implementation:**
```json
{
  "model": "task:translation",
  "meta": {"task_type": "translation"}
}
```

**Rationale:**
- Decouple chunk logic from specific model names
- Easy to upgrade models (change model_selector.py, not all chunks)
- Supports eco/fast mode switching
- DSGVO compliance (security/vision always local)

---

### 4. Backend Transparency ✅

**Decision:** Backend determined by config.meta.backend, not by pipeline or chunk

**Rationale:**
- Same pipeline can use ComfyUI (local) or OpenRouter (cloud)
- Easy to add new backends without changing pipelines
- Config controls everything (structure + content + backend)

---

### 5. No Fourth Layer ✅

**Decision:** No external registries or instruction_types system

**Rationale:**
- Instruction text belongs in configs (content layer)
- External indirection creates ambiguity and redundancy
- Three layers sufficient: Chunks (structure) → Pipelines (flow) → Configs (content)

---

### 6. Config Override Pattern for Runtime Optimization ✅

**Decision:** Use `dataclasses.replace()` for dynamic config modification, store optimization instructions in output chunk metadata

**Implementation:**
```python
from dataclasses import replace

# Load optimization instruction from output chunk
optimization_instruction = output_chunk['meta'].get('optimization_instruction')

# Create modified config with extended context
stage2_config = replace(
    config,
    context=config.context + "\n\n" + optimization_instruction,
    meta={**config.meta, 'optimization_added': True}
)

# Pass override to pipeline executor
result = await pipeline_executor.execute_pipeline(
    config_override=stage2_config
)
```

**Rationale:**
- **Pedagogical Constraint:** Max 2 LLM calls per workflow (single call for interception + optimization)
- **Storage Location:** Optimization instructions belong with model config (output chunk metadata)
- **Runtime Flexibility:** Same interception config works with different output configs
- **Dataclass Pattern:** Config is a dataclass, not Pydantic - use `dataclasses.replace()`, NOT `Config.from_dict()`

**Critical Implementation Rules:**
- ⚠️ MUST use `dataclasses.replace()` for config modification
- ⚠️ MUST load chunks directly from filesystem (ConfigLoader doesn't have `get_chunk()`)
- ⚠️ MUST use `await` for async pipeline execution (can't nest `asyncio.run()`)

**Bug History:** Session 64 Part 3 (2025-11-22) - Fixed 3 critical bugs violating these patterns

**Example Use Case:** SD3.5 Large Dual CLIP optimization (980 char instruction for clip_g + t5xxl architecture)

---

### 7. Component Reusability: MediaOutputBox Template ✅

**Decision:** Create single reusable MediaOutputBox.vue component instead of duplicating output box code in each view

**Problem:**
- ~300 lines of identical output box HTML/CSS duplicated in text_transformation.vue and image_transformation.vue
- Every change (new button, styling, feature) required 2x editing + 2x testing
- Inconsistencies accumulated (e.g., i2i lacked Print, Analyze buttons)
- Poor scalability (adding video/audio views = more duplication)

**Solution:**
- **Single Component:** `/public/ai4artsed-frontend/src/components/MediaOutputBox.vue` (515 lines)
- **Props-Based Configuration:** All state passed via props (outputImage, mediaType, progress, etc.)
- **Event-Based Actions:** Parent views implement action handlers (save, print, download, analyze, forward)
- **Exposed Section Ref:** Component exposes internal `<section>` element via `defineExpose({ sectionRef })` for autoscroll

**Rationale:**

1. **DRY Principle:**
   - Before: ~300 lines × 2 views = 600 lines of duplicate code
   - After: 515 lines component + (19 lines × 2 views) = 553 lines total
   - Net reduction: 47 lines (plus better maintainability)

2. **Single Source of Truth:**
   - All output box UI/UX in one file
   - Bug fixes apply to all views instantly
   - Design changes (button order, colors, spacing) unified

3. **Scalability:**
   - Future views (video, audio, 3d) can reuse with 19 lines
   - No need to copy/paste output box code ever again

4. **Customization via Props:**
   - `forwardButtonTitle` prop allows different tooltips per view
   - Parent views implement action handlers differently (e.g., `sendToI2I()` in T2I forwards to I2I, in I2I it re-transforms)

5. **Autoscroll Compatibility:**
   - Critical requirement: Parent views need DOM element reference for `scrollDownOnly()`
   - Solution: Component exposes `sectionRef` via `defineExpose()`
   - Parent accesses: `pipelineSectionRef.value?.sectionRef`

**Implementation Pattern:**

```vue
<!-- Parent View (text_transformation.vue, image_transformation.vue) -->
<script setup>
import MediaOutputBox from '@/components/MediaOutputBox.vue'

const pipelineSectionRef = ref()

// Action handlers (each view implements differently)
function saveMedia() { /* ... */ }
function printImage() { /* ... */ }
function sendToI2I() { /* ... */ }  // T2I: forward to I2I, I2I: re-transform
function downloadMedia() { /* ... */ }
function analyzeImage() { /* ... */ }

// Autoscroll usage
scrollDownOnly(pipelineSectionRef.value?.sectionRef, 'start')
</script>

<template>
  <MediaOutputBox
    ref="pipelineSectionRef"
    :output-image="outputImage"
    :media-type="outputMediaType"
    :is-executing="isPipelineExecuting"
    :progress="generationProgress"
    forward-button-title="Custom tooltip text"
    @save="saveMedia"
    @print="printImage"
    @forward="sendToI2I"
    @download="downloadMedia"
    @analyze="analyzeImage"
    @image-click="showImageFullscreen"
  />
</template>
```

**Code Reduction Impact:**
- **text_transformation.vue:** -505 lines (170 HTML + 300 CSS + 35 methods)
- **image_transformation.vue:** -293 lines (150 HTML + 200 CSS, added action methods)
- **MediaOutputBox.vue:** +515 lines (new component)
- **Net:** -283 lines total, plus improved maintainability

**Features Included:**
- ⭐ Save (stub, disabled)
- 🖨️ Print (opens print dialog)
- ➡️ Forward (customizable action)
- 💾 Download (timestamped filename)
- 🔍 Analyze (calls `/api/image/analyze`)
- 3 states: Empty (inactive toolbar), Generating (progress), Final (active toolbar)
- All media types: Image, Video, Audio, 3D, Unknown
- Image analysis section (expandable)
- Responsive (vertical toolbar desktop, horizontal mobile)

**Views Using Component:**
- `/public/ai4artsed-frontend/src/views/text_transformation.vue`
- `/public/ai4artsed-frontend/src/views/image_transformation.vue`

**Session:** Session 99 (2025-12-15)
**Commit:** 8e8e3e0

---

### 8. Träshy: Living Assistant Interface Design ✅

**Decision:** Transform the chat assistant (Träshy) from a static button into an active, context-aware companion that follows the user's focus and appears "alive"

**Problem:**
- Static chat icon in corner feels disconnected from workflow
- User has no sense of assistant's awareness or availability
- Standard chatbot UI lacks pedagogical warmth
- Fixed position can obstruct content or become invisible on scroll

**Solution: Three-Layer Context Awareness**

1. **Page Context (Pinia Store)**
   - Views report their state: `activeViewType`, `pageContent`, `focusHint`
   - ChatOverlay reads store to understand current context
   - Context prepended to first message (before run_id session exists)

2. **Focus Tracking**
   - MediaInputBox emits `@focus` events
   - View tracks `focusedField`: 'input' | 'context' | 'interception' | 'optimization'
   - Träshy Y-position follows focused element via `getBoundingClientRect()`

3. **Living Animation**
   - `trashy-idle`: Subtle floating (translate + rotate, 4s cycle)
   - `trashy-breathe`: Gentle scale pulse (1.0 → 1.03, 3s cycle)
   - Movement: cubic-bezier with overshoot for organic feel
   - Asynchronous cycles (3s + 4s) create non-repetitive motion

**Pädagogisches Konzept:**

| Eigenschaft | Umsetzung | Pädagogischer Effekt |
|-------------|-----------|---------------------|
| **Präsenz** | Immer sichtbar, sanft animiert | "Ich bin da wenn du mich brauchst" |
| **Aufmerksamkeit** | Folgt dem Fokus | "Ich sehe was du tust" |
| **Lebendigkeit** | Atmen, Schweben | "Ich bin kein totes UI-Element" |
| **Kontext** | Weiß was auf der Page passiert | "Ich verstehe deinen Workflow" |
| **Nicht-Aufdringlichkeit** | Hover pausiert Animation | "Ich störe nicht, du hast Kontrolle" |

**Technical Implementation:**

```typescript
// pageContextStore.ts - Cross-component communication
export const usePageContextStore = defineStore('pageContext', () => {
  const activeViewType = ref<string>('')
  const pageContent = ref<PageContent>({})
  const focusHint = ref<FocusHint>(DEFAULT_FOCUS_HINT)

  function setPageContext(ctx: PageContext) { ... }
  function formatForLLM(routePath: string): string { ... }
})

// View: Report context and track focus
watch(pageContext, (ctx) => {
  pageContextStore.setPageContext(ctx)
}, { immediate: true, deep: true })

// ChatOverlay: Calculate clamped position
const clampedTop = Math.max(MARGIN, Math.min(maxTop, requestedTop))
```

```css
/* Idle animation - creates "living" feel */
@keyframes trashy-idle {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(2px, -3px) rotate(1deg); }
  50% { transform: translate(-1px, -5px) rotate(-0.5deg); }
  75% { transform: translate(-2px, -2px) rotate(0.5deg); }
}

/* Movement with organic overshoot */
transition: top 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
```

**Rationale:**

1. **Pedagogical Warmth:** Educational tools benefit from "human" touches. A living assistant feels more approachable than a static button.

2. **Context Awareness:** By tracking focus, Träshy demonstrates attention to the user's current task, making help feel more relevant.

3. **Non-Intrusive Presence:** Animations are subtle (2-5px movement). Hover pauses animation for precise clicking. Viewport clamping prevents obstruction.

4. **Technical Elegance:** Pinia store solves Vue's provide/inject limitation (only works parent→child, not sibling→sibling).

**Files:**
- `src/stores/pageContext.ts` - Pinia store
- `src/components/ChatOverlay.vue` - Positioning + animations
- `src/components/MediaInputBox.vue` - Focus events
- `src/views/*.vue` - Focus tracking

**Session:** Session 136 (2026-01-25)
**Commits:** `7f34bfd` through `bc65f2c`

---

