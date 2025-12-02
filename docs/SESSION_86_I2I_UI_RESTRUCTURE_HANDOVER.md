# Session 86 Handover: Image Transformation UI Restructure

**Status:** 🟡 IN PROGRESS (50% complete)
**Branch:** `develop`
**Last Commit:** `6529818` - "feat: Session 85 final improvements - UX + prompt optimization"

---

## Executive Summary

Session 85 completed the **QWEN Image Edit i2i backend implementation** (100% functional). Session 86 started **major UI restructuring** to align `image_transformation.vue` with `text_transformation.vue` design patterns. Work is 50% complete - planning done, implementation pending.

---

## What Was Completed (Session 85)

### ✅ Backend - Fully Working
1. **Prompt Injection Fix** - Uses `input_mappings` from chunk JSON instead of hardcoded title search
2. **Meta-Prompt Optimization** - No headers, direct action commands only (Transform, Add, Remove, Change)
3. **Progress Simulation** - 23-second estimated duration with real-time percentage (0→90% over 23s, then 100%)
4. **Button Styling** - `>>> Start >>>` button matches text_transformation.vue exactly
5. **Model Downloads** - All 4 QWEN models (20.8GB) downloaded and symlinked

### ✅ Cleanup
- Removed SD3.5 img2img config and chunk (non-functional)
- Removed retry button under output image (redundant)
- Updated documentation (DEVELOPMENT_DECISIONS.md, DEVELOPMENT_LOG.md, SESSION_85)

---

## What Needs To Be Done (Session 86)

### 🔴 CRITICAL: Header Consolidation
**Problem:** Each Vue component has its own header code (bad web design).
**Solution:** Extract header to shared component, use once across all views.

```vue
<!-- CURRENT (BAD): Duplicated in each vue -->
<header class="page-header">
  <button class="return-button" @click="$router.push('/')" title="Zurück zu Phase 1">
    ← Phase 1
  </button>
  <h1 class="page-title">AI4ArtsEd - AI-Lab</h1>
</header>

<!-- REQUIRED (GOOD): Single shared component -->
<PageHeader /> <!-- defined once, used everywhere -->
```

**Action Items:**
1. Create `/public/ai4artsed-frontend/src/components/PageHeader.vue`
2. Extract header HTML + CSS from text_transformation.vue
3. Replace header in all views: text_transformation.vue, image_transformation.vue
4. Test navigation across all views

---

### 🟡 Major UI Restructure (50% Complete)

#### Planning Done ✅
Analysis of text_transformation.vue structure completed. Key patterns identified:

**Standard Vue Structure:**
- No section titles (no h2 tags like "Wähle ein Medium", "Dein transformiertes Bild")
- Bubble cards with icons + labels only
- Start button **always visible** (enabled/disabled, never v-if)
- Output frame with 3 states: empty, generating, final
- Safety stamp next to Start button, not on image
- Single continuous flow, no phase transitions

#### Implementation Pending ❌

