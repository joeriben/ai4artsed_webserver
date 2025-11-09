# Frontend Architecture Documentation Series

**Created:** 2025-11-06
**Status:** Planning Documents
**Purpose:** Complete frontend architecture specification for AI4ArtsEd DevServer Vue.js rebuild

---

## Document Series Overview

This directory contains a **6-part documentation series** that systematizes and details the complete frontend architecture for the AI4ArtsEd DevServer. These documents were created to plan the Vue.js frontend rebuild with a 3-phase user experience model.

---

## Reading Order

### 1️⃣ [FRONTEND_01_ARCHITECTURE_OVERVIEW.md](./FRONTEND_01_ARCHITECTURE_OVERVIEW.md)

**Summary:** High-level overview of the entire frontend architecture

**Key Topics:**
- 3-phase model (Selection → Flow Experience)
- Technology stack (Vue.js, Pinia, TypeScript)
- Metadata-driven, config-agnostic design principles
- State management strategy
- Real-time polling architecture
- Backend API integration overview

**Read First:** Start here to understand the overall structure

**Word Count:** ~5,000 words

---

### 2️⃣ [FRONTEND_02_PHASE_1_SCHEMA_SELECTION.md](./FRONTEND_02_PHASE_1_SCHEMA_SELECTION.md)

**Summary:** Detailed specification for Phase 1 (Schema-Config Selection Interface)

**Key Topics:**
- Three full-screen visualization modes:
  - Mode A: Arranged Tiles (grid view)
  - Mode B: List View (table view)
  - Mode C: LLM-Assisted Dialog (conversational selection)
- Icon-based mode switching
- DX7-style flowchart symbolization (auxiliary icons)
- Search, filter, categorization patterns
- User config integration and management
- Execution parameter selection (eco/fast, kids/youth)

**Prerequisites:** Read FRONTEND_01 first

**Word Count:** ~10,000 words

---

### 3️⃣ [FRONTEND_03_PHASE_2_3_FLOW_EXPERIENCE.md](./FRONTEND_03_PHASE_2_3_FLOW_EXPERIENCE.md)

**Summary:** Detailed specification for Phase 2+3 (Combined Flow Experience)

**Key Topics:**
- Unified flow experience (prompt input → execution → output)
- Box-and-connection visualization (4-stage pipeline)
- Prompt positioning indicators
- Real-time status polling (1-second intervals)
- Entity timeline view (all intermediate outputs)
- Media output display:
  - Image output (PNG/JPG)
  - Audio output (MP3/WAV)
  - Music output (dual-input configs)
  - Text output (transformations)
- Error handling and safety blocks

**Prerequisites:** Read FRONTEND_01 and FRONTEND_02 first

**Word Count:** ~12,000 words

---

### 4️⃣ [FRONTEND_04_VUE_COMPONENT_ARCHITECTURE.md](./FRONTEND_04_VUE_COMPONENT_ARCHITECTURE.md)

**Summary:** Technical specification for Vue.js component structure

**Key Topics:**
- Complete component hierarchy
- Project file structure
- Phase 1 components (ConfigBrowser, TileView, ListView, etc.)
- Phase 2+3 components (PipelineFlow, StageBox, EntityTimeline, etc.)
- Pinia state stores:
  - configStore (config metadata and selection)
  - pipelineStore (execution state)
  - userStore (user preferences)
- Composables (usePipelinePolling, useMediaPlayer, etc.)
- Vue Router configuration
- TypeScript type definitions
- Testing strategy (unit, integration, E2E)

**Prerequisites:** Read FRONTEND_01-03 for context

**Word Count:** ~8,000 words

---

### 5️⃣ [FRONTEND_05_METADATA_SCHEMA_SPECIFICATION.md](./FRONTEND_05_METADATA_SCHEMA_SPECIFICATION.md)

**Summary:** Complete specification for config metadata structure

**Key Topics:**
- Required metadata fields (8 fields):
  - id, name, description, category, icon, difficulty, output_types, pipeline
- Optional metadata fields (15+ fields):
  - tags, author, version, example_inputs, estimated_time, flowchart, etc.
- Validation rules (backend + frontend)
- API endpoint specification (`/pipeline_configs_metadata`)
- User config creation workflow
- Example configs (minimal, full-featured, user)
- Migration and versioning strategy

**Prerequisites:** Read FRONTEND_01-02 for context

**Word Count:** ~7,000 words

---

### 6️⃣ [FRONTEND_06_VISUAL_DESIGN_PATTERNS.md](./FRONTEND_06_VISUAL_DESIGN_PATTERNS.md)

**Summary:** Complete visual design language specification

**Key Topics:**
- Color system:
  - Primary/secondary colors
  - Semantic colors (success, error, warning)
  - Status colors (pending, in-progress, completed)
  - Category colors (art-movements, media-generation, etc.)
