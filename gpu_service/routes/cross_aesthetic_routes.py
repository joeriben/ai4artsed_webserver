"""
GPU Service Cross-Aesthetic Routes

REST endpoints for cross-aesthetic generation experiments.
Implements three strategies exploiting the modality indifference of generative AI.
"""

import asyncio
import base64
import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

cross_aesthetic_bp = Blueprint('cross_aesthetic', __name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _get_backend():
    from services.cross_aesthetic_backend import get_cross_aesthetic_backend
    return get_cross_aesthetic_backend()


@cross_aesthetic_bp.route('/api/cross_aesthetic/available', methods=['GET'])
def available():
    """Check if cross-aesthetic generation is available."""
    try:
        from config import CROSS_AESTHETIC_ENABLED
        if not CROSS_AESTHETIC_ENABLED:
            return jsonify({"available": False, "reason": "disabled"})
        return jsonify({"available": True})
    except Exception as e:
        return jsonify({"available": False, "reason": str(e)})


@cross_aesthetic_bp.route('/api/cross_aesthetic/image_to_audio', methods=['POST'])
def image_to_audio():
    """Strategy A: CLIP image embeddings → Stable Audio conditioning.

    Request JSON:
        image_base64: str (required) - base64-encoded image
        duration_seconds: float (default 10.0)
        steps: int (default 100)
        cfg_scale: float (default 7.0)
        seed: int (default -1)

    Returns: { success, audio_base64, seed, strategy_info }
    """
    data = request.get_json()
    if not data or 'image_base64' not in data:
        return jsonify({"success": False, "error": "image_base64 required"}), 400

    try:
        image_bytes = base64.b64decode(data['image_base64'])
    except Exception:
        return jsonify({"success": False, "error": "Invalid base64 image data"}), 400

    seed = int(data.get('seed', -1))
    duration = float(data.get('duration_seconds', 10.0))

    backend = _get_backend()
    audio_bytes = _run_async(backend.image_to_audio(
        image_bytes=image_bytes,
        duration_seconds=duration,
        steps=int(data.get('steps', 100)),
        cfg_scale=float(data.get('cfg_scale', 7.0)),
        seed=seed,
    ))

    if audio_bytes is None:
        return jsonify({"success": False, "error": "Cross-aesthetic generation failed"}), 500

    return jsonify({
        "success": True,
        "audio_base64": base64.b64encode(audio_bytes).decode('utf-8'),
        "seed": seed,
        "duration_seconds": duration,
        "strategy_info": {
            "strategy": "A",
            "description": "CLIP image embeddings injected as Stable Audio conditioning",
            "clip_model": backend.clip_model_id,
            "embedding_flow": "image → CLIP [1,256,768] → pool [1,128,768] → Stable Audio DiT",
        },
    })


@cross_aesthetic_bp.route('/api/cross_aesthetic/shared_seed', methods=['POST'])
def shared_seed():
    """Strategy B: Same noise seed → parallel image + audio generation.

    Request JSON:
        prompt: str (required)
        seed: int (default 42)
        image_params: dict (optional) - { model_id, width, height, steps, cfg_scale }
        audio_params: dict (optional) - { duration_seconds, steps, cfg_scale }

    Returns: { success, image_base64, audio_base64, seed, strategy_info }
    """
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"success": False, "error": "prompt required"}), 400

    seed = int(data.get('seed', 42))
    img_params = data.get('image_params', {})
    aud_params = data.get('audio_params', {})

    backend = _get_backend()
    image_bytes, audio_bytes = _run_async(backend.shared_seed(
        prompt=data['prompt'],
        seed=seed,
        image_model=img_params.get('model_id', 'stabilityai/stable-diffusion-3.5-large'),
        image_width=int(img_params.get('width', 1024)),
        image_height=int(img_params.get('height', 1024)),
        image_steps=int(img_params.get('steps', 25)),
        image_cfg=float(img_params.get('cfg_scale', 4.5)),
        audio_duration=float(aud_params.get('duration_seconds', 10.0)),
        audio_steps=int(aud_params.get('steps', 100)),
        audio_cfg=float(aud_params.get('cfg_scale', 7.0)),
    ))

    if image_bytes is None and audio_bytes is None:
        return jsonify({"success": False, "error": "Both generations failed"}), 500

    result = {
        "success": True,
        "seed": seed,
        "strategy_info": {
            "strategy": "B",
            "description": "Same noise seed, different learned dynamics",
        },
    }

    if image_bytes:
        result["image_base64"] = base64.b64encode(image_bytes).decode('utf-8')
    if audio_bytes:
        result["audio_base64"] = base64.b64encode(audio_bytes).decode('utf-8')

    return jsonify(result)


@cross_aesthetic_bp.route('/api/cross_aesthetic/cross_decode', methods=['POST'])
def cross_decode():
    """Strategy C: Generate in one modality, decode with the other's VAE.

    Request JSON:
        prompt: str (required)
        direction: str ("image_to_audio" or "audio_to_image")
        seed: int (default 42)
        image_params: dict (optional) - { steps, cfg_scale }
        audio_params: dict (optional) - { duration_seconds, steps, cfg_scale }

    Returns: { success, output_base64, output_type, seed, strategy_info }
    """
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"success": False, "error": "prompt required"}), 400

    direction = data.get('direction', 'image_to_audio')
    seed = int(data.get('seed', 42))
    img_params = data.get('image_params', {})
    aud_params = data.get('audio_params', {})

    backend = _get_backend()
    output_bytes = _run_async(backend.cross_decode(
        prompt=data['prompt'],
        direction=direction,
        seed=seed,
        image_steps=int(img_params.get('steps', 25)),
        image_cfg=float(img_params.get('cfg_scale', 4.5)),
        audio_duration=float(aud_params.get('duration_seconds', 10.0)),
        audio_steps=int(aud_params.get('steps', 100)),
        audio_cfg=float(aud_params.get('cfg_scale', 7.0)),
    ))

    if output_bytes is None:
        return jsonify({"success": False, "error": "Cross-decoding failed"}), 500

    output_type = "audio" if direction == "image_to_audio" else "image"

    return jsonify({
        "success": True,
        "output_base64": base64.b64encode(output_bytes).decode('utf-8'),
        "output_type": output_type,
        "seed": seed,
        "strategy_info": {
            "strategy": "C",
            "description": f"Latent cross-decoding: {direction}",
            "direction": direction,
            "warning": "Experimental — output may be chaotic/glitchy (intentional)",
        },
    })
