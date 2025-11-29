# Session: GPT-5 Image - OpenRouter to Direct OpenAI Refactor

**Date**: 2025-11-24
**Commit**: f683e6c
**Status**: ✅ Code Complete | ⏳ Testing Blocked (Missing API Key)

---

## Problem Discovery

GPT-5 Image (gpt-image-1) was failing to save images despite having base64 handling code. Investigation revealed the root cause:

### Incorrect Configuration
- **Wrong API**: Using OpenRouter Chat Completions instead of Direct OpenAI Images API
- **Wrong Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Wrong API Key**: `OPENROUTER_API_KEY` instead of `OPENAI_API_KEY`
- **Wrong Response Format**: Chat completion structure instead of Images API base64

### Failed Runs
- `59202bde-1ffc-4cef-860c-92703dfeafec` (13:00) - No image saved
- `4daf17c4-3f1c-4d6e-8153-97e5807b1a06` (13:03) - No image saved
- `778a6999-bc72-4dfd-bd29-03075b593e94` (13:02) - Incomplete run

---

## Solution: Complete API Refactor

### 1. Chunk Reconfiguration
**File**: `devserver/schemas/chunks/output_image_gpt5.json`

Rewrote to use Official OpenAI Images API per [OpenAI Documentation](https://platform.openai.com/docs/guides/image-generation):

```json
{
  "api_config": {
    "provider": "openai",
    "endpoint": "https://api.openai.com/v1/images/generations",
    "headers": {
      "Authorization": "Bearer {{OPENAI_API_KEY}}"
    },
    "request_body": {
      "model": "gpt-image-1",
      "prompt": "{{PROMPT}}",
      "response_format": "b64_json"
    }
  },
  "output_mapping": {
    "type": "images_api_base64",
    "extract_path": "data[0].b64_json"
  }
}
```

### 2. Backend Router Updates
**File**: `devserver/schemas/engine/backend_router.py`

**Added Dynamic API Key Loading** (lines 628-641):
```python
provider = api_config.get('provider', 'openrouter')
if provider == 'openai':
    key_file = 'openai_api.key'
else:
    key_file = 'openrouter_api.key'
```

**Added Images API Extraction Method** (lines 731-759):
```python
def _extract_image_from_images_api(self, data: Dict, output_mapping: Dict) -> Optional[str]:
    """Extract base64 from {data: [{b64_json: "..."}]} response"""
    if 'data' in data and len(data['data']) > 0:
        return data['data'][0]['b64_json']
```

**Added Output Mapping Type Routing** (lines 666-677):
```python
mapping_type = output_mapping.get('type', 'chat_completion_with_image')
if mapping_type == 'images_api_base64':
    image_data = self._extract_image_from_images_api(data, output_mapping)
else:
    image_data = self._extract_image_from_chat_completion(data, output_mapping)
```

### 3. Routes Pure Base64 Handler
**File**: `devserver/my_app/routes/schema_pipeline_routes.py`

**Added Detection for Pure Base64 Strings** (lines ~1529-1560):
```python
elif not output_value.startswith(('http://', 'https://', 'data:')) \
     and len(output_value) > 1000 \
     and output_value[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/':
    # OpenAI Images API returns pure base64 (no data: URI prefix)
    image_bytes = base64.b64decode(output_value)
    saved_filename = recorder.save_entity(...)
```

**Added Comprehensive Debug Logging**:
- Traces media storage routing decisions
- Logs which code path is matched (SwarmUI, workflow, HTTP, data URI, pure base64, ComfyUI)

---

## Architecture Impact

### Multi-Provider API Key System
The backend now supports multiple API providers with dynamic key loading:
- **OpenAI Direct**: Uses `openai_api.key` → Official OpenAI endpoints
- **OpenRouter**: Uses `openrouter_api.key` → OpenRouter proxy endpoints

### Flexible Response Parsing
New `output_mapping.type` field determines extraction strategy:
- `images_api_base64` → OpenAI Images API format (`data[0].b64_json`)
- `chat_completion_with_image` → Chat Completions format (`choices[0].message.content`)

### Dual Base64 Format Support
Routes now handle both:
- **Data URIs**: `data:image/png;base64,iVBORw0KGgo...` (DALL-E, Stable Diffusion)
- **Pure Base64**: `iVBORw0KGgo...` (GPT-5 Image via Images API)

---

## Testing Requirements

### 🚨 BLOCKER: Missing API Key File

The refactor is complete but **cannot be tested** without the OpenAI API key.

**Required File**: `/home/joerissen/ai/ai4artsed_webserver/devserver/openai_api.key`

**Format**: Plain text file with OpenAI API key (starts with `sk-proj-...`)

### Test Command
```bash
curl -X POST http://localhost:17802/api/schema/pipeline/stage4 \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "test-gpt5-direct",
    "prompt": "A minimalist geometric composition inspired by Bauhaus design principles",
    "output_config": "gpt5_image",
    "user_language": "en",
    "seed": 42
  }'
```

### Expected Output
- **Success Response**: `{"success": true, "run_id": "test-gpt5-direct", ...}`
- **Image Saved**: `exports/json/test-gpt5-direct/07_output_image.png`
- **File Size**: ~1-2 MB (1024x1024 PNG)
- **Metadata**: Provider = openai, source = images_api_base64

---

## Technical Details

### OpenAI Images API Response Format
```json
{
  "created": 1732454591,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ]
}
```

**Key Differences from Chat Completions**:
- Pure base64 string (no `data:image/png;base64,` prefix)
- Extracted from `data[0].b64_json` (not `choices[0].message.content`)
- Synchronous response (no streaming)

### GPT-5 Image Model Specs
- **Model ID**: `gpt-image-1`
- **Resolution**: 1024x1024 PNG
- **Cost**: ~$0.04 per image
- **Context**: 400k tokens (4k prompt max)
- **Response Time**: 5-15 seconds
- **Features**: Advanced reasoning, text rendering, high quality

---

## User Feedback & Insights

### Critical Realization
> "WHAT???? WIR VERWENDEN HIER OPENAI DIREKT"

This led to discovering the chunk was misconfigured to use OpenRouter instead of Direct OpenAI.

### API Key Clarification
> "und das sind ja acuh zwei völlig unterschiedlcihe APi-keys"

Confirmed OpenAI and OpenRouter require separate API keys (not interchangeable).

### Legacy Execution Mode
> "davon abgesehen hat fast/eco in devserver nichts mit Stage4 zu tun ... das war legacy"

Clarified that execution_mode (fast/eco) is deprecated and unrelated to Stage 4 media generation.

---

## Git Timeline

### Commits
1. **484b571** - `feat: Add optimization_applied flag for model-specific prompt optimization`
2. **168a26b** - `fix: Add base64 data URI handler for GPT-5 Image storage` (incomplete fix)
3. **f683e6c** - `fix: Refactor GPT-5 Image from OpenRouter to Direct OpenAI Images API` (this commit)

### Branch Status
- **Branch**: develop
- **Ahead of origin**: 3 commits (unpushed)
- **Working Tree**: Clean

---

## Next Steps

### 1. Create API Key File ⏳
```bash
# Option A: Create manually
echo "sk-proj-YOUR_KEY_HERE" > /home/joerissen/ai/ai4artsed_webserver/devserver/openai_api.key
chmod 600 /home/joerissen/ai/ai4artsed_webserver/devserver/openai_api.key

# Option B: Copy from existing source
cp ~/path/to/openai_key.txt /home/joerissen/ai/ai4artsed_webserver/devserver/openai_api.key
```

### 2. Restart Backend 🔄
```bash
cd /home/joerissen/ai/ai4artsed_webserver
./1_stop_all.sh
./3_start_backend_dev.sh &
```

### 3. Run End-to-End Test ✅
```bash
# Test Stage 4 directly
curl -X POST http://localhost:17802/api/schema/pipeline/stage4 \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "test-gpt5",
    "prompt": "A Dada-style photomontage",
    "output_config": "gpt5_image",
    "user_language": "en"
  }'

# Verify image saved
ls -lh exports/json/test-gpt5/07_output_image.png
file exports/json/test-gpt5/07_output_image.png
```

### 4. Frontend Integration Test 🎨
- Open Youth Flow UI
- Select Dada + GPT-5 Image
- Submit prompt
- Verify image displays and downloads correctly

### 5. Push to Remote 🚀
```bash
git push origin develop
```

---

## Success Criteria

- ✅ Code refactored to use Direct OpenAI Images API
- ✅ Dynamic API key loading implemented
- ✅ Pure base64 extraction added
- ✅ Comprehensive debug logging added
- ✅ Changes committed with detailed message
- ⏳ API key file created
- ⏳ End-to-end test passed
- ⏳ Image saved to exports folder
- ⏳ Frontend displays image correctly

---

## Known Issues & Limitations

### Python Bytecode Cache
During debugging, Python's `__pycache__` directories prevented code changes from taking effect even after backend restarts. Cleared manually before testing.

### Execution Mode Confusion
Initial investigation incorrectly focused on execution_mode (fast/eco). These are deprecated legacy features unrelated to Stage 4.

### Multiple Backend Processes
System showed many background backend processes running. Should be monitored to avoid conflicts.

---

## Files Modified

1. `devserver/schemas/chunks/output_image_gpt5.json` - Complete rewrite
2. `devserver/schemas/engine/backend_router.py` - +77 lines (dynamic keys, Images API extraction)
3. `devserver/my_app/routes/schema_pipeline_routes.py` - +35 lines (pure base64 handler, debug logging)

**Total Changes**: 3 files, +135 insertions, -58 deletions

---

## References

- [OpenAI Images API Documentation](https://platform.openai.com/docs/guides/image-generation)
- [GPT-5 Image Model Card](https://platform.openai.com/docs/guides/image-generation?image-generation-model=gpt-image-1)
- OpenAI Python SDK: `client.images.generate(model="gpt-image-1", response_format="b64_json")`
