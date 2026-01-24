# Handover: Prompt Optimization Instruction - GELÖST

**Datum:** 2026-01-24
**Status:** GELÖST (Session 135)

---

## Das Problem (war)

Die `prompt_optimization` Instruction in `schemas/engine/instruction_selector.py` hatte:
- Hardcodierte kulturelle Mappings ("qiyun shengdong → dynamic brushstrokes")
- Ein image-spezifisches Output-Format (`[CLIP: ...] || [T5: ...]`)
- Diese Beispiele waren **falsch**, weil sie kreative Interception-Outputs in fixierte Bildanweisungen hardcodieren wollten

---

## Die Lösung

**Erkenntnis:** Die Output-Chunks (z.B. `output_image_sd35_large.json`, `output_video_ltx.json`) enthalten bereits sehr detaillierte, media-spezifische `optimization_instruction` in ihrem `meta` Feld. Diese werden als `Context` an das LLM übergeben.

**Fix:** Die `prompt_optimization` META-Instruction wurde vereinfacht zu:

```python
"prompt_optimization": {
    "description": "Apply media-specific optimization rules from Context",
    "default": """Transform the Input according to the rules in Context.

The Context contains media-specific transformation rules.
Apply these rules precisely to the Input.
Preserve the language of the Input.

Output ONLY the transformed result.
NO meta-commentary, NO headers, NO formatting."""
}
```

**Warum das funktioniert:**
1. Die media-spezifischen Regeln stehen bereits in den Output-Chunks
2. Die META-Instruction muss nur sagen: "Folge den Context-Regeln"
3. Keine hardcodierten Beispiele = keine falschen Annahmen über kreative Outputs
4. Explizite Anweisung zur Spracherhaltung

---

## Geänderte Datei

`devserver/schemas/engine/instruction_selector.py` - Zeilen 27-37

---

## Verifizierung (TODO)

1. DevServer starten
2. Interception ausführen (z.B. Literati)
3. Optimization für SD3.5 Large triggern
4. Prüfen:
   - Output in Eingabesprache
   - Keine Sprach-Mischung
   - SD3.5-Format aus chunk `optimization_instruction` befolgt
