# Session Handover - Session 16 → Session 17

**Date:** 2025-11-03
**Branch:** `feature/schema-architecture-v2`
**Last Commit:** (pending) - "refactor: Rename pipelines to input-type convention"

---

## ⚠️ INSTRUCTIONS FOR NEXT SESSION

**STOP! Before doing ANYTHING:**

1. ✅ Read `docs/readme.md` - Project overview
2. ✅ Read `docs/SESSION_HANDOVER.md` (this file)
3. ✅ Read `docs/devserver_todos.md` for current priorities
4. ✅ Read `docs/ARCHITECTURE.md` completely - especially Section 1 on 4-Stage Architecture
5. ✅ NEVER use `rm` command without asking user first
6. ✅ NEVER edit files without understanding the full context
7. ✅ NEVER skip documentation reading

**If you don't follow these steps, you WILL break critical features.**

---

## 🔧 What Was Fixed in Session 16

### CRITICAL FIX: Restored Missing Pipeline

**Problem Identified:**
User reported error: `Config 'sd35_large' not found` during Stage 4 (media generation).

**Root Cause Analysis:**
1. The `single_text_media_generation.json` pipeline file was mistakenly deprecated in Session 15
2. File was renamed to `single_text_media_generation.json.deprecated`
3. Output configs (`sd35_large.json`, `gpt5_image.json`) require this pipeline
4. Without the pipeline, ConfigLoader marked these configs as invalid (pipeline not found)
5. Stage 4 failed because it couldn't load the output config

**Solution Implemented:**
```bash
cd devserver/schemas/pipelines
mv single_text_media_generation.json.deprecated single_text_media_generation.json
```

**Verification:**
- ✅ Config loader now finds 7 pipelines (was 6)
- ✅ `sd35_large` config loads correctly
- ✅ `gpt5_image` config loads correctly
- ✅ Both configs resolve to `single_text_media_generation` pipeline

**Why This Pipeline is Critical:**
According to ARCHITECTURE.md, there are two distinct approaches to media generation:

1. **Direct Generation** (`single_text_media_generation` pipeline):
   - User input → Direct media generation
   - No text transformation/optimization step
   - Used by output configs like `sd35_large`, `gpt5_image`
   - Pipeline chunks: `["output_image"]` only

2. **Optimized Generation** (`image_generation` pipeline):
   - User input → Text optimization (`manipulate`) → Media generation
   - Includes prompt enhancement/refinement
   - Pipeline chunks: `["manipulate", "comfyui_image_generation"]`

The 4-Stage system uses `single_text_media_generation` for Stage 4 because:
- Stage 2 already did text transformation (Prompt Interception)
- Stage 4 should do direct media generation, not transform again
- Deleting this pipeline broke the entire 4-stage flow

---

## 🎯 What Needs to Happen Next

### Immediate Priority: Test the Full 4-Stage Flow

The user requested: "Hier muss etwas repariert werden" (Something needs to be fixed here)

**Next Steps:**
1. Restart devserver to load the restored pipeline
2. Test the full 4-stage execution with `dada` config
3. Verify all stages complete successfully:
   - Stage 1: Pre-Interception (GPT-OSS translation + safety)
   - Stage 2: Interception (Prompt transformation - e.g., Dada)
   - Stage 3: Pre-Output Safety (content filtering)
   - Stage 4: Output Generation (image via sd35_large)

**Test Command:**
```bash
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "dada",
    "input_text": "Eine Blume auf der Wiese",
    "execution_mode": "eco",
    "safety_level": "kids"
  }'
```

**Expected Result:**
- All 4 stages should complete
- No "Config not found" errors
- Image should be generated (or placeholder if ComfyUI not available)

---

## 📋 Session 15 Context (For Reference)

### What Was Completed in Session 15

**Major Achievement:** The 3-part Prompt Interception system (pedagogical core) was fully restored!

