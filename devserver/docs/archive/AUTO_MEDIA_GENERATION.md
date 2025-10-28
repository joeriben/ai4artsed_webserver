# Auto-Media-Generation System

## Overview

The Auto-Media-Generation system automatically generates media (images, audio, video) after text-only schema pipelines complete. This eliminates the need for separate pipeline definitions for text transformation and media generation.

## Architecture

### Flow Diagram

```
User Input
    ↓
Schema Pipeline (Text-only, e.g., TEST_dadaismus)
    ↓
Text Transformation (Dadaismus, Translation, etc.)
    ↓
Pipeline Completion ✓
    ↓
[AUTO-POST-PROCESSING]
    ├─ Check: ComfyUI already triggered? → Yes: Return media
    └─ No ↓
         ├─ Detect Output Type (tags, meta, default: image)
         └─ Output Type = Image? → Yes ↓
              ├─ Generate ComfyUI Workflow
              ├─ Submit to ComfyUI
              └─ Return media response with prompt_id
```

## Implementation

### 1. Helper Functions (`workflow_routes.py`)

#### `detect_output_type(final_output: str, schema_info: dict) -> str`

Detects the desired media output type with the following priority:

1. **Explicit tags** in output text:
   - `#image#` → image
   - `#music#` → music
   - `#audio#` → audio
   - `#video#` → video

2. **Schema meta** `output_type` field

3. **Default**: `image` (for text-only pipelines)

#### `generate_image_from_text(text_prompt: str, schema_name: str = None) -> Optional[str]`

Generates an image from text using ComfyUI:

1. Loads the `sd35_standard` workflow template
2. Generates ComfyUI workflow with text as prompt
3. Submits to ComfyUI
4. Returns `prompt_id` for tracking

### 2. Post-Processing Logic (`workflow_routes.py:execute_workflow()`)

After a schema pipeline completes:

```python
if result.status.value == 'completed':
    # Check if ComfyUI was already triggered in pipeline
    prompt_id = None
    for step in result.steps:
        if step.metadata and 'prompt_id' in step.metadata:
            prompt_id = step.metadata['prompt_id']
            break
    
    # AUTO-POST-PROCESSING: Auto-Media-Generation
    if not prompt_id:
        schema_info = executor.get_schema_info(schema_name)
        detected_output_type = detect_output_type(final_output, schema_info)
        
        if detected_output_type == "image":
            # Remove media tags from prompt
            clean_output = final_output.replace("#image#", "").strip()
            
            # Generate image asynchronously
            prompt_id = asyncio.run(generate_image_from_text(
                text_prompt=clean_output,
                schema_name=schema_name
            ))
```

### 3. Frontend Integration

The frontend already supports media output via the Media Output System:

```javascript
// In workflow-streaming.js
if (data.media) {
    // Display image/audio/video automatically
    mediaOutputManager.displayImage(data.media.prompt_id);
}
```

## Usage Examples

### Example 1: Text-only Pipeline with Auto-Image

**Pipeline**: `dev/TEST_dadaismus`

```
User: "Ein Kamel fliegt über den Schwarzwald"
  ↓
Pipeline: Dadaismus transformation
  ↓
Output: "Inspired by my friend's whimsical input, 'A camel flies...'
  ↓
Server: No output type specified → Default: Image
  ↓
Server: Generate ComfyUI workflow with Dadaismus output
  ↓
ComfyUI: Generate image (prompt_id: d54f287c-27a7-4cc4-ba01-5a983ea8a833)
  ↓
Frontend: Display image via Media Output System
```

### Example 2: Explicit Output Type via Tag

**Pipeline**: Custom text pipeline

```yaml
chunks:
  - prompt_interception:
      prompt: "Transform to haiku #image#"
```

The `#image#` tag explicitly requests image generation.

### Example 3: Meta-defined Output Type

**Schema**: `schema_data/my_pipeline.yaml`

