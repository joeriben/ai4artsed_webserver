# Plan: GPT-5 Image via OpenRouter Integration

**Datum:** 2025-10-27
**Ziel:** Bildgenerierung via OpenRouter GPT-5 Image (große Modellversion) als "fast" Mode Alternative

---

## 0. Architektur-Klärung: Chunks vs Configs

### Chunks = Primitives (atomar)
- **Output-Chunks** enthalten komplettes Workflow/API-Setup mit **Default-Werten**
- Beispiel: `output_image_sd35_large.json` - Euler Sampler, 25 steps, CFG 5.5
- Beispiel: `output_image_gpt5_large.json` - 1024x1024, quality="standard"

### Configs = Anwendungsfälle (kombiniert Chunks + Parameter-Overrides)
- **Output-Configs** verweisen auf Output-Chunks und überschreiben Parameter
- Beispiel: `sd35_large.json` - Standard (nutzt Chunk-Defaults)
- Beispiel: `sd35_large_highquality.json` - 50 steps, CFG 7.0 (Override)
- Beispiel: `gpt5_image_large_highquality.json` - 1792x1024, quality="hd" (Override)

### Naming Convention für Output-Configs:

```
{model}.json                  // Standard (nutzt Chunk-Defaults)
{model}_highquality.json      // Hohe Qualität (mehr steps/bessere settings)
{model}_draft.json            // Schneller Entwurf (wenige steps)
{model}_lowcfg.json           // Niedriger CFG (experimenteller)
```

**Wichtig:** Model-Name im Config-Namen sichtbar machen, damit klar ist welches Model verwendet wird!

---

## 1. Architektur-Übersicht

### Unterschied zu ComfyUI (eco mode)
| Aspekt | ComfyUI (eco) | OpenRouter GPT-5 (fast) |
|--------|---------------|-------------------------|
| Backend | Local ComfyUI Server | Cloud API (OpenRouter) |
| Workflow | ComfyUI API JSON (11 nodes) | Einfacher API Call |
| Output-Chunk Type | `output_chunk` mit `workflow` | `api_output_chunk` mit `api_config` |
| Kosten | Nur GPU-Strom | Pro API Call |
| Geschwindigkeit | 20-60 Sek (je nach GPU) | ~5-15 Sek (Cloud) |

### Output-Chunk Architektur für API-basierte Generierung

**Problem:** Output-Chunks wurden für ComfyUI Workflows designed (embedded workflow JSON)

**Lösung:** Neuer Output-Chunk Subtyp für API-basierte Backends

**WICHTIG:** GPT-5 Image nutzt Chat Completion API, nicht Image Generation API!

```json
{
  "name": "output_image_gpt5",
  "type": "api_output_chunk",
  "backend_type": "openrouter",
  "media_type": "image",
  "description": "GPT-5 Image - Multimodal chat model with image generation via OpenRouter",

  "api_config": {
    "provider": "openrouter",
    "model": "openai/gpt-5-image",
    "endpoint": "https://openrouter.ai/api/v1/chat/completions",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{OPENROUTER_API_KEY}}",
      "Content-Type": "application/json",
      "HTTP-Referer": "https://ai4artsed.com",
      "X-Title": "AI4ArtsEd DevServer"
    },
    "request_body": {
      "model": "openai/gpt-5-image",
      "messages": [
        {
          "role": "system",
          "content": "You are an AI assistant that generates images. When asked to create an image, generate it directly without additional commentary."
        },
        {
          "role": "user",
          "content": "{{PROMPT}}"
        }
      ],
      "temperature": 0.7,
      "max_tokens": 4096
    }
  },

  "input_mappings": {
    "prompt": {
      "field": "request_body.messages[1].content",
      "source": "{{PREVIOUS_OUTPUT}}",
      "description": "Image generation prompt (as chat message)"
    },
    "temperature": {
      "field": "request_body.temperature",
      "default": 0.7,
      "allowed_values": [0.0, 2.0],
      "description": "Sampling temperature"
    },
    "max_tokens": {
      "field": "request_body.max_tokens",
      "default": 4096,
      "description": "Maximum completion tokens"
    }
  },

  "output_mapping": {
    "type": "chat_completion_with_image",
    "format": "multimodal",
    "extract_path": "choices[0].message.content",
    "extract_logic": "Find first content item with type='image_url', extract image_url.url",
    "description": "Extract image URL from multimodal chat completion response"
  },

  "meta": {
    "estimated_duration_seconds": "5-15",
    "requires_gpu": false,
    "api_provider": "openrouter",
    "model_id": "openai/gpt-5-image",
    "provider_model_id": "gpt-5-2025-08-07",
    "cost_per_image": "$0.00004 (output images at $0.04/K)",
    "context_length": 400000,
    "max_prompt_tokens": 272000,
    "max_completion_tokens": 128000,
    "modalities": {
      "input": ["image", "text", "file"],
      "output": ["image", "text"]
    },
    "features": [
      "Mandatory reasoning mode",
      "Advanced text rendering in images",
      "Detailed image editing",
      "Improved instruction following"
    ],
    "notes": "GPT-5 Image via OpenRouter. Chat completion model with image generation. Requires openrouter_api.key file in devserver root."
  }
}
```

