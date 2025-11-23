# DevServer Architecture

**Part 12: Frontend Architecture**

---


### Overview

**Status:** ✅ Complete migration (2025-10-28), v2.0.0-alpha.1 (2025-11-09)
**Architecture:** 100% Backend-abstracted - Frontend NEVER accesses ComfyUI directly

**SSE Streaming Status:** ⏸ POSTPONED (Session 39) - SpriteProgressAnimation used instead

The Frontend implements a clean separation between UI and Backend services, using Backend API exclusively for all operations.

### Core Components

#### 1. Config Browser (`config-browser.js`)

**Purpose:** Card-based visual selection of 37+ configs

```javascript
// Initialization
initConfigBrowser()
  → fetch('/pipeline_configs_metadata')
  → Backend returns: { configs: [...] }
  → Render cards grouped by category
```

**Features:**
- Card-based UI with icon, name, description
- Grouped by category (Bildgenerierung, Textverarbeitung, etc.)
- Visual selection feedback
- Difficulty stars
- Workshop badges

**Data Flow:**
```
User clicks card
  → selectConfig(configId)
  → Store in selectedConfigId
  → Visual feedback (selected class)
```

#### 2. Execution Handler (`execution-handler.js`)

**Purpose:** Backend-abstracted execution + media polling

**Execution Flow:**
```javascript
submitPrompt()
  → Validate: configId + promptText
  → Build payload: { schema, input_text, execution_mode, aspect_ratio }
  → POST /api/schema/pipeline/execute
  → Backend returns: {
      status: "success",
      final_output: "transformed text",
      media_output: {
        output: "prompt_id",
        media_type: "image"
      }
    }
  → Display transformed text
  → Start media polling
```

**Media Polling (NEW Architecture):**
```javascript
pollForMedia(promptId, mediaType)
  → Every 1 second:
    → GET /api/media/info/{promptId}
    → If 404: Continue polling (not ready yet)
    → If 200: Media ready!
      → displayMediaFromBackend(promptId, mediaInfo)
```

**Media Display:**
```javascript
displayImageFromBackend(promptId)
  → Create <img src="/api/media/image/{promptId}">
  → Backend fetches from ComfyUI internally
  → Returns PNG directly
```

#### 3. Application Initialization (`main.js`)

**Purpose:** Bootstrap application with new architecture

```javascript
initializeApp()
  → initSimpleTranslation()
  → loadConfig()
  → initConfigBrowser()  // NEW: Card-based UI
  → setupImageHandlers()
  → initSSEConnection()  // DEPRECATED: SSE streaming postponed (Session 39)
```

**Note:** SSE (Server-Sent Events) streaming was attempted in Session 37 but postponed in Session 39. v2.0.0-alpha.1 uses SpriteProgressAnimation for progress indication instead.

#### 4. SpriteProgressAnimation Component (`SpriteProgressAnimation.vue`)

**Purpose:** Visual progress feedback for pipeline execution (educational + entertaining)
**Target Audience:** Children and youth (iPad-optimized, lightweight)
**Status:** ✅ Implemented Session 40 (2025-11-09)

**Architecture:**
- Token processing metaphor: INPUT grid → PROCESSOR → OUTPUT grid
- 14x14 pixel grids (196 tokens)
- Pure CSS animations (no heavy libraries)
- 26 randomized pixel art images (robot, animals, food, space, etc.)

**Key Features:**
- **Neural Network Visualization:** 5 pulsating nodes + connection lines in processor box
- **Color Transformation:** Gradual color change visible during processing (40% of animation time)
- **Flight Animation:** Tokens fly from left edge to right edge through processor (0.6s per token)
- **Real-time Timer:** "generating X sec._" with blinking cursor
- **Progress Scaling:** Animation completes at 90% progress

