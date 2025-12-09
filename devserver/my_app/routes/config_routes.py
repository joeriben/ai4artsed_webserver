"""
Flask routes for configuration
"""
import logging
import asyncio
import aiohttp
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
    Check availability of ComfyUI models for all output configs.

    Query Parameters:
        force_refresh (bool): If true, bypass cache and query fresh

    Returns:
        JSON response with availability map:
        {
            "status": "success",
            "availability": {
                "flux2": true,
                "sd35_large": true,
                "wan22_video": false
            },
            "comfyui_reachable": true,
            "cached": false,
            "cache_age_seconds": 0
        }

    Error Response (ComfyUI unreachable):
        {
            "status": "error",
            "error": "ComfyUI not reachable: ...",
            "availability": {},
            "comfyui_reachable": false
        }
    """
    try:
        from my_app.services.model_availability_service import ModelAvailabilityService

        # Check for force_refresh parameter
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'

        # Create service and run async check
        service = ModelAvailabilityService()

        # Run async method in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            availability = loop.run_until_complete(service.check_all_configs())
        finally:
            loop.close()

        return jsonify({
            "status": "success",
            "availability": availability,
            "comfyui_reachable": True,
            "cached": service._is_cache_valid(),
            "cache_age_seconds": service._get_cache_age()
        })

    except aiohttp.ClientError as e:
        logger.error(f"[MODEL_AVAILABILITY] ComfyUI unreachable: {e}")
        return jsonify({
            "status": "error",
            "error": f"ComfyUI not reachable: {str(e)}",
            "availability": {},
            "comfyui_reachable": False
        }), 503

    except Exception as e:
        logger.error(f"[MODEL_AVAILABILITY] Error checking model availability: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "availability": {},
            "comfyui_reachable": False
        }), 500