**Problem Identified:**
The original ComfyUI `ai4artsed_prompt_interception` custom node used a 3-part prompt structure, but DevServer was only using 2 parts. The critical 3rd element (TASK_INSTRUCTION - telling the LLM HOW to transform) was missing.

**Solution Implemented:**

1. **New Module: `instruction_selector.py`**
   - Location: `devserver/schemas/engine/instruction_selector.py`
   - Mirrors `model_selector.py` architecture
   - Defines INSTRUCTION_TYPES: `artistic_transformation` (default), `passthrough` (testing)
   - Priority: custom override → pipeline instruction_type → fallback

2. **Updated: `manipulate.json` chunk template**
   - Location: `devserver/schemas/chunks/manipulate.json:4`
   - OLD (2-part): `{{INSTRUCTION}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}`
   - NEW (3-part): `Task:\n{{TASK_INSTRUCTION}}\n\nContext:\n{{CONTEXT}}\n\nPrompt:\n{{INPUT_TEXT}}`
   - **Exactly matches original ComfyUI node structure!**

3. **Updated: `chunk_builder.py`**
   - Added `_get_task_instruction()` method (lines 165-184)
   - Updated `replacement_context` with new placeholders:
     - `TASK_INSTRUCTION` - from instruction_selector (how to transform)
     - `CONTEXT` - from config.context (artistic attitude)
     - `INPUT_TEXT` - user's input (the prompt)

4. **Updated: All 32 interception configs**
   - Added `instruction_type` field for transparency/editability
   - 31 configs: `"instruction_type": "artistic_transformation"`
   - 1 config (passthrough): `"instruction_type": "passthrough"`

5. **Updated: `text_transformation.json` pipeline**
   - Added `instruction_type: "artistic_transformation"` field

6. **Testing: ✅ Verified**
   - Created `test_prompt_interception_simple.py`
   - Confirmed 3-part structure matches original ComfyUI node

7. **Documentation: ✅ Complete**
   - `docs/ARCHITECTURE.md`: New section 6 on instruction_selector.py
   - `devserver/CLAUDE.md`: Updated placeholder section

**Git Status from Session 15:**
- Committed: `95f628b`
- Pushed to remote: `feature/schema-architecture-v2`
- Files changed: 45 files (+604 -2720 lines)

**Files Deleted in Session 15 (Cleanup):**
- `docs/ARCHITECTURE.md.backup_20251101`
- `docs/README_FIRST.md`
- `devserver/schemas/pipelines/simple_interception.json`
- `devserver/schemas/pipelines/single_text_media_generation.json` ← **THIS WAS A MISTAKE!**

---

## 🎯 Priority for Next Sessions

### 1. Browser Testing + Interface Design

**Goal 1: Test Prompt Interception in Browser**

1. Start devserver: `./start_devserver.sh` (port 17801)
2. Open: http://localhost:17801
3. Test with configs: dada, bauhaus, passthrough
4. Verify transformation output looks correct

**Goal 2: Design Educational Interface**

**Context from User:**
> "Now that the dev system works basically, our priority should be to develop the interface/frontend according to educational purposes. The schema-pipeline-system has been inspired by the idea that ENDUSER may edit or create new configs."

**Key Principles for UI Design:**

1. **Use Stage 2 pipelines as visual guides**
   - `text_transformation.json` shows the flow: input → manipulate → output
   - Pipeline metadata documents what happens at each step

2. **Make the 3-part structure visible and editable**
   - Show TASK_INSTRUCTION (from instruction_type)
   - Show CONTEXT (from config.context)
   - Show PROMPT (user input)
   - Allow editing of configs

3. **Educational transparency**
   - Students should see HOW their prompt is transformed
   - Students should be able to edit configs to create new styles
   - Students should understand the prompt interception concept

4. **Reference files for UI design**
   - `devserver/schemas/pipelines/*.json` - Flow structure
   - `devserver/schemas/configs/interception/*.json` - Config examples
   - `docs/ARCHITECTURE.md` Section 6 - instruction_selector.py docs

