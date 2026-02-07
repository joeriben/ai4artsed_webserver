"""
Stage Orchestrator - Helper functions for 4-Stage Architecture
Extracted from pipeline_executor.py for Phase 2 refactoring

These functions will be used by DevServer (schema_pipeline_routes.py)
to orchestrate Stage 1-3, while PipelineExecutor becomes a DUMB executor.

DUMB helpers: Just execute specific stage configs, return results
"""
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging
import json
import re
import time as _time

logger = logging.getLogger(__name__)

# ============================================================================
# FUZZY MATCHING: Levenshtein distance for typo-resilient filter lists
# ============================================================================

def _levenshtein(s1: str, s2: str) -> int:
    """Simple Levenshtein distance (stdlib-only, no dependencies)"""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            curr_row.append(min(
                prev_row[j + 1] + 1,   # insertion
                curr_row[j] + 1,        # deletion
                prev_row[j] + (c1 != c2)  # substitution
            ))
        prev_row = curr_row
    return prev_row[-1]


def _fuzzy_contains(text_lower: str, term: str, max_distance: int = 2) -> bool:
    """Check if any word/phrase in text fuzzy-matches term within Levenshtein distance"""
    term_len = len(term)
    words = text_lower.split()

    if ' ' in term:
        # Multi-word term (e.g., "heil hitler"): check word combinations
        term_word_count = len(term.split())
        for i in range(len(words)):
            for j in range(i + 1, min(i + term_word_count + 1, len(words) + 1)):
                combo = ' '.join(words[i:j])
                if abs(len(combo) - term_len) <= max_distance:
                    if _levenshtein(combo, term) <= max_distance:
                        return True
    else:
        # Single-word term: check each word individually
        for word in words:
            if abs(len(word) - term_len) <= max_distance:
                if _levenshtein(word, term) <= max_distance:
                    return True
    return False


# ============================================================================
# SPACY NER: DSGVO Personal Data Detection
# ============================================================================

# SpaCy models cache (loaded once at module level)
_SPACY_MODELS: Optional[List] = None
_SPACY_LOAD_ATTEMPTED = False

# Primary NER models: German (most users) + multilingual (foreign names)
# These two cover the DSGVO use case without excessive false positives.
# The multilingual model catches names from any language (Turkish, Arabic, etc.)
_SPACY_MODEL_NAMES = [
    'de_core_news_lg',   # German (primary language of the platform)
    'xx_ent_wiki_sm',    # Multilingual fallback (catches foreign names)
]

# Regex patterns for DSGVO-relevant data that SpaCy doesn't catch
_EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
_PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,5}\)?[-.\s]?\d{3,}[-.\s]?\d{2,}')
_ADDRESS_REGEX = re.compile(r'\b(?:[A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|weg|gasse|allee|platz|ring|damm|ufer))\s+\d+\b', re.IGNORECASE)

def _load_spacy_models() -> List:
    """Load all SpaCy NER models (called once, cached)"""
    global _SPACY_MODELS, _SPACY_LOAD_ATTEMPTED

    if _SPACY_LOAD_ATTEMPTED:
        return _SPACY_MODELS or []

    _SPACY_LOAD_ATTEMPTED = True

    try:
        import spacy
    except ImportError:
        logger.warning("[SPACY] spacy not installed — DSGVO NER check disabled")
        _SPACY_MODELS = []
        return []

    models = []
    load_start = _time.time()

    for model_name in _SPACY_MODEL_NAMES:
        try:
            nlp = spacy.load(model_name, disable=['parser', 'tagger', 'lemmatizer', 'attribute_ruler'])
            models.append((model_name, nlp))
        except OSError:
            logger.debug(f"[SPACY] Model '{model_name}' not installed, skipping")

    load_time = _time.time() - load_start
    _SPACY_MODELS = models
    logger.info(f"[SPACY] Loaded {len(models)} NER models in {load_time:.1f}s")
    return models


