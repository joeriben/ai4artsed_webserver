# Session 91: Settings System mit DSGVO/VRAM Matrix

**Datum**: 2025-12-08
**Status**: Implementiert, Testing ausstehend
**Branch**: `develop` (Commit: `ca9a373`)

---

## Ziel

Maschinen-spezifische Konfiguration für unterschiedliche GPU-Hardware:
- **PC1**: RTX 6000 Pro Blackwell (96GB VRAM) - DSGVO-konform mit lokalen Modellen
- **PC2**: RTX 4090 (24GB VRAM) - Andere Konfiguration

**Lösung**: 2D-Matrix (VRAM-Tier × DSGVO-Modus) mit automatischer Hardware-Erkennung

---

## Architektur

### 2D-Konfig-Matrix

**Dimensionen:**
1. **VRAM-Tier**: `vram_8` | `vram_16` | `vram_24` | `vram_32` | `vram_48` | `vram_96`
2. **DSGVO-Modus**: `local_only` (true/false)

**Logik:**
- **DSGVO=false** (Cloud erlaubt): Aktuelle hardcodierte `config.py` Werte bleiben
- **DSGVO=true** (nur lokal): Matrix bestimmt Modelle basierend auf VRAM-Tier

### Modell-Strategie

| VRAM | Strategie | Text-LLM | Vision-LLM | Grund |
|------|-----------|----------|------------|-------|
| 8 GB | Getrennt | gemma:2b | Cloud only | Minimal |
| 16 GB | Getrennt | gemma:2b | llava:7b | Load-Zeit OK |
| 24 GB | Getrennt | mistral-nemo | llama3.2-vision:11b | Load-Zeit OK |
| 32 GB | Getrennt | mistral-nemo | llama3.2-vision:11b | Mehr Headroom |
| 48 GB | **Universal** | llava:34b | llava:34b | ~20GB, kein Wechsel |
| 96 GB | **Universal** | llama3.2-vision:90b | llama3.2-vision:90b | ~50GB, kein Wechsel |

**Prinzip**: Große VRAM → Ein Universal-Modell (kein Load/Unload). Kleine VRAM → Getrennte Modelle.

---

## Implementierte Komponenten

### Backend (Python)

| Datei | Beschreibung | Status |
|-------|--------------|--------|
| `devserver/my_app/services/gpu_detection_service.py` | VRAM-Erkennung (pynvml + nvidia-smi) | ✅ Erstellt |
| `devserver/my_app/services/settings_service.py` | Matrix-Auswertung, Persistenz | ✅ Erstellt |
| `devserver/my_app/routes/settings_routes.py` | REST API (6 Endpoints) | ✅ Erstellt |
| `devserver/schemas/configs/config_matrix.json` | 2D-Matrix Definition | ✅ Erstellt |
| `devserver/config.py` | `get_effective_model()` Funktion | ✅ Erweitert |
| `devserver/my_app/__init__.py` | Settings-Initialisierung | ✅ Erweitert |
| `devserver/schemas/engine/chunk_builder.py` | DSGVO-aware Model-Resolution | ✅ Integriert |

### Frontend (Vue)

| Datei | Beschreibung | Status |
|-------|--------------|--------|
| `public/.../src/stores/settingsStore.ts` | Pinia Store | ✅ Erstellt |
| `public/.../src/views/SettingsView.vue` | Settings-Seite | ✅ Erstellt |
| `public/.../src/App.vue` | Settings-Button + DSGVO-Indikator | ✅ Erweitert |
| `public/.../src/router/index.ts` | Route `/settings` | ✅ Erweitert |

### Output-Configs

| Datei | Änderung | Status |
|-------|----------|--------|
| `devserver/schemas/configs/output/gpt_image_1.json` | `is_cloud_service: true` | ✅ Getaggt |
| `devserver/schemas/configs/output/gemini_3_pro_image.json` | `is_cloud_service: true` | ✅ Getaggt |

### Konfiguration

