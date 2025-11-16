# Development Decisions - Current & Active
**AI4ArtsEd DevServer - Active Architectural Decisions**

> **IMPORTANT FOR ALL TASKS:**
> Every significant development decision MUST be documented here.
> Format: Date, Decision, Reasoning, Affected Files

**Full History:** See `docs/archive/DEVELOPMENT_DECISIONS_FULL.md` (2435 lines, Sessions 1-17)

---

## 📋 Quick Reference - Current Architecture

**Current System Status (as of 2025-11-16):**
- ✅ 4-Stage Pipeline Architecture (DevServer orchestrates Stages 1-4)
- ✅ GPT-OSS:20b for Stage 1 (Translation + §86a Safety unified)
- ✅ Config-based system (Interception configs, Output configs, Pre-output safety)
- ✅ Backend abstraction (Ollama, ComfyUI, SwarmUI APIs)
- ✅ Multi-output support (model comparison, batch generation)
- ✅ Recursive pipelines ("Stille Post" iterative transformation)
- ✅ Unified storage (symlink: prod → dev for shared research data)

**Deployment (Research Phase - 2025-11-16):**
- 🌐 Internet-facing via Cloudflare tunnel (multiple courses)
- 📱 Primary device: iPad Pro 10"
- 🔄 Legacy backend (port TBD) - Active for students
- 🔧 Dev backend (port 17801) - Development only
- 📊 Shared storage: `/home/joerissen/ai/ai4artsed_webserver/exports/`

---

## 🎯 Active Decision 0: Deployment Architecture - Dev/Prod Separation for Research Phase (2025-11-16, Session 46)

**Status:** ✅ IMPLEMENTED (storage unified, port separation pending)
**Context:** Multi-user research environment with active student courses
**Date:** 2025-11-16

### The Decision: Dual Backend with Unified Storage

