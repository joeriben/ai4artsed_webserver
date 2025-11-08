# Vector Fusion Workflow - Implementation Plan

**Created:** 2025-11-08
**Status:** Implementation Plan
**Based on:** DATA_FLOW_ARCHITECTURE.md

---

## Goal

Implement the "Split-and-Combine" vector manipulation workflow:
1. User inputs: "a cute puppy playing in a garden"
2. Stage 2: LLM splits into semantic parts (part_a, part_b)
3. Stage 4: CLIP encodes both parts separately, fuses vectors, generates image

**Pedagogical value:** Shows how semantic relationships in vector space affect AI generation.

---

## Current Status

### ✅ Files Already Created (Last Session)

1. `schemas/chunks/text_split.json` - Text splitting chunk (needs fixes)
2. `schemas/chunks/output_vector_fusion_clip_sd35.json` - ComfyUI workflow ✅ VERIFIED
3. `schemas/pipelines/text_semantic_split.json` - Stage 2 pipeline ✅ VERIFIED
4. `schemas/pipelines/vector_fusion_generation.json` - Stage 4 pipeline ✅ VERIFIED
5. `schemas/configs/split_and_combine_setup.json` - Stage 2 config ✅ EXISTS
6. `schemas/configs/vector_fusion_linear_clip.json` - Stage 4 config ✅ VERIFIED
7. `my_app/routes/schema_pipeline_routes.py` - Has conditional Stage 3 logic ✅

### ❌ What Needs Fixing/Implementing

1. **text_split.json** - Missing required fields (model, parameters)
2. **Stage 2 → Stage 4 orchestration** - JSON parsing + custom_placeholders population
3. **API endpoint or workflow** - How does user invoke this?
4. **Testing** - End-to-end verification

---

## Implementation Steps

### Step 1: Fix text_split.json Chunk ⚠️ CRITICAL

**Problem:** Missing required fields that ChunkBuilder expects

**Fix:**
```json
{
  "name": "text_split",
  "description": "Semantic text splitting - splits input into structured parts",
  "template": "{{CONTEXT}}\n\nInput:\n{{INPUT_TEXT}}",
  "backend_type": "ollama",
  "model": "gpt-OSS:20b",  // ADD THIS
  "parameters": {           // ADD THIS
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": false,
    "keep_alive": "10m"
  },
  "meta": {
    "chunk_type": "text_split",
    "output_format": "text",  // NOT "json" - ChunkBuilder doesn't use this
    "estimated_duration": "fast"
  }
}
```

**Key changes:**
- Add `model` field (copy from manipulate.json)
- Add `parameters` object (copy from manipulate.json)
- Remove invented fields: `type`, top-level `task_type`, `output_format`
- Simplify `meta` to match existing chunks

### Step 2: Implement Stage 2 → Stage 4 Orchestration

**Option A: New Route `/api/schema/pipeline/execute_multi_stage`**

Handles multi-stage workflows where Stage 2 output becomes Stage 4 input.

**Location:** `my_app/routes/schema_pipeline_routes.py`

```python
@schema_bp.route('/pipeline/execute_multi_stage', methods=['POST'])
def execute_multi_stage():
    """
    Execute multi-stage workflow (Stage 2 → Stage 4)

    Example: Vector fusion
    - Stage 2: text_semantic_split → JSON output
    - Parse JSON → custom_placeholders
    - Stage 4: vector_fusion_generation → image
    """
    data = request.get_json()

    stage2_config = data.get('stage2_config')  # e.g., "split_and_combine_setup"
    stage4_config = data.get('stage4_config')  # e.g., "vector_fusion_linear_clip"
    input_text = data.get('input_text')

    # Execute Stage 2
    stage2_result = pipeline_executor.execute_pipeline(stage2_config, input_text, ...)

    # Parse JSON output
    split_data = json.loads(stage2_result.final_output)

    # Create context with custom_placeholders
    context = PipelineContext(
        input_text="",  # Not used in Stage 4
        user_input=input_text
    )
    context.custom_placeholders.update({
        'PART_A': split_data['part_a'],
        'PART_B': split_data['part_b']
    })

    # Execute Stage 4 with populated placeholders
    stage4_result = pipeline_executor.execute_pipeline(
        stage4_config,
        input_text="",  # Not used
        context=context,  # ← Pass pre-populated context
        ...
    )

    return jsonify({
        'stage2_output': split_data,
        'stage4_output': stage4_result.final_output,
        'media_output': ...
    })
```

**Option B: Modify execute_pipeline to Auto-Handle JSON**

Add logic to PipelineExecutor to detect JSON output and auto-populate placeholders.

```python
# In pipeline_executor.py
async def _execute_pipeline_steps(...):
    for step in steps:
        output = await self._execute_single_step(step, context, ...)

        # Try to parse as JSON and populate custom_placeholders
        try:
            parsed = json.loads(output)
            if isinstance(parsed, dict):
                context.custom_placeholders.update(parsed)
                logger.info(f"[JSON-OUTPUT] Parsed and added to custom_placeholders: {list(parsed.keys())}")
        except:
            pass  # Not JSON, treat as normal string output

        context.add_output(output)
```

