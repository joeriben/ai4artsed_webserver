# Execution History & Research Data Export - Design Document V2

**Date:** 2025-11-03
**Status:** 🔄 IN DESIGN - Architecture-First Approach
**Priority:** HIGH (fixes broken research data export)
**Architecture:** **Hybrid - Stateless Pipeline + Stateful Research Tracker**

**Previous Version:** V1 was abandoned due to implementation before understanding architecture

---

## ACTUAL Current Architecture (Verified from Code)

### How Stage 3-4 Loop Works TODAY

```python
# schema_pipeline_routes.py lines 222-330

# Step 1: Config specifies output_configs
config.media_preferences = {
    "output_configs": ["sd35_large", "gpt5_image"]  # Request 2 outputs
}

# Step 2: DevServer loops through configs
for i, output_config_name in enumerate(configs_to_execute):
    # Stage 3: Safety check for this config
    safety_result = execute_stage3_safety(...)

    if not safety_result['safe']:
        media_outputs.append({'status': 'blocked', ...})
        continue

    # Stage 4: Execute this ONE config → generates ONE output
    output_result = pipeline_executor.execute_pipeline(output_config_name, ...)

    media_outputs.append({
        'config': output_config_name,
        'output': output_result.final_output,  # ONE output per config
        'media_type': media_type
    })
```

### Key Facts

1. **No `count` parameter** - Each config produces exactly 1 output
2. **Multiple outputs** = Multiple configs in `output_configs` array
3. **Loop iteration** = One config execution
4. **Current limitation** = Can't request "3 images from sd35_large", must list it 3 times

---

## Data Model Design (Based on Actual Architecture)

### Core Principle

Track execution history matching the **actual 4-stage loop structure**:
- Stage 1: Runs ONCE (translation + safety)
- Stage 2: Runs ONCE (interception pipeline)
- **Stage 3-4 Loop**: Runs N times (once per output_config)

### ExecutionItem Structure

```python
@dataclass
class ExecutionItem:
    """Single logged item in execution history"""

    # Identity & Ordering
    sequence_number: int          # Global order across ALL items (1, 2, 3, ...)
    timestamp: datetime           # When this item was created

    # Pipeline Context
    stage: int                    # Which stage (1, 2, 3, 4)
    output_config_index: Optional[int] = None  # Which iteration of Stage 3-4 loop (1, 2, 3, ...)

    # Item Classification
    media_type: MediaType         # text, image, audio, music, video, 3d, metadata
    item_type: ItemType           # Semantic meaning (see taxonomy below)

    # Content
    content: Optional[str] = None          # Text content (prompts, translations)
    file_path: Optional[str] = None        # Path to media file

    # Technical Metadata
    config_used: Optional[str] = None      # Which config generated this
    model_used: Optional[str] = None       # Which model was used
    prompt_id: Optional[str] = None        # ComfyUI prompt ID

    # Flexible metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Key Design Decisions

1. **`output_config_index`** instead of `stage_step`
   - Reflects ACTUAL loop: iteration 1, 2, 3 of `output_configs` array
   - Maps directly to code: `for i, output_config_name in enumerate(configs_to_execute)`
   - Clear meaning: "This is the 2nd output config execution"

2. **No separate output_request logging**
   - Current architecture doesn't have `output_requests` objects
   - Configs directly specify output_configs array
   - No need for parent-child relationship tracking

3. **Future-proof but realistic**
   - If batch generation is added later, can use `metadata['batch_index']`
   - If output_requests are added, can add `output_request_index` field
   - Don't over-engineer for features that don't exist

---

## Item Type Taxonomy (Simplified)

### User Inputs (Stage 0)
- `USER_INPUT_TEXT` - Original text from user
- `USER_INPUT_IMAGE` - Original image from user

### Stage 1 (Translation + §86a Safety)
- `TRANSLATION_RESULT` - Translated text
- `STAGE1_SAFETY_CHECK` - Safety check result (metadata)
- `STAGE1_BLOCKED` - Content blocked (metadata with reason)

### Stage 2 (Interception)
- `INTERCEPTION_RESULT` - Transformed prompt from pipeline

### Stage 3 (Per Output Config)
- `STAGE3_SAFETY_CHECK` - Safety check for this output config
- `STAGE3_BLOCKED` - This output blocked

### Stage 4 (Per Output Config)
- `OUTPUT_IMAGE` - Generated image
- `OUTPUT_AUDIO` - Generated audio
- `OUTPUT_MUSIC` - Generated music
- `OUTPUT_VIDEO` - Generated video
- `OUTPUT_3D` - Generated 3D model

### System Events
- `PIPELINE_START` - Pipeline began
- `PIPELINE_COMPLETE` - Pipeline finished
- `PIPELINE_ERROR` - Pipeline failed

---

## Example Execution Flow

### Config: image_comparison.json
```json
{
  "pipeline": "text_transformation",
  "media_preferences": {
    "output_configs": ["sd35_large", "gpt5_image"]
  }
}
```

### Tracked Execution History
```python
ExecutionRecord{
  execution_id: "abc-123",
  config_name: "image_comparison",

  items: [
    # Stage 1
    {seq: 1, stage: 1, item_type: "user_input_text", content: "Eine Blume"},
    {seq: 2, stage: 1, item_type: "translation_result", content: "A flower"},
    {seq: 3, stage: 1, item_type: "stage1_safety_check", metadata: {safe: true}},

    # Stage 2
    {seq: 4, stage: 2, item_type: "interception_result", content: "BLUME! CHAOS!"},

    # Stage 3-4 Loop Iteration 1 (sd35_large)
    {seq: 5, stage: 3, output_config_index: 1, item_type: "stage3_safety_check",
     config_used: "sd35_large", metadata: {safe: true}},
    {seq: 6, stage: 4, output_config_index: 1, item_type: "output_image",
     config_used: "sd35_large", file_path: "/exports/img1.png", prompt_id: "xyz1"},

    # Stage 3-4 Loop Iteration 2 (gpt5_image)
    {seq: 7, stage: 3, output_config_index: 2, item_type: "stage3_safety_check",
     config_used: "gpt5_image", metadata: {safe: true}},
    {seq: 8, stage: 4, output_config_index: 2, item_type: "output_image",
     config_used: "gpt5_image", file_path: "https://...", metadata: {url: "..."}}
  ]
}
```

---

## Frontend Display Capabilities

### Student View (Simple)
```
Show only: OUTPUT_* items
Display: "Image 1", "Image 2"
```

### Advanced View
```
Show: INTERCEPTION_RESULT + OUTPUT_* items
Display:
  "Transformed: BLUME! CHAOS!"
  "Image 1 (SD3.5 Large)"
  "Image 2 (GPT-5)"
