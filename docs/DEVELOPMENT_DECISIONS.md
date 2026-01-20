# Development Decisions - Current & Active
**AI4ArtsEd DevServer - Active Architectural Decisions**

> **IMPORTANT FOR ALL TASKS:**
> Every significant development decision MUST be documented here.
> Format: Date, Decision, Reasoning, Affected Files

**Full History:** See `docs/archive/DEVELOPMENT_DECISIONS_FULL.md` (2435 lines, Sessions 1-17)

---

## 📋 Quick Reference - Current Architecture

**Current System Status (as of 2025-12-02):**
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

## 🏛️ ARCHITECTURAL PARADIGM: Werkraum → Lab Transition (2026-01-16)

**Status:** ✅ DOCUMENTED (ongoing evolution)
**Context:** Historical transition from workflow-centric to frontend-centric architecture

### The Two Paradigms

| Aspect | Werkraum (Workflow) | Lab (OO/Dezentriert) |
|--------|---------------------|----------------------|
| **Orchestrator** | Server | Frontend/User |
| **Data Flow** | Linear, predetermined | Flexible, user-controlled |
| **Server Role** | "Smart Orchestrator" | "Service Provider" |
| **Client Role** | "Dumb Display" | "Intelligent Composer" |
| **Endpoints** | Unified (server decides stages) | Atomic (client composes services) |

### Historical Context

**Werkraum Era (ComfyUI Workflows):**
- Unidirectional pipeline: Input → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Output
- Server controlled the entire flow
- Frontend was a simple display layer
- Endpoint: `/api/schema/pipeline/execute` handled everything

**Lab Era (Current):**
- Flexible interaction: User can edit any text at any point
- Parallel LLM runs possible
- Every output is editable input for next step
- Frontend orchestrates which services to call

### Architectural Implication: Atomic Backend Services

In the Lab paradigm, the backend provides **atomic services** that the frontend composes:

| Endpoint | Stage | Purpose | Safety |
|----------|-------|---------|--------|
| `/api/schema/pipeline/interception` | 1+2 | User input → Interception | Auto (Stage 1) |
| `/api/schema/pipeline/optimize` | 3a | Model-specific format (clip_g tokens) | No |
| `/api/schema/pipeline/translate` | 3b | German → English translation | No |
| `/api/schema/pipeline/safety` | - | Reusable safety check (for custom flows) | - |
| `/api/schema/pipeline/generation` | 3c+4 | Pre-output safety + Media generation | Auto (Stage 3) |
| `/api/schema/pipeline/legacy` | 1+4 | Direct ComfyUI workflow | Auto (Stage 1) |

**Key Principles:**
1. **Safety is Server responsibility** - Endpoints with user-facing input auto-run safety
   - `/interception` → Stage 1 (Input Safety)
   - `/generation` → Stage 3 (Pre-Output Safety)
   - `/legacy` → Stage 1 (Input Safety)
2. **Atomic services** - Frontend composes the flow, backend executes steps
3. **No skip flags** - Instead of `skip_stage2: true`, just use `/legacy` endpoint

### Example Flows

**text_transformation.vue (Standard Flow):**
```
User Input → /interception (Stage 1+2) → User selects model
           → /optimize + /translate (parallel) → /generation (Stage 4)
```

**surrealizer.vue (Legacy Flow):**
```
User Input → /legacy (Stage 1 + ComfyUI workflow)
```

### Historical Context: Optimization Fix (2026-01-16)

**Bug:** Stage 3 optimization streaming called `/execute`, which always ran Stage 1—redundant.

**Wrong Fix (Werkraum thinking):** Add `skip_stage1` parameter.

**Correct Fix (Lab thinking):** Create `/optimize` endpoint that by design has no Stage 1.

### Coexistence Strategy

Both paradigms coexist in the current codebase:

- **Werkraum patterns** remain for backward compatibility and simpler flows
- **Lab patterns** enable advanced interactive features
- **Migration path:** Gradually decompose unified endpoints into atomic services as needed

### Files Affected

- `schema_pipeline_routes.py`: Both `/execute` (Werkraum) and `/optimize` (Lab) endpoints
- `text_transformation.vue`: Uses Lab pattern (calls atomic services)
- `surrealizer.vue`: Uses Werkraum pattern (single unified call)

---

## 🎯 Active Decision: Unified Export - run_id Across Lab Endpoints (2026-01-17)

**Status:** ✅ IMPLEMENTED
**Context:** Export function was broken - entities split across multiple folders
**Commit:** `7f07197` - `fix(export): Unified run_id and fix image saving for all backends`

### The Problem

In the Lab architecture, `/interception` and `/generation` are **atomic endpoints** called by the frontend. Each endpoint was generating its own `run_id`, resulting in:

- `/interception` → `run_1234_abc/` (input, safety, interception)
- `/generation` → `run_5678_xyz/` (output_image)

**Result:** Export function BROKEN - entities scattered across folders.

### The Solution

**Frontend passes run_id from /interception to /generation:**

```
Frontend (text_transformation.vue)
├── POST /interception → receives run_id in response
├── Stores run_id (currentRunId ref)
└── POST /generation { run_id: currentRunId } → uses SAME folder
```

**Backend changes:**
1. `/interception` initializes Recorder, saves input/safety/interception, returns `run_id`
2. `/generation` accepts optional `run_id`, loads existing Recorder via `load_recorder()`
3. All output entities saved to SAME run folder

### Additional Fix: Multi-Backend Image Saving

**Bug:** Only SD3.5 (`swarmui_generated`) saved images. QWEN, FLUX2, Gemini, GPT-Image failed.

**Root Cause:** Different backends return different output formats:
- `swarmui_generated`: Binary data via SwarmUI API
- `workflow_generated`: `filesystem_path` (QWEN, FLUX2)
- URL outputs: HTTP URLs (Gemini via OpenRouter)
- Base64 outputs: Inline base64 data (OpenAI)

**Fix in `/generation` endpoint:**
```python
elif output_value == 'workflow_generated':
    # Check filesystem_path first (QWEN, FLUX2)
    filesystem_path = output_result.metadata.get('filesystem_path')
    if filesystem_path and os.path.exists(filesystem_path):
        with open(filesystem_path, 'rb') as f:
            file_data = f.read()
        recorder.save_entity(...)
    elif media_files:  # Fallback: Legacy binary data
        ...

# Base64 handling for OpenAI-style outputs
elif output_value and len(output_value) > 100:
    file_data = base64.b64decode(output_value)
    recorder.save_entity(...)
```

### Architectural Note: media_type Consistency ✅ RESOLVED

**User feedback:** The distinction between `media_type: "image"` and `media_type: "image_workflow"` is **ontologically unjustified**.

- SD3.5, QWEN, FLUX2 are ALL image models
- The only valid distinction: image vs video vs audio
- Internal workflow differences should be transparent

**Resolved (2026-01-17):** Eliminated `image_workflow` type - all image models now use `media_type: "image"`.
- Changed `output_image_qwen.json` and `output_image_flux2.json`
- Simplified `backend_router.py` line 749

### Files Modified

| File | Change |
|------|--------|
| `schema_pipeline_routes.py` | Added `load_recorder` import, recorder init in `/interception`, run_id acceptance in `/generation`, filesystem_path + base64 handling |
| `text_transformation.vue` | Added `currentRunId` ref, pass run_id to /generation |

### Test Results

- ✅ SD3.5: Works (unchanged)
- ✅ QWEN: Images saved from `filesystem_path`
- ✅ FLUX2: Images saved from `filesystem_path`
- ✅ Gemini 3 Pro: Images saved from base64
- ✅ GPT-Image: Images saved from base64/URL
- ✅ All entities in ONE unified folder

---

## 🎯 Active Decision: Failsafe Transition - SwarmUI Single Front Door (2026-01-08, Session 116)

**Status:** ✅ IMPLEMENTED
**Context:** Centralizing all traffic through SwarmUI (Port 7801) while preserving legacy workflow compatibility
**Date:** 2026-01-08