def fast_dsgvo_check(text: str) -> Tuple[bool, List[str], bool]:
    """
    Fast DSGVO personal data check using SpaCy NER + regex (~12-60ms)

    Runs ALL loaded language models over the text and unions results.
    Reason: A Turkish name in German text needs the multilingual model.

    Detects:
    - PER: Person names (first + last name combinations)
    - LOC with house numbers: Addresses
    - Email addresses (regex)
    - Phone numbers (regex)

    Returns:
        (has_personal_data, found_entities, spacy_available) - True if DSGVO-relevant data found
    """
    models = _load_spacy_models()

    if not models:
        return (False, [], False)

    found_entities = set()
    check_start = _time.time()

    # Run all language models and union results
    for model_name, nlp in models:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == 'PER':
                    # Only flag multi-word names (first + last) — single words are too common
                    if ' ' in ent.text.strip():
                        found_entities.add(f"Name: {ent.text.strip()}")
                elif ent.label_ == 'LOC':
                    # Check if it's an address (LOC + house number nearby)
                    context = text[max(0, ent.start_char - 5):ent.end_char + 10]
                    if re.search(r'\d+', context):
                        found_entities.add(f"Adresse: {ent.text.strip()}")
        except Exception as e:
            logger.debug(f"[SPACY] Error with model {model_name}: {e}")

    # Regex checks (language-independent)
    for match in _EMAIL_REGEX.finditer(text):
        found_entities.add(f"Email: {match.group()}")

    for match in _PHONE_REGEX.finditer(text):
        # Filter out short numbers (year numbers, dimensions, etc.)
        digits_only = re.sub(r'\D', '', match.group())
        if len(digits_only) >= 7:
            found_entities.add(f"Telefon: {match.group()}")

    for match in _ADDRESS_REGEX.finditer(text):
        found_entities.add(f"Adresse: {match.group()}")

    check_time = _time.time() - check_start
    entity_list = sorted(found_entities)

    if entity_list:
        logger.info(f"[DSGVO-NER] Found {len(entity_list)} entities in {check_time*1000:.1f}ms: {entity_list[:3]}")
    else:
        logger.debug(f"[DSGVO-NER] Clean ({check_time*1000:.1f}ms)")

    return (len(entity_list) > 0, entity_list, True)


# ============================================================================
# HYBRID SAFETY: Fast String-Matching + LLM Context Verification
# ============================================================================

# Cache for filter terms (loaded once at module level)
_FILTER_TERMS_CACHE: Optional[Dict[str, List[str]]] = None
_BILINGUAL_86A_CACHE: Optional[List[str]] = None

def load_filter_terms() -> Dict[str, List[str]]:
    """Load all filter terms from JSON files (cached)"""
    global _FILTER_TERMS_CACHE

    if _FILTER_TERMS_CACHE is None:
        try:
            # Load Stage 3 filters (Youth/Kids)
            stage3_path = Path(__file__).parent.parent / "youth_kids_safety_filters.json"
            with open(stage3_path, 'r', encoding='utf-8') as f:
                stage3_data = json.load(f)

            # Load Stage 1 filters (CSAM/Violence/Hate)
            stage1_path = Path(__file__).parent.parent / "stage1_safety_filters.json"
            with open(stage1_path, 'r', encoding='utf-8') as f:
                stage1_data = json.load(f)

            _FILTER_TERMS_CACHE = {
                'kids': stage3_data['filters']['kids']['terms'],
                'youth': stage3_data['filters']['youth']['terms'],
                'stage1': stage1_data['filters']['stage1']['terms']
            }
            logger.info(f"Loaded filter terms: stage1={len(_FILTER_TERMS_CACHE['stage1'])}, kids={len(_FILTER_TERMS_CACHE['kids'])}, youth={len(_FILTER_TERMS_CACHE['youth'])}")
        except Exception as e:
            logger.error(f"Failed to load filter terms: {e}")
            _FILTER_TERMS_CACHE = {'kids': [], 'youth': [], 'stage1': []}

    return _FILTER_TERMS_CACHE

def load_bilingual_86a_terms() -> List[str]:
    """Load bilingual §86a critical terms for pre/post GPT-OSS filtering (cached)"""
    global _BILINGUAL_86A_CACHE

    if _BILINGUAL_86A_CACHE is None:
        try:
            bilingual_path = Path(__file__).parent.parent / "stage1_86a_critical_bilingual.json"
            with open(bilingual_path, 'r', encoding='utf-8') as f:
                bilingual_data = json.load(f)

            _BILINGUAL_86A_CACHE = bilingual_data['filters']['stage1_critical_86a']['terms']
            logger.info(f"Loaded bilingual §86a critical terms: {len(_BILINGUAL_86A_CACHE)} terms")
        except Exception as e:
            logger.error(f"Failed to load bilingual §86a terms: {e}")
            _BILINGUAL_86A_CACHE = []

    return _BILINGUAL_86A_CACHE

def fast_filter_bilingual_86a(text: str) -> Tuple[bool, List[str]]:
    """
    Fuzzy bilingual matching for critical §86a terms (~1-5ms)
    Uses Levenshtein distance for terms >= 6 chars to catch misspellings.
    Works on both German (pre-translation) and English (post-translation) text.

    Returns:
        (has_terms, found_terms) - True if §86a critical terms found
    """
    terms_list = load_bilingual_86a_terms()

    if not terms_list:
        return (False, [])

    text_lower = text.lower()
    found_terms = []
    for term in terms_list:
        term_lower = term.lower()
        if len(term_lower) >= 6:
            # Long unambiguous terms: fuzzy match (catches svastika, hakenkreutz, etc.)
            if _fuzzy_contains(text_lower, term_lower, max_distance=2):
                found_terms.append(term)
        else:
            # Short terms: exact substring match only (too many false positives otherwise)
            if term_lower in text_lower:
                found_terms.append(term)

    return (len(found_terms) > 0, found_terms)

