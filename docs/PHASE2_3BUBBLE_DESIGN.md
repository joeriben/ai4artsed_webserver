# Phase 2: 3-Bubble Design with Stage 1+2 Separation

**Date:** 2025-11-08
**Status:** ✅ Frontend Complete | ⏳ Backend Pending
**Branch:** feature/schema-architecture-v2

---

## Overview

Pedagogically superior design that separates **text transformation (Stage 1+2)** from **media generation (Stage 3+4)** in the UI.

### Pedagogical Goals

1. **Maximum Transparency:** Students see each transformation step
2. **Quality Control:** Review transformed prompt before expensive media generation
3. **Learning Opportunity:** Understand what prompt actually goes to Stable Diffusion
4. **Cost/Time Efficiency:** Iterate on text (5-10s) before committing to media (20-30s)

---

## UI Design: 3 Circular Force Nodes

```
┌──────────────────────────────────────────────────┐
│  ← Zurück    🎨 Dada                             │
├──────────────────────────────────────────────────┤
│                                                  │
│   ○ Dein Input         ○ Deine Anweisungen      │ ← Two input forces
│   (WAS) Blue           (WIE) Orange              │
│   Editable             Read-only                 │
│                                                  │
│              ⚙️ Stage 1+2                        │ ← Rotating gear during transform
│           transformiert...                       │
│                                                  │
│              ↓  ↓                                │
│                                                  │
│        ○ Transformierter Prompt                  │ ← 3rd bubble (result)
│        Purple, editable                          │   Grey → Fills purple
│        "Petal-chaos contradicting..."            │
│                                                  │
│  [Beispiele]    [✨ Transformieren]              │ ← Button 1: Transform (Stage 1+2)
│                 [🎨 Weiter zum Bild generieren]  │ ← Button 2: Continue to Phase 3
│                 [🔄 Neu transformieren]          │ ← Button 3: Re-transform
└──────────────────────────────────────────────────┘
```

---

## User Flow

### State 1: Initial (No Transformation)
- Blue bubble: User types input
- Orange bubble: Shows config context (read-only)
- Purple bubble: **Grey, dashed border, "Noch nicht transformiert..."**
- Button: "✨ Transformieren"

### State 2: Transforming (Stage 1+2)
- ⚙️ Gear icon spins in center
- Stage indicator:
  - "Stage 1: Übersetzung + Sicherheit..." (2-3s)
  - "Stage 2: Transformation..." (3-5s)
- Purple bubble still grey

### State 3: Transformed (Ready for Media)
- Purple bubble **fills in** with transformed prompt
- Border changes: dashed → solid
- Opacity: 0.5 → 1.0
- Text becomes **editable** (user can fine-tune!)
- Buttons change:
  - "🎨 Weiter zum Bild generieren" (primary)
  - "🔄 Neu transformieren" (secondary)

### State 4: User Edits Transformed Prompt (Optional)
- Click in purple bubble
- Edit the transformed text
- Changes are sticky (saved for Phase 3)

### State 5: Continue to Phase 3
- Click "Weiter zum Bild generieren"
- Navigate to Phase 3 with:
  - `user_input`
  - `context`
  - `transformed_prompt` (edited or original)
- Phase 3 executes Stage 3+4 (media generation)

---

## Technical Implementation

### Frontend (✅ Complete)

**File:** `public/ai4artsed-frontend/src/views/Phase2CreativeFlowView.vue`

**State Variables:**
```typescript
const userInput = ref('')
const transformedPrompt = ref('')
const isTransforming = ref(false)
const transformationStage = ref<number>(0) // 0=idle, 1=stage1, 2=stage2
```

**Methods:**
- `handleTransform()` - Execute Stage 1+2, fill purple bubble
- `handleReTransform()` - Clear transformed prompt, allow re-execution
- `handleContinueToPhase3()` - Navigate to Phase 3 with transformed prompt
- `handleTransformedPromptEdit()` - User edits the transformed prompt

**CSS Features:**
- `.node-result.is-empty` - Grey, dashed, 50% opacity
- `.node-result.is-filled` - Purple, solid, fade-in animation
- `.llm-icon.rotating` - ⚙️ spins during transformation
- `.transform-btn` / `.continue-btn` - Different gradient buttons

---

### Backend (⏳ Pending)

**Required:** New endpoint for Stage 1+2 only

**Endpoint:** `POST /api/schema/pipeline/transform`

**Request:**
```json
{
  "schema": "dada",
  "input_text": "Eine Blume auf der Wiese",
  "user_language": "de",
  "execution_mode": "eco",
  "safety_level": "kids"
}
```

