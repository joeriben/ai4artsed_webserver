# DevServer Architecture

**Part 12: Frontend Architecture**

---


### Overview

**Status:** ✅ Complete migration (2025-10-28)
**Architecture:** 100% Backend-abstracted - Frontend NEVER accesses ComfyUI directly

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
  → initSSEConnection()
```

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

### Legacy Components (Obsolete)

These files are marked `.obsolete` and no longer used:

- ❌ `workflow.js.obsolete` - Dropdown-based config selection
- ❌ `workflow-classifier.js.obsolete` - Runtime workflow classification
- ❌ `workflow-browser.js.obsolete` - Incomplete migration attempt
- ❌ `workflow-streaming.js.obsolete` - Legacy API with direct ComfyUI access
- ❌ `dual-input-handler.js.obsolete` - Replaced by execution-handler

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