def fast_filter_check(prompt: str, safety_level: str) -> Tuple[bool, List[str]]:
    """
    Fuzzy matching against filter lists (~1-5ms)
    Uses Levenshtein distance for terms >= 6 chars to catch misspellings.

    Returns:
        (has_terms, found_terms) - True if problematic terms found
    """
    filter_terms = load_filter_terms()
    terms_list = filter_terms.get(safety_level, [])

    if not terms_list:
        logger.warning(f"No filter terms for safety_level '{safety_level}'")
        return (False, [])

    prompt_lower = prompt.lower()
    found_terms = []
    for term in terms_list:
        term_lower = term.lower()
        if len(term_lower) >= 6:
            # Long unambiguous terms: fuzzy match
            if _fuzzy_contains(prompt_lower, term_lower, max_distance=2):
                found_terms.append(term)
        else:
            # Short terms: exact substring match only
            if term_lower in prompt_lower:
                found_terms.append(term)

    return (len(found_terms) > 0, found_terms)

# ============================================================================
# PARSING HELPERS
# ============================================================================

def parse_llamaguard_output(output: str) -> Tuple[bool, List[str]]:
    """
    Parse Llama-Guard output format:
    "safe" → (True, [])
    "unsafe\nS1,S3" → (False, ['S1', 'S3'])
    "unsafe,S8, Violent Crimes" → (False, ['S8'])
    """
    lines = output.strip().split('\n')
    first_line = lines[0].strip()
    first_line_lower = first_line.lower()

    if first_line_lower == 'safe':
        return (True, [])
    elif first_line_lower.startswith('unsafe'):
        # Handle two formats:
        # Format 1: "unsafe\nS1,S3" (two lines)
        # Format 2: "unsafe,S8, Violent Crimes" (one line with comma)

        if ',' in first_line:
            # Format 2: Extract codes from first line after "unsafe,"
            # Use original case-preserved string for S-code extraction
            parts = first_line.split(',', 1)[1].strip()
            # Extract S-codes (S1, S2, etc.) - case insensitive
            codes = re.findall(r'[Ss]\d+', parts)
            # Normalize to uppercase
            codes = [code.upper() for code in codes]
            return (False, codes)
        elif len(lines) > 1:
            # Format 1: Codes on second line
            codes = [code.strip() for code in lines[1].split(',')]
            return (False, codes)
        return (False, [])
    else:
        # Unexpected format
        logger.warning(f"Unexpected Llama-Guard output format: {output[:100]}")
        return (True, [])  # Default to safe if uncertain

def build_safety_message(codes: List[str], lang: str = 'de') -> str:
    """
    Build user-friendly safety message from Llama-Guard codes using llama_guard_explanations.json
    """
    explanations_path = Path(__file__).parent.parent / 'llama_guard_explanations.json'

    try:
        with open(explanations_path, 'r', encoding='utf-8') as f:
            explanations = json.load(f)

        base_msg = explanations['base_message'][lang]
        hint_msg = explanations['hint_message'][lang]

        # Build message from codes
        messages = []
        for code in codes:
            if code in explanations['codes']:
                messages.append(f"• {explanations['codes'][code][lang]}")
            else:
                messages.append(f"• Code: {code}")

        if not messages:
            return explanations['fallback'][lang]

        full_message = base_msg + "\n\n" + "\n".join(messages) + hint_msg
        return full_message

    except Exception as e:
        logger.error(f"Error building safety message: {e}")
        return "Dein Prompt wurde aus Sicherheitsgründen blockiert." if lang == 'de' else "Your prompt was blocked for safety reasons."

def parse_preoutput_json(output: str) -> Dict[str, Any]:
    """
    Parse output from pre-output pipeline.
    Accepts two formats:
    1. Plain text: "safe" or "unsafe" (llama-guard format)
    2. JSON: {"safe": true/false, "positive_prompt": "...", ...}
    """
    output_cleaned = output.strip().lower()

    # CASE 1: Plain text "safe"/"unsafe" from llama-guard
    if output_cleaned == "safe":
        return {
            "safe": True,
            "positive_prompt": None,
            "negative_prompt": None,
            "abort_reason": None
        }
    elif output_cleaned.startswith("unsafe"):
        # llama-guard returns "unsafe\nS1\nS2" etc.
        return {
            "safe": False,
            "positive_prompt": None,
            "negative_prompt": None,
            "abort_reason": "Content flagged as unsafe by safety filter"
        }

    # CASE 2: Try JSON parsing
    try:
        # Remove markdown code blocks if present
        cleaned = re.sub(r'```json\s*|\s*```', '', output.strip())
        parsed = json.loads(cleaned)

        # Validate required fields
        if 'safe' not in parsed:
            raise ValueError("Missing 'safe' field in pre-output JSON")

        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse pre-output JSON: {e}\nOutput: {output[:200]}")
        # Return safe default to allow continuation
        return {
            "safe": True,
            "positive_prompt": output,
            "negative_prompt": "blurry, low quality, bad anatomy",
            "abort_reason": None
        }

