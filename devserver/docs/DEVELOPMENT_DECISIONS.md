# Development Decisions Log
**AI4ArtsEd DevServer - Chronological Decision History**

> **WICHTIG FÜR ALLE TASKS:**
> Jede bedeutende Entwicklungsentscheidung MUSS hier eingetragen werden.
> Format: Datum, Entscheidung, Begründung, betroffene Dateien

---

## 2025-11-02: Safety Filter Enhancement (§86a StGB Compliance + Hybrid System Optimization)

### Decision
**Extended Stage 1 safety filters with German extremist symbols/terms (§86a StGB) and optimized for hybrid string-filter → llama-guard system**

**Actions Taken:**
1. ✅ Added German §86a StGB forbidden symbols/organizations to `stage1_safety_filters.json`
2. ✅ Simplified ambiguous terms (removed context qualifiers like "terrorist", "flag")
3. ✅ Added German language equivalents (völkermord, schwarze sonne, etc.)
4. ✅ Added numerical/abbreviated codes (88, HH, 14 words)
5. ✅ Updated documentation to reflect hybrid filtering strategy

### Reasoning

**Problem: Legal Compliance Gap**
- Original filter focused on US-based threats (CSAM, violence, hate speech)
- Missing German legal requirements (§86a StGB - forbidden symbols)
- Germany requires blocking: Nazi symbols, extremist organizations (RAF, PKK, ISIS flags)
- School context requires strict compliance for educational use

**User Request:**
> "ergänze die Safety-Filter-Listen auch um extremistische Symbole. Die sind in den USA erlaubt, in der BRD aber nicht, z.B. Hakenkreuze, antisemitische Symbole etc."

### Solution: Hybrid System Architecture Understanding

**Critical Insight - The Hybrid Flow:**
```
User input → Fast string filter → If match: llama-guard3:8b assessment
                                 → If no match: Pass (fast path)
```

**Key Realization:**
- String filter does NOT immediately block - it triggers LLM review
- False positives (e.g., "isis" goddess) → llama-guard clears them
- False negatives (missed threats) → llama-guard catches them
- This allows AGGRESSIVE string filtering without blocking legitimate content

**Design Decision: Simplify Ambiguous Terms**

Initial approach (wrong):
- "isis flag", "isis terrorist", "raf terrorist" (with context qualifiers)
- Reasoning: Avoid blocking "ISIS" goddess or "RAF" air force

Corrected approach (right):
- "isis", "raf", "pkk" (without context qualifiers)
- Reasoning: String match only triggers review, llama-guard handles context

**User Correction:**
> "however, ISIS and the likes should be included in the filter list. actually, any terms that are also harmless can be on this list because if there is a hit, it will not just block but try to understand the context."

### Added Terms

**German Nazi Symbols (§86a StGB):**
- hakenkreuz, nazisymbol, ss-runen, ss-symbol
- schwarze sonne, sonnenrad, wolfsangel
- reichskriegsflagge, totenkopf-ss, waffen-ss
- blut und boden, blut und ehre

**German Language Equivalents:**
- völkermord (genocide), shoa (Holocaust)
- eisernes kreuz nazi (iron cross)

**Extremist Organizations:**
- isis, raf, pkk, taliban, al qaeda
- rote armee fraktion, kurdistan workers party

**Codes & Abbreviations:**
- 88, hh (Heil Hitler)
- 14 words, blood and soil

### Architecture Notes

**Stage 1 vs Stage 3 Separation:**
- **Stage 1 (universal):** All users, all ages → Blocks extremism, CSAM, violence
- **Stage 3 (age-specific):** kids/youth only → Blocks age-inappropriate content (scary, horror, dark)
- NO redundancy: Extremist symbols belong in Stage 1 only

**Visual vs Textual Distinction:**
- Visual symbols (swastika): Cannot contextualize in image generation → Strict block
- Textual terms (isis, raf): AI interprets from context → Trigger review only

### Files Modified
- `schemas/stage1_safety_filters.json`
  - Added ~20 German terms
  - Simplified ambiguous terms (removed qualifiers)
  - Updated note to explain hybrid system

### Related Documentation
- ARCHITECTURE.md Section 1.3 - Stage 1 rules (translation + safety)
- README_FIRST.md - Safety as pedagogical requirement

---

## 2025-11-02: GPT-OSS-20b as Unified Stage 1-3 Model + VRAM Management Strategy

### Decision
**Adopt OpenAI's gpt-oss-safeguard-20b as unified model for Stage 1 (Translation), Stage 2 (Interception), and Stage 3 (Safety), replacing the current multi-model architecture (mistral-nemo + llama-guard3).**

**Status:** RESEARCH COMPLETE, Implementation pending
**Impact:** MAJOR - Makes entire model_selector.py architecture obsolete

### Context: The Multi-Model Problem

**Current Architecture (Before GPT-OSS):**
```
Stage 1: Translation → mistral-nemo (8B, 1-2s)
Stage 1: Safety     → llama-guard3:8b (1-2s)
Stage 2: Interception → mistral-nemo (8B, 1-2s)
Stage 3: Pre-Output Safety → llama-guard3:8b (1-2s)

Total per request: 4-6s (+ 2-3s model loading overhead)
Memory: Load/unload different models → VRAM thrashing
Code: Complex model_selector.py with task-based mapping
```

**Problems:**
1. **Performance:** 2 different models loaded/unloaded repeatedly
2. **Complexity:** model_selector.py maps tasks to models for eco/fast modes
3. **VRAM Management:** 24GB/32GB cards struggle with model swapping + ComfyUI
4. **Quality:** Separate models for translation and safety (no context sharing)

**User Insight:**
> "wait, Denkfehler: wenn wir in stage 2 auch GPT-OSS verwenden könnten? müssen wir es gar nicht unloaden."

### Research: GPT-OSS-20b Testing Results

**Model Specs:**
- Full name: `openai/gpt-oss-safeguard-20b`
- Parameters: 21B total, 3.6B active (MoE - Mixture of Experts)
- VRAM: 16GB (fits in 24GB cards with room for other processes)
- Performance: Fast as 8B models due to MoE architecture

**Test Methodology:**
- Created 3 test scripts testing Translation, Safety, Artistic Transformation
- Tested with/without §86a StGB system prompt
- Tested with/without Arts Education context
- Compared quality, performance, false positive/negative rates

**Results:**

