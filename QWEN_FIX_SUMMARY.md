# QWEN Prompt Fix - Summary für morgen

**Commit:** `38bf0c6` (develop branch)
**Status:** ✅ Bereit zum Testen

---

## Was gemacht wurde:

### 1. Backend-Fix (backend_router.py)
**Problem:** Line 328 extrahiert Prompt aus `parameters` dict (leer) statt aus `prompt` parameter
**Fix:** `text_prompt = prompt` (direkt den richtigen Parameter nutzen)

### 2. Neue Test-Config (parallel zur alten)
**Name:** "Qwen Test" (🔬 Icon)
**Files:**
- `devserver/schemas/configs/output/qwen_test.json`
- `devserver/schemas/chunks/output_image_qwen_test.json`

**Unterschied zur alten:** Komplett neu geschrieben, direkte Prompt-Injection

---

## Testen (morgen):

### Im Frontend (localhost:5173):

**Option 1: "Qwen Image"** (Original + Fix)
- Prompt: "ein rotes Haus"
- Erwartung: Neues Bild (NICHT mehr das gecachte alte)

**Option 2: "Qwen Test"** (🔬, Neue Implementation)
- Prompt: "ein blaues Auto"
- Erwartung: Neues Bild

### Logs überprüfen:
```bash
# Backend-Logs filtern für QWEN:
tail -f <backend-log> | grep -E "WORKFLOW-CHUNK|qwen|QWEN"
```

**Suche nach:**
- ✅ `[WORKFLOW-CHUNK] Using prompt: 'A red house...'` (NICHT leer!)
- ✅ ComfyUI generation logs mit QWEN models
- ❌ NICHT mehr: `[DEBUG-FIX] ⚠️ No text prompt in parameters!`

---

## Was zu erwarten ist:

**Wenn Original QWEN funktioniert:**
→ Backend-Fix war erfolgreich, `qwen_test` kann gelöscht werden

**Wenn nur QWEN_TEST funktioniert:**
→ Tieferes Problem im Workflow-Mapping, weitere Investigation nötig

**Wenn beide nicht funktionieren:**
→ Problem ist woanders (ComfyUI, Model-Files, etc.)

---

## Backup-Plan:

Alle Änderungen sind committed, alte Configs intakt:
- Original `qwen` Config: Unverändert
- Neue `qwen_test` Config: Parallel verfügbar
- Backend-Fix: Kann leicht revertiert werden

**Rollback:** `git revert 38bf0c6` falls nötig

---

## Backend & Frontend Status:

**Backend:** Läuft auf Port 17802 (3_start_backend_dev.sh im Hintergrund)
**Frontend:** Läuft auf Port 5173 (npm run dev im Hintergrund)

**Beide sollten automatisch laufen.**

---

Gute Nacht! 🌙
