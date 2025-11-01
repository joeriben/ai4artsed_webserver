# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ READ THIS FIRST - MANDATORY

**Before doing ANY work in this repository, read `docs/README_FIRST.md`.**

This project implements **pedagogical concepts** (Prompt Interception, Counter-Hegemonic Pedagogy) that are NOT obvious from code alone. Working without reading documentation WILL break critical features and waste time.

**Required reading time: ~55 minutes**

After reading, you must be able to answer:
- What is "Prompt Interception" and why does it matter pedagogically?
- How did Legacy Server implement it vs. DevServer?
- What is the Three-Layer System (Chunks → Pipelines → Configs)?
- Why are pipelines categorized by INPUT type, not output type?

## 📐 AUTHORITATIVE: 4-Stage Architecture

**Before implementing ANY flow logic, read:**
- **`docs/ARCHITECTURE.md` Section 1** (AUTHORITATIVE - Version 3.0)

Section 1 of ARCHITECTURE.md defines the CORRECT orchestration model:

### Key Principles (Must Understand)
1. **DevServer = Smart Orchestrator** (schema_pipeline_routes.py)
   - Knows about 4-stage flow
   - Orchestrates Stage 1 (translation + safety) based on input types
   - Orchestrates Stage 3-4 per output request

2. **PipelineExecutor = Dumb Engine** (pipeline_executor.py)
   - Just executes chunks
   - NO Stage 1-3 logic inside
   - Returns output_requests for DevServer to handle

3. **Non-Redundant Safety Rules**
   - Pipelines declare: `input_requirements: {texts: 2, images: 1}`
   - DevServer knows: text → translation + safety, image → image safety
   - Safety rules in ONE place, not duplicated in 37+ configs

4. **Stage 3-4 Loop**
   - Stage 2 can request multiple outputs (image + audio)
   - Stage 3-4 run ONCE per output request (not once per pipeline)

**Current Bug (As of 2025-11-01):**
- PipelineExecutor has Stage 1-3 logic inside (WRONG)
- When AUTO-MEDIA calls execute_pipeline('gpt5_image'), it triggers Stage 1-3 again
- Causes redundant translation + safety checks
- **Fix:** Refactor per ARCHITECTURE.md Section 1

## 🚨 CRITICAL: Context Window Full Protocol

### The Problem

When Claude Code's context window fills up, the next session often:
- ❌ Doesn't read documentation (or reads superficially)
- ❌ Starts editing files immediately without understanding
- ❌ Ignores established processes and safety rules
- ❌ Uses `rm` to delete files without asking
- ❌ Breaks critical features due to lack of context

**This is a MAJOR architectural flaw of Claude Code. We must work around it.**

### The Solution: Proper Handover Protocol

When the user says **"Context window is full"** or **"Schreib jetzt alles in .md Dateien"**:

#### Step 1: STOP ALL WORK IMMEDIATELY
- Do NOT continue with the current task
- Do NOT start new implementations
- Do NOT edit any more files

#### Step 2: Create HANDOVER.md
Create `docs/HANDOVER.md` with this EXACT structure:

```markdown
# Session Handover - [Date]

## ⚠️ INSTRUCTIONS FOR NEXT SESSION

**STOP! Before doing ANYTHING:**

1. ✅ Read `docs/README_FIRST.md` completely (~55 min)
2. ✅ Read `docs/HANDOVER.md` (this file)
3. ✅ Read `docs/devserver_todos.md` for current priorities
4. ✅ NEVER use `rm` command without asking user first
5. ✅ NEVER edit files without understanding the full context
6. ✅ NEVER skip documentation reading

**If you don't follow these steps, you WILL break critical features.**

## Current Task

[ONE SENTENCE describing what was being worked on]

**Full details in:** `docs/devserver_todos.md` section [X]

## Current Status

- [ ] Task A - Status: [in progress/blocked/waiting]
- [ ] Task B - Status: [completed but needs testing]

## What Needs to Happen Next

1. [First concrete step]
2. [Second concrete step]
3. See `docs/devserver_todos.md` for full context

## Critical Context

**What you MUST understand before continuing:**
- [Key architectural decision that affects current task]
- [Important constraint or requirement]
- [What NOT to do and why]

## Files Currently Being Modified

- `path/to/file1.py` - Purpose: [brief explanation]
- `path/to/file2.json` - Purpose: [brief explanation]

## Session Metrics

- Session duration: Xh XXm
- Files modified: X files
- Lines changed: +XXX -XXX
- Cost: $XX.XX

**Updated:** `docs/DEVELOPMENT_LOG.md`
```

