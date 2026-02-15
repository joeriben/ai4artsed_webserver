"""
Flask routes for configuration
"""
import logging
import asyncio
from flask import Blueprint, jsonify, request

from config import COMFYUI_PREFIX

logger = logging.getLogger(__name__)

# Create blueprint
config_bp = Blueprint('config', __name__)


@config_bp.route('/config', methods=['GET'])
def get_config():
    """Get frontend configuration"""
    try:
        config_data = {
            "comfyui_proxy_prefix": COMFYUI_PREFIX
        }
        return jsonify(config_data)
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"error": "Konfiguration konnte nicht geladen werden"}), 500


@config_bp.route('/api/models/availability', methods=['GET'])
def get_model_availability():
    """
    Check availability of models across all backends (ComfyUI, GPU service, cloud APIs).

    Each backend is checked independently — ComfyUI being down does NOT prevent
    Diffusers/HeartMuLa configs from being reported as available.

    Query Parameters:
        force_refresh (bool): If true, bypass cache and query fresh

    Returns:
        JSON response with availability map:
        {
            "status": "success",
            "availability": {
                "flux2_diffusers": true,
                "sd35_large": false,
                "heartmula_standard": true
            },
            "comfyui_reachable": false,
            "gpu_service_reachable": true,
            "cached": false,
            "cache_age_seconds": 0
        }
    """
    try:
        from my_app.services.model_availability_service import ModelAvailabilityService

        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        service = ModelAvailabilityService()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if force_refresh:
                service.invalidate_caches()
            availability = loop.run_until_complete(service.check_all_configs())
            gpu_status = loop.run_until_complete(service.get_gpu_service_status())
        finally:
            loop.close()

        return jsonify({
            "status": "success",
            "availability": availability,
            "comfyui_reachable": service._is_comfyui_reachable(),
            "gpu_service_reachable": gpu_status.get("gpu_service_reachable", False),
            "cached": service._is_cache_valid() or service._is_gpu_cache_valid(),
            "cache_age_seconds": service._get_cache_age()
        })

    except Exception as e:
        logger.error(f"[MODEL_AVAILABILITY] Error checking model availability: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "availability": {},
            "comfyui_reachable": False,
            "gpu_service_reachable": False
        }), 500
