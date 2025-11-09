# DEACTIVATED CONFIGS ANALYSIS
**Date:** 2025-11-08
**Total Configs:** 14
**Purpose:** Review of deactivated configs for potential reactivation or permanent retirement

---

## 1. image_comparison (SD3.5 vs GPT-5)

**Current Properties:** algorithmic, facts, contemporary, explore, serious

**Status:** DEACTIVATED (likely for technical/cost reasons, not quality)

### Property Analysis

**chill:** N/A (not assigned)

**chaotic:** N/A (not assigned)

**narrative:** N/A (not assigned)

**algorithmic:** ✅ KEEP
Model comparison is a systematic process of parallel execution and output analysis.

**facts:** ✅ KEEP
Comparing model outputs is factual analysis, not emotional interpretation.

**emotion:** N/A (not assigned)

**historical:** N/A (not assigned)

**contemporary:** ✅ KEEP
Model comparison is a contemporary AI literacy practice.

**explore:** ✅ KEEP
Helps users explore how different AI systems interpret the same prompt - pedagogically exploratory.

**create:** N/A (not assigned, correctly - this is comparative analysis, not primary creation)

**playful:** N/A (not assigned)

**serious:** ✅ KEEP
Understanding model differences is serious AI literacy work.

**RECOMMENDED CHANGES:**
- None - properties are well-assigned

---

### Context Prompt Quality
**Status:** ✅ GOOD (for a passthrough config)
**Legacy Comparison:** Not found (appears to be new config)
**Issues:** None

**Analysis:** The context "Pass on the input text unchanged. Do not modify, enhance, or transform the prompt in any way. Return it exactly as provided." is appropriate for a comparison config. The pedagogical value comes from the side-by-side outputs, not prompt transformation. The `media_preferences` field correctly specifies dual output: `["sd35_large", "gpt5_image"]`.

---

### Description Quality
**Status:** ✅ EXCELLENT
**Issues:** None

**Analysis:** "Creates the same image with two different AI models side-by-side. Helps you compare how different systems interpret your prompt." - This is pedagogically perfect. It clearly explains the comparison process and educational value.

---

### Metadata
**age (min_age):** 12 - ✅ APPROPRIATE
**Consistency:** ✅ EXCELLENT

---

### Reactivation Recommendation
**Status:** ⚠️ CONSIDER REACTIVATION (with cost warnings)

**Reasoning:** This is pedagogically valuable for teaching AI literacy and model differences. However, it requires both SD3.5 (local/free) and GPT-5 Image (cloud/paid), which has cost implications. Recommend reactivating with:
1. Clear cost warnings in UI
2. eco mode option (SD3.5 vs Flux1 Dev - both local)
3. Educational framing about why models differ

---

## 2. quantumtheory

**Current Properties:** chaotic, narrative, facts, contemporary, explore, playful

**Status:** DEACTIVATED (likely for complexity/accessibility)

### Property Analysis

**chill:** N/A (not assigned)

**chaotic:** ⚠️ QUESTIONABLE
Quantum mechanics is probabilistic and weird, but the *language* of quantum field theory is highly structured and technical. The transformation creates strange descriptions, but follows rigorous scientific terminology. This might be "chaotic" in outcome, but not in process.

**narrative:** ❌ REMOVE
The context explicitly forbids narrative: "Do not use metaphors like 'resembling' or 'representing.'" Quantum field theory descriptions are not stories - they're scientific redescriptions.

**algorithmic:** ✅ ADD
The context provides "Transformation Rules" for systematic reconceptualization. This is algorithmic translation from macroscopic to quantum framework.

**facts:** ✅ KEEP
Quantum physics is factual scientific description, even when counterintuitive. The context demands "clinical, scientific tone."

**emotion:** N/A (not assigned)

**historical:** N/A (not assigned, though quantum theory developed 1920s-1960s)

**contemporary:** ✅ KEEP
Quantum field theory is contemporary physics (ongoing research), even though quantum mechanics began in 1920s.

**explore:** ✅ KEEP
Helps users explore scientific reconceptualization and the strangeness of quantum descriptions.

**create:** N/A (not assigned)

**playful:** ❌ REMOVE
The context demands "clinical, scientific tone" and "no explanations." This is not playful - it's rigorous scientific redescription. While results might seem absurd, the pedagogical frame is serious.