#### Step 3: Update Required Documentation
1. ✅ Update `docs/DEVELOPMENT_LOG.md` with session stats
2. ✅ Update `docs/devserver_todos.md` with current status
3. ✅ Update `docs/DEVELOPMENT_DECISIONS.md` if architectural changes were made

#### Step 4: Commit Current State
```bash
git add .
git commit -m "chore: Session handover - context window full

[Summary of what was completed]

Next session: See docs/HANDOVER.md
Session cost: $XX.XX"
```

### Rules for NEW Sessions

**If you see a `docs/HANDOVER.md` file:**

1. ⚠️ **MANDATORY:** Read `docs/README_FIRST.md` COMPLETELY before ANY work
2. ⚠️ Read `docs/HANDOVER.md` to understand context
3. ⚠️ Read `docs/devserver_todos.md` to understand priorities
4. ⚠️ Verify you understand the pedagogical concepts (Prompt Interception, etc.)
5. ⚠️ Ask user questions if ANYTHING is unclear
6. ⚠️ Do NOT start editing files until user confirms you understand the context

**NEVER:**
- ❌ Start working immediately without reading docs
- ❌ Use `rm` command without explicit user permission
- ❌ Edit files based on superficial understanding
- ❌ Ignore warnings in HANDOVER.md
- ❌ Skip reading README_FIRST.md "to save time"

**Reading documentation is NOT optional. It saves time and money.**

## Architecture Overview

### Current Migration Status (2025-10-29)

✅ **Completed (Session 4):**
- Frontend 100% migrated to Backend-abstracted architecture
- All 37 configs working with new API (`/api/schema/pipeline/execute`)
- Media polling via Backend (`/api/media/info/{prompt_id}`)
- Media serving via Backend (`/api/media/image/{prompt_id}`)
- Legacy workflow routes deprecated → `.obsolete`
- ComfyUI never accessed directly from Frontend

❌ **Critical Blocker - NOT Implemented:**
- **Pre-Interception 4-Stage System** (translation, safety checks)
- Currently using legacy pre-processing (if any)
- Must be implemented in `PipelineExecutor`, not server routes
- Full design in `docs/PRE_INTERCEPTION_DESIGN.md`

### Three-Layer Pipeline System

DevServer is **NOT** a typical API server. It's a template-based pipeline system with strict layer separation:

```
Layer 3: CONFIGS (Content)
  ↓ references
Layer 2: PIPELINES (Input-Type Orchestration)
  ↓ uses
Layer 1: CHUNKS (Primitive Operations)
```

**Core Principles:**
1. **Input-Type Pipelines**: Categorized by what they consume (not output media or backend)
2. **Backend Transparency**: Same pipeline works with ComfyUI, OpenRouter, or Ollama
3. **No Fourth Layer**: Content belongs in configs, not external registries
4. **Separation of Concerns**: Text transformation ≠ Media generation

### Pipeline Types

| Pipeline | Input | Output | Count |
|----------|-------|--------|-------|
| `text_transformation` | 1 text | Text | 30+ configs |
| `single_prompt_generation` | 1 text | Image/Audio/Video | Multiple configs |
| `dual_prompt_generation` | 2 texts | Music | 1 config (AceStep) |
| `image_plus_text_generation` | Image + Text | Image | Not yet implemented |

