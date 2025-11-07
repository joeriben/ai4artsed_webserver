# Phase 2+3: Creative Input & Process Transparency

**Version:** 2.0
**Date:** 2025-11-06
**Status:** Planning Document - REVISED
**Parent:** FRONTEND_ARCHITECTURE_OVERVIEW.md

---

## Executive Summary - REVISED

Phase 2+3 has **two distinct pedagogical functions** that require different visualizations:

**Phase 2 - Creative Act:**
- User prompt input
- Meta-prompt conceptualization
- The creative/artistic intention

**Phase 3 - AI Process Transparency:**
- Shows EVERY step of the AI system's work
- Educational goal: Make AI decision-making visible
- Children/Youth see how prompts flow through transformations
- **Box per Entity** (not per Stage!) - everything that appears in `exports/json` gets a box

### Why This Matters Pedagogically

**Against Black-Box-Solutionism:**
- AI tools should not hide their process
- Students understand AI as a series of transformations, not magic
- Every intermediate step is visible and inspectable

**For Process-Based Learning:**
- See input → translation → safety → interception → output
- Understand how meta-prompts modify input prompts
- Recursive processes become visible (8 iterations of Stillepost visible)

---

## Phase 2: Creative Input Interface

### Purpose

Allow users to enter their creative input (prompt) that will flow through the system.

### Visual Structure

```
┌──────────────────────────────────────────────────────────┐
│  Phase 2: Your Creative Input                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Config: 🎨 Dada Transformation                         │
│  Mode: Fast  │  Safety: Kids                            │
│                                                          │
│  ─────────────────────────────────────────────────────── │
│                                                          │
│  Enter your prompt:                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │                                                    │  │
│  │  A beautiful flower in a sunny meadow             │  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Character count: 37 / 500                               │
│                                                          │
│  Example prompts:                                        │
│  • "A surreal landscape with floating islands"          │
│  • "An astronaut riding a bicycle through space"        │
│  • "A cozy cabin in a snowy forest at twilight"         │
│                                                          │
│  [Execute Pipeline →]                                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Key Elements

- **Config Summary:** Reminder of selected config
- **Execution Parameters:** Visible but not editable (set in Phase 1)
- **Prompt Input:** Large text area, character count
- **Example Prompts:** Clickable to auto-fill
- **Execute Button:** Starts Phase 3

---

## Phase 3: AI Process Transparency

### Purpose

**Educational Transparency:** Show every step of the AI system's processing pipeline as distinct, inspectable boxes.

### Core Principle: Entity-Based Visualization

**NOT Stage-Based (4 boxes), but Entity-Based (one box per `exports/json` file):**

```
Every file that ends up in exports/{run_id}/json/ gets a box:
- 01_input.txt
- 02_translation.txt
- 03_safety_stage1.json
- 04_interception_context.txt (meta-prompt)
- 05_interception_result.txt
- 06_safety_pre_output.json
- 07_output_image.png
... and so on
```

### Visual Structure: Entity Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Phase 3: AI Process Transparency                                        │
│  Pipeline Execution: Dada Transformation                                 │
│  Status: Running  │  Elapsed: 00:23                                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│  │ 01_input.txt    │ →  │ 02_translation  │ →  │ 03_safety       │    │
│  │                 │    │      .txt       │    │    _stage1.json │    │
│  │ "Eine Blume..." │    │ "A flower..."   │    │ ✓ SAFE          │    │
│  │                 │    │                 │    │                 │    │
│  │ ✓ Available     │    │ ✓ Available     │    │ ✓ Available     │    │
│  │ [View]          │    │ [View]          │    │ [View]          │    │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐                            │
│  │ 04_interception │ →  │ 05_interception │                            │
│  │    _context.txt │    │    _result.txt  │                            │
│  │                 │    │                 │                            │
│  │ Meta-Prompt:    │    │ "Flower-chaos   │                            │
│  │ "Transform with │    │  meadow-umbrella│                            │
│  │  Dada..."       │    │  contradiction!"│                            │
│  │                 │    │                 │                            │
│  │ ✓ Available     │    │ ⟳ In Progress   │                            │
│  │ [View]          │    │ [View Partial]  │                            │
│  └─────────────────┘    └─────────────────┘                            │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐                            │
│  │ 06_safety_pre   │ →  │ 07_output       │                            │
│  │    _output.json │    │    _image.png   │                            │
│  │                 │    │                 │                            │
│  │ ○ Pending       │    │ ○ Pending       │                            │
│  └─────────────────┘    └─────────────────┘                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Entity Box Structure

Each entity (file in `exports/json`) gets a box:

```
┌─────────────────────┐
│ Filename            │  ← Entity filename
│ (e.g. 02_translation│
│      .txt)          │
├─────────────────────┤
│                     │
│ Content Preview     │  ← First 50 chars or summary
│ "A flower in..."    │
│                     │
├─────────────────────┤
│ Status: ✓/⟳/○      │  ← Available / In Progress / Pending
│ [View] [Download]   │  ← Actions
└─────────────────────┘
```

### Status Icons

- **✓ Available:** Entity exists and can be viewed
- **⟳ In Progress:** Currently being generated
- **○ Pending:** Not yet started

### Recursive Pipelines Visualization

**Example: Stillepost (8 iterations)**

Each iteration appears as separate entity:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│04_intercept  │ →  │04_intercept  │ →  │04_intercept  │ → ...
│  _iter1.txt  │    │  _iter2.txt  │    │  _iter3.txt  │
│              │    │              │    │              │
│"flower..."   │    │"meadow..."   │    │"echo..."     │
│✓ Available   │    │✓ Available   │    │⟳ In Progress │
│[View]        │    │[View]        │    │[View Partial]│
└──────────────┘    └──────────────┘    └──────────────┘

... continuing to iteration 8
```