**Recommendation: Option B is simpler and more automatic.**

### Step 3: Modify PipelineExecutor to Accept Pre-Populated Context

**Problem:** Current `execute_pipeline()` always creates a new context

**Fix:** Allow passing a pre-populated context

```python
# In pipeline_executor.py:95
async def execute_pipeline(
    self,
    config_name: str,
    input_text: str,
    user_input: Optional[str] = None,
    execution_mode: str = 'eco',
    safety_level: str = 'kids',
    tracker=None,
    config_override=None,
    context_override: Optional[PipelineContext] = None  # ADD THIS
) -> PipelineResult:

    # Create pipeline context (or use override)
    if context_override:
        context = context_override
        logger.info("[CONTEXT-OVERRIDE] Using pre-populated context")
    else:
        context = PipelineContext(
            input_text=input_text,
            user_input=user_input or input_text
        )
```

### Step 4: Test Workflow

**Test A: Stage 2 Only (Text Splitting)**

```bash
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "split_and_combine_setup",
    "input_text": "a cute puppy playing in a garden",
    "execution_mode": "eco",
    "safety_level": "kids"
  }'
```

**Expected output:**
```json
{
  "final_output": "{\"part_a\": \"a cute puppy\", \"part_b\": \"playing in a garden\"}",
  "status": "completed"
}
```

**Test B: Stage 4 Only (Vector Fusion with Manual Input)**

```python
# Manual test via Python
context = PipelineContext(input_text="", user_input="")
context.custom_placeholders['PART_A'] = "a cute puppy"
context.custom_placeholders['PART_B'] = "playing in a garden"

result = await pipeline_executor.execute_pipeline(
    'vector_fusion_linear_clip',
    '',
    context_override=context
)
```

**Test C: Full Workflow (Stage 2 → Stage 4)**

After implementing Option A or B above, test the full flow.

---

## Implementation Order

### Phase 1: Fix and Test Individually ✅

1. ✅ Fix `text_split.json` (add model, parameters)
2. ✅ Test Stage 2 alone (text splitting)
3. ✅ Test Stage 4 alone (manual PART_A/PART_B)

### Phase 2: Implement Orchestration 🔧

**Choose implementation approach:**
- **Simple:** Option B (auto-parse JSON in PipelineExecutor)
- **Explicit:** Option A (new multi-stage route)

**Implement:**
1. Add context_override parameter to execute_pipeline()
2. Add JSON auto-parsing to _execute_pipeline_steps()
3. OR create new /execute_multi_stage route

### Phase 3: Test End-to-End ✅

1. Test full workflow via API
2. Verify ComfyUI receives correct PART_A and PART_B
3. Verify image generation works

### Phase 4: Frontend Integration (Future) 🔮

1. Add UI for multi-stage workflows
2. Show Stage 2 output before Stage 4 execution
3. Allow user to edit split parts before generating

---

## Open Questions

### Q1: How Should User Invoke This?

**Option A:** Single API call with both configs
```json
{
  "workflow": "vector_fusion",
  "stage2_config": "split_and_combine_setup",
  "stage4_config": "vector_fusion_linear_clip",
  "input_text": "..."
}
```

**Option B:** Two separate calls (user sees Stage 2 output first)
```
1. POST /api/schema/pipeline/execute (stage2_config)
   → Returns: {"part_a": "...", "part_b": "..."}
2. POST /api/schema/pipeline/execute (stage4_config) with custom_placeholders
   → Returns: image
```

**Option C:** Automatic (system detects JSON output and continues)
- User calls Stage 2
- System detects JSON output
- System auto-populates custom_placeholders
- System executes Stage 4 automatically

**Recommendation:** Start with Option B (explicit), add Option C later for convenience.

### Q2: Where Does JSON Parsing Happen?

**Option A:** In PipelineExecutor (automatic)
- Pro: Works for all pipelines automatically
- Con: May parse unintended outputs

**Option B:** In DevServer route (explicit)
- Pro: Full control over when to parse
- Con: Need to implement for each multi-stage workflow

**Recommendation:** Option A with metadata flag:
```json
{
  "pipeline_stage": "2",
  "meta": {
    "output_format": "json",  // Hint to auto-parse
    "auto_populate_placeholders": true
  }
}
```

---

## Success Criteria

- [ ] text_split.json loads without errors
- [ ] Stage 2 executes and outputs valid JSON
- [ ] JSON is parsed and added to custom_placeholders
- [ ] Stage 4 receives PART_A and PART_B placeholders
- [ ] ComfyUI generates image with dual CLIP encoding
- [ ] Full workflow completes end-to-end
- [ ] Documentation updated with working example

---

## Next Steps

1. Fix text_split.json
2. Implement JSON auto-parsing (Option B)
3. Add context_override parameter
4. Test Stage 2 alone
5. Test Stage 4 with manual context
6. Test full workflow end-to-end

---

**Ready to implement!**
