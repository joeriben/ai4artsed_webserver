# STORAGE FIX - PRÄZISE ANWEISUNGEN FÜR SONNET

## ⚠️ WICHTIG: KEINE INTERPRETATION, NUR EXAKTE AUSFÜHRUNG!

---

## PHASE 1: KRITISCHE BUG FIXES (3 Stellen)

### Fix 1: schema_pipeline_routes.py, Zeile 915

**VORHER:**
```python
dest_path = os.path.join(recorder.run_dir, output_filename)
```

**NACHHER:**
```python
dest_path = recorder.run_folder / output_filename
```

### Fix 2: pipeline_stream_routes.py, Zeile 60

**VORHER:**
```python
if not recorder.run_dir.exists():
```

**NACHHER:**
```python
if not recorder.run_folder.exists():
```

### Fix 3: pipeline_stream_routes.py, Zeile 75

**VORHER:**
```python
metadata_path = recorder.run_dir / 'metadata.json'
```

**NACHHER:**
```python
metadata_path = recorder.run_folder / 'metadata.json'
```

---

## PHASE 2: CUSTOM CODE ERSETZEN

### In schema_pipeline_routes.py, ERSETZE Zeilen 897-926 KOMPLETT:

**LÖSCHE DIESE 30 ZEILEN (897-926):**
```python
elif output_value == 'workflow_generated':
    # Workflow-based generation (audio, video, etc.) - filesystem copy
    logger.info(f"[RECORDER-DEBUG] Workflow generated - metadata keys: {list(output_result.metadata.keys())}")
    filesystem_path = output_result.metadata.get('filesystem_path')
    if filesystem_path:
        # Direct filesystem copy (for audio/video from ComfyUI)
        import shutil
        import os

        # Determine output filename based on media type
        if media_type == 'audio':
            ext = 'mp3'
        elif media_type == 'video':
            ext = 'mp4'
        else:
            ext = 'bin'

        output_filename = f"07_output_{media_type}.{ext}"
        dest_path = os.path.join(recorder.run_dir, output_filename)

        try:
            shutil.copy2(filesystem_path, dest_path)
            saved_filename = output_filename
            logger.info(f"[RECORDER] ✓ Copied {media_type} from filesystem: {output_filename}")
        except Exception as e:
            logger.error(f"[RECORDER] Failed to copy {media_type} file: {e}")
            saved_filename = None
    else:
        logger.warning(f"[RECORDER] No filesystem_path in metadata for workflow_generated")
        saved_filename = None
```

**ERSETZE MIT DIESEN 18 ZEILEN:**
```python
elif output_value == 'workflow_generated':
    # Use recorder.save_entity for consistency
    filesystem_path = output_result.metadata.get('filesystem_path')
    if filesystem_path:
        try:
            with open(filesystem_path, 'rb') as f:
                file_data = f.read()

            saved_filename = recorder.save_entity(
                entity_type=f'output_{media_type}',
                content=file_data,
                metadata={
                    'config': output_config_name,
                    'backend': 'comfyui',
                    'seed': seed,
                    'filesystem_path': filesystem_path
                }
            )
            logger.info(f"[RECORDER] Saved {media_type} from filesystem: {saved_filename}")
        except Exception as e:
            logger.error(f"[RECORDER] Failed to save {media_type} from filesystem: {e}")
            saved_filename = None
    else:
        logger.warning(f"[RECORDER] No filesystem_path in metadata for workflow_generated")
        saved_filename = None
```

---

## PHASE 3: VERIFIKATION

### Führe diese Befehle aus um zu verifizieren:

```bash
# 1. Verifiziere dass KEIN run_dir mehr existiert:
grep -n "recorder\.run_dir" devserver/my_app/routes/*.py devserver/schemas/engine/*.py

# Erwartete Ausgabe: NICHTS (keine Treffer)
```

```bash
# 2. Verifiziere dass die imports entfernt wurden:
grep -n "import shutil" devserver/my_app/routes/schema_pipeline_routes.py

# Erwartete Ausgabe: NICHTS oder nur andere legitime Verwendungen
```

```bash
# 3. Verifiziere dass kein hardcoded "07" mehr existiert:
grep -n '"07_output_' devserver/my_app/routes/schema_pipeline_routes.py

# Erwartete Ausgabe: NICHTS (keine Treffer)
```

---

## PHASE 4: TEST

```bash
# Starte den Server
cd devserver
python3 server.py

# In anderem Terminal: Teste audio generation
curl -X POST http://localhost:7777/api/schema_pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "music",
    "input_text": "peaceful piano music",
    "execution_mode": "eco",
    "safety_level": "all"
  }'
```

---

## ⚠️ HÄUFIGE FEHLER - NICHT MACHEN!

1. ❌ NICHT `os.path.join()` verwenden - use Path `/` operator
2. ❌ NICHT neue imports hinzufügen (shutil, os sind nicht mehr nötig)
3. ❌ NICHT die Zeilen falsch zählen - genau 897-926 ersetzen
4. ❌ NICHT `run_dir` irgendwo stehen lassen
5. ❌ NICHT eigene "Verbesserungen" hinzufügen

---

## FINALE CHECKLISTE

- [ ] 3x `run_dir` → `run_folder` geändert
- [ ] Zeilen 897-926 komplett ersetzt (nicht mehr, nicht weniger)
- [ ] Keine `import shutil` mehr in diesem Block
- [ ] Kein hardcoded "07" mehr
- [ ] `grep "recorder\.run_dir"` gibt NICHTS zurück
- [ ] Server startet ohne Fehler
- [ ] Audio generation funktioniert

---

## WENN FERTIG:

Committe mit dieser Message:
```
fix: Clean up storage chaos - use consistent save_entity API

- Fix AttributeError: run_dir → run_folder (3 locations)
- Replace 30 lines custom filesystem copy with save_entity() call
- Remove hardcoded sequence numbers
- Consistent Path object usage

Fixes critical bugs in audio/video storage from Session 51.
```

---

END OF INSTRUCTIONS