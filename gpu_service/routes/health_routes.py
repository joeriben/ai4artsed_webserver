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

        # Get VRAM coordinator status (includes all backends)
        coordinator_status = {}
        try:
            from services.vram_coordinator import get_vram_coordinator
            coordinator = get_vram_coordinator()
            coordinator_status = coordinator.get_status()
        except Exception as e:
            logger.warning(f"VRAM coordinator status failed: {e}")

        return jsonify({
            "status": "ok",
            "gpu": gpu_info,
            "vram_coordinator": coordinator_status,
        })

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@health_bp.route('/api/health/vram', methods=['GET'])
def vram_status():
    """Detailed VRAM status from coordinator."""
    try:
        from services.vram_coordinator import get_vram_coordinator
        coordinator = get_vram_coordinator()
        return jsonify(coordinator.get_status())
    except Exception as e:
        logger.error(f"VRAM status error: {e}")
        return jsonify({"error": str(e)}), 500
