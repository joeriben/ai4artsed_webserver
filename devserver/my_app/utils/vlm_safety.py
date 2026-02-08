"""
VLM Safety Check — Image safety via local VLM (Ollama).

Extracted from schema_pipeline_routes.py to be reusable for both
post-generation checks and input image upload checks.
"""

import base64
import logging
from pathlib import Path

import requests
import config

logger = logging.getLogger(__name__)

VLM_PROMPTS = {
    'kids': (
        'Is the image free of violence, nudity, unsettling, scaring, '
        'potentially traumatizing, or other content unsafe or unhealthy '
        'for children age 6-12 years? Provide a clear decision: "safe" or "unsafe".'
    ),
    'youth': (
        'Is the image free of violence, nudity, unsettling, scaring, '
        'potentially traumatizing, or other content unsafe or unhealthy '
        'for teenagers age 14-18 years? Provide a clear decision: "safe" or "unsafe".'
    ),
}


def vlm_safety_check(image_path: str | Path, safety_level: str) -> tuple[bool, str, str]:
    """
    Check image safety via qwen3-vl. Returns (is_safe, reason, description). Fail-open.

    Args:
        image_path: Path to the image file on disk.
        safety_level: 'kids' or 'youth' (only these trigger VLM check).

    Returns:
        (is_safe, reason, description) — description is the VLM's image analysis.
        (True, '', '') on safe or error (fail-open).
    """
    try:
        image_path = Path(image_path)
        if not image_path.exists():
            logger.warning("[VLM-SAFETY] Image file not found — skipping check")
            return (True, '', '')

        prompt_text = VLM_PROMPTS.get(safety_level)
        if not prompt_text:
            return (True, '', '')

        image_bytes = image_path.read_bytes()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        ollama_url = f"{config.OLLAMA_API_BASE_URL}/api/chat"
        payload = {
            'model': config.VLM_SAFETY_MODEL,
            'messages': [{
                'role': 'user',
                'content': prompt_text,
                'images': [image_b64]
            }],
            'stream': False,
            'options': {
                'temperature': 0.0,
                'num_predict': 2000
            },
            'keep_alive': '10m'
        }

        logger.info(f"[VLM-SAFETY] Checking image ({len(image_bytes)} bytes) with {config.VLM_SAFETY_MODEL} for safety_level={safety_level}")

        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()

        response_json = response.json()
        message = response_json.get('message', {})

        # qwen3 uses thinking mode: answer may be in 'content' or 'thinking'
        content = message.get('content', '').lower().strip()
        thinking = message.get('thinking', '').lower().strip()
        combined = content or thinking
        logger.info(f"[VLM-SAFETY] Model response: content={content!r}, thinking={thinking!r}")

        # Use thinking as image description (it contains the VLM's analysis)
        description = message.get('thinking', '').strip()

        if 'unsafe' in combined:
            return (False, f"VLM safety check ({config.VLM_SAFETY_MODEL}): image flagged as unsafe for {safety_level}", description)
        return (True, '', description)

    except Exception as e:
        # Fail-open: VLM failure should never block
        logger.warning(f"[VLM-SAFETY] Error during check (fail-open): {e}")
        return (True, '', '')