**Response:**
```json
{
  "success": true,
  "transformed_prompt": "Petal-chaos contradicting meadow-umbrella existence",
  "stage1_output": {
    "translation": "A flower in the meadow",
    "safety_passed": true,
    "safety_score": 0.98
  },
  "stage2_output": {
    "interception_result": "Petal-chaos contradicting meadow-umbrella existence",
    "model_used": "qwen2.5:7b"
  },
  "execution_time_ms": 5234
}
```

**Implementation Location:**
```
devserver/my_app/routes/schema_pipeline_routes.py

@app.route('/api/schema/pipeline/transform', methods=['POST'])
def transform_prompt():
    """
    Execute Stage 1+2 only (no media generation)
    - Stage 1: Translation + Safety check
    - Stage 2: Prompt interception transformation
    Returns: Transformed prompt for Phase 3
    """
    # 1. Load config
    # 2. Execute Stage 1 (translation + safety via pre-interception pipeline)
    # 3. Execute Stage 2 (interception pipeline with config context)
    # 4. Return transformed prompt
```

**Backend Architecture:**
The 4-stage system is ALREADY designed (see ARCHITECTURE.md Section 1). This endpoint just exposes Stage 1+2 separately.

---

### Pinia Store Updates (⏳ Pending)

**File:** `public/ai4artsed-frontend/src/stores/pipelineExecution.ts`

**Add:**
```typescript
const transformedPrompt = ref('')

function updateTransformedPrompt(text: string) {
  transformedPrompt.value = text
}

function clearTransformedPrompt() {
  transformedPrompt.value = ''
}

return {
  // ... existing
  transformedPrompt: computed(() => transformedPrompt.value),
  updateTransformedPrompt,
  clearTransformedPrompt
}
```

---

## Seed Management (Future Feature)

**User Idea:** "After Phase 3, returning to Phase 2 enables either starting again with 3 same prompts (interface/backend will automatically change SEED), or altering any of the inputs (interface/backend will keep the same SEED as before)."

### Concept

**Use Case 1: Re-run with Same Inputs (Different Result)**
- User likes the transformation
- Wants a different image variation
- Returns to Phase 2, clicks "Generate" again
- Backend: **Changes SEED** → different image, same prompt

**Use Case 2: Edit Inputs (Reproducible Result)**
- User wants to tweak the input
- Edits blue or purple bubble
- Clicks "Transform" → "Generate"
- Backend: **Keeps SEED** → reproducible result for debugging

### Implementation Plan (Future)

1. **Store SEED in Phase 3 execution response**
   ```json
   {
     "run_id": "abc123",
     "seed": 42,
     "transformed_prompt": "..."
   }
   ```

2. **Pass SEED back to Phase 2 when navigating**
   - Store in Pinia: `lastSeed`
   - Show indicator: "Using SEED: 42" or "Random SEED"

3. **Backend logic:**
   ```python
   if inputs_changed(current, previous):
       # Keep seed for reproducibility
       seed = request.get('seed', previous_seed)
   else:
       # Generate new seed for variation
       seed = random.randint(0, 2**32 - 1)
   ```

4. **UI Enhancements:**
   - "🎲 Use Random Seed" toggle
   - "📌 Lock Seed: 42" indicator
   - "History" dropdown showing previous runs

**Status:** Not implementing now - just documented the idea.

---

## Different Pipeline Handling

**User Note:** "Different pipelines would demand different handlings here. I think we can deal with this by implementing templates that are coupled with Stage2-pipelines (same name e.g.)."

### Pipeline Types & Phase 2 Behavior

| Pipeline Type | Stage 1+2 | Stage 3+4 | Phase 2 Behavior |
|---------------|-----------|-----------|------------------|
| `text_transformation` | ✅ Yes | ❌ No media | Show result in purple bubble, NO Phase 3 button |
| `single_text_media_generation` | ✅ Yes | ✅ Image | Show transformed prompt, button "Weiter zum Bild" |
| `dual_text_media_generation` | ✅ Yes (2 inputs) | ✅ Music | Need 2 blue bubbles, then continue |
| `image_text_media_generation` | ✅ Yes (image+text) | ✅ Image | Upload image, text input, transform, continue |

### Template System (Future)

**Concept:** Each pipeline could have a Phase 2 UI template:

```
schemas/pipelines/text_transformation.json
  → ui_template: "single_input_no_media"

schemas/pipelines/single_text_media_generation.json
  → ui_template: "single_input_with_media"

schemas/pipelines/dual_text_media_generation.json
  → ui_template: "dual_input_with_media"
```

