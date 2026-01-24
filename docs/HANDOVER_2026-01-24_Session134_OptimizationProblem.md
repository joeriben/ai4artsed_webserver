# Handover: Prompt Optimization Instruction - UNGELÖST

**Datum:** 2026-01-24
**Status:** OFFEN - Nächste Session muss das lösen

---

## Das Problem

Die `prompt_optimization` Instruction in `schemas/engine/instruction_selector.py` funktioniert nicht richtig.

### Beispiel-Fehler (Literati)

**Interception-Output (gut):**
```
Qiyun shengdong, die Geist-Resonanz und Lebensbewegung... Kiefern, Bambus, Pflaumen
und Orchideen folgen den strengen Konventionen des Mustard Seed Garden Manual...
```

**Optimization-Output (schlecht):**
```
moral landscape, small human figures, kiefern, bambus, pflaumen, orchideen,
konfuzianische ordnung, algorithmische pinselstriche, iterative algorithmen...
```

**Fehler:**
- Mischung Deutsch/Englisch (Übersetzung kommt erst DANACH in Stage 3!)
- Abstrakte Konzepte die nicht visualisierbar sind (konfuzianische ordnung, algorithmische pinselstriche)
- Keine echte Übersetzung kultureller Konzepte in visuelle Rendering-Anweisungen

---

## Die Kernkomplexität

Es gibt **verschiedene Interception-Typen** mit unterschiedlichen Optimization-Anforderungen:

| Typ | Beispiele | Was Optimization leisten muss |
|-----|-----------|------------------------------|
| **Kulturell** | Literati, Renaissance, Bauhaus | Kulturelle Konzepte → visuelle Äquivalente |
| **Logisch** | Im Gegenteil, Entkitscher | Logische Transformation → bildliche Umsetzung |
| **Dekonstruktiv** | Surrealizer, Split&Combine | Dekonstruktion → kompositorische Anweisungen |
| **Ästhetisch** | Analog Photography 1870s/1970s | Ästhetische Parameter → technische Bildparameter |
| **Technisch** | Technical Drawing, P5JS | Technische Specs → Rendering-Specs |

**Eine generische Instruction kann das nicht leisten.**

---

## Anforderungen an Optimization

1. **Eingabesprache beibehalten** - Übersetzung zu Englisch erfolgt in Stage 3
2. **Kulturelle Spezifität erhalten** - nicht generisieren
3. **Konzepte in Visuelles übersetzen:**
   - "qiyun shengdong" → dynamische Pinselstriche, Bewegungsgefühl
   - "Guo Xis Drei Fernen" → hoher Horizont, geschichtete Tiefe, atmosphärische Perspektive
   - "sfumato" → weiche Kanten, rauchige Übergänge
4. **Dual-Encoder-Format** für SD3.5/FLUX:
   - CLIP-G: Kurze Keywords
   - T5-XXL: Natürliche Beschreibung

---

## Aktuelle Instruction (unzureichend)

```python
"prompt_optimization": {
    "default": """Translate the Input into visual instructions for image generation.
    TASK: Convert cultural and artistic concepts into HOW THEY LOOK.
    ...
    OUTPUT FORMAT (in input language):
    [CLIP: visual keywords, 25 words max] || [T5: descriptive sentence]
    """
}
```

Zu generisch, keine Beispiele für verschiedene Interception-Typen.

---

## Mögliche Lösungsansätze

1. **Typ-spezifische Optimization-Instructions**
   - Neue Instruction-Types: `optimization_cultural`, `optimization_logical`, etc.
   - Configs definieren welchen Optimization-Typ sie brauchen

2. **Config-Level Optimization-Prompts**
   - Jede Interception-Config hat eigenen Optimization-Prompt im JSON
   - Mehr Aufwand, aber präziser

3. **Zwei-Schritt-Prozess**
   - Schritt 1: Analyse der visualisierbaren Elemente
   - Schritt 2: Formatierung für CLIP/T5

---

## Datei

`devserver/schemas/engine/instruction_selector.py` - Zeile 27-47 (prompt_optimization)
