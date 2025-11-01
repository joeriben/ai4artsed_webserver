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

logger = logging.getLogger(__name__)

# ============================================================================
# HYBRID SAFETY: Fast String-Matching + LLM Context Verification
# ============================================================================

# Cache for filter terms (loaded once at module level)
_FILTER_TERMS_CACHE: Optional[Dict[str, List[str]]] = None

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

def fast_filter_check(prompt: str, safety_level: str) -> Tuple[bool, List[str]]:
    """
    Fast string-matching against filter lists (~0.001s)

    Returns:
        (has_terms, found_terms) - True if problematic terms found
    """
    filter_terms = load_filter_terms()
    terms_list = filter_terms.get(safety_level, [])

    if not terms_list:
        logger.warning(f"No filter terms for safety_level '{safety_level}'")
        return (False, [])

    prompt_lower = prompt.lower()
    found_terms = [term for term in terms_list if term.lower() in prompt_lower]

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

    if safety_level == 'off':
        return {
            "safe": True,
            "method": "disabled",
            "abort_reason": None,
            "positive_prompt": prompt,
            "negative_prompt": ""
        }

    # HYBRID APPROACH: Fast string-match first
    start_time = time.time()
    has_terms, found_terms = fast_filter_check(prompt, safety_level)
    fast_check_time = time.time() - start_time

    if not has_terms:
        # FAST PATH: No problematic terms → instantly safe (95% of requests)
        logger.info(f"[STAGE3-SAFETY] PASSED (fast-path, {fast_check_time*1000:.1f}ms)")
        return {
            "safe": True,
            "method": "fast_filter",
            "abort_reason": None,
            "positive_prompt": prompt,
            "negative_prompt": ""
        }

    # SLOW PATH: Terms found → LLM context verification (prevents false positives)
    logger.info(f"[STAGE3-SAFETY] found terms {found_terms[:3]}... → LLM context check (fast: {fast_check_time*1000:.1f}ms)")

    # Determine which pre-output config to use
    pre_output_config = f'text_safety_check_{safety_level}'

    llm_start_time = time.time()
    result = await pipeline_executor.execute_pipeline(
        pre_output_config,
        prompt,
        execution_mode=execution_mode
    )
    llm_check_time = time.time() - llm_start_time

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
                "found_terms": found_terms
            }
        else:
            # SAFE: False positive (e.g., "CD player", "dark chocolate")
            logger.info(f"[STAGE3-SAFETY] PASSED (LLM verified false positive, llm: {llm_check_time:.1f}s)")

            return {
                "safe": True,
                "method": "llm_context_check",
                "abort_reason": None,
                "positive_prompt": safety_data.get('positive_prompt', prompt),
                "negative_prompt": safety_data.get('negative_prompt', ''),
                "found_terms": found_terms,
                "false_positive": True
            }
    else:
        logger.warning(f"[STAGE3-SAFETY] LLM check failed: {result.error}, continuing (fail-open)")
        return {
            "safe": True,
            "method": "llm_check_failed",
            "abort_reason": None,
            "positive_prompt": prompt,
            "negative_prompt": ""
        }