**Technical Implementation:**
```typescript
// Progress calculation scaled to complete at 90%
const processedCount = computed(() => {
  const scaledProgress = Math.min(props.progress / 90, 1)
  return Math.floor(scaledProgress * totalTokens)
})

// Color transformation using CSS color-mix
@keyframes pixel-fly-from-left {
  42% { background-color: color-mix(in srgb, var(--from-color) 70%, var(--to-color) 30%); }
  50% { background-color: color-mix(in srgb, var(--from-color) 50%, var(--to-color) 50%); }
  58% { background-color: color-mix(in srgb, var(--from-color) 30%, var(--to-color) 70%); }
  68% { background-color: var(--to-color); }
}
```

**Performance:**
- CPU/GPU: Minimal (pure CSS transforms)
- Animation duration: 0.6s per pixel (balances visibility vs. smoothness)
- Memory: Timer cleanup in onUnmounted
- Responsive: Mobile @media queries for smaller screens

**Design Decision:**
User rejected complex pixel-art sprites as "schlimm" (terrible). Token processing metaphor chosen for:
- Educational value (visualizes AI transformation)
- Simplicity (geometric shapes easier to animate)
- Conceptual alignment (matches GenAI token processing model)

See: `DEVELOPMENT_LOG.md` Session 40 for detailed iteration history.

### API Endpoints Used by Frontend

**Config Selection:**
```
GET /pipeline_configs_metadata
→ Returns: { configs: [{ id, name, description, category, ... }] }
```

**Execution:**
```
POST /api/schema/pipeline/execute
Body: { schema: "dada", input_text: "...", execution_mode: "eco" }
→ Returns: { status, final_output, media_output }
```

**Media Polling:**
```
GET /api/media/info/{prompt_id}
→ If ready: { type: "image", count: 1, files: [...] }
→ If not ready: 404
```

**Media Retrieval:**
```
GET /api/media/image/{prompt_id}
→ Returns: PNG file (binary)

GET /api/media/audio/{prompt_id}
→ Returns: MP3/WAV file (binary)

GET /api/media/video/{prompt_id}
→ Returns: MP4 file (binary) [future]
```

### Benefits of Backend Abstraction

1. **Generator Independence**
   - Frontend doesn't know about ComfyUI
   - Backend can switch to SwarmUI, Replicate, etc. without Frontend changes

2. **Media Type Flexibility**
   - Same polling logic for image, audio, video
   - Media type determined by Config metadata

3. **Clean Error Handling**
   - Backend validates and provides meaningful errors
   - Frontend just displays them

4. **Stateless Frontend**
   - No workflow state management
   - No complex polling logic
   - Simple request/response pattern

5. **Progress Indication**
   - SpriteProgressAnimation provides visual feedback (Session 39)
   - SSE streaming postponed for future enhancement
   - Backend handles complexity, frontend stays simple

### Legacy Components (Obsolete)

These files are marked `.obsolete` and no longer used:

- ❌ `workflow.js.obsolete` - Dropdown-based config selection
- ❌ `workflow-classifier.js.obsolete` - Runtime workflow classification
- ❌ `workflow-browser.js.obsolete` - Incomplete migration attempt
- ❌ `workflow-streaming.js.obsolete` - Legacy API with direct ComfyUI access
- ❌ `dual-input-handler.js.obsolete` - Replaced by execution-handler
- ⏸ `sse-connection.js` - SSE streaming infrastructure (postponed Session 39, may be reactivated later)

### File Structure

```
public_dev/
├── index.html                      # Main UI (no dropdown, only card container)
├── css/
│   ├── workflow-browser.css       # Card-based UI styles
│   └── ...
├── js/
│   ├── main.js                     # Application bootstrap (NEW architecture)
│   ├── config-browser.js           # Card-based config selection (NEW)
│   ├── execution-handler.js        # Backend-abstracted execution (NEW)
│   ├── ui-elements.js              # DOM element references
│   ├── ui-utils.js                 # UI helper functions
│   ├── simple-translation.js       # i18n for static UI
│   ├── image-handler.js            # Image upload handling
│   ├── sse-connection.js           # Real-time queue updates
│   └── *.obsolete                  # Legacy files (deprecated)
```