**Phase 2 Components:**
```
Phase2CreativeFlowView.vue (router)
  ├── Phase2SingleInputTemplate.vue (current implementation)
  ├── Phase2DualInputTemplate.vue (future: 2 blue bubbles)
  └── Phase2ImageTextTemplate.vue (future: image upload + text)
```

**For Now:** Only implement `single_input` template (current design). Other templates can be added later.

---

## Testing Checklist

### Frontend Testing (Can Test Now)

- [ ] Load Phase 2 from Phase 1
- [ ] Purple bubble starts grey/dashed "Noch nicht transformiert..."
- [ ] Type in blue bubble (user input)
- [ ] Click "Transformieren" button
- [ ] ⚙️ Gear appears and rotates
- [ ] Stage indicator shows "Stage 1... Stage 2..."
- [ ] Purple bubble fills in with transformed text (mock)
- [ ] Border changes dashed → solid
- [ ] Can edit purple bubble text
- [ ] Button changes to "Weiter zum Bild generieren"
- [ ] "Neu transformieren" button appears
- [ ] Click "Neu transformieren" → purple clears
- [ ] Click "Weiter..." → shows Phase 3 placeholder alert

### Backend Testing (After Endpoint Created)

- [ ] POST `/api/schema/pipeline/transform` returns transformed prompt
- [ ] Stage 1: Translation works (de → en)
- [ ] Stage 1: Safety check executes
- [ ] Stage 2: Interception uses config context
- [ ] Response time < 10 seconds
- [ ] Error handling for unsafe content
- [ ] Error handling for translation failures

---

## Performance Metrics

**Current (One-Click Execute All Stages):**
- Total time: ~30-40 seconds
- No visibility into transformation
- Can't iterate on text

**New (Separated Stages):**
- Stage 1+2: ~5-10 seconds (text only)
- Review/Edit: 0 seconds (user time)
- Stage 3+4: ~20-30 seconds (media generation)
- **Total time: Same, but with transparency and control**

**Iteration Efficiency:**
- Bad transformation? Fix in 10s (no wasted 30s on media)
- Good transformation, bad image? Re-run Stage 3+4 only
- Debugging: Clear separation of failure points

---

## Pedagogical Impact

### Before (One-Click Black Box)
```
User Input → [??? Magic ???] → Image
```
Students don't understand what happened.

### After (Transparent Stages)
```
User Input (WAS)
   ↓ Stage 1: Translation
"A flower"
   ↓ Stage 1: Safety ✓
   ↓ Stage 2: Dada Transformation
   ↓ + Context (WIE)
"Petal-chaos contradicting meadow-umbrella existence"
   ↓ User reviews: "Perfect!"
   ↓ Phase 3: Stage 3+4
Image generated
```

Students SEE:
- What the transformation did
- How context changed the meaning
- What prompt actually generated the image

**This is the core of counter-hegemonic AI pedagogy.**

---

## Files Modified

### Frontend
1. `public/ai4artsed-frontend/src/views/Phase2CreativeFlowView.vue` - Complete redesign
2. `public/ai4artsed-frontend/src/i18n.ts` - Added 10+ new translations
3. `public/ai4artsed-frontend/src/stores/pipelineExecution.ts` - (Pending: add transformed_prompt)

### Backend (Pending)
1. `devserver/my_app/routes/schema_pipeline_routes.py` - Add `/api/schema/pipeline/transform` endpoint
2. `devserver/schemas/engine/pipeline_executor.py` - (May need method to execute Stage 1+2 only)

### Documentation
1. `docs/PHASE2_3BUBBLE_DESIGN.md` - This file
2. `docs/SESSION_38_PHASE2_REDESIGN.md` - Session history (update)

---

## Next Steps

### Immediate (Frontend Polish)
1. ✅ Test the UI flow
2. ⏳ Add Pinia store integration for transformed_prompt
3. ⏳ Handle edge cases (empty input, safety failures)

### Backend Implementation
1. Create `/api/schema/pipeline/transform` endpoint
2. Implement Stage 1 execution (translation + safety)
3. Implement Stage 2 execution (interception)
4. Return transformed prompt in structured format

### Future Enhancements
1. Seed management system
2. Pipeline-specific templates (dual input, image+text)
3. History/undo system for transformations
4. A/B comparison of transformations

---

**Status:** Frontend implementation complete and ready for testing!
**Next:** Backend endpoint creation for full functionality.

**Session Duration:** ~2 hours
**Implementation Complexity:** Medium (mostly frontend work)
**Pedagogical Value:** ⭐⭐⭐⭐⭐ (Maximum)
