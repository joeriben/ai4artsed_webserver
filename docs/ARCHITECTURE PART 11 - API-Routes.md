# DevServer Architecture

**Part 11: API Routes**

---


### Primary Endpoint: `/api/workflow/execute`

**Purpose:** Execute a config-based pipeline

**Request:**
```json
{
  "schema_name": "dada",
  "prompt": "A surreal dream",
  "mode": "eco"  // or "fast"
}
```

**Response:**
```json
{
  "success": true,
  "schema_pipeline": true,
  "schema_name": "dada",
  "final_output": "Ein surrealistischer Traum in dadaistischer Ästhetik...",
  "steps_completed": 1,
  "execution_time": 2.35,
  "original_prompt": "A surreal dream",
  "translated_prompt": "Ein surrealistischer Traum...",
  "backend_info": [
    {
      "step": 1,
      "backend": "ollama",
      "model": "mistral-nemo:latest"
    }
  ]
}
```

**Pre-Translation Logic:**
```python
# Check for #notranslate# marker
if "#notranslate#" in original_prompt:
    translated_prompt = original_prompt.replace("#notranslate#", "")
elif should_translate:
    translated_prompt = await translator_service.translate(original_prompt, "de")
else:
    translated_prompt = original_prompt
```

**Media Generation:**
```python
# After text pipeline, check for media generation
if config.media_preferences.default_output == "image":
    prompt_id = await generate_image_from_text(
        text_prompt=final_output,
        schema_name=schema_name
    )
    response["media"] = {
        "type": "image",
        "prompt_id": prompt_id,
        "url": f"/api/media/image/{prompt_id}"
    }
```

---

### Supporting Endpoints

**Get Available Configs:**
```
GET /api/workflow/schemas
Response: ["dada", "bauhaus", "overdrive", ...]
```

**Get Config Info:**
```
GET /api/workflow/schema/<name>
Response: {name, description, category, display, ...}
```

**Get Media Status:**
```
GET /api/media/status/<prompt_id>
Response: {status: "completed", output_url: "..."}
```

---

