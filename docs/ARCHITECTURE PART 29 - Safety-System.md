# ARCHITECTURE PART 29 — Safety System

**Status:** Authoritative
**Last Updated:** 2026-02-12 (Session 170)
**Scope:** Complete safety architecture — levels, filters, enforcement points, legal basis

---

## 1. Design Principles

The safety system addresses **three independent concerns**:

| Concern | Legal Basis | Scope | Applies To |
|---------|------------|-------|------------|
| **§86a StGB** | Criminal law | Prohibited symbols (Nazi, terrorist) | All levels except Research |
| **DSGVO** | Data protection (GDPR) | Personal data in prompts (NER) | All levels except Research |
| **Jugendschutz** | Youth protection (JuSchG) | Age-inappropriate content | Kids, Youth only |

These concerns are **independent and non-redundant**. Each has its own detection mechanism and cannot substitute for another.

**Core principle:** The safety system is a constitutive part of the software's scientific integrity (see LICENSE.md §4). Disabling it outside authorized research contexts constitutes a license violation (LICENSE.md §3(e)).

---

## 2. Safety Levels

Four canonical levels, defined in `devserver/config.py`:

| Level | §86a | DSGVO/NER | Age Filter | VLM Image Check | Stage 3 LLM | Use Case |
|-------|------|-----------|------------|-----------------|-------------|----------|
| **kids** | Yes | Yes | Yes (kids params) | Yes | Yes | Primary education (8-12) |
| **youth** | Yes | Yes | Yes (youth params) | Yes | Yes | Secondary education (13-17) |
| **adult** | Yes | Yes | No | No | No | Adult/university education |
| **research** | No | No | No | No | No | Authorized research institutions only |

**Backend-only:** The safety level is never sent by the frontend. It is controlled exclusively by `config.DEFAULT_SAFETY_LEVEL` (set via Settings UI, persisted in `user_settings.json`).

**Legacy normalization:** The value `"off"` (pre-2026-02) is automatically normalized to `"research"` on config load (`my_app/__init__.py`).

---

## 3. Enforcement Points

### 3.1 Stage 1 — Input Safety (`stage_orchestrator.py`)

**Function:** `execute_stage1_gpt_oss_unified()`

```
Input text
  │
  ├─ research → SKIP ALL (early return)
  │
  ├─ STEP 1: §86a Fast-Filter (~0.001s)
  │    Bilingual keyword matching (DE+EN)
  │    Hit → LLM context verification → BLOCK or allow
  │
  ├─ STEP 2: Age-Appropriate Fast-Filter
  │    Skip for adult/research
  │    kids/youth → filter list match → LLM verification → BLOCK or allow
  │
  └─ STEP 3: DSGVO SpaCy NER (~50-100ms)
       Models: de_core_news_lg + xx_ent_wiki_sm (2 models only!)
       PER entity detected → LLM verification (false-positive reduction)
       Confirmed PER → BLOCK
```

**Key files:**
- `devserver/schemas/engine/stage_orchestrator.py` — orchestration logic
- `devserver/schemas/data/stage1_safety_*.json` — filter term lists
- `devserver/schemas/configs/pre_interception/` — LLM prompt configs

### 3.2 SAFETY-QUICK — Frontend Pre-Check (`schema_pipeline_routes.py`)

**Endpoint:** `POST /api/schema/pipeline/safety/quick`

Called autonomously by `MediaInputBox` on blur/paste. Two modes:

**Text mode** (field: `text`):
```
research → SKIP (return safe=true, checks_passed=['safety_skip'])
adult    → §86a fast-filter + DSGVO NER (full checks)
youth    → §86a fast-filter + DSGVO NER (full checks)
kids     → §86a fast-filter + DSGVO NER (full checks)
```

**Image mode** (field: `image_path`):
```
research/adult → SKIP (vlm_skipped)
youth/kids     → VLM safety check via Ollama
```

### 3.3 Stage 3 — Pre-Output Safety (`stage_orchestrator.py`)

**Function:** `execute_stage3_safety()`

