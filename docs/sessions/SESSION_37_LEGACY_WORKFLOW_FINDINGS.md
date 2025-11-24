# Session 37 - Legacy Workflow Context Findings

**Date:** 2025-11-08
**Source:** `/home/joerissen/ai/_backups/webserver/ai4artsed_webserver_2506152345/workflows/`

---

## Critical Discovery: Surrealization is NOT an Interception Config

**Finding:** The legacy workflow `ai4artsed_VECTOR_Surrealization_2506092253.json` is **NOT a prompt interception config** but a **split-pipeline** with dual CLIP/T5 optimization for SD3.5.

**Architecture:**
1. Translation node (input_context: "")
2. T5 optimization node (input_context: "prompting expert", 250 words max)
3. CLIP optimization node (input_context: "prompt expert", 50 words max)
4. T5-CLIP fusion with alpha parameter extraction

**Implications:**
- Surrealization needs a **completely new pipeline** (split_up pipeline)
- It needs new **chunks** (possibly vector manipulation chunks)
- Current config with "prompting expert" placeholder is WRONG architecture
- This explains why it's broken - it was never meant to be a simple interception config

**Recommendation:**
- Deactivate Surrealization until split_up pipeline is implemented
- OR redesign as true semantic deconstruction config (not vector-level)

---

## Verified Legacy Context Prompts

### 1. Overdrive

**Legacy File:** `ai4artsed_INTERVENTION_Overdrive_2506152234.json`
**Context (Node 42, Line 211):**

```
Your gift is to exaggerate the content of the input beyond measure. YOU ARE THE OVERDRIVE who amplifies everything to its grotesque limit and beyond distortion. Exaggerate in every respect, go over the top, show off, make everything big!
```

**Assessment:** ✅ **EXCELLENT CONTEXT** - Clear, characterful, pedagogically sound

**Current Config Status:** Has placeholder "prompting expert"

**Recommendation:** **RESTORE** this exact context to current config

---

### 2. TheOpposite

**Legacy File:** `ai4artsed_INTERVENTION_TheOpposite_fast_2506132130.json`
**Context (Node 42, Line 200):**

```
describe the exact diametral opposite
```

**Assessment:** ⚠️ **TOO BRIEF** but pedagogically clear

**Current Config Status:** Similar brief instruction

**Recommendation:** **EXPAND** slightly with examples:
```
Describe the exact diametral opposite.

Transform all entities and their relations into their polar opposites:
- Spatial relations reverse (above ↔ below, inside ↔ outside)
- Properties invert (bright ↔ dark, hot ↔ cold, large ↔ small)
- Social relations flip (friend ↔ enemy, supporting ↔ opposed by)
- Emotional states reverse (joy ↔ grief, calm ↔ agitated)
- Temporal markers invert (before ↔ after, past ↔ future)

Ensure the resulting structure is coherent and internally consistent.
```

---

### 3. ClichéFilter

**Legacy File:** `ai4artsed_INTERVENTION_ClichéFilter_2506152321.json`
**Status:** File exists but needs analysis

**Action:** Read this file next to extract context

---

### 4. Dada

**Legacy File:** `ai4artsed_ART_Dada_2506052148.json`
**Status:** Already excellent in current config

**Action:** Compare to verify no regression

---

### 5. StillePost

**Legacy File:** `ai4artsed_CULTURE_StillePost_2506110110.json`
**Status:** Already excellent in current config

**Action:** Compare to verify no regression

---

## Placeholder Origins Explained

**User note (from PROPERTY_TAXONOMY_SUMMARY.md:174):**
> "I used expressions like 'professional translator' and 'prompting expert' for certain API-Workflows (in particular translation nodes and nodes for formal prompt optimization), but they slipped in here somehow."

**Interpretation:**
- "professional translator" = correct for **translation nodes** (Stage 1)
- "prompting expert" = correct for **prompt optimization nodes** (SD3.5 dual-pipeline)
- **BUT:** These are NOT correct for **interception context** (Stage 2)

**What happened:**
Session 34 or earlier copy-pasted system prompts from **different node types** into the interception context fields.

---

## Wordsmith / Lyricist Investigation

**User note (PROPERTY_TAXONOMY_SUMMARY.md:174):**
> "The wordsmith thing is particularly for lyrics in AceStep API-Workflow and could be right for the music config with dual text pipeline."

**Hypothesis:** ImageAndSound/ImageToSound might have a **dual-text pipeline** (like Surrealization has dual CLIP/T5) where lyrics are generated separately.

**Action:** Need to find music-related workflows in legacy backups

---

## Next Steps

1. ✅ Read ClichéFilter legacy workflow
2. ✅ Search for music/sound legacy workflows (ImageAndSound, ImageToSound)
3. ✅ Compare Dada/StillePost legacy vs current (verify no regression)
4. ✅ Update all broken configs with correct contexts
5. ⚠️ Decide on Surrealization: Deactivate OR Redesign

---

## Files to Check Next

```bash
# Already checked:
✅ ai4artsed_INTERVENTION_Overdrive_2506152234.json
✅ ai4artsed_INTERVENTION_TheOpposite_fast_2506132130.json
✅ ai4artsed_VECTOR_Surrealization_2506092253.json

# Need to check:
⏳ ai4artsed_INTERVENTION_ClichéFilter_2506152321.json
⏳ ai4artsed_ART_Dada_2506052148.json (verification)
⏳ ai4artsed_CULTURE_StillePost_2506110110.json (verification)
⏳ (search for music/sound workflows)
```