**1. Translation + Typo Correction: ⭐⭐⭐⭐⭐ Excellent**
- Input: "Eien Bluhme auf der Wiesse" (children's spelling errors)
- Output: "A flower on the meadow" (correct translation + typo correction)
- Quality: Superior to mistral-nemo
- Context-aware: "Haustir" → "Haustier" (pet) not "Haustür" (door) in Arts Education context

**2. Artistic Transformation: ⭐⭐⭐⭐⭐ Outstanding**
- Dada transformation: Innovative, non-clichéd responses
- Bauhaus transformation: Perfect geometric reduction, functional language
- Quality: Matches mistral-nemo artistic capabilities

**3. Safety (§86a StGB): ⭐⭐⭐⭐⭐ WITH explicit German law prompt**
- WITHOUT §86a prompt: "Hakenkreuz Fahne" → SAFE (neutral mention) ❌
- WITH §86a prompt: "Hakenkreuz Fahne" → UNSAFE (§86a violation) ✅
- False positive handling: "ISIS goddess" → SAFE ✓ (correct)
- False negative prevention: "ISIS terrorist flag" → UNSAFE ✓ (correct)

**Critical Discovery:**
> Model is highly configurable via system prompt. US-centric by default, but correctly applies German law when explicitly instructed.

### Solution Architecture: Unified Single-Model System

**New Architecture (After GPT-OSS):**
```
Stage 1: Translation → gpt-oss-20b (16GB, 2s)
Stage 1: Safety     → (INTEGRATED - same model context)
Stage 2: Interception → gpt-oss-20b (REUSED - already in VRAM)
Stage 3: Pre-Output Safety → gpt-oss-20b (REUSED - already in VRAM)

Total per request: 2-3s (single model, no loading overhead)
Memory: Keep loaded Stage 1-3, unload only before ComfyUI Stage 4
Code: model_selector.py becomes OBSOLETE
```

**Performance Improvement:**
- Current: 4-6s (2 models, repeated loading)
- New: 2-3s (1 model, stays loaded)
- **Savings: 30-50% faster + better quality**

### VRAM Management Strategy

**Problem:**
- GPT-OSS: 16GB VRAM
- ComfyUI (SD3.5/Flux): 12-15GB VRAM
- Total: 28-31GB (exceeds 24GB cards)

**Solution: Dynamic Loading by Backend**
```python
# Stage 1-3: Keep GPT-OSS loaded
ollama.generate(model="gpt-oss-20b", keep_alive="10m")

# Stage 4 Decision Point:
if backend == "comfyui":
    # Unload GPT-OSS before ComfyUI
    ollama.generate(model="gpt-oss-20b", keep_alive="0s")
elif backend == "api":  # GPT-5 Image, OpenRouter, etc.
    # Keep GPT-OSS loaded (API doesn't use local VRAM)
    pass  # No unload needed
```

**Benefits:**
- API-based workflows (GPT-5 Image): No VRAM conflict, keep model loaded
- ComfyUI workflows: Explicit unload prevents OOM errors
- Next request: Model stays in VRAM if within 10m window

### §86a StGB System Prompt Integration

**Problem:** GPT-OSS-20b is US-centric by default (First Amendment standards)

**Solution:** Explicit German legal framework in system prompt

```python
GPT_OSS_STAGE1_SYSTEM = """You assist children/adolescents (ages 8-17) in Arts Education.

LEGAL FRAMEWORK: §86a StGB (Strafgesetzbuch - German Criminal Code)
In Germany, it is ILLEGAL to display, distribute, or use symbols of:
- Nazi organizations (swastika/hakenkreuz, SS runes, Hitler salute)
- Terrorist organizations (ISIS flags, PKK symbols, RAF symbols)
- Extremist organizations (KKK, white supremacist symbols)

Educational/historical context does NOT make these symbols legal in Germany.
A "neutral mention" of a swastika flag is STILL ILLEGAL under §86a StGB.

TASKS:
1. CORRECT SPELLING for creative image prompts
   - Ambiguous typos: Interpret as creative subjects (Haustir→Haustier not Haustür)
   - Children want to create images of interesting things (animals, scenes)
2. TRANSLATE German→English (preserve creative structure)
3. SAFETY CHECK: Block §86a StGB violations, violence, CSAM, hate speech

OUTPUT:
- Translated text OR
- "BLOCKED: §86a StGB - [specific reason]"
"""
```

**Key Elements:**
1. Arts Education context (typo interpretation)
2. Explicit §86a StGB legal reference
3. Clear violation examples
4. Integrated Translation + Safety in single pass

### Performance Analysis

**Current Multi-Model System:**
```
Translation:     mistral-nemo (8B)    1-2s
Safety Check 1:  llama-guard3 (8B)    1-2s
Interception:    mistral-nemo (8B)    1-2s (reload or reuse?)
Safety Check 2:  llama-guard3 (8B)    1-2s (reload or reuse?)
────────────────────────────────────────────
Total:           4-6s per request
Models:          2 different models
Loading:         2-3s overhead per model switch
```

**New Unified GPT-OSS System:**
```
Stage 1 (Translation + Safety):  gpt-oss-20b (21B/3.6B active)  2-3s
Stage 2 (Interception):          gpt-oss-20b (REUSED)          0.5s
Stage 3 (Pre-Output Safety):     gpt-oss-20b (REUSED)          0.5s
────────────────────────────────────────────────────────────────────
Total:           3-4s per request
Models:          1 unified model
Loading:         0s (stays in VRAM)
```

**Quality Improvements:**
- Shared context across stages (model "remembers" translation choices)
- Better typo correction (Arts Education context)
- Consistent safety standards (same model, same prompt)
- Superior artistic transformation (proven in tests)

### Architecture Impact: Model Selector Obsolescence

**CRITICAL: This decision makes the following architecture OBSOLETE:**

**Files That Can Be Removed (After Implementation + Testing):**
1. `schemas/engine/model_selector.py` - Entire file becomes unnecessary
2. Task-based model mapping (`task:translation`, `task:safety`, etc.)
3. Eco/fast mode model switching logic
4. Complex model selection in chunk_builder.py

**Why Obsolete:**
- Single model handles all tasks → No task-based selection needed
- Same model for eco/fast → No mode-based switching needed
- OpenRouter/Ollama distinction remains, but simpler:
  - Ollama: `gpt-oss-20b` (local)
  - OpenRouter: `openai/gpt-oss-safeguard-20b` (API)

**Code Simplification:**
```python
# BEFORE (complex):
from .model_selector import model_selector
base_model = resolved_config.meta.get('model_override') or template.model
final_model = model_selector.select_model_for_mode(base_model, execution_mode)

# AFTER (simple):
model = "gpt-oss-20b"  # Always, for all tasks
```

**User Statement:**
> "Immerhin macht diese Entscheidung die komplette aufwändige Model-Selektion und das Mapping lokal-> Openrouter überflüssig. Dieser ganze Code kann eigentlich entfernt werden (würde ich jetzt im Code ggf. auskommentieren, aber noch nicht entfernen, da wichtigeres zu tun ist, und wir GPT-OSS auch noch im Einsatz testen müssen)."

### Implementation Status

**✅ Completed:**
- Research phase (3 test scripts, comprehensive testing)
- §86a StGB compliance testing (WITH/WITHOUT prompt comparison)
- Arts Education context testing (typo disambiguation)
- Performance benchmarking
- VRAM management strategy design
- System prompt template design
- Documentation in devserver_todos.md

**⏳ Pending Implementation:**
- [ ] Update config.py: MODEL constants → `gpt-oss-20b`
- [ ] Implement §86a StGB system prompt in ollama_service.py
- [ ] Add Arts Education context for typo correction
- [ ] Implement keep_alive management (10m Stage 1-3, 0s before ComfyUI)
- [ ] Add backend detection in Stage 4 (comfyui vs api)
- [ ] Test combined Translation+Safety+Interception flow
- [ ] Benchmark real-world performance vs. current system
- [ ] (Later) Comment out model_selector.py code
- [ ] (Later) Remove model_selector.py after 2-3 months of stable operation

### Test Scripts Location
**Research artifacts preserved:**
- `/tmp/test_gpt_oss_safeguard.py` - Full test suite (translation, dada, bauhaus, safety)
- `/tmp/test_gpt_oss_german_law.py` - §86a StGB compliance tests
- `/tmp/test_gpt_oss_context_correction.py` - Arts Education typo tests

**Note:** Scripts contain hardcoded API key, NOT committed to Git

### Future Considerations

**After Implementation + Testing:**
1. Monitor performance in production (2-3 weeks)
2. Collect user feedback on translation quality
3. Verify §86a StGB blocking works correctly in real scenarios
4. Test VRAM management on 24GB cards
5. If stable: Comment out model_selector.py (mark as deprecated)
6. If stable for 2-3 months: Remove model_selector.py entirely

**Rollback Strategy:**
- Keep model_selector.py code intact initially (comment out, don't delete)
- Easy revert: Change config.py constants back to mistral-nemo/llama-guard3
- Test scripts available for regression testing

**API Key Management:**
- OpenRouter API key in `/devserver/openrouter_api.key`
- Backend auto-detects: Ollama (local) vs OpenRouter (cloud)

### Files Modified
**Documentation:**
- `docs/devserver_todos.md` - Research results, implementation plan
- `docs/DEVELOPMENT_DECISIONS.md` - This entry

**Pending Changes (Implementation):**
- `devserver/config.py` - MODEL constants
- `devserver/my_app/services/ollama_service.py` - System prompts, keep_alive
- `devserver/schemas/engine/backend_router.py` - VRAM management logic

**Future Cleanup (Post-Testing):**
- `devserver/schemas/engine/model_selector.py` - Mark as deprecated/remove

### Related Documentation
- devserver_todos.md - Full implementation checklist
- ARCHITECTURE.md Section 1 - 4-Stage orchestration (where models are used)
- README_FIRST.md - Model selection philosophy
- Test scripts in `/tmp/test_gpt_oss_*.py` - Research methodology

### Key Quotes

**On unified model architecture:**
> "wait, Denkfehler: wenn wir in stage 2 auch GPT-OSS verwenden könnten? müssen wir es gar nicht unloaden."

**On model selector obsolescence:**
> "Immerhin macht diese Entscheidung die komplette aufwändige Model-Selektion und das Mapping lokal-> Openrouter überflüssig."

**On §86a StGB prompt necessity:**
> "Adressiere es explizit unter Verweis auf §86 StGB. Mal sehen ob es dann besser funktioniert."

**On Arts Education context:**
> "ergänze zu 1: correct spelling errors according to -> und dann Verweis auf die Situation: Kinder und Jugendliche die in Arts Education-Kursen Bilder und Medien prompten"

---

## 2025-11-01 (Evening 2): Multi-Output Support for Model Comparison

### Decision
**Implement Stage 3-4 Loop to support multiple media outputs from a single prompt**

**Actions Taken:**
1. ✅ Modified `schema_pipeline_routes.py` to loop over `output_configs[]` array
2. ✅ Each output config gets independent Stage 3 safety check + Stage 4 execution
3. ✅ Created `image_comparison.json` config for SD3.5 vs GPT-5 comparison
4. ✅ Response includes `media_outputs` array for multi-output scenarios
5. ✅ Maintained backward compatibility with single `default_output`

### Reasoning

**Problem: Single Output Limitation**
- 4-Stage Architecture only supported single media output per request
- No way to compare different models (SD3.5 vs GPT-5) with same prompt
- No way to generate multiple formats (image + audio) from single input
- Model comparison required separate requests → inefficient

**User Request (Pedagogical Goal):**
> "Enable side-by-side model comparison for educational purposes. Students should be able to generate the same prompt with different models (local SD3.5 vs cloud GPT-5) to understand model differences."

**Use Case - Workshop Scenario:**
- Teacher wants students to compare:
  - Local SD3.5 (free, DSGVO-compliant, slower)
  - Cloud GPT-5 (paid, non-DSGVO, faster, different style)
- Single request generates both images
- Side-by-side comparison in UI

### Solution: Stage 3-4 Loop

**Architecture Change:**
- Stage 1 (Pre-Interception): Runs ONCE per user input
- Stage 2 (Interception): Runs ONCE (main pipeline)
- **Stage 3-4: Loop over `output_configs[]` array**

**Config Format:**
```json
{
  "media_preferences": {
    "output_configs": ["sd35_large", "gpt5_image"]
  }
}
```

**Execution Flow:**
```
User Input: "Eine Blume auf der Wiese"
  ↓
Stage 1: Translation + Safety (once)
  ↓
Stage 2: Interception (once, e.g., dada transformation)
  ↓
Stage 3-4 Loop:
  ├─ Iteration 1: sd35_large
  │  ├─ Stage 3: Pre-Output Safety ✅
  │  └─ Stage 4: ComfyUI workflow → image_1.png
  └─ Iteration 2: gpt5_image
     ├─ Stage 3: Pre-Output Safety ✅
     └─ Stage 4: OpenRouter API → image_2.png

Response: {
  "media_outputs": [
    {"config": "sd35_large", "output": "prompt_id_1"},
    {"config": "gpt5_image", "output": "base64_data"}
  ]
}
```

### Alternative Approaches Considered

**Option A: Separate Requests (rejected)**
```python
# Request 1: Generate with SD3.5
POST /execute {config: "sd35_large", ...}

# Request 2: Generate with GPT-5
POST /execute {config: "gpt5_image", ...}
```
❌ Runs Stage 1 twice (translation + safety redundant)
❌ Runs Stage 2 twice (main pipeline redundant)
❌ 2x API cost, 2x execution time
❌ Harder to correlate results (different prompt_ids)

**Option B: Loop in Stage 2 Pipeline (rejected)**
```python
# Pipeline declares output_configs internally
stillepost.json → output_configs: ["sd35_large", "gpt5_image"]
```
❌ Violates separation of concerns (pipelines should be dumb)
❌ Configs lose control over output selection
❌ User can't override output configs without editing pipeline

**Option C: Stage 3-4 Loop in DevServer (chosen) ✅**
```python
# DevServer orchestrates Stage 3-4 loop
for config in output_configs:
    execute_stage3_safety(...)
    execute_stage4_generation(...)
```
✅ Correct: DevServer = smart orchestrator
✅ Stage 1-2 run once (no redundancy)
✅ Config has full control (user-editable)
✅ Backward compatible (single output still works)

### Technical Implementation

**Location:** `my_app/routes/schema_pipeline_routes.py`

**Key Code:**
```python
# Determine which output configs to use
output_configs = media_preferences.get('output_configs', [])

if output_configs:
    # Multi-Output: Explicit list
    configs_to_execute = output_configs
elif default_output and default_output != 'text':
    # Single-Output: Lookup from default_output
    configs_to_execute = [lookup_output_config(default_output, execution_mode)]

# Execute Stage 3-4 for EACH output config
media_outputs = []
for i, output_config_name in enumerate(configs_to_execute):
    logger.info(f"[4-STAGE] Stage 3-4 Loop iteration {i+1}/{len(configs_to_execute)}")

    # Stage 3: Pre-Output Safety (per config)
    if safety_level != 'off':
        safe, codes = execute_stage3_safety(...)
        if not safe:
            continue  # Skip unsafe outputs

    # Stage 4: Media Generation
    result = await pipeline_executor.execute_pipeline(output_config_name, ...)
    media_outputs.append(result)
```

**Per-Config Safety:**
- Each output config gets independent Stage 3 check
- Enables different safety thresholds per media type
- Example: Stricter rules for video than image
- One blocked output doesn't affect others

### Benefits

**1. Efficiency:**
- Stage 1 runs once (no redundant translation/safety)
- Stage 2 runs once (no redundant pipeline execution)
- Only Stage 3-4 loop (minimal overhead)

**2. Model Comparison (Pedagogical):**
- Generate same prompt with multiple models
- Side-by-side comparison in UI
- Students see model differences firsthand
- Educational goal: Understanding model biases/styles

**3. Multi-Format Output (Future):**
```json
{
  "output_configs": ["sd35_large", "stableaudio"]
}
```
→ Generate both image and audio from same prompt

**4. Multi-Resolution Output (Future):**
```json
{
  "output_configs": ["sd35_1024", "sd35_2048"]
}
```
→ Generate same image at multiple resolutions

**5. Backward Compatibility:**
- Single-output configs unchanged
- Frontend doesn't need updates
- Clients detect multi-output by array type

### Validation of 4-Stage Architecture

**This implementation proves the 4-Stage Architecture design is correct:**

✅ **DevServer = Smart Orchestrator**
- Knows when to loop (output_configs array)
- Knows when NOT to loop (single default_output)
- Orchestrates Stage 3-4 per output

✅ **PipelineExecutor = Dumb Engine**
- No awareness of multi-output
- Just executes chunks as instructed
- No redundant Stage 1-3 calls

✅ **Non-Redundant Safety Rules**
- Stage 1 safety runs once (input text)
- Stage 3 safety runs per output (generated prompts)
- No duplicate checks

✅ **Separation of Concerns**
- Config declares what outputs it wants
- DevServer orchestrates the loop
- PipelineExecutor just executes

### Test Results

**Config:** image_comparison.json
**Input:** "Eine Blume auf der Wiese"
**Output Configs:** ["sd35_large", "gpt5_image"]

**Results:**
- ✅ Stage 1: Ran once (translation + safety)
- ✅ Stage 2: Ran once (pass-through transformation)
- ✅ Stage 3-4 Loop: Ran 2x (once per output config)
  - Iteration 1: sd35_large → ComfyUI workflow (ComfyUI_06804_.png)
  - Iteration 2: gpt5_image → OpenRouter API (base64 PNG, ~2.1MB)
- ✅ Logs confirm correct execution flow
- ✅ Backward compatibility verified (single output still works)

**Execution Time:** ~120 seconds (normal for 2 image generations)

### Files Modified

**Modified:**
- `my_app/routes/schema_pipeline_routes.py` (+199 -75 lines)
  - Implemented Stage 3-4 Loop
  - Added `output_configs` array support
  - Response includes `media_outputs` array

**Created:**
- `schemas/configs/interception/image_comparison.json` (58 lines)
  - Pass-through config (no prompt modification)
  - Uses `output_configs: ["sd35_large", "gpt5_image"]`
  - Purpose: Model comparison (SD3.5 local vs GPT-5 cloud)

### Documentation Updated

- ✅ Commit message: 55bbfca (detailed implementation notes)
- ✅ DEVELOPMENT_LOG.md: Session 11 continuation entry
- ✅ DEVELOPMENT_DECISIONS.md: This entry
- ⏭️ ARCHITECTURE.md: Multi-Output Flow documentation (pending)
- ⏭️ devserver_todos.md: Mark Multi-Output complete (pending)

### User Quotes

> "The recursive pipeline system validates our 4-Stage Architecture. Now the Multi-Output support proves it scales to complex scenarios. Both implementations show that DevServer = Smart Orchestrator is the correct design."

### Related Sessions

- **Session 11 (Part 1):** Recursive Pipeline System (6f8d064)
  - Loops INSIDE Stage 2 (text_transformation_recursive)
  - Validates: Stage 1 runs once, not per iteration
- **Session 11 (Part 2):** Multi-Output Support (55bbfca)
  - Loops OUTSIDE Stage 2 (Stage 3-4 Loop)
  - Validates: Stage 1-2 run once, Stage 3-4 loop per output

**Both implementations:**
- ✅ Prove 4-Stage Architecture is correct
- ✅ Demonstrate DevServer = Smart Orchestrator
- ✅ Show PipelineExecutor = Dumb Engine
- ✅ Validate non-redundant safety rules

---

## 2025-11-01 (Evening): Config Folder Restructuring + User-Config Naming System

### Decision
**Reorganize configs into purpose-based folders with prefix-based user-config naming**

**Actions Taken:**
1. ✅ Created folder structure: `interception/`, `output/`, `user_configs/`
2. ✅ Moved 31 configs to `interception/` (user-facing)
3. ✅ Moved 6 configs to `output/` (system-only)
4. ✅ Implemented user-config naming: `user_configs/username/file.json` → `u_username_file`
5. ✅ Auto-inject `meta.owner` field based on folder structure
6. ✅ Frontend API: Filter out `meta.stage="output"` configs
7. ✅ Frontend API: Include `meta.owner` in response

### Reasoning

**Problem 1: Flat Config Structure**
All 37 configs in root folder made it unclear which are:
- User-facing (interception configs for browsing)
- System-internal (output configs for media generation)
- System pipelines (pre_interception, pre_output)

**Problem 2: Future User-Config Collision Risk**
When users create their own configs, name collisions are inevitable:
- User creates `dada.json` → conflicts with system `dada.json`
- No way to distinguish system vs user configs
- No tracking of ownership

### Solution: Folder-Based Organization + Prefix Naming

**Folder Structure:**
```
configs/
├── interception/       (31 user-facing configs)
├── output/             (6 system-only configs)
├── user_configs/       (user-created configs)
│   └── username/       (per-user isolation)
├── pre_interception/   (system pipelines)
└── pre_output/         (system pipelines)
```

**Naming Convention:**
- **System configs:** Simple name (stem)
  - `interception/dada.json` → `"dada"`
  - `output/sd35_large.json` → `"sd35_large"`

- **User configs:** Prefixed name
  - `user_configs/doej/my_dada.json` → `"u_doej_my_dada"`
  - `user_configs/alice/test.json` → `"u_alice_test"`

**Benefits:**
1. ✅ **No collisions:** `u_` prefix guarantees uniqueness
2. ✅ **Scalable:** No manual mapping/registry needed
3. ✅ **Self-documenting:** Username embedded in config name
4. ✅ **Easy filtering:** Frontend can filter by prefix or owner
5. ✅ **Automatic owner tracking:** `meta.owner` injected from folder path

### Alternative Approaches Considered

**Option A: Namespace System (rejected)**
```python
SCOPE_MAPPING = {
    "interception": "system",
    "user_configs": "user"
}
```
❌ Requires manual mapping maintenance
❌ Not scalable (new folders = update mapping)

**Option B: Collision Detection + Error (rejected)**
```python
if config_name in configs:
    raise Error("Config name collision")
```
❌ Breaks when user creates `dada.json`
❌ Forces users to pick unique names (bad UX)

**Option C: Prefix System (chosen) ✅**
```python
if folder == "user_configs":
    name = f"u_{username}_{stem}"
else:
    name = stem
```
✅ Automatic, no maintenance
✅ Scales infinitely
✅ Clear ownership

### Implementation Details

**config_loader.py:**
```python
# Auto-detect owner from folder structure
if parts[0] == "user_configs":
    username = parts[1]
    config_name = f"u_{username}_{stem}"
    owner = username
elif parts[0] in ["interception", "output"]:
    config_name = stem
    owner = "system"
else:
    config_name = full_path
    owner = "system"

# Auto-inject meta.owner
meta["owner"] = owner
```

**Frontend API (schema_pipeline_routes.py):**
```python
# Filter: Don't show output configs in user-facing browser
if config_data.get("meta", {}).get("stage") == "output":
    continue

# Inject owner for frontend badges
metadata["meta"]["owner"] = owner
```

### Files Modified
- `schemas/engine/config_loader.py` - User-config naming + owner injection
- `my_app/routes/schema_pipeline_routes.py` - Output filtering + owner in API
- `.gitignore` - `/output/` (root-only) vs `configs/output/` (tracked)
- 37 config files moved to new folder structure

### User Experience Impact

**Before:**
- Frontend shows all 42 configs (including system-only output configs)
- No way to distinguish system vs user configs
- Risk of name collisions

**After:**
- Frontend shows 36 configs (only user-facing + system pipelines)
- Output configs hidden (sd35_large, gpt5_image, etc.)
- User configs clearly marked with owner badge
- Example: "Test Dada (by doej)"

### Testing
- ✅ Config loader: 42 configs loaded correctly
- ✅ Frontend API: 37 returned (output configs filtered)
- ✅ User config: `u_doej_test_dada` with `meta.owner="doej"`
- ✅ No breaking changes: System configs still work with simple names

### Future Considerations
- User-config UI: Users can create/edit configs in `user_configs/username/`
- Session-based isolation: `username` from session, not hardcoded
- Config validation: Ensure user configs don't break system
- Quota system: Limit number of user configs per user

---

## 2025-11-01 (PM): Documentation Consolidation - Single Source of Truth

### Decision
**Consolidate fragmented documentation into clear hierarchy**

**Actions Taken:**
1. ✅ Merged `4_STAGE_ARCHITECTURE.md` into `ARCHITECTURE.md` as Section 1 (Part I)
2. ✅ Deleted `4_STAGE_ARCHITECTURE.md` (now redundant)
3. ✅ Deleted `README.md` (merged into README_FIRST.md)
4. ✅ Moved historical docs to `docs/tmp/`:
   - `API_MIGRATION.md` (historical implementation doc)
   - `PRE_INTERCEPTION_DESIGN.md` (historical planning doc)
5. ✅ Updated all references in `CLAUDE.md` and `README_FIRST.md`

### Reasoning

**Problem:**
User correctly identified:
> "docs are inconsistent now. there is an architecture.md and now a '4_stage_architecture.md', am API-Migration, and PRE-Interception-design.md also I think there should be one readme_first.md and not and additional readme.md)"

**Issues:**
- 4 documents describing architecture (fragmented)
- Unclear which is authoritative
- Historical planning docs (PRE_INTERCEPTION_DESIGN.md) mixed with current docs
- Two READMEs (README.md + README_FIRST.md) causing confusion

### Final Documentation Structure

```
docs/
├── README_FIRST.md              ← Single entry point
├── ARCHITECTURE.md (v3.0)       ← Complete reference
│   ├── Part I: Orchestration (Section 1 - 4-Stage Flow)
│   └── Part II: Components (Sections 2-13 - Implementation)
├── LEGACY_SERVER_ARCHITECTURE.md  ← Historical context
├── DEVELOPMENT_DECISIONS.md       ← Decision log
├── DEVELOPMENT_LOG.md            ← Session tracking
├── devserver_todos.md            ← Current tasks
├── DEVSERVER_COMPREHENSIVE_DOCUMENTATION.md  ← Pedagogical perspective
└── tmp/                          ← Historical/planning docs
    ├── API_MIGRATION.md           (historical)
    ├── PRE_INTERCEPTION_DESIGN.md (historical planning)
    └── (other session-specific docs)
```

### Benefits

1. **Single Source of Truth:** ARCHITECTURE.md is THE technical reference
2. **Clear Structure:** Part I (how it works) → Part II (what the parts are)
3. **No Duplication:** One ARCHITECTURE doc, one README
4. **Historical Separation:** Planning docs in tmp/, not mixed with current
5. **Easy Navigation:** Clear TOC with Part I/II division

### Files Modified

**Consolidated:**
- `docs/4_STAGE_ARCHITECTURE.md` → `docs/ARCHITECTURE.md` Section 1 (deleted original)
- `docs/README.md` → `docs/README_FIRST.md` (deleted original)

**Moved:**
- `docs/API_MIGRATION.md` → `docs/tmp/API_MIGRATION.md`
- `docs/PRE_INTERCEPTION_DESIGN.md` → `docs/tmp/PRE_INTERCEPTION_DESIGN.md`

**Updated References:**
- `CLAUDE.md`: 4_STAGE_ARCHITECTURE.md → ARCHITECTURE.md Section 1
- `README_FIRST.md`: Updated reading list with consolidated docs
- Total reading time: 85 minutes (was 75, added 10 for expanded Section 3)

### Reading Order (README_FIRST.md)

1. **ARCHITECTURE.md Section 1** (20 min) - 4-Stage orchestration flow
2. **LEGACY_SERVER_ARCHITECTURE.md** (20 min) - Pedagogical foundation
3. **ARCHITECTURE.md Sections 2-13** (30 min) - Components reference
4. **devserver_todos.md** (5 min) - Current priorities
5. **DEVELOPMENT_DECISIONS.md** (10 min) - Decision history

**Total:** 85 minutes of focused reading before any implementation

### Version Updates

- **ARCHITECTURE.md:** v2.1 → v3.0 (major consolidation)
- **README_FIRST.md:** Updated references, reading time
- **CLAUDE.md:** Updated to reference ARCHITECTURE.md Section 1

---

## 2025-11-01 (AM): 4-Stage Architecture v2.0 - DevServer as Main Orchestrator

### Decision
**Complete architectural redesign: Move Stage 1-3 logic from PipelineExecutor to DevServer**

**Core Changes:**
1. **PipelineExecutor = Dumb Engine** (just executes chunks, no pre/post processing)
2. **DevServer = Smart Orchestrator** (knows 4-stage flow, orchestrates all stages)
3. **Non-Redundant Safety Rules** (hardcoded in DevServer, not in pipelines)
4. **Stage 3-4 Loop** (runs once per output request, not once per pipeline)

### Problem Identified

**Current Bug (2025-11-01 console output):**
```
User: "EIne Blume auf der Wiese" with overdrive config
  ↓
✅ Stage 1: Translation + Safety (correct)
✅ Stage 2: Overdrive transformation (correct)
✅ Stage 3: Pre-Output safety (correct)
❌ AUTO-MEDIA calls execute_pipeline('gpt5_image', ...)
   → execute_pipeline() has Stage 1-3 logic inside!
   → Translation runs AGAIN on already-English text
   → Safety check runs AGAIN
   → Stage 2 tries to run (gpt5_image has context field)
   → Wasted API calls, confusing logs
```

**Root Cause:**
- Stage 1-3 logic embedded in `pipeline_executor.py` execute_pipeline() (lines 308-499)
- Every call to execute_pipeline() triggers all stages
- When AUTO-MEDIA generates output, it calls execute_pipeline() for output config
- Output config shouldn't run Stage 1-3 (already done!)

### Reasoning

**Architectural Principle (From User Clarification):**
> "Pipeline are orchestrators, but devserver is the orchestrator of pipelines."
> "Stage 2-pipeline only says: i need 2 text inputs and an image; it does not say anything about safety."
> "Server knows: text -> pre-stage2 safety pipeline for text; image -> pre-stage2 safety for image."

**Why This Matters:**

1. **Separation of Concerns:**
   - PipelineExecutor = Engine (runs chunks)
   - DevServer = Orchestrator (knows flow)
   - Mixing these = loops and redundant calls

2. **Non-Redundant Safety:**
   - If 37+ configs each declare safety requirements → duplication
   - If DevServer knows "text → safety" → one place, no duplication
   - Change safety rules → update one file, not 37+

3. **Complex Pipeline Support:**
   - Stage 2 can request multiple outputs (image + audio)
   - Each output request needs Stage 3-4
   - Stage 3-4 must run OUTSIDE pipeline executor
   - Example: Multi-media config requests 2 images + 1 audio = 3× Stage 3-4 runs

4. **Looping Pipelines:**
   - "Stille Post" translates 8× in Stage 2
   - Stage 1 should run ONCE (before loop)
   - Stage 3-4 should run ONCE (after loop)
   - Current architecture can't handle this

### What Was Done

**Documentation (2025-11-01):**
- ✅ Created: `docs/4_STAGE_ARCHITECTURE.md` (AUTHORITATIVE, 600+ lines)
  - Complete flow diagrams
  - Examples: simple, looping, multi-output, iterative
  - Separation of concerns (what pipelines declare vs DevServer knows)
  - Output request mechanism
  - Non-redundant safety rules
  - Implementation guide with steps

- ✅ Updated: `CLAUDE.md`
  - Added "AUTHORITATIVE: 4-Stage Architecture" section
  - Documented current bug
  - Key principles for future tasks

- ✅ Updated: `DEVELOPMENT_DECISIONS.md` (this entry)

**Implementation (Pending):**
- [ ] Strip Stage 1-3 from pipeline_executor.py (make dumb)
- [ ] Move Stage 1 orchestration to schema_pipeline_routes.py
- [ ] Implement output_request mechanism
- [ ] Move Stage 3-4 loop to schema_pipeline_routes.py
- [ ] Add `meta.output_config = true` flag to output configs
- [ ] Test end-to-end flows

### Correct Architecture (Version 2.0)

```
┌─────────────────────────────────────────────────────────┐
│ schema_pipeline_routes.py (DevServer - SMART)          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ I. Stage 1: Pre-Interception                           │
│    Read: pipeline.input_requirements {texts: N}        │
│    For each text:                                       │
│      → execute_pipeline('translation', text)           │
│      → run_hybrid_safety_check(text, 'stage1')         │
│                                                         │
│ II. Stage 2: Interception                              │
│     result = execute_pipeline(user_config, inputs)     │
│     # PipelineExecutor just runs chunks (DUMB)         │
│     # Returns: output_requests = [{type, prompt, ...}] │
│                                                         │
│ III. For EACH output_request:                          │
│      Stage 3: run_hybrid_safety_check(prompt, level)   │
│      Stage 4: execute_pipeline(output_config, prompt)  │
│                                                         │
│ IV. Collect all media + metadata                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ pipeline_executor.py (PipelineExecutor - DUMB)         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ def execute_pipeline(config, inputs):                  │
│   # ONLY:                                               │
│   # 1. Load config + pipeline                          │
│   # 2. Execute chunks                                   │
│   # 3. Return result                                    │
│   #                                                     │
│   # NO Stage 1-3 logic!                                │
│   # NO pre-processing!                                 │
│   # NO safety checks!                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Pipeline Declarations (Non-Redundant)

**Pipelines declare ONLY structure:**
```json
{
  "name": "text_transformation",
  "input_requirements": {
    "texts": 1
  },
  "chunks": ["manipulate"]
}
```

**Pipelines DO NOT declare:**
- ❌ Safety requirements (DevServer knows)
- ❌ Translation needs (DevServer knows: text → translate)

**DevServer hardcodes safety rules:**
```python
STAGE1_SAFETY = {
    "text": "pre_interception/safety_llamaguard",
    "image": "pre_interception/image_safety_vision"
}

STAGE3_SAFETY = {
    ("image", "kids"): "text_safety_check_kids",
    ("image", "youth"): "text_safety_check_youth"
}
```

### Examples

**Simple Flow (overdrive → gpt5_image):**
```
Stage 1: translation + safety (RUN ONCE)
Stage 2: overdrive transformation (RUN ONCE)
Stage 3: safety check on output (RUN ONCE)
Stage 4: gpt5_image generation (RUN ONCE)
```

**Looping Flow (stillepost → 8 translations → image):**
```
Stage 1: translation + safety (RUN ONCE)
Stage 2: 8 translation loops (RUN ONCE, loops inside)
Stage 3-4: safety + image (RUN ONCE after loop)
```

**Multi-Output Flow (text → image + audio):**
```
Stage 1: translation + safety (RUN ONCE)
Stage 2: transformation (RUN ONCE, requests 2 outputs)
Stage 3-4: safety + image (RUN for output #1)
Stage 3-4: safety + audio (RUN for output #2)
```

### Files To Modify

**Core Refactoring:**
- `schemas/engine/pipeline_executor.py` - Remove lines 308-499 (Stage 1-3 logic)
- `my_app/routes/schema_pipeline_routes.py` - Add Stage 1 + Stage 3-4 loop

**Supporting Changes:**
- `schemas/pipelines/*.json` - Add `input_requirements` field
- `schemas/configs/gpt5_image.json` - Add `meta.output_config = true`
- `schemas/configs/sd35_large.json` - Add `meta.output_config = true`

**Documentation:**
- `docs/4_STAGE_ARCHITECTURE.md` - AUTHORITATIVE reference (created)
- `CLAUDE.md` - Points to authoritative doc (updated)
- `docs/README_FIRST.md` - Add to mandatory reading (pending)

### Implementation Strategy

**Incremental Refactoring (Safe):**
1. Add `input_requirements` to pipelines (backward compatible)
2. Implement Stage 1 in DevServer (parallel to existing)
3. Add flag: `use_new_architecture = False` (toggle)
4. Test new path thoroughly
5. Set flag to `True`
6. Remove old Stage 1-3 code from executor

**NOT Big Bang (Risky):**
- ❌ Don't delete 400 lines and rewrite everything
- ❌ Don't break existing functionality
- ✅ Incremental, testable, rollback-able

### Benefits

1. **No More Loops:** Impossible for pipelines to trigger themselves
2. **Performance:** No redundant translation/safety calls
3. **Maintainability:** Change safety rules in ONE place
4. **Complex Pipelines:** Supports loops, multi-output, evaluation
5. **Clear Logs:** Each stage logs once, easy to debug
6. **Testability:** Test orchestration separately from execution

### Related Documentation

- **AUTHORITATIVE:** `docs/4_STAGE_ARCHITECTURE.md` (complete flow reference)
- **Context:** `docs/PRE_INTERCEPTION_DESIGN.md` (original 4-stage design)
- **TODOs:** `docs/devserver_todos.md` (implementation tasks)

---

## 2025-10-28 (PM): COMPLETE Frontend Migration - Backend-Abstracted Architecture

### Decision
**Rebuild Frontend from scratch with complete Backend abstraction**
- Created NEW: `config-browser.js` - Card-based config selection
- Created NEW: `execution-handler.js` - Uses `/api/schema/pipeline/execute` + `/api/media/*`
- Updated: `main.js` - Initializes new architecture
- Moved to `.obsolete`: `workflow-streaming.js`, `workflow-browser.js`, `workflow.js`, `workflow-classifier.js`
- Changed: `model_selector.py` - Replaced gemma2:9b with mistral-nemo (faster)

### Reasoning

**Problem:**
Previous migration (AM) was incomplete:
- `workflow-streaming.js` still used legacy `/run_workflow` endpoint
- Frontend directly accessed ComfyUI (`/comfyui/history/{prompt_id}`)
- No integration between config-browser and execution
- Mixed legacy + new code caused confusion

**Complete New Architecture:**
```
Config Selection:
  Frontend → /pipeline_configs_metadata → Backend returns 37 configs

Execution:
  Frontend → /api/schema/pipeline/execute
  Backend → Chunks/Pipelines (Text transformation)
  Backend → Auto-Media (Image generation)
  Backend → Returns { media_output: { output: prompt_id, media_type: "image" } }

Media Polling (NEW!):
  Frontend → /api/media/info/{prompt_id} (every second)
  Backend → Checks ComfyUI status internally
  Backend → Returns { type: "image", files: [...] } OR 404 (not ready)

Media Display (NEW!):
  Frontend → /api/media/image/{prompt_id}
  Backend → Fetches from ComfyUI internally
  Backend → Returns PNG directly
```

**Benefits:**
- ✅ Frontend NEVER accesses ComfyUI directly
- ✅ Backend can replace ComfyUI with other generators transparently
- ✅ Media-type comes from Config metadata (extensible to audio/video)
- ✅ Clean separation of concerns
- ✅ 100% Backend-abstracted (no legacy REST)

**Performance:**
- Replaced gemma2:9b with mistral-nemo (3x faster for text transformation)

### Testing
✅ Dada Config selection works
✅ Text transformation successful
✅ Image generation successful (SD3.5 Large)
✅ Media polling via Backend API works
✅ Image display via Backend API works

### Files Changed
**New:**
- `public_dev/js/config-browser.js` - Simple card-based config browser
- `public_dev/js/execution-handler.js` - Backend-abstracted execution + polling

**Modified:**
- `public_dev/js/main.js` - Initialize config-browser
- `public_dev/index.html` - Removed legacy dropdown
- `schemas/engine/model_selector.py` - gemma2:9b → mistral-nemo

**Obsoleted:**
- `public_dev/js/workflow.js.obsolete`
- `public_dev/js/workflow-classifier.js.obsolete`
- `public_dev/js/workflow-browser.js.obsolete` (incomplete migration)
- `public_dev/js/workflow-streaming.js.obsolete` (legacy API)
- `public_dev/js/dual-input-handler.js.obsolete`

---

## 2025-10-28 (AM): Frontend Migration - Karten-Browser + Legacy Cleanup

### Decision
**Remove legacy Workflow-based Frontend, activate Config-based Karten-Browser**
- Removed `workflow.js` (dropdown system) → replaced by `workflow-browser.js` (card-based UI)
- Removed `WorkflowClassifier` → Config metadata will handle input validation
- Added `/pipeline_configs_metadata` endpoint for Karten-Browser
- Simplified `DualInputHandler` - removed workflow-type checks

### Reasoning

**Problem:**
- "Workflow" terminology is legacy (should be "Config")
- Dropdown unsuitable for 37+ configs (no search, filtering, categorization)
- `WorkflowClassifier` asked backend "Is this inpainting?" - wrong approach
- Inpainting doesn't exist yet in new system

**Correct Architecture:**
- Frontend displays **Configs** (not "Workflows")
- Config metadata declares requirements: `"requires_image": true`
- No separate classification service needed
- DualInputHandler checks Config metadata, not workflow type

**Migration Path:**
```
OLD: workflow.js → /list_workflows → WorkflowClassifier → Inpainting check
NEW: workflow-browser.js → /pipeline_configs_metadata → Config.meta.requires_image
```

**Current State:**
- No Inpainting configs exist yet
- All test configs use `simple_interception` pipeline (text-only)
- DualInputHandler simplified: "If image → use it, if not → text only"
- Future: Check `config.meta.requires_image` when Inpainting-Configs exist

### What Was Done

**Frontend Changes:**
- `public_dev/js/workflow.js` → `.obsolete` (deprecated dropdown system)
- `public_dev/js/workflow-classifier.js` → `.obsolete` (replaced by config metadata)
- `public_dev/js/main.js` - Removed `loadWorkflows()` call
- `public_dev/js/dual-input-handler.js` - Simplified input processing

**Backend Changes:**
- Added `/pipeline_configs_metadata` endpoint (used by Karten-Browser)
- Commented out `/list_workflows`, `/workflow_metadata` (only used by deprecated dropdown)
- Kept `schema_compat_bp` blueprint for backward compatibility during migration

**Documentation:**
- Updated DEVELOPMENT_DECISIONS.md (this file)
- Updated devserver_todos.md with migration progress
- Updated ARCHITECTURE.md with DualInputHandler explanation

### Future Implementation: Inpainting

**When Inpainting is needed:**
1. Create Pipeline: `image_plus_text_generation.json`
2. Create Config: `inpainting_sd35.json` with `"meta": {"requires_image": true}`
3. Create Output-Chunk: `output_image_inpainting.json` with ComfyUI Inpainting workflow
4. Update DualInputHandler to check: `if (config.meta.requires_image && !imageData) throw Error`

**Data Flow:**
```
User uploads image + enters prompt
  → Frontend checks selected Config metadata
  → If config.meta.requires_image: Validate image present
  → DualInputHandler processes: mode='image_plus_text'
  → Backend routes to image_plus_text_generation pipeline
  → Inpainting Output-Chunk receives both inputs
  → ComfyUI processes inpainting
```

### Files Modified
- `public_dev/js/workflow.js` → `.obsolete`
- `public_dev/js/workflow-classifier.js` → `.obsolete`
- `public_dev/js/main.js`
- `public_dev/js/dual-input-handler.js`
- `my_app/routes/schema_pipeline_routes.py`
- `docs/DEVELOPMENT_DECISIONS.md` (this file)

### Files Kept (Not Deprecated)
- `workflow-streaming.js` - Still used for submission (should be renamed to config-streaming.js)
- `workflow-browser.js` - Active card-based UI (consider rename to config-browser.js)

---

## 2025-10-27: GPT-5 Image OpenRouter Integration + API Output-Chunks

### Decision
**Add API-based Output-Chunks alongside ComfyUI-based Output-Chunks**
- Created new `api_output_chunk` type for cloud API-based media generation
- GPT-5 Image via OpenRouter as first implementation
- API keys stored in `.key` files (excluded from git) for easy end-user setup

### Reasoning

**User Request:**
> "secure but easy solution, not some deep system diving with variables. end users of the system will be amateurs"

**Problem:**
- ComfyUI Output-Chunks contain embedded workflows (complex JSON)
- Cloud APIs (OpenRouter, OpenAI, Replicate) don't use ComfyUI workflows
- Need clean separation between workflow-based and API-based backends

**Solution - API Output-Chunk Structure:**
```json
{
  "name": "output_image_gpt5",
  "type": "api_output_chunk",
  "backend_type": "openrouter",
  "media_type": "image",
  "api_config": {
    "provider": "openrouter",
    "model": "openai/gpt-5-image",
    "endpoint": "https://openrouter.ai/api/v1/chat/completions",
    "method": "POST",
    "request_body": {...},
    "input_mappings": {...},
    "output_mapping": {...}
  }
}
```

**Key Architectural Decisions:**

1. **API Key Management:** `.key` files (not environment variables)
   - Simple for end users (just paste key into file)
   - Excluded from git via `*.key` pattern
   - Location: devserver root (e.g., `openrouter_api.key`)

2. **GPT-5 Image as Multimodal Chat Model:**
   - Uses `/api/v1/chat/completions` endpoint (NOT `/images/generations`)
   - Response format: `message.images[]` array with image URLs
   - Cost: ~$0.00004 per image

3. **Backend Router Enhancement:**
   - Added `_process_api_output_chunk()` method
   - Checks chunk type: `api_output_chunk` vs `output_chunk`
   - Routes accordingly: API call vs ComfyUI workflow

### What Was Done

**New Files:**
- `schemas/chunks/output_image_gpt5.json` - API Output-Chunk for GPT-5 Image
- `schemas/configs/gpt5_image.json` - Output Config (fast mode cloud generation)
- `schemas/configs/passthrough.json` - Interception Config with NULL-manipulation
- `schemas/engine/output_config_selector.py` - Auto-media config selection
- `schemas/output_config_defaults.json` - Central output config mapping
- `openrouter_api.key` - API key file (git-ignored)
- `test_gpt5_image.py`, `test_gpt5_simple.py` - Test scripts
- `OPENROUTER_SETUP.md` - Setup guide for end users

**Modified Files:**
- `schemas/engine/backend_router.py`:
  - `_process_api_output_chunk()` - Process API-based Output-Chunks
  - `_extract_image_from_chat_completion()` - Extract image from GPT-5 response
  - `_load_api_key()` - Load API keys from `.key` files
  - Updated `_process_comfyui_request()` to route by chunk type
- `my_app/routes/workflow_routes.py`:
  - Fixed `execution_mode` undefined bug (variable was named `mode`)
- `schemas/output_config_defaults.json`:
  - `image.fast = "gpt5_image"` (cloud)
  - `image.eco = "sd35_large"` (local)

### Future Considerations

**Extensibility:**
- Can now easily add more API-based Output-Chunks:
  - DALL-E 3 (OpenAI)
  - Midjourney (via API)
  - Replicate models
  - Stability AI API

**Known Issues:**
1. Frontend shows Output Configs (`sd35_large`, `gpt5_image`) as user-selectable
   - These should only be used by auto-media system
   - Need filtering mechanism (e.g., `meta.system_config: true`)

2. No clear architectural separation between:
   - Interception Configs (user-facing, text manipulation)
   - Output Configs (system-only, media generation)

**Deferred Refactoring:**
- Separate directory structure (`interception/` and `output/` folders)
- Attempted but rolled back due to complexity
- Would require updates to 5+ engine modules
- Postponed until system is stable and tested

### Files Modified
- schemas/engine/backend_router.py
- my_app/routes/workflow_routes.py
- schemas/output_config_defaults.json

### Files Created
- schemas/chunks/output_image_gpt5.json
- schemas/configs/gpt5_image.json
- schemas/configs/passthrough.json
- schemas/engine/output_config_selector.py
- schemas/output_config_defaults.json
- openrouter_api.key
- test_gpt5_image.py
- test_gpt5_simple.py
- OPENROUTER_SETUP.md
- docs/tmp/GPT5_IMAGE_OPENROUTER_PLAN.md

---

## 2025-10-27: AUTO-MEDIA GENERATION - Output-Config Defaults System

### Decision
**Centralized default Output-Config mapping via `output_config_defaults.json`**
- Pre-pipeline configs (dada.json) suggest media type via `media_preferences.default_output`
- Pre-pipeline configs DO NOT choose specific models
- DevServer uses `output_config_defaults.json` to map `media_type + execution_mode → output_config`

### Reasoning

**Separation of Concerns:**
- Text manipulation configs should not dictate which image/audio model to use
- Dada says "I produce visual content" not "I use SD3.5 Large"
- Content transformation is separate from media generation

**Problem with Alternative Approaches:**

❌ **Adding `output_configs` to pre-pipeline configs (dada.json):**
```json
{
  "output_configs": {
    "image": {"eco": "sd35_large", "fast": "flux1"}
  }
}
```
- Violates separation of concerns
- Text manipulation shouldn't know about specific models
- 34+ configs would all need to specify output models
- Changes to default image model require editing 34+ files

✅ **Centralized `output_config_defaults.json`:**
```json
{
  "image": {"eco": "sd35_large", "fast": "flux1_openrouter"},
  "audio": {"eco": "stable_audio", "fast": "stable_audio_api"},
  "music": {"eco": "acestep", "fast": null},
  "video": {"eco": "animatediff", "fast": null}
}
```
- One central place defines defaults
- Pre-pipeline configs stay focused on text transformation
- Change default image model: edit one line
- Pedagogically clear: separation between content and generation

**Data Flow:**
```
1. User runs dada.json config
2. Dada outputs optimized text
3. DevServer reads: media_preferences.default_output = "image"
4. DevServer reads: execution_mode = "eco"
5. DevServer lookup: output_config_defaults["image"]["eco"] → "sd35_large"
6. DevServer executes: single_prompt_generation with sd35_large config
7. Image generated via Output-Chunk system
```

**User Override Options:**
- `#image#`, `#audio#`, `#music#`, `#video#` tags override default
- `default_output = "text"` → no auto-media generation

### Files Affected
- **Created:**
  - `schemas/output_config_defaults.json` (central mapping)
  - `schemas/engine/output_config_selector.py` (loader/selector)
  - `ExecutionContext` class (media tracking throughout execution)
  - `MediaOutput` dataclass (structured media output tracking)
- **Updated:**
  - `my_app/routes/workflow_routes.py` (replace deprecated generate_image_from_text)
  - `docs/ARCHITECTURE.md` (Pattern 5: Auto-Media Generation + DevServer awareness)

### DevServer Media Awareness
**Decision:** DevServer must track expected and actual media types throughout execution

**Why:**
1. **Media Collection** - Track all media in multi-step processes (text → image → audio)
2. **Presentation Logic** - Format API response based on media type
3. **Pipeline Chaining** - Reuse execution context for multiple generations
4. **Error Handling** - Validate expected vs actual media type
5. **Frontend Communication** - Tell UI what media to expect/display

**Implementation:**
- `ExecutionContext` tracks: expected_media_type, generated_media[], text_outputs[]
- `MediaOutput` tracks: media_type, prompt_id, output_mapping, config_name, status
- Validation: Output-Chunk.media_type matches expected type

### Implementation Status
- ✅ **Design:** Documented in ARCHITECTURE.md + DEVELOPMENT_DECISIONS.md
- ⚠️ **Implementation:** READY TO BEGIN

---

## 2025-10-26: OUTPUT-CHUNK ARCHITECTURE - Embedded ComfyUI Workflows

### Decision
**Output-Chunks now contain complete ComfyUI API workflows embedded in JSON**
- ComfyUI workflows are stored directly in chunk files (not generated dynamically)
- Each Output-Chunk includes: `workflow`, `input_mappings`, `output_mapping`, `meta`
- Deprecate: `comfyui_workflow_generator.py` (will be removed in future cleanup)

### Reasoning

**Problem with Dynamic Generation:**
- `comfyui_workflow_generator.py` hardcoded workflows in Python code
- Workflows were generated at runtime from templates
- Separated workflow structure from data (against "data over code" principle)
- Made workflows harder to edit for non-programmers

**New Approach - Embedded Workflows:**
```json
{
  "name": "output_audio_stable_audio",
  "type": "output_chunk",
  "workflow": {
    "3": { "class_type": "KSampler", "inputs": {...} },
    "4": { "class_type": "CheckpointLoaderSimple", ... },
    ...
  },
  "input_mappings": {
    "prompt": {"node_id": "6", "field": "inputs.text"},
    ...
  },
  "output_mapping": {
    "node_id": "19", "output_type": "audio", "format": "mp3"
  }
}
```

**Advantages:**
1. **Workflows are Data:** JSON format, not Python code
2. **Easier to Edit:** Can be modified without code changes
3. **Transparency:** Complete workflow visible in chunk file
4. **No Generation:** Server fills placeholders and submits directly to ComfyUI
5. **Backend Agnostic:** Same format works with ComfyUI, SwarmUI, etc.

**Migration Strategy:**
- Extract existing workflows from `comfyui_workflow_generator.py`
- Convert to Output-Chunk JSON format
- Add `input_mappings` metadata (server needs to know where to inject prompts)
- Add `output_mapping` metadata (server needs to know where to extract media)
- Update `backend_router.py` to process Output-Chunks directly

### Files Affected
- **Deprecated:**
  - `schemas/engine/comfyui_workflow_generator.py` (marked for removal)
- **To Create:**
  - `schemas/chunks/output_image_sd35_standard.json`
  - `schemas/chunks/output_audio_stable_audio.json`
  - `schemas/chunks/output_music_acestep.json`
- **To Update:**
  - `schemas/engine/backend_router.py` (process Output-Chunks)
  - `docs/ARCHITECTURE.md` (document Output-Chunk structure)

### Implementation Status
- ⚠️ **Design:** Documented in ARCHITECTURE.md
- ⚠️ **Implementation:** NOT YET IMPLEMENTED
- ⚠️ **Migration:** Old system still in place (comfyui_workflow_generator.py still used)

---

## 2025-10-26: CHUNK CONSOLIDATION - Single manipulate Chunk

### Decision
**Consolidated all text transformation chunks into ONE `manipulate.json` chunk**
- Deleted: `translate.json`, `prompt_interception.json`, `prompt_interception_lyrics.json`, `prompt_interception_tags.json`
- Fixed: `manipulate.json` template (removed duplicate placeholder)
- Updated: All pipelines to use `manipulate` chunk only

### Reasoning (Joerissen)
> "Dann reicht ein manipulate-Chunk [...] 'Prompt interception' ist ein kritisches pädagogisches Konzept das auf dieser Ebene nicht auftauchen sollte"

**Technical Problem:**
- Multiple chunks (translate, prompt_interception, manipulate) were functionally identical
- Only difference: placeholder naming and temperature settings
- `translate` = `manipulate` with translation context + low temperature
- `prompt_interception` = `manipulate` with explicit Task/Context structure
- Content belongs in Configs, not in separate chunks

**Placeholder Redundancy:**
```python
# Before:
replacement_context = {
    'INSTRUCTION': instruction_text,
    'INSTRUCTIONS': instruction_text,  # Duplicate!
    'TASK': instruction_text,          # Duplicate!
    'CONTEXT': instruction_text,       # Duplicate!
}
```
All four resolved to same value (config.context) → caused duplication in rendered prompts

**Template Duplication Example:**
```
# manipulate.json before:
{{INSTRUCTIONS}}

{{CONTEXT}}      ← Duplicate!

Text to manipulate:
{{PREVIOUS_OUTPUT}}
```
Instruction appeared TWICE in all 29 configs using simple_manipulation pipeline!

### What Was Done

**Deleted Chunks:**
1. ✅ `translate.json` - Unused (0 configs), redundant
2. ✅ `prompt_interception.json` - Only 1 config used it, now uses simple_manipulation
3. ✅ `prompt_interception_lyrics.json` - BROKEN (invalid structure)
4. ✅ `prompt_interception_tags.json` - BROKEN (invalid structure)

**Fixed Template:**
```json
// manipulate.json - BEFORE
{
  "template": "{{INSTRUCTIONS}}\n\n{{CONTEXT}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}"
}

// manipulate.json - AFTER
{
  "template": "{{INSTRUCTION}}\n\nText to manipulate:\n\n{{PREVIOUS_OUTPUT}}"
}
```

**Updated chunk_builder.py:**
```python
# Removed TASK and CONTEXT aliases
replacement_context = {
    'INSTRUCTION': instruction_text,
    'INSTRUCTIONS': instruction_text,  # Backward compatibility only
    'INPUT_TEXT': context.get('input_text', ''),
    'PREVIOUS_OUTPUT': context.get('previous_output', ''),
    'USER_INPUT': context.get('user_input', ''),
    **context.get('custom_placeholders', {})
}
```

**Updated Pipelines:**
- `audio_generation.json`: prompt_interception → manipulate
- `image_generation.json`: prompt_interception → manipulate
- `music_generation.json`: [prompt_interception_tags, prompt_interception_lyrics] → [manipulate]
- `simple_interception.json`: [translate, manipulate] → [manipulate, manipulate]
- Deleted: `prompt_interception_single.json`

**Updated Configs:**
- `translation_en.json`: prompt_interception_single → simple_manipulation

### Current Architecture (Post-Consolidation)

**Chunk Inventory:**
1. ✅ `manipulate.json` - Universal text transformation
2. ✅ `comfyui_image_generation.json` - Image generation
3. ✅ `comfyui_audio_generation.json` - Audio generation

**Pipeline Structure:**
- 6 pipelines (down from 7)
- All text operations use `manipulate` chunk
- Content differentiation via `config.context` field

**Test Results:**
- ✅ 34 configs loaded successfully
- ✅ 6 pipelines loaded successfully
- ✅ All tests passing
- ✅ No duplication in rendered prompts
- ✅ Token efficiency improved (instruction appears once, not twice)

### Impact Analysis

**Affected Configs:**
- 29 configs using `simple_manipulation` → Cleaner prompts, no duplication
- 2 configs using `music_generation` → Simplified pipeline structure
- 2 configs using `audio_generation` → Updated to manipulate chunk
- 1 config using `prompt_interception_single` → Now uses simple_manipulation

**Token Savings:**
- Removed ~50-200 tokens per request (instruction no longer duplicated)
- Affects 30 configs

**Pedagogical Clarity:**
- "Prompt interception" remains a pedagogical concept at Config level
- Chunk level now purely technical (manipulate = transform text)
- No semantic confusion between chunk names and content

### Future Considerations

**Prompt Interception as Pedagogical Concept:**
- Configs can still use "Task / Context / Prompt" structure in their `config.context` field
- Example:
```json
{
  "context": "Task:\nTransform this prompt...\n\nContext:\nYou are a Dadaist artist...\n\nPrompt:"
}
```
- The structure is content, not template architecture

**Task-Type Metadata (Next Phase):**
- Add `task_type` to chunk metadata
- Link to model_selector.py categories (translation, vision, etc.)
- Enable task-based LLM selection

### Files Modified

**Chunks (Deleted):**
- `schemas/chunks/translate.json` ❌
- `schemas/chunks/prompt_interception.json` ❌
- `schemas/chunks/prompt_interception_lyrics.json` ❌
- `schemas/chunks/prompt_interception_tags.json` ❌

**Chunks (Modified):**
- `schemas/chunks/manipulate.json` (fixed template)

**Pipelines (Deleted):**
- `schemas/pipelines/prompt_interception_single.json` ❌

**Pipelines (Modified):**
- `schemas/pipelines/audio_generation.json`
- `schemas/pipelines/image_generation.json`
- `schemas/pipelines/music_generation.json`
- `schemas/pipelines/simple_interception.json`

**Configs (Modified):**
- `schemas/configs/translation_en.json`

**Engine (Modified):**
- `schemas/engine/chunk_builder.py` (removed TASK/CONTEXT aliases)

---

## 2025-10-26: REMOVAL of instruction_types System

### Decision
**Instruction_types System komplett entfernt** (instruction_types.json + instruction_resolver.py)

### Reasoning (Joerissen)
> "Instruction type war eine eigenständige Fehlentscheidung des LLM. Sie ist redundant und erzeugt ambivalente Datenverteilung."

**Technisches Problem:**
- Instruction_types beschrieben 6 Kategorien mit 17 Varianten von Textmanipulation/Analyse
- Das Auslagern führte zu komplizierten und redundanten Informationsverweisen
- Widersprach der sauberen 3-Schichten-Architektur (Chunks → Pipelines → Configs)

**Die 6 Kategorien waren:**
1. **translation** (3 variants: standard, culture_sensitive, rigid)
   - Zweck: Übersetzung mit unterschiedlichen Ansätzen
   - Problem: Übersetzungs-Nuancen gehören in Config-context, nicht in externes System

2. **manipulation** (5 variants: standard, creative, amplify, analytical, poetic)
   - Zweck: Texttransformation mit verschiedenen Stilen
   - Problem: "Creative" widerspricht theoretischem Ansatz (Haltungen statt Stile)
   - Problem: Diese "Stile" sind eigentlich Inhalte und gehören in Configs

3. **security** (2 variants: standard, strict)
   - Zweck: Content-Filtering unterschiedlicher Strenge
   - Problem: Sicherheits-Policy gehört in Config-Parameter, nicht in separate Typen

4. **image_analysis** (4 variants: formal, descriptive, iconographic, non_western)
   - Zweck: Bildanalyse-Methoden (Panofsky etc.)
   - Problem: Analyse-Methode ist Inhalt (gehört in Config), nicht Struktur

5. **prompt_optimization** (3 variants: image_generation, audio_generation, music_generation)
   - Zweck: Optimierung für verschiedene Medien-Backends
   - Problem: Media-spezifische Optimierung gehört in Chunk-Templates, nicht in Typen

6. **[weitere ungenutzte Kategorien]**
   - Viele instruction_types wurden in keinem Config referenziert
   - Redundanz: Configs enthielten bereits komplette instruction-Texte im context-Feld

**Architektonisches Problem:**
- Instruction_types waren ein viertes Layer zwischen Pipeline (Struktur) und Config (Inhalt)
- Erzeugte Ambivalenz: Gehört die Instruktion zur Struktur oder zum Inhalt?
- Antwort: Zum Inhalt! → `context` field in Config

### What Was Done
1. ✅ `schemas/instruction_types.json` → `.OBSOLETE`
2. ✅ `schemas/engine/instruction_resolver.py` → `.OBSOLETE`
3. ✅ Removed `instruction_type` field from all 34 configs
4. ✅ Removed from `Config` and `ResolvedConfig` dataclasses
5. ✅ Updated `chunk_builder.py`: Now uses `resolved_config.context` directly
6. ✅ Removed from `pipeline_executor.py`, `workflow_routes.py`, tests
7. ✅ All tests passing

### Current Architecture (Post-Removal)
**Three Clean Layers:**
- **Layer 1 - Chunks**: Template primitives (`manipulate.json`, `translate.json`, etc.)
- **Layer 2 - Pipelines**: Structural chunk sequences (no content)
- **Layer 3 - Configs**: User-facing content with `context` field

**What `context` field now does:**
- Contains complete instruction text (former "metaprompt")
- Populates `{{INSTRUCTION}}`, `{{INSTRUCTIONS}}`, `{{TASK}}`, `{{CONTEXT}}` placeholders
- No more indirection via instruction_types.json

### Future Consideration (Joerissen)
> "Wenn wir später jedoch feststellen, dass devserver eine Information über den Character einer pipeline-config-Information in den Metadaten einer config benötigen würde, dann würden wir diesen Klassifikator wieder herstellen. Aber nur als Information in den meta-daten, in keiner Weise als funktionale Referenz für den Code."

**IF we need classification later:**
- ✅ Add as metadata field: `"meta": {"instruction_type": "manipulation"}`
- ✅ For UI display/filtering only
- ❌ NEVER as functional code reference
- ❌ NEVER as indirection to external file

### Files Modified
**Core Engine:**
- `schemas/engine/config_loader.py` (removed instruction_type from dataclasses)
- `schemas/engine/chunk_builder.py` (now uses context directly)
- `schemas/engine/pipeline_executor.py` (removed from metadata)
- `schemas/engine/instruction_resolver.py` → `.OBSOLETE`

**Configs:**
- All 34 files in `schemas/configs/` (removed instruction_type field)

**Routes:**
- `my_app/routes/workflow_routes.py` (removed from API response)

**Tests:**
- `test_refactored_system.py` (removed instruction_resolver tests)

**Obsolete Files:**
- `schemas/instruction_types.json.OBSOLETE`
- `schemas/engine/instruction_resolver.py.OBSOLETE`

---

## 2025-10-26: REMOVAL of Legacy DevServer Code

### Decision
**All legacy engine modules removed** - DevServer no longer needs legacy code from pre-refactoring phase

### Reasoning (Joerissen)
> "der legacy-server läuft auf Port 5000 stabil (und wird nicht angetastet, wird aktuell verwendet). Devserver braucht m.E. keine Legacy-codes mehr. [...] Pipeline-Config-System ist so leistungsfähig dass wir alles 'übersetzen' können. Und zur Not kann legacy immer parallel betrieben werden."

**Context:**
- Legacy-Server (Port 5000) runs independently and stably
- DevServer's new Pipeline-Config-System is fully capable
- No need for code duplication between legacy and devserver
- Parallel operation possible when needed (no integration required)

### What Was Done
1. ✅ `schemas/engine/schema_registry.py` → `.OBSOLETE`
2. ✅ `schemas/engine/chunk_builder_old.py` → `.OBSOLETE`
3. ✅ `schemas/engine/pipeline_executor_old.py` → `.OBSOLETE`
4. ✅ Updated `schemas/__init__.py` - removed SchemaRegistry import
5. ✅ `schemas/schema_data/` → `schemas/schema_data_LEGACY_TESTS/`
6. ✅ All tests still passing (34 configs loaded)

### Files Marked OBSOLETE
**Engine Modules:**
- `schemas/engine/schema_registry.py.OBSOLETE` (pre-refactoring registry)
- `schemas/engine/chunk_builder_old.py.OBSOLETE` (pre-refactoring builder)
- `schemas/engine/pipeline_executor_old.py.OBSOLETE` (pre-refactoring executor)

**Test Data:**
- `schemas/schema_data_LEGACY_TESTS/` (old test configs)

### Active Engine Architecture (Post-Cleanup)
**Core Modules (ONLY):**
- `config_loader.py` - Config + Pipeline loader
- `chunk_builder.py` - Template-based chunk builder
- `pipeline_executor.py` - Pipeline orchestration
- `backend_router.py` - Backend routing (Ollama/ComfyUI/OpenRouter)
- `model_selector.py` - Model selection (eco/fast modes)
- `comfyui_workflow_generator.py` - ComfyUI workflow generation
- `prompt_interception_engine.py` - Legacy bridge for prompt interception

**Status:** Clean, no legacy code dependencies ✅

---

## 2025-10-26: Directory Restructure (configs_new → configs)

### Decision
Renamed `configs_new/` to `configs/` (primary config directory)
Renamed old `configs/` to `configs_old_DELETEME/`

### Reasoning
Previous task created `configs_new` instead of replacing `configs` → caused path reference problems

### What Was Done
```bash
mv configs configs_old_DELETEME
mv configs_new configs
# Updated all Python file references with sed
```

---

## TEMPLATE for Future Entries

## YYYY-MM-DD: [Decision Title]

### Decision
[What was decided]

### Reasoning
[Why - technical, pedagogical, architectural reasons]

### What Was Done
[Concrete changes - files, code, tests]

### Future Considerations
[Important notes for future development]

### Files Modified
[List of affected files]

---

## Development Principles (Standing Decisions)

### Architecture Principles
1. **Three-Layer Architecture (Immutable)**
   - Chunks (primitives) → Pipelines (structure) → Configs (content)
   - NO fourth layer for indirection
   - Content belongs in Config, not external references

2. **Context Field = Complete Instruction**
   - `context` contains full instruction text (former metaprompt)
   - No indirection via external files
   - Direct usage in chunk_builder.py

3. **Terminology (Joerissen)**
   - Avoid terms like "creative" - contradicts theoretical approach
   - Focus: "Haltungen statt Stile" (attitudes not styles)
   - No "solutionistic" language

### Data Management Principles
1. **NO Data Duplication**
   - Single source of truth for each data type
   - Configs in `schemas/configs/*.json` (not in registry/database)
   - Read directly from files

2. **Metadata Philosophy**
   - Metadata = Information ABOUT the data (display, categorization)
   - Metadata ≠ Functional code references
   - Metadata can contain classification for UI purposes only

### Testing Principles
1. **Test Files**
   - `test_refactored_system.py` - Architecture component tests
   - `test_pipeline_execution.py` - Full execution tests (requires Ollama)

2. **Test Coverage Required**
   - Every major architectural change needs test updates
   - Tests must pass before task completion

---

## History of Obsolete Decisions

### ❌ Instruction Types System (Removed 2025-10-26)
**Why it was created:** Previous LLM task tried to create reusable instruction templates
**Why it failed:** Created redundant fourth layer, ambivalent data distribution
**Lesson:** Keep architecture flat - no indirection layers between structure and content

---

## Decision 2025-10-29: Pre-Interception 4-Stage System Implementation (Stage 1+2)

### Context
User requested implementation of 4-Stage Pre-Interception System designed in Session 5 (documented in `PRE_INTERCEPTION_DESIGN.md`). System needed to:
- Auto-translate German text to English
- Run safety checks with Llama-Guard
- Do this BEFORE the main interception pipeline (dada, bauhaus, etc.)

### The Challenge: Loop Prevention
Initial design consideration: How to prevent infinite loops when pre-interception configs call themselves?

**Explored Approaches:**
1. ❌ Language detection (`is_german_text()`) - Unnecessary complexity, translation handles it
2. ❌ Multiple flags (`skip_pre_translation`, `skip_safety_check`) - Too granular
3. ✅ **Single `system_pipeline: true` flag** - Simple, clear, effective

### Decision: `system_pipeline: true` Flag
**Chosen Approach:**
```python
is_system_pipeline = resolved_config.meta.get('system_pipeline', False)
if not is_system_pipeline:
    # Run Stage 1: Pre-Interception
    # Stage 1a: Translation
    # Stage 1b: Safety
# Run Stage 2: Main Pipeline
```

**Rationale:**
- System pipelines (pre-interception configs) have `system_pipeline: true`
- User pipelines (dada, bauhaus, etc.) don't have this flag
- Single flag = simple logic, no ambiguity
- Configs in subdirectories (`pre_interception/`, `pre_output/`) provide additional organization

### Decision: No Language Detection
**User Statement:**
> "ich weiß nicht woher die idee kommt dass man testen müsste ob etwas deutscher Text ist [...] Das ist natürlich Unsinn. Entferne diese Funktion: JEDE Eingabe wird IMMER dieser pipeline zugeführt."

**Chosen Approach:**
- Translation pipeline runs for ALL inputs (German AND English)
- Translation config itself handles language detection via its instruction prompt:
  ```
  "If text is already in English, return it unchanged!"
  ```

**Rationale:**
- Simpler logic - no language detection function needed
- LLM handles edge cases better than regex/heuristics
- Consistent behavior - same code path for all languages

### Decision: `model_override` in Config Meta
**Problem:** Safety config needs to use `llama-guard3:8b`, but chunk default was `gemma2:9b`

**Solution:** Check `config.meta.model_override` before `chunk.model`
```python
base_model = resolved_config.meta.get('model_override') or template.model
final_model = model_selector.select_model_for_mode(base_model, execution_mode)
```

**Impact:**
- Safety config: `"model_override": "llama-guard3:8b"` → Uses correct model
- Other configs: No override → Use chunk default

### Decision: Recursive Config Loading
**Problem:** Subdirectories (`pre_interception/`, `pre_output/`) not scanned

**Solution:** Change `glob("*.json")` → `glob("**/*.json")` in `config_loader.py`

**Impact:**
- Config names become relative paths: `pre_interception/safety_llamaguard`
- Clear organization of system vs user configs
- No naming conflicts

### Decision: mistral-nemo Instead of gemma2:9b
**Problem:** gemma2:9b was very slow (~30s+ per text transformation)

**Solution:** Changed `manipulate.json` chunk from `gemma2:9b` → `mistral-nemo:latest`

**Performance Impact:**
- Translation: ~4s (was ~10s)
- Safety: ~1.5s (with llama-guard3:8b)
- Dada transformation: ~4s (was ~12s)
- **Total: ~10s (was 30s+) - 3x faster!** ⚡

**User Context:**
> "Es ist immer noch (oder wieder) gemma2:9b überall. Das wollten wir komplett austauschen gegen Nemo in der Konfigurationsdatei (gemma2 braucht ewig)."

### Implementation Results

**Files Created:**
- `schemas/configs/pre_interception/correction_translation_de_en.json`
- `schemas/configs/pre_interception/safety_llamaguard.json`
- `schemas/configs/pre_output/image_safety_refinement.json` (not yet active)
- `schemas/llama_guard_explanations.json` (German error messages)

**Files Modified:**
- `schemas/engine/pipeline_executor.py` - Stage 1+2 logic, helper functions
- `schemas/engine/config_loader.py` - Recursive glob, relative path names
- `schemas/engine/chunk_builder.py` - model_override support
- `schemas/chunks/manipulate.json` - mistral-nemo instead of gemma2

**Helper Functions Added:**
- `parse_llamaguard_output()` - Handles both "safe" and "unsafe,S8, Violent Crimes" formats
- `build_safety_message()` - German error messages from S-codes
- `parse_preoutput_json()` - For Stage 3 (not yet used)

**What Works:**
- ✅ German text → Translation → Safety → Interception → Output
- ✅ English text → Safety → Interception → Output (no unnecessary translation)
- ✅ Unsafe content blocked with German messages
- ✅ llama-guard3:8b for safety, mistral-nemo for transformations
- ✅ 3x performance improvement

**What's Missing:**
- Stage 3: Pre-Output safety before media generation (config exists, not active)
- Stage 4: Media generation integration with Stage 3

### Lessons Learned
1. **Keep it Simple:** One flag (`system_pipeline`) beats multiple flags
2. **Trust the LLM:** No need for language detection, LLM handles it
3. **Config Over Code:** model_override in config beats hardcoded logic
4. **User Knows Best:** Listen when user says "this is nonsense" 😊

---

**Last Updated:** 2025-10-29
**Next Task:** Implement Stage 3+4 (Pre-Output safety before media generation)