# ============================================================================
# STAGE EXECUTION FUNCTIONS (For DevServer to use in Phase 3)
# ============================================================================

async def execute_stage1_translation(
    text: str,
    execution_mode: str,
    pipeline_executor
) -> str:
    """
    Execute Stage 1a: Translation
    DUMB: Just calls translation pipeline, returns result

    Args:
        text: Input text to translate
        execution_mode: 'eco' or 'fast'
        pipeline_executor: PipelineExecutor instance

    Returns:
        Translated text
    """
    result = await pipeline_executor.execute_pipeline(
        'pre_interception/correction_translation_de_en',
        text,
        execution_mode=execution_mode
    )

    if result.success:
        return result.final_output
    else:
        logger.warning(f"Translation failed: {result.error}, continuing with original text")
        return text

async def execute_stage1_safety(
    text: str,
    safety_level: str,
    execution_mode: str,
    pipeline_executor
) -> Tuple[bool, List[str]]:
    """
    Execute Stage 1b: Hybrid Safety Check
    Fast string-match → LLM verification if terms found

    Args:
        text: Text to check for safety
        safety_level: Not used in Stage 1 (always uses 'stage1' filters)
        execution_mode: 'eco' or 'fast'
        pipeline_executor: PipelineExecutor instance

    Returns:
        (is_safe, error_codes)
    """
    import time

    # HYBRID APPROACH: Fast string-match first
    start_time = time.time()
    has_terms, found_terms = fast_filter_check(text, 'stage1')
    fast_check_time = time.time() - start_time

    if not has_terms:
        # FAST PATH: No problematic terms → instantly safe (95% of requests)
        logger.info(f"[STAGE1-SAFETY] PASSED (fast-path, {fast_check_time*1000:.1f}ms)")
        return (True, [])

    # SLOW PATH: Terms found → Llama-Guard context verification
    logger.info(f"[STAGE1-SAFETY] found terms {found_terms[:3]}... → Llama-Guard check (fast: {fast_check_time*1000:.1f}ms)")

    llm_start_time = time.time()
    result = await pipeline_executor.execute_pipeline(
        'pre_interception/safety_llamaguard',
        text,
        execution_mode=execution_mode
    )
    llm_check_time = time.time() - llm_start_time

    if result.success:
        is_safe, codes = parse_llamaguard_output(result.final_output)

        if not is_safe:
            logger.warning(f"[STAGE1-SAFETY] BLOCKED by Llama-Guard: {codes} (llm: {llm_check_time:.1f}s)")
            return (False, codes)
        else:
            # FALSE POSITIVE: Terms found but context is safe
            logger.info(f"[STAGE1-SAFETY] PASSED (Llama-Guard verified false positive, llm: {llm_check_time:.1f}s)")
            return (True, [])
    else:
        logger.warning(f"[STAGE1-SAFETY] Llama-Guard failed: {result.error}, continuing (fail-open)")
        return (True, [])  # Fail-open

