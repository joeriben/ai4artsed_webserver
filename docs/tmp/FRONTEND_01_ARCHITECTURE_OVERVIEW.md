# Frontend Architecture Overview - AI4ArtsEd DevServer

**Version:** 1.0
**Date:** 2025-11-06
**Status:** Planning Document
**Target Technology:** Vue.js

---

## Executive Summary

The AI4ArtsEd DevServer frontend is organized into **three distinct phases** that guide users from schema selection through prompt creation to pipeline execution and media output. The architecture is **metadata-driven** and **config-agnostic**, supporting dynamic addition/removal of system and user-created configurations without requiring frontend code changes.

### Core Design Principles

1. **Metadata-Driven UI**: All display elements driven by config metadata (icons, categories, descriptions)
2. **Phase-Based Navigation**: Clear progression through Selection → Execution → Output
3. **Real-Time Feedback**: Live status updates during 4-stage pipeline execution
4. **Backend Abstraction**: No direct access to ComfyUI/Ollama/OpenRouter - fully API-driven
5. **Extensibility**: User configs integrate seamlessly with system configs

---

## Three-Phase Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: SELECTION                       │
│                  (Schema-Config Choice)                     │
│                                                             │
│  Mode A: Tiles    Mode B: Lists    Mode C: LLM Dialog     │
│  [Icon Switch] ←→ [Icon Switch] ←→ [Icon Switch]          │
│                                                             │
│  ↓ User selects config + execution parameters              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              PHASE 2+3: FLOW EXPERIENCE                     │
│        (Prompt Input + Execution + Output)                  │
│                                                             │
│  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐            │
│  │Stage1│ ─→ │Stage2│ ─→ │Stage3│ ─→ │Stage4│            │
│  │Pre   │    │Inter │    │Safety│    │Media │            │
│  │Proc  │    │cept  │    │Check │    │Gen   │            │
│  └──────┘    └──────┘    └──────┘    └──────┘            │
│                                                             │
│  • Real-time progress tracking                              │
│  • Box-and-connection visualization                         │
│  • Entity timeline (translation, interception, media)       │
│  • Live status polling                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Schema Selection

**Purpose:** Allow users to discover and select the appropriate schema-config for their creative intent.

**Key Features:**
- Three full-screen visualization modes (user-switchable via icons)
- Dynamic loading from `/pipeline_configs_metadata` API endpoint
- Support for both system and user-created configs
- Metadata-driven display (no hardcoded config lists)
- Search, filter, categorization capabilities

**Outputs:**
- Selected `config_id`
- User-specified `execution_mode` (eco/fast)
- User-specified `safety_level` (kids/youth)

**See:** `PHASE_1_SCHEMA_SELECTION.md` for detailed specification

---

## Phase 2+3: Flow Experience (Combined)

**Purpose:** Unified experience for prompt input, pipeline execution monitoring, and media output viewing.

**Why Combined?**
Phases 2 and 3 are tightly coupled in user experience:
- Prompt input determines pipeline flow
- Pipeline execution is visualized in real-time
- Output emerges progressively as stages complete
- User sees **where** their prompt sits in the flow and **where** interception happens

**Key Features:**
- Box-and-connection visualization of 4-stage pipeline
- Prompt positioning indicators (user input, interception prompts)
- Real-time status polling (1-second intervals)
- Entity timeline view (01_input.txt, 02_translation.txt, etc.)
- Progressive media display as available

**Backend Integration:**
- `POST /api/schema/pipeline/execute` (initiate)
- `GET /api/pipeline/{run_id}/status` (poll)
- `GET /api/pipeline/{run_id}/entities` (track outputs)
- `GET /api/pipeline/{run_id}/entity/{type}` (fetch entity)

**See:** `PHASE_2_3_FLOW_EXPERIENCE.md` for detailed specification

---

## Technology Stack

### Frontend Framework: Vue.js

