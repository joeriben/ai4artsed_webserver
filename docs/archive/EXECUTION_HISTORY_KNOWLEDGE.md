# Execution History Implementation - Essential Knowledge

**Date:** 2025-11-03 Session 17
**Purpose:** Document architectural understanding gained before implementation
**Status:** Pre-Implementation Knowledge Capture

---

## Critical Lesson Learned

**NEVER implement before understanding the architecture completely.**

I initially created data structures based on assumptions about how `output_requests` work, without reading the actual code. This was wrong. The user correctly stopped me and insisted I understand the architecture first.

---

## How Stage 3-4 Loop ACTUALLY Works (Verified from Code)

### File: `my_app/routes/schema_pipeline_routes.py` (lines 222-330)

```python
# Step 1: Config specifies which output configs to use
media_preferences = config.media_preferences or {}
output_configs = media_preferences.get('output_configs', [])

# Example from image_comparison.json:
# "media_preferences": {
#     "output_configs": ["sd35_large", "gpt5_image"]
# }

# Step 2: Build list of configs to execute
if output_configs:
    # Multi-output case: Use explicit list
    configs_to_execute = output_configs  # ["sd35_large", "gpt5_image"]
elif default_output and default_output != 'text':
    # Single-output case: Lookup from default_output type
    output_config_name = lookup_output_config(default_output, execution_mode)
    configs_to_execute = [output_config_name]  # ["sd35_large"]
else:
    # Text-only case
    configs_to_execute = []

# Step 3: Loop through each config
for i, output_config_name in enumerate(configs_to_execute):
    # Stage 3: Safety check for THIS config
    safety_result = execute_stage3_safety(...)

    if not safety_result['safe']:
        media_outputs.append({'status': 'blocked', ...})
        continue  # Skip Stage 4 for this config

    # Stage 4: Execute THIS config → generates ONE output
    output_result = pipeline_executor.execute_pipeline(output_config_name, ...)

    # Collect result
    media_outputs.append({
        'config': output_config_name,
        'output': output_result.final_output,  # ONE output per config
        'media_type': media_type
    })
```

### Key Facts

1. **No `count` parameter exists** - Each config generates exactly 1 output
2. **Multiple outputs** = List multiple configs in `output_configs` array
3. **Loop variable `i`** = Iteration number (0, 1, 2, ...)
4. **Each iteration** = One complete Stage 3-4 cycle for one config

---

## What DOESN'T Exist (Common Misconceptions)

### ❌ Misconception 1: `output_requests` with `count`

```python
# THIS DOES NOT EXIST:
output_requests = [
    {"config": "sd35_large", "count": 3, "prompt": "..."}
]
```

**Reality:** The `output_requests` structure in `docs/ARCHITECTURE.md` is **planned future functionality**, not current implementation.

### ❌ Misconception 2: Batch Generation

```python
# THIS DOES NOT EXIST:
result = execute_pipeline("sd35_large", count=3)
# Returns 3 images
```

**Reality:** Each config execution produces exactly 1 output. To get 3 images, you must:
- Option A: List config 3 times: `["sd35_large", "sd35_large", "sd35_large"]`
- Option B: Call the pipeline 3 times separately

### ❌ Misconception 3: Pipeline Returns output_requests

```python
# THIS DOES NOT EXIST:
pipeline_result = execute_pipeline("dada", ...)
# pipeline_result.output_requests = [...]
```

**Reality:** Pipeline returns only `final_output` (transformed text). DevServer reads `media_preferences` from the **config JSON file**, not from pipeline result.

---

## Current Multi-Output Flow (Verified Example)

### Config: `image_comparison.json`

```json
{
  "name": "image_comparison",
  "pipeline": "text_transformation",
  "context": "Transform the prompt in Dada style",
  "media_preferences": {
    "output_configs": ["sd35_large", "gpt5_image"]
  }
}
```

### Execution Flow

```
Stage 1 (ONCE):
  - Translation: "Eine Blume" → "A flower"
  - Safety: ✓ PASSED

Stage 2 (ONCE):
  - Execute text_transformation pipeline
  - Result: "BLUME! CHAOS! SINNLOS!"

Stage 3-4 Loop (TWICE - once per output_config):

  Loop Iteration 1 (i=0, config="sd35_large"):
    Stage 3:
      - Check safety for "BLUME! CHAOS! SINNLOS!"
      - Result: ✓ SAFE
    Stage 4:
      - Execute sd35_large pipeline
      - Result: image file → /exports/xyz1.png (prompt_id: xyz1)

  Loop Iteration 2 (i=1, config="gpt5_image"):
    Stage 3:
      - Check safety for "BLUME! CHAOS! SINNLOS!"
      - Result: ✓ SAFE
    Stage 4:
      - Execute gpt5_image pipeline
      - Result: image URL → https://cdn.openai.com/...

Final Result:
  media_outputs = [
    {config: "sd35_large", output: "xyz1", media_type: "image"},
    {config: "gpt5_image", output: "https://...", media_type: "image"}
  ]
```