**Current image_transformation.vue issues:**
1. Has 6 section titles (lines 6, 17, 35, 52, 78, 123) - all must be removed
2. Has separate category selection (lines 34-48) - must be removed, auto-select "image"
3. Has separate model selection (lines 50-74) - must be removed, auto-select `qwen_img2img`
4. Has separate optimization section (lines 76-97) - must be removed (QWEN doesn't need it)
5. Start button is `v-if` (line 100) - must be always visible, only disabled
6. Output is separate section (line 122) - must be integrated into output-frame
7. Progress is separate section (line 114) - must be inside output-frame

---

## Target Structure (Based on text_transformation.vue)

```vue
<template>
  <div class="image-transformation-view">

    <!-- Shared Header Component -->
    <PageHeader />

    <div class="phase-2a" ref="mainContainerRef">

      <!-- Section 1: Image Upload (Bubble Card) -->
      <section class="image-upload-section">
        <div class="image-bubble bubble-card" :class="{ filled: uploadedImage }">
          <div class="bubble-header">
            <span class="bubble-icon">🖼️</span>
            <span class="bubble-label">Lade dein Bild hoch</span>
          </div>
          <ImageUploadWidget @image-uploaded="..." />
        </div>
      </section>

      <!-- Section 2: Context Prompt (Bubble Card) -->
      <section class="context-section">
        <div class="context-bubble bubble-card" :class="{ filled: contextPrompt }">
          <div class="bubble-header">
            <span class="bubble-icon">📋</span>
            <span class="bubble-label">Wie soll das Bild verändert werden?</span>
          </div>
          <textarea v-model="contextPrompt" class="bubble-textarea" rows="4"></textarea>
        </div>
      </section>

      <!-- START BUTTON (Always Visible) -->
      <div class="start-button-container">
        <button
          class="start-button"
          :class="{ disabled: !canStartGeneration || isPipelineExecuting }"
          :disabled="!canStartGeneration || isPipelineExecuting"
          @click="startGeneration"
        >
          <span class="button-arrows button-arrows-left">>>></span>
          <span class="button-text">Start</span>
          <span class="button-arrows button-arrows-right">>>></span>
        </button>

        <!-- Safety Stamp (next to button, not on image) -->
        <transition name="fade">
          <div v-if="showSafetyApprovedStamp" class="safety-stamp">
            <div class="stamp-inner">
              <div class="stamp-icon">✓</div>
              <div class="stamp-text">Safety<br/>Approved</div>
            </div>
          </div>
        </transition>
      </div>

      <!-- OUTPUT FRAME (3 States: empty, generating, final) -->
      <section class="pipeline-section" ref="pipelineSectionRef">
        <div class="output-frame" :class="{
          empty: !isPipelineExecuting && !outputImage,
          generating: isPipelineExecuting && !outputImage
        }">
          <!-- State 1: Empty (before generation) -->
          <div v-if="!isPipelineExecuting && !outputImage" class="empty-state">
            <div class="empty-icon">🖼️</div>
            <p>Dein transformiertes Bild erscheint hier</p>
          </div>

          <!-- State 2: Generating (progress animation) -->
          <div v-if="isPipelineExecuting && !outputImage" class="generation-animation-container">
            <SpriteProgressAnimation :progress="generationProgress" />
          </div>

          <!-- State 3: Final Output -->
          <div v-else-if="outputImage" class="final-output">
            <img :src="outputImage" alt="Generated image" @click="openFullscreen" />
          </div>
        </div>
      </section>

    </div>
  </div>
</template>
```

---

## Script Changes Required

### Auto-select qwen_img2img (Remove User Selection)

```typescript
// CURRENT (BAD): User selects category and model
const selectedCategory = ref<string | null>(null)
const selectedConfig = ref<string | null>(null)

const configsByCategory = {
  image: [
    { id: 'qwen_img2img', label: 'Qwen\nIMG2IMG', emoji: '🌟', ... }
  ]
}

// REQUIRED (GOOD): Auto-select on mount
const selectedConfig = ref<string>('qwen_img2img') // Always qwen_img2img for i2i

onMounted(() => {
  selectedConfig.value = 'qwen_img2img' // Auto-select, no UI for it
})

// Remove: selectCategory(), selectConfig(), configsByCategory, availableCategories
```

### Start Button Always Visible

```typescript
// CURRENT (BAD): Start button shown conditionally
const canStartGeneration = computed(() => {
  return uploadedImage.value && contextPrompt.value && selectedConfig.value
})

// In template: v-if="canStartGeneration"

// REQUIRED (GOOD): Button always visible, just disabled
const canStartGeneration = computed(() => {
  return uploadedImage.value && contextPrompt.value.trim().length > 0
})

// In template: NO v-if, only :disabled="!canStartGeneration"
```

### Remove Optimization Preview

QWEN doesn't need separate optimization display. The meta-prompt optimization happens server-side (Stage 3), user doesn't need to see it.

**Remove:**
- `hasOptimization` computed property
- `isOptimizationLoading` ref
- `optimizedPrompt` ref (or keep for internal use only, no display)
- Optimization section template (lines 76-97)

---

## CSS Changes Required

### Copy ALL Styles from text_transformation.vue

**Critical:** Don't just copy button styles - copy **ENTIRE** CSS structure:

1. `.text-transformation-view` → `.image-transformation-view`
2. `.page-header` - header styles (or extract to PageHeader.vue)
3. `.phase-2a` - main container styles
4. `.bubble-card`, `.bubble-header`, `.bubble-icon`, `.bubble-label`, `.bubble-textarea`
5. `.start-button-container`, `.start-button`, `.button-arrows`, animations
6. `.pipeline-section`, `.output-frame`, `.empty-state`, `.generation-animation-container`, `.final-output`
7. `.safety-stamp` - positioning next to button, not on image
8. All responsive breakpoints

**Why?** Consistency is critical. Both views must look **identical** except for content. Users should not notice design differences between text→image and image→image modes.

---

## Testing Checklist

After completing restructure:

- [ ] Header is shared component (not duplicated code)
- [ ] No section titles (h2 tags) visible
- [ ] No category selection UI (auto-selects "image")
- [ ] No model selection UI (auto-selects qwen_img2img)
- [ ] Start button always visible (disabled when can't start)
- [ ] Output frame shows empty state initially
- [ ] Progress animation shows in output frame during generation
- [ ] Final image shows in output frame after completion
- [ ] Safety stamp appears next to button, not on image
- [ ] Fonts match text_transformation.vue exactly
- [ ] Colors match text_transformation.vue exactly
- [ ] Spacing/padding matches text_transformation.vue exactly
- [ ] Responsive breakpoints work correctly
- [ ] Navigation between views works (header back button)

---

## Files To Modify

### Create New
- `/public/ai4artsed-frontend/src/components/PageHeader.vue` (extract from text_transformation.vue)

### Modify
- `/public/ai4artsed-frontend/src/views/image_transformation.vue` (complete rewrite)
- `/public/ai4artsed-frontend/src/views/text_transformation.vue` (replace header with `<PageHeader />`)
- `/public/ai4artsed-frontend/src/App.vue` (if global styles needed)

### Reference (Read Only)
- `/public/ai4artsed-frontend/src/views/text_transformation.vue` (lines 1-250 for structure)
- `/public/ai4artsed-frontend/src/views/text_transformation.vue` (lines 1300-1600 for CSS)

---

## Known Issues / Gotchas

1. **Image Upload Widget** - Must adapt to bubble-card style (add bubble-header inside widget)
2. **Progress Animation** - Must fit inside output-frame (may need size adjustments)
3. **Fullscreen Modal** - Keep existing implementation, works fine
4. **Context Prompt Edit** - Keep `handleContextPromptEdit()` logic (resets optimization when edited)
5. **Safety Stamp** - Position absolute relative to start-button-container, not output-frame

---

## Architecture Decisions

### Why Remove Model Selection?

**Reason:** Only 1 model per medium. UI clutter for no benefit.
- Image → qwen_img2img (only option)
- Video → Future: ltx_video or similar (only 1 option per medium)
- Audio → Future: single model

**If** we add multiple models per medium later, restore model selection. But current architecture: 1 medium = 1 best model.

### Why Remove Category Selection?

**Reason:** User already chose mode in header (📝 Text→Bild vs 🖼️ Bild→Bild).
Selecting category again is **redundant**.

**Mode Toggle (Header)** = Primary selection
**Category Bubbles (in view)** = Redundant, remove

### Why Remove Optimization Preview?

**Reason:** QWEN's optimization_instruction is lightweight and fast.
Text_transformation shows optimization because Stage 2 interception is pedagogically important.
Image_transformation has no Stage 2 - optimization is just prompt formatting, not worth displaying.

---

## Estimated Work (Next Session)

- **PageHeader extraction:** 30 minutes
- **Template rewrite:** 60 minutes
- **CSS adaptation:** 45 minutes
- **Script cleanup:** 30 minutes
- **Testing:** 30 minutes
- **Total:** ~3 hours

---

## Contact Points / Questions

If unclear:
1. **"What should X look like?"** → Reference text_transformation.vue, copy design exactly
2. **"Do I need this feature?"** → If text_transformation doesn't have it, remove it
3. **"Where should this code go?"** → Match text_transformation.vue structure 1:1

**Guiding Principle:** Make image_transformation.vue a **simplified clone** of text_transformation.vue with:
- Image upload instead of text input
- No interception step (Stage 2 skipped)
- Auto-selected model (no UI)

Everything else: **identical**.

---

## Session 86 Deliverables (When Complete)

- [ ] PageHeader.vue component created and integrated
- [ ] image_transformation.vue restructured (no titles, no selections, always-visible button)
- [ ] CSS matches text_transformation.vue exactly
- [ ] All tests passing (checklist above)
- [ ] Frontend built successfully
- [ ] Committed and pushed to develop branch
- [ ] Documentation updated (this handover marked complete)

---

**Next Session Start Here:**
1. Create PageHeader.vue
2. Rewrite image_transformation.vue template (use target structure above)
3. Copy ALL CSS from text_transformation.vue
4. Remove category/model selection logic from script
5. Test thoroughly
6. Commit

**DO NOT:** Start implementation without reading this entire handover first.