### Testing Checklist

When testing Frontend changes:

- [ ] Config browser loads 37+ configs
- [ ] Config selection works (visual feedback)
- [ ] Text input + config selection → valid payload
- [ ] POST /api/schema/pipeline/execute succeeds
- [ ] Transformed text displays correctly
- [ ] Media polling via /api/media/info works
- [ ] Image displays via /api/media/image works
- [ ] Audio/music displays correctly (if applicable)
- [ ] Error messages display user-friendly text

---

## Vue Frontend v2.0.0 (Property Selection Interface)

**Status:** ✅ Active (2025-11-21)
**Location:** `/public/ai4artsed-frontend/`
**Technology:** Vue 3 + TypeScript + Vite

### Architecture Overview

The Vue frontend implements a visual property-based configuration selection system, allowing users to explore AI art generation configs through an interactive bubble interface.

**Core Flow:**
```
PropertyQuadrantsView (Parent)
    ↓
PropertyCanvas (Unified Component)
    ↓
PropertyBubble (Category bubbles) + Config Bubbles (Configuration selection)
```

---

## Bubble Design System

**Status:** ✅ Project-wide design pattern (2025-11-21)
**Canonical Implementation:** `PropertyCanvas.vue` + `PropertyBubble.vue`
**Scope:** All phases of the application (current + future)

### Overview

The Bubble Design System is the foundational UI pattern for the AI4ArtsEd frontend. It uses circular "bubbles" as the primary interaction metaphor for both category selection (Phase 1) and configuration selection across all phases.

**Design Principles:**
1. **Consistency** - Same bubble metaphor across all phases
2. **Visual Hierarchy** - Size difference indicates importance (configs > categories)
3. **Accessibility** - High contrast, clear labels, touch-friendly sizes
4. **Responsiveness** - Percentage-based sizing scales with viewport
5. **Visual Polish** - Shadows, backdrop filters, smooth animations

---

### Visual Design Elements

#### 1. Category Bubbles (PropertyBubble component)

**Purpose:** Top-level property categories (semantics, aesthetics, arts, heritage, freestyle)

**Visual Specifications:**
- **Shape:** Circular (`border-radius: 50%`)
- **Size:** 12% of container width with `aspect-ratio: 1:1`
- **Background:** `rgba(20, 20, 20, 0.9)` (dark, semi-transparent)
- **Border:** `3px solid` with category-specific color
- **Content:** Emoji symbol + text label (centered)
- **Typography:**
  - Symbol: Large emoji (48px default)
  - Label: 14px, semi-bold, white

**States:**
- **Default:** Dark background, colored border, no glow
- **Hover:** `transform: scale(1.1)` with colored glow shadow
- **Selected:** Background filled with category color, elevated shadow

**Implementation Example:**
```vue
<div class="property-bubble selected"
     :style="{
       left: '50%',
       top: '50%',
       '--bubble-color': '#2196F3',
       '--bubble-shadow': '0 0 20px #2196F3'
     }">
  <span class="property-symbol">💬</span>
</div>
```

```css
.property-bubble {
  width: 12%;  /* Percentage of container */
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  background: rgba(20, 20, 20, 0.9);
  border: 3px solid var(--bubble-color);
  box-shadow: var(--bubble-shadow);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.property-bubble:hover {
  transform: scale(1.1);
  box-shadow: 0 0 25px var(--bubble-color);
}

.property-bubble.selected {
  background: var(--bubble-color);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
```

---

#### 2. Config Bubbles

**Purpose:** Individual configuration selection (dada, bauhaus, abstract-photo, etc.)