### The Decision: Route Legacy Workflows via SwarmUI Proxy

**Problem:**
- Legacy workflows (Surrealizer, etc.) were hardcoded to access ComfyUI directly on Port 7821.
- This bypassed SwarmUI's orchestration, queue management, and user history.
- "Split brain" architecture where some requests went to 7801 and others to 7821.

**Solution:**
- **Single Front Door:** All DevServer traffic goes to **Port 7801** (SwarmUI).
- **Proxy Pattern:** Legacy workflows use SwarmUI's `/ComfyBackendDirect/*` endpoints to reach the managed ComfyUI instance.
- **Config Flag:** `USE_SWARMUI_ORCHESTRATION = True` (default).
- **Emergency Fallback:** `ALLOW_DIRECT_COMFYUI` flag allows reverting to Port 7821 if SwarmUI is down.

### Architecture

**Before (Split):**
```
DevServer
├── New Pipelines ───> SwarmUI (7801) ───> ComfyUI (Internal)
└── Legacy Workflows ──> ComfyUI (7821)
```

**After (Unified):**
```
DevServer
├── New Pipelines ───> SwarmUI (7801) ───> ComfyUI (Internal)
└── Legacy Workflows ──> SwarmUI (7801) ──> /ComfyBackendDirect/ ──> ComfyUI (Internal)
```

### Benefits

1. **Centralized Management:** SwarmUI controls the queue for ALL generations (legacy and new).
2. **Simplified Networking:** Only one port (7801) needs to be exposed/managed.
3. **Compatibility:** Legacy workflows run without modification (transparent proxying).
4. **Resilience:** If SwarmUI is running, ComfyUI is accessible.

### Implementation Details

**Files Modified:**
- `config.py`: Added feature flags.
- `legacy_workflow_service.py`: Dynamic base URL selection.
- `swarmui_client.py`: Added support for legacy image retrieval methods via proxy.
- `backend_router.py`: Updated routing logic for legacy chunks.

---

## 🎓 DESIGN DECISION (2026-01-13): LoRA Training Studio Path Configuration

**Date:** 2026-01-13
**Session:** 115

### Decision

All LoRA training paths must be configured in `config.py` using environment variables with relative fallbacks. No hardcoded absolute paths or usernames in repository code.

### Context

**Problem:**
- Initial training_service.py had hardcoded paths like `/home/joerissen/ai/kohya_ss_new`
- Usernames in git repo = non-portable, security issue
- Different developers/deployments have different directory structures

### Solution

**Path Configuration Pattern:**
```python
# config.py
_AI_TOOLS_BASE = _SERVER_BASE.parent  # Derived from project location

KOHYA_DIR = Path(os.environ.get("KOHYA_DIR", str(_AI_TOOLS_BASE / "kohya_ss_new")))
LORA_OUTPUT_DIR = Path(os.environ.get("LORA_OUTPUT_DIR", str(_AI_TOOLS_BASE / "SwarmUI/Models/loras")))
```

**Model-Specific Prefixes:**
- NOT a global config variable
- Determined by model-specific config generator method
- `_generate_sd35_config()` → adds `"sd35_"` prefix automatically
- Future: `_generate_flux_config()` → adds `"flux_"` prefix

### Affected Files
- `devserver/config.py` - Path variables added
- `devserver/my_app/services/training_service.py` - Imports from config

---

## 🧠 DESIGN DECISION (2026-01-13): VRAM Management for Training

**Date:** 2026-01-13
**Session:** 115

### Decision

Training operations must check available VRAM before starting and offer to clear GPU memory by unloading ComfyUI and Ollama models.

### Context

**Problem:**
- SD3.5 Large LoRA training requires ~50GB VRAM
- ComfyUI models (loaded for image generation) occupy 20-40GB
- Ollama LLMs occupy 10-25GB
- Training fails with OOM if models are loaded

### Solution

**Pre-Training VRAM Check:**
1. `GET /api/training/check-vram` - Returns total/used/free VRAM
2. If `free_gb < 50`: Show warning dialog with "Clear VRAM" option
3. `POST /api/training/clear-vram` - Unloads:
   - ComfyUI: `POST http://127.0.0.1:7821/free`
   - Ollama: `POST /api/generate` with `keep_alive: 0`

**UI Flow:**
```
Click "Start Training"
       ↓
VRAM Check Dialog appears
       ↓
[Enough VRAM?] ──Yes──> "Start Training" button
       ↓ No
"Clear ComfyUI + Ollama VRAM" button
       ↓
VRAM freed, now shows "Start Training"
```

### Affected Files
- `devserver/my_app/routes/training_routes.py` - New endpoints
- `public/ai4artsed-frontend/src/views/TrainingView.vue` - VRAM dialog UI

---

## 🎨 DESIGN DECISION (2026-01-08): Material Design Icon Migration

**Date:** 2026-01-08
**Session:** 115 (Complete Icon System Migration)

### Decision

Replace all emoji icons throughout the frontend with Google Material Design SVG icons.

### Context

**Previous State:**
- Emoji icons (💡📋🖼️✨🖌️📷 etc.) used throughout the UI
- Inconsistent rendering across browsers and operating systems
- Visually dominant and distracting from core content
- Limited customization options (size, color, transitions)

**User Feedback:**
> "Die neuen Icons sind erheblich klarer und ästhetisch weniger dominant. Das gibt unserem träshigen Träshi auch etwas mehr ästhetischen Raum."

### Reasoning

**Visual Hierarchy:**
- Emoji icons were competing for attention with the actual content
- Material Design icons provide clearer, more subtle visual cues
- Allows the "trashy aesthetic" UI design to breathe without icon clutter
- Better balance between functionality and aesthetic space

**Technical Benefits:**
- Sharp, scalable rendering at all sizes
- `currentColor` integration for theme consistency
- No cross-browser rendering inconsistencies
- Standardized Material Design library (maintenance)
- Easier customization (size, color, transitions)

**Pedagogical Alignment:**
- Cleaner interface supports focus on creative process
- Less visual noise = better learning environment
- Icons serve UI function without dominating student attention

### Implementation

**Icon Categories Replaced:**

1. **Property Quadrant Icons (8):**
   - technical_imaging, arts, attitudes, critical_analysis, semantics, research, aesthetics, freestyle
   - Pattern: Conditional SVG rendering with `v-if`/`v-else-if` chains

2. **MediaInputBox Header Icons (6):**
   - Lightbulb (💡), Clipboard (📋), Arrow (➡️), Robot (✨), Image (🖼️), Plus (➕)
   - Supports both emoji and string names for flexibility

3. **Image Upload Icons (4):**
   - Upload prompts, category bubbles (image/video/sound)
   - Responsive sizing: 32px-64px depending on context

**Technical Pattern:**
```vue
<svg v-if="icon === '💡' || icon === 'lightbulb'"
     xmlns="http://www.w3.org/2000/svg"
     height="24" viewBox="0 -960 960 960"
     fill="currentColor">
  <path d="...Google Material Design path data..."/>
</svg>
```

**Color Strategy:**
- All SVGs use `fill="currentColor"` for theme integration
- Property colors based on color psychology:
  * Orange #FF6F00: Emotional warmth (attitudes)
  * Green #4CAF50: Growth, critical thinking (critical_analysis)
  * Cyan #00BCD4: Scientific, analytical (research)
  * Amber #FFC107: Creative freedom (freestyle)

### Files Affected

**Icon Assets (14 new):** `public/ai4artsed-frontend/src/assets/icons/*.svg`
**Components (5):** PropertyBubble, PropertyCanvas, MediaInputBox, ImageUploadWidget, multi_image_transformation

### Commits

- 337f069: Property icons + config preview images + unique colors
- ecad50d: MediaInputBox header icons
- 4821ae7: Image icons inside MediaBoxes
- c00ece5: i18n placeholders + CSS collision fix