**serious:** ✅ ADD
Scientific reconceptualization and quantum thinking are serious pedagogical work.

**RECOMMENDED CHANGES:**
- REMOVE: narrative (forbids metaphor and storytelling)
- REMOVE: chaotic (structured scientific language)  OR KEEP and clarify
- REMOVE: playful (rigorous scientific frame)
- ADD: algorithmic (follows transformation rules)
- ADD: serious (scientific pedagogy)

**Revised Properties:** facts, contemporary, algorithmic, explore, serious (and possibly chill or chaotic depending on interpretation)

---

### Context Prompt Quality
**Status:** ✅ GOOD
**Legacy Comparison:** Found at workflows_legacy/aesthetics/ai4artsed_QuantumTheory_2509071919.json
**Issues:** None significant

**Analysis:** The context is sophisticated and pedagogically strong. It provides clear transformation rules (re-conceptualize macroscopic objects, re-interpret light/environment, shift to probabilistic interactions) with specific terminology ('localized concentration of field excitations', 'fermion-boson system'). The negative prompting effectively prevents macroscopic language. This teaches scientific reconceptualization rigorously. However, it's very advanced - potentially too difficult for most users.

---

### Description Quality
**Status:** ✅ GOOD
**Issues:** Very advanced for age 12+

**Analysis:** "Translates everything into quantum physics language. Trees become field excitations, sunlight becomes photon flux, and everything is described as energy states and particle interactions." - Accurate and clear, though the concepts are genuinely difficult.

---

### Metadata
**age (min_age):** 12 - ⚠️ TOO LOW (should be 16+ or adult)
**Complexity:** expert - ✅ CORRECT

---

### Deactivation Reasoning & Recommendation
**Status:** ⚠️ KEEP DEACTIVATED (too advanced for target audience)

**Reasoning:** While pedagogically sophisticated, quantum field theory is genuinely difficult. Most users (including many adults) lack the physics background to appreciate or learn from this transformation. The outputs would be incomprehensible without quantum mechanics knowledge. This is "too clever" for a general educational tool.

**Alternative:** Consider simpler "Scientific Description" config that uses biology or chemistry language instead of quantum physics.

---

## 3. yorubaheritage

**Current Properties:** chill, narrative, emotion, historical, explore, serious

**Status:** DEACTIVATED (moved to /deactivated/ folder in this session)

### Property Analysis

**chill:** ✅ KEEP
Yorùbá culture as described emphasizes "restraint," "ritual propriety," "reverence," and "cultivated harmony." This is a controlled, structured context.

**chaotic:** N/A (not assigned)

**narrative:** ✅ KEEP
The context requires "ritual contextualization" and transformation into "community gathering," "ancestral invocation," and "social ceremony." These are narrative structures.

**algorithmic:** N/A (not assigned)

**facts:** N/A (not assigned, correctly - this is deeply cultural/spiritual)

**emotion:** ✅ KEEP
The context explicitly requires "ìwà pẹ̀lẹ́ (gentle character)," "ìbá (respect)," "reverence," and "ethical texture." This is thoroughly emotional and relational.

**historical:** ⚠️ QUESTIONABLE
Yorùbá culture is *living heritage*, not a completed historical period. The description says "allows for critical assessment of AI limits" - this pedagogical framing is contemporary. However, the config treats Yorùbá culture as a fixed traditional system (problematic representation).

**contemporary:** ⚠️ SHOULD ADD
Yorùbá culture is living and evolving. If teaching about it, must acknowledge it as contemporary living practice, not museum artifact.

**explore:** ✅ KEEP
The description explicitly states: "Allows for a critical assessment of the limits of generative AI with regard to cultural knowledge." This is pedagogically exploratory and critically important.

**create:** N/A (not assigned)

**playful:** N/A (not assigned)

**serious:** ✅ KEEP
Engaging with living cultural systems requires deep respect and seriousness. The context demands "reverence" and "alignment."

**RECOMMENDED CHANGES:**
- CONSIDER: contemporary (Yorùbá is living culture, not frozen history)
- CRITICAL ISSUE: The entire config needs cultural expert review

---

