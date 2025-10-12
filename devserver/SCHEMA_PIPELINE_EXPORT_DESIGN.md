# Schema-Pipeline Export Design
## Strukturierte Forschungsdaten für Schema-basierte Workflows

### Problem
Legacy-Server exportiert nur ComfyUI-Output (Bilder/Audio). Schema-Pipelines haben jedoch:
- **Pipeline-Schritte** (z.B. Dadaismus-Transformation → Image-Generation)
- **Mehrere Backends** (Ollama für Text, ComfyUI für Bilder)
- **Zwischenergebnisse** (transformierter Text vor Bildgenerierung)
- **Metadata** (welche Chunks, welche Parameter)

### Verbessertes Export-Format

#### Verzeichnisstruktur
```
exports/html/session_DOE_J_250714202907_46cf69f1/
├── metadata.json              # Erweiterte Metadata
├── pipeline_data.json         # Pipeline-spezifische Daten
├── output_DOE_J_...html      # HTML-Export
├── media/                     # Media-Dateien
│   ├── step_1_ollama_output.txt
│   ├── step_2_comfyui_image_001.png
│   └── ...
└── steps/                     # Pipeline-Schritte (optional)
    ├── step_1_prompt_interception.json
    ├── step_2_comfyui_generation.json
    └── ...
```

#### Enhanced metadata.json
```json
{
  "version": "2.0",
  "export_type": "schema_pipeline",
  
  "session": {
    "user_id": "DOE_J",
    "session_id": "46cf69f1",
    "timestamp": "250714202907",
    "export_date": "2025-10-12T18:48:12Z"
  },
  
  "pipeline": {
    "schema_name": "TEST_dadaismus",
    "pipeline_type": "text_to_image",
    "chunks_used": [
      "prompt_interception",
      "comfyui_image_generation"
    ],
    "backends_used": ["ollama", "comfyui"],
    "total_steps": 2,
    "execution_time": 25.3
  },
  
  "input": {
    "user_prompt": "Ein Kamel fliegt über den Schwarzwald",
    "language": "de",
    "safety_level": "off"
  },
  
  "outputs": {
    "final_text": "Inspired by my friend's whimsical input...",
    "media_generated": [
      {
        "type": "image",
        "filename": "step_2_comfyui_image_001.png",
        "backend": "comfyui",
        "prompt_id": "46cf69f1-2624-477d-baf2-dc4c89043119",
        "parameters": {
          "model": "sd3.5_large",
          "steps": 25,
          "cfg": 5.5,
          "seed": 1234567
        }
      }
    ]
  },
  
  "research_tags": [
    "dadaismus",
    "text_transformation",
    "auto_image_generation",
    "sd3.5"
  ]
}
```

#### pipeline_data.json (detaillierte Schritte)
```json
{
  "pipeline_execution": {
    "schema": "TEST_dadaismus",
    "start_time": "2025-10-12T18:48:09Z",
    "end_time": "2025-10-12T18:48:34Z",
    "status": "completed",
    
    "steps": [
      {
        "step_number": 1,
        "chunk_type": "prompt_interception",
        "backend": "ollama",
        "start_time": "2025-10-12T18:48:09Z",
        "duration": 3.2,
        "input": {
          "prompt": "Ein Kamel fliegt über den Schwarzwald",
          "model": "mistral-nemo",
          "instruction": "Transform to Dadaismus style"
        },
        "output": {
          "text": "Inspired by my friend's whimsical input, 'A camel flies over the Black Forest,' I envision a piece that explodes the absurdity...",
          "tokens": 245
        },
        "metadata": {
          "model_name": "mistral-nemo:latest",
          "temperature": 0.7
        }
      },
      {
        "step_number": 2,
        "chunk_type": "comfyui_image_generation",
        "backend": "comfyui",
        "start_time": "2025-10-12T18:48:12Z",
        "duration": 22.1,
        "input": {
          "prompt": "Inspired by my friend's whimsical input...",
          "workflow_template": "sd35_standard"
        },
        "output": {
          "images": [
            {
              "filename": "step_2_comfyui_image_001.png",
              "width": 1024,
              "height": 1024,
              "format": "PNG"
            }
          ],
          "prompt_id": "46cf69f1-2624-477d-baf2-dc4c89043119"
        },
        "metadata": {
          "model": "sd3.5_large.safetensors",
          "steps": 25,
          "cfg_scale": 5.5,
          "sampler": "euler",
          "scheduler": "normal",
          "seed": 1234567
        }
      }
    ]
  }
}
```

### Vorteile für Forschung

1. **Vollständige Reproduzierbarkeit**
   - Alle Pipeline-Parameter dokumentiert
   - Zwischenschritte gespeichert
   - Backend-Versionen erfasst

2. **Strukturierte Analyse**
   - JSON-Format für programmatische Analyse
   - Klare Trennung: Input → Transformation → Output
   - Zeitstempel für Performance-Analyse

3. **Flexibel erweiterbar**
   - Neue Backends einfach integrierbar
   - Custom Research-Tags möglich
   - Verschiedene Pipeline-Typen unterstützt

4. **QDA-Software-kompatibel**
   - XML-Export mit Pipeline-Struktur
   - DOCX mit vollständiger Dokumentation
   - Medien eingebettet

### Implementation

#### Neue Methode in export_manager.py
```python
def auto_export_schema_pipeline(
    self,
    schema_name: str,
    pipeline_result: PipelineResult,
    user_input: str,
    media_prompt_id: str = None
) -> bool:
    """
    Export einer Schema-Pipeline Session
    
    Args:
        schema_name: Name des Schemas
        pipeline_result: PipelineResult Objekt
        user_input: Original User-Prompt
        media_prompt_id: ComfyUI Prompt-ID (falls auto-generiert)
    """
```

### Export-Trigger

Export wird getriggert:
1. **Auto-Export**: Nach Pipeline + Media-Completion
2. **Manual-Export**: Via Frontend-Button

### Nächste Schritte

1. ✅ Design dokumentieren
2. [ ] `auto_export_schema_pipeline()` implementieren
3. [ ] Pipeline-Result → Export-Data Mapping
4. [ ] ComfyUI-History mit Pipeline-Steps kombinieren
5. [ ] Enhanced HTML/PDF/XML/DOCX Templates
6. [ ] Test mit TEST_dadaismus Pipeline