async def execute_stage1_gpt_oss_unified(
    text: str,
    safety_level: str,
    execution_mode: str,
    pipeline_executor
) -> Tuple[bool, str, Optional[str], List[str]]:
    """
    Execute Stage 1: Fast-Filter-First Safety Check (NO Translation)

    New Flow (eliminates LLM call in 95%+ of cases):
    1. §86a Fast-Filter bilingual (~0.001s)
       → Hit? → BLOCK immediately (§86a is unambiguous)
    2. Age-appropriate Fast-Filter (~0.001s)
       → No hit? → continue to step 3
       → Hit? → LLM Context-Check (e.g. "cute vampire" vs "scary vampire")
    3. DSGVO SpaCy NER (~50-100ms)
       → No entities? → SAFE (done, no LLM needed)
       → Entities found? → BLOCK with explanation
       → SpaCy unavailable? → LLM Fallback (DSGVO is in GPT-OSS prompt)

    Args:
        text: Input text to safety-check (in original language)
        safety_level: 'kids', 'youth', 'adult', or 'off'
        execution_mode: 'eco' or 'fast'
        pipeline_executor: PipelineExecutor instance

    Returns:
        (is_safe, original_text, error_message, checks_passed)
    """
    total_start = _time.time()

    # ── STEP 1: §86a Fast-Filter (bilingual, ~0.001s) ──────────────────
    # §86a violations are unambiguous — no LLM context check needed
    s86a_start = _time.time()
    has_86a_terms, found_86a_terms = fast_filter_bilingual_86a(text)
    s86a_time = _time.time() - s86a_start

    if has_86a_terms:
        error_message = (
            f"⚠️ Dein Prompt wurde blockiert\n\n"
            f"GRUND: §86a StGB\n\n"
            f"Dein Prompt enthält Begriffe, die nach deutschem Recht verboten sind: {', '.join(found_86a_terms[:3])}\n\n"
            f"WARUM DIESE REGEL?\n"
            f"Diese Symbole werden benutzt, um Gewalt und Hass zu verbreiten.\n"
            f"Wir schützen dich und andere vor gefährlichen Inhalten."
        )
        logger.warning(f"[STAGE1] BLOCKED §86a fast-filter: {found_86a_terms[:3]} ({s86a_time*1000:.1f}ms)")
        return (False, text, error_message, ['§86a'])

    # ── STEP 2: Age-appropriate Fast-Filter (~0.001s) ──────────────────
    # Skip for 'adult' and 'off' — only §86a and DSGVO apply
    if safety_level not in ('off', 'adult'):
        age_start = _time.time()
        has_age_terms, found_age_terms = fast_filter_check(text, safety_level)
        age_time = _time.time() - age_start

        if has_age_terms:
            # Terms found → LLM context check (prevents false positives like "cute vampire")
            logger.info(f"[STAGE1] Age-filter hit: {found_age_terms[:3]} → LLM context check ({age_time*1000:.1f}ms)")

            # Call GPT-OSS for context-aware age-check
            text_with_metadata = f"[SAFETY: {safety_level}]\n{text}"
            llm_start = _time.time()
            result = await pipeline_executor.execute_pipeline(
                'pre_interception/gpt_oss_safety',
                text_with_metadata,
                execution_mode=execution_mode
            )
            llm_time = _time.time() - llm_start

            if not result.success:
                logger.warning(f"[STAGE1] LLM age-check failed: {result.error}, continuing (fail-open)")
                # Fall through to DSGVO check
            else:
                response = result.final_output.strip()

                if response.startswith("BLOCKED:"):
                    blocked_parts = response[8:].strip()

                    if "Kids-Filter" in blocked_parts:
                        parts = blocked_parts.split(" - ", 2)
                        found_terms_str = parts[1] if len(parts) > 1 else "inappropriate content"
                        explanation = parts[2] if len(parts) > 2 else "Prompt contains terms inappropriate for children"

                        error_message = (
                            f"⚠️ Dein Prompt wurde blockiert\n\n"
                            f"GRUND: Kinder-Schutzfilter (6-12 Jahre)\n\n"
                            f"{explanation}\n\n"
                            f"Gefundene Begriffe: {found_terms_str}\n\n"
                            f"WARUM DIESE REGEL?\n"
                            f"Dein Prompt enthält Begriffe, die für Kinder erschreckend oder verstörend sein können.\n"
                            f"Wir schützen dich vor Inhalten, die Angst machen oder ungeeignet für dein Alter sind."
                        )
                        logger.warning(f"[STAGE1] BLOCKED Kids-Filter (LLM confirmed, {llm_time:.1f}s)")
                        return (False, text, error_message, ['§86a', 'age_filter'])

                    elif "Youth-Filter" in blocked_parts:
                        parts = blocked_parts.split(" - ", 2)
                        found_terms_str = parts[1] if len(parts) > 1 else "inappropriate content"
                        explanation = parts[2] if len(parts) > 2 else "Prompt contains terms inappropriate for youth"

                        error_message = (
                            f"⚠️ Dein Prompt wurde blockiert\n\n"
                            f"GRUND: Jugendschutzfilter (13-17 Jahre)\n\n"
                            f"{explanation}\n\n"
                            f"Gefundene Begriffe: {found_terms_str}\n\n"
                            f"WARUM DIESE REGEL?\n"
                            f"Dein Prompt enthält explizite Begriffe, die für Jugendliche ungeeignet sind."
                        )
                        logger.warning(f"[STAGE1] BLOCKED Youth-Filter (LLM confirmed, {llm_time:.1f}s)")
                        return (False, text, error_message, ['§86a', 'age_filter'])

                    elif "§86a StGB" in blocked_parts:
                        parts = blocked_parts.split(" - ", 2)
                        law_reference = parts[0] if len(parts) > 0 else "§86a StGB"
                        symbol = parts[1] if len(parts) > 1 else "extremist content"
                        explanation = parts[2] if len(parts) > 2 else "This content violates German law"

                        error_message = (
                            f"⚠️ Dein Prompt wurde blockiert\n\n"
                            f"GRUND: {law_reference} - {symbol}\n\n"
                            f"{explanation}\n\n"
                            f"WARUM DIESE REGEL?\n"
                            f"Diese Symbole werden benutzt, um Gewalt und Hass zu verbreiten.\n"
                            f"Wir schützen dich und andere vor gefährlichen Inhalten."
                        )
                        logger.warning(f"[STAGE1] BLOCKED §86a (LLM, {llm_time:.1f}s)")
                        return (False, text, error_message, ['§86a'])

                    elif "DSGVO" in blocked_parts:
                        error_message = (
                            f"⚠️ Dein Prompt wurde blockiert\n\n"
                            f"GRUND: DSGVO - Persönliche Daten erkannt\n\n"
                            f"{blocked_parts}\n\n"
                            f"Bitte verwende keine echten Namen, Adressen oder andere persönliche Daten."
                        )
                        logger.warning(f"[STAGE1] BLOCKED DSGVO (LLM, {llm_time:.1f}s)")
                        return (False, text, error_message, ['§86a', 'age_filter', 'dsgvo_llm'])

                    else:
                        error_message = (
                            f"⚠️ Dein Prompt wurde blockiert\n\n"
                            f"GRUND: Sicherheitsfilter\n\n"
                            f"{blocked_parts}"
                        )
                        logger.warning(f"[STAGE1] BLOCKED (unknown type, LLM, {llm_time:.1f}s)")
                        return (False, text, error_message, ['§86a', 'age_filter'])

                elif response.startswith("SAFE:"):
                    # LLM says safe — false positive (e.g., "cute vampire")
                    logger.info(f"[STAGE1] Age-filter false positive confirmed by LLM ({llm_time:.1f}s)")
                    # Fall through to DSGVO check
                else:
                    # Unexpected format — fail-open, fall through to DSGVO check
                    logger.warning(f"[STAGE1] Unexpected LLM response format: {response[:80]}, fail-open")
    else:
        logger.debug(f"[STAGE1] Age-filter skipped (safety_level={safety_level})")

    # ── STEP 3: DSGVO SpaCy NER (~50-100ms) or LLM Fallback ──────────
    # Track which checks we've passed so far
    checks_passed = ['§86a']
    if safety_level not in ('off', 'adult'):
        checks_passed.append('age_filter')

    dsgvo_start = _time.time()
    has_personal_data, found_entities, spacy_available = fast_dsgvo_check(text)
    dsgvo_time = _time.time() - dsgvo_start

    if spacy_available and has_personal_data:
        # SpaCy found personal data → BLOCK
        entities_str = ', '.join(found_entities[:5])
        error_message = (
            f"⚠️ Dein Prompt wurde blockiert\n\n"
            f"GRUND: DSGVO - Persönliche Daten erkannt\n\n"
            f"Folgende persönliche Daten wurden in deinem Prompt gefunden:\n"
            f"{entities_str}\n\n"
            f"WARUM DIESE REGEL?\n"
            f"Der Schutz persönlicher Daten (DSGVO) verbietet die Verarbeitung von Namen, "
            f"Adressen und Kontaktdaten ohne Einwilligung.\n"
            f"Bitte verwende Phantasienamen oder beschreibe Personen ohne echte Namen."
        )
        checks_passed.append('dsgvo_ner')
        logger.warning(f"[STAGE1] BLOCKED DSGVO: {found_entities[:3]} ({dsgvo_time*1000:.1f}ms)")
        return (False, text, error_message, checks_passed)

    elif spacy_available and not has_personal_data:
        # SpaCy clean → SAFE
        checks_passed.append('dsgvo_ner')

    elif not spacy_available:
        # SpaCy NOT available → LLM Fallback for DSGVO check
        logger.warning(f"[STAGE1] SpaCy unavailable → LLM fallback for DSGVO check")
        text_with_metadata = f"[SAFETY: {safety_level}]\n{text}"
        llm_start = _time.time()
        result = await pipeline_executor.execute_pipeline(
            'pre_interception/gpt_oss_safety',
            text_with_metadata,
            execution_mode=execution_mode
        )
        llm_time = _time.time() - llm_start

        if result.success:
            response = result.final_output.strip()
            if response.startswith("BLOCKED:") and "DSGVO" in response:
                error_message = (
                    f"⚠️ Dein Prompt wurde blockiert\n\n"
                    f"GRUND: DSGVO - Persönliche Daten erkannt\n\n"
                    f"{response[8:].strip()}\n\n"
                    f"Bitte verwende Phantasienamen oder beschreibe Personen ohne echte Namen."
                )
                checks_passed.append('dsgvo_llm')
                logger.warning(f"[STAGE1] BLOCKED DSGVO (LLM fallback, {llm_time:.1f}s)")
                return (False, text, error_message, checks_passed)
            elif response.startswith("BLOCKED:"):
                # LLM caught something else (§86a or age) that fast-filter missed
                blocked_parts = response[8:].strip()
                error_message = (
                    f"⚠️ Dein Prompt wurde blockiert\n\n"
                    f"GRUND: Sicherheitsfilter\n\n"
                    f"{blocked_parts}"
                )
                checks_passed.append('dsgvo_llm')
                logger.warning(f"[STAGE1] BLOCKED by LLM fallback: {response[:80]} ({llm_time:.1f}s)")
                return (False, text, error_message, checks_passed)
            else:
                # LLM says safe
                checks_passed.append('dsgvo_llm')
                logger.info(f"[STAGE1] DSGVO LLM fallback: SAFE ({llm_time:.1f}s)")
        else:
            # LLM failed — fail-open but log warning
            checks_passed.append('dsgvo_llm')
            logger.warning(f"[STAGE1] DSGVO LLM fallback failed: {result.error}, continuing (fail-open)")

    # ── ALL CHECKS PASSED ──────────────────────────────────────────────
    total_time = _time.time() - total_start
    logger.info(f"[STAGE1] SAFE ({total_time*1000:.1f}ms total, checks: {checks_passed})")
    return (True, text, None, checks_passed)

