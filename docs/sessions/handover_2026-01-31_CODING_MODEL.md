# Handover: CODING_MODEL für Code-Generierung

**Date:** 2026-01-31
**Status:** 90% fertig - nur noch testen

## Kontext

Code-Generierung (Tone.js, p5.js) verwendete hardcoded `claude-sonnet-4.5` (teuer).
Jetzt: Globales `CODING_MODEL` Setting mit Codestral als Default.

## Was implementiert wurde

### 1. config.py
```python
CODING_MODEL = "mistral/codestral-latest"
```

### 2. settings_routes.py
- HARDWARE_MATRIX: 36 Einträge mit CODING_MODEL für alle VRAM-Tiers × Provider
- GET `/api/settings/`: CODING_MODEL in Response aufgenommen

### 3. SettingsView.vue
```javascript
'CODING_MODEL': 'Code Generation (Tone.js, p5.js)'
```

### 4. Output-Configs (Override-Pattern)
- `tonejs_code.json`: `meta.model: "CODING_MODEL"`
- `p5js_code.json`: `meta.model: "CODING_MODEL"`

### 5. schema_pipeline_routes.py
- `_load_model_from_output_config()`: Lädt Model aus Output-Config, löst Config-Variablen auf
- Override-Logik in Optimization-Route:
  ```python
  if output_config:
      model_override = _load_model_from_output_config(output_config)
  if model_override and model_override != "DEFAULT":
      model = model_override
  else:
      model = STAGE3_MODEL
  ```
- Import geändert: `STAGE3_MODEL` statt `STAGE2_INTERCEPTION_MODEL`

### 6. text_transformation.vue
- `output_config: selectedConfig.value || ''` zu optimizationStreamingParams hinzugefügt

## Geänderte Dateien (NICHT COMMITTED)

- `devserver/config.py`
- `devserver/my_app/routes/settings_routes.py`
- `devserver/my_app/routes/schema_pipeline_routes.py`
- `devserver/schemas/configs/output/tonejs_code.json`
- `devserver/schemas/configs/output/p5js_code.json`
- `public/ai4artsed-frontend/src/views/SettingsView.vue`
- `public/ai4artsed-frontend/src/views/text_transformation.vue`
- `DEVELOPMENT_LOG.md` (Session 154 Entry - kann entfernt werden)

## Zu testen

1. Backend neu starten
2. Settings öffnen → CODING_MODEL Feld sollte erscheinen
3. Quick-Fill testen → CODING_MODEL sollte befüllt werden
4. Tone.js generieren
5. Log prüfen: `[LOAD-MODEL] Resolved config.CODING_MODEL → mistral/codestral-latest`

## Bekannte Issues

- `STAGE2_OPTIMIZATION_MODEL` ist falsch benannt (Optimization ist Stage 3, nicht Stage 2)
- Später refactoren zu `STAGE3_OPTIMIZATION_MODEL`

## Architektur-Prinzip

**Override-Pattern:**
- Standard: Output-Configs haben kein `meta.model` oder `"DEFAULT"` → verwendet `STAGE3_MODEL`
- Override: `meta.model: "CODING_MODEL"` → spezielles Model für Code-Generierung