---

## 2. Backend Router Erweiterung

### Neue Methode: `_process_api_output_chunk()`

```python
async def _process_api_output_chunk(self, chunk_name: str, prompt: str, parameters: Dict[str, Any]) -> BackendResponse:
    """Process API-based Output-Chunk (OpenRouter, Replicate, etc.)"""

    # 1. Load API Output-Chunk
    chunk = self._load_output_chunk(chunk_name)
    if chunk.get('type') != 'api_output_chunk':
        return BackendResponse(success=False, error=f"Not an API Output-Chunk")

    # 2. Build API request with deep copy to avoid mutation
    import copy
    api_config = chunk['api_config']
    request_body = copy.deepcopy(api_config['request_body'])

    # Apply input mappings
    for param_name, mapping in chunk['input_mappings'].items():
        field_path = mapping['field']
        value = parameters.get(param_name, prompt if param_name == 'prompt' else mapping.get('default'))

        # Set nested value (e.g., "request_body.messages[1].content")
        self._set_nested_value(request_body, field_path.replace('request_body.', ''), value)

    # 3. Get API key from environment
    import os
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return BackendResponse(success=False, error="OPENROUTER_API_KEY not set")

    # 4. Build headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai4artsed.com",
        "X-Title": "AI4ArtsEd DevServer"
    }

    # 5. Make API call
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(
            api_config['endpoint'],
            json=request_body,
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()

                # Extract image URL from multimodal chat completion response
                # For GPT-5 Image: choices[0].message.content is a list with type="image_url"
                image_url = self._extract_image_from_chat_completion(data, chunk['output_mapping'])

                if not image_url:
                    return BackendResponse(success=False, error="No image found in response")

                return BackendResponse(
                    success=True,
                    content=image_url,
                    metadata={
                        'chunk_name': chunk_name,
                        'media_type': chunk['media_type'],
                        'provider': api_config['provider'],
                        'model': api_config['model'],
                        'image_url': image_url
                    }
                )
            else:
                error = await response.text()
                logger.error(f"API error: {error}")
                return BackendResponse(success=False, error=f"API error: {response.status}")

def _extract_image_from_chat_completion(self, data: Dict, output_mapping: Dict) -> Optional[str]:
    """Extract image URL from chat completion response with multimodal content"""
    try:
        content = data['choices'][0]['message']['content']

        # Content can be string or list of content items
        if isinstance(content, list):
            for item in content:
                if item.get('type') == 'image_url':
                    return item['image_url']['url']

        return None
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Failed to extract image from response: {e}")
        return None

def _set_nested_value(self, obj: Any, path: str, value: Any):
    """Set nested value in dict or list using path notation (e.g., 'messages[1].content')"""
    import re
    parts = re.split(r'\.|\[|\]', path)
    parts = [p for p in parts if p]  # Remove empty strings

    current = obj
    for i, part in enumerate(parts[:-1]):
        if part.isdigit():
            current = current[int(part)]
        else:
            current = current[part]

    final_key = parts[-1]
    if final_key.isdigit():
        current[int(final_key)] = value
    else:
        current[final_key] = value
```

### Backend Router Routing-Logik Update

