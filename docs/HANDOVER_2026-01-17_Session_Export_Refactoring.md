# Handover: Export & Session Architecture Refactoring

**Date:** 2026-01-17
**Status:** IMPLEMENTED - Testing needed

---

## Was wurde erreicht

### 1. Unified Export Fix (COMMITTED)
- `run_id` wird von `/interception` durch Frontend zu `/generation` durchgereicht
- Alle Backends speichern korrekt: SD3.5, QWEN, FLUX2, Gemini, GPT-Image
- Commits: `7f07197`, `d0e85f6`, `680e704`

### 2. Routing Refactoring (COMMITTED)
- `media_type: "image_workflow"` eliminiert
- Neues Flag: `requires_workflow: true/false` in Chunks
- QWEN/FLUX2: `requires_workflow: true` (Custom Nodes)
- SD3.5: `requires_workflow: false` (SwarmUI Simple API)
- Commits: `a08a39d`, `da18e8b`

### 3. Pipeline Executor Init Fix (COMMITTED)
- `_load_optimization_instruction()` und `_load_estimated_duration()`
- Rufen jetzt `init_schema_engine()` auf wenn `pipeline_executor` None ist
- Commit: `da18e8b`

---

## Was implementiert wurde (2026-01-17 Session 2)

### Commits:
- `1fabb11` - Revert "fix: Return LATEST image by default" (index=-1 fix)
- `521f96e` - feat(export): Each generation creates new run with complete context

### Änderungen:

1. **`pipeline_recorder.py`**:
   - `__init__`: Date-based folder structure (`exports/json/YYYY-MM-DD/run_xxx/`)
   - `load_recorder()`: Searches across date folders for existing runs

2. **`schema_pipeline_routes.py`**:
   - `/generation` ALWAYS creates new `run_id` (removed `provided_run_id` logic)
   - Accepts context: `input_text`, `interception_result`, `interception_config`, `device_id`
   - Saves all entities (input, interception, optimized_prompt) upfront

3. **`text_transformation.vue`**:
   - `getDeviceId()`: LocalStorage-based UUID for workshop tracking
   - `lastInterceptionConfig`: Tracks which interception config was used
   - `/generation` call sends all context data

---

## Was noch zu testen ist

### Task 1: Option A - Jede Generation = Neuer Run

**Problem:** Aktuell akkumulieren mehrere Bilder in einem Run-Ordner.

**Lösung:** `/generation` erstellt IMMER neuen `run_id`, Frontend sendet alle Kontext-Daten.

**Frontend sendet an `/generation`:**
```typescript
{
  // Kontext von Interception (Frontend hat diese Daten)
  input_text: "Der Hase und der Igel...",
  interception_result: "Der Hase und der Igel. Ich fotografiere...",
  interception_config: "planetarizer",
  safety_level: "youth",

  // Generation-spezifisch
  prompt: "...",  // evtl. optimiert
  output_config: "flux2",
  seed: 123456,

  // Device ID (NEU)
  device_id: "a1b2c3d4-..."

  // KEIN run_id mehr!
}
```

**Backend `/generation`:**
1. Erstellt NEUE `run_id`
2. Speichert ALLE Entities:
   - `01_input.txt`
   - `02_interception.txt`
   - `03_optimized_prompt.txt` (falls vorhanden)
   - `04_output_image.png`
   - `metadata.json`

**Dateien zu ändern:**
- `devserver/my_app/routes/schema_pipeline_routes.py` - `/generation` Endpoint
- `public/ai4artsed-frontend/src/views/text_transformation.vue` - Kontext-Daten senden

### Task 2: Datum-basierte Ordnerstruktur

**Problem:** `exports/json/` wird zu groß.

**Lösung:**
```
exports/json/
├── 2026-01-17/
│   ├── run_abc/
│   └── run_xyz/
├── 2026-01-16/
│   └── run_123/
```

**Dateien zu ändern:**
- `devserver/my_app/services/pipeline_recorder.py`:
  ```python
  # Zeile ~71 ändern von:
  self.run_folder = self.base_path / run_id
  # zu:
  date_folder = datetime.now().strftime('%Y-%m-%d')
  self.run_folder = self.base_path / date_folder / run_id
  ```
- `load_recorder()` muss über Datum-Ordner suchen können

### Task 3: Device-ID für Workshop-Tracking

**Problem:** Bei Workshops: Welches iPad hat welche Daten erzeugt?

**Lösung:**
1. **Frontend:** LocalStorage-basierte Device-ID
   ```typescript
   const deviceId = localStorage.getItem('device_id')
     || (localStorage.setItem('device_id', crypto.randomUUID()),
         localStorage.getItem('device_id'))
   ```

2. **Backend:** `device_id` in Metadaten speichern
   ```json
   {
     "run_id": "run_xxx",
     "device_id": "a1b2c3d4-...",
     "device_name": "iPad Tisch 3"  // Optional, später über Admin-UI
   }
   ```

3. **Export-Tool:** Kann nach `device_id` filtern

---

## Zu revertende Commits

- Commit `525c7c7` (index=-1 Fix) - wird mit Option A obsolet

---

## Offene Design-Entscheidungen

### Multi-Output Workflows
- Legacy Workflows (partial_elimination etc.) haben eigene Routinen
- Brauchen KEINEN Fix, bleiben wie sie sind

### Device Naming
- Optional: Admin-UI um Geräte zu benennen
- Oder: QR-Code scannen bei Workshop-Start
- Oder: Einfach nur UUID speichern, später zuordnen

---

## Git Status bei Session-Ende

```
Recent commits:
525c7c7 fix: Return LATEST image by default (TO REVERT)
da18e8b fix: Initialize pipeline_executor before using config_loader
a08a39d refactor(routing): Use requires_workflow flag
c8b5077 Revert "fix(routing): Check chunk workflow..."
```

Untracked (WIP):
- `devserver/schemas/pipelines/p5js_code.json`
- `public/ai4artsed-frontend/src/views/p5js_code.vue`

---

## Testplan nach Implementation

1. **Neuer Run pro Generation:**
   - Interception → Generate FLUX2 → Check: Neuer Ordner mit allen Daten
   - Generate SD3.5 (gleiche Interception) → Check: SEPARATER neuer Ordner

2. **Datum-Ordner:**
   - Check: Runs landen in `exports/json/2026-01-17/`
   - Check: `load_recorder()` findet alte Runs

3. **Device-ID:**
   - Check: `device_id` in metadata.json
   - Check: Unterschiedliche Browser haben unterschiedliche IDs

---

## Referenz-Dateien

| Datei | Relevanz |
|-------|----------|
| `schema_pipeline_routes.py` | `/generation` Endpoint |
| `pipeline_recorder.py` | `LivePipelineRecorder`, `load_recorder()` |
| `text_transformation.vue` | Frontend Flow |
| `media_routes.py` | `/api/media/image/<run_id>` |

---

**Erstellt:** 2026-01-17 13:15
**Autor:** Claude Opus 4.5 Session