| Datei | Änderung | Status |
|-------|----------|--------|
| `.gitignore` | `devserver/user_settings.json` | ✅ Hinzugefügt |

---

## API Endpoints

```
GET  /api/settings                 → Aktuelle Settings + Hardware-Info
PUT  /api/settings                 → Settings aktualisieren (partial)
POST /api/settings/reset           → Auf Defaults zurücksetzen
GET  /api/settings/hardware        → GPU-Info
POST /api/settings/hardware/detect → Hardware neu erkennen
GET  /api/settings/matrix          → Komplette Matrix
GET  /api/settings/output-configs  → Verfügbare Output-Configs
GET  /api/settings/categories      → Verfügbare Kategorien (disabled-Flags)
```

---

## Startup-Flow

```
Server startet
    │
    ├─ user_settings.json existiert NICHT?
    │   ├─ GPU Detection → VRAM auslesen
    │   ├─ VRAM-Tier bestimmen
    │   ├─ Defaults aus Matrix (DSGVO=false)
    │   └─ user_settings.json erstellen
    │
    └─ user_settings.json existiert?
        └─ File laden (Auto-Detection ignoriert)
```

---

## user_settings.json Schema

```json
{
  "schema_version": "1.0",
  "created_at": "2025-12-08T10:00:00Z",
  "modified_at": "2025-12-08T14:30:00Z",
  "hardware": {
    "gpu_name": "NVIDIA RTX 6000 Pro Blackwell",
    "vram_mb": 98304,
    "vram_tier": "vram_96"
  },
  "dsgvo_local_only": false,
  "models": {
    "text_model": "ollama/llama3.2-vision:90b",
    "vision_model": "ollama/llama3.2-vision:90b"
  },
  "default_output_config": "sd35_large"
}
```

**Speicherort**: `devserver/user_settings.json` (gitignored)

---

## Testing-Checkliste

### Backend Tests

- [ ] Server startet ohne Fehler
- [ ] GPU Detection funktioniert (`gpu_detection_service.py`)
- [ ] `user_settings.json` wird beim ersten Start erstellt
- [ ] Settings API ist erreichbar: `GET /api/settings`
- [ ] VRAM-Tier wird korrekt erkannt
- [ ] Matrix-Defaults werden korrekt geladen

### Frontend Tests

- [ ] Settings-Seite lädt: `http://localhost:5173/settings`
- [ ] Hardware-Info wird angezeigt
- [ ] DSGVO-Toggle funktioniert
- [ ] Settings-Button im Header ist sichtbar
- [ ] DSGVO-Indikator erscheint wenn aktiviert

### Integration Tests

- [ ] DSGVO=true → chunk_builder.py nutzt lokale Modelle
- [ ] DSGVO=false → chunk_builder.py nutzt config.py Defaults
- [ ] Output-Configs werden korrekt gefiltert
- [ ] Cloud-Configs (gpt_image_1, gemini_3_pro) sind disabled wenn DSGVO=true

---

## Bekannte Probleme / Offene Punkte

### Testing Required

1. **Import-Fehler möglich**: `pynvml` Bibliothek möglicherweise nicht installiert
   - Fallback auf `nvidia-smi` sollte funktionieren
   - Testen mit: `python -c "from my_app.services.gpu_detection_service import detect_gpu; print(detect_gpu())"`

2. **Settings-Initialisierung**: Beim Server-Start wird `initialize_settings()` aufgerufen
   - Checken ob Fehler im Log
   - Checken ob `user_settings.json` erstellt wurde

3. **Frontend-Store**: `settingsStore.fetchSettings()` wird in `App.vue` onMounted aufgerufen
   - Checken ob API-Call erfolgreich
   - Browser DevTools → Network → `/api/settings`

4. **Circular Import**: Möglicher Circular Import zwischen `config.py` und `settings_service.py`
   - Getestet durch lazy loading in `config._get_settings_service()`

### Noch zu implementieren

