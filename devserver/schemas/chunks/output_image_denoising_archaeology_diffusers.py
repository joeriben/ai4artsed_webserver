"""
Output Chunk: Denoising Archaeology (Diffusers)

Generates image with step-by-step denoising visualization.
Captures VAE-decoded intermediates at every sampling step.
This is a Python-based chunk - the code IS the chunk.

Input: prompt (TEXT_1)
Output: dict with final image + per-step JPEG thumbnails
"""

import logging

logger = logging.getLogger(__name__)

CHUNK_META = {
    "name": "output_image_denoising_archaeology_diffusers",
    "media_type": "image",
    "output_format": "png",
    "estimated_duration_seconds": "35-55",
    "requires_gpu": True,
    "gpu_vram_mb": 8000,
}

DEFAULTS = {
    "steps": 25,
    "cfg": 4.5,
    "negative_prompt": "",
    "seed": None,
    "capture_every_n": 1,
}


async def execute(
    prompt: str = None,
    TEXT_1: str = None,
    negative_prompt: str = None,
    steps: int = None,
    cfg: float = None,
    seed: int = None,
    **kwargs
) -> dict:
    """Returns dict (not bytes) - uses extended Python chunk dict-return path."""
    from my_app.services.diffusers_backend import get_diffusers_backend

    prompt = prompt or TEXT_1
    steps = steps if steps is not None else DEFAULTS["steps"]
    cfg = cfg if cfg is not None else DEFAULTS["cfg"]
    negative_prompt = negative_prompt or DEFAULTS["negative_prompt"]

    if not prompt or not prompt.strip():
        raise ValueError("No prompt provided for denoising archaeology")

    backend = get_diffusers_backend()
    result = await backend.generate_image_with_archaeology(
        prompt=prompt,
        negative_prompt=negative_prompt,
        steps=steps,
        cfg_scale=cfg,
        seed=seed if seed is not None else -1,
        capture_every_n=DEFAULTS["capture_every_n"],
    )

    if result is None:
        raise Exception("Denoising archaeology generation failed")

    return {
        'content_marker': 'diffusers_archaeology_generated',
        'image_data': result['image_base64'],
        'archaeology_data': {
            'step_images': result['step_images'],
            'total_steps': result['total_steps'],
            'seed': result['seed'],
        },
        'seed': result['seed'],
    }