**Pedagogical Value:**
- Students see how prompt degrades/transforms through iterations
- "Stille Post" (telephone game) metaphor becomes visible
- Each step is inspectable

### Meta-Prompt Visibility

**Special Case: Interception Context**

Show how meta-prompt connects input and output:

```
┌─────────────────────────────────────────────────────┐
│  Interception Process                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Input Prompt (from 02_translation.txt):           │
│  "A beautiful flower in a sunny meadow"            │
│                                                     │
│  ↓ Combined with                                    │
│                                                     │
│  Meta-Prompt (from 04_interception_context.txt):   │
│  "Transform the following text using Dada art      │
│   movement principles: create nonsensical word     │
│   combinations that challenge conventional         │
│   meaning..."                                       │
│                                                     │
│  ↓ Results in                                       │
│                                                     │
│  Interception Output (05_interception_result.txt): │
│  "Meadow-flower-chaos umbrella contradiction       │
│   spiral absurd!"                                   │
│                                                     │
│  [View Full Prompt Chain]                           │
└─────────────────────────────────────────────────────┘
```

**Pedagogical Value:**
- Students understand HOW AI combines prompts
- Meta-prompts are not hidden but explained
- The "instruction + content" pattern becomes clear

---

## Dynamic Entity Loading

### Progressive Display

As pipeline executes, entities appear sequentially:

**Time 0s:** Execute button clicked
```
[01_input.txt] ⟳ → [○] → [○] → [○]
```

**Time 2s:** Input captured, translation starting
```
[01_input.txt] ✓ → [02_translation.txt] ⟳ → [○] → [○]
```

**Time 5s:** Translation complete, safety checking
```
[01_input.txt] ✓ → [02_translation.txt] ✓ → [03_safety.json] ⟳ → [○]
```

... and so on

### Real-Time Polling

**Implementation:**
- Poll `/api/pipeline/{run_id}/status` every 1 second
- Response includes list of available entities
- Frontend dynamically creates/updates entity boxes
- New entities fade in when they become available

---

## Entity Viewer Modal

When user clicks **[View]** on entity box:

```
┌───────────────────────────────────────────────────┐
│  02_translation.txt                         [✕]  │
├───────────────────────────────────────────────────┤
│                                                   │
│  Content Type: text/plain                        │
│  Size: 47 bytes                                   │
│  Created: 2025-11-06 14:23:18                    │
│                                                   │
│  ─────────────────────────────────────────────── │
│                                                   │
│  Content:                                         │
│  ┌───────────────────────────────────────────┐   │
│  │ A beautiful flower in a sunny meadow     │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ─────────────────────────────────────────────── │
│                                                   │
│  Previous Entity:                                 │
│  ← 01_input.txt: "Eine schöne Blume..."         │
│                                                   │
│  Next Entity:                                     │
│  → 03_safety_stage1.json: {"status": "SAFE"}     │
│                                                   │
│  [Copy to Clipboard]  [Download]  [Close]         │
└───────────────────────────────────────────────────┘
```

**Features:**
- Show full content (not just preview)
- Navigation to previous/next entity
- Download individual entity
- Copy to clipboard for text entities

---

## Responsive Layout

### Desktop (1920px+)

**Horizontal Flow:**
```
[Entity] → [Entity] → [Entity] → [Entity] → [Entity]
```

### Laptop (1280px+)

**Horizontal Flow (Compact):**
```
[Entity] → [Entity] → [Entity]
    ↓
[Entity] → [Entity]
```

### Tablet/Mobile (< 1024px)

