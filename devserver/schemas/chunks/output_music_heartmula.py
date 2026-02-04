"""
Output Chunk: HeartMuLa Music Generation

Generates music from lyrics and style tags using HeartMuLa (heartlib).
This is a Python-based chunk - the code IS the chunk.

Input (from Stage 2/3 or direct):
    - lyrics (TEXT_1): Song lyrics with [Verse], [Chorus], [Bridge] markers
    - tags (TEXT_2): Comma-separated style tags (genre, mood, instruments)

Output:
    - MP3 audio bytes

Usage:
    result = await execute(lyrics="[Verse] Hello...", tags="pop, upbeat")
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Chunk metadata (replaces JSON meta section)
CHUNK_META = {
    "name": "output_music_heartmula",
    "media_type": "music",
    "output_format": "mp3",
    "estimated_duration_seconds": "120-300",
    "requires_gpu": True,
    "gpu_vram_mb": 16000,
    "supported_languages": ["en", "zh", "ja", "ko", "es"]
}

# Default parameters (replaces JSON input_mappings defaults)
# IMPORTANT: max_audio_length_ms must match HeartMuLa's training (120s max)
# Longer audio causes CUDA out-of-bounds errors in codec
DEFAULTS = {
    "temperature": 1.0,
    "topk": 50,
    "cfg_scale": 1.5,
    "max_audio_length_ms": 120000,  # 2 minutes (HeartMuLa standard, DO NOT EXCEED)
    "seed": None  # None = random
}


async def execute(
    lyrics: str = None,
    tags: str = "",
    TEXT_1: str = None,  # Pipeline convention: first text input
    TEXT_2: str = None,  # Pipeline convention: second text input
    temperature: float = None,
    topk: int = None,
    cfg_scale: float = None,
    max_audio_length_ms: int = None,
    seed: int = None,
    **kwargs  # Ignore extra parameters from pipeline
) -> bytes:
    """
    Execute HeartMuLa music generation.

    Args:
        lyrics: Song lyrics with structure markers [Verse], [Chorus], [Bridge]
        tags: Comma-separated style tags (genre, mood, instruments, tempo)
        temperature: Creativity (0.1-2.0)
        topk: Token sampling parameter
        cfg_scale: Classifier-free guidance scale
        max_audio_length_ms: Maximum audio length in milliseconds
        seed: Seed for reproducibility (None = random)

    Returns:
        MP3 audio bytes (ready for storage/response)

    Raises:
        Exception: If generation fails or backend unavailable
    """
    from my_app.services.heartmula_backend import get_heartmula_backend
    from config import HEARTMULA_ENABLED
    import random

    # Map pipeline convention (TEXT_1, TEXT_2) to semantic names
    if lyrics is None and TEXT_1 is not None:
        lyrics = TEXT_1
    if not tags and TEXT_2 is not None:
        tags = TEXT_2

    # Apply defaults
    temperature = temperature if temperature is not None else DEFAULTS["temperature"]
    topk = topk if topk is not None else DEFAULTS["topk"]
    cfg_scale = cfg_scale if cfg_scale is not None else DEFAULTS["cfg_scale"]
    max_audio_length_ms = max_audio_length_ms if max_audio_length_ms is not None else DEFAULTS["max_audio_length_ms"]

    # Handle seed
    if seed is None or seed == "random":
        seed = random.randint(0, 2**32 - 1)

    logger.info(f"[CHUNK:heartmula] Executing with lyrics={len(lyrics)} chars")
    logger.info(f"[CHUNK:heartmula] Tags (full): '{tags}'")
    logger.info(f"[CHUNK:heartmula] Parameters: temp={temperature}, topk={topk}, cfg={cfg_scale}, max_ms={max_audio_length_ms}, seed={seed}")

    # Check if HeartMuLa is enabled
    if not HEARTMULA_ENABLED:
        logger.error("[CHUNK:heartmula] Backend disabled in config")
        raise Exception("HeartMuLa backend is disabled (HEARTMULA_ENABLED=false)")

    # Get backend
    backend = get_heartmula_backend()

    # Check availability
    if not await backend.is_available():
        logger.error("[CHUNK:heartmula] Backend not available")
        raise Exception("HeartMuLa not available. Check heartlib installation and model files.")

    # Validate input
    if not lyrics or not lyrics.strip():
        logger.error("[CHUNK:heartmula] No lyrics provided")
        raise ValueError("No lyrics provided for music generation")

    # Validate lyrics length (HeartMuLa has token limits)
    MAX_LYRICS_CHARS = 2000  # Conservative limit
    if len(lyrics) > MAX_LYRICS_CHARS:
        logger.warning(f"[CHUNK:heartmula] Lyrics too long ({len(lyrics)} chars), truncating to {MAX_LYRICS_CHARS}")
        lyrics = lyrics[:MAX_LYRICS_CHARS]

    # Validate tags (keep simple like HeartMuLa examples: "piano,happy")
    MAX_TAGS_CHARS = 200  # HeartMuLa expects simple tags
    if tags and len(tags) > MAX_TAGS_CHARS:
        logger.warning(f"[CHUNK:heartmula] Tags too long ({len(tags)} chars), truncating to {MAX_TAGS_CHARS}")
        tags = tags[:MAX_TAGS_CHARS]
        # Ensure we don't cut mid-tag
        if ',' in tags:
            tags = ','.join(tags.split(',')[:-1])  # Remove partial last tag

    # Generate music
    audio_bytes = await backend.generate_music(
        lyrics=lyrics,
        tags=tags,
        temperature=temperature,
        topk=topk,
        cfg_scale=cfg_scale,
        max_audio_length_ms=max_audio_length_ms,
        seed=seed,
        output_format="mp3"
    )

    if audio_bytes is None:
        logger.error("[CHUNK:heartmula] Generation returned None")
        raise Exception("Music generation failed")

    logger.info(f"[CHUNK:heartmula] Generated {len(audio_bytes)} bytes (seed={seed})")

    # Return raw bytes - backend_router will wrap them properly
    return audio_bytes