**Visual Specifications:**
- **Shape:** Circular (`border-radius: 50%`)
- **Size:** 18% of container width (larger than categories to show hierarchy)
- **Background:** White with config preview image
- **Image:** `background-size: cover`, `background-position: center`
- **Text Badge Overlay:**
  - Position: `bottom: 8%` of bubble
  - Background: `rgba(0, 0, 0, 0.85)`
  - Border-radius: `10px`
  - Backdrop-filter: `blur(8px)`
  - Max 2 lines with ellipsis overflow
  - Typography: 14px, font-weight 600, white color

**States:**
- **Default:** Preview image + text badge
- **Hover:** `transform: scale(1.1)` with elevated shadow
- **Selected:** (Navigation trigger - no persistent state)

**Implementation Example:**
```vue
<div class="config-bubble"
     :style="{
       left: '72%',
       top: '28%',
       backgroundImage: 'url(/config-previews/dada.png)'
     }"
     @click="selectConfiguration(config)">
  <div class="config-content">
    <div class="preview-image" />
    <div class="text-badge">Dada</div>
  </div>
</div>
```

```css
.config-bubble {
  width: 18%;  /* Larger than category bubbles */
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: absolute;
  overflow: hidden;
}

.config-bubble:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.preview-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  border-radius: 50%;
}

.text-badge {
  position: absolute;
  bottom: 8%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  color: white;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  max-width: 80%;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
```

---

### Color System

**Category Colors:**
```javascript
const categoryColorMap: Record<string, string> = {
  semantics: '#2196F3',   // Blue 💬
  aesthetics: '#9C27B0',  // Purple 🪄
  arts: '#E91E63',        // Pink 🖌️
  heritage: '#4CAF50',    // Green 🌍
  freestyle: '#FFC107',   // Gold 🫵
}
```

**Usage:**
- Category bubble borders
- Selected state backgrounds
- Hover glow effects
- Color consistency across all UI elements

---

### Layout Pattern

#### X-Formation (Category Bubbles)

Categories are arranged in an X-pattern with Freestyle at the center:

```typescript
// Positions in percentage (0-100) relative to container
const categoryPositions: Record<string, CategoryPosition> = {
  freestyle: { x: 50, y: 50 },      // Center
  semantics: { x: 72, y: 28 },      // Top-right (45°)
  aesthetics: { x: 72, y: 72 },     // Bottom-right (135°)
  arts: { x: 28, y: 72 },           // Bottom-left (225°)
  heritage: { x: 28, y: 28 },       // Top-left (315°)
}
```

**Rationale:**
- Central Freestyle allows quick access to unrestricted configs
- Symmetric layout provides visual balance
- 45° angles maximize space utilization
- Percentage positioning ensures responsiveness

#### Circular Arrangement (Config Bubbles)

Configs appear in a circle around their selected category:

```typescript
const OFFSET_DISTANCE = 25  // Percentage units

const getConfigStyle = (config: ConfigMetadata, index: number) => {
  const categoryX = categoryPositions[selectedCategory.value].x
  const categoryY = categoryPositions[selectedCategory.value].y

  // Calculate angle based on config count
  const angle = (index / visibleConfigs.length) * 2 * Math.PI

  // Calculate position on circle
  const configX = categoryX + Math.cos(angle) * OFFSET_DISTANCE
  const configY = categoryY + Math.sin(angle) * OFFSET_DISTANCE

  return {
    left: `${configX}%`,
    top: `${configY}%`,
  }
}
```

**Rationale:**
- Configs visually connected to their parent category
- Equal spacing prevents overlap
- Dynamic calculation supports any number of configs
- Maintains spatial relationship across viewport sizes

---

### Responsive Container

**Container Sizing:**
```css
.cluster-wrapper {
  width: min(70vw, 70vh);
  height: min(70vw, 70vh);
  position: relative;
  margin: 0 auto;
}
```