**Rationale:**
- Component-based architecture matches phase structure
- Reactive data binding ideal for real-time status updates
- Vue Router supports phase navigation
- Vuex/Pinia for cross-phase state management
- Strong TypeScript support for type safety

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│           Vue Application Layer                 │
│  • Router (Phase 1 ↔ Phase 2+3)                │
│  • State Management (selected config, run_id)  │
│  • API Service (backend abstraction)           │
└─────────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────────┐
│          Component Layer                        │
│  Phase 1:                                       │
│    • ConfigBrowser (parent)                     │
│    • TileView / ListView / LLMDialogView        │
│    • ConfigCard / ConfigRow                     │
│  Phase 2+3:                                     │
│    • PipelineFlow (parent)                      │
│    • StageBox / ConnectionLine                  │
│    • EntityTimeline / MediaPlayer               │
└─────────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────────┐
│          Backend API Layer                      │
│  • /pipeline_configs_metadata (Phase 1)        │
│  • /api/schema/pipeline/execute (Phase 2+3)    │
│  • /api/pipeline/{run_id}/status (polling)     │
│  • /api/pipeline/{run_id}/entity/{type}        │
└─────────────────────────────────────────────────┘
```

---

## Metadata-Driven Design

### Config Metadata Structure

All UI elements in Phase 1 are driven by config metadata returned from API:

```json
{
  "id": "dada",
  "name": "Dada Transformation",
  "description": "Transform text using Dada art movement principles",
  "category": "art-movements",
  "icon": "🎨",
  "difficulty": 2,
  "tags": ["text", "transformation", "experimental"],
  "input_requirements": { "type": "text", "max_length": 500 },
  "output_types": ["text"],
  "pipeline": "text_transformation",
  "is_user_config": false
}
```

### Dynamic Rendering

**Key Principle:** Frontend NEVER hardcodes config lists. All configs discovered at runtime.

**Benefits:**
- Add new configs → Automatically appear in Phase 1
- Remove configs → Automatically disappear
- User configs → Integrate seamlessly
- Category changes → UI adapts automatically

**Implementation:**
```javascript
// Vue Component (Tile View Example)
async mounted() {
  const response = await api.get('/pipeline_configs_metadata');
  this.configs = response.data.configs;
  this.categories = this.groupByCategory(this.configs);
}
```

---

## State Management Strategy

### Phase Transitions

```
Phase 1 State:
  • availableConfigs: Config[]
  • selectedConfig: Config | null
  • executionMode: 'eco' | 'fast'
  • safetyLevel: 'kids' | 'youth'
  • visualizationMode: 'tiles' | 'list' | 'llm'

Phase 2+3 State:
  • runId: string | null
  • currentStage: 1-4
  • currentStep: string
  • progress: string (e.g., "3/8")
  • entities: Entity[]
  • pipelineStatus: 'running' | 'completed' | 'error'
  • executionStartTime: Date
```

### Data Flow

```
User Action (Phase 1)
  → Select Config
  → Store in Vuex/Pinia
  → Navigate to Phase 2+3
  → Use stored config for execution
  → Store run_id after execution starts
  → Poll status using run_id
  → Update Phase 2+3 UI in real-time
```

---

## Backend API Integration

### Phase 1 Endpoints

```
GET /pipeline_configs_metadata
→ Returns: { configs: Config[] }
→ Used by: All Phase 1 visualization modes
→ Frequency: On mount + refresh
```

### Phase 2+3 Endpoints

```
POST /api/schema/pipeline/execute
Body: {
  schema: string,
  input_text: string,
  execution_mode: 'eco' | 'fast',
  safety_level: 'kids' | 'youth'
}
→ Returns: { status, run_id, final_output, execution_time }
→ Used by: Pipeline execution trigger

GET /api/pipeline/{run_id}/status
→ Returns: { status, current_state, elapsed_time, entities }
→ Used by: Real-time polling (1-second intervals)

GET /api/pipeline/{run_id}/entities
→ Returns: { entities: Entity[] }
→ Used by: Entity timeline display