```yaml
meta:
  output_type: "image"  # Always generate images
```

## Configuration

### ComfyUI Workflow Template

The system uses the `sd35_standard` template from `comfyui_workflow_generator.py`:

- **Model**: Stable Diffusion 3.5 Large
- **Resolution**: 1024x1024 (default)
- **Steps**: 25
- **CFG**: 5.5
- **Sampler**: euler
- **Scheduler**: normal

### Default Parameters

```python
{
    "WIDTH": 1024,
    "HEIGHT": 1024,
    "STEPS": 25,
    "CFG": 5.5,
    "SAMPLER": "euler",
    "SCHEDULER": "normal",
    "CHECKPOINT": "sd3.5_large.safetensors"
}
```

## Testing

Run the test suite:

```bash
cd devserver
python TEST_auto_media_generation.py
```

**Expected Output**:
1. ✓ Pipeline executes successfully
2. ✓ Output type detected as "image"
3. ✓ Image generation queued
4. ✓ Image generated and saved

## API Response Format

### With Auto-Generated Media

```json
{
    "success": true,
    "schema_pipeline": true,
    "schema_name": "TEST_dadaismus",
    "final_output": "Dadaismus-transformed text...",
    "steps_completed": 2,
    "execution_time": 4.63,
    "original_prompt": "Ein Kamel fliegt über den Schwarzwald",
    "translated_prompt": "Dadaismus-transformed text...",
    "status_updates": [
        "Schema-Pipeline 'TEST_dadaismus' erfolgreich ausgeführt",
        "Bild wird automatisch generiert..."
    ],
    "media": {
        "type": "image",
        "prompt_id": "d54f287c-27a7-4cc4-ba01-5a983ea8a833",
        "url": "/api/media/image/d54f287c-27a7-4cc4-ba01-5a983ea8a833"
    }
}
```

## Future Enhancements

### Planned Features

1. **Audio Generation**: Support for `#music#` and `#audio#` tags
2. **Video Generation**: Support for `#video#` tag
3. **Custom Parameters**: Allow schemas to specify generation parameters
4. **Multi-Media**: Generate multiple media types from single pipeline

### Schema Configuration Example

```yaml
meta:
  output_type: "image"
  image_params:
    width: 1920
    height: 1080
    steps: 30
    cfg: 7.0
```

## Troubleshooting

### Issue: No image generated

**Check**:
1. ComfyUI is running (port 8188 or 7821)
2. SD 3.5 model is installed
3. Server logs for `[AUTO-MEDIA]` messages

### Issue: Wrong output type

**Solution**:
- Add explicit tag: `#image#`, `#music#`, etc.
- Or set `output_type` in schema meta

### Issue: Poor image quality

**Solution**:
- Ensure pipeline output is descriptive
- The text output becomes the image prompt
- More detailed text = better images

## Technical Details

### Dependencies

- `schemas/engine/comfyui_workflow_generator.py` - Workflow generation
- `my_app/services/comfyui_client.py` - ComfyUI communication
- `my_app/routes/media_routes.py` - Media serving
- `public_dev/js/media-output.js` - Frontend display

### Performance

- Pipeline execution: ~4-5s
- Image generation: ~20-30s (SD 3.5)
- Total time: ~25-35s

### Logging

All auto-media operations are logged with `[AUTO-MEDIA]` prefix:

```
[AUTO-MEDIA] No media generated by pipeline 'TEST_dadaismus'
[AUTO-MEDIA] Detected output type: image
[AUTO-MEDIA] Triggering auto-image-generation for text-only pipeline
[AUTO-MEDIA] Image generation queued: d54f287c-27a7-4cc4-ba01-5a983ea8a833
```

## Credits

- Schema-Pipeline Architecture: AI4ArtsEd Team
- ComfyUI Integration: Stable Diffusion 3.5
- Auto-Generation System: v1.0 (December 2025)
