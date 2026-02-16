"""
Cross-Aesthetic Routes — DevServer proxy to GPU service

Crossmodal Lab v2: Thin JSON proxy for crossmodal generation experiments.
Frontend calls /api/cross_aesthetic/* -> DevServer -> GPU service (port 17803).

Endpoints:
- GET  /api/cross_aesthetic/available          - Health check + backend status
- POST /api/cross_aesthetic/synth              - Latent Audio Synth
- POST /api/cross_aesthetic/image_guided_audio - ImageBind gradient guidance
- POST /api/cross_aesthetic/mmaudio            - MMAudio image/text to audio
"""

import logging
import requests as http_requests

from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

cross_aesthetic_bp = Blueprint('cross_aesthetic', __name__, url_prefix='/api/cross_aesthetic')


def _proxy_get(path: str):
    """Forward GET to GPU service, return JSON."""
    from config import GPU_SERVICE_URL
    url = f"{GPU_SERVICE_URL.rstrip('/')}{path}"
    try:
        resp = http_requests.get(url, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except http_requests.ConnectionError:
        return jsonify({"available": False, "error": "GPU service unreachable"}), 503
    except Exception as e:
        return jsonify({"available": False, "error": str(e)}), 500


def _proxy_post(path: str):
    """Forward POST JSON to GPU service, return JSON response as-is."""
    from config import GPU_SERVICE_URL, GPU_SERVICE_TIMEOUT
    url = f"{GPU_SERVICE_URL.rstrip('/')}{path}"
    data = request.get_json() or {}
    try:
        resp = http_requests.post(url, json=data, timeout=GPU_SERVICE_TIMEOUT)
        return jsonify(resp.json()), resp.status_code
    except http_requests.ConnectionError:
        return jsonify({"success": False, "error": "GPU service unreachable"}), 503
    except http_requests.Timeout:
        return jsonify({"success": False, "error": "GPU service timeout"}), 504
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cross_aesthetic_bp.route('/available', methods=['GET'])
def available():
    return _proxy_get('/api/cross_aesthetic/available')


@cross_aesthetic_bp.route('/synth', methods=['POST'])
def synth():
    return _proxy_post('/api/cross_aesthetic/synth')


@cross_aesthetic_bp.route('/image_guided_audio', methods=['POST'])
def image_guided_audio():
    return _proxy_post('/api/cross_aesthetic/image_guided_audio')


@cross_aesthetic_bp.route('/mmaudio', methods=['POST'])
def mmaudio():
    return _proxy_post('/api/cross_aesthetic/mmaudio')
