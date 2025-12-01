# Session 84 - p5.js Implementation Plan

**Date:** 2025-11-30
**Model:** Claude Opus 4.5
**Focus:** p5.js code generation integration based on validation testing

---

## Phase 0 Validation Results ✅

**Test Environment:** Standalone HTML page (`docs/experiments/p5js_llm_test.html`)

**Key Findings:**
1. ✅ **LLM generates valid p5.js code** - Code runs without errors
2. ✅ **Visual output matches semantic intent** - Scene descriptions translate to recognizable visuals
3. ✅ **Meta-prompt works perfectly** - System prompt from ChatGPT brainstorming is effective
4. ✅ **Multilingual input supported** - Sonnet 4.5 handles German/English without translation
5. ⚠️ **Simple input required** - Standard interception results are too complex for code generation

---

## Critical Discovery: Input Complexity Problem

**Problem:**
Standard interception configs (Dadaism, Bauhaus, Overdrive) produce **complex, poetic, abstract prompts**:
- "COLOSSAL MEGA-FLOWER with ENORMOUS BLAZING PETALS pulsating with INFINITE ENERGY..."
- These are perfect for image generation (Stable Diffusion loves detail)
- But **fail for code generation** (LLM can't translate abstract concepts to geometric shapes)

**Solution:**
Create a **"Simplifier"** Stage 2 config (opposite of Overdrive):
- Input: Complex, poetic user description
- Output: **Simple, geometric scene description** suitable for p5.js
- Example: "A house, some trees, agricultural fields, animals, people" → Perfect for code generation

---

## Implementation Plan

### 1. New Stage 2 Config: `p5js_simplifier`

**File:** `devserver/schemas/configs/interception/p5js_simplifier.json`

**Purpose:** Transform user input into simple, geometric scene descriptions

**Context (Pedagogical Instruction):**
```
You are a visual simplification assistant for creative coding.
Your task: Transform user descriptions into simple, geometric scene descriptions suitable for p5.js sketches.

Guidelines:
- Break down complex descriptions into basic elements (shapes, positions, colors)
- Use concrete, visual language (not abstract/poetic)
- Focus on spatial relationships (foreground/background, left/right, size)
- Identify primitive shapes (rectangles, circles, lines)
- Keep it SHORT and CLEAR (2-4 sentences maximum)

Example transformations:
Input: "Eine wilde, pulsierende Blumenwiese voller Leben und Energie"
Output: "A meadow with grass at the bottom. Several flowers of different sizes and colors. Some small insects flying around. Blue sky with a sun."

Input: "Ein Haus in einer friedlichen Landschaft"
Output: "A simple house (rectangle + triangle roof) in the center. Green grass at the bottom. Blue sky at the top. A tree next to the house. Some bushes in the background."

IMPORTANT: Output only the simplified scene description, no explanation.
```

**Key Properties:**
- Pipeline: `text_transformation` (reuse existing)
- Stage: `interception`
- Output: Simple, geometric scene description
- Language: Multilingual (no translation needed)

---

### 2. New Pipeline: `code_generation`

**File:** `devserver/schemas/pipelines/code_generation.json`

```json
{
  "name": "code_generation",
  "input_requirements": {
    "texts": 1
  },
  "chunks": ["manipulate"],
  "meta": {
    "workflow_type": "code_generation",
    "reusable": true,
    "pre_translation": false,
    "skip_translation": true
  }
}
```

**Key Difference:**
- `skip_translation: true` - Sonnet 4.5 handles multilingual input
- Uses same chunk structure as `text_transformation`
- But routes to different Vue component

---

### 3. New Output Config: `p5js_code`

**File:** `devserver/schemas/configs/output/p5js_code.json`

**Purpose:** Generate p5.js code from simplified scene description

**Optimization Instruction (Meta-Prompt):**
```
You are a p5.js creative coding assistant.
Generate a complete p5.js sketch that can run in the browser with the standard p5.js library.

Requirements:
– Use function setup() and function draw()
– Call createCanvas(800, 600) in setup()
– Do not use external images or fonts
– Use only primitive shapes (rect, ellipse, line, triangle, arc, bezier)
– Use color() for fills and strokes
– Represent depth with size and vertical position (larger/closer, smaller/farther)
– Add variety: different sizes, colors, positions for similar elements
– Include comments to map parts of the code to the scene description
– Output only JavaScript code, no markdown, no explanation

Style guidelines:
– Use variables for positions/sizes to make code readable
– Group related elements in functions (e.g., drawTree(), drawHouse())
– Use HSB color mode for natural color variations
– Add subtle randomness for organic feel (but use randomSeed for reproducibility)
```

**Key Properties:**
- Backend: OpenRouter (not ComfyUI)
- Model: `anthropic/claude-sonnet-4.5`
- Media type: `code`
- Output format: JavaScript (p5.js)

---

### 4. New Vue Component: `code_generation.vue`

**File:** `public/ai4artsed-frontend/src/views/code_generation.vue`

**UI Structure:**

```
┌─────────────────────────────────────────┐
│ Phase 1: Schema Selection              │
│ User selects "p5.js Creative Coding"    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Phase 2A: Input                         │
│ ┌─────────────────────────────────────┐ │
│ │ 📝 Input Text (user description)    │ │
│ │ "Ein Haus in einer Landschaft..."   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 🎯 Context (Simplifier)             │ │
│ │ "Transform into geometric scene..." │ │
│ └─────────────────────────────────────┘ │
│                                         │
│         [Start >>> Button]              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Phase 2B: Interception Result           │
│ ┌─────────────────────────────────────┐ │
│ │ 📝 Simplified Scene (editable)      │ │
│ │ "A simple house (rectangle +        │ │
│ │  triangle roof) in the center..."   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│         [Generate Code >>> Button]      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Phase 3: Code Output                    │
│ ┌───────────────┬─────────────────────┐ │
│ │ 💻 Code       │ 🎬 Live Preview     │ │
│ │ (editable)    │ (p5.js canvas)      │ │
│ │               │                     │ │
│ │ function...   │ [Running sketch]    │ │
│ │               │                     │ │
│ │               │                     │ │
│ └───────────────┴─────────────────────┘ │
│                                         │
│ [▶️ Run] [⏹️ Stop] [📋 Copy] [💾 Save] │
└─────────────────────────────────────────┘
```

**Key Features:**
1. **Code Editor:**
   - Syntax highlighting (Monaco or CodeMirror)
   - Editable code (user can tweak after generation)
   - Line numbers
   - Auto-formatting

2. **Live Preview:**
   - iframe with p5.js loaded from CDN
   - Sandboxed execution
   - JavaScript error handling
   - Real-time update on "Run" button

3. **Controls:**
   - ▶️ Run: Execute code in iframe
   - ⏹️ Stop: Clear canvas / stop animation
   - 📋 Copy: Copy code to clipboard
   - 💾 Save: Download as .js file

4. **Error Display:**
   - JavaScript runtime errors shown in UI
   - Syntax errors highlighted
   - Helpful error messages

---

## Architecture Decision: NEW Pipeline + Vue

**Why p5.js needs its own pipeline:**

| Aspect | Image/Audio Generation | p5.js Code Generation |
|--------|------------------------|----------------------|
| **Input** | Complex, detailed prompts | Simple, geometric descriptions |
| **Output** | Static file (PNG, MP3) | Executable code (JavaScript) |
| **Display** | `<img>` / `<audio>` tag | Code editor + iframe sandbox |
| **Iteration** | Generate new → wait | Edit code → instant re-run |
| **Error handling** | Backend (ComfyUI logs) | Browser (JavaScript console) |

**Conclusion:** p5.js is fundamentally different → needs dedicated pipeline + Vue component.

---

## Implementation Steps

### Backend (Phase 1)
1. ✅ Create `code_generation.json` pipeline
2. ✅ Create `p5js_simplifier.json` interception config
3. ✅ Create `p5js_code.json` output config
4. ✅ Add `code` media type handling to `schema_pipeline_routes.py`
5. ✅ Test API flow: Input → Simplification → Code generation

### Frontend (Phase 2)
1. ✅ Create `code_generation.vue` component
2. ✅ Integrate code editor (Monaco or CodeMirror)
3. ✅ Implement p5.js iframe sandbox
4. ✅ Add execution controls (Run/Stop/Copy)
5. ✅ Error boundary for JavaScript errors
6. ✅ Add to Phase 1 config selection
7. ✅ Add route to Vue Router

### Testing (Phase 3)
1. ✅ Test with example prompts:
   - "A house in a landscape with animals" (German/English)
   - "A forest scene with trees and a path"
   - "An underwater scene with fish and coral"
2. ✅ Test error handling (syntax errors, runtime errors)
3. ✅ Test edit-run cycle (user tweaks code)
4. ✅ Test on different devices (desktop/tablet)

---

## Translation Strategy

**Decision: SKIP TRANSLATION**

**Rationale:**
- Sonnet 4.5 is multilingual (German, English, French, Spanish, etc.)
- Translation adds latency and potential errors
- p5.js code is language-agnostic (JavaScript)
- User can input prompt in ANY language → Sonnet handles it

**Implementation:**
- Set `skip_translation: true` in pipeline meta
- DevServer bypasses Stage 1 translation
- Stage 2 (simplification) works with original language
- Stage 4 (code generation) produces English-commented code

---

## File Locations

**Backend:**
- `devserver/schemas/pipelines/code_generation.json` (NEW)
- `devserver/schemas/configs/interception/p5js_simplifier.json` (NEW)
- `devserver/schemas/configs/output/p5js_code.json` (NEW)
- `devserver/my_app/routes/schema_pipeline_routes.py` (MODIFY - add `code` media type)

**Frontend:**
- `public/ai4artsed-frontend/src/views/code_generation.vue` (NEW)
- `public/ai4artsed-frontend/src/components/P5Sandbox.vue` (NEW - optional)
- `public/ai4artsed-frontend/src/router/index.ts` (MODIFY - add route)
- `public/ai4artsed-frontend/src/views/direct.vue` (MODIFY - add to Phase 1)

**Already Exists:**
- `devserver/my_app/routes/media_routes.py` - `/api/media/p5/<run_id>` route (Session 76)

---

## Pedagogical Context

**Why "Simplifier" is crucial:**

1. **Educational Goal:** Teach students to think in terms of **geometric primitives**
2. **Cognitive Skill:** Decompose complex scenes into basic shapes
3. **Creative Constraint:** Limitations foster creativity (only rectangles/circles/lines)
4. **Iteration Loop:** Simple → Code → Visual → Refine → Repeat

**Example Learning Flow:**
```
Student Input: "Eine wilde Blumenwiese"
       ↓ (Simplifier)
Geometric Description: "Grass (green rectangles at bottom),
                        Flowers (circles of different colors),
                        Sky (blue background)"
       ↓ (Code Generation)
p5.js Code: rect(0, 400, 800, 200); // grass
            ellipse(200, 350, 30, 30); // flower
            ...
       ↓ (Visual Output)
[Student sees geometric interpretation]
       ↓ (Learning)
"Oh, a flower is just a circle on a line!"
```

---

## Future Extensions

### 1. Sonic Pi Integration
- Reuse `code_generation` pipeline
- New config: `sonicpi_simplifier.json`
- New output: `sonicpi_code.json`
- New Vue: Sonic Pi editor (or extend `code_generation.vue`)

### 2. Iterative Refinement
- Add "Regenerate" button with feedback
- User can say "Make the house bigger" → regenerate code
- Chat-based code iteration

### 3. Gallery / Sharing
- Save generated sketches to database
- Share via URL (like p5.js editor)
- Community gallery of student work

### 4. Animation Support
- Extend meta-prompt for `draw()` loop animations
- Add time-based transformations
- Teach concepts like `frameCount`, `sin()`, `cos()`

---

## Success Criteria

✅ **Phase 0 (Validation):**
- [x] LLM generates valid p5.js code
- [x] Visual output matches semantic intent
- [x] Meta-prompt works reliably

✅ **Phase 1 (Backend):**
- [ ] Pipeline routes requests correctly
- [ ] Simplifier reduces complexity
- [ ] Code generation produces runnable JavaScript
- [ ] API returns code in correct format

✅ **Phase 2 (Frontend):**
- [ ] Vue component displays correctly
- [ ] Code editor syntax-highlights JavaScript
- [ ] iframe executes p5.js code
- [ ] Error messages show up in UI
- [ ] User can edit and re-run code

✅ **Phase 3 (Integration):**
- [ ] End-to-end flow works (input → simplify → code → display)
- [ ] Multilingual input handled correctly
- [ ] No crashes or hung states
- [ ] Performance acceptable (<5s total)

---

## Notes

- **Validation file preserved:** `docs/experiments/p5js_llm_test.html` (DO NOT COMMIT)
- **API key security:** Never hardcode keys in HTML/JS files
- **Model choice:** Sonnet 4.5 preferred (multilingual, high quality)
- **Alternative model:** Gemini 1.5 Pro also works well

---

## Next Steps

1. Review this plan with user
2. Get approval for architecture decisions
3. Begin Phase 1 implementation (backend)
4. Test each component independently
5. Integrate frontend
6. End-to-end testing
7. Deploy to production (if successful)