GET /api/pipeline/{run_id}/entity/{type}
→ Returns: File content (text, JSON, image binary)
→ Used by: Entity viewing, media display
```

---

## User Config Integration

### System vs User Configs

**System Configs:**
- Located in `/devserver/schemas/configs/`
- Curated, stable, well-tested
- Installed with application

**User Configs:**
- Created by users via UI or file upload
- Stored in user-specific location (TBD)
- Marked with `is_user_config: true` in metadata
- Can be shared, exported, imported

### Phase 1 Integration

**Visual Differentiation:**
- User configs show badge/indicator
- Optional filtering: "Show only my configs"
- User configs appear in same visualization modes (tiles/list/LLM)

**Management Actions:**
- Edit user config
- Delete user config
- Export/share user config
- Duplicate system config to create user variant

---

## Real-Time Updates Strategy

### Polling Architecture

**Phase 2+3 Polling Pattern:**
```javascript
async startPolling(runId) {
  this.pollInterval = setInterval(async () => {
    const status = await api.get(`/api/pipeline/${runId}/status`);

    this.currentStage = status.current_state.stage;
    this.currentStep = status.current_state.step;
    this.progress = status.current_state.progress;
    this.entities = status.entities;

    if (status.status === 'completed' || status.status === 'error') {
      this.stopPolling();
    }
  }, 1000); // Poll every 1 second
}
```

**Benefits:**
- Simple implementation (no WebSocket complexity)
- Backend already provides status endpoint
- Graceful degradation (missed poll = 1 second delay)
- Easy to implement progress bars, spinners

**Future Enhancement:**
- Consider Server-Sent Events (SSE) for lower latency
- Backend already has SSE infrastructure (`sse-connection.js`)

---

## Visual Design Philosophy

### DX7-Inspired Symbolization

**Context:** Yamaha DX7 synthesizer used algorithm diagrams to show signal flow.

**Application:** Use simplified flowchart symbols as **auxiliary icons** for schema-configs:

```
Example: "dada" config icon
┌─────────┐
│ Input   │
└────┬────┘
     │
┌────▼────┐
│ Dada    │  ← Stylized transformation box
│ Trans   │
└────┬────┘
     │
┌────▼────┐
│ Output  │
└─────────┘
```

**Usage:**
- NOT for primary navigation (too complex)
- AS visual symbolization in tiles/cards
- AS differentiation between pipeline types
- AS "preview" of what happens in Phase 2+3

### Box-and-Connection Language

**Phase 2+3 Visualization:**
- Each stage = distinct box with color/icon
- Connections = animated lines showing progress
- Active stage = highlighted, pulsing
- Completed stages = checkmark, subdued color
- Failed stages = error icon, red highlight

---

## Responsive Design Considerations

### Desktop-First Approach

**Rationale:**
- Complex visualizations require screen real estate
- Educational/pedagogical use case (classroom computers)
- Admin/teacher workflows desktop-heavy

**Breakpoints:**
```
Desktop:  1920px+ (primary target)
Laptop:   1280px+ (full features)
Tablet:   768px+  (adapted layouts)
Mobile:   <768px  (simplified, future consideration)
```

### Phase-Specific Adaptations

**Phase 1:**
- Desktop: 3-4 column tile grid, side-by-side list
- Laptop: 2-3 column tile grid
- Tablet: 2 column tile grid, vertical list

**Phase 2+3:**
- Desktop: Horizontal stage flow (left-to-right)
- Laptop: Horizontal stage flow (compact)
- Tablet: Vertical stage flow (top-to-bottom)

---

## Accessibility Considerations

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Stage boxes: minimum 4.5:1 contrast ratio
- Icon-only mode switchers: include text labels + ARIA

**Keyboard Navigation:**
- Phase 1: Arrow keys to navigate tiles/list
- Tab navigation through all interactive elements
- Enter/Space to select config

**Screen Readers:**
- ARIA labels for all icons
- Status updates announced via `aria-live` regions
- Progress descriptions (not just visual)

**Motion Sensitivity:**
- `prefers-reduced-motion` media query
- Disable box pulsing, line animations if preferred

---

## Performance Considerations

### Lazy Loading

**Phase 1:**
- Load config metadata eagerly (small payload)
- Lazy load config icons/images
- Virtual scrolling for large config lists (100+ configs)

**Phase 2+3:**
- Load media entities on-demand (images can be large)
- Progressive image loading (blur-up technique)
- Cache entity fetches (avoid re-fetching unchanged entities)

### Bundle Optimization

```
Phase 1 Bundle: ~150KB (config browser, mode switchers)
Phase 2+3 Bundle: ~250KB (pipeline flow, media players)
Shared Bundle: ~100KB (API service, state management)

