# Stage2-Prompt Qualitätskriterien (Trashy-Version)

**Für:** Trashy AI-Assistent
**Stand:** 2026-01-25

---

## Was sind Stage2-Prompts?

Stage2-Prompts sind die "Transformationsregeln" in AI4ArtsEd. Sie bestimmen, WIE der Input des Users verwandelt wird - nicht WAS daraus wird.

**Kernprinzip:** Die KI ist ein "Co-Akteur", kein Werkzeug. Sie interpretiert die Regeln und bringt ihre eigene "Handschrift" ein.

---

## Die 4 Säulen guter Stage2-Prompts

### 1. Perspektivübernahme statt Stilimitation

**RICHTIG:**
> "DU BIST eine Künstlerin der 1870er Jahre. Du lebst in..."

**FALSCH:**
> "Generiere im Vintage-Stil"

**VERBOTEN:**
> "im Stil von [Künstlername]"

---

### 2. Klare Methodik mit Schritten

**RICHTIG:**
> "1. Analysiere... 2. Wende an... 3. Reduziere... 4. Beschreibe..."

**FALSCH:**
> "Sei kreativ und mach was Schönes"

---

### 3. Konkrete Verbote

**RICHTIG:**
> "VERBOTEN: romantisierende Begriffe ('nostalgisches Leuchten'), digitale Terminologie (Pixel, Sensoren)"

**FALSCH:**
> "Sei nicht zu kitschig"

---

### 4. Output-Format spezifizieren

**RICHTIG:**
> "Ein Absatz, 120-180 Wörter"

**FALSCH:**
> Kein Längenhinweis

---

## Red Flags (sofort korrigieren!)

| Problem | Beispiel |
|---------|----------|
| Platzhalter-Text | "professional translator" |
| Künstlername | "im Stil von Monet" |
| Leerer Context | `"context": {"en": "", "de": ""}` |
| Meta erlaubt | Kein Verbot von "Ich werde..." |
| Optimierungs-Framing | "Mache besser" |

---

## Bewertungs-Skala

| Score | Status | Beschreibung |
|-------|--------|--------------|
| 3 | Exzellent | Vollständige Methodik, Beispiele, Verbote, Format |
| 2 | Gut | Funktional, kleinere Verbesserungen möglich |
| 1 | Schwach | Fehlende Elemente, unklar |
| 0 | Kritisch | Platzhalter, keine Anleitung |

---

## Gold-Standard Beispiele

### Fotografie (analog_photography_1870s)
- Rollenidentität: "Du bist eine professionelle Fotografin..."
- Material: "silberjodierte Kupferplatten, Quecksilberentwicklung"
- Verbote: "NICHT verwenden: romantisierende Begriffe, 'im Stil von [Fotograf]'"
- Format: "Ein Absatz, 120-180 Wörter"

### Kunstgeschichte (bauhaus)
- 4-Schritt-Methodik
- Perspektiv-Verbot: "ES IST DIR VERBOTEN... 'Im Stil von'"
- Transformationsbeispiele: "Vase → funktionaler Prototyp"

### Kritisches Denken (planetarizer)
- Klares Framework: Anthropozän-Denken
- Strenge Verbote: "Othering, Exotisierung STRIKT untersagt"
- Theoretische Basis genannt

---

## Schnell-Check für neue Prompts

1. Hat der Prompt eine **Rollenidentität**? ("Du bist...")
2. Gibt es **konkrete Schritte** oder Methodik?
3. Sind **Verbote** spezifisch formuliert?
4. Ist das **Output-Format** angegeben?
5. Sind **beide Sprachen** (EN/DE) vollständig?

Wenn eine Frage mit NEIN beantwortet wird → Revision nötig!

---

## Spezialfälle

### Passthrough-Configs
`surrealizer`, `split_and_combine`, `partial_elimination` haben leere/minimale Contexts - DAS IST ABSICHT! Sie leiten Prompts direkt an spezielle Workflows weiter.

### User-Defined
`user_defined` hat leeren Context - DAS IST ABSICHT! User gibt eigene Regeln über UI ein.

### LORA-Trigger
Configs wie `cooked_negatives` müssen einen Trigger-Term enthalten (z.B. "cooked negatives"), um das LORA zu aktivieren.

---

*Diese Zusammenfassung basiert auf dem ausführlichen Dokument `docs/STAGE2_PROMPT_QUALITY_CRITERIA.md`*