**Vertical Flow:**
```
[Entity 1]
    ↓
[Entity 2]
    ↓
[Entity 3]
    ↓
[Entity 4]
```

---

## Connection to Backend

### API Integration

**Get Entity List:**
```javascript
GET /api/pipeline/{run_id}/status

Response:
{
  "status": "running",
  "entities": [
    {
      "filename": "01_input.txt",
      "type": "input",
      "available": true,
      "size": 47,
      "mime_type": "text/plain"
    },
    {
      "filename": "02_translation.txt",
      "type": "translation",
      "available": true,
      "size": 47,
      "mime_type": "text/plain"
    },
    {
      "filename": "04_interception_iter3.txt",
      "type": "interception",
      "available": false,  // Still being generated
      "in_progress": true
    }
  ]
}
```

**Get Entity Content:**
```javascript
GET /api/pipeline/{run_id}/entity/02_translation.txt

Response: (file content)
```

---

## Error Handling in Entity Flow

### Failed Entity

```
┌─────────────────────┐
│ 03_safety_stage1    │
│      .json          │
├─────────────────────┤
│                     │
│ ✗ UNSAFE CONTENT    │
│                     │
│ Pipeline stopped    │
│ [View Details]      │
└─────────────────────┘
```

**Error Modal:**
```
┌───────────────────────────────────────┐
│  Safety Check Failed                  │
├───────────────────────────────────────┤
│                                       │
│  Stage: stage1_safety_check           │
│  Reason: Content flagged as unsafe    │
│                                       │
│  Blocked Categories:                  │
│  • Violence                           │
│                                       │
│  The pipeline has been stopped.       │
│  No media will be generated.          │
│                                       │
│  Actions:                             │
│  • Try a different prompt             │
│  • Adjust safety level (Youth)        │
│  • Return to config selection         │
│                                       │
│  [New Prompt]  [Back to Selection]    │
└───────────────────────────────────────┘
```

---

## Implementation Notes

### Vue Component Structure

```
Phase2_3View.vue
├── Phase2_PromptInput.vue
└── Phase3_ProcessFlow.vue
    ├── EntityBox.vue (multiple instances)
    ├── EntityConnection.vue
    └── EntityViewer.vue (modal)
```

### State Management

**Pinia Store: `pipelineStore`**
```typescript
{
  runId: string | null,
  phase: 2 | 3,  // Current phase
  inputPrompt: string,
  entities: Entity[],
  status: 'idle' | 'running' | 'completed' | 'error'
}
```

### Entity Type Definitions

```typescript
interface Entity {
  filename: string;
  type: 'input' | 'translation' | 'safety' | 'interception' | 'output';
  available: boolean;
  in_progress?: boolean;
  size?: number;
  mime_type?: string;
  preview?: string;  // First 50 chars for display
}
```

---

## Pedagogical Design Principles

### 1. Transparency Over Simplicity

**Don't hide complexity, explain it:**
- Show all intermediate steps
- Make meta-prompts visible
- Explain what each entity represents

### 2. Inspectability

**Every step is clickable/viewable:**
- View entity content
- Download entity
- Compare entities (before/after transformation)

### 3. Process Understanding

**Students learn AI is not magic:**
- Translation: "Why does it translate first?"
- Safety: "What does AI consider unsafe?"
- Interception: "How do meta-prompts work?"
- Recursion: "How does iteration change results?"

### 4. No Black Boxes

**Everything is documented and visible:**
- Context files (meta-prompts) are entities
- Safety decisions are JSON files (inspectable)
- Intermediate transformations are saved

---

## Future Enhancements

### V2.0 Features

1. **Compare Mode:** Side-by-side comparison of entities
2. **Annotation:** Students can add notes to entities
3. **Export Educational Report:** PDF with all steps documented
4. **Replay Mode:** Step through pipeline execution step-by-step

### V3.0 Features

1. **Branch Visualization:** Show parallel paths (for dual-input configs)
2. **Collaborative Mode:** Multiple students analyze same run
3. **Historical Comparison:** Compare different runs side-by-side

---

## Related Documentation

- `FRONTEND_01_ARCHITECTURE_OVERVIEW.md` - Overall architecture
- `FRONTEND_02_PHASE_1_SCHEMA_SELECTION.md` - Config selection
- `FRONTEND_04_VUE_COMPONENT_ARCHITECTURE.md` - Component structure
- `/docs/LIVE_PIPELINE_RECORDER.md` - Backend entity tracking

---

**Document Status:** ✅ Revised - Entity-Based Visualization
**Next Steps:** Create visual mockups, implement Phase 2 first
**Key Change:** Stage-based → Entity-based visualization for pedagogical transparency
