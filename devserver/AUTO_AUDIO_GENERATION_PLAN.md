# Auto-Audio-Generation mit Stable Audio
**Analog zu Auto-Image-Generation**

## Ziel
Text-Pipelines mit `#audio#` Tag sollen automatisch Audio mit Stable Audio generieren.

## Implementation Plan

### 1. Stable Audio API Client
**Datei**: `devserver/my_app/services/stable_audio_client.py`
- API-Key Management
- Audio-Generierung Request
- Status-Polling
- Audio-Download

### 2. Audio-Workflow-Generator
**Datei**: `devserver/schemas/engine/audio_workflow_generator.py`
- Stable Audio Parameter
- Workflow-Template für Audio

### 3. Backend-Integration
**Datei**: `devserver/my_app/routes/workflow_routes.py`
- `generate_audio_from_text()` Funktion (analog zu `generate_image_from_text()`)
- Detection für `#audio#` Tag (bereits in `detect_output_type()`)
- Post-Processing für Audio

### 4. Frontend-Integration
**Dateien**: 
- `devserver/public_dev/js/media-output.js` (bereits vorhanden)
- `devserver/public_dev/js/workflow-streaming.js` (Polling)

## Stable Audio API Details

**Endpoint**: `https://api.stability.ai/v2beta/stable-audio/generate/audio`

**Request**:
```json
{
  "text_description": "Ambient forest sounds with birds chirping",
  "duration_seconds": 10,
  "cfg_scale": 7.0,
  "seed": 0
}
```

**Response**:
```json
{
  "id": "generation_id",
  "status": "processing" | "completed" | "failed"
}
```

**Polling**: `GET /v2beta/stable-audio/generate/{id}`

**Download**: Audio als base64 oder URL

## Tag-Strategie

- `#audio#` → Stable Audio (Sound Effects, Ambient)
- `#music#` → AceStep (später, braucht Lyrics)

## Next Steps

1. [ ] Stable Audio API Client erstellen
2. [ ] Audio-Workflow-Generator
3. [ ] Backend-Integration
4. [ ] Frontend-Testing
5. [ ] Dokumentation