```
research/adult → Translation only (no safety LLM)
youth/kids     → Translation + LLM semantic safety check
```

Stage 3 catches prompts that pass all fast-filters but would generate harmful imagery. Example: "Wesen sind feindselig zueinander und fügen einander Schaden zu" — passes keyword filters but generates harmful content for children.

**Code safety:** `execute_stage3_safety_code()` — same skip logic for generated code (JavaScript, Ruby, etc.)

### 3.4 Post-Generation VLM Check (`schema_pipeline_routes.py`)

**Scope:** Images only, kids/youth only

After Stage 4 generates an image, a local VLM (qwen3-vl:2b via Ollama) analyzes the actual pixels before delivery to frontend.

```
media_type != 'image' → SKIP
safety_level not in (kids, youth) → SKIP
VLM → "safe" → SSE 'complete'
VLM → "unsafe" → SSE 'blocked' (stage: 'vlm_safety')
VLM → error → fail-open → SSE 'complete'
```

**Config:** `VLM_SAFETY_MODEL` in `config.py`
**Technical note:** qwen3-vl uses thinking mode — analysis in `message.thinking`, decision in `message.content`. Both checked. `num_predict: 500` minimum.

---

## 4. Detection Mechanisms

### 4.1 §86a Fast-Filter

**Function:** `fast_filter_bilingual_86a()` in `stage_orchestrator.py`

Bilingual (DE+EN) keyword matching against known prohibited symbols:
- Nazi symbols: Hakenkreuz, SS-Runen, Schwarze Sonne, etc.
- Terrorist organizations: ISIS/ISIL, Al-Qaeda, PKK, RAF
- Extremist codes: 88 (HH), 18 (AH), 28 (B&H)

**Data:** `devserver/schemas/data/stage1_safety_filters_86a.json`

On match → LLM context verification to reduce false positives (e.g., "1988" vs "88").

### 4.2 Age-Appropriate Fast-Filter

**Function:** `fast_filter_check()` in `stage_orchestrator.py`

Fuzzy matching against level-specific filter lists:
- `stage1_safety_filters_kids.json`
- `stage1_safety_filters_youth.json`

On match → LLM semantic check via pipeline executor.

### 4.3 DSGVO SpaCy NER

**Function:** `fast_dsgvo_check()` in `stage_orchestrator.py`

Only 2 SpaCy models loaded (prevents cross-language false positives):
- `de_core_news_lg` — German NER
- `xx_ent_wiki_sm` — Multilingual NER

Looks for `PER` (person) entities. On hit → `llm_verify_person_name()` for false-positive reduction.

**CRITICAL: Local-only LLM verification.** The `llm_verify_person_name()` function ALWAYS runs via local Ollama — never external APIs. Sending detected personal names to Mistral/Anthropic/OpenAI for verification would itself be a DSGVO violation. Model: `config.SAFETY_MODEL` (configurable in Settings UI, default: `gpt-OSS:20b`).

**Fail-closed:** If the local LLM returns an empty response or is unavailable, the system blocks with an admin-contact error message. Safety verification must never fail-open.

**Available safety models:** `llama-guard3:1b`, `llama-guard3:latest`, `llama-guard3:8b`, `gpt-OSS:20b`, `gpt-OSS:120b`.

**Lesson learned:** Running all 12 SpaCy models causes cross-language confusion (e.g., `en_core_web_lg` flags "Der Eiffelturm" as PERSON).

### 4.4 VLM Image Analysis

**Function:** `vlm_safety_check()` in `my_app/utils/vlm_safety.py`

Post-generation visual analysis. Different prompts per safety level:
- Kids (6-12): Checks for violence, nudity, unsettling/traumatizing content
- Youth (14-18): Adapted thresholds for teenagers

**Fail-open:** VLM errors never block generation.

---

## 5. Flow Summary

