"""
Canvas Workflow Routes - API endpoints for Canvas Workflow Builder

Session 129: Phase 2 Implementation

Provides:
- /api/canvas/interception-configs - List available interception configs
- /api/canvas/output-configs - List available output/generation configs
- /api/canvas/workflows - Save/load workflow definitions (future)
"""
import logging
from pathlib import Path
from flask import Blueprint, jsonify, request
import json

logger = logging.getLogger(__name__)

# Create blueprint
canvas_bp = Blueprint('canvas', __name__)


def _get_schemas_path() -> Path:
    """Get the schemas directory path"""
    # Navigate from routes to devserver/schemas
    current_file = Path(__file__)
    devserver_path = current_file.parent.parent.parent  # my_app/routes -> my_app -> devserver
    return devserver_path / "schemas"


def _load_config_summaries(config_type: str) -> list:
    """
    Load config summaries from configs directory

    Args:
        config_type: 'interception' or 'output'

    Returns:
        List of config summary dicts with id, name, description, icon, color, etc.
    """
    schemas_path = _get_schemas_path()
    configs_path = schemas_path / "configs" / config_type

    if not configs_path.exists():
        logger.warning(f"Config path not found: {configs_path}")
        return []

    summaries = []

    for config_file in sorted(configs_path.glob("*.json")):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract summary info
            config_id = config_file.stem

            # Get name (multilingual dict or string)
            name_data = data.get('name', config_id)
            if isinstance(name_data, dict):
                name = name_data
            else:
                name = {'en': str(name_data), 'de': str(name_data)}

            # Get description (multilingual dict or string)
            desc_data = data.get('description', '')
            if isinstance(desc_data, dict):
                description = desc_data
            else:
                description = {'en': str(desc_data), 'de': str(desc_data)}

            # Get display properties
            display = data.get('display', {})
            icon = display.get('icon', '📦')
            color = display.get('color', '#64748b')

            # Build summary
            summary = {
                'id': config_id,
                'name': name,
                'description': description,
                'icon': icon,
                'color': color
            }

            # Add type-specific fields
            if config_type == 'interception':
                summary['category'] = data.get('category', {}).get('en', 'General')
            elif config_type == 'output':
                media_prefs = data.get('media_preferences', {})
                summary['mediaType'] = media_prefs.get('default_output', 'image')
                meta = data.get('meta', {})
                summary['backend'] = meta.get('backend', 'unknown')

            summaries.append(summary)

        except Exception as e:
            logger.error(f"Error loading config {config_file}: {e}")
            continue

    logger.info(f"Loaded {len(summaries)} {config_type} configs")
    return summaries


@canvas_bp.route('/api/canvas/llm-models', methods=['GET'])
def get_llm_models():
    """
    Get list of available LLM models for interception/translation nodes

    Returns:
        {
            "models": [
                {
                    "id": "gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "provider": "openai",
                    "description": "Fast and efficient model",
                    "isDefault": true
                },
                ...
            ]
        }
    """
    # TODO: Load from config or detect available models dynamically
    # For now, return a static list of commonly used models
    models = [
        {
            "id": "gpt-4o-mini",
            "name": "GPT-4o Mini",
            "provider": "openai",
            "description": "Fast, efficient, good for most tasks",
            "isDefault": True
        },
        {
            "id": "gpt-4o",
            "name": "GPT-4o",
            "provider": "openai",
            "description": "Most capable OpenAI model"
        },
        {
            "id": "claude-3-5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "provider": "anthropic",
            "description": "Balanced performance and speed"
        },
        {
            "id": "claude-3-5-haiku",
            "name": "Claude 3.5 Haiku",
            "provider": "anthropic",
            "description": "Fast and cost-effective"
        },
        {
            "id": "gemini-2.0-flash",
            "name": "Gemini 2.0 Flash",
            "provider": "google",
            "description": "Google's fast multimodal model"
        }
    ]

    return jsonify({
        'status': 'success',
        'models': models,
        'count': len(models)
    })


@canvas_bp.route('/api/canvas/output-configs', methods=['GET'])
def get_output_configs():
    """
    Get list of available output/generation configs

    Returns:
        {
            "configs": [
                {
                    "id": "sd35_large",
                    "name": {"en": "SD 3.5 Large", "de": "SD 3.5 Large"},
                    "description": {...},
                    "icon": "🎨",
                    "color": "#10b981",
                    "mediaType": "image",
                    "backend": "comfyui"
                },
                ...
            ]
        }
    """
    try:
        configs = _load_config_summaries('output')
        return jsonify({
            'status': 'success',
            'configs': configs,
            'count': len(configs)
        })
    except Exception as e:
        logger.error(f"Error loading output configs: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'configs': []
        }), 500


@canvas_bp.route('/api/canvas/workflows', methods=['GET'])
def list_workflows():
    """
    List saved canvas workflows

    TODO: Implement in Phase 3
    """
    return jsonify({
        'status': 'success',
        'workflows': [],
        'message': 'Workflow persistence not yet implemented'
    })


@canvas_bp.route('/api/canvas/workflows', methods=['POST'])
def save_workflow():
    """
    Save a canvas workflow

    TODO: Implement in Phase 3
    """
    return jsonify({
        'status': 'error',
        'message': 'Workflow persistence not yet implemented'
    }), 501


@canvas_bp.route('/api/canvas/execute', methods=['POST'])
def execute_workflow():
    """
    Execute a canvas workflow

    TODO: Implement in Phase 3
    """
    return jsonify({
        'status': 'error',
        'message': 'Workflow execution not yet implemented'
    }), 501