---

## Implications for Execution History Design

### What Needs to Be Tracked

1. **Stage 1 items** (execute once):
   - User input text
   - Translation result
   - Stage 1 safety check result

2. **Stage 2 items** (execute once):
   - Interception result (transformed prompt)

3. **Stage 3-4 items** (execute N times, once per output_config):
   - For EACH iteration:
     - Which config is being executed (`output_config_name`)
     - Which iteration number this is (`i` from loop, or 1-based: 1, 2, 3)
     - Stage 3 safety check result
     - Stage 4 output (file path, URL, or prompt_id)

### Critical Design Question

**How do we identify which loop iteration an output came from?**

Options:
- A) Use loop counter `i` (0, 1, 2) - matches code
- B) Use 1-based numbering (1, 2, 3) - more human-friendly
- C) Use config name only - loses order info if same config listed twice
- D) Use combination: `(config_name, iteration_within_that_config)`

**Example Problem:** If `output_configs = ["sd35_large", "gpt5_image", "sd35_large"]`:
- Need to distinguish between the TWO sd35_large executions
- Config name alone is insufficient
- Need iteration number

---

## Research Requirements (From User)

### User Quote (Session 17):

> "We have different media types to store: text, image, sound, later: video, potentially others such as 3D-files. These files have a meaningful order at the time of production/inference (translation, security check result, prompt interception (1, 2, 3, ...), (Stage3-Check result + media output) (1, 2, 3, ...)"

### Key Requirements

1. **Preserve order** - Items must maintain chronological sequence
2. **Count multiple outputs** - "prompt interception (1, 2, 3)" and "media output (1, 2, 3)"
3. **Media-sensitive** - Know what type each item is (text, image, audio)
4. **Semantic metadata** - Know what each item represents (translation vs. interception vs. output)
5. **Flexible frontend** - Show/hide items based on audience:
   - Students: Only final outputs
   - Advanced: Show transformation process
   - Researchers: Show everything including safety checks

---

## Questions That Still Need Answering

### Q1: Loop Iteration Numbering

For tracking Stage 3-4 loop iterations:
- **Global iteration counter** (1, 2, 3 across ALL outputs)?
- **Per-config counter** (e.g., "2nd sd35_large execution")?
- **Both?**

**Example:**
```
output_configs = ["sd35_large", "gpt5_image", "sd35_large"]

Option A - Global:
  Iteration 1: sd35_large
  Iteration 2: gpt5_image
  Iteration 3: sd35_large

Option B - Per-Config:
  sd35_large #1
  gpt5_image #1
  sd35_large #2
```

### Q2: Recursive Pipelines (Stille Post)

How to track recursive executions? Example: `stillepost.json` runs 8 iterations.
- Are these 8 separate Stage 2 executions?
- Or is it 1 Stage 2 execution with internal iterations?
- How does this affect item numbering?

### Q3: Backend Failures

If Stage 4 fails (ComfyUI crashes, API timeout):
- Do we log a failed output item?
- Or just mark execution as error?
- How do we distinguish "blocked by safety" vs. "technical failure"?

---

## Documentation That Helped

### Must-Read Files

1. **`docs/ARCHITECTURE PART I.md`** (lines 39-200)
   - Section 1.2: Core Architecture diagram
   - Shows Stage 3-4 loop clearly
   - Key quote: "FOR EACH request in pipeline_result.output_requests"
   - **BUT:** This describes PLANNED architecture, not current implementation

2. **`devserver/RULES.md`**
   - Section 1: Explains Interception vs. Output pipelines
   - Critical distinction: Output pipelines are DUMB (1 input → 1 output)

3. **`my_app/routes/schema_pipeline_routes.py`** (lines 222-330)
   - **ACTUAL IMPLEMENTATION** of Stage 3-4 loop
   - Shows `output_configs` array usage
   - Shows `for i, output_config_name in enumerate(configs_to_execute)`

### Config Examples

- **`schemas/configs/interception/dada.json`** - Single output case
- **`schemas/configs/interception/image_comparison.json`** - Multiple outputs case

---

## Recommended Next Steps (For Fresh Task)

1. **Create comprehensive design doc** BEFORE any code
2. **Answer the 3 questions** above (with user input)
3. **Draw execution flow diagram** showing what gets logged when
4. **Design data structures** based on answers
5. **Get user approval** on design
6. **ONLY THEN** start implementing

---

## What NOT To Do

❌ Implement data structures before understanding architecture
❌ Assume documentation describes current implementation (may be future plans)
❌ Use confusing terminology like "output_config_index" without explaining
❌ Use `rm` command without user permission
❌ Start coding before getting design approval

---

**Created:** 2025-11-03 Session 17
**Purpose:** Preserve hard-won architectural understanding for next session
**Status:** Knowledge capture complete, ready for fresh design task
