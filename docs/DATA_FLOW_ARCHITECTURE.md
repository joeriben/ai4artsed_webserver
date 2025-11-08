# Data Flow Architecture - How Data Passes Between Pipeline Stages

**Created:** 2025-11-08
**Status:** AUTHORITATIVE
**Purpose:** Document the ACTUAL data flow mechanism (not imagined complexity)

---

## Executive Summary

**The system is simple.** Data flows between pipeline stages via a single mechanism:

```python
context.custom_placeholders: Dict[str, Any]
```

Any data type (string, dict, list, image bytes) can pass between stages by putting it in `custom_placeholders`. ChunkBuilder automatically makes it available as placeholders.

---

## Core Mechanism

### 1. PipelineContext Structure

**Location:** `schemas/engine/pipeline_executor.py:40`

```python
@dataclass
class PipelineContext:
    """Pipeline context for data exchange between steps"""
    input_text: str
    user_input: str
    previous_outputs: List[str] = field(default_factory=list)
    custom_placeholders: Dict[str, Any] = field(default_factory=dict)  # ← THE KEY
    pipeline_metadata: Dict[str, Any] = field(default_factory=dict)
```

**How it works:**
- Each pipeline execution gets ONE context object
- Context is passed to every chunk in the pipeline
- Chunks can read from and write to `custom_placeholders`

### 2. ChunkBuilder Merges Placeholders

**Location:** `schemas/engine/chunk_builder.py:96`

```python
def build_chunk(self, chunk_name, resolved_config, context, ...):
    replacement_context = {
        'INPUT_TEXT': context.get('input_text', ''),
        'PREVIOUS_OUTPUT': context.get('previous_output', ''),
        'USER_INPUT': context.get('user_input', ''),

        **context.get('custom_placeholders', {}),  # ← Merges ALL custom data
        **resolved_config.parameters
    }

    # Now ANY key in custom_placeholders becomes a {{PLACEHOLDER}}
    processed_template = self._replace_placeholders(template.template, replacement_context)
```

**Example:**
```python
# Chunk A puts data into context
context.custom_placeholders['PART_A'] = "a cute puppy"
context.custom_placeholders['PART_B'] = "in a garden"

# Chunk B's template can use:
# "{{PART_A}}" → "a cute puppy"
# "{{PART_B}}" → "in a garden"
```

---

## Data Flow Patterns

### Pattern 1: Sequential Text Processing (Simple)

**Example:** Dada interception (Stage 1 → Stage 2 → Stage 4)

```
Stage 1 (DevServer):
  INPUT: "Eine Blume"
  → Translation: "A flower"
  → context.input_text = "A flower"

Stage 2 (text_transformation pipeline):
  Chunk: manipulate
  → Reads: {{INPUT_TEXT}} = "A flower"
  → Outputs: "A chaotic collage of petals..."
  → context.add_output("A chaotic collage...")

Stage 4 (gpt5_image):
  Chunk: output_image_gpt5
  → Reads: {{PREVIOUS_OUTPUT}} = "A chaotic collage..."
  → Generates image
```

### Pattern 2: Structured Output (JSON) → Multiple Inputs

**Example:** Vector fusion (Stage 2 outputs JSON, Stage 4 needs both parts)

```
Stage 2 (text_semantic_split pipeline):
  Chunk: text_split
  → Reads: {{INPUT_TEXT}} = "a cute puppy playing in a garden"
  → Outputs JSON string: '{"part_a": "a cute puppy", "part_b": "playing in a garden"}'
  → context.add_output('{"part_a": "...", "part_b": "..."}')

[DevServer MUST parse JSON and populate custom_placeholders]
  result = json.loads(context.get_previous_output())
  context.custom_placeholders['PART_A'] = result['part_a']
  context.custom_placeholders['PART_B'] = result['part_b']

Stage 4 (vector_fusion_generation pipeline):
  Chunk: output_vector_fusion_clip_sd35
  → Reads: {{PART_A}} = "a cute puppy"
  → Reads: {{PART_B}} = "playing in a garden"
  → Dual CLIP encoding + fusion
  → Generates image
```

### Pattern 3: Multiple Input Types (Text + Image)

**Example:** Image-to-image with text guidance (future)

```
Stage 1 (DevServer):
  INPUT: {"text": "make it cyberpunk", "image": <bytes>}
  → context.input_text = "make it cyberpunk"
  → context.custom_placeholders['INPUT_IMAGE'] = image_bytes

Stage 2 (image_transformation pipeline):
  Chunk: image_manipulation
  → Reads: {{INPUT_TEXT}} = "make it cyberpunk"
  → Reads: {{INPUT_IMAGE}} = image_bytes
  → Outputs modified image
```

---

## What `input_requirements` ACTUALLY Does

**MISCONCEPTION:** `input_requirements` controls data flow between stages
**REALITY:** `input_requirements` is metadata for Stage 1 pre-processing only

### Purpose 1: DevServer Stage 1 Logic

**Location:** `my_app/routes/schema_pipeline_routes.py`

```python
pipeline = config_loader.get_pipeline(config.pipeline_name)
input_reqs = pipeline.input_requirements  # {"texts": 2, "images": 1}

# DevServer uses this to know what pre-processing to run:
if "texts" in input_reqs:
    for i in range(input_reqs["texts"]):
        # Run translation + safety on each text

if "images" in input_reqs:
    for i in range(input_reqs["images"]):
        # Run image safety on each image
```