Code Splitting: Load Phase 2+3 only after config selection
```

---

## Security Considerations

### User Config Validation

**Frontend Validation:**
- Schema validation before submission
- File size limits (prevent abuse)
- Content-type verification (image/audio uploads)

**Backend Responsibility:**
- Sanitize all user-provided config fields
- Validate pipeline references exist
- Rate limiting on config creation

### XSS Prevention

**User-Generated Content:**
- Config names/descriptions rendered as text (not HTML)
- Use Vue's default escaping (v-text, not v-html)
- Sanitize markdown if description supports formatting

---

## Error Handling Strategy

### Phase 1 Errors

**Config Loading Failure:**
```
Error: "Unable to load available schemas. Please refresh."
Action: Retry button, fallback to cached configs
```

**Empty Config List:**
```
Message: "No schemas available. Contact administrator."
Action: Show support contact info
```

### Phase 2+3 Errors

**Execution Failure:**
```
Error: "Pipeline execution failed at Stage 2: [reason]"
Action: Show detailed error, offer retry, return to Phase 1
```

**Polling Timeout:**
```
Error: "Lost connection to pipeline status. Reconnecting..."
Action: Exponential backoff, manual refresh option
```

**Media Generation Failure:**
```
Message: "Media could not be generated. Text output available."
Action: Show text output, hide media player, log error
```

---

## Testing Strategy

### Unit Tests

**Phase 1 Components:**
- Config card rendering from metadata
- Mode switching logic
- Search/filter functionality
- Config selection state management

**Phase 2+3 Components:**
- Stage box status updates
- Entity timeline rendering
- Polling start/stop logic
- Media player error handling

### Integration Tests

**API Integration:**
- Mock `/pipeline_configs_metadata` responses
- Mock `/api/schema/pipeline/execute` responses
- Test polling behavior with mocked status updates
- Test error response handling

### E2E Tests

**User Flows:**
1. Load Phase 1 → Select config → Navigate to Phase 2+3
2. Execute pipeline → Poll status → View media output
3. Switch Phase 1 modes → Select config from each mode
4. Handle execution errors → Return to Phase 1
5. Create user config → See it appear in Phase 1

---

## Development Roadmap

### MVP (Minimum Viable Product)

**Phase 1:**
- Mode A (Tiles) only
- Basic metadata display (icon, name, description)
- Config selection → navigate to Phase 2+3

**Phase 2+3:**
- Basic 4-stage box visualization
- Text status updates (no fancy animations)
- Media display (image only, basic player)

### V1.0 (Full Feature Set)

**Phase 1:**
- All three modes (Tiles, List, LLM Dialog)
- Mode switching icons
- Search/filter/categorization
- User config integration

**Phase 2+3:**
- Full box-and-connection visualization
- Entity timeline view
- Advanced media player (image, audio, video)
- Prompt positioning indicators
- Export/share functionality

### Future Enhancements

- User config editor (in-app creation)
- Collaborative sharing (share run results)
- History view (past executions)
- Admin dashboard (system monitoring)
- Multi-language i18n (beyond German/English)

---

## Related Documentation

**Phase-Specific:**
- `PHASE_1_SCHEMA_SELECTION.md` - Detailed Phase 1 specification
- `PHASE_2_3_FLOW_EXPERIENCE.md` - Detailed Phase 2+3 specification

**Technical:**
- `VUE_COMPONENT_ARCHITECTURE.md` - Component hierarchy and structure
- `METADATA_SCHEMA_SPECIFICATION.md` - Config metadata requirements
- `VISUAL_DESIGN_PATTERNS.md` - Visual design language and wireframes

**Backend Integration:**
- `/docs/ARCHITECTURE PART 11 - API-Routes.md` - Complete API documentation
- `/docs/LIVE_PIPELINE_RECORDER.md` - Real-time status tracking system
- `/docs/README.md` - System overview and quick start

---

## Questions for Implementation Phase

### To Be Decided:

1. **User Config Storage:**
   - File system location for user configs?
   - Database vs file-based storage?
   - Per-user directories or single shared location?

2. **LLM Dialog Mode (Phase 1 Mode C):**
   - Which LLM to use for config recommendation?
   - Hosted locally or API-based?
   - Prompt engineering strategy?

3. **State Management:**
   - Vuex vs Pinia vs Composition API only?
   - Persist state to localStorage?
   - Handle browser refresh during execution?

4. **Build/Deploy:**
   - Standalone SPA or integrated with backend?
   - Build output location (`/public/` vs `/public_dev/`)?
   - Development proxy configuration?

---

**Document Status:** ✅ Planning Complete
**Next Steps:** Review with team → Begin component specification
**Target Start Date:** TBD
**Estimated Timeline:** MVP (2-3 weeks) → V1.0 (6-8 weeks)