## Common Commands

### Development Server

```bash
# Start DevServer (Waitress WSGI server)
python3 server.py

# Server runs on http://localhost:17801
# Frontend: http://localhost:17801
```

**CRITICAL:** The `/server` directory (parent level) is LEGACY and must NEVER be modified. Only work in `/devserver`.

### Testing

```bash
# Architecture tests (fast, no dependencies)
python3 test_refactored_system.py

# Execution tests (requires Ollama running)
python3 test_pipeline_execution.py

# Test specific config
python3 test_pipeline_execution.py dada
```

### Schema/Config Management

```bash
# List available configs
ls schemas/configs/*.json

# Validate JSON syntax
python3 -m json.tool schemas/configs/dada.json

# Test pipeline execution
python3 -c "
from schemas.engine.pipeline_executor import PipelineExecutor
import asyncio
executor = PipelineExecutor('schemas')
result = asyncio.run(executor.execute_pipeline('dada', 'test prompt'))
print(result.final_output)
"
```

### Backend Services

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check ComfyUI status (custom port from config)
curl http://localhost:7821/system_stats

# List running models
ollama list
```

**Current Model Configuration (from config.py):**
- Translation: `mistral-nemo` (changed from gemma2:9b for better quality + 3x faster)
- Safety: `llama-guard3:8b`
- Analysis: `llava:13b` (for vision tasks)
- ComfyUI: Custom port `7821` (not default 8188)

## Key Architecture Concepts

### 1. Chunks (Layer 1: Primitives)

**Location:** `schemas/chunks/*.json`

**Two Types:**
- **Processing Chunks**: Text transformation via LLM (e.g., `manipulate.json`)
- **Output Chunks**: Media generation via ComfyUI (e.g., `output_image_sd35_large.json`)

**Key Design:**
- Processing Chunks use template strings with `{{PLACEHOLDERS}}`
- Output Chunks contain complete ComfyUI API workflows (embedded JSON)
- Chunks specify `backend_type` (ollama/comfyui/openrouter) and `task_type` for model selection

### 2. Pipelines (Layer 2: Orchestration)

**Location:** `schemas/pipelines/*.json`

**Critical Rule:** Pipelines are categorized by **INPUT structure**, not output type or backend.

**Example:**
```json
{
  "name": "single_prompt_generation",
  "description": "Single text → Media (image/audio/video)",
  "chunks": ["output_image"],
  "meta": {
    "input_type": "single_text",
    "output_types": ["image", "audio", "music", "video"],
    "backend_agnostic": true
  }
}
```

### 3. Configs (Layer 3: Content)

**Location:** `schemas/configs/*.json`

**Two Categories:**
1. **Interception Configs** (~30): Text transformation (dada.json, bauhaus.json, etc.)
2. **Output Configs** (~4+): Media generation (sd35_large.json, flux1_dev.json, etc.)

**Key Field - `context`:**
The `context` field contains the complete instruction text (formerly "metaprompt"). This is what gets injected into chunk templates as `{{INSTRUCTION}}`.

**Critical Metadata:**
```json
{
  "pipeline": "text_transformation",  // Which pipeline to use
  "media_preferences": {
    "default_output": "text",  // or "image", "audio", "music", "video"
  },
  "meta": {
    "task_type": "advanced",  // Affects model selection
    "requires_image": true     // For future inpainting support
  }
}
```

### 4. Execution Modes: eco vs fast

**eco mode (default):**
- Local models (Ollama, ComfyUI)
- Free, privacy-preserving, DSGVO-compliant
- Slower but unlimited usage

**fast mode:**
- Cloud APIs (OpenRouter, OpenAI)
- Paid, faster, higher quality
- Non-DSGVO compliant (requires explicit user consent)

**Task-Based Model Selection:**
```python
# In chunks:
"model": "task:translation"  // NOT hardcoded model name

# model_selector.py maps to:
"translation": {
  "eco": "local/qwen2.5-translator",
  "fast": "openrouter/anthropic/claude-3.5-haiku"
}
```

### 5. Backend Routing

**Flow:**
```
Config → Pipeline → Chunk → backend_router.py → Backend Service
```

**Backend Types:**
- `ollama`: Local LLM (mistral-nemo, llama3.2, gemma2)
- `comfyui`: Local media generation (SD3.5, Flux1, Stable Audio)
- `openrouter`: Cloud APIs (Claude, GPT, Gemini)

**Important:** Backend determined by config metadata and execution mode, NOT by pipeline name.

## Critical Implementation Rules

### 1. Where Logic Belongs

**❌ NEVER implement logic in:**
- `my_app/routes/schema_pipeline_routes.py` - Only route handling, no business logic
- Frontend JavaScript - Only UI and API calls

**✅ Logic belongs in:**
- `schemas/engine/pipeline_executor.py` - Pipeline orchestration
- `schemas/engine/backend_router.py` - Backend selection and routing
- `schemas/engine/chunk_builder.py` - Placeholder replacement
- `schemas/configs/*.json` - Content and instructions

### 2. Pre-Interception Pipeline (4-Stage System)

**Status:** ❌ NOT IMPLEMENTED - **CRITICAL BLOCKER FOR COMPLETE MIGRATION**

**Important Design (From Session 5 Recovery):**

Pre-processing (translation, safety checks) should be implemented as **Pipeline Configs**, not server code.

**Designed 4-Stage System:**
```
Stage 1: Pre-Interception (correction + translation + Llama-Guard safety)
  ↓
Stage 2: Interception (user-selected config like dada.json)
  ↓
Stage 3: Pre-Output (safety check + refinement before media generation)
  ↓
Stage 4: Output (media generation)
```

**Critical Documents:**
- **Full Design:** `docs/PRE_INTERCEPTION_DESIGN.md` (user Q&A completed, decisions finalized)
- **Implementation Plan:** `docs/devserver_todos.md` (see "Pre-Interception 4-Stage System Implementation")

**Key Design Decisions (From User Q&A):**
- Correction + Translation: Consolidated in 1 LLM call (performance)
- Llama-Guard: Separate pipeline, obligatory, runs after translation
- Pre-Output: Media-type-specific (image first, audio/video later)
- Safety failure: Text alternative + explanation (NOT abort, NOT silent)
- Performance target: <60s acceptable

**Where Logic MUST Go:**
- ✅ In `schemas/engine/pipeline_executor.py` (pipeline orchestration)
- ❌ NOT in `my_app/routes/schema_pipeline_routes.py` (server routes)

**User Quote:**
> "Es wäre doch konsistenter und transparenter, wenn pre-interception-Maßnahmen durch pre-interception-pipelinconfigs durchgeführt werden und nicht im Servercode verborgen sind."

**Status (2025-10-28):** The system currently uses legacy pre-processing (if any). This MUST be migrated to the 4-Stage Pipeline system before considering the migration "complete".

### 3. Placeholder System

**Available Placeholders:**
- `{{INSTRUCTION}}` - Complete instruction from config.context
- `{{INPUT_TEXT}}` - Original user input (first step only)
- `{{PREVIOUS_OUTPUT}}` - Output from previous chunk (chaining)
- `{{USER_INPUT}}` - Original user input (available in all steps)

**Removed (Post-Consolidation):**
- `{{TASK}}` - Was redundant alias for INSTRUCTION
- `{{CONTEXT}}` - Was redundant alias for INSTRUCTION

### 4. Output-Chunk Structure

Output-Chunks contain **complete ComfyUI API workflows** embedded in JSON:

```json
{
  "name": "output_image_sd35_large",
  "type": "output_chunk",
  "backend_type": "comfyui",
  "media_type": "image",
  "workflow": {
    // Complete ComfyUI API JSON (11+ nodes)
  },
  "input_mappings": {
    "prompt": {"node_id": "10", "field": "inputs.value", ...}
  },
  "output_mapping": {
    "node_id": "19", "output_type": "image", ...
  }
}
```

**No dynamic generation** - workflows are data, not code. The deprecated `comfyui_workflow_generator.py` should NOT be used.

### 5. Frontend Architecture (100% Backend-Abstracted)

**Critical Rule:** Frontend NEVER accesses ComfyUI directly.

**Execution Flow:**
```javascript
// Submit execution
POST /api/schema/pipeline/execute
  → Backend executes pipeline
  → Returns: { final_output, media_output: { output: prompt_id } }

// Poll for media (NEW)
GET /api/media/info/{prompt_id}  // Every second
  → Backend checks ComfyUI internally
  → Returns: { type: "image", files: [...] } OR 404

// Display media (NEW)
<img src="/api/media/image/{prompt_id}">
  → Backend fetches from ComfyUI
  → Returns PNG directly
```

**Benefits:** Backend can replace ComfyUI with SwarmUI, Replicate, etc. without Frontend changes.

## Documentation Requirements

### MANDATORY: Update These Files

Every session MUST update:

1. **DEVELOPMENT_LOG.md** - Session tracking with cost data
   - Session start time, tasks completed, cost breakdown
   - Token usage (input/output/cache)
   - Files modified (lines added/removed)

2. **devserver_todos.md** - Task completion
   - Mark completed tasks with ✅ and timestamp
   - Add new tasks discovered during work

3. **DEVELOPMENT_DECISIONS.md** - Architectural changes
   - Document WHY decisions were made (not just WHAT)
   - Include user quotes, reasoning, alternatives considered

4. **ARCHITECTURE.md** - System structure changes
   - Update when adding/removing components
   - Keep Three-Layer System section current

### When Context Window is Full

**MANDATORY:** Create `docs/HANDOVER.md` following the template in the "Context Window Full Protocol" section above.

**Do NOT:**
- ❌ Continue working without creating handover
- ❌ Pass incomplete context to next session
- ❌ Skip updating DEVELOPMENT_LOG.md

### Git Commit Format

```
[type]: [Brief description]

[Detailed changes]
- Change 1
- Change 2

Session cost: $XX.XX
Session duration: Xh XXm
Files changed: +XXX -XXX lines

Related docs:
- Updated DEVELOPMENT_DECISIONS.md
- Updated devserver_todos.md
```

## Critical Warnings

### ❌ Things That Will Break Pedagogy

1. **Removing Prompt Interception** - This is the core pedagogical concept
2. **Making Configs "More Efficient"** - Content is intentionally verbose for learning
3. **Bypassing Pre-Pipeline** - Users must see transformation process
4. **Direct ComfyUI Access from Frontend** - Breaks backend abstraction

### ❌ Common Mistakes to Avoid

1. **Implementing logic in server routes** - Logic belongs in engine modules
2. **Hardcoding model names** - Use task-based selection (`model: "task:translation"`)
3. **Creating output-type pipelines** - Pipelines are input-type based
4. **Bypassing config metadata** - Frontend must respect config requirements
5. **Not reading documentation first** - Costs time and breaks features
6. **Using `rm` command without asking** - ALWAYS move to .obsolete or ask first
7. **Starting new session without reading HANDOVER.md** - Will break features and waste time
8. **Continuing work when context is full** - STOP and create HANDOVER.md instead

### ✅ When in Doubt

1. Read `docs/README_FIRST.md` - All answers are there
2. Check `docs/DEVELOPMENT_DECISIONS.md` - See why past decisions were made
3. **Check `docs/tmp/` for design documents** - Active design work may be in progress
4. Ask user before architectural changes - Pedagogy overrides technical "optimization"

### ⚠️ Active Design Documents

Before implementing features, check if design documents exist:

**Check These Locations:**
1. `docs/` - Core design documents (e.g., PRE_INTERCEPTION_DESIGN.md)
2. `docs/tmp/` - Active design work, session recoveries, analysis documents
3. `docs/devserver_todos.md` - Lists pending implementations with design document references

**Example:**
If implementing Pre-Interception, read `docs/PRE_INTERCEPTION_DESIGN.md` first - user has already answered all Q&A, decisions are finalized. Don't re-design, just implement.

## File Structure Reference

```
ai4artsed_webserver/
├── server/                   # ⚠️ LEGACY - DO NOT TOUCH
├── devserver/                # ✅ NEW ARCHITECTURE (work here)
│   ├── server.py             # Entry point (runs on port 17801)
│   ├── config.py             # Server configuration
│   ├── schemas/
│   │   ├── chunks/               # Layer 1: Primitive operations
│   │   ├── pipelines/            # Layer 2: Input-type orchestration
│   │   ├── configs/              # Layer 3: Content and metadata
│   │   └── engine/               # Core execution logic
│   │       ├── pipeline_executor.py      # Orchestrates execution
│   │       ├── backend_router.py         # Routes to backends
│   │       ├── chunk_builder.py          # Builds chunks with placeholders
│   │       ├── config_loader.py          # Loads configs/pipelines
│   │       └── model_selector.py         # Task-based model selection
│   ├── my_app/
│   │   ├── routes/
│   │   │   ├── schema_pipeline_routes.py  # Main API endpoint
│   │   │   └── media_routes.py            # Media serving
│   │   └── services/
│   │       ├── ollama_service.py          # Local LLM integration
│   │       └── comfyui_service.py         # Local media generation
│   ├── public_dev/js/
│   │   ├── config-browser.js              # Card-based config selection
│   │   └── execution-handler.js           # Backend-abstracted execution
│   └── docs/
│       ├── README_FIRST.md                # MANDATORY reading
│       ├── ARCHITECTURE.md                # Technical reference
│       ├── DEVELOPMENT_DECISIONS.md       # Decision history
│       └── devserver_todos.md             # Task tracking
```

## Troubleshooting

### Server Won't Start
```bash
# Check if port 17801 is already in use
lsof -i :17801

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if ComfyUI is running (custom port)
curl http://localhost:7821/system_stats
```

### Pipeline Execution Fails
```bash
# Test pipeline directly
python3 test_pipeline_execution.py dada

# Test architecture
python3 test_refactored_system.py

# Check config syntax
python3 -m json.tool schemas/configs/dada.json
```

### Frontend Not Loading
- Check browser console for errors
- Verify server is running on http://localhost:17801
- Check that `public_dev/` directory exists

## Related Resources

- **Main Documentation:** `docs/ARCHITECTURE.md` (comprehensive technical reference)
- **Pedagogical Context:** `docs/LEGACY_SERVER_ARCHITECTURE.md` (explains "why")
- **Pre-Interception Design:** `docs/PRE_INTERCEPTION_DESIGN.md` (4-Stage Pipeline design, user Q&A)
- **Development Decisions:** `docs/DEVELOPMENT_DECISIONS.md` (architectural history)
- **Task Tracking:** `docs/devserver_todos.md` (current priorities)
- **Development Log:** `docs/DEVELOPMENT_LOG.md` (session history and costs - if exists)

---

**Version:** 1.2
**Created:** 2025-10-28
**Last Updated:** 2025-10-29 (Added Context Window Full Protocol)
**Status:** Comprehensive handover protocol added to prevent broken context window transitions

**Changes in 1.2:**
- Added "Context Window Full Protocol" section with mandatory handover procedure
- Added HANDOVER.md template for session transitions
- Updated "Common Mistakes" with context window rules
- Fixed incorrect port (17801), entry point (server.py), ComfyUI port (7821)
- Added troubleshooting section
