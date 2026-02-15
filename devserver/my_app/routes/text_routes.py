"""
Text Routes — DevServer proxy to GPU service's Latent Text Lab

Session 176: Proxies REST + SSE endpoints for dekonstruktive LLM operations.
Session 177: Added rep-engineering, compare, bias-probe endpoints.
Frontend calls /api/text/* → DevServer → GPU service (port 17803).

Endpoints:
- GET  /api/text/models - List loaded models
- GET  /api/text/presets - List available model presets
- POST /api/text/load - Load model
- POST /api/text/unload - Unload model
- POST /api/text/embedding - Get prompt embedding
- POST /api/text/interpolate - Interpolate between prompts
- POST /api/text/attention - Get attention maps
- POST /api/text/rep-engineering - Representation Engineering (Zou 2023)
- POST /api/text/compare - Comparative Model Archaeology
- POST /api/text/bias-probe - Bias Archaeology
- POST /api/text/generate - Generate with token surgery
- POST /api/text/generate/stream - SSE streaming generation
- POST /api/text/variations - Generate seed variations
- POST /api/text/layers - Compare layer outputs
"""

import logging
import asyncio
import json

from flask import Blueprint, request, jsonify, Response, stream_with_context

logger = logging.getLogger(__name__)

text_bp = Blueprint('text', __name__, url_prefix='/api/text')


def _run_async(coro):
    """Run async coroutine in sync Flask context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _get_client():
    """Get TextClient singleton (lazy import)."""
    from my_app.services.text_client import get_text_client
    return get_text_client()


# =============================================================================
# Model Management
# =============================================================================

@text_bp.route('/models', methods=['GET'])
def list_models():
    """List currently loaded models."""
    client = _get_client()
    models = _run_async(client.get_loaded_models())
    return jsonify({"models": models})


@text_bp.route('/presets', methods=['GET'])
def list_presets():
    """List available model presets."""
    client = _get_client()
    presets = _run_async(client.get_presets())
    return jsonify({"presets": presets})


@text_bp.route('/load', methods=['POST'])
def load_model():
    """Load an LLM model."""
    data = request.get_json() or {}
    model_id = data.get("model_id")
    quantization = data.get("quantization")

    if not model_id:
        return jsonify({"error": "model_id required"}), 400

    client = _get_client()
    result = _run_async(client.load_model(model_id, quantization))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/unload', methods=['POST'])
def unload_model():
    """Unload a specific model."""
    data = request.get_json() or {}
    model_id = data.get("model_id")

    if not model_id:
        return jsonify({"error": "model_id required"}), 400

    client = _get_client()
    result = _run_async(client.unload_model(model_id))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


# =============================================================================
# Dekonstruktive Operations
# =============================================================================

@text_bp.route('/embedding', methods=['POST'])
def get_embedding():
    """Get embedding representation of a prompt."""
    data = request.get_json() or {}
    text = data.get("text")
    model_id = data.get("model_id")
    layer = data.get("layer", -1)

    if not text or not model_id:
        return jsonify({"error": "text and model_id required"}), 400

    client = _get_client()
    result = _run_async(client.get_prompt_embedding(text, model_id, layer))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/interpolate', methods=['POST'])
def interpolate_prompts():
    """Analyze embedding space between two prompts."""
    data = request.get_json() or {}
    prompt_a = data.get("prompt_a")
    prompt_b = data.get("prompt_b")
    model_id = data.get("model_id")
    steps = data.get("steps", 5)
    layer = data.get("layer", -1)

    if not prompt_a or not prompt_b or not model_id:
        return jsonify({"error": "prompt_a, prompt_b, and model_id required"}), 400

    client = _get_client()
    result = _run_async(client.interpolate_prompts(prompt_a, prompt_b, model_id, steps, layer))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/attention', methods=['POST'])
def get_attention():
    """Get attention patterns for visualization."""
    data = request.get_json() or {}
    text = data.get("text")
    model_id = data.get("model_id")
    layer = data.get("layer")
    head = data.get("head")

    if not text or not model_id:
        return jsonify({"error": "text and model_id required"}), 400

    client = _get_client()
    result = _run_async(client.get_attention_map(text, model_id, layer, head))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/rep-engineering', methods=['POST'])
def rep_engineering():
    """Representation Engineering: concept directions via contrast pairs."""
    data = request.get_json() or {}
    contrast_pairs = data.get("contrast_pairs")
    model_id = data.get("model_id")

    if not contrast_pairs or not model_id:
        return jsonify({"error": "contrast_pairs and model_id required"}), 400

    client = _get_client()
    result = _run_async(client.rep_engineering(
        contrast_pairs=contrast_pairs,
        model_id=model_id,
        target_layer=data.get("target_layer", -1),
        test_text=data.get("test_text"),
        alpha=data.get("alpha", 1.0),
        max_new_tokens=data.get("max_new_tokens", 50),
        temperature=data.get("temperature", 0.7),
        seed=data.get("seed", -1),
    ))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/compare', methods=['POST'])
def compare_models():
    """Compare two models' internal representations."""
    data = request.get_json() or {}
    text = data.get("text")
    model_id_a = data.get("model_id_a")
    model_id_b = data.get("model_id_b")

    if not text or not model_id_a or not model_id_b:
        return jsonify({"error": "text, model_id_a, and model_id_b required"}), 400

    client = _get_client()
    result = _run_async(client.compare_models(
        text=text,
        model_id_a=model_id_a,
        model_id_b=model_id_b,
        max_new_tokens=data.get("max_new_tokens", 50),
        temperature=data.get("temperature", 0.7),
        seed=data.get("seed", 42),
    ))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/bias-probe', methods=['POST'])