### Context Prompt Quality
**Status:** ⚠️ SOPHISTICATED BUT REQUIRES EXPERT VALIDATION
**Legacy Comparison:** Found at workflows_legacy/arts_and_heritage/ai4artsed_YorubaHeritage_2509071028.json
**Issues:** **CRITICAL - Cultural accuracy and appropriation concerns**

**Analysis:** The context is detailed and shows engagement with Yorùbá concepts (àṣẹ, òrun, ayé, ògboni, òrìṣà, lunli, xiushen, li, junzi, ìwà pẹ̀lẹ́, ìbá, òtítọ́, ìbáṣepọ̀). It attempts to avoid "tourist clichés" and demands serious cultural translation. The negative prompting (NO NEGATIONS, no western terms, no brand names) shows thoughtfulness.

**HOWEVER:** This is extremely sensitive material. Questions:
1. Was this designed with Yorùbá cultural consultants?
2. Does Prof. Rissen have expertise in Yorùbá philosophy to validate accuracy?
3. Is it appropriate for a German academic to design AI configs about Yorùbá culture?
4. The description mentions "critical assessment of AI limits" - is this meta-pedagogical framing sufficient to avoid appropriation?

The config *could* be valuable for teaching about AI's cultural limitations, BUT it needs validation from Yorùbá scholars before reactivation.

---

### Description Quality
**Status:** ✅ GOOD (with critical framing)
**Issues:** None

**Analysis:** "Tries to translate everything into Yorùbá cultural framework with ancestral roles, ritual contexts, and spiritual relationships. Allows for a critical assessment of the limits of generative AI with regard to cultural knowledge." - The inclusion of "Tries to" and "critical assessment of limits" provides important epistemic humility. This frames it as an experiment in AI's cultural knowledge, not as authoritative cultural teaching.

---

### Metadata
**age (min_age):** 12 - ✅ APPROPRIATE (with proper framing)
**Consistency:** ⚠️ INCONSISTENT (historical vs. living heritage issue)

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED - Keep deactivated pending expert review

**Reasoning:** While the config shows cultural sensitivity and critical framing, it deals with living cultural knowledge that requires validation from Yorùbá scholars. The description's mention of "critical assessment of AI limits" suggests the *intent* is pedagogically sound (teaching about AI's cultural blindspots), but implementation requires expert validation.

**Recommendation:**
1. Keep deactivated until Yorùbá cultural expert review
2. If validated, reactivate with strong pedagogical framing about AI limitations
3. If not validated, redesign as generic "Cultural Translation" config that teaches about translation limits without appropriating specific cultures
4. Consider alternative: "Cultural Mistranslation" config that *intentionally* shows AI's failures with cultural concepts

---

## 4. clichéfilter_v1

**Current Properties:** chill, narrative, facts, contemporary, explore, serious

**Status:** DEACTIVATED (replaced by V2)

### Property Analysis
**Same issues as ClichéFilter V2:** Context is "professional translator" - completely broken placeholder.

**Properties:** Same problematic assignments as V2 (chill should be chaotic, narrative should be algorithmic).

---

### Context Prompt Quality
**Status:** ❌ AI-SLOP / BROKEN (same as V2)

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED - V2 is active (though V2 also needs fixing)

**Reasoning:** If this was replaced by V2, deactivation is correct. However, V2 has the same broken context, so neither version works properly.

---

## 5. clichéfilter_v3_250616192

**Current Properties:** chill, narrative, facts, contemporary, explore, serious

**Status:** DEACTIVATED (experimental variant)

### Property Analysis
**Same issues as V1 and V2.**

---

### Context Prompt Quality
**Status:** ❌ AI-SLOP / BROKEN (same placeholder)

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED

**Reasoning:** If V2 is the current version, experimental V3 should remain deactivated. However, ALL clichéfilter versions have broken contexts and need complete redesign.

---

## 6. ethicaladvisor

**Current Properties:** chill, facts, contemporary, explore, serious

**Status:** DEACTIVATED (likely for complexity/scope)

### Property Analysis

**chill:** ❌ REMOVE
Ethical review creates tension and confrontation. It challenges users' choices - this is not a "controlled context" but rather introduces uncertainty and critique.

**chaotic:** N/A (not assigned, but ethical judgment could feel chaotic)

**narrative:** ⚠️ CONSIDER ADDING
Ethics is fundamentally about relationships, consequences, and stories. Ethical reasoning often uses narratives ("what if everyone did this?").