### Purpose 2: Frontend UI Generation

**Location:** `schema_pipeline_routes.py:1483`

```python
@schema_bp.route('/config/<config_id>/pipeline', methods=['GET'])
def get_config_pipeline(config_id):
    return jsonify({
        "input_requirements": pipeline.input_requirements or {},
        # Frontend uses this to know how many input bubbles to show
    })
```

**Frontend logic:**
- `{"texts": 1}` → Show 1 text input bubble
- `{"texts": 2}` → Show 2 text input bubbles (e.g., AceStep lyrics + tags)
- `{"texts": 1, "images": 1}` → Show 1 text + 1 image input bubble

### What It DOESN'T Do

❌ Control data passing between stages
❌ Define placeholder names
❌ Restrict what data can be in custom_placeholders
❌ Enforce any runtime validation

**Data passing uses custom_placeholders, not input_requirements!**

---

## Working Example: Music Generation (AceStep)

**File:** `schemas/pipelines/music_generation.json`

```json
{
  "input_requirements": {
    "texts": 2
  }
}
```

**What this means:**
- Stage 1: DevServer expects 2 text inputs from user
- Frontend: Shows 2 text input bubbles
- Stage 1: Runs translation + safety on BOTH texts

**How data flows:**
```python
# User provides 2 texts
input_text_1 = "happy upbeat"  # tags
input_text_2 = "I love you baby"  # lyrics

# DevServer Stage 1
context.input_text = input_text_1
context.custom_placeholders['LYRICS'] = input_text_2

# Stage 2 manipulate chunk
template = "Create music with tags: {{INPUT_TEXT}} and lyrics: {{LYRICS}}"
# Resolves to: "Create music with tags: happy upbeat and lyrics: I love you baby"
```

---

## Implementing New Multi-Input Workflows

### Step 1: Define Pipeline Structure

**Example:** Vector fusion needs split text parts

```json
{
  "name": "vector_fusion_generation",
  "pipeline_stage": "4",
  "input_requirements": {
    "texts": 1  // Stage 1 will translate/safety-check 1 text
  }
}
```

### Step 2: Define Chunk Template

**Example:** Output chunk expects PART_A and PART_B

```json
{
  "name": "output_vector_fusion_clip_sd35",
  "input_mappings": {
    "prompt_part_a": {
      "source": "{{PART_A}}"
    },
    "prompt_part_b": {
      "source": "{{PART_B}}"
    }
  }
}
```

### Step 3: Populate custom_placeholders

**Two options:**

**Option A: Inside a chunk** (Stage 2 splitting chunk)
```python
# Chunk outputs JSON
output = '{"part_a": "...", "part_b": "..."}'

# PipelineExecutor or DevServer parses and populates
data = json.loads(output)
context.custom_placeholders.update({
    'PART_A': data['part_a'],
    'PART_B': data['part_b']
})
```

**Option B: DevServer orchestration** (before Stage 4)
```python
# After Stage 2 completes
stage2_result = pipeline_executor.execute_pipeline('text_semantic_split', input_text)
split_data = json.loads(stage2_result.final_output)

# Before Stage 4
context = PipelineContext(...)
context.custom_placeholders['PART_A'] = split_data['part_a']
context.custom_placeholders['PART_B'] = split_data['part_b']

# Execute Stage 4
stage4_result = pipeline_executor.execute_pipeline('vector_fusion_generation', '', context=context)
```

---

## Key Takeaways

1. **custom_placeholders is the ONLY mechanism** for passing data between stages
2. **input_requirements is metadata** for Stage 1 pre-processing and Frontend UI
3. **Placeholders are simple** - any Dict key becomes {{KEY}}
4. **ChunkBuilder merges everything** automatically
5. **Data types don't matter** - strings, dicts, lists, bytes all work

---

## Common Mistakes

### ❌ Mistake 1: Thinking input_requirements controls data flow

```json
// WRONG: This doesn't create PART_A and PART_B placeholders
{
  "input_requirements": {
    "split_text": {
      "part_a": "string",
      "part_b": "string"
    }
  }
}
```

**Correct:** Use custom_placeholders in code:
```python
context.custom_placeholders['PART_A'] = "..."
context.custom_placeholders['PART_B'] = "..."
```

### ❌ Mistake 2: Creating complex nested structures in pipelines

**WRONG:** Inventing special handling for structured data
**CORRECT:** Just use the Dict - it's already there!

### ❌ Mistake 3: Not parsing JSON outputs

```python
# Stage 2 outputs: '{"part_a": "...", "part_b": "..."}'

# WRONG: Pass JSON string to Stage 4
context.custom_placeholders['DATA'] = json_string

# CORRECT: Parse and flatten
data = json.loads(json_string)
context.custom_placeholders.update(data)
```

---

## References

- **PipelineContext:** `schemas/engine/pipeline_executor.py:40`
- **ChunkBuilder placeholder merging:** `schemas/engine/chunk_builder.py:96`
- **DevServer Stage 1 logic:** `my_app/routes/schema_pipeline_routes.py:500`
- **Working example:** `schemas/pipelines/music_generation.json`

---

**Version:** 1.0
**Last Updated:** 2025-11-08
**Next Review:** When implementing new multi-input workflows