### 2. GPT-OSS Stage 3 Implementation (Deferred)

**From Session 14:** Replace llama-guard3 with GPT-OSS in Stage 3
**Status:** Deferred - Focus shifted to interface design
**See:** `docs/devserver_todos.md` for details

---

## Critical Context

### 3-Part Prompt Interception Structure

**Original ComfyUI node structure:**
```python
full_prompt = (
    f"Task:\n{style_prompt.strip()}\n\n"
    f"Context:\n{input_context.strip()}\nPrompt:\n{input_prompt.strip()}"
)
```

**DevServer implementation (now matches exactly):**
```
Task:
{{TASK_INSTRUCTION}}

Context:
{{CONTEXT}}

Prompt:
{{INPUT_TEXT}}
```

**Mapping:**
- `TASK_INSTRUCTION` = style_prompt (how to transform - from instruction_selector)
- `CONTEXT` = input_context (artistic attitude from config.context)
- `INPUT_TEXT` = input_prompt (user's input)

### Architecture Consistency

The instruction-type system mirrors the model-type system:

```
model_selector.py:         instruction_selector.py:
  6 task types                2 instruction types (extensible)
  eco/fast modes              artistic_transformation/passthrough
  Model selection             Instruction selection

Priority (same for both):
  1. Config-level override
  2. Pipeline-level default
  3. System-level fallback
```

### 4-Stage Architecture Overview

```
Stage 1: Pre-Interception
  - Translation (if needed)
  - GPT-OSS safety check
  - Config: pre_interception/gpt_oss_unified

Stage 2: Interception (Main Pipeline)
  - Prompt transformation (e.g., Dada, Bauhaus)
  - Uses 3-part structure (Task + Context + Prompt)
  - Config: User-selected (e.g., dada, bauhaus)

Stage 3: Pre-Output Safety
  - Keyword filter (stage1_safety_filters.json)
  - LLM context check if keywords found
  - Config: text_safety_check_kids/youth

Stage 4: Output Generation
  - Media generation (image, audio, video)
  - Config: Selected from output_config_defaults.json
  - For eco+image: sd35_large
```

---

## Files Modified This Session (Session 16)

**Restored Files:**
- `devserver/schemas/pipelines/single_text_media_generation.json` - Restored from `.deprecated`

**To Be Committed:**
- This handover document
- Git commit documenting the fix

---

## Known Issues / Future Work

### No Critical Blockers

The pipeline restoration should fix the Stage 4 error. Need to test the full flow.

### Future Enhancements (Not Urgent)

1. Add more instruction types if needed (beyond artistic_transformation/passthrough)
2. Consider custom instruction editor in UI
3. Visual diff tool to compare original vs transformed prompts
4. Implement remaining output pipelines (audio, video, music)

---

## Important Reminders

### For Development

1. **NEVER use `rm` or deprecate files** without understanding full impact
2. **Read ARCHITECTURE.md Section 1** before implementing ANY flow logic
3. **Prompt Interception is pedagogical core** - don't "optimize" it away
4. **Configs are content, not code** - verbose is intentional for learning
5. **Pipelines in `pipelines/` directory are CRITICAL** - don't delete without checking all config references

### For Next Session

**If starting UI work:**
- Read `docs/ARCHITECTURE.md` Section 3 (Three-Layer System)
- Study existing frontend: `devserver/public_dev/js/`
- User wants ENDUSER to edit configs via UI

**If debugging:**
- Check logs: DevServer runs on port 17801
- Test endpoint: `POST /api/schema/pipeline/execute`
- Test configs: dada, bauhaus, passthrough

**Pipeline Dependency Check:**
Before deprecating/deleting ANY pipeline file:
```bash
cd devserver/schemas/configs
grep -r '"pipeline": "PIPELINE_NAME"' **/*.json
```

---

**Last Updated:** 2025-11-03
**Next Session:** Test 4-stage flow, then continue with educational interface design
**Status:** ✅ Critical pipeline restored - Ready for testing!