```
User Input
  │
  ├─ [Frontend] MediaInputBox on blur/paste
  │   └─ POST /safety/quick (§86a + DSGVO, text)
  │   └─ POST /safety/quick (VLM, uploaded images)
  │
  ├─ [Stage 1] execute_stage1_gpt_oss_unified()
  │   └─ §86a fast-filter → Age filter → DSGVO NER
  │
  ├─ [Stage 2] Prompt Interception (no safety)
  │
  ├─ [Stage 3] execute_stage3_safety()
  │   └─ Translation + LLM semantic check (kids/youth)
  │
  ├─ [Stage 4] Media Generation
  │
  └─ [Post-Gen] VLM Image Check (kids/youth, images only)
        └─ Safe → deliver | Unsafe → SSE 'blocked'
```

### 5.1 Canvas Workflows — Intentionally Unfiltered

Canvas routes (`/api/canvas/execute`, `/execute-stream`, `/execute-batch`) have **no safety enforcement by design**. Canvas is restricted to `adult` and `research` safety levels only — kids/youth cannot access it. Since `adult` skips age-appropriate checks and `research` skips all checks, no input filtering is needed on Canvas routes. Stage 3 safety still applies during generation for `adult`.

---

## 6. Configuration

### config.py

```python
DEFAULT_SAFETY_LEVEL = 'kids'          # Default, overridden by user_settings.json
VLM_SAFETY_MODEL = 'qwen3-vl:2b'      # Ollama model for image checks
STAGE1_TEXT_MODEL = '...'              # Model for Stage 1 LLM checks
```

### user_settings.json

```json
{
  "DEFAULT_SAFETY_LEVEL": "research"
}
```

Loaded at startup by `reload_user_settings()` in `my_app/__init__.py`. Legacy `"off"` values are normalized to `"research"`.

### Settings UI

`SettingsView.vue` — Safety Level dropdown with descriptive info boxes per level. Research mode shows red warning about restricted use (see LICENSE.md §3(e)).

---

## 7. Legal Integration

The research mode restriction is codified in `LICENSE.md` §3(e):
- Requires institutional affiliation (university, Forschungseinrichtung)
- Requires documented research purpose
- Requires ethical oversight (Ethikkommission/IRB)
- Prohibits exposure of unfiltered outputs to minors
- Violation = license termination (§7) + scientific integrity impairment (§4, §14 UrhG)

---

## 8. Key Files

| File | Role |
|------|------|
| `devserver/config.py` | Safety level defaults, VLM model config |
| `devserver/my_app/__init__.py` | Legacy "off" → "research" normalization |
| `devserver/schemas/engine/stage_orchestrator.py` | Stage 1 + Stage 3 safety logic |
| `devserver/my_app/routes/schema_pipeline_routes.py` | SAFETY-QUICK endpoint, VLM post-gen check |
| `devserver/my_app/utils/vlm_safety.py` | VLM image analysis |
| `devserver/schemas/data/stage1_safety_filters_*.json` | Filter term lists |
| `public/.../views/SettingsView.vue` | Safety level dropdown UI |
| `LICENSE.md` §3(e) | Research mode legal restrictions |

---

## 9. Historical Context

| Session | Date | Change |
|---------|------|--------|
| 14 | 2025-11-02 | §86a StGB system prompt for GPT-OSS (ISIS failure case) |
| 29 | 2025-11-10 | Hybrid fast-filter + LLM verification |
| 132 | 2026-01-23 | Centralized safety in stage_orchestrator.py |
| 143 | 2026-01-27 | Fast-Filter-First architecture (no LLM for 95%+ cases) |
| 161 | 2026-02-07 | VLM post-generation image check |
| 170 | 2026-02-12 | Safety-level centralization ("off" → "research"), LICENSE.md §3(e) |

---

## 10. Related Documents

- `docs/reference/safety-architecture-matters.md` — Original §86a failure analysis (Session 14)
- `docs/HANDOVER_SAFETY_REFACTORING.md` — Planned endpoint separation (2026-01-26)
- `docs/ARCHITECTURE PART 01 - 4-Stage Orchestration Flow.md` — Pipeline overview
- `LICENSE.md` §3(e), §4 — Legal framework for safety system