**algorithmic:** N/A (not assigned, correctly - ethics is not rule-based but interpretive)

**facts:** ⚠️ QUESTIONABLE
Ethics involves facts (e.g., artists' work used without permission) but is fundamentally about *values*, not facts. Ethical judgments are normative, not descriptive.

**emotion:** ⚠️ CONSIDER ADDING
Ethics is deeply emotional - guilt, responsibility, care, harm. The context mentions "ethical point of view" which involves affective moral reasoning.

**historical:** N/A (not assigned)

**contemporary:** ✅ KEEP
AI ethics is an urgent contemporary concern.

**explore:** ✅ KEEP
Ethical review helps users explore moral dimensions of AI use - pedagogically exploratory.

**create:** N/A (not assigned)

**playful:** N/A (not assigned)

**serious:** ✅ KEEP
Ethics is serious moral reasoning.

**RECOMMENDED CHANGES:**
- REMOVE: chill (creates tension, not comfort)
- REMOVE: facts (ethics is normative, not factual)
- ADD: emotion (moral reasoning is affective)
- CONSIDER: narrative (ethics uses stories)

**Revised Properties:** contemporary, explore, serious, emotion, narrative(?)

---

### Context Prompt Quality
**Status:** ⚠️ NEEDS IMPROVEMENT
**Legacy Comparison:** Found at workflows_legacy/LLM/ai4artsed_EthicalAdvisor_2508271838.json
**Issues:** Pedagogically interesting but incompletely developed

**Analysis:** The context asks the AI to "React to this prompt from an ethical point of view" and mentions "unpaid exploitation of artists" and "impact of short-cutting one's own creative efforts." These are legitimate ethical concerns. The flags (#disapproved# or #considerations#) provide structured feedback.

**HOWEVER:** The framing is individualistic and potentially shame-based ("advising a person"). Better pedagogical framing would:
1. Acknowledge systemic issues (AI training on copyrighted work)
2. Discuss structural solutions (artist compensation, attribution)
3. Avoid moralizing individual users for using available tools
4. Frame ethics as collective responsibility, not personal guilt

---

### Description Quality
**Status:** ✅ GOOD
**Issues:** None

**Analysis:** "Reviews your image prompt from an ethical perspective. Considers issues like artist exploitation and the impact of shortcuts on creativity." - Clear and pedagogically valuable framing.

---

### Metadata
**age (min_age):** 12 - ✅ APPROPRIATE
**Consistency:** ⚠️ INCONSISTENT (chill doesn't fit ethical confrontation)

---

### Deactivation Reasoning & Recommendation
**Status:** ⚠️ CONSIDER REACTIVATION (with redesign)

**Reasoning:** Ethical AI literacy is *critical* for contemporary education. However, the current implementation risks shame-based pedagogy. Recommend:
1. Redesign context to focus on structural ethics, not individual morality
2. Remove "chill" property
3. Reactivate as part of critical AI literacy curriculum
4. Consider renaming to "AI Ethics Lens" or "Critical AI Literacy"

**Pedagogical value:** HIGH (if redesigned)
**Current quality:** MEDIUM
**Priority:** MEDIUM-HIGH for reactivation with improvements

---

## 7. (((promptinterception)))

**Current Properties:** chill, narrative, contemporary, explore

**Status:** DEACTIVATED (meta-experimental)

### Property Analysis

**chill:** ⚠️ UNCLEAR
Meta-reflection on prompt interception itself - is this "controlled"? Without seeing the actual context (it's "professional translator" placeholder), hard to judge.

**narrative:** ⚠️ UNCLEAR
Does this tell stories *about* interception, or does it intercept narratively? The triple parentheses suggest experimental/meta framing.

**algorithmic:** N/A (not assigned)

**facts:** N/A (not assigned)

**emotion:** N/A (not assigned)

**historical:** N/A (not assigned)

**contemporary:** ✅ KEEP
Meta-reflection on AI prompt transformation is contemporary practice.

**explore:** ✅ KEEP
This is explicitly exploratory about the prompt interception concept itself.

**create:** N/A (not assigned)

**playful:** ⚠️ LIKELY
Triple parentheses and "experimental meta-interception" suggest playful experimentation.

**serious:** N/A (not assigned, but meta-pedagogy is serious)

**RECOMMENDED CHANGES:**
Cannot properly assess without seeing actual implementation beyond placeholder

---

### Context Prompt Quality
**Status:** ❌ AI-SLOP / BROKEN
**Legacy Comparison:** Found at workflows_legacy/model/ai4artsed_(((PromptInterception)))_2507101853.json
**Issues:** Just "professional translator" placeholder

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED (broken placeholder)

**Reasoning:** The concept (meta-reflection on prompt interception) is pedagogically interesting but completely unimplemented. The triple parentheses suggest this was an experimental idea that never developed beyond placeholder.

**Recommendation:** Either develop properly with meta-pedagogical framing, or permanently retire.

---

## 8-10. LLM-Comparison Configs (14b, 30b, Mistral)

**Current Properties:** chill, algorithmic, contemporary, explore, serious

**Status:** DEACTIVATED (likely replaced by image_comparison or cost concerns)

### Property Analysis (applies to all three)

**chill:** ✅ KEEP
Model comparison provides structured analysis within controlled parameters.

**chaotic:** N/A (not assigned)

**narrative:** N/A (not assigned, correctly - comparison is analytical)

**algorithmic:** ✅ KEEP
Comparison follows systematic process of parallel execution and analysis.

**facts:** ⚠️ CONSIDER ADDING
Comparing model outputs is factual analysis.

**emotion:** N/A (not assigned)

**historical:** N/A (not assigned)

**contemporary:** ✅ KEEP
Model comparison is contemporary AI literacy practice.

**explore:** ✅ KEEP
Helps users explore how model size/architecture affects outputs.

**create:** N/A (not assigned)

**playful:** N/A (not assigned)

**serious:** ✅ KEEP
Understanding model differences is serious AI literacy.

**RECOMMENDED CHANGES:**
- ADD: facts (analytical comparison)

---

### Context Prompt Quality
**Status:** ❌ AI-SLOP / BROKEN
**Legacy Comparison:** Found at workflows_legacy/model/
**Issues:** All three just have "conversationalist" as context

**Analysis:** Another set of placeholder contexts. Model comparison needs:
1. Instructions for parallel execution
2. Guidance on output analysis
3. Explanation of why models differ
4. Pedagogical framing about model architecture

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED (broken placeholders)

**Reasoning:** While LLM comparison is pedagogically valuable, these configs are completely unimplemented. The contexts provide no guidance. If model comparison is desired, use the image_comparison pattern and create proper text comparison configs.

---

## 11. splitandcombinelinear

**Current Properties:** chaotic, algorithmic, explore, playful

**Status:** DEACTIVATED (replaced by spherical variant)

### Property Analysis
**Same as spherical variant** - properties are appropriate for split/combine operations.

---

### Context Prompt Quality
**Status:** ❌ AI-SLOP / BROKEN
**Issues:** Just "prompting expert" placeholder (same as spherical variant)

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED (replaced by spherical, but both broken)

**Reasoning:** If "spherical" is the improved version, linear should stay deactivated. However, *both* versions have broken contexts with just "prompting expert" placeholder. Neither works without complete context redesign.

---

## 12. traditionalchinese_long_prompts

**Current Properties:** chill, narrative, emotion, historical, explore, serious

**Status:** DEACTIVATED (possibly replaced by ConfucianLiterati)

### Property Analysis

**chill:** ✅ KEEP (if focusing on harmony and balance in Chinese aesthetics)

**narrative:** ✅ KEEP (Chinese art often tells stories through scroll painting sequences)

**emotion:** ✅ KEEP (Chinese aesthetics are deeply emotional - 意境 yìjìng "artistic mood")

**historical:** ⚠️ QUESTIONABLE
If this refers to historical Chinese art movements (Tang, Song dynasties), yes. But if "traditional" means living cultural practice, should be contemporary.

**contemporary:** ⚠️ CONSIDER ADDING
Chinese culture is living heritage, not museum artifact. Depends on how config frames it.

**explore:** ✅ KEEP (if pedagogically exploratory about Chinese aesthetics)

**serious:** ✅ KEEP (cultural translation is serious work)

---

### Context Prompt Quality
**Status:** ❌ AI-SLOP / BROKEN
**Legacy Comparison:** Found at workflows_legacy/arts_and_heritage/ai4artsed_TraditionalChinese_long_prompts_2506121345(1).json
**Issues:** Just "Prompting Expert" placeholder

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED (broken placeholder)

**Reasoning:** The config name suggests it was for longer prompts optimized for Chinese aesthetics, possibly replaced by the more specific ConfucianLiterati config. However, with just "Prompting Expert" as context, it's completely unimplemented.

**Note:** Same cultural sensitivity concerns as ConfucianLiterati and YorubaHeritage. Any cultural translation config needs expert validation.

---

## 13. translation_en

**Current Properties:** chill, algorithmic, facts, explore

**Status:** DEACTIVATED (system pipeline, not user-facing)

### Property Analysis

**chill:** ✅ KEEP
Translation follows controlled, predictable rules.

**algorithmic:** ✅ KEEP
Translation is rule-based linguistic transformation.

**facts:** ✅ KEEP
Translation preserves factual content across languages.

**explore:** ⚠️ QUESTIONABLE
System translation is functional, not exploratory. This property might be wrong for a system pipeline.

---

### Context Prompt Quality
**Status:** ✅ GOOD (for system pipeline)
**Issues:** None - "Target language: English. Preserve structure and formatting." is appropriate for system function.

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED (system pipeline)

**Reasoning:** The metadata confirms this is a system pipeline (`"system_pipeline": true, "skip_pre_translation": true`). It was used internally for pre-processing, not as user-facing config. Correct to keep deactivated from user interface.

---

## 14. passthrough

**Current Properties:** NULL (special case)

**Status:** DEACTIVATED (likely pedagogically problematic)

### Property Analysis

**Properties: "NULL"** - This is intentional. Passthrough has no transformation properties because it performs no transformation.

---

### Context Prompt Quality
**Status:** ✅ PERFECT (for what it does)
**Issues:** None

**Analysis:** "Pass on the input text unchanged. Do not modify, enhance, or transform the prompt in any way. Return it exactly as provided." - This is exactly right for a passthrough function.

---

### Deactivation Reasoning & Recommendation
**Status:** ✅ CORRECTLY DEACTIVATED (pedagogically problematic)

**Reasoning:** Passthrough defeats the entire pedagogical purpose of prompt interception. If users want direct image generation without transformation, they can use standard AI tools. The AI4ArtsEd project is specifically about *intervention* in the AI process. Passthrough undermines this pedagogical philosophy.

**Keep deactivated permanently.**

---

# SUMMARY

## Deactivation Categories

### ✅ CORRECTLY DEACTIVATED - Keep deactivated
1. **passthrough** - Defeats pedagogical purpose
2. **translation_en** - System pipeline, not user-facing
3. **clichéfilter_v1, v3** - Replaced by v2 (though v2 also broken)
4. **splitandcombinelinear** - Replaced by spherical (though both broken)
5. **quantumtheory** - Too advanced for audience
6. **yorubaheritage** - Needs cultural expert validation
7. **traditionalchinese_long_prompts** - Possibly replaced by ConfucianLiterati
8. **(((promptinterception)))** - Experimental placeholder, never developed
9. **llm-comparison configs (3)** - Broken placeholders

### ⚠️ CONSIDER REACTIVATION (with improvements)
1. **image_comparison** - Pedagogically valuable, needs cost warnings
2. **ethicaladvisor** - Critical AI literacy tool, needs redesign to avoid shame-based pedagogy

### ❌ BROKEN CONFIGS FOUND IN DEACTIVATED
- Multiple configs with placeholder contexts ("professional translator", "prompting expert", "conversationalist")
- These were never properly implemented

## Cultural Sensitivity Concerns
**Configs requiring expert validation:**
- yorubaheritage (Yorùbá cultural specialists)
- traditionalchinese_long_prompts (Sinology experts)
- confucianliterati (active config, also needs validation)

**Recommendation:** Create "Cultural Translation - Limits of AI" config that teaches about AI's cultural blindspots without appropriating specific cultures.

## Property Assignment Issues
Most deactivated configs have property issues, but since they're deactivated, fixing properties is lower priority than active configs.

---

**Analysis Complete:** 2025-11-08
**Next Step:** Create PROPERTY_TAXONOMY_SUMMARY.md with statistics
