# Stage2 Interception Prompt Review

**Date:** 2026-01-25
**Reviewer:** Claude Code (Session 136)
**Total Configs:** 29 (24 active, 5 system/passthrough)

---

> **⚠️ Critical Note (Added 2026-01-25):**
>
> This document's analysis and especially the "Proposed Rewrites" section should be treated with caution. The review approach was mechanistic and checklist-based, which may not capture actual pedagogical effectiveness. Specific concerns:
>
> - **The proposed rewrites have NOT been tested** in real workshop conditions
> - Some rewrites may be **overcomplicated** (e.g., overdrive's guitar metaphor may confuse the LLM)
> - Some may reflect **eurocentric assumptions** (e.g., tellastory's narrative structure)
> - Scores are **structural assessments**, not measures of practical performance
>
> **Before implementing any rewrite:** Test the *current* prompt first. If it works well in practice, structural "improvements" may be unnecessary or harmful. Practical workshop feedback should take priority over structural completeness.

---

## Executive Summary

| Category | Count |
|----------|-------|
| Excellent (Score 3) | 13 |
| Good (Score 2-2.5) | 6 |
| Needs Improvement (Score 1-1.5) | 3 |
| Passthrough/System (N/A) | 5 |
| By Design Empty | 1 |
| **Deprecated/Broken** | **1** |

**Key Finding:** Most configs are now in good shape. The November 2025 critical issues (placeholder texts) have been largely addressed. Main remaining issues are:
1. `overdrive.json` - Too brief, no methodology
2. `tellastory.json` - Generic, needs narrative methodology
3. `cooked_negatives.json` - Very brief, relies solely on LORA
4. `hunkydoryharmonizer.json` - Content mismatch (safety vs harmonization)

---

## Detailed Analysis Table

### EXCELLENT (Score 3)

| Config | Name | Analysis | Status |
|--------|------|----------|--------|
| `analog_photography_1870s.json` | Daguerreotype | **Gold Standard.** Role identity, material constraints, comprehensive prohibitions, output format. Complete bilingual parity. | No change |
| `analog_photography_1970s.json` | Analog 1970s | Same quality as 1870s. Leica M4, Kodachrome, darkroom processes. Full methodology. | No change |
| `bauhaus.json` | Rationa/Bauhaus | Rigorous 4-step methodology. Strong perspective-taking prohibition. Geometric reduction rules with examples. | No change |
| `confucianliterati.json` | Literati | Extremely detailed cultural framework. 7 sections with specific rules, percentages (30% Analects, 40% liubai). Advanced. | No change |
| `renaissance.json` | Renaissance | Clear humanistic methodology. Artform selection (painting/sculpture/architecture). Mathematical principles without naming them. | No change |
| `technicaldrawing.json` | Technical | Clear 4-rule transformation. Good examples (embrace → interlocking). Strong negative prompting directive. | No change |
| `clichéfilter_v2.json` | De-Kitsch | **Fixed since Nov 2025.** Now comprehensive 4-step cliché identification and reconstruction methodology. | No change |
| `planetarizer.json` | Planetarizer | Clear decolonial framework. Specific prohibitions (Othering, Orientalism). Named theorists. Actionable rules. | No change |
| `one_world.json` | One World | Similar to Planetarizer. Postcolonial thinking with named theorists. Clear bias deconstruction rules. | No change |
| `jugendsprache.json` | Slang | Comprehensive vocabulary lists. Clear target audience. Different slang for EN (UK Drill/Grime) vs DE (German urban). | No change |
| `piglatin.json` | Word Game | Complete algorithmic rules with examples. Different game for DE (Hühnersprache). Clever meta-instruction. | No change |
| `stillepost.json` | Telephone | Clean translation rules. Uses `{{TARGET_LANGUAGE}}` placeholder. Proper recursive pipeline. | No change |
| `p5js_simplifier.json` | Listifier | Excellent layered structure with examples. Clear HINTERGRUND/MITTELGRUND/VORDERGRUND format. | No change |

### GOOD (Score 2-2.5)

| Config | Name | Score | Analysis | Revision Suggestion |
|--------|------|-------|----------|---------------------|
| `digital_photography.json` | Digital Photo | 2.5 | Good iPhone 3 material constraints. Clear era-specific artefacts. | Minor: Consider stronger role identity |
| `analogue_copy.json` | Analogue Copy | 2.5 | Detailed generational loss description. Good material focus. | Minor: Add specific examples |
| `forceful.json` | Forceful | 2.5 | Clear attitudinal stance. Multi-sensory output (visual, sonic, performative). | Minor: Add concrete examples of "Zuspitzung" |
| `sensitive.json` | Sensitive | 2.5 | Good relational/process focus. Clear "in-between" methodology. | Minor: Add examples of "Kippen" |
| `mad_world.json` | Mad World | 2.5 | Good absurdist framework. Historical reference to Dada without forcing style. | Minor: Could add more concrete operations |
| `theopposite.json` | On the Contrary | 2.5 | **Improved since Nov 2025.** Now has categorized examples (spatial, visual, emotional, etc.). | Minor: Add edge case handling |

### NEEDS IMPROVEMENT (Score 1-1.5)

| Config | Name | Score | Analysis | Revision Needed |
|--------|------|-------|----------|-----------------|
| `overdrive.json` | Amplifier | 1.5 | **Too brief** (2 sentences). No methodology, no dimensions, no examples. Just "übertreibe maßlos". | **MAJOR: See rewrite below** |
| `tellastory.json` | Your Story | 1.5 | Very generic storytelling instruction. No narrative structure, no methodology. | **MAJOR: See rewrite below** |
| `cooked_negatives.json` | Cooked Negatives | 1.5 | Relies almost entirely on LORA trigger. No visual/aesthetic description. | **MEDIUM: Add aesthetic description** |

### CONTENT MISMATCH (Needs Review)

| Config | Name | Score | Issue |
|--------|------|-------|-------|
| `hunkydoryharmonizer.json` | Sweetener | 2 | **Mismatch:** Name/description say "harmonious and cute" but context describes **child-safety moderation** (avoid horror, dark fantasy). Two different purposes conflated. | **Decision needed:** Is this a harmonizer or a safety filter? |

### PASSTHROUGH/SYSTEM (Score N/A)

| Config | Name | Analysis |
|--------|------|----------|
| `surrealizer.json` | Surrealizer | `skip_stage2: true` - Passes to ComfyUI T5-CLIP workflow. By design. |
| `split_and_combine.json` | Split & Combine | `skip_stage2: true` - Vector manipulation research. By design. |
| `partial_elimination.json` | Partial Elimination | `skip_stage2: true` - Dimension elimination research. By design. |
| `image_transformation.json` | Image Transformation | System config, hidden. By design. |
| `multi_image_transformation.json` | Multi-Image | System config, hidden. By design. |

### BY DESIGN EMPTY

| Config | Name | Analysis |
|--------|------|----------|
| `user_defined.json` | Your Call | Empty context BY DESIGN - user provides rules via UI. |

---

## Proposed Rewrites

> **⚠️ These rewrites are UNTESTED DRAFTS.** They were generated through structural analysis without real-world validation. Before implementing:
> 1. Test the **current** prompt to understand how it actually performs
> 2. If there are real problems, consider whether these drafts address them
> 3. Any rewrite should be tested with target models before deployment
>
> Some of these proposals may be overcomplicated, culturally biased, or simply worse than the originals.

### 1. overdrive.json - MAJOR REVISION

**Current (Score 1.5):**
```
"Deine Gabe ist es, den Inhalt der Eingabe maßlos zu übertreiben. DU BIST DER OVERDRIVE, der alles bis zur grotesken Grenze und darüber hinaus bis zur Verzerrung verstärkt. Übertreibe in jeder Hinsicht, geh über die Stränge, gib an, mach alles groß!"
```

**Proposed (Score 3):**
```
DU BIST DER OVERDRIVE. Deine Aufgabe ist systematische Übertreibung und Amplifikation – inspiriert vom gleichnamigen Gitarreneffekt, der das Signal an die Verzerrungsgrenze und darüber hinaus treibt.

AMPLIFIKATIONS-DIMENSIONEN (wende alle an):
1. SKALA: Vergrößere alle Größenangaben um mindestens eine Größenordnung. Ein Hund wird zum Hund von der Größe eines Hauses. Eine Stadt wird zur Megalopolis.
2. INTENSITÄT: Steigere alle Qualitäten ins Extreme. Warm wird glühend heiß. Leise wird ohrenbetäubend laut. Sanft wird brutal zart.
3. KONTRAST: Verstärke alle Gegensätze. Hell/Dunkel, Groß/Klein, Schnell/Langsam – die Spannung zwischen ihnen wird maximal.
4. DICHTE: Multipliziere Mengen. Einer wird zu Hunderten. Einige werden zu Tausenden. Die Szene überquillt.
5. EMOTION: Steigere emotionale Valenz. Freude wird Ekstase. Trauer wird Verzweiflung. Ruhe wird erhabene Stille.

TRANSFORMATION:
- Erhalte die Grundstruktur und Entitäten des Inputs
- Übertreibe JEDES Element systematisch
- Das Ergebnis soll an der Grenze zum Absurden sein, aber noch kohärent
- Beschreibe das übertriebene Szenario in einem Absatz, 100-150 Wörter

VERBOTEN: Understatement, Mäßigung, "ein bisschen", "etwas", "relativ"
```

---

### 2. tellastory.json - MAJOR REVISION

**Current (Score 1.5):**
```
"Du bist ein Geschichtenerzähler. Du hast den INPUT als Anregung erhalten. Du versuchst, aus dem Input eine kurze Geschichte zu machen, die sowohl die Inhalte ALS AUCH die Form und die Emotionalität des Inputs aufgreift und als Inspiration verwendet."
```

**Proposed (Score 3):**
```
DU BIST EIN GESCHICHTENERZÄHLER. Der Input ist dein Ausgangspunkt für eine kurze Erzählung, die visuell beschrieben wird – als würdest du die Schlüsselszene für eine Bildgenerierung vorbereiten.

NARRATIVE STRUKTUR:
1. SETTING: Etabliere Ort und Atmosphäre basierend auf dem Input
2. FIGUR: Identifiziere oder erschaffe eine zentrale Figur mit sichtbarer Haltung/Emotion
3. MOMENT: Wähle einen spannungsgeladenen oder emotionalen Augenblick
4. DETAIL: Füge ein spezifisches visuelles Detail hinzu, das die Geschichte verdichtet

TRANSFORMATION:
- Extrahiere das emotionale Potenzial aus dem Input
- Verwandle abstrakte Begriffe in konkrete szenische Bilder
- Fokussiere auf EINEN Moment, nicht auf eine ganze Handlung
- Beschreibe die Szene so, dass sie als einzelnes Bild funktioniert

OUTPUT:
Ein Absatz, 80-120 Wörter. Beschreibe die Szene visuell und atmosphärisch. Keine Handlungssequenzen, sondern ein eingefrorener erzählerischer Moment.

VERBOTEN: Meta-Kommentare ("Diese Geschichte handelt von..."), Zusammenfassungen, abstrakte Erklärungen
```

---

### 3. cooked_negatives.json - MEDIUM REVISION

**Current (Score 1.5):**
```
"Du arbeitest mit künstlerisch-destruktiven analogen Film-Techniken. Deine Bilderzeugung ist durch die physische Veränderung und Zersetzung des Negativfilms durch Kochen vor der Filmentwicklung geprägt. Du aktivierst ein entsprechendes LORA indem DU den Trigger Term 'cooked negatives' in Deinem Output verwendest. Ein Absatz, 120–180 Wörter"
```

**Proposed (Score 2.5):**
```
Du arbeitest mit künstlerisch-destruktiven analogen Film-Techniken. Das Kochen von Filmnegativen vor der Entwicklung erzeugt unvorhersehbare Veränderungen: Emulsionsverlauf, Farbverschiebungen, Blasenbildung, partielle Auflösung der Silberschicht, organische Muster durch Hitzeeinwirkung.

VISUELLE EIGENSCHAFTEN:
- Verlaufende, ineinanderfließende Farben
- Organische Blasen- und Rissstrukturen
- Teilweise aufgelöste Konturen
- Unvorhersehbare Farbstiche (oft warm: Orange, Magenta)
- Textur zwischen flüssig und kristallin

TRANSFORMATION:
Denke den Input als durch diesen destruktiven Prozess gegangen. Beschreibe das Bild so, als ob es die Spuren des Kochens trägt – nicht als Effekt, sondern als materielle Realität.

OUTPUT:
Ein Absatz, 120-180 Wörter. Du MUSST den Trigger-Term 'cooked negatives' in deinem Output verwenden, um das entsprechende LORA zu aktivieren.
```

---

### 4. hunkydoryharmonizer.json - CLARIFICATION NEEDED

**Issue:** The config conflates two different purposes:
- **Name/Description:** "Makes everything harmonious and cute"
- **Context:** Child-safety moderation (avoid horror, dark fantasy)

**Options:**

**Option A: Make it a true Harmonizer**
```
DU BIST DER HARMONISIERER. Deine Aufgabe ist es, den Input in eine sanfte, ausgewogene, ästhetisch angenehme Version zu transformieren.

HARMONISIERUNGS-PRINZIPIEN:
1. FORMEN: Scharfe Kanten werden weich und gerundet
2. FARBEN: Kontraste werden gedämpft, Pastelltöne bevorzugt
3. PROPORTIONEN: Alles wird leicht verniedlicht (größere Augen, kürzere Proportionen)
4. ATMOSPHÄRE: Warm, einladend, beruhigend
5. BEZIEHUNGEN: Freundlich, kooperativ, harmonisch

TRANSFORMATION:
Erhalte den Kerninhalt des Inputs, aber transformiere alle ästhetischen Qualitäten in Richtung Harmonie und Niedlichkeit. Das Ergebnis soll sich "wohlig" anfühlen.

Ein Absatz, 80-120 Wörter.
```

**Option B: Rename to "SafeGuard" and keep current content**

The current content is actually a **child-safety filter**, not a harmonizer. Consider renaming to make purpose clear.

---

## Priority List

### CRITICAL (Immediate)
1. `overdrive.json` - Apply proposed rewrite

### HIGH (This Sprint)
2. `tellastory.json` - Apply proposed rewrite
3. `hunkydoryharmonizer.json` - Decide purpose, then revise

### MEDIUM (Backlog)
4. `cooked_negatives.json` - Apply proposed rewrite
5. `forceful.json` - Add concrete examples
6. `sensitive.json` - Add concrete examples
7. `mad_world.json` - Add concrete operations

### LOW (Polish)
8. `theopposite.json` - Add edge case handling
9. `digital_photography.json` - Strengthen role identity
10. `analogue_copy.json` - Add specific examples

---

## Verification

After revisions:
1. Test each revised prompt with sample inputs
2. Compare outputs across model families (Llama, Mistral, Claude)
3. Verify pedagogical alignment (transformation visible, editable)
4. Update this document with results

---

*Analysis completed: 2026-01-25*
