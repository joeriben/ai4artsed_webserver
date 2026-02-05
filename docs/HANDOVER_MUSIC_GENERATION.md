# Handover: Music Generation (HeartMuLa) Pipeline

**Date:** 2026-02-05
**Status:** Generation WORKS, Audio playback im Frontend noch 404

---

## Was funktioniert

### Pipeline End-to-End
- **HeartMuLa generiert MP3s** - bestätigt durch Export-Ordner
- **TEXT_1 (Lyrics) + TEXT_2 (Tags)** werden korrekt an HeartMuLa übergeben
- **device_id** konsistent (kein `dev_*` Prefix mehr)
- **Dual Interception** (lyrics_refinement + tags_generation) streamt korrekt
- **Phase 4 Seed** wird für Python-Chunks übersprungen (random statt 123456789)
- **Wikipedia** per `skip_wikipedia` Flag deaktivierbar (für music_generation.vue aktiv)
- **Audio-Länge Slider** im Frontend (30s - 4min, default 2min)

### Commits dieser Session
1. `b94bc4a` - TEXT_2 Bug fix (chunk_builder.py: `context.get('text2')` → `context['user_input']`)
2. `967be0e` - device_id für main generation request
3. `86c4652` - device_id für dual interception requests
4. `ee6ed36` - custom_placeholders Extraction im Backend
5. `78d4a4f` - custom_placeholders Injection in Python chunk parameters

### Weitere Änderungen (committed via andere Session)
- `pipeline_executor.py`: `_SKIP_WIKIPEDIA` Flag + Seed-Skip für Python chunks
- `schema_pipeline_routes.py`: `skip_wikipedia` Extraktion in GET handler + context_override
- `output_music_heartmula.py`: max_audio_length_ms=240000

---

## Offene Bugs

### 1. KRITISCH: `/api/media/music/<run_id>` gibt 404

**Symptom:** Audio Player erscheint, aber Datei kann nicht geladen werden.

**Ursache:** Entity-Typ Mismatch.
- Recorder speichert alle Medien als Typ `"output_image"` (Legacy-Name)
- `/api/media/music/` Endpoint sucht nach Typ `"music"` oder `"audio"`
- MP3-Datei existiert im Export-Ordner, wird aber nicht gefunden

**Fix (uncommitted in media_routes.py):**
```python
# Fallback: output_image entities mit Audio-Endung
for entity in recorder.metadata.get('entities', []):
    if entity.get('type') == 'output_image' and entity.get('filename', '').endswith(('.mp3', '.wav', '.ogg', '.flac')):
        music_entity = entity
        break
```

**Langfristiger Fix:** Entity-Typ korrekt als `"music"` speichern statt `"output_image"`.
Ort: `schema_pipeline_routes.py` Zeile ~4189 wo `output_image` Entity erstellt wird.

### 2. Wiki-Marker in LLM-Output

**Symptom:** Refined Lyrics enthalten `<wiki lang="en">Doo-wop</wiki>` Marker als Text.

**Ursache:** `skip_wikipedia` verhindert die Wikipedia-Lookups, aber die `manipulate.json` Chunk-Vorlage instruiert das LLM trotzdem, `<wiki>` Marker zu generieren. Die Marker werden ohne Lookup nicht aufgelöst und landen als Rohtext im Output.

**Fix-Optionen:**
- A) Eigene Chunks für lyrics_refinement/tags_generation ohne Wikipedia-Instruktion
- B) Marker aus Output strippen wenn `_SKIP_WIKIPEDIA` aktiv
- C) Separate Chunk-Vorlage ohne Wikipedia-Block

### 3. safety_level Default: `kids` statt User-Setting

**Symptom:** Alle Requests gehen mit `safety_level: kids`, obwohl Backend-Default `youth` ist.

**Ursache:** `pipelineExecution.ts:43` hat `safetyLevel = ref('kids')` hardcoded.
Der Store lädt den Wert nicht aus den User-Settings.

---

## Architektur-Notizen

### Dual Interception Flow
```
Frontend (music_generation.vue)
  ├── SSE Stream 1: lyrics_refinement (input: user lyrics)
  ├── SSE Stream 2: tags_generation (input: user tags)
  └── POST: /api/schema/pipeline/interception
        ├── schema: heartmula (skip_stage2=true)
        ├── custom_placeholders: { TEXT_1, TEXT_2, max_audio_length_ms }
        └── Pipeline: heartmula → dual_text_media_generation → output_music_heartmula.py
```

### Parameter-Flow für HeartMuLa
```
Frontend custom_placeholders: { TEXT_1, TEXT_2, max_audio_length_ms }
  → schema_pipeline_routes.py: extracted into custom_params
  → pipeline_executor.py: context_override.custom_placeholders
  → chunk_builder.py: parameters.update(custom_placeholders)
  → output_music_heartmula.py: execute(TEXT_1=lyrics, TEXT_2=tags, max_audio_length_ms=...)
```

### Seed-Logik
- Phase 4 Seed (123456789) wird für Python-Chunks übersprungen
- HeartMuLa generiert eigenen random Seed
- Check: `chunk_request.get('backend_type') != 'python'`

---

## Dateien

### Frontend
- `public/ai4artsed-frontend/src/views/music_generation.vue` - Hauptseite

### Backend
- `devserver/my_app/routes/schema_pipeline_routes.py` - Pipeline Orchestrierung
- `devserver/my_app/routes/media_routes.py` - Media Serving (404 Fix)
- `devserver/schemas/engine/pipeline_executor.py` - Wikipedia Skip + Seed Skip
- `devserver/schemas/engine/chunk_builder.py` - custom_placeholders Injection
- `devserver/schemas/chunks/output_music_heartmula.py` - HeartMuLa Chunk
- `devserver/schemas/configs/output/heartmula_standard.json` - Output Config

### Interception Configs
- `devserver/schemas/configs/interception/heartmula.json` - Main (skip_stage2)
- `devserver/schemas/configs/interception/lyrics_refinement.json` - Lyrics Stream
- `devserver/schemas/configs/interception/tags_generation.json` - Tags Stream
