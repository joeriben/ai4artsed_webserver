"""
Flask routes for configuration
"""
import logging
from flask import Blueprint, jsonify

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