def bias_probe():
    """Systematic bias probing through controlled token manipulation."""
    data = request.get_json() or {}
    prompt = data.get("prompt")
    model_id = data.get("model_id")

    if not prompt or not model_id:
        return jsonify({"error": "prompt and model_id required"}), 400

    client = _get_client()
    result = _run_async(client.bias_probe(
        prompt=prompt,
        model_id=model_id,
        bias_type=data.get("bias_type", "gender"),
        custom_boost=data.get("custom_boost"),
        custom_suppress=data.get("custom_suppress"),
        num_samples=data.get("num_samples", 3),
        max_new_tokens=data.get("max_new_tokens", 50),
        temperature=data.get("temperature", 0.7),
        seed=data.get("seed", 42),
    ))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/generate', methods=['POST'])
def generate_with_surgery():
    """Generate text with token-level logit manipulation."""
    data = request.get_json() or {}
    prompt = data.get("prompt")
    model_id = data.get("model_id")

    if not prompt or not model_id:
        return jsonify({"error": "prompt and model_id required"}), 400

    client = _get_client()
    result = _run_async(client.generate_with_token_surgery(
        prompt=prompt,
        model_id=model_id,
        boost_tokens=data.get("boost_tokens"),
        suppress_tokens=data.get("suppress_tokens"),
        boost_factor=data.get("boost_factor", 2.0),
        max_new_tokens=data.get("max_new_tokens", 50),
        temperature=data.get("temperature", 0.7),
        seed=data.get("seed", -1),
    ))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/generate/stream', methods=['POST'])
def generate_streaming():
    """SSE streaming generation — proxy raw bytes from GPU service."""
    data = request.get_json() or {}
    prompt = data.get("prompt")
    model_id = data.get("model_id")

    if not prompt or not model_id:
        return jsonify({"error": "prompt and model_id required"}), 400

    import requests as http_requests
    from config import GPU_SERVICE_URL

    gpu_url = f"{GPU_SERVICE_URL.rstrip('/')}/api/text/generate/stream"

    def proxy_stream():
        try:
            with http_requests.post(gpu_url, json=data, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        yield line.decode('utf-8') + '\n\n'
        except http_requests.ConnectionError:
            yield f"data: {json.dumps({'type': 'error', 'message': 'GPU service unreachable'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(
        stream_with_context(proxy_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


@text_bp.route('/variations', methods=['POST'])
def generate_variations():
    """Generate deterministic variations with different seeds."""
    data = request.get_json() or {}
    prompt = data.get("prompt")
    model_id = data.get("model_id")

    if not prompt or not model_id:
        return jsonify({"error": "prompt and model_id required"}), 400

    client = _get_client()
    result = _run_async(client.generate_variations(
        prompt=prompt,
        model_id=model_id,
        num_variations=data.get("num_variations", 5),
        temperature=data.get("temperature", 0.8),
        base_seed=data.get("base_seed", 42),
        max_new_tokens=data.get("max_new_tokens", 50),
    ))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


@text_bp.route('/layers', methods=['POST'])
def compare_layers():
    """Analyze how representations change through layers."""
    data = request.get_json() or {}
    text = data.get("text")
    model_id = data.get("model_id")

    if not text or not model_id:
        return jsonify({"error": "text and model_id required"}), 400

    client = _get_client()
    result = _run_async(client.compare_layer_outputs(text, model_id))

    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)