async def execute_stage3_safety(
    prompt: str,
    safety_level: str,
    media_type: str,
    execution_mode: str,
    pipeline_executor
) -> Dict[str, Any]:
    """
    Execute Stage 3: Pre-Output Safety Check
    Hybrid: Fast string-match → LLM verification if terms found

    Args:
        prompt: Prompt to check before media generation
        safety_level: 'kids', 'youth', or 'off'
        media_type: Type of media being generated (for logging)
        execution_mode: 'eco' or 'fast'
        pipeline_executor: PipelineExecutor instance

    Returns:
        {
            "safe": bool,
            "method": "fast_filter" | "llm_context_check",
            "abort_reason": str | None,
            "positive_prompt": str | None,
            "negative_prompt": str | None,
            "found_terms": list | None,
            "false_positive": bool | None
        }
    """
    import time

    # STEP 1: ALWAYS translate first (regardless of safety path or level)
    # Translation happens even if safety is 'off'
    translate_start = time.time()
    translate_result = await pipeline_executor.execute_pipeline(
        'pre_output/translation_en',  # Translation config (just translate chunk)
        prompt,
        execution_mode=execution_mode
    )
    translate_time = time.time() - translate_start

    if translate_result.success:
        translated_prompt = translate_result.final_output
        logger.info(f"[STAGE3-TRANSLATION] Translated in {translate_time:.2f}s: {translated_prompt[:150]}...")
    else:
        # Translation failed - use original prompt
        translated_prompt = prompt
        logger.warning(f"[STAGE3-TRANSLATION] Translation failed, using original prompt")

    # If safety is disabled or adult level, return translated prompt without safety check
    if safety_level in ('off', 'adult'):
        return {
            "safe": True,
            "method": "disabled",
            "abort_reason": None,
            "positive_prompt": translated_prompt,
            "negative_prompt": ""
        }

    # STEP 2: HYBRID APPROACH: Fast string-match first
    start_time = time.time()
    has_terms, found_terms = fast_filter_check(translated_prompt, safety_level)
    fast_check_time = time.time() - start_time

    if not has_terms:
        # FAST PATH: No problematic terms → instantly safe (95% of requests)
        logger.info(f"[STAGE3-SAFETY] PASSED (fast-path, {fast_check_time*1000:.1f}ms)")
        return {
            "safe": True,
            "method": "fast_filter",
            "abort_reason": None,
            "positive_prompt": translated_prompt,
            "negative_prompt": "",
            "model_used": None,
            "backend_type": None,
            "execution_time": translate_time + fast_check_time
        }

    # SLOW PATH: Terms found → LLM context verification (prevents false positives)
    logger.info(f"[STAGE3-SAFETY] found terms {found_terms[:3]}... → LLM context check (fast: {fast_check_time*1000:.1f}ms)")

    # Determine which safety check config to use (just safety_check, not translate)
    safety_check_config = f'pre_output/safety_check_{safety_level}'

    llm_start_time = time.time()
    result = await pipeline_executor.execute_pipeline(
        safety_check_config,
        translated_prompt,  # Use already-translated prompt
        execution_mode=execution_mode
    )
    llm_check_time = time.time() - llm_start_time

    # Extract metadata from pipeline result
    model_used = None
    backend_type = None
    if result.steps and len(result.steps) > 0:
        for step in reversed(result.steps):
            if step.metadata:
                model_used = step.metadata.get('model_used', model_used)
                backend_type = step.metadata.get('backend_type', backend_type)
                if model_used and backend_type:
                    break

    if result.success:
        # Parse JSON output
        safety_data = parse_preoutput_json(result.final_output)

        if not safety_data.get('safe', True):
            # UNSAFE: LLM confirmed it's problematic in context
            abort_reason = safety_data.get('abort_reason', 'Content blocked by safety filter')
            logger.warning(f"[STAGE3-SAFETY] BLOCKED by LLM: {abort_reason} (llm: {llm_check_time:.1f}s)")

            return {
                "safe": False,
                "method": "llm_context_check",
                "abort_reason": abort_reason,
                "positive_prompt": None,
                "negative_prompt": None,
                "found_terms": found_terms,
                "model_used": model_used,
                "backend_type": backend_type,
                "execution_time": llm_check_time
            }
        else:
            # SAFE: False positive (e.g., "CD player", "dark chocolate")
            logger.info(f"[STAGE3-SAFETY] PASSED (LLM verified false positive, llm: {llm_check_time:.1f}s)")

            return {
                "safe": True,
                "method": "llm_context_check",
                "abort_reason": None,
                "positive_prompt": translated_prompt,
                "negative_prompt": safety_data.get('negative_prompt', ''),
                "found_terms": found_terms,
                "false_positive": True,
                "model_used": model_used,
                "backend_type": backend_type,
                "execution_time": translate_time + llm_check_time
            }
    else:
        logger.warning(f"[STAGE3-SAFETY] LLM check failed: {result.error}, continuing (fail-open)")
        return {
            "safe": True,
            "method": "llm_check_failed",
            "abort_reason": None,
            "positive_prompt": translated_prompt,
            "negative_prompt": ""
        }