```python
async def _process_comfyui_request(self, comfyui_service, request: BackendRequest) -> BackendResponse:
    """ComfyUI-Request verarbeiten mit Output-Chunks oder Legacy-Workflow-Generator"""

    output_chunk_name = request.parameters.get('output_chunk')

    if output_chunk_name:
        # Load chunk to check type
        chunk = self._load_output_chunk(output_chunk_name)

        if chunk.get('type') == 'api_output_chunk':
            # Route to API backend
            return await self._process_api_output_chunk(output_chunk_name, schema_output, request.parameters)
        else:
            # Route to ComfyUI backend
            return await self._process_output_chunk(output_chunk_name, schema_output, request.parameters)
```

---

## 3. Configs: Standard + Varianten

### 3.1 gpt5_image.json (Standard)

```json
{
  "pipeline": "single_prompt_generation",
  "name": {
    "en": "GPT-5 Image",
    "de": "GPT-5 Image"
  },
  "description": {
    "en": "Cloud-based image generation using GPT-5 Image via OpenRouter (multimodal chat model)",
    "de": "Cloud-basierte Bildgenerierung mit GPT-5 Image via OpenRouter (multimodales Chat-Modell)"
  },
  "category": {
    "en": "Image Generation (Cloud)",
    "de": "Bildgenerierung (Cloud)"
  },
  "context": "Transform the input text into an optimized image generation prompt. Focus on visual details, composition, lighting, and artistic style. The model will generate an image directly.",

  "parameters": {
    "OUTPUT_CHUNK": "output_image_gpt5",
    "temperature": 0.7,
    "max_tokens": 4096
  },

  "media_preferences": {
    "default_output": "image",
    "supported_types": ["image", "text"]
  },

  "meta": {
    "model": "gpt-5-image",
    "model_id": "openai/gpt-5-image",
    "provider_model_id": "gpt-5-2025-08-07",
    "backend": "openrouter",
    "backend_type": "openrouter",
    "requires_gpu": false,
    "requires_api_key": "OPENROUTER_API_KEY",
    "estimated_duration_seconds": "5-15",
    "cost_model": "api_call",
    "cost_per_image": "$0.00004",
    "context_length": 400000,
    "modalities": ["image", "text"],
    "features": ["reasoning", "text_rendering", "image_editing"],
    "notes": "GPT-5 Image via OpenRouter. Multimodal chat model with advanced image generation. Requires API key.",
    "version": "1.0"
  },

  "display": {
    "icon": "☁️",
    "color": "#4A90E2",
    "category": "image_generation_cloud",
    "difficulty": 1,
    "order": 20
  },

  "tags": {
    "en": ["image", "gpt-5", "cloud", "fast", "openrouter", "multimodal", "reasoning"],
    "de": ["bild", "gpt-5", "cloud", "schnell", "openrouter", "multimodal", "reasoning"]
  },

  "audience": {
    "workshop_suitable": true,
    "min_age": 10,
    "complexity": "beginner"
  }
}
```

### 3.2 Varianten: Nicht nötig für GPT-5 Image

**Wichtig:** Im Gegensatz zu SD3.5 Large hat GPT-5 Image keine vergleichbaren Qualitätsparameter (steps, CFG, etc.).

Die Bildqualität wird durch:
- Den Prompt selbst (instruiere höhere Detailtiefe)
- Temperature (kreativitätskontrolle)
- Max_tokens (Antwortlänge)

**Daher:** Erstmal nur `gpt5_image.json` als Standard-Config. Varianten können später bei Bedarf hinzugefügt werden.

---

## 4. output_config_defaults.json Update

```json
{
  "image": {
    "eco": "sd35_large",
    "fast": "gpt5_image",
    "_note": "eco=local ComfyUI, fast=cloud OpenRouter GPT-5"
  }
}
```

**Naming Schema:**
- Standard defaults: `{mode}` (z.B. "eco", "fast")
- Varianten (future): `{mode}_{variant}` (z.B. "eco_highquality")

**Hinweis:** Varianten für GPT-5 Image später, wenn Bedarf besteht.

---

## 5. Implementierungs-Schritte

### Phase 1: Backend Router API Support ✅
1. Add `_process_api_output_chunk()` method
2. Add `_apply_input_mappings_to_dict()` helper
3. Add `_extract_from_path()` helper (for nested JSON extraction)
4. Update routing logic to detect `api_output_chunk` type
5. Add aiohttp dependency if needed

### Phase 2: Output-Chunk Creation ✅
1. Create `output_image_gpt5_large.json`
2. Define `api_config` structure
3. Define `input_mappings` for prompt, size, quality
4. Define `output_mapping` for URL extraction

