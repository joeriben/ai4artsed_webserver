# Evolution der Instruction-Prompts für künstlerische/kulturelle Interceptions

**Zeitraum:** 22. Juni 2025 - 07. September 2025 (77 Tage)
**Anzahl Versionen:** 4 identifizierte Entwicklungsstufen

---

## 📊 Entwicklungskurve

```
Komplexität
    │
    │ ████████████                                  VERSION 1 (Dada)
    │ ████████████████████                          VERSION 2 (Expressionism)
    │ ████████████████████████                      VERSION 3 (Renaissance)
    │ ████                                          VERSION 4 (AKTUELL)
    │
    └────────────────────────────────────────────> Zeit
      Juni                              September
```

**Trend:** Von maximaler technischer Spezifikation zur minimalistischen Konzept-Orientierung

---

## VERSION 1: Dada (22.06.2025)

**Länge:** ~550 Wörter
**Charakteristik:** Technische Mikro-Kontrolle

### Kernelemente:
- ✅ Strikte **55-Wörter-Grenze** (absolut)
- ✅ Explizite **Token-Limit-Erwähnung** (SD 3.5, clip_g, t5xxlenc)
- ✅ Detaillierte **Output-Formatierung**
- ✅ "Be verbose!" (Widerspruch zum Limit!)
- ✅ Verbot von Meta-Terms

### Vollständiger Text:
```
You received two inputs: 1) the input_prompt and 2) the input_context.

Transform the input_prompt into an image description according to the instructions
defined in the input_context. Explicitely communicate the input_context as cultural
cf. artistic. cf intervening context. Also communicate genres/artistic traditions in
a concrete way (i.e. is it a dance, a photo, a painting, a song, a movie, a statue/
sculpture? how should it be translated into an image?)

This is not a linguistic translation, but a aesthetic, semantic and structural
transformation. Be verbose!

Reconstruct all entities and their relations as specified, ensuring that:
- Each entity is retained – or respectively transformed – as instructed.
- Each relation is altered in line with the particular aesthetics, genre-typical
  traits, and logic of the "Context". Be explicit about visual aesthetics in terms
  of materials, techniques, composition, and overall atmosphere. Mention the
  input_context als cultural, cf. artistic, c.f intervening context in your OUTPUT
  explicitely.

Output only the transformed description as plain descriptive text. Be aware if the
output is something depicted (like a ritual or any situation) OR itself a cultural
artefact (such as a specific drawing technique). Describe accordingly. In your
output, communicate which elements are most important for an succeeding image
generation.

Create an output prompt tailored for Stable Diffusion 3.5 with combined clip_g and
t5xxlenc. Regard the Token Limit (75), OUPUT max. 55 Words!
DO NOT USE ANY META-TERMS, JUST THE INSTRUCTIONS FOR IMAGE GENERATION! Do not
explain your reasoning.
```

---

## VERSION 2: Expressionism (05.09.2025)

**Länge:** ~650 Wörter
**Charakteristik:** Anti-Cliché-Regeln hinzugefügt

### Neu hinzugefügt:
- ✅ **Token-Flexibilität:** "55 Words + bis zu 300 für Details"
- ✅ **Anti-Referenz-Regeln:** "Never output artist names, movements, museums, dates"
- ✅ **Prozedural-Fokus:** "Use only procedural, material, and compositional language"

### Änderung:
```diff
- Regard the Token Limit (75), OUPUT max. 55 Words!
+ Regard the Token Limit: max. 55 Words for the core of the prompt.
+ You may use up to 300 words to be more verbose, but everything important
+ must fit into the 55 words limit.
+
+ Never output or allude to any artist, movement, museum, date, or 'in the
+ style of'. Use only procedural, material, and compositional language.
+ If a proper name is generated, replace it with a neutral procedural term.
```

---

## VERSION 3: Renaissance (06.09.2025)

**Länge:** ~750 Wörter
**Charakteristik:** Anti-Meta-Sprache verschärft

### Neu hinzugefügt:
- ✅ **Anti-Symbolik:** "Never say something 'represents' or 'demonstrates'"
- ✅ **Direkte Visualität:** "Provide the visual translation yourself"
- ✅ **Nicht-Direktiv:** "You are not talking to a person, purely describe"
- ✅ **Struktur-Klarheit:** "Begin with 55 words, append the rest"

### Änderung:
```diff
  This is not a linguistic translation, but a aesthetic, semantic and
- structural transformation. Be verbose!
+ structural transformation. Be verbose! Provide the visual translation
+ yourself. Never leave it to someone else, i.e. never say something
+ "represents" or "demonstrates" something: always think and make clear
+ what this should visually mean. Describe then what you mean.

+ Output only the transformed description as plain descriptive text.
+ You are not talking to a person. you are not telling anyone what to do.
+ YOu purely and simply describe an image/scene.

+ NEVER tell "what the image should show" or what someone "should do".
+ Just describe an image as pure description.
```