# ============================================================================
# SESSION 84: STAGE 3 SAFETY CHECK FOR CODE OUTPUT
# ============================================================================

async def execute_stage3_safety_code(
    code: str,
    safety_level: str,
    media_type: str,
    execution_mode: str,
    pipeline_executor
) -> dict:
    """
    Stage 3 Safety Check for Code Output (P5.js, SonicPi, etc.)

    Checks generated code for unsafe patterns without translation.
    Uses fast filter + conditional LLM verification.

    Args:
        code: Generated code (JavaScript, Ruby, etc.)
        safety_level: Safety level ('kids', 'youth', 'off')
        media_type: Media type ('code')
        execution_mode: Execution mode ('eco', 'fast')
        pipeline_executor: Pipeline executor for LLM calls

    Returns:
        dict: Safety result with structure:
            {
                'safe': bool,
                'positive_prompt': str (original code if safe),
                'method': str,
                'abort_reason': Optional[str],
                'patterns_found': Optional[List[str]],
                'execution_time': float
            }
    """
    from datetime import datetime

    start_time = datetime.now()

    logger.info(f"[STAGE3-CODE] Safety check for code (level: {safety_level})")

    # If safety is off or adult, skip all checks
    if safety_level in ('off', 'adult'):
        logger.info(f"[STAGE3-CODE] Safety level '{safety_level}' → allowing code")
        return {
            'safe': True,
            'positive_prompt': code,
            'method': 'safety_off',
            'execution_time': (datetime.now() - start_time).total_seconds()
        }

    # Fast filter: Check for dangerous code patterns
    UNSAFE_CODE_PATTERNS = [
        'eval(',
        'Function(',
        'document.cookie',
        'localStorage.',
        'sessionStorage.',
        'fetch(',
        'XMLHttpRequest',
        'import(',
        'require(',
        '<script',
        '</script',
        'innerHTML',
        'outerHTML',
        'document.write',
        'setTimeout(',
        'setInterval('
    ]

    found_patterns = []
    code_lower = code.lower()
    for pattern in UNSAFE_CODE_PATTERNS:
        if pattern.lower() in code_lower:
            found_patterns.append(pattern)

    if not found_patterns:
        # FAST PATH: No unsafe patterns detected
        logger.info(f"[STAGE3-CODE] Safety check passed (fast filter, no patterns found)")
        return {
            'safe': True,
            'positive_prompt': code,
            'method': 'fast_filter',
            'execution_time': (datetime.now() - start_time).total_seconds()
        }

    # SLOW PATH: Unsafe patterns found → LLM context verification
    logger.warning(f"[STAGE3-CODE] Found patterns: {found_patterns} → LLM verification")

    # Create verification prompt
    verification_prompt = f"""You are a code safety analyzer for educational creative coding environments.

A student generated code that contains potentially unsafe patterns: {', '.join(found_patterns)}

Analyze the code and determine:
1. Is this code actually dangerous, or are these patterns used safely?
2. Could this code be executed in a sandboxed iframe without risk?

Code to analyze:
```javascript
{code}
```

Respond with JSON only:
{{
  "safe": true or false,
  "reasoning": "brief explanation",
  "abort_reason": "reason if unsafe, otherwise null"
}}
"""

    # Call LLM for context verification
    try:
        llm_result = await pipeline_executor.execute_chunk_async(
            chunk_name='manipulate',
            inputs={'INPUT_TEXT': verification_prompt},
            execution_mode=execution_mode
        )

        # Parse JSON response
        import json
        import re

        # Extract JSON from response (handle markdown code blocks)
        response_text = llm_result.get('output', '{"safe": false}')
        json_match = re.search(r'\{[^{}]*"safe"[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            response_data = json.loads(json_match.group())
        else:
            response_data = json.loads(response_text)

        is_safe = response_data.get('safe', False)
        abort_reason = response_data.get('abort_reason')

        logger.info(f"[STAGE3-CODE] LLM verification result: safe={is_safe}, reason={abort_reason}")

        return {
            'safe': is_safe,
            'positive_prompt': code if is_safe else '',
            'abort_reason': abort_reason if not is_safe else None,
            'method': 'llm_context_check',
            'patterns_found': found_patterns,
            'execution_time': (datetime.now() - start_time).total_seconds()
        }

    except Exception as e:
        # Fail-open: Allow code if LLM check fails (sandbox provides final protection)
        logger.error(f"[STAGE3-CODE] LLM verification failed: {e} → allowing code (fail-open)")
        return {
            'safe': True,
            'positive_prompt': code,
            'method': 'llm_failed_failopen',
            'patterns_found': found_patterns,
            'execution_time': (datetime.now() - start_time).total_seconds()
        }