**Rationale:**
- Square aspect ratio simplifies percentage calculations
- `min()` ensures container fits both portrait and landscape
- 70% viewport leaves room for header and margins
- All child bubbles use percentage positioning relative to this container

---

### Interaction Design

#### Touch Support

All bubbles support both mouse and touch events:

```typescript
<div
  @click="handleClick"
  @touchstart.prevent="selectConfiguration(config)"
>
```

**Considerations:**
- Touch targets minimum 44x44px (iOS/Android guidelines)
- Prevents default touch behavior to avoid scrolling
- Distinguishes tap from drag events

#### Smooth Transitions

All state changes use consistent timing:

```css
transition: transform 0.3s ease, box-shadow 0.3s ease;
```

**Transition Types:**
- **Transform:** Scale effects on hover/select
- **Box-shadow:** Glow effects for visual feedback
- **Opacity:** Fade-in/out for config bubbles

**Config Bubble Transitions:**
```vue
<transition-group name="config-fade">
  <!-- Config bubbles -->
</transition-group>
```

```css
.config-fade-enter-active,
.config-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.config-fade-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.config-fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
```

#### XOR Selection Logic

Only ONE category can be selected at a time:

```typescript
const handlePropertyToggle = (property: string) => {
  if (selectedCategory.value === property) {
    // Deselect if clicking same category
    selectedCategory.value = null
  } else {
    // Select new category (auto-deselects previous)
    selectedCategory.value = property
  }
}
```

**Rationale:**
- Simplifies user mental model (one choice at a time)
- Reduces UI complexity (no multi-select state management)
- Matches pedagogical flow (progressive refinement)

---

### Implementation Reference

**Canonical Files:**
- `/public/ai4artsed-frontend/src/components/PropertyCanvas.vue` - Complete implementation
- `/public/ai4artsed-frontend/src/components/PropertyBubble.vue` - Category bubble component
- `/public/ai4artsed-frontend/src/assets/main.css` - Global bubble styles

**Key Code Sections:**

1. **Category Bubble Component** (`PropertyBubble.vue`)
   - Lines 59-65: Style computation with CSS variables
   - Lines 2-14: Template structure with percentage positioning

2. **Config Bubble Layout** (`PropertyCanvas.vue`)
   - Lines 22-40: Config bubble rendering with preview images
   - Lines 145-165: Circular positioning calculation
   - Lines 92-97: Category color mapping

3. **Container Setup** (`PropertyCanvas.vue`)
   - Lines 2-42: Template with cluster-wrapper container
   - CSS: `.cluster-wrapper` responsive sizing

---

### Future Application

This design system should be applied to:

**Phase 2: Creative Flow**
- Bubble-based workflow step selection
- Same size hierarchy (categories > steps)
- Maintain color consistency

**Phase 3: Pipeline Execution**
- Progress visualization using bubble metaphor
- Stage completion indicators (filled bubbles)
- Error states (red border/glow)

**Phase 4: Output Gallery**
- Generated media as bubbles (circular thumbnails)
- Hover for preview, click for full view
- Maintain text badge overlay pattern

**General Guidelines:**
- Always use circular (`border-radius: 50%`) for bubbles
- Maintain size hierarchy (larger = more important)
- Use percentage positioning for responsiveness
- Apply consistent transition timings (0.3s ease)
- Follow category color system
- Text badges always at 8% from bottom with backdrop-filter

---

### Key Components

#### 1. PropertyCanvas.vue (Unified Component)

**Purpose:** Displays category bubbles and configuration bubbles in a single coordinate system

**Location:** `/public/ai4artsed-frontend/src/components/PropertyCanvas.vue`

**Architecture Decision (2025-11-21, Commits e266628 + be3f247):**

Previously split into two separate components (PropertyCanvas + ConfigCanvas), which caused coordinate system mismatches. The two components used different positioning logic, resulting in config bubbles appearing in incorrect locations.