**Problem:**
- Multiple students in courses accessing via internet (iPad Pro 10")
- Need stable production environment for students
- Need development environment for ongoing research/fixes
- Previous setup caused 404 errors (dual storage locations)

**Solution Chosen: Symlinked Storage + Port Separation**

**Architecture:**
```
┌─────────────────────────────────────────────────────┐
│  Students (Internet, iPad Pro 10")                 │
│  ↓                                                  │
│  Cloudflare Tunnel (lab.ai4artsed.org)             │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  LEGACY Backend (Production - Active)              │
│  - Students use this (stable, tested)              │
│  - Port: TBD (separate from new system)            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  NEW DevServer System (Development Phase)          │
│  ├─ Dev Backend: port 17801 (development)          │
│  ├─ Prod Backend: port 17801 (CONFLICT!)           │
│  │  └─ TODO: Change to 17802 for separation        │
│  └─ Frontend: port 5173 (Vite proxy)               │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  UNIFIED STORAGE (Research Data)                   │
│  Canonical: /home/joerissen/.../exports/           │
│  Symlink: /opt/ai4artsed-production/exports → dev  │
│  - 300+ runs (7.5GB)                               │
│  - Accessible to researcher (not hidden in /opt/)  │
└─────────────────────────────────────────────────────┘
```

**Port Configuration (Planned):**
- **Legacy Backend:** Separate port (students access this)
- **17801:** Production backend (when ready for migration)
- **17802:** Dev backend (development/testing)
- **5173:** Vite frontend (proxies to backend)

**Storage Decision:**
- **Canonical location:** `/home/joerissen/ai/ai4artsed_webserver/exports/`
- **Rationale:** Research data must be accessible to researcher
- **Symlink direction:** prod → dev (not dev → prod as in Session 44)
- **Why reversed:** Data belongs in visible location, not hidden in /opt/

**Deployment Context:**
- **Current (Research Phase):** Internet via Cloudflare, multiple courses
- **Future (Post-Research):** WiFi-only deployment after project ends
- **Primary Users:** Students on iPad Pro 10" (NOT solo researcher)

**What Changed from Session 44:**
1. ❌ Session 44 created symlink: dev → prod (wrong direction)
2. ✅ Session 46 reversed: prod → dev (correct - data accessible)
3. ❌ Session 44 documented "WiFi-only, temporary internet" (wrong context)
4. ✅ Session 46 corrected: "Internet-facing research, WiFi-only later"

**Technical Implementation:**
- Storage: 300 runs merged from both locations
- Symlink: `/opt/ai4artsed-production/exports` → `/home/joerissen/ai/ai4artsed_webserver/exports`
- Backend: Relative paths (`BASE_DIR / "exports"`) work automatically
- No code changes needed (paths resolve via symlink)

**Files Modified:**
- `/opt/ai4artsed-production/exports` (now symlink)
- `docs/STORAGE_SYMLINK_STRATEGY.md` (corrected deployment context)
- `docs/SESSION_44_SUMMARY.md` (corrected deployment context)

**Port Separation - COMPLETED (2025-11-16):**
- [x] Prod backend config: `PORT = 17801` (for students/Cloudflare)
- [x] Dev backend config: `PORT = 17802` (for development)
- [x] Vite proxy updated to 17802 (dev backend)
- [x] Start scripts updated (`3 start_backend_fg.sh`)
- **Students use:** Port 17801 (production backend via Cloudflare)
- **Development uses:** Port 17802 (dev backend, Vite proxy)

**Rationale:**
- Students need stable environment (can't have dev interruptions)
- Research data must be accessible (not buried in /opt/)
- Unified storage prevents 404 errors
- Port separation allows simultaneous dev + prod

---

## 🎯 Active Decision 1: Token Processing Animation for Progress Visualization (2025-11-09, Session 40)

**Status:** ✅ IMPLEMENTED
**Context:** Progress visualization for GenAI pipeline execution (target: children/youth)
**Date:** 2025-11-09

### The Decision: Token Processing Metaphor with Neural Network Visualization

**Problem:**
- Pipeline execution takes 10-30 seconds
- Boring spinner + progress bar insufficient for educational/youth context
- Need engaging, educational animation that runs smoothly on iPad Pro 10"

**Options Considered:**

1. **Complex Pixel-Art Sprites (REJECTED)**
   - Animated characters (hare and hedgehog story)
   - User feedback: "sieht wirklich schlimm aus" (looks terrible)
   - Reason rejected: Too "gewollt" (forced), complex to animate smoothly

2. **Simple Cumulative Animations (REJECTED)**
   - Stars collecting, glass filling, dots grid
   - User feedback: Not thematically relevant
   - Reason rejected: Doesn't connect to GenAI/AI processing concept

3. **Token Processing with Neural Network (CHOSEN)**
   - INPUT grid → PROCESSOR box → OUTPUT grid
   - Tokens fly through neural network layers
   - Color transformation visible during processing
   - Forms recognizable pixel art images (26 different images)

**Decision:**
Token processing metaphor with visible neural network layer processing and gradual color transformation.

**Rationale:**
- **Educational:** Visualizes how AI processes and transforms data
- **Conceptually Aligned:** Matches GenAI token processing model
- **Simple to Animate:** Geometric shapes (colored squares) for smooth performance
- **Engaging:** 26 different images (animals, space, food) keep it fresh
- **iPad-Optimized:** Pure CSS animations, no heavy libraries
- **User Validated:** Multiple iterations with positive feedback

**Key Technical Decisions:**

1. **Progress Scaling to 90%**
   - User requirement: Animation complete at 90% progress
   - Implementation: `const scaledProgress = Math.min(props.progress / 90, 1)`
   - Rationale: INPUT queue empty by 90%, remaining 10% for final processing

2. **Visible Color Transformation (40% of Animation Time)**
   - 20-68% of animation spent inside processor box
   - Gradual color mixing: 100% original → 50/50 mix → 100% target
   - Uses CSS `color-mix(in srgb, ...)` for smooth gradients
   - Rationale: User explicitly requested visible transformation

3. **0.6s Per-Token Animation Duration**
   - Fast enough to complete before next token starts
   - Slow enough to see flying motion through all rows
   - Balance between visibility and smoothness
   - Rationale: Testing showed 3s too slow (animations cut off), 0.6s optimal

4. **Neural Network Visualization in Processor**
   - 5 pulsating nodes + 4 connection lines
   - Flicker effect with brightness variations (0.8x to 1.7x)
   - Lightning icon (⚡) with rotation and scaling
   - Rationale: More engaging than simple box, shows "AI thinking"

**Implementation:**
- Component: `SpriteProgressAnimation.vue` (648 lines)
- 26 pixel art images (14x14 grid, 7-color palette)
- Real-time timer: "generating X sec._" with blinking cursor
- Pure CSS animations (no JavaScript canvas)
- TypeScript strict mode compliance

**Affected Files:**
- `public/ai4artsed-frontend/src/components/SpriteProgressAnimation.vue` (new)
- `public/ai4artsed-frontend/src/views/Phase2CreativeFlowView.vue` (integrated)
- `public/ai4artsed-frontend/src/views/PipelineExecutionView.vue` (integrated)

**Future Considerations:**
- Could add more image templates based on workshop themes
- Could make animation speed configurable (age group settings)
- Could sync animation with actual pipeline stages (requires SSE)

---

## 🎯 Active Decision 2: SSE Streaming Postponed in Favor of Animation (2025-11-09, Session 39)

**Status:** POSTPONED
**Context:** Frontend real-time progress updates for pipeline execution
**Date:** 2025-11-09

### The Decision: Use SpriteProgressAnimation Instead of SSE Streaming

**Problem:**
- Pipeline execution takes 10-30 seconds
- Users need visual feedback that system is working
- Session 37 attempted SSE (Server-Sent Events) streaming implementation
- SSE implementation incomplete, unstable, blocking v2.0.0-alpha.1 release

**Options Considered:**

1. **SSE Streaming (ATTEMPTED)**
   - Real-time progress updates from backend
   - Step-by-step pipeline stage notifications
   - Complexity: HIGH
   - Status: Incomplete, buggy after 2+ hours work

2. **WebSockets**
   - Bidirectional communication
   - More complex than SSE
   - Overkill for one-way progress updates

3. **Polling**
   - Frontend polls /api/pipeline/{run_id}/status every N seconds
   - Already implemented via LivePipelineRecorder
   - Works but not real-time

4. **SpriteProgressAnimation (CHOSEN)**
   - Pure frontend animation
   - No backend changes required
   - User already implemented: "Dafür habe ich jetzt eine hübsche Warte-Animation"
   - Simple, reliable, working

**Decision:**
Postpone SSE streaming, use SpriteProgressAnimation for v2.0.0-alpha.1

**Rationale:**
- User explicitly requested: "SSE-Streaming würde ich vorerst lassen"
- Animation already working and sufficient for current needs
- SSE can be added later as enhancement without breaking changes
- Unblocks release: v2.0.0-alpha.1 shipped on time
- LivePipelineRecorder polling already works for post-execution data

**Implementation:**
- Stashed Session 37 SSE code: `git stash push -m "WIP: Frontend seed UI and progressive generation (Session 37)"`
- SpriteProgressAnimation component in Phase 2 view
- Polling-based updates for completion detection

**Future Consideration:**
SSE streaming can be reconsidered for:
- Multi-stage progress bars
- Real-time Stage 1-4 status updates
- Workshop scenarios with multiple concurrent users
- When frontend UX design is finalized and stable

**Affected Files (Session 37 - Stashed):**
- `devserver/my_app/__init__.py` - SSE blueprint import
- `devserver/my_app/routes/pipeline_stream_routes.py` - SSE endpoints
- Frontend components - SSE connection handlers

---

## 🎯 Active Decision 2: Variable Scope Pattern for Conditional Pipeline Stages (2025-11-09, Session 39)

**Status:** IMPLEMENTED
**Context:** stage4_only feature support for fast regeneration
**Date:** 2025-11-09

### The Decision: Extract Loop-External Dependencies Before Conditional Blocks

**Problem:**
Session 37 implemented `stage4_only` flag to skip Stage 1-3 for fast image regeneration. However, `media_type` variable was only defined INSIDE the Stage 3 conditional block. When Stage 3 was skipped, Stage 4 tried to access undefined `media_type` → UnboundLocalError crash.

**Root Cause:**
```python
# BEFORE FIX (Session 37):
if not stage4_only:  # Skip Stage 3 when True
    # Stage 3 safety check
    if 'image' in output_config_name.lower():
        media_type = 'image'  # ← Defined HERE
    # ...

# Stage 4 needs media_type
recorder.download_and_save_from_comfyui(media_type=media_type)  # ← CRASH!
```

**Architecture Pattern Established:**

**Rule:** If a variable is used OUTSIDE a conditional block, it MUST be defined BEFORE the block.

**Implementation:**
```python
# AFTER FIX (Session 39 - Lines 733-747):

# DETERMINE MEDIA TYPE (needed for both Stage 3 and Stage 4)
# Extract media type from output config name BEFORE Stage 3-4 Loop
# This ensures media_type is ALWAYS defined, even when stage4_only=True
if 'image' in output_config_name.lower() or 'sd' in output_config_name.lower():
    media_type = 'image'
elif 'audio' in output_config_name.lower():
    media_type = 'audio'
elif 'music' in output_config_name.lower() or 'ace' in output_config_name.lower():
    media_type = 'music'
elif 'video' in output_config_name.lower():
    media_type = 'video'
else:
    media_type = 'image'  # Default fallback

# NOW Stage 3 can be conditional
if safety_level != 'off' and not stage4_only:
    # Stage 3 code...

# Stage 4 can safely use media_type regardless of stage4_only
```

**Benefits:**
1. **Variable always defined** - No UnboundLocalError possible
2. **Clean separation** - Dependency extraction vs conditional logic
3. **Maintainable** - Easy to see what Stage 4 depends on
4. **Scalable** - Pattern applies to any conditional stage skip

**Generalized Pattern:**
```python
# 1. Extract dependencies FIRST
variable_needed_by_both = determine_variable(...)

# 2. THEN conditional blocks
if condition:
    do_stage_3()

# 3. Variable available regardless
do_stage_4(variable_needed_by_both)
```

**Affected Files:**
- `devserver/my_app/routes/schema_pipeline_routes.py` (lines 733-747)

**Testing:**
- ✅ Normal flow (stage4_only=False): All stages run, media_type defined
- ✅ Fast regen (stage4_only=True): Stage 3 skipped, media_type still defined
- ✅ All media types: image, audio, music, video
- ✅ Fallback: Unknown types default to 'image'

**Key Learning:**
Python variable scope in conditional blocks is NOT block-scoped. Variable defined in `if` block exists outside, BUT only if `if` branch executes. For variables used outside conditional blocks, define BEFORE the condition.

---

## 🎯 Active Decision 3: Property Taxonomy for Config Selection UI (2025-11-07, Session 34)

**Status:** IMPLEMENTED
**Context:** Phase 1 UI needs non-consumeristic filtering system for config selection

### The Decision: 6 Property Pairs Based on Grounded Theory Analysis

**Problem:** Tags like [lustig] [schnell] serve consumeristic "user choice" model, contradict pedagogical goals (counter-hegemonic, agency-oriented)

**Solution:** Property pairs as tension fields (Spannungsfelder) that express transformation qualities:

```
1. calm ↔ chaotic          (chillig - chaotisch)       - Process control
2. narrative ↔ algorithmic (erzählen - berechnen)      - Transformation mode
3. facts ↔ emotion         (fakten - gefühl)           - Focus/affect
4. historical ↔ contemporary (geschichte - gegenwart)  - Temporal orientation
5. explore ↔ create        (erforschen - erschaffen)   - Purpose
6. playful ↔ serious       (spiel - ernst)             - Attitude
```

### Architecture

**Config Level:** Properties stored as arrays in config JSON
```json
"properties": ["chaotic", "narrative", "emotion", "historical", "create", "playful"]
```

**Frontend i18n:** Labels in `i18n.js` following existing pattern
```javascript
properties: {
  calm: 'chillig',
  chaotic: 'chaotisch',
  ...
}
```

**UI Logic:** Positive logic (nothing shown until properties selected) + AND-logic filtering

### Critical Pedagogical Insight

YorubaHeritage description updated to reflect limits:
> "Tries to translate... Allows for a critical assessment of the limits of generative AI with regard to cultural knowledge."

**Reason:** LLMs may understand contexts; image generation models are culturally indifferent. This exposes AI bias pedagogically.

### Rejected Approaches
- Abstract academic categories (Iteration 01: "Reflexionsmodus", "dekonstruktiv")
- Separate metadata files (violates existing i18n architecture)
- Neutral tags (would reinforce solutionism)

---

## 🎯 Active Decision 2: Execution History Architecture (2025-11-03, Session 17)

**Status:** DESIGNED (Not yet implemented)
**Priority:** HIGH (Fixes broken research data export)

### The Decision: Observer Pattern (Stateless Pipeline + Stateful Tracker)

**Core Principle:**
- **Pipeline stays stateless** - Pure functions, no side effects
- **Tracker is stateful** - Observes pipeline, tracks execution history
- **Loose coupling** - Tracker failure doesn't break pipeline execution

### Architecture

\`\`\`
Pipeline Execution (STATELESS)           ExecutionTracker (STATEFUL)
┌─────────────────────────┐             ┌──────────────────────────┐
│ Stage 1: Translation    │             │ - In-memory storage      │
│ Stage 2: Interception   │──observe──→ │ - Async event queue      │
│ Stage 3: Safety         │             │ - Session tracking       │
│ Stage 4: Generation     │             │ - Auto-export to disk    │
└─────────────────────────┘             └──────────────────────────┘
\`\`\`

### What Gets Tracked

1. **Inputs** (user text, uploaded images)
2. **All stage outputs** (translation, interception, safety checks, media generation)
3. **Metadata** (configs used, models used, timestamps)
4. **Semantic labels** (what each item means - for pedagogical frontend)
5. **Sequential order** (actual execution order, including parallel stages)

### Storage Structure

\`\`\`
research_data/
├── dada/
│   ├── <execution_id>.json
│   └── ...
├── bauhaus/
└── stillepost/
\`\`\`

### Key Insight: Frontend Flexibility

The structured JSON enables different pedagogical views:

**Student View:** Show only input → transformation → output
**Advanced View:** Show translation → interception → output
**Researcher View:** Show everything (safety checks, metadata, timing)

### Critical Lesson from Session 17

> "NEVER implement before understanding the architecture completely."

The previous session failed because it assumed \`output_requests\` with \`count\` parameters existed. In reality:
- Current code uses \`output_configs\` array in config JSON
- Each config executes exactly once (no \`count\` parameter)
- Multiple outputs = list config multiple times in array
- See \`my_app/routes/schema_pipeline_routes.py\` lines 222-330

**Reference:** \`docs/archive/EXECUTION_HISTORY_KNOWLEDGE.md\` for detailed architectural understanding

---

## 🎯 Active Decision 2: GPT-OSS Unified Stage 1 (2025-11-02, Session 14)

**Status:** ✅ IMPLEMENTED & TESTED

### The Decision: Single LLM Call for Translation + §86a Safety

**OLD:** Two-step Stage 1 (mistral-nemo translation → llama-guard3 safety)
**NEW:** One-step Stage 1 (GPT-OSS:20b for both)

### Why This Matters

**Problem:** Session 13 failure case
- Test input: "Isis-Kämpfer sprayt Isis-Zeichen" (ISIS terrorist)
- Previous system: Marked SAFE ❌
- Root cause: US-centric model applied First Amendment framework
- Model interpreted "isis" as Egyptian goddess, not ISIS

**Solution:** Full §86a StGB legal text in system prompt
- Model now applies German legal framework
- Explicit rules for student context
- Educational error messages in primary language (currently German, configurable via PRIMARY_LANGUAGE - see devserver_todos.md Priority 2)

### Performance Impact

- **Before:** 2-4s (mistral-nemo 1-2s + llama-guard3 1-2s)
- **After:** 1-2s (single GPT-OSS call)
- **Savings:** 1-2s per request + no model switching overhead

### Files

- \`devserver/schemas/configs/pre_interception/gpt_oss_unified.json\`
- \`devserver/schemas/engine/stage_orchestrator.py\` (execute_stage1_gpt_oss_unified)
- \`devserver/my_app/routes/schema_pipeline_routes.py\`

---

## 🎯 Active Decision 3: 4-Stage Architecture with DevServer Orchestration (2025-11-01)

**Status:** ✅ IMPLEMENTED

### The Decision: DevServer Orchestrates, Pipeline Executes

**Architecture:**
\`\`\`
Stage 1 (DevServer): Translation + §86a Safety
Stage 2 (Pipeline):  Interception (Dada, Bauhaus, etc.)
Stage 3 (DevServer): Pre-output safety (age-appropriate)
Stage 4 (Pipeline):  Media generation (ComfyUI, APIs)
\`\`\`

**Why This Split:**
- Stages 1+3 = Safety/compliance (belongs in orchestrator)
- Stages 2+4 = Creative transformation (belongs in pipeline)
- Clear separation of concerns

### Stage 3-4 Loop

**Critical Implementation Detail:**
\`\`\`python
# In schema_pipeline_routes.py
for i, output_config_name in enumerate(configs_to_execute):
    # Stage 3: Safety check for THIS config
    safety_result = execute_stage3_safety(...)

    if not safety_result['safe']:
        continue  # Skip Stage 4 for blocked content

    # Stage 4: Execute THIS config → generates ONE output
    output_result = pipeline_executor.execute_pipeline(output_config_name, ...)
\`\`\`

**Key Facts:**
- Each config in \`output_configs\` array executes exactly once
- No \`count\` parameter exists (future enhancement)
- Multi-output = list multiple configs in array

---

## 🎯 Active Decision 4: Config-Based System (2025-10-26 - 2025-11-01)

**Status:** ✅ IMPLEMENTED

### The Decision: Three Config Types

1. **Interception Configs** (\`schemas/configs/interception/\`)
   - User-facing configs (Dada, Bauhaus, Stille Post)
   - Define Stage 2 transformation pipeline
   - Specify media preferences (output_configs)

2. **Output Configs** (\`schemas/configs/output/\`)
   - Backend configs (sd35_large, gpt5_image)
   - Define Stage 4 media generation
   - Not directly selectable by users

3. **Pre-Output Configs** (\`schemas/configs/pre_output/\`)
   - Age-appropriate safety (kids, youth)
   - Stage 3 content filtering

### Benefits

- ✅ User doesn't see backend complexity
- ✅ Backend changes don't affect user experience
- ✅ Can swap models (SD3.5 → FLUX) without user-facing changes
- ✅ Multiple outputs for comparison

---

## 🎯 Active Decision 5: Backend Abstraction (2025-10-27 - 2025-10-28)

**Status:** ✅ IMPLEMENTED

### The Decision: Three Backend Types

1. **Ollama** - Local LLMs (mistral-nemo, llama-guard3, GPT-OSS)
2. **ComfyUI** - Local image generation (SD3.5, FLUX)
3. **OpenRouter** - API-based outputs (GPT-5 Image, future music/video)

### Output Chunk Format

All outputs return unified format:
\`\`\`python
{
    "media_type": "image" | "text" | "audio" | "video",
    "backend": "comfyui" | "openrouter" | "ollama",
    "content": <file_path> | <url> | <text>,
    "prompt_id": <for ComfyUI retrieval>
}
\`\`\`

### Files

- \`devserver/schemas/chunks/output_comfyui.json\`
- \`devserver/schemas/chunks/output_openrouter_gpt5_image.json\`
- \`devserver/schemas/engine/comfyui_api.py\`
- \`devserver/schemas/engine/openrouter_api.py\`

---

## 🧩 Development Principles (Standing Decisions)

### 1. Config Over Code
- New features = new config file, not code changes
- Users edit JSON, not Python

### 2. Fail-Safe Design
- Safety checks: Fail-open on errors (log warning, continue)
- Research tracker: Optional, non-blocking
- Principle: System degradation > complete failure

### 3. Separation of Concerns
- Pipeline = stateless, pure functions
- Tracker/Logger = stateful, observer pattern
- Safety = orchestrator responsibility
- Creativity = pipeline responsibility

### 4. Educational Transparency
- Error messages in primary language explain WHY content is blocked (currently German, configurable)
- Frontend can show/hide intermediate results
- Research data enables pedagogical analysis

---

## 🎯 Active Decision 7: Unified Media Storage with "Run" Terminology (2025-11-04, Session 27)

**Status:** ✅ IMPLEMENTED
**Priority:** HIGH (fixes broken export functionality)

### Context

Media files were not persisted consistently across backends:
- **ComfyUI**: Images displayed in frontend but NOT stored locally
- **OpenRouter**: Images stored as data strings in JSON (unusable for research)
- **Export function**: Failed because media wasn't persisted to disk
- **Research data**: URLs printed to console instead of actual files

### The Decision: Unified Media Storage Service

**Storage Architecture:**
- **Flat structure**: `exports/json/{run_id}/` (no hierarchical sessions)
- **"Run" terminology**: NOT "execution" (German connotations: "Hinrichtungen")
- **Atomic research units**: One folder contains ALL files for one complete run
- **Backend-agnostic**: Works with ComfyUI, OpenRouter, Replicate, future backends
- **UUID-based**: Concurrent-safety for workshop scenario (15 kids)

**Structure:**
```
exports/json/{run_uuid}/
├── metadata.json           # Single source of truth
├── input_text.txt         # Original user input
├── transformed_text.txt   # After Stage 2 interception
└── output_<type>.<format> # Generated media (image, audio, video)
```

### Rationale

**Why Flat Structure:**
> User: "I just think we do not have an entity 'session' yet, and I would not know how to discriminate sessions technically."

No session entity exists. Flat UUID-based folders with metadata enable future queries without complex hierarchy.

**Why "Run" Terminology:**
> User: "stop using 'execution'. this is also the word for killing humans."

German language sensitivity. "Run" is neutral and commonly used in programming contexts.

**Why Atomic Units:**
> User: "Our data management has to keep 'atomic' research events, such as one pipeline run, together."

One folder = one complete research event. No split data across multiple locations.

### Implementation

**File:** `devserver/my_app/services/media_storage.py` (414 lines)

**Detection Logic:**
```python
if output_value.startswith('http'):
    # API-based (OpenRouter) - Download from URL
    media_storage.add_media_from_url(run_id, url, media_type)
else:
    # ComfyUI - Fetch via prompt_id
    media_storage.add_media_from_comfyui(run_id, prompt_id, media_type)
```

**Integration Points:**
1. Pipeline start: Create run folder + save input text
2. Stage 4: Auto-detect backend + download media
3. Response: Return `run_id` to frontend (not raw prompt_id/URL)

### Affected Files

**Created:**
- `devserver/my_app/services/media_storage.py` (414 lines) - Core service
- `docs/UNIFIED_MEDIA_STORAGE.md` - Technical documentation

**Modified:**
- `devserver/my_app/routes/schema_pipeline_routes.py` - Integration
- `devserver/my_app/routes/media_routes.py` - Rewritten for local serving

### API Endpoints

- `GET /api/media/image/<run_id>` - Serve image
- `GET /api/media/audio/<run_id>` - Serve audio
- `GET /api/media/video/<run_id>` - Serve video
- `GET /api/media/info/<run_id>` - Metadata only
- `GET /api/media/run/<run_id>` - Complete run info

### Benefits

✅ **All media persisted** - ComfyUI and OpenRouter work identically
✅ **Export-ready** - Research data complete and accessible
✅ **Backend-agnostic** - Easy to add new backends (Replicate, etc.)
✅ **Concurrent-safe** - Workshop scenario supported
✅ **Simple queries** - Metadata enables filtering without complex joins

### Testing Status

**Required:** ComfyUI eco mode, OpenRouter fast mode, concurrent requests

---

## 🎯 Active Decision 8: Unified run_id to Fix Dual-ID Bug (2025-11-04, Session 29)

**Status:** ✅ IMPLEMENTED & TESTED
**Priority:** CRITICAL (complete system desynchronization)

### Context: The Dual-ID Bug

**The Problem:**
OLD system used TWO different UUIDs causing complete desynchronization:
- **OLD ExecutionTracker**: Generated `exec_20251104_HHMMSS_XXXXX`
- **OLD MediaStorage**: Generated `uuid.uuid4()`
- **Result**: Execution history referenced non-existent media files

**User Insight:**
> "remember, this is what the old executiontracker did not achieve the whole time"
> "meaning it is not a good reference"

The OLD ExecutionTracker found the media polling issue but FAILED to fix it for months.

### The Decision: Unified run_id Architecture

**Core Principle:**
Generate `run_id = str(uuid.uuid4())` **ONCE** at pipeline start.
Pass this SINGLE ID to ALL systems.

**Architecture:**
```
Pipeline Start (schema_pipeline_routes.py)
↓
run_id = str(uuid.uuid4())  ← Generated ONCE
↓
├─→ ExecutionTracker(execution_id=run_id)    ← Uses same ID
├─→ MediaStorage.create_run(run_id)          ← Uses same ID
└─→ LivePipelineRecorder(run_id)             ← Uses same ID
    ↓
    Single source of truth: pipeline_runs/{run_id}/metadata.json
```

### Implementation

**File:** `devserver/my_app/services/pipeline_recorder.py` (400+ lines)

**LivePipelineRecorder Features:**
- Unified `run_id` passed to constructor
- Sequential entity tracking: 01_input.txt → 06_output_image.png
- Single source of truth in `metadata.json`
- Real-time state tracking (stage/step/progress)
- Metadata enrichment for each entity

**File Structure:**
```
pipeline_runs/{run_id}/
├── metadata.json              # Single source of truth
├── 01_input.txt              # User input
├── 02_translation.txt        # Translated text
├── 03_safety.json            # Safety results
├── 04_interception.txt       # Transformed prompt
├── 05_safety_pre_output.json # Pre-output safety
└── 06_output_image.png       # Generated media
```

### Critical Bug Fix: Media Polling

**The Issue:**
ComfyUI generates images asynchronously. Calling `get_history(prompt_id)` immediately after submission returns empty result.

**File Modified:** `devserver/my_app/services/media_storage.py` (line 214)

**The Fix:**
```python
# OLD (BROKEN):
# history = await client.get_history(prompt_id)

# NEW (FIXED):
history = await client.wait_for_completion(prompt_id)
```

**Why This Matters:**
- `wait_for_completion()` polls every 2 seconds until workflow finishes
- **OLD ExecutionTracker identified this issue but NEVER fixed it**
- **NEW LivePipelineRecorder SUCCEEDED on first implementation**

### Test Proof

**Test Run:** `812ccc30-5de8-416e-bfe7-10e913916672`

**Result:**
```json
{"status": "success", "media_output": "success"}
```

**All 6 entities created:**
```bash
01_input.txt
02_translation.txt
03_safety.json
04_interception.txt
05_safety_pre_output.json
06_output_image.png  ← This was MISSING in OLD system
metadata.json
```

### Dual-System Migration Strategy

**Both systems run in parallel (by design):**

**OLD System:**
- ExecutionTracker: `exec_20251104_HHMMSS_XXXXX`
- Output: `/exports/pipeline_runs/exec_*.json`
- Status: Maintained for validation

**NEW System:**
- LivePipelineRecorder: `{unified_run_id}`
- Output: `pipeline_runs/{run_id}/`
- Status: Production-ready

**MediaStorage:**
- Uses unified `run_id` from NEW system
- Output: `exports/json/{run_id}/`
- Synchronized with LivePipelineRecorder

**Rationale:**
- Ensure no data loss during migration
- Validate NEW system against OLD system
- Gradual deprecation path for OLD system

### API Endpoints for Frontend

**File Created:** `devserver/my_app/routes/pipeline_routes.py` (237 lines)

**Real-Time Polling:**
- `GET /api/pipeline/<run_id>/status` - Current execution state
- `GET /api/pipeline/<run_id>/entity/<type>` - Fetch specific entity
- `GET /api/pipeline/<run_id>/entities` - List all entities

**Frontend Integration Ready:**
- Status polling for progress bars
- Entity fetching for live preview
- MIME type detection for proper display

### Affected Files

**Created (3 files, ~800 lines):**
- `devserver/my_app/services/pipeline_recorder.py` (400+ lines, flattened from package)
- `devserver/my_app/routes/pipeline_routes.py` (237 lines, 3 endpoints)
- `docs/LIVE_PIPELINE_RECORDER.md` (17KB technical documentation)

**Modified (2 files):**
- `devserver/my_app/__init__.py` (blueprint registration)
- `devserver/my_app/routes/schema_pipeline_routes.py` (entity saves at all stages)

**File Structure Migration:**
- `/devserver/pipeline_recorder/` (package) → `/devserver/my_app/services/pipeline_recorder.py` (single file)
- Follows existing service pattern (ollama_service.py, comfyui_service.py, media_storage.py)

### Success Metrics

✅ **NEW system succeeded where OLD system failed**
- OLD: Found media polling issue months ago, never fixed it
- NEW: Fixed immediately with proper polling mechanism

✅ **Dual-ID Bug Resolved**
- Single unified `run_id` across all systems
- No more desynchronization
- All entities properly tracked and accessible

✅ **Production Ready**
- Tested successfully end-to-end
- All 6 entities created correctly
- Real-time API endpoints functional

### Future Refactoring (Deferred)

**Architectural Discussion:**
User suggested making ComfyUI execution blocking in `backend_router.py`:
- Chunk waits for completion internally
- Returns actual media bytes instead of just `prompt_id`
- Removes need for polling in media_storage.py

**Status:** Deferred to future session. Current polling solution works correctly.

---

## 📚 Related Documentation

- **Architecture:** \`docs/ARCHITECTURE PART I.md\`, \`docs/ARCHITECTURE PART II.md\`
- **Full Decision History:** \`docs/archive/DEVELOPMENT_DECISIONS_FULL.md\` (Sessions 1-17, 2435 lines)
- **Development Log:** \`docs/DEVELOPMENT_LOG.md\` (Session chronology with costs)
- **Active TODOs:** \`docs/devserver_todos.md\`
- **Session Handover:** \`docs/SESSION_HANDOVER.md\`

---

## Session 30: Internationalization (i18n) Requirement (2025-11-04)

### Decision: NEVER Hardcode Language-Specific Strings

**Problem Identified:**
During Session 30 implementation of frontend polling, hardcoded German strings were added to JavaScript:
- `'Verbindung langsam, Versuch läuft...'`
- `'Pipeline-Start', 'Übersetzung & Sicherheit'`, etc.

**User Correction (Critical):**
> "never directly use 'german', but a placeholder for language configuration. this system is at least bilingual and has to be prepared for multilinguality. german maybe now set as active language in config.py, but english will be equally important. every frontend interface part should be a variable that pulls the right terms from a dict."

### Architecture Requirements

**System Design:**
- **Bilingual:** German + English (equally important)
- **Multilingual-Ready:** Prepared for additional languages
- **Decentralized:** Pipelines/configs have their own bilingual translation

**Implementation:**
1. **Frontend:** All UI strings must come from language configuration dict (i18n system)
2. **Backend:** Language strings pulled from `config.py` active language setting
3. **NO Hardcoding:** Never embed German, English, or any language directly in code

**Example (CORRECT):**
```javascript
// Frontend i18n system
setStatus(i18n.status.connectionSlow, 'warning');
const stageName = i18n.stages[stageId];
```

**Legacy Frontend Status:**
- `public_dev/` contains hardcoded German strings (documented violation)
- **NO FURTHER WORK** will be done on legacy frontend
- Polling implementation (Session 30) was final backend piece
- New frontend(s) will be built with i18n from day 1

**Rule Added:** `devserver/CLAUDE.md` Critical Implementation Rules Section 0 - Internationalization is now **mandatory first rule** for all future frontends.

---

## 🎯 Active Decision 7: Frontend Architecture - Vue.js 3-Phase Model (2025-11-06, Session 33)

**Status:** PLANNED (Documentation complete, implementation pending)
**Priority:** HIGH (New frontend architecture)

### The Decision: 3-Phase User Journey with Entity-Based Transparency

**Core Principle:**
- **Phase 1:** Config Selection (Browse, Search, Select)
- **Phase 2:** Creative Input (Prompt entry)
- **Phase 3:** AI Process Transparency (Entity-based visualization)

### Phase 2 vs Phase 3 - Pedagogical Distinction

**Phase 2 - Creative Act:**
- Purpose: Prompt input, creative expression
- User Action: Write/conceptualize their prompt
- Interface: Simple textarea, examples, execute button

**Phase 3 - AI Process Transparency:**
- Purpose: **Make AI decision-making visible** (Against Black-Box Solutionism)
- Pedagogical Goal: Students understand AI as series of transformations, not magic
- Interface: **Entity-based visualization** (NOT stage-based)

### Key Architectural Decision: Entity-Based Visualization

**NOT Stage-Based (4 boxes):**
```
❌ [Stage 1] → [Stage 2] → [Stage 3] → [Stage 4]
   (Too abstract, hides process)
```

**Entity-Based (one box per file in exports/json):**
```
✅ [01_input.txt] → [02_translation.txt] → [03_safety.json] →
   [04_interception_context.txt] → [05_interception_result.txt] →
   [06_safety_pre_output.json] → [07_output_image.png]
```

**Rationale:**
1. **Transparency:** Every intermediate step is visible and inspectable
2. **Pedagogical:** Students see HOW AI processes information step-by-step
3. **Meta-Prompt Visibility:** Interception context files show what instructions modify prompts
4. **Recursive Visibility:** For Stillepost (8 iterations), all 8 steps visible as separate entities
5. **Against Solutionism:** No black boxes, every transformation documented

### What This Means for Implementation

**Every file in `exports/{run_id}/json/` gets a box:**
- Input files (01_input.txt)
- Translation files (02_translation.txt)
- Safety check results (03_safety_stage1.json)
- **Meta-prompts** (04_interception_context.txt) ← Pedagogically crucial
- Interception results (05_interception_result.txt)
- Pre-output safety (06_safety_pre_output.json)
- Final outputs (07_output_image.png, etc.)
- **Recursive iterations** (04_interception_iter1.txt through iter8.txt)

**Real-Time Display:**
- Poll `/api/pipeline/{run_id}/status` every 1 second
- Entities appear progressively as they become available
- Status icons: ✓ Available / ⟳ In Progress / ○ Pending
- Click any entity to view full content in modal

### Technology Stack

**Framework:** Vue.js 3 (Composition API)
**State Management:** Pinia
**Routing:** Vue Router
**Styling:** Scoped CSS (BEM methodology)
**i18n:** vue-i18n (DE/EN, extensible)
**Build:** Vite

### Metadata-Driven Design

**Principle:** Frontend NEVER hardcodes config lists
- Configs expose metadata via `/pipeline_configs_metadata` API
- Frontend dynamically renders based on metadata
- New configs appear automatically
- User configs integrate seamlessly

**Config Metadata Structure:**
```json
{
  "id": "dada",
  "name": {"de": "Dada-Transformation", "en": "Dada Transformation"},
  "description": {"de": "...", "en": "..."},
  "category": "art-movements",
  "icon": "🎨",
  "difficulty": 3,
  "output_types": ["text"],
  "pipeline": "text_transformation"
}
```

### Internationalization (i18n)

**Mandatory from Day 1:**
- UI strings in dictionary files (`locales/de.json`, `locales/en.json`)
- Config content multilingual in config files themselves
- Automatic translation augmentation via existing translation pipelines
- Browser language detection with manual override
- Locale persistence in localStorage

### Documentation

**Complete Planning Documents:**
- `docs/tmp/FRONTEND_00_README.md` - Overview
- `docs/tmp/FRONTEND_01_ARCHITECTURE_OVERVIEW.md` - 3-phase architecture
- `docs/tmp/FRONTEND_02_PHASE_1_SCHEMA_SELECTION.md` - Config browser
- `docs/tmp/FRONTEND_03_PHASE_2_3_FLOW_EXPERIENCE_V2.md` - **Entity-based visualization (REVISED)**
- `docs/tmp/FRONTEND_04_VUE_COMPONENT_ARCHITECTURE.md` - Component structure
- `docs/tmp/FRONTEND_05_METADATA_SCHEMA_SPECIFICATION.md` - Metadata schema
- `docs/tmp/FRONTEND_06_VISUAL_DESIGN_PATTERNS.md` - Design system

**Total Documentation:** ~51,000 words

### Implementation Timeline

**Status:** Ready for implementation
**Next Steps:**
1. Set up Vue.js project structure
2. Implement Phase 1 MVP (Tile view only)
3. Implement Phase 2 (Prompt input)
4. Implement Phase 3 (Entity flow visualization)
5. Polish & enhance

**Estimated Timeline:**
- MVP (basic functionality): 2-3 weeks
- V1.0 (full features): 6-8 weeks

### Affected Files

**New Directory:** `/frontend/` (to be created)
**Backend API:** Existing endpoints already support entity-based responses
**Documentation:** All frontend docs in `docs/tmp/FRONTEND_*.md`

---

**Last Updated:** 2025-11-06 (Session 33)
**Active Decisions:** 7
**Status:** Clean, concise, actively maintained

---

## 2025-11-08: Data Flow Architecture - custom_placeholders is THE Mechanism

**Context:** Session 39 discovered that previous session had fundamentally misunderstood the data flow architecture.

**Wrong Understanding (Previous Session):**
- Thought `input_requirements` controls data flow between pipeline stages
- Invented complex nested structures for passing data
- Misunderstood how placeholders work

**Correct Understanding:**
- **`context.custom_placeholders: Dict[str, Any]` is the ONLY mechanism for passing data between stages**
- ChunkBuilder automatically merges custom_placeholders into template replacements as `{{PLACEHOLDERS}}`
- `input_requirements` is **just metadata** for:
  - Stage 1 pre-processing (knows what inputs to translate/safety-check)
  - Frontend UI generation (creates input fields)
- Any data type can pass through - just add it to the dict

**Key Insight:**
The system is simpler than we thought. No need for complex field names or nested structures. Just:
1. Put data in `custom_placeholders`
2. Use `{{KEY}}` in templates
3. ChunkBuilder handles the rest

**Example - Working Music Generation:**
```python
# music_generation config has:
"input_requirements": {"texts": 2}

# Stage 1 knows: process 2 separate text inputs
# Frontend UI shows: 2 text input fields
# Pipeline execution:
context.custom_placeholders['MELODY'] = user_input_1
context.custom_placeholders['LYRICS'] = user_input_2

# Template uses: {{MELODY}} and {{LYRICS}}
```

**Architectural Principle:**
> **"Input requirements describe WHAT arrives at Stage 1. Custom placeholders describe HOW data flows internally."**

**Impact on Vector Fusion:**
- Stage 2 outputs JSON: `{"part_a": "...", "part_b": "..."}`
- JSON auto-parsing adds to custom_placeholders: `PART_A`, `PART_B`
- Stage 4 uses `{{PART_A}}` and `{{PART_B}}` in template
- No complex field names needed, no nested structures

**Documentation:**
- `docs/DATA_FLOW_ARCHITECTURE.md` - Full explanation with examples
- `docs/SESSION_SUMMARY_2025-11-08.md` - Session details
- `docs/archive/HANDOVER_WRONG_2025-11-08_vector_workflows.md` - Wrong understanding archived

**Why This Matters:**
- Prevents future sessions from reinventing complexity
- Shows that extensibility is built-in (any data type works)
- Clarifies the separation of concerns (metadata vs data flow)
- Makes multi-stage workflows simple to implement

