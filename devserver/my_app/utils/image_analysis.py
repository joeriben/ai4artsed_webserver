"""
Universal Image Analysis Helper
Reusable function for analyzing images with vision models
"""

import base64
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def analyze_image(
    image_path: str,
    prompt: Optional[str] = None,
    analysis_type: str = 'bildwissenschaftlich'
) -> str:
    """
    Analyze image using Ollama vision model

    Args:
        image_path: Path to image file OR base64-encoded image string
        prompt: Analysis prompt. If None, uses default from config.py
                based on analysis_type + DEFAULT_LANGUAGE.
                Fallback: "Analyze this image thoroughly."
        analysis_type: Analysis framework to use:
            - 'bildungstheoretisch': Jörissen/Marotzki (Bildungspotenziale)
            - 'bildwissenschaftlich': Panofsky (art-historical, default)
            - 'ethisch': Ethical analysis
            - 'kritisch': Decolonial & critical media studies

    Returns:
        Analysis text from vision model

    Raises:
        FileNotFoundError: If image_path is file path and doesn't exist
        Exception: If Ollama request fails
    """
    # Import here to avoid circular dependencies
    from config import (
        IMAGE_ANALYSIS_MODEL,
        DEFAULT_LANGUAGE,
        IMAGE_ANALYSIS_PROMPTS
    )
    import requests

    # Step 1: Load image as base64
    if ',' in image_path and image_path.startswith('data:image'):
        # Already base64 with data URL prefix
        image_data = image_path.split(',', 1)[-1]
    elif Path(image_path).exists():
        # File path - load and encode
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
    else:
        # Assume it's already base64 string
        image_data = image_path

    # Step 2: Get prompt with fallback cascade
    if prompt is None:
        try:
            # Try to get from config based on analysis_type + language
            prompt = IMAGE_ANALYSIS_PROMPTS[analysis_type][DEFAULT_LANGUAGE]
        except (KeyError, ImportError, AttributeError):
            # Fallback if prompts not in config or invalid analysis_type
            prompt = "Analyze this image thoroughly."
            logger.warning(f"Analysis prompt not found for {analysis_type}/{DEFAULT_LANGUAGE}, using fallback")

    # Step 3: Call Ollama directly
    payload = {
        "model": IMAGE_ANALYSIS_MODEL,
        "prompt": prompt,
        "images": [image_data],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 2000
        },
        "keep_alive": "0s"  # Unload model after use (save VRAM)
    }

    logger.info(f"[IMAGE-ANALYSIS] Analyzing image with {IMAGE_ANALYSIS_MODEL}")

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        analysis_text = result.get("response", "").strip()

        if not analysis_text:
            raise Exception("Empty response from Ollama")

        logger.info(f"[IMAGE-ANALYSIS] Analysis complete ({len(analysis_text)} chars)")
        return analysis_text

    except Exception as e:
        logger.error(f"[IMAGE-ANALYSIS] Failed: {e}")
        raise


def analyze_image_from_run(
    run_id: str,
    prompt: Optional[str] = None,
    analysis_type: str = 'bildwissenschaftlich'
) -> str:
    """
    Convenience function: Analyze image from LivePipelineRecorder run_id

    Args:
        run_id: Run ID from LivePipelineRecorder
        prompt: Analysis prompt (optional, uses default if None)
        analysis_type: Analysis framework (bildungstheoretisch/bildwissenschaftlich/ethisch/kritisch)

    Returns:
        Analysis text

    Raises:
        FileNotFoundError: If run_id not found or no image in run
    """
    from my_app.utils.live_pipeline_recorder import LivePipelineRecorder

    # Load recorder
    recorder = LivePipelineRecorder.load(run_id)
    if not recorder:
        raise FileNotFoundError(f"Run ID not found: {run_id}")

    # Find image entity
    entities = recorder.metadata.get('entities', [])
    image_entity = next(
        (e for e in entities if e.get('type') == 'image'),
        None
    )

    if not image_entity:
        raise FileNotFoundError(f"No image found in run {run_id}")

    # Session 130: Use get_file_path() for final/ subfolder
    image_path = recorder.get_file_path(image_entity['filename'])

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    logger.info(f"[IMAGE-ANALYSIS] Loading image from run {run_id}: {image_path}")

    # Analyze
    return analyze_image(str(image_path), prompt, analysis_type)