**Solution:** Merged ConfigCanvas functionality into PropertyCanvas, creating a single unified component with one coordinate system.

**Key Features:**
- **Unified Coordinate System:** All bubbles (category + config) use percentage-based positioning within the same container
- **Responsive Sizing:** Container dimensions calculated as `min(70vw, 70vh)` for consistent scaling
- **X-Formation Layout:** 5 category bubbles arranged in X-pattern with Freestyle in center
- **Dynamic Config Display:** Config bubbles appear in circular arrangement around selected category
- **Touch Support:** iPad/mobile-friendly touch events
- **Config Preview Images:** Displays preview images from `/config-previews/{config-id}.png`
- **Text Badge Overlay:** Black semi-transparent badge at 8% from bottom (matching ConfigTile design)

**Coordinate System:**
```typescript
// All positions in percentage (0-100) relative to cluster-wrapper
const categoryPositions: Record<string, CategoryPosition> = {
  freestyle: { x: 50, y: 50 },      // Center
  semantics: { x: 72, y: 28 },       // Top-right (45°)
  aesthetics: { x: 72, y: 72 },      // Bottom-right (135°)
  arts: { x: 28, y: 72 },            // Bottom-left (225°)
  heritage: { x: 28, y: 28 },        // Top-left (315°)
}
```

**Config Bubble Positioning:**
```typescript
// Configs arranged in circle around their parent category
const angle = (index / visibleConfigs.length) * 2 * Math.PI
const configX = categoryX + Math.cos(angle) * OFFSET_DISTANCE
const configY = categoryY + Math.sin(angle) * OFFSET_DISTANCE
```

**Styling:**
- **Category Bubbles:** 100px diameter, glassmorphic effect, category-specific colors
- **Config Bubbles:** 240px diameter, preview image background, text badge overlay
- **Transitions:** Smooth fade-in/out for config bubbles (config-fade transition)
- **Hover Effects:** Scale transforms on hover (category: 1.05, config: 1.08)

**Bug Fixed (Commit e266628):**
```
BEFORE (Two Components):
PropertyCanvas → percentage positioning
ConfigCanvas → pixel positioning + different center calculation
Result: Configs appeared top-right, not around categories

AFTER (Unified):
PropertyCanvas → single percentage-based coordinate system
Result: Configs correctly positioned around categories
```

#### 2. PropertyBubble.vue (Category Bubble Component)

**Purpose:** Individual category bubble with emoji symbol and color

**Location:** `/public/ai4artsed-frontend/src/components/PropertyBubble.vue`

**Features:**
- Percentage-based absolute positioning
- Draggable within container bounds
- Selection state management
- Emoji symbols with category colors
- Glassmorphic styling

**Props:**
- `property: string` - Category identifier (e.g., "semantics")
- `color: string` - Hex color for category
- `is-selected: boolean` - Selection state
- `x: number` - X position in percentage (0-100)
- `y: number` - Y position in percentage (0-100)
- `symbol-data: SymbolData` - Emoji and metadata

#### 3. PropertyQuadrantsView.vue (Parent View)

**Purpose:** Container view managing layout and responsive sizing

**Location:** `/public/ai4artsed-frontend/src/views/PropertyQuadrantsView.vue`

**Responsibilities:**
- Header with title and "Clear Selection" button
- ResizeObserver for responsive canvas dimensions
- Props passing to PropertyCanvas
- Navigation to pipeline execution

**Layout:**
```vue
<div class="property-view">
  <header>
    <h1>Konfiguration auswählen</h1>
    <button v-if="hasSelection">Auswahl löschen</button>
  </header>
  <div class="canvas-area">
    <PropertyCanvas :selected-properties="selectedProperties" />
  </div>
</div>
```

#### 4. ConfigTile.vue (Grid View Component)

**Purpose:** Alternative grid-based config selection (not used in PropertyCanvas)

**Location:** `/public/ai4artsed-frontend/src/components/ConfigTile.vue`

