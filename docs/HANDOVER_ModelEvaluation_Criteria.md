# Handover: Kriterien für LLM Model Evaluation

**Kontext:** Session 133 führte eine Model-Evaluation durch, die oberflächlich war und keine aussagekräftigen Ergebnisse lieferte. Dieses Dokument definiert Kriterien für eine korrekte Evaluation.

---

## Fehler der vorherigen Evaluation

1. **Oberflächliche Bewertung:** "Enthält Renaissance-Vokabular" wurde als Erfolg gewertet
2. **Keine echte Qualitätsprüfung:** Meta-Kommentare ("wird ausgeführt als...") wurden übersehen
3. **Kulturelle Spezifität ignoriert:** Generische Beschreibungen wurden akzeptiert
4. **Buzzword-Blindheit:** Fachbegriffe im Output = gute Bewertung, ohne Prüfung ob korrekt angewendet

---

## Korrekte Evaluationskriterien

### 1. Kulturelle Spezifität
- [ ] Output verwendet **kulturspezifisches Vokabular** (nicht generische Kunstbegriffe)
- [ ] Renaissance ≠ Literati ≠ Bauhaus - Outputs müssen **unterscheidbar** sein
- [ ] KEIN Default zu westlichen/europäischen Ästhetik-Annahmen bei nicht-westlichen Traditionen

### 2. Keine Meta-Kommentare
- [ ] KEINE Phrasen wie "wird ausgeführt als", "zeigt", "stellt dar"
- [ ] KEINE Phrasen wie "I will...", "This depicts...", "The artwork shows..."
- [ ] Output beschreibt DAS KUNSTWERK, nicht dass es EIN Kunstwerk ist

### 3. Konkrete visuelle Elemente
- [ ] Spezifische Techniken genannt (sfumato, cun-Striche, etc.)
- [ ] Konkrete Materialien (Xuan-Papier, Holztafel, etc.)
- [ ] Kompositionselemente (Zentralperspektive, Drei Fernen, etc.)

### 4. Ekphrasis-Test
- [ ] Liest sich wie Beschreibung eines EXISTIERENDEN Kunstwerks
- [ ] Jemand könnte die Kunsttradition allein aus der Beschreibung identifizieren

### 5. Pädagogischer Wert
- [ ] Output eignet sich zur kritischen Diskussion über KI und Kultur
- [ ] Zeigt wo KI kulturelles Wissen korrekt/inkorrekt anwendet

---

## Test-Protokoll für Evaluation

### Test-Prompt
```
"Ein Strassenfest"
```

### Test-Configs (Minimum)
1. **Renaissance** - Europäische Kunstgeschichte
2. **Literati** - Konfuzianische Gelehrtenmalerei (härter, kulturell spezifisch)
3. **Im Gegenteil** - Logische Transformation (nicht künstlerisch)
4. **Bauhaus** - Moderne, geometrisch
5. **Analog Photography 1870s** - Technisch/ästhetisch

### Bewertungsmatrix pro Output

| Kriterium | 0 (fail) | 1 (partial) | 2 (good) |
|-----------|----------|-------------|----------|
| Kulturspezifisches Vokabular | Generisch | Teils spezifisch | Durchgehend spezifisch |
| Keine Meta-Kommentare | Mehrere | Vereinzelt | Keine |
| Konkrete visuelle Elemente | Abstrakt | Teils konkret | Durchgehend konkret |
| Unterscheidbar von anderen Stilen | Austauschbar | Teils erkennbar | Klar identifizierbar |

**Minimum für "bestanden": 6/8 Punkte**

---

## Beispiel: GUTER vs. SCHLECHTER Output

### Renaissance - SCHLECHT (Session 133)
```
Ein Strassenfest wird als Gemälde ausgeführt. Die Szene entfaltet sich auf einer
breiten, gepflasterten Straße...
```
❌ "wird als Gemälde ausgeführt" = Meta-Kommentar
❌ Generische Beschreibung, könnte jede Epoche sein

### Renaissance - GUT (erwartet)
```
Auf grundierter Holztafel entfaltet sich in strenger Zentralperspektive ein
Straßenfest. Sfumato modelliert die Gesichter der Figuren, die in pyramidaler
Gruppierung den Bildraum strukturieren. Lasuren in Ölfarbe...
```
✅ Spezifische Technik (sfumato, Lasuren)
✅ Spezifische Komposition (Zentralperspektive, pyramidale Gruppierung)
✅ Kein Meta-Kommentar

### Literati - SCHLECHT
```
Ein Strassenfest ist eine lebhafte Veranstaltung, die in vielen Gemeinschaften
gefeiert wird...
```
❌ Wikipedia-Erklärung statt Transformation
❌ Keine kulturelle Spezifität

### Literati - GUT (Session 134 mit Fix)
```
Qiyun shengdong dominiert das Bild. Kiefern, Bambus, Pflaumen und Orchideen
folgen den Konventionen des Mustard Seed Garden Manual, ihre Äste in
kalligrafischen Linien als Knochenstruktur-Pinselstriche...
```
✅ Kulturspezifisches Vokabular (qiyun shengdong, Mustard Seed Garden Manual)
✅ Konkrete Techniken (kalligrafische Linien, Knochenstruktur-Pinselstriche)