```

### Researcher View
```
Show: Everything
Display:
  Stage 1: Translation → Safety ✓
  Stage 2: Interception → "BLUME! CHAOS!"
  Stage 3-4 (1/2): sd35_large
    ├─ Safety ✓
    └─ Output → img1.png
  Stage 3-4 (2/2): gpt5_image
    ├─ Safety ✓
    └─ Output → https://...
```

---

## Implementation Plan

### Phase 1: Core Data Structures ✅ READY TO IMPLEMENT
1. Create `execution_record.py` with:
   - `ExecutionItem` dataclass
   - `ExecutionRecord` dataclass
   - Item type enums
   - JSON serialization

### Phase 2: Stateful Tracker
1. Create `execution_tracker.py` with:
   - Observer pattern
   - Async event queue (thread-safe)
   - LRU memory management
   - Session tracking

### Phase 3: Integration with schema_pipeline_routes.py
1. Add tracker initialization
2. Log items after each stage
3. Track output_config_index in loop
4. Handle errors gracefully

### Phase 4: Research API
1. GET /api/research/execution/<id>
2. GET /api/research/config/<name>/executions
3. Export to ZIP

---

## What's Different from V1?

| Aspect | V1 (Wrong) | V2 (Correct) |
|--------|-----------|--------------|
| **Understanding** | Assumed `output_requests` with `count` | Read actual code: `output_configs` array |
| **Field Name** | `stage_step` (ambiguous) | `output_config_index` (explicit) |
| **Complexity** | Over-engineered for non-existent features | Matches current architecture exactly |
| **Process** | Implementation → Understanding | Understanding → Design → Implementation |

---

## Success Criteria

✅ Tracks ALL items from Stage 1-4
✅ Correctly handles multiple output configs
✅ Distinguishes between loop iterations
✅ Frontend can flexibly display by view level
✅ Research can query: "How many outputs did config X generate?"
✅ Non-blocking (tracker failure doesn't break pipeline)
✅ Async-ready (event queue)

---

**Next Step:** Implement Phase 1 with this correct understanding.
