# Stage2 Interception Prompt Quality Criteria

**Version:** 2026-01-25
**Purpose:** Framework for evaluating and designing Stage2 pedagogical transformation prompts

---

## 1. Core Principles

### 1.1 The WAS/WIE Principle (What/How Separation)

Stage2 Interception implements the fundamental WAS/WIE principle:

- **WAS (What):** The user's input - the core idea or image
- **WIE (How):** The `config.context` - the transformation rules

The LLM is framed as a **Co-Akteur** (co-actor), not a tool. It:
- Interprets user input according to explicit rules
- Applies transformation framework consistently
- Adds its own "handwriting" through interpretive choices
- Produces results that are collaborative, not mechanical

### 1.2 Pedagogical Purpose

Stage2 prompts are NOT about:
- Making "better" prompts
- Optimizing for model efficiency
- Automating prompt engineering

Stage2 prompts ARE about:
- **Making visible** how rules transform ideas
- **Making editable** - students can intervene at every step
- **Making comparable** - different rules on same idea
- **Making criticalizable** - students discuss transformation choices

---

## 2. The manipulate.json Template Structure

All Stage2 prompts work within this proven 3-part template:

```
Task:
{{TASK_INSTRUCTION}}    // Generic: HOW to transform (from instruction_selector.py)

Context:
{{CONTEXT}}             // Specific: WHAT rules to apply (from config.context)

Important: Respond in the same language as the input prompt below.

Prompt:
{{INPUT_TEXT}}          // User's original text
```

