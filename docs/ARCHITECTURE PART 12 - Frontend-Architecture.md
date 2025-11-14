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