### Phase 3: Config Creation ✅
1. Create `gpt5_image_large.json` config
2. Set OUTPUT_CHUNK to output_image_gpt5_large
3. Add explicit parameters (size, quality)
4. Add meta info (requires_api_key, cost_model)

### Phase 4: Defaults Update ✅
1. Update `output_config_defaults.json`
2. Set `image.fast = "gpt5_image_large"`

### Phase 5: Testing ✅
1. Test API Output-Chunk loading
2. Test OpenRouter API call with dummy data
3. Test full chain: dada → gpt5_image_large (fast mode)
4. Test error handling (no API key, API errors)

---

## 6. Vorteile GPT-5 Image (fast) vs SD3.5 Large (eco)

### GPT-5 Image Large (fast)
✅ Schneller (5-15 Sek vs 20-60 Sek)
✅ Keine lokale GPU nötig
✅ Konsistente Performance
✅ Einfacher zu deployen (nur API key)
✅ Automatische Updates (OpenAI side)
❌ Kosten pro Bild
❌ Internetverbindung erforderlich
❌ Weniger Kontrolle über Generation

### SD3.5 Large (eco)
✅ Kostenlos (nur Strom)
✅ Volle Kontrolle (Sampler, Scheduler, Seeds)
✅ Funktioniert offline
✅ Custom Models möglich
❌ Langsamer
❌ Benötigt 8GB+ VRAM
❌ Setup-Aufwand (ComfyUI + Models)

---

## 7. Erweiterbarkeit

Diese Architektur ermöglicht einfache Integration weiterer API-basierter Services:

- **Replicate** (Flux, SDXL, etc.)
- **Stability AI API** (Stable Diffusion)
- **Midjourney** (wenn API verfügbar)
- **DALL-E 3** via OpenRouter
- **Firefly** (Adobe)

Jeder Service benötigt nur:
1. Ein `api_output_chunk` JSON
2. Ein Config JSON
3. Eintrag in `output_config_defaults.json`

Kein neuer Backend-Code nötig! ✨

---

## 8. GPT-5 Image Spezifikationen (OpenRouter)

**Genaue Daten von https://openrouter.ai/openai/gpt-5-image:**

### Model Details
- **Model ID:** `openai/gpt-5-image`
- **Provider Model ID:** `gpt-5-2025-08-07`
- **Type:** Multimodal chat model (NOT pure image generation API!)
- **API Endpoint:** `/api/v1/chat/completions` (Chat endpoint, not /images/generations!)

### Modalitäten
- **Input:** image, text, file
- **Output:** image, text (combined in chat format)

### Context & Tokens
- **Context Length:** 400,000 tokens
- **Max Prompt Tokens:** 272,000
- **Max Completion Tokens:** 128,000

### Pricing (per million tokens/images)
- Input tokens: $10/M
- Output tokens: $10/M
- **Input images:** $0.01/K ($0.00001 per image)
- **Output images:** $0.04/K (~$0.00004 per image)
- Web search: $10/K
- Input cache read: $0.00125/M

### Supported Parameters
- Reasoning (mandatory in some modes)
- Structured outputs
- Response format
- Seed, max_tokens, temperature, top_p
- Stop sequences, frequency/presence penalties
- Logit bias, logprobs
- Tools, tool choice

### Wichtiger Unterschied!
GPT-5 Image ist KEIN `/images/generations` API wie DALL-E 3.
Es ist ein **Chat Completion Model** das Bilder **generieren kann** als Teil der Chat-Response.

**Request Format:**
```json
POST /api/v1/chat/completions
{
  "model": "openai/gpt-5-image",
  "messages": [
    {
      "role": "user",
      "content": "Generate an image of a sunset over mountains"
    }
  ]
}
```

**Response Format:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": [
          {
            "type": "image_url",
            "image_url": {
              "url": "https://..."
            }
          },
          {
            "type": "text",
            "text": "I've generated an image of..."
          }
        ]
      }
    }
  ]
}
```

---

## 9. Geschätzte Implementierungszeit

- **Backend Router API Support:** 2-3 Stunden
- **Output-Chunk + Config Creation:** 1 Stunde
- **Testing + Debugging:** 1-2 Stunden
- **Documentation:** 30 Minuten

**Total:** ~5-7 Stunden

---

**Status:** Plan dokumentiert, bereit für Implementierung morgen nach dada → sd35_large Test.