### Alternative Considered

**Keep Emoji Icons:**
- Rejected: Cross-platform inconsistencies
- Rejected: Limited customization
- Rejected: Visual dominance conflicts with pedagogical goals

### Future Implications

- Standardized on Material Design library for all future icon additions
- Easier to maintain consistent visual language
- Prepared for potential theming/dark mode in future

---

## 🚨 CRITICAL ARCHITECTURE FIX (2025-12-28): Unified Streaming Orchestration

**Date:** 2025-12-28
**Session:** 111 (Streaming Architecture Refactoring)

### Problem Identified

**Architecture Violation:** The `/api/text_stream/*` endpoints violated the core principle that **DevServer = Smart Orchestrator | Frontend = Dumb Display**.

**Specific Issues:**
1. **Frontend Orchestration:** Frontend was calling stage-specific endpoints (`/api/text_stream/stage2`) directly, deciding which stages to run
2. **Bypassed Safety:** Stage 1 (§86a StGB safety check) was not enforced in streaming mode - frontend could skip it
3. **Security Risk:** Frontend could be manipulated to bypass safety checks (unprofessional, illegal)
4. **Code Duplication:** Interception and Optimization used different endpoints despite being functionally identical

### Solution Implemented

**Architectural Principle Enforced:**
```
Frontend calls ONE endpoint: /api/schema/pipeline/execute
↓
DevServer orchestrates ALL stages (Stage 1 → Stage 2)
↓
Frontend receives SSE stream and displays results
```

**Key Changes:**
1. **Deleted `/api/text_stream/*`** - Entire path removed, violations eliminated
2. **Unified Endpoint:** `/api/schema/pipeline/execute` now supports streaming via `enable_streaming=true`
3. **Mandatory Stage 1:** Safety check ALWAYS runs first (synchronous, ~2-8s), blocks unsafe content
4. **Stage 2 Streaming:** Character-by-character SSE streaming after Stage 1 passes
5. **Unified Architecture:** Interception and Optimization use SAME endpoint, just different parameters

### Technical Implementation

**Backend (`schema_pipeline_routes.py`):**
```python
# Supports both GET (EventSource) and POST (JSON)
@schema_bp.route('/pipeline/execute', methods=['POST', 'GET'])

# Streaming function runs Stage 1 FIRST, always
def execute_pipeline_streaming(data: dict):
    # Stage 1: Safety Check (synchronous)
    is_safe, checked_text, error_message = execute_stage1_gpt_oss_unified(...)
    if not is_safe:
        yield blocked_event  # STOP - DevServer decides
        return

    # Stage 2: Interception (streaming)
    for chunk in ollama_stream:
        yield chunk_event
```

**Frontend (`text_transformation.vue`):**
```typescript
// BOTH Interception and Optimization use same endpoint
streamingUrl = '/api/schema/pipeline/execute'

// Only parameters differ:
// Interception: input_text=user_input, context_prompt=pipeline_context
// Optimization: input_text=interception_result, context_prompt=optimization_instruction
```

### Architectural Principles Established

1. **DevServer = Orchestrator:** Backend decides stage execution order, safety checks, and flow control
2. **Frontend = Display:** Frontend only listens to streams and displays results
3. **Mandatory Safety:** Stage 1 cannot be bypassed - technically impossible
4. **No Duplication:** Functionally identical operations use same code path
5. **Clean Separation:** Orchestration logic lives ONLY in DevServer, never in Frontend

### Files Modified

**Backend:**
- `devserver/my_app/__init__.py` - Removed text_stream_routes import
- `devserver/my_app/routes/schema_pipeline_routes.py` - Added SSE streaming to unified endpoint
- `devserver/my_app/routes/text_stream_routes.py` - **DELETED**

**Frontend:**
- `public/ai4artsed-frontend/src/views/text_transformation.vue` - Updated to use unified endpoint for both Interception and Optimization

### Testing Verification

✅ **Stage 1 Safety:** "HAKENKREUZ" correctly blocked with §86a message, Stage 2 never runs
✅ **Stage 2 Streaming:** "ein blauer Vogel" passes Stage 1, streams character-by-character
✅ **Interception:** Full flow works (Stage 1 → Stage 2 streaming)
✅ **Optimization:** Works identically to Interception (same endpoint, different params)
✅ **Browser Test:** Confirmed working in production-like environment

### Impact

**Security:** ✅ §86a compliance enforced at server level, cannot be bypassed
**Architecture:** ✅ Clean separation of concerns, single source of truth
**Maintainability:** ✅ Less code, no duplication, clear responsibilities
**Professional:** ✅ Industry-standard architecture (backend orchestrates, frontend displays)

---

## Session 110 - 2025-12-22

### Decision: text_transformation.vue Refactoring - Stop After Phase 1

**Context:** File was 2665 lines (26k tokens) with 48% being inline CSS (1285 lines). Maintenance nightmare. Planned 4-phase incremental refactoring.

**Completed:**
- ✅ **Phase 1: Style Extraction** (48% reduction)
  - Created `/src/assets/animations.css` (2.1K) - Shared @keyframes
  - Created `/src/views/text_transformation.css` (26K) - Component styles
  - Updated Vue component to import external CSS
  - Result: 2665 → 1396 lines (48% reduction)
  - Risk: MINIMAL (pure CSS move, zero logic changes)
  - Verification: TypeScript passed, user confirmed "Funktioniert"

**Skipped (Intentionally):**
- ❌ **Phase 2: Component Extraction** (StartButton, CodeEditor)
  - Would reduce by ~10% but involves state management, v-model bindings
  - Risk: LOW-MEDIUM
- ❌ **Phase 3: Selector Extraction** (CategorySelector, ModelSelector)
  - Would reduce by ~15% but complex state, hover logic, metadata loading
  - Risk: MEDIUM-HIGH
- ❌ **Phase 4: Script Optimization** (composables, watchers)
  - Would reduce by ~5% but micro-optimizations
  - Risk: MEDIUM

**Decision:** Stop after Phase 1