**Note:** ConfigTile is used in list/grid views, while PropertyCanvas uses inline config bubbles. Both share the same preview image + text badge design pattern.

### Design Patterns

#### Config Preview Images (Commit be3f247)

All config bubbles display preview images with consistent styling:

```vue
<div class="config-bubble">
  <div class="config-content">
    <!-- Background image -->
    <div class="preview-image"
         :style="{ backgroundImage: `url(/config-previews/${config.id}.png)` }">
    </div>

    <!-- Text badge overlay -->
    <div class="text-badge">
      {{ config.name[currentLanguage] }}
    </div>
  </div>
</div>
```

**Styling:**
```css
.preview-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  border-radius: 50%;
}

.text-badge {
  position: absolute;
  bottom: 8%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}
```

**Removed:** Fallback letter placeholder system (previously used when images were unavailable)

#### XOR Selection Logic

Only ONE category can be selected at a time:

```typescript
const handlePropertyToggle = (property: string) => {
  if (selectedCategory.value === property) {
    // Deselect if clicking same category
    selectedCategory.value = null
  } else {
    // Select new category (auto-deselects previous)
    selectedCategory.value = property
  }
}
```

### State Management

**Store:** `/public/ai4artsed-frontend/src/stores/configSelection.ts`

**Managed State:**
- `categories: string[]` - Available property categories
- `availableConfigs: ConfigMetadata[]` - All configurations
- `selectedProperties: string[]` - Currently selected categories (XOR: max 1)
- `selectedConfigId: string | null` - Currently selected configuration

### Removed Components

**ConfigCanvas.vue** (Removed - commit e266628)
- **Reason:** Coordinate system mismatch with PropertyCanvas
- **Functionality:** Merged into PropertyCanvas
- **Files Affected:**
  - Deleted: `src/components/ConfigCanvas.vue`
  - Modified: `src/components/PropertyCanvas.vue` (integrated ConfigCanvas logic)
  - Modified: `src/views/PropertyQuadrantsView.vue` (removed ConfigCanvas reference)

### Navigation Flow

```
PropertyQuadrantsView
  ↓ User clicks category bubble
PropertyCanvas updates → configs appear
  ↓ User clicks config bubble
selectConfiguration(config)
  ↓
router.push(`/pipeline-execution/${config.id}`)
  ↓
PipelineExecutionView (config loaded, ready for prompt input)
```

### Known Issues & Solutions

**Issue 1: Config Bubbles Appearing Top-Right (RESOLVED)**
- **Cause:** Separate PropertyCanvas + ConfigCanvas components with different coordinate systems
- **Solution:** Merged into unified PropertyCanvas with single coordinate system (commit e266628)

**Issue 2: Centering Problems (ACTIVE - See `docs/PropertyCanvas_Problem.md`)**
- **Status:** Under investigation
- **Problem:** Category bubbles not perfectly centered in viewport
- **Affected File:** `PropertyCanvas.vue` positioning logic

### File Structure

```
public/ai4artsed-frontend/
├── src/
│   ├── components/
│   │   ├── PropertyCanvas.vue        # Unified canvas (categories + configs)
│   │   ├── PropertyBubble.vue        # Individual category bubble
│   │   ├── ConfigTile.vue            # Grid view config tile (alternative UI)
│   │   └── PropertyBubble.vue.archive # Backup of previous version
│   ├── views/
│   │   ├── PropertyQuadrantsView.vue # Main selection view
│   │   └── PropertyQuadrantsView.vue.archive # Backup of previous version
│   ├── stores/
│   │   ├── configSelection.ts        # Config selection state
│   │   └── userPreferences.ts        # Language & preferences
│   ├── assets/
│   │   └── main.css                  # Global styles
│   └── router/
│       └── index.ts                  # Vue Router config
└── public/
    └── config-previews/              # Config preview images
        ├── bauhaus.png
        ├── dada.png
        └── ...
```