1. **Output-Config Filterung in Vue**: `text_transformation.vue` und `image_transformation.vue` müssen `settingsStore.isCategoryEnabled()` nutzen
   - Categories mit `disabled: true` ausblenden
   - Output-Configs basierend auf `availableOutputConfigs` filtern

2. **Weitere Output-Configs taggen**: Nur `gpt_image_1` und `gemini_3_pro_image` haben `is_cloud_service: true`
   - Alle lokalen Configs sollten explizit `is_cloud_service: false` haben (optional, zur Klarheit)

3. **Settings-Page erweitern**: Aktuell nur Basic-Version
   - Individuelle Modell-Konfiguration (Experten-Modus)
   - Dropdown für manuelle Modell-Auswahl

4. **Flux2 Output-Config**: Für 96GB VRAM noch zu erstellen
   - `devserver/schemas/configs/output/flux2.json`

---

## Nächste Schritte

1. **Backend starten**: `./3_start_backend_dev.sh`
2. **Frontend starten**: `./4_start_frontend_dev.sh`
3. **Logs prüfen**: Backend-Log auf Fehler checken
4. **Settings-API testen**: `curl http://localhost:17802/api/settings`
5. **Frontend testen**: `http://localhost:5173/settings`
6. **Fehler fixen**: Import-Fehler, fehlende Dependencies
7. **Vue-Integration**: Output-Config Filterung in text_transformation.vue

---

## Commits

1. `877cd6b` - chore: Add deployment scripts and Session 90 handover docs
2. `f8ea3ba` - fix: TypeScript errors in Vue components
3. `ca9a373` - feat: Settings system with DSGVO/VRAM matrix (Session 91)

**Pushed to**: `develop`
**Not yet merged to**: `main`

---

## Architektur-Notizen

### Wichtige Design-Entscheidungen

1. **Keine "Overrides"**: Settings sind Konfigurationen, nicht Overrides
   - Matrix liefert Empfehlungen beim ersten Start
   - Danach: User-Settings

2. **Existierende `disabled` Flag nutzen**: Vue hat bereits `disabled: true` für Categories (z.B. 3D)
   - KEINE Parallelstruktur implementiert
   - Settings-API liefert `disabled`-Status
   - Vue nutzt existierende Logik

3. **Lazy Loading**: `config.py` lädt Settings-Service lazy um Circular Imports zu vermeiden

4. **DSGVO=false**: Keine Filterung nötig, aktuelle config.py bleibt

---

## Fehlersuche

### Problem: Settings-Seite nicht erreichbar

**Mögliche Ursachen:**
1. Frontend-Build fehlt Route nicht
2. Backend-Import-Fehler blockiert Server-Start
3. Settings-API wirft Fehler

**Debug-Schritte:**
```bash
# 1. Backend-Log prüfen
# Schauen nach: "[INIT] Settings initialized: VRAM tier=..."

# 2. Settings-API direkt testen
curl http://localhost:17802/api/settings

# 3. Frontend dev console
# Browser → DevTools → Console → Fehler?

# 4. GPU Detection manuell testen
cd /home/joerissen/ai/ai4artsed_development/devserver
python3 -c "from my_app.services.gpu_detection_service import detect_gpu; print(detect_gpu())"
```

### Problem: Import-Fehler

**Wahrscheinlich**: `pynvml` nicht installiert

**Fix:**
```bash
pip install pynvml
```

**Oder**: nvidia-smi Fallback sollte automatisch greifen

---

## Dateien für nächste Session

**Kritisch zum Debuggen:**
- `devserver/my_app/__init__.py:103-109` - Settings-Initialisierung
- `devserver/my_app/services/settings_service.py` - Kern-Logik
- `devserver/my_app/services/gpu_detection_service.py` - Hardware-Detection
- `public/.../src/App.vue:68-70` - Settings-Store Initialisierung
- `public/.../src/views/SettingsView.vue` - Settings-Page

**Noch zu integrieren:**
- `public/.../src/views/text_transformation.vue:477-482` - Categories disabled-Flag
- `public/.../src/components/MediumSelectionBubbles.vue` - Output-Config Filterung
