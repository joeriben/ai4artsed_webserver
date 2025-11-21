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