### Testing Checklist (Vue Frontend)

When testing PropertyCanvas changes:

- [ ] All 5 category bubbles display correctly in X-formation
- [ ] Freestyle bubble centered in viewport
- [ ] Category selection works (XOR: only one selected)
- [ ] Config bubbles appear only when category selected
- [ ] Config bubbles positioned correctly around selected category
- [ ] Config preview images load correctly
- [ ] Text badges display config names
- [ ] Config selection navigates to pipeline execution
- [ ] Touch events work on iPad
- [ ] Responsive sizing works across viewport sizes
- [ ] "Clear Selection" button appears/disappears correctly

---

## Frontend API Patterns

### ⚠️ CRITICAL: Pipeline API Usage

#### Rule 1: Always Use Config ID for Schema Parameter

When calling pipeline endpoints (`/pipeline/stage2`, `/pipeline/execute`, `/pipeline/stage3-4`), the `schema` parameter must be the **config ID**, never the pipeline name.

**Correct Pattern:**
```typescript
// Phase 2 Youth Flow - runInterception()
const response = await axios.post('/api/schema/pipeline/stage2', {
  schema: pipelineStore.selectedConfig?.id || 'overdrive',  // ✅ Config ID
  input_text: inputText.value,
  context_prompt: contextPrompt.value || undefined,
  user_language: 'de',
  execution_mode: 'eco',
  safety_level: 'youth',
  output_config: selectedConfig.value
})

// Phase 2 Youth Flow - executePipeline()
const response = await axios.post('/api/schema/pipeline/execute', {
  schema: pipelineStore.selectedConfig?.id || 'overdrive',  // ✅ Config ID
  input_text: inputText.value,
  interception_result: interceptionResult.value,
  context_prompt: contextPrompt.value || undefined,
  user_language: 'de',
  execution_mode: 'eco',
  safety_level: 'youth',
  output_config: selectedConfig.value
})
```

**Wrong Pattern (NEVER DO THIS):**
```typescript
// ❌ WRONG - Using pipeline name instead of config ID
schema: pipelineStore.selectedConfig?.pipeline  // Causes 404 error!
```

**Why This Matters:**

1. **Config Structure:**
   ```json
   {
     "id": "bauhaus",                     // ← Use for 'schema' parameter
     "pipeline": "text_transformation",   // ← NEVER use for 'schema'
     "version": "1.0",
     "category": "artistic"
   }
   ```

2. **Backend File Loading:**
   - Backend uses `schema` to load: `schemas/configs/{schema}.json`
   - Example: `schema: "bauhaus"` → Loads `bauhaus.json` ✅
   - Example: `schema: "text_transformation"` → Looks for `text_transformation.json` (doesn't exist) → 404 ❌

3. **Silent Failure:**
   - Error appears in browser console
   - Backend logs show nothing (request never reaches route handler)
   - FastAPI returns 404 before route execution

**Debugging Clue:** If you see 404 errors in browser console but backend logs are silent, suspect wrong `schema` parameter value.

**Bug History:** Session 64 Part 4 (2025-11-23) - Youth Flow sent `config.pipeline` instead of `config.id`, causing production-breaking 404 errors. Nearly forced complete revert of Session 64 refactoring.

**Affected Files:**
- `/public/ai4artsed-frontend/src/views/Phase2YouthFlowView.vue` (lines 403, 460) - FIXED ✅
- `/public/ai4artsed-frontend/src/views/PipelineExecutionView.vue` (line 250) - Already correct ✅
- All future views making pipeline API calls

**Code Review Checklist:**
- [ ] All `schema:` parameters use `pipelineStore.selectedConfig?.id`
- [ ] No `schema:` parameters use `pipelineStore.selectedConfig?.pipeline`
- [ ] Fallback values use valid config IDs (e.g., `'overdrive'`)

---

