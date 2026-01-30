# HANDOVER: Canvas Batch - Image Export Issue

## Session 149 Status
**Commit**: `0b399eb` - feat(canvas): Add batch execution and CanvasRecorder

## Problem
Text-Outputs werden korrekt in `exports/json/.../final/` gespeichert, aber **generierte Bilder nicht**.

## Implementierte Architektur

### CanvasRecorder (`my_app/services/canvas_recorder.py`)
```python
recorder.save_entity(node_id, node_type, content)  # Text - funktioniert
recorder.save_image_from_url(node_id, url, config_id, seed)  # Bilder - PROBLEM
```

### Integration in canvas_routes.py
```python
# Nach erfolgreicher Generation (Zeile ~605):
if output and output.get('url'):
    recorder.save_image_from_url(
        node_id=node_id,
        url=output['url'],
        config_id=config_id,
        seed=output.get('seed')
    )
```

## Vermutete Ursachen

### 1. URL-Format Problem
Die `output['url']` von `execute_stage4_generation_only()` ist möglicherweise:
- Eine relative URL (`/api/media/image/...`) statt absolute
- Ein lokaler Pfad statt HTTP-URL
- Eine SwarmUI-interne URL die nicht von außen erreichbar ist

**Debug-Schritt**: Logger in `save_image_from_url()` prüfen:
```python
logger.info(f"[CANVAS_RECORDER] Attempting to download from: {url}")
```

### 2. Timeout/Async Problem
`save_image_from_url()` verwendet synchrones `requests.get()` innerhalb eines bereits laufenden async Kontexts.

**Mögliche Lösung**: Async version verwenden oder Bild-Daten direkt von `execute_stage4_generation_only()` zurückgeben.

### 3. Generation gibt keine URL zurück
Prüfen was `gen_result['media_output']` tatsächlich enthält:
```python
logger.info(f"[Canvas] Generation result: {gen_result['media_output']}")
```

## Zu prüfende Dateien

1. **`canvas_routes.py`** (Zeilen ~600-615): Generation node handling
2. **`canvas_recorder.py`** (Zeilen ~120-150): `save_image_from_url()`
3. **`schema_pipeline_routes.py`**: Was gibt `execute_stage4_generation_only()` zurück?

## Schnellster Fix-Ansatz

Statt URL-Download: Bild-Bytes direkt von `execute_stage4_generation_only()` holen:

```python
# In execute_stage4_generation_only() - media_output erweitern:
media_output = {
    'url': ...,
    'media_type': ...,
    'image_data': image_bytes  # NEU: Raw bytes
}

# In canvas_routes.py - direkt speichern:
if output.get('image_data'):
    recorder.save_image_from_bytes(
        node_id=node_id,
        image_data=output['image_data'],
        config_id=config_id,
        seed=output.get('seed'),
        backend=output.get('backend', 'unknown')
    )
```

## Batch-Endpoint funktioniert
Der Batch-Endpoint (`/api/canvas/execute-batch`) selbst funktioniert - SSE-Events werden korrekt gesendet, Ordner werden erstellt.

## Test-Workflow
1. Canvas mit: Input → Interception → Generation → Collector
2. Ausführen (single oder batch)
3. Prüfen: `exports/json/YYYY-MM-DD/*/canvas_run_*/final/`
4. Erwartung: `01_input.txt`, `02_interception.txt`, `03_generation.png`
5. Aktuell: Nur .txt Dateien vorhanden

## Relevante Log-Ausgaben
Suche nach:
- `[CANVAS_RECORDER]` - Recorder-Aktivität
- `[Canvas Tracer] Generation:` - Generation-Ergebnis
- `save_image_from_url` - Download-Versuch