**Rationale:**
- **Risk/Benefit Analysis:** Phase 1 achieved 48% reduction with MINIMAL risk
- **Diminishing Returns:** Phase 2-4 would add only ~30% more reduction but MEDIUM-HIGH risk
- **Current State:** File is now maintainable (1396 lines), functional, TypeScript passes
- **Fail-Safety First:** User explicitly chose safety over further optimization
- **User Decision:** "Lassen wir" (Let's leave it at Phase 1)

**Trade-offs:**
- ✅ **Achieved:** Massive maintainability improvement (48% reduction)
- ✅ **Preserved:** Zero breaking changes, fully functional
- ✅ **Avoided:** Risk of introducing bugs through component extraction
- ❌ **Missed:** Could have reached 60-70% reduction if Phase 2-4 completed
- ❌ **Missed:** Component reusability (StartButton could be used elsewhere)

**Impact:**
- **Files Modified:**
  - `src/views/text_transformation.vue` (2665 → 1396 lines)
  - `src/assets/animations.css` (new, 2.1K)
  - `src/views/text_transformation.css` (new, 26K)
- **Commit:** `1ebdba8` - "refactor(text-transformation): Extract inline styles to external CSS files (Phase 1)"
- **Technical Debt:** File still contains ~1100 lines of logic that COULD be extracted, but SHOULD NOT be due to risk

**Lessons Learned:**
1. **Safety First:** 48% improvement with zero risk is better than 70% with potential bugs
2. **Incremental Wins:** Don't chase perfection, achieve "good enough"
3. **Risk Assessment:** Component extraction involves state complexity that CSS doesn't have
4. **User Validation:** "Funktioniert" is the ultimate success metric

**Future Considerations:**
If text_transformation.vue grows significantly in the future (e.g., new media types), revisit Phase 2-4. For now, the file is maintainable and not worth the risk.

---

## Session 109 - 2025-12-22

### Decision: SSE Streaming with Waitress (No Server Migration)

**Context:** SSE text streaming infrastructure implemented in previous session but buffering prevented typewriter effect. Handover document recommended replacing Waitress with Gunicorn.

**User Constraint:** "Not justified to replace a working server for one small animation feature."

**Analysis:**
1. **Gunicorn benefits:** Only helps SSE, NOT WebSockets (would need ASGI for WebSockets)
2. **ComfyUI:** Uses HTTP polling (2s intervals), not streaming - Gunicorn wouldn't help
3. **ASGI migration:** Would require rewriting 50+ routes with async/await (~2-3 weeks effort)
4. **Waitress status:** Stable, works for all other endpoints, simple configuration

**Decision:** Keep Waitress, optimize Flask code instead

**Solution Implemented:**
```python
# Flask explicit flushing forces Waitress to send chunks immediately
from flask import stream_with_context

def generate():
    yield generate_sse_event('chunk', {...})
    yield ''  # Force flush

return Response(stream_with_context(generate()), ...)
```

**Why This Works:**
- `stream_with_context()` maintains request context during streaming
- Empty `yield ''` forces Waitress to flush buffer immediately
- Verified with curl: Chunks arrive progressively (not batched)
- No server replacement needed

**Trade-offs:**
- ✅ Minimal code change (10 lines)
- ✅ Waitress remains stable for all other endpoints
- ✅ Easy to rollback if issues arise
- ❌ Slightly more verbose code (extra yield per chunk)

**Alternative Considered (Rejected):**
- **Gunicorn + gevent:** Would solve SSE buffering but doesn't provide broader benefits (ComfyUI still uses polling)
- **ASGI (Uvicorn + Quart/FastAPI):** Massive migration effort for minimal UX improvement

**Future Path:**
If ComfyUI WebSocket integration is implemented (real-time progress for Stage 4 image generation), use **Flask-SocketIO + eventlet** which works with Waitress (no ASGI needed).

---

### Decision: Dev vs Prod Streaming URLs

**Problem:** Vite dev proxy buffers SSE despite backend fixes. Direct localhost:17802 connection works but fails in production (port 17801).

**Solution:** Environment-aware URL strategy
```javascript
const isDev = import.meta.env.DEV
const url = isDev
  ? `http://localhost:17802/api/text_stream/...`  // Dev: Direct backend
  : `/api/text_stream/...`  // Prod: Relative URL via Nginx
```

**Rationale:**
- **Dev mode:** Vite proxy buffers SSE → use direct backend connection
- **Prod mode:** Nginx doesn't buffer SSE → use relative URL
- **Cloudflare:** Only sees HTTPS requests to domain → not affected by localhost URLs

**Trade-offs:**
- ✅ Works in both environments
- ✅ No CORS issues in prod (relative URL = same origin)
- ✅ No Vite buffering in dev (bypasses proxy)
- ⚠️ Dev requires backend on specific port (17802)

---

### Decision: Runtime Config Loading for user_settings.json

**Problem:** Backend routes imported config at module load time (before user_settings.json loaded)
```python
# WRONG: Import-time binding
from config import STAGE2_INTERCEPTION_MODEL  # Reads before user_settings loaded
model = request.args.get('model', STAGE2_INTERCEPTION_MODEL)  # Uses old value
```

**Root Cause:**
- `_load_user_settings()` runs in `create_app()` and uses `setattr(config, key, value)`
- But route modules import before app creation
- Import-time binding captures old value from config.py

**Solution:** Import module, access attribute at runtime
```python
# RIGHT: Runtime binding
import config  # Import module reference
model = request.args.get('model', config.STAGE2_INTERCEPTION_MODEL)  # Reads current value
```

**Impact:**
- Stage 2 now correctly uses 120b from user_settings.json (not hardcoded 20b)
- All user configuration honored at runtime

**Files Affected:**
- `text_stream_routes.py` (Stage 2, Stage 4)

---

## Session 108 - 2025-12-21

### Decision: Minimal Editable Code Box (No Syntax Highlighting)

**Context:** User requested editable p5.js code output with syntax highlighting (Prism.js) and run button. Initial implementation with Prism.js caused critical blocking issue.

**Problem with Initial Approach:**
```typescript
// BLOCKING: Top-level await in Vue script setup
try {
  const prismModule = await import('prismjs')
  await import('prismjs/themes/prism-tomorrow.css')
  await import('prismjs/components/prism-javascript')
} catch (error) { ... }
```
**Result:** Browser slowdown (Firefox warning), views showing no content, interception_result broken.

**Rollback & Decision:**
- `git reset --hard d5263a3` to restore working state
- User agreed to drop syntax highlighting complexity
- **Decision:** Implement minimal solution without external dependencies

**Final Implementation:**
1. **Editable textarea** - Remove `readonly`, use `v-model="editedCode"`
2. **Run button (▶️)** - Replace clipboard icon, trigger iframe re-render
3. **Vue reactivity** - `watch(outputCode)` to initialize `editedCode`
4. **Key-based re-render** - Increment `iframeKey` to force iframe reload

**Trade-offs:**
- ❌ No syntax highlighting (Prism.js dropped)
- ❌ No complex overlay pattern
- ✅ Zero external dependencies
- ✅ Simple, maintainable code
- ✅ Fast, non-blocking component load
- ✅ User can still edit and run code

**Technical Lesson:**
**Never use top-level `await` in Vue script setup** - it blocks component mounting and breaks reactivity. If async imports are needed, use `onMounted()` hook instead.

**Alternative Considered (Not Implemented):**
Moving Prism import to `onMounted()` would fix blocking issue, but user preferred simplicity over syntax highlighting.

**Files Modified:**
- `public/ai4artsed-frontend/src/views/text_transformation.vue`

**Commits:**
- `576e387` - feat: Add editable p5.js code box with run button (minimal version)
- `4dffb53` - fix: Increase code textarea height to match iframe (400px → 600px)

---

## Session 96 - 2025-12-11

### Decision: Internal App Clipboard for Copy/Paste Buttons
**Context:** All textareas needed consistent copy/paste/delete functionality. Initial approach attempted browser Clipboard API (`navigator.clipboard.readText()`) and `execCommand('paste')`, but both had issues:
- `navigator.clipboard.readText()` requires permission dialog (bad UX)
- `execCommand('paste')` is deprecated and unreliable across browsers

**Decision:** Implement internal app-wide clipboard buffer (`const appClipboard = ref('')`)
- Copy buttons write to `appClipboard.value`
- Paste buttons read from `appClipboard.value` and set directly to textarea refs
- No browser permissions, no deprecated APIs
- Works reliably across all textareas in the app

**Reasoning:**
- Simple, predictable, consistent behavior
- No security dialogs interrupting workflow
- Copy/paste within app is sufficient for the use case (users can still use Ctrl+V for external content)
- Same pattern as existing "Config → Context" functionality

**Affected Files:**
- `public/ai4artsed-frontend/src/views/text_transformation.vue`
  - Added: `appClipboard` ref (line 492)
  - Modified: All copy/paste functions for 5 textareas (inputText, contextPrompt, interceptionResult, optimizedPrompt, outputCode)
  - Added: Copy/Paste/Delete buttons to interceptionResult, optimizedPrompt
  - Added: Copy button to outputCode (readonly)

**Alternative Rejected:** Draft Context feature (Provide/Inject pattern to share form state with Träshy chat) - too complex, didn't solve the core problem, unreliable

---

## 🎯 Active Decision: Input Mappings Pattern for ComfyUI Workflows (2025-12-01, Sessions 84-85)

**Status:** ✅ IMPLEMENTED & TESTED
**Sessions:** 84, 85
**Files Modified:** `backend_router.py`, `legacy_workflow_service.py`
**Config Example:** `/devserver/schemas/chunks/output_image_qwen_img2img.json`

### Summary

Declarative `input_mappings` pattern replaces hardcoded node IDs in prompt injection configs. Enables clean separation between workflow definition and input routing logic.

### Pattern

```json
{
  "input_mappings": {
    "prompt": { "node": 76, "field": "inputs.prompt" },
    "input_image": { "node": 78, "field": "inputs.image" }
  }
}
```

### Rationale

**Why this matters:**
- ComfyUI node IDs vary across workflows (not standardized)
- Multiple nodes can accept same input type (e.g., QWEN's dual TextEncodeQwenImageEdit nodes)
- Hardcoding node paths in prompt_injection config creates maintenance burden
- Declarative approach centralizes workflow-specific routing logic in chunk JSON

**Architectural benefit:**
- Backend becomes generic (reads mappings, injects values)
- Chunks define workflow structure (nodes, connections) AND input routing
- No need for backend code changes per new workflow type

**Implementation detail:**
`legacy_workflow_service.py` prioritizes `input_mappings` from chunk, falls back to legacy `prompt_injection` config for backwards compatibility.

### Related Concepts

- **Execution Mode Routing** - Companion pattern (see below)
- **Chunk Consolidation** - Related simplification decision (ARCHITECTURE PART 15)

---

## 🎯 Active Decision: Execution Mode Routing (2025-12-01, Sessions 84-85)

**Status:** ✅ IMPLEMENTED & TESTED
**Sessions:** 84, 85
**Location:** `backend_router.py` (lines 700-741)
**Config Field:** `execution_mode` in chunk JSON

### Summary

Chunks declare `execution_mode` to specify execution handler. Decouples workflow logic from execution strategy.

### Pattern

```json
{
  "execution_mode": "legacy_workflow"
}
```

**Supported modes:**
- `"legacy_workflow"` - Full ComfyUI workflow via legacy_workflow_service
- Future: `"direct_api"`, `"distributed"`, `"streaming"`, etc.

### Rationale

**Why separation matters:**
- ComfyUI workflows vs direct API calls have different execution paths
- Same workflow might need different handlers in different contexts
- Future optimization (streaming, batching) requires flexibility
- Chunk-level routing enables media-specific execution strategies

**Scalability:**
- New execution mode → Add handler function
- Backend router delegates based on mode
- Workflows unchanged (mode is just metadata)

### Backwards Compatibility

Chunks without `execution_mode` default to `"legacy_workflow"` for legacy workflow chunks.

### Related Decisions

- **Input Mappings Pattern** - Companion pattern
- **Backend Transparency** - Related architectural principle (ARCHITECTURE PART 15)

---

## 🎯 Active Decision: Mode Implementation - Separate Routes (2025-12-01, Sessions 84-85)

**Status:** ✅ IMPLEMENTED & TESTED
**Sessions:** 84, 85
**Routes:** `/text-transformation` (t2i) vs `/image-transformation` (i2i)
**Components:** `text_transformation.vue`, `image_transformation.vue`
**Header Toggle:** Mode selector in navigation bar

### Summary

Text-to-Image (t2i) and Image-to-Image (i2i) workflows implemented via separate routes with identical Stage 2 configs.

### Architecture

```
/text-transformation          /image-transformation
      ↓                              ↓
[Upload text input]          [Upload image input]
      ↓                              ↓
Stage 1: Translation          Stage 1: Image context
      ↓                              ↓
Stage 2: [SHARED CONFIGS]
      ↓
[Kunstgeschichte, Surrealismus, etc.]
      ↓
Stage 3: Safety + Translation
      ↓
Stage 4: Media Generation
      ↓
[sd35_large (t2i only), qwen_img2img (i2i only)]
```

### Key Design Principles

1. **Separate Routes** - Clear t2i vs i2i distinction
2. **Shared Stage 2 Configs** - Pedagogical transformations apply equally
3. **Mode-Specific Output Configs** - Only relevant models available per mode
4. **Header Toggle** - User-facing mode selection

### Why This Approach

**Option Comparison:**
- ❌ Option B (Mode toggle in single route): Creates Route→Mode→Pipeline ambiguity
- ❌ Option C (Graceful fallback): Implicit behavior hard to debug
- ✅ Option A (Separate routes): Clear, explicit, no hidden magic

**Educational value:**
- Users explicitly choose mode (aware of workflow type)
- Interface reflects workflow structure (spatial separation)
- No confusing automatic fallbacks

### Frontend Implementation

Both `text_transformation.vue` and `image_transformation.vue`:
- Mirror identical UI structure
- Use same Stage 2 config selector
- Header shows "📝 Text→Bild" or "🖼️ Bild→Bild" active mode
- Toggle button switches between modes

### Backend Implementation

Both routes call same orchestrator with different initial context:
```python
# /text-transformation
context['input_type'] = 'text'

# /image-transformation
context['input_type'] = 'image'
context['input_image_path'] = upload_result['path']
```

Output configs filter based on `input_type`:
- qwen_img2img: `input_type: "image"`
- sd35_large: `input_type: "text"`

### Status

- ✅ Routes implemented
- ✅ Frontend toggle implemented
- ✅ Output config filtering works
- ✅ End-to-end testing passed
- ✅ German→English translation works for both modes

---

## 🎯 Active Decision: No Optimization UI for img2img (QWEN) (2025-12-02, Session 86)

**Status:** ✅ IMPLEMENTED & COMPLETE
**Sessions:** 85, 86
**Files Modified:** `image_transformation.vue`, `PageHeader.vue` (new)
**Frontend Commit:** d66321e (Session 86 final UI restructure)

### Summary

Image-to-Image (i2i) workflows using QWEN img2img do NOT need the Stage 2 Optimization step that text-to-image (t2i) workflows require. Simplified flow eliminates UI clutter and improves execution speed by ~1 second.

### Why img2img Doesn't Need Optimization

**Comparison:**

| Aspect | Text-to-Image (t2i) | Image-to-Image (i2i) |
|--------|---------------------|----------------------|
| **Pedagogical Transformation** | ✅ Artistic interception (Dada, Bauhaus) | ❌ No artistic transformation needed |
| **Model-Specific Optimization** | ✅ SD3.5 needs prompt refinement | ❌ QWEN works well with direct prompts |
| **UI Complexity** | 3 states (input → interception → optimization) | 2 states (input → generation) |
| **User Experience** | Learn artistic perspectives, then optimize | Describe desired transformation, generate |

### The Architecture

**QWEN img2img Pipeline (Simplified):**
```
Input: Image + Context description
   ↓
Stage 1: Translate context description (German → English)
   ↓
Stage 2: (SKIPPED - no interception/optimization)
   ↓
Stage 3: Safety validation
   ↓
Stage 4: QWEN img2img generation
   - Input: original image + translated context
   - Output: transformed image
```

**vs. Text-to-Image Pipeline (Complex):**
```
Input: Text prompt
   ↓
Stage 1: Translate (German → English)
   ↓
Stage 2a: Pedagogical Interception (artistic transformation)
   ↓
Stage 2b: Model Optimization (SD3.5-specific refinement)
   ↓
Stage 3: Safety validation
   ↓
Stage 4: SD3.5 image generation
```

### Frontend Implementation

**Removed from image_transformation.vue:**
1. Model selection UI (was hardcoded choice between img2img models)
2. Optimization preview box (would show "optimized" prompt)
3. Two-phase "Start" buttons (was Start1 → interception, Start2 → generation)

**Result:**
- Single "Start" button (context description → direct generation)
- No optimization preview
- Faster user workflow
- Less cognitive load
- 100% CSS parity with text_transformation.vue structure

### UI/UX Impact

**Before (Complex):**
- User uploads image + enters description
- Clicks "Start1" (shows optimization preview)
- Sees "optimized" context in box
- Clicks "Start2" (generates image)
- 3+ seconds overhead just for optimization UI

**After (Simple):**
- User uploads image + enters description
- Clicks "Start" (direct generation)
- Sees progress animation
- Image appears
- ~2 seconds faster, simpler workflow

### Design Principle

> **"If optimization_instruction is missing or not pedagogically significant, eliminate it from the UI"**

This applies to:
- img2img with QWEN (confirmed, implemented)
- Future: Video generation with LTX-Video (likely)
- Future: Audio generation with ACEnet (likely)

The backend CAN perform optimization if needed, but the UI doesn't expose it unless it serves a pedagogical purpose.

### Technical Implementation

**Backend (unchanged from Session 85):**
- Pipeline executes stages correctly
- Safety checks still performed
- No `/pipeline/optimize` call for i2i workflows

**Frontend (Session 86 restructure):**
- Extracted PageHeader component (shared with text_transformation.vue)
- Removed category/model selection UI
- Auto-selects config based on mode
- Single cohesive input → generation flow

### Files Changed

**Created:**
- `public/ai4artsed-frontend/src/components/PageHeader.vue` (shared header)

**Modified:**
- `public/ai4artsed-frontend/src/views/image_transformation.vue` (removed optimization section)
- `public/ai4artsed-frontend/src/views/text_transformation.vue` (uses PageHeader component)

### Decision Criteria Applied

✅ **UX Simplification** - Fewer UI elements = less cognitive load
✅ **Performance** - ~1 second faster execution
✅ **Consistency** - Image mode now as simple as t2i mode
✅ **Pedagogical** - No pedagogical value in showing optimization step
✅ **Maintainability** - One less layer of complexity

### Future Reconsideration

If QWEN performance significantly improves with explicit optimization:
- Can add optimization back as hidden background process (no UI changes)
- Users wouldn't be aware, but output quality improves
- Architectural flexibility maintained

### Related Documentation

- **DEVELOPMENT_LOG.md** - Session 86 complete implementation details
- **SESSION_86_I2I_UI_RESTRUCTURE_HANDOVER.md** - Original planning document

---

## 🎯 Active Decision: Progressive Disclosure Scrolling Pattern (2025-11-29, Session 80)

**Status:** ✅ IMPLEMENTED
**Component:** `text_transformation.vue`
**Pattern Name:** Progressive Disclosure for Educational UX

### Summary

Auto-scroll functionality that serves a **didactic purpose** - actively guiding users through distinct phases of the creative-technical workflow to prevent cognitive overload.

### The Pattern

**Three phases of guided progression:**

1. **Scroll1**: After interception → Reveals media category selection
2. **Scroll2**: After category selection → Reveals model options and generation controls
3. **Scroll3**: After generation start → Focuses on output/animation

**Design Principle:** Interface complexity is revealed step-by-step. Each scroll marks a **conceptual transition** in the creative process.

**Key Rule:** Scrolling only moves **downward** (forward progression through pipeline).

### Why This Matters

**Educational UX Design:**
- Users learn workflow structure through **spatial navigation**
- Physical scrolling becomes part of the learning experience
- Prevents overwhelming users with all options simultaneously
- Maintains user agency while providing guidance

**Cognitive Load Management:**
- Complex multi-stage workflows broken into digestible phases
- Interface reveals what's needed when it's needed
- Visual feedback reinforces mental model of pipeline stages

### Implementation Detail

**Critical:** The `.text-transformation-view` uses `position: fixed`, so scrolling must target the **container** (`mainContainerRef`), NOT `window`.

```javascript
// Correct implementation
mainContainerRef.value.scrollTo({
  top: mainContainerRef.value.scrollHeight,
  behavior: 'smooth'
})
```

### Full Documentation

See [ARCHITECTURE PART 12 - Frontend-Architecture.md](./ARCHITECTURE%20PART%2012%20-%20Frontend-Architecture.md#progressive-disclosure-scrolling-pattern) for complete implementation details and code examples.

### Files Changed
- `public/ai4artsed-frontend/src/views/text_transformation.vue`
  - Functions: `scrollDownOnly()`, `scrollToBottomOnly()`
  - CSS: `.output-frame` dimensioning fixed (adaptive to image size)
- `docs/ARCHITECTURE PART 12 - Frontend-Architecture.md` - Pattern documentation

---

## 🎯 Active Decision: Stage 2 Optimization - Two Separate Endpoints (2025-11-26, Session 76)

**Status:** ✅ IMPLEMENTED
**Decision:** Create `/pipeline/optimize` endpoint separate from `/pipeline/stage2`
**Principle:** Two user actions → Two endpoints (not one endpoint with flags)

### Quick Summary

| User Action | Endpoint | Purpose |
|-------------|----------|---------|
| Clicks "Start" Button | `/pipeline/stage2` | Interception with config.context |
| Selects Model | `/pipeline/optimize` | Optimization with optimization_instruction |

### Why This Matters

**From user feedback:**
> "Ich kann - als Mensch - wirklich nicht verstehen wieso Start1 nicht einfach eine Aktion auslösen kann die sich auf die zwei Boxen VOR/OBERHALB von Start 1 beziehen, und der Klick auf das Modell eine Aktion auslösen kann, die sich auf die Box DIREKT DARÜBER bezieht."

**The EINFACHE solution:** Two clear endpoints for two clear operations. No flags, no complex logic.

### Key Architectural Insights

1. **Use PromptInterceptionEngine** - Don't build prompts manually
2. **optimization_instruction goes in CONTEXT** - Not in TASK_INSTRUCTION
3. **Frontend states intent explicitly** - Each click maps to ONE endpoint
4. **No workarounds** - Use the system's modularity
5. **Don't warn about normal behavior** - Only notify for actual errors

**Full details:** See [ARCHITECTURE_STAGE2_SEPARATION.md](./ARCHITECTURE_STAGE2_SEPARATION.md)

### Files Changed
- `devserver/my_app/routes/schema_pipeline_routes.py` - Added `/pipeline/optimize` endpoint
- `public/ai4artsed-frontend/src/views/text_transformation.vue` - runOptimization() calls `/optimize`

---

## 🎯 Active Decision: Stage 2 Refactoring - Separate Interception & Optimization Functions (2025-11-26, Session 75+)

**Status:** ✅ IMPLEMENTED
**Context:** Critical bug fix - config.context contaminating optimization calls
**Date:** 2025-11-26

### The Problem: Mixing Unrelated Operations

**Root Cause Bug:**
The function `execute_stage2_with_optimization()` was combining two COMPLETELY independent operations in a single LLM call:

1. **Interception** (Pedagogical Transformation)
   - Input: User's original text
   - Context: `config.context` (artistic attitude like "analog photography", "dada", "bauhaus")
   - Output: Transformed text with artistic perspective

2. **Optimization** (Model-Specific Refinement)
   - Input: Interception result
   - Context: `optimization_instruction` from output chunk (e.g., "describe as cinematic scene")
   - Output: Text optimized for specific image generation model

**The Bug:**
```python
# OLD (BROKEN):
# config.context ("dada attitude") was leaking into optimization
# optimization_instruction should replace context, not blend with it

original_context = config.context  # "dada attitude"
new_context = original_context + "\n\n" + optimization_instruction  # CONTAMINATED!
```

**Result:** Optimization was using BOTH artistic attitude AND model-specific rules, causing:
- Inefficient prompts (conflicting instructions)
- Confusion about responsibilities
- User-reported bug: "Prompt optimization seems to use config.context instead of optimization instruction"

### The Solution: Complete Separation

**Three Independent Functions:**

1. **`execute_stage2_interception()`** - Pure Interception
   - Purpose: Pedagogical transformation ONLY
   - Uses: `config.context` (artistic attitude)
   - Input: User's text
   - Output: Transformed text
   - **No access to optimization_instruction**

2. **`execute_optimization()`** - Pure Optimization (CRITICAL FIX)
   - Purpose: Model-specific refinement ONLY
   - Uses: `optimization_instruction` from output chunk
   - Input: Interception result (or any text)
   - Output: Optimized prompt
   - **Critical:** Uses Prompt Interception structure CORRECTLY:
     ```python
     full_prompt = (
         f"Task:\nTransform the INPUT according to the rules provided by the CONTEXT.\n\n"
         f"Context:\n{optimization_instruction}\n\n"  # ← optimization_instruction goes HERE
         f"Prompt:\n{input_text}"
     )
     ```
   - **NO access to config.context** - Complete isolation guaranteed
   - **This was the root cause:** optimization_instruction must go in CONTEXT field, not be appended to existing context

3. **`execute_stage2_with_optimization()`** - Deprecated Proxy (Backward Compatibility)
   - Purpose: FAILSAFE - calls the two new functions internally
   - Emits: `DeprecationWarning` to guide future development
   - Result: Returns `Stage2Result` with both:
     - `interception_result` (after Call 1)
     - `optimized_prompt` (after Call 2)
     - `two_phase_execution: true` metadata flag

### Critical Understanding: Prompt Interception Structure

**This refactoring revealed a fundamental misunderstanding:**

In Prompt Interception, the `optimization_instruction` is NOT an additional rule to append to existing context. It IS the context for the transformation:

```python
# WRONG (Old approach):
context = config.context + optimization_instruction  # Blends two contexts

# CORRECT (New approach):
# optimization_instruction IS the CONTEXT (USER_RULES)
full_prompt = f"""Task:
Transform the INPUT according to the rules provided by the CONTEXT.

Context:
{optimization_instruction}

Prompt:
{input_text}"""
```

**Why This Matters:**
- Config.context defines WHO the LLM thinks it is (artistic persona)
- Optimization_instruction defines WHAT the LLM should optimize for (model constraints)
- These are DIFFERENT concerns and must never mix
- The isolated `execute_optimization()` function makes this separation permanent

### Helper Functions Added

1. **`_load_optimization_instruction(output_config_name)`**
   - Loads optimization instruction from output chunk metadata
   - Handles file I/O and error recovery gracefully
   - Returns None if not found (optimization is optional)

2. **`_build_stage2_result(interception_result, optimized_prompt, ...)`**
   - Builds Stage2Result dataclass for backward compatibility
   - Ensures deprecated proxy returns expected structure
   - Includes metadata about which functions ran

### Implementation Details

**Files Modified:**
- `/devserver/my_app/routes/schema_pipeline_routes.py`
  - Lines 123-140: `_load_optimization_instruction()` helper
  - Lines 143-181: `_build_stage2_result()` helper
  - Lines 188-246: New `execute_optimization()` function
  - Lines 248-296: New `execute_stage2_interception()` function
  - Lines 302-421: Backup `execute_stage2_with_optimization_SINGLE_RUN_VERSION()`
  - Lines 424-505: Deprecated proxy `execute_stage2_with_optimization()`

**No Breaking Changes:**
- Deprecated proxy maintains backward compatibility
- Old code calling `execute_stage2_with_optimization()` still works
- DeprecationWarning guides developers to new functions
- All existing configs and pipelines work unchanged

### Testing & Validation

✅ **Isolation Verified:**
- `execute_optimization()` has zero access to config.context
- File scope prevents any config contamination
- Optimization uses ONLY optimization_instruction

✅ **Structure Correct:**
- Prompt Interception pattern correctly implemented
- optimization_instruction in CONTEXT field (not TASK field)
- Task field is generic ("Transform the INPUT...")

✅ **Backward Compatible:**
- Deprecated proxy calls new functions internally
- No API changes for existing callers
- DeprecationWarning guides future refactoring

### Design Principles Applied

1. **NO WORKAROUNDS** - Fixed root problem (context leakage), not symptoms
2. **CLEAN SEPARATION** - Each function has single responsibility
3. **BACKWARD COMPATIBLE** - Deprecated proxy prevents breaking changes
4. **SELF-DOCUMENTING** - Function names express purpose (Interception vs Optimization)
5. **FAILSAFE ARCHITECTURE** - Proxy emits deprecation warnings to guide future work

### Related Documentation

- **ARCHITECTURE PART 01** - Updated Section 1.2 with new function calls
- **Session 75+ Handover** - Complete technical documentation
- **DEVELOPMENT_LOG.md** - Session entry with detailed change log

### Future Work

- Remove deprecated proxy in Session 80+ (after safe period)
- Update Frontend Vue to call new functions directly
- Consider making optimization_instruction mandatory in output chunks
- Potential: Move optimization to separate "Phase 2b" UI state

---

## 🎯 Active Decision 1: Stage 3 Architecture Correction - Translation Placement (2025-11-21, Session 59)

**Status:** 📋 PLANNED (Session 56-58 plan was flawed, corrected in Session 59)
**Context:** Translation placement in 4-stage flow + preserving user edit opportunity
**Date:** 2025-11-21

### The Thinking Error: Session 56-58 "Mega-Prompt" Plan

**Flawed Plan (Session 56-58):**
```
Stage 1: Translation + Safety
Stage 2: Interception + Optimization + Safety (all in ONE "mega-prompt")
Stage 3: ELIMINATED ← "33% faster!"
Stage 4: Media Generation
```

**Why This Was Wrong:**
1. **Pedagogical Error:** Users need to EDIT after optimization, BEFORE final safety
2. **No Edit Opportunity:** Merging Stage 2+3 prevents user from seeing/editing optimized prompt
3. **Lost Transparency:** Prompt interception is for REFLECTION - users must see intermediate results
4. **Misunderstood Goal:** Speed optimization sacrificed pedagogical core principle

### The Correct Architecture (Session 59)

**Revised Plan:**
```
Stage 1: Safety ONLY (NO translation, work in original language DE/EN)
  ↓ Text in German/English (bilingual §86a filters work on both)

Stage 2: Interception + Optimization (in original language, ONE LLM call)
  ↓ Transformed + optimized text (still in German/English)

→ USER CAN EDIT HERE! ← This is the key pedagogical moment!

Stage 3: Translation (DE→EN) + Safety Check
  ↓ English text, safety-approved

Stage 4: Media Generation
```

**Key Changes:**
1. **Translation moved:** Stage 1 → Stage 3
2. **Stage 2 extended:** Add media-specific optimization (SD3.5, Audio, Music)
3. **Edit opportunity preserved:** User edits in native language BEFORE final safety
4. **Stage 3 kept separate:** Not merged into Stage 2

### Why This Is Correct

**Pedagogical:**
- Users work in native language (German) for better reflection
- Users can edit optimized prompt before media generation
- Prompt interception remains transparent (see intermediate steps)
- Aligns with "Gegenhegemoniale Pädagogik" - empowerment through understanding

**Technical:**
- Bilingual §86a filters work on both DE and EN
- Same total execution time (translation still happens once)
- Simpler architecture (no complex "mega-prompt" JSON parsing)
- Clean separation of concerns

### Implementation Plan

**Files to Modify:**
1. `/devserver/schemas/configs/pre_interception/gpt_oss_safety_only_bilingual.json` (NEW)
   - Stage 1: Safety without translation

2. `/devserver/schemas/engine/stage_orchestrator.py`
   - Add `execute_stage1_safety_only_bilingual()`
   - Add `execute_stage3_translation()`

3. `/devserver/my_app/routes/schema_pipeline_routes.py`
   - Update Stage 1 call (use safety-only function)
   - Update Stage 3-4 loop (add translation before safety)

4. `/devserver/schemas/configs/pre_output/translation_de_en_stage3.json` (NEW)
   - Stage 3: Translation DE→EN

**Optional Enhancements:**
5. `/devserver/schemas/chunks/optimize_*.json` (NEW)
   - Media-specific optimization chunks (image, audio, music)

### Related Documentation

- **ARCHITECTURE PART 01** - Updated to reflect correct Stage 1-3 flow (Version 2.1)
- **Session 57-58 Branch:** `feature/stage2-mega-prompt` - DO NOT MERGE (flawed architecture)
- **Develop Branch:** Clean state, start implementation from here

### Lessons Learned

**What Went Wrong:**
- Prioritized speed optimization over pedagogical goals
- Didn't question "why does user need to edit after optimization?"
- Session 56 handover documented flawed plan as if it were fact

**How to Avoid This:**
- Always ask: "What is the pedagogical purpose of each stage?"
- User edit opportunities are CRITICAL in this system
- Document assumptions so they can be challenged
- Consult architecture agent before major changes

---

## 🎯 Active Decision 2: PropertyCanvas Unification - Single Coordinate System (2025-11-21, Session 63)

**Status:** ✅ IMPLEMENTED (Commits e266628 + be3f247)
**Context:** Vue frontend component architecture for property-based config selection
**Date:** 2025-11-21

### The Problem: Coordinate System Mismatch

**Original Architecture (FLAWED):**
```
PropertyQuadrantsView
  ├── PropertyCanvas (category bubbles) → percentage-based positioning
  └── ConfigCanvas (config bubbles)     → pixel-based positioning + different center
```

**Result:**
- Config bubbles appeared in wrong positions (top-right corner)
- Two components calculated center differently
- Mixing percentage and pixel units caused misalignment
- Z-index conflicts between layers

### The Decision: Merge into Single Unified Component

**New Architecture:**
```
PropertyQuadrantsView
  └── PropertyCanvas (unified)
      ├── Category bubbles (percentage positioning)
      └── Config bubbles (percentage positioning, same coordinate system)
```

**Key Changes:**
1. **Merged ConfigCanvas → PropertyCanvas** (commit e266628)
   - Single component manages both category and config bubbles
   - Unified coordinate system (percentage-based)
   - Same center calculation for all bubbles

2. **Added Config Preview Images** (commit be3f247)
   - Preview images from `/config-previews/{config-id}.png`
   - Text badge overlay at 8% from bottom (matches ConfigTile design)
   - Removed fallback letter placeholder system

### Technical Implementation

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

// Configs positioned around parent category
const angle = (index / visibleConfigs.length) * 2 * Math.PI
const configX = categoryX + Math.cos(angle) * OFFSET_DISTANCE
const configY = categoryY + Math.sin(angle) * OFFSET_DISTANCE
```

**Container Sizing:**
```css
.cluster-wrapper {
  width: min(70vw, 70vh);
  height: min(70vw, 70vh);
  position: relative;
}
```

### Benefits

**Technical:**
- Single source of truth for positioning
- Consistent coordinate system (no unit mixing)
- Simpler component hierarchy (one less component)
- Easier to maintain and debug

**Visual:**
- Config bubbles correctly positioned around categories
- Smooth transitions and animations
- Consistent styling across all bubbles
- Preview images provide immediate visual recognition

### Files Modified

**Deleted:**
- `public/ai4artsed-frontend/src/components/ConfigCanvas.vue` (merged into PropertyCanvas)

**Modified:**
- `public/ai4artsed-frontend/src/components/PropertyCanvas.vue` (integrated ConfigCanvas logic)
- `public/ai4artsed-frontend/src/views/PropertyQuadrantsView.vue` (removed ConfigCanvas reference)
- `public/ai4artsed-frontend/src/assets/main.css` (updated styles)

**Archived (Backup):**
- `public/ai4artsed-frontend/src/components/PropertyBubble.vue.archive`
- `public/ai4artsed-frontend/src/views/PropertyQuadrantsView.vue.archive`

### Lessons Learned

**What Went Wrong:**
- Splitting category and config bubbles into separate components seemed logical initially
- Each component developed its own positioning logic independently
- Coordinate system mismatch wasn't obvious until visual testing

**Why This Solution Works:**
- Single component = single coordinate system
- Percentage-based positioning scales consistently
- Relative positioning within same container eliminates offset bugs

**General Principle:**
When components share the same visual space and coordinate system, they should be part of the same component to avoid positioning mismatches.

### Related Documentation

- **ARCHITECTURE PART 12 - Frontend-Architecture.md** - Full component documentation
- **docs/PropertyCanvas_Problem.md** - Centering issue (still under investigation)
- **docs/SESSION_62_CENTERING_PROBLEM.md** - Historical debugging notes

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


---

## Session 94: Surrealizer/Direct Vue Separation (2025-12-12)

### Decision: Create Dedicated surrealizer.vue While Preserving Generic direct.vue

**Context:**
- Surrealizer is production-stable workflow with alpha slider (-75 to +75)
- User has 2-3 additional Hacking workflows in ComfyUI
- Previous attempts at routing changes failed due to misunderstanding convention-based routing

**Problem:**
- `surrealizer.json` config pointed to `direct` pipeline → loaded `direct.vue` with dropdown
- Dropdown caused confusion for production workflow
- User wanted dedicated Vue for each stable workflow

**Architecture Decision:**

**Production Workflow (Dedicated):**
```
surrealizer.json config → surrealizer.json pipeline → surrealizer.vue
- Hardcoded to surrealization_legacy output config
- Alpha slider (-75 to +75) with 5 labels
- No dropdown selection
- Clean, focused UX for workshop use
```

**Convention-Based Routing Pattern:**
```
Config JSON → Pipeline JSON → Vue Component
├─ "pipeline": "X" → ├─ "name": "X" → X.vue
└─ (Stage 2 config)  └─ (Pipeline def)   └─ (Frontend)
```

**Critical Insight - Why Previous Attempts Failed:**
1. **Pipeline name MUST exactly match Vue filename** (case-sensitive!)
2. **Correct order of creation:**
   - ✅ FIRST: Create Vue component
   - ✅ THEN: Create pipeline definition
   - ✅ LAST: Update config reference
   - ❌ WRONG: Change config first (breaks routing before Vue exists)

3. **No explicit registry needed** - PipelineRouter.vue uses dynamic import:
   ```typescript
   import(`../views/${pipelineName}.vue`)
   ```

**Files Created:**
- `/devserver/schemas/pipelines/surrealizer.json` (new pipeline, reusable: false)
- `/public/ai4artsed-frontend/src/views/surrealizer.vue` (dedicated component)

**Files Modified:**
- `/devserver/schemas/configs/interception/surrealizer.json` (pipeline: "surrealizer")

**Changes in surrealizer.vue:**
- Removed output config dropdown section
- Removed `availableConfigs` array
- Removed `selectedOutputConfig` ref
- Hardcoded API call: `output_config: 'surrealization_legacy'`
- Simplified `canExecute` computed (no config check)

**Testing:**
```bash
curl http://localhost:17802/api/config/surrealizer/pipeline
# Returns: {"pipeline_name": "surrealizer", ...}
```

**Benefits:**
- **Production stability** - Dedicated Vue, no accidental config changes
- **Clean UX** - No dropdown confusion for workshop students
- **Scalability** - Pattern ready for 2-3 additional Hacking workflows
- **Zero router changes** - Convention-based routing handles automatically

**Migration Path for Future Workflows:**
1. **Stable/Production workflow** → Create dedicated Vue (like Surrealizer)
2. **Experimental/Research** → Keep in `direct.vue` with dropdown (if reactivated)

**Architectural Note:**
The `direct_workflow.json` config was deactivated (`.deactivated` suffix) during this session. If needed in future, it can be reactivated as a generic "Hacking Lab" with dropdown for experimental workflows.

**Documentation:**
- Plan file: `/home/joerissen/.claude/plans/hashed-stargazing-dongarra.md`
- Contains complete routing simulation with line numbers
- Shows exact data flow through Backend (lines 2931, 2937, 2945) and Frontend (lines 31, 37)

**Session Commits:**
- `4a52aa1` - Enhanced slider (5 labels, gradient, 48px thumb)
- `c332f48` - Dedicated surrealizer.vue with routing separation

**Why This Documentation Matters:**
- **Future-proofing:** Next time routing needs to change, follow this pattern
- **Prevents regression:** Explicit order of operations prevents breaking changes
- **Educational:** Shows convention-based routing is simpler than explicit registry
- **Template:** Use for displaced_world, relational_inquiry, other new workflows