- Typography:
  - Font families (Inter, Poppins)
  - Type scale (modular 1.250)
  - Font weights and line heights
- Spacing system (8px base unit)
- Component styles:
  - Config cards (tile view)
  - Stage boxes (Phase 2+3)
  - Connection lines (animated flow)
  - Buttons, modals, forms
- DX7-inspired flowchart SVG implementations:
  - Linear flow
  - Recursive loop
  - Branching (parallel paths)
  - Complex (custom)
- Animation guidelines
- Responsive design patterns
- Accessibility (WCAG 2.1 AA compliance)

**Prerequisites:** Read FRONTEND_01-04 for context

**Word Count:** ~9,000 words

---

## Total Documentation

- **6 comprehensive documents**
- **~51,000 words total**
- **Complete frontend specification**

---

## Key Concepts

### 3-Phase User Journey

```
Phase 1: Selection
  ↓
  User selects schema-config + execution params
  ↓
Phase 2+3: Flow Experience (Combined)
  ↓
  Prompt Input → Pipeline Execution (4 stages) → Media Output
```

### Metadata-Driven Design

- **No hardcoded config lists** in frontend
- Configs expose metadata via API
- Frontend dynamically renders based on metadata
- New configs appear automatically
- User configs integrate seamlessly

### 4-Stage Pipeline

```
Stage 1: Pre-Processing (Translation + Safety)
  ↓
Stage 2: Interception (Text Transformation)
  ↓
Stage 3: Pre-Output Safety Check
  ↓
Stage 4: Media Generation (Image/Audio/Music)
```

### Real-Time Updates

- Status polling every 1 second
- Progressive entity display
- Live stage progress tracking
- Animated connection lines showing data flow

---

## Technology Stack

**Frontend Framework:**
- Vue.js 3 (Composition API)
- TypeScript (type safety)
- Pinia (state management)
- Vue Router (navigation)

**Build Tools:**
- Vite (bundler)
- Vitest (unit testing)
- Playwright/Cypress (E2E testing)

**Backend API:**
- Existing Python/Flask backend
- RESTful API endpoints
- Real-time status polling (no WebSocket required)

---

## Design Principles

1. **Clarity Over Decoration:** Information hierarchy is paramount
2. **Educational Focus:** Designs support learning, not just task completion
3. **Accessible by Default:** WCAG 2.1 AA compliance minimum
4. **Playful but Professional:** Engaging for students, credible for educators
5. **Metadata-Driven:** Visuals adapt dynamically to config metadata
6. **Extensible:** System grows without code changes (add configs dynamically)

---

## Implementation Status

**Status:** 📋 **Planning Complete** → Ready for implementation

**Next Steps:**
1. Review documentation with team
2. Create design mockups (Figma/Sketch)
3. Set up Vue.js project structure
4. Implement Phase 1 MVP (Tile view only)
5. Implement Phase 2+3 MVP (Basic pipeline flow)
6. Iterate and expand features

**Estimated Timeline:**
- MVP (Phases 1-3 basic): 2-3 weeks
- V1.0 (Full features): 6-8 weeks
- V2.0 (Polish + enhancements): 10-12 weeks

---

## Related Documentation

**Backend Architecture:**
- `/docs/README.md` - System overview
- `/docs/ARCHITECTURE PART 01 - 4-Stage Orchestration Flow.md`
- `/docs/ARCHITECTURE PART 11 - API-Routes.md`
- `/docs/LIVE_PIPELINE_RECORDER.md`

**Session Documentation:**
- `/docs/SESSION_32_SUMMARY.md` - Latest session (system validation)

---

## Questions & Decisions

**Open Questions (Documented):**
1. LLM Mode implementation (local vs cloud vs rule-based)
2. User config storage location (filesystem vs database)
3. Config icon strategy (emoji vs SVG vs generated)
4. State persistence (localStorage vs session)

**Decisions Made:**
1. ✅ Phase 2+3 combined (not separate)
2. ✅ Three visualization modes in Phase 1 (all switchable)
3. ✅ DX7 flowcharts as auxiliary symbolization (not primary)
4. ✅ Metadata-driven, config-agnostic design
5. ✅ Vue.js 3 with Composition API + TypeScript

---

## Changelog

**2025-11-06:**
- Initial documentation series created
- All 6 documents completed
- Series renamed with numbered prefix for clarity

---

## Contact & Contribution

**Questions?** See individual documents for detailed specifications

**Feedback?** Update documents as requirements evolve

**Implementation?** Follow reading order above for complete understanding

---

**Document Status:** ✅ Complete Planning Documentation
**Ready for:** Design mockups → Implementation → Testing
**Maintained by:** AI4ArtsEd Team