---

## VERSION 4 (AKTUELL): Confucian/Yoruba/Bauhaus (07.09.2025)

**Länge:** ~320 Wörter (-57% gegenüber V3!)
**Charakteristik:** Radikale Vereinfachung

### Entfernt:
- ❌ Alle Wortzahl-Limits
- ❌ Token-Limit-Erwähnungen
- ❌ SD 3.5 Spezifikationen
- ❌ Anti-Referenz-Regeln
- ❌ Meta-Sprache-Verbote
- ❌ Strukturierungs-Anweisungen
- ❌ "Be verbose!"
- ❌ "Do not explain your reasoning"

### Hinzugefügt:
- ✅ "cosmologic" (kulturelle Erweiterung)

### Vollständiger Text:
```
You received two inputs: 1) the input_prompt and 2) the input_context.

Transform the input_prompt into an image description according to the instructions
defined in the input_context. Explicitely transform the input_context as cultural
cf. artistic. cf intervening context. Also transform genres/artistic traditions in
a concrete way (i.e. is it a dance, a photo, a painting, a song, a movie, a statue/
sculpture? how should it be translated into an image?)

This is not a linguistic translation, but a cultural, aesthetic, cosmologic.
semantic and structural transformation.

Reconstruct all entities and their relations as specified, ensuring that:
- Each entity is retained – or respectively transformed – as instructed.
- Each relation is altered in line with the particular aesthetics, genre-typical
  traits, and logic of the "Context". Be explicit about visual traits aesthetics
  in terms of materials, techniques, composition, and overall atmosphere. Mention
  the input_context als cultural, cf. artistic, c.f intervening context in your
  OUTPUT explicitely.
```

---

## 🔍 Erkenntnisse

### 1. Paradigmenwechsel

| Phase | Kontrolle liegt bei | Fokus |
|-------|---------------------|--------|
| V1 (Juni) | Instruction-Prompt | Technische Output-Spezifikation |
| V2-V3 (Anfang Sept) | Instruction-Prompt | Anti-Cliché, Anti-Meta |
| V4 (Mitte Sept) | **Context-Prompt** | Kulturelle Transformation |

### 2. Von "Wie sag es?" zu "Was sag es?"

**Früher (V1-V3):** Micro-Management der Formulierung
- "Maximal 55 Wörter"
- "Sag nicht 'represents'"
- "Erwähne keine Künstler"
- "Strukturiere so: Erst X, dann Y"

**Jetzt (V4):** Vertrauen in die kulturelle Logik des Context
- Keine technischen Limits
- Keine Sprach-Verbote
- Fokus auf "cosmologic/cultural/aesthetic transformation"

### 3. Die Arbeit wandert in den Context-Prompt

**Beispiel Yoruba Heritage:**

Der Context-Prompt enthält jetzt:
- 3.500+ Wörter detaillierte kulturelle Regeln
- Ritual-Kontextualisierung
- Rollen-Definitionen
- Temporale Rahmen
- Materielle Symbolik
- Ethische Textur
- Negative-Prompt-Verbote (innerhalb des Contexts!)

Der Instruction-Prompt sagt nur noch:
- "Transform according to context"
- "Be explicit about visual traits"

---

## 💡 Fazit

**Die Evolution zeigt eine Reifung des Systems:**

1. **Phase 1 (Juni):** "Ich muss dem LLM genau sagen, WIE es formulieren soll"
   - Resultat: Rigide, widersprüchliche Regeln

2. **Phase 2 (Anfang September):** "Ich muss verhindern, dass das LLM Fehler macht"
   - Resultat: Defensive, verbots-basierte Prompts

3. **Phase 3 (Mitte September):** "Ich beschreibe die kulturelle Logik präzise, das LLM findet die Form"
   - Resultat: Konzeptuelle Klarheit, systemisches Vertrauen

**Der aktuelle Stand (V4) ist:**
- ✅ Minimalistisch (320 Wörter statt 750)
- ✅ Konzeptuell (cultural/aesthetic/cosmologic)
- ✅ Vertrauensvoll (keine Mikro-Kontrolle)
- ✅ Flexibel (keine starren Limits)

**Die eigentliche Intelligenz steckt jetzt im Context-Prompt**, der die kulturelle/künstlerische Logik ausführlich definiert. Der Instruction-Prompt ist nur noch der "Startbefehl".