**Design Implications for config.context:**
- Assume TASK_INSTRUCTION already says "transform according to these rules"
- DO NOT repeat "Your task is to transform..." (redundant)
- Directly describe the transformation framework
- Be self-contained (don't rely on external documents)

---

## 3. Quality Criteria Framework

### 3.1 Content Quality (Weight: 40%)

| Criterion | Gold Standard | Red Flag |
|-----------|---------------|----------|
| **Perspective-Taking** | "DU BIST eine Künstlerin der 1870er Jahre" | "Generate in vintage style" |
| **Process Description** | Clear numbered steps/phases | Only outcome description |
| **Transformation Rules** | Concrete operations with examples | Vague aesthetic labels |
| **Cultural Specificity** | Conceptual principles, not surface style | "Japanese art style" |
| **No Artist Names** | "ES IST DIR VERBOTEN... 'im Stil von'" | "in the style of Monet" |
| **Bilingual Parity** | Both EN/DE are primary texts | One is translation of other |

### 3.2 Structural Quality (Weight: 30%)

| Criterion | Gold Standard | Red Flag |
|-----------|---------------|----------|
| **Role Identity** | "Du bist... Du lebst in..." | No clear perspective |
| **Instruction Clarity** | Action verbs: "Reduziere, Analysiere" | Vague: "Consider, Maybe" |
| **Prohibitions** | Specific: "VERBOTEN: romantisierende Begriffe" | Generic: "Don't be flowery" |
| **Output Format** | "Ein Absatz, 120-180 Wörter" | Unspecified length |
| **Meta-Prohibition** | "NO meta-commentary ('I will...')" | Missing |
| **Appropriate Length** | 150-800 words depending on complexity | Too brief (<50) or bloated |

### 3.3 Model Appropriateness (Weight: 15%)

| Model Family | Optimal Structure |
|--------------|-------------------|
| **Llama** | Example-heavy, flat, concrete anchors, role-play framing |
| **Mistral** | Minimal, precise, short imperative sentences, explicit rules |
| **Claude/OpenAI** | Hierarchical sections, both principles AND rules, nuanced |

### 3.4 Pedagogical Consistency (Weight: 15%)

| Criterion | Description |
|-----------|-------------|
| **WAS/WIE Separation** | Rules apply to ANY input, not tied to specific content |
| **Co-Akteur Space** | Room for LLM interpretation within framework |
| **Transformation Visibility** | Output shows connection to rules, discussable |
| **Student Editability** | Output can be modified without breaking style |

---

## 4. Red Flags (Automatic Revision Required)

Any of these issues requires immediate revision:

| Red Flag | Example | Fix |
|----------|---------|-----|
| **Placeholder Text** | "professional translator" | Write actual transformation rules |
| **Artist Name as Style** | "in the style of Dalí" | Describe the principles/perspective |
| **Empty Context** | `"context": {"en": "", "de": ""}` | Add complete framework |
| **Meta-Commentary Enabled** | No prohibition of "I will..." | Add explicit prohibition |
| **Optimization Framing** | "Make better", "Optimize" | Use "Transform according to..." |
| **Single Language Only** | Missing DE or EN version | Add full bilingual support |
| **Unspecified Output** | No word count or format | Add "Ein Absatz, X-Y Wörter" |

---

## 5. Scoring System (0-3)

| Score | Status | Definition |
|-------|--------|------------|
| **3** | Excellent | Clear methodology, specific rules, examples, prohibitions, output format |
| **2.5** | Good | Functional with minor improvements possible |
| **2** | Acceptable | Works but needs structural improvements |
| **1.5** | Needs Work | Major gaps in methodology or clarity |
| **1** | Poor | Missing key elements, unclear transformation |
| **0** | Critical | Placeholder text, no guidance, broken |

---

## 6. Gold Standard Examples

### 6.1 Photography/Technical: `analog_photography_1870s.json`

**Score: 3/3**

Key Features:
- Clear role identity: "Du bist eine professionelle Fotografin und Künstlerin. Du lebst in den 1870er Jahren."
- Material constraints: specific equipment, processes, materials
- Comprehensive prohibitions: "VERBOTEN: romantisierende Begriffe, 'im Stil von [Fotografenname]', digitale Terminologie"
- Output format: "Ein Absatz, 120-180 Wörter"
- Required structure: "Der Input wird stets zuerst genannt in der Form..."

### 6.2 Art-Historical: `bauhaus.json`

**Score: 3/3**

Key Features:
- 4-step methodology: Analysis → Functionalism → Geometric Reduction → Material/Color
- Perspective-taking prohibition: "ES IST DIR VERBOTEN DEN STIL... 'Im Stil von'"
- Specific transformations: "Vase → funktionaler Prototyp für einen zylindrischen Behälter"
- Clear prohibitions: "Verboten sind jegliche romantische, naturalistische oder ornamentale Sprache"

### 6.3 Critical Thinking: `planetarizer.json`

**Score: 3/3**

Key Features:
- Clear framework: Anthropocene thinking, planetary perspective
- Specific prohibitions: "Jede Form von Othering, Exotisierung, Romantisierung... ist STRIKT untersagt"
- Named theoretical basis: "Frantz Fanon, Homi Bhabha, Gayatri Spivak, Walter Mignolo"
- Actionable rules: "normalisierte Konsumwelt-Bezüge umgeschrieben werden zu einer planetar... orientierten Perspektive"

---

## 7. Common Anti-Patterns

| Anti-Pattern | Why Problematic | Solution |
|--------------|-----------------|----------|
| "Professional translator/expert" | Zero guidance | Write actual transformation rules |
| "Be creative" | Unactionable | Describe what creativity means in this context |
| Wikipedia mode | Explains instead of transforms | Focus on transformation, not explanation |
| Surface aesthetics | "Make it look X" | Describe the perspective/methodology |
| Over-specification | No room for LLM interpretation | Balance rules with interpretive space |

---

## 8. Revision Workflow

### 8.1 Triage

1. **Check for Red Flags** → Fix immediately if any found
2. **Score with Rubric** → Calculate weighted score
3. **Prioritize:**
   - Score < 1.0: Critical - immediate revision
   - Score 1.0-2.0: High priority
   - Score 2.0-2.5: Medium priority
   - Score > 2.5: Low priority polish

### 8.2 Revision Steps

1. Identify specific issues using this framework
2. Reference similar excellent configs for patterns
3. Draft revision maintaining bilingual parity
4. Test with target model(s)
5. Verify pedagogical alignment (WAS/WIE, visibility, editability)
6. Re-score with rubric

---

## 9. Special Cases

### 9.1 Passthrough Configs (skip_stage2: true)

Some configs skip Stage2 interception by design:
- `surrealizer.json` - ComfyUI vector manipulation
- `split_and_combine.json` - Prompt splitting research
- `partial_elimination.json` - Dimension elimination research

These are NOT broken - they pass prompts directly to specialized workflows.

### 9.2 User-Defined Config

`user_defined.json` has empty context BY DESIGN:
- User provides their own rules via UI
- Empty context is intentional, not a bug

### 9.3 LORA-Trigger Configs

Configs like `cooked_negatives.json` primarily inject trigger terms:
- Must include trigger term instruction: "Aktiviere ein entsprechendes LORA indem DU den Trigger Term 'X' verwendest"
- Can be brief if LORA handles the aesthetic

---

## 10. Documentation Integration

This framework should be used for:
1. **Quality Review** - Evaluating existing prompts
2. **New Prompt Design** - Creating new interception configs
3. **Workshop Training** - Teaching prompt design principles
4. **Trashy Integration** - Simplified version for AI assistant

---

*Last Updated: 2026-01-25*
*Author: AI4ArtsEd DevServer Documentation*
