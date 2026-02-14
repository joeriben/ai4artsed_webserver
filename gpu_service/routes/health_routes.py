"""
GPU Service Health Routes

Provides health check, GPU info, and loaded model status.
"""

import logging
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check with GPU and model status."""
    try:
        import torch

        gpu_info = {}
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            allocated = torch.cuda.memory_allocated(0) / 1024**3
            reserved = torch.cuda.memory_reserved(0) / 1024**3
            total = props.total_memory / 1024**3
            gpu_info = {
                "gpu_name": props.name,
                "total_vram_gb": round(total, 2),
                "allocated_gb": round(allocated, 2),
                "reserved_gb": round(reserved, 2),
                "free_gb": round(total - reserved, 2),
            }

        # Get loaded models from diffusers backend
        loaded_models = []
        try:
            from services.diffusers_backend import get_diffusers_backend
            backend = get_diffusers_backend()
            loaded_models = list(backend._pipelines.keys())
        except Exception:
            pass

        # Check HeartMuLa status
        heartmula_loaded = False
        try:
            from services.heartmula_backend import get_heartmula_backend
            hm = get_heartmula_backend()
            heartmula_loaded = hm._is_loaded
        except Exception:
            pass

        return jsonify({
            "status": "ok",
            "gpu": gpu_info,
            "loaded_models": loaded_models,
            "heartmula_loaded": heartmula_loaded,
        })

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500
