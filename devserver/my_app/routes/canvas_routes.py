"""
Canvas Workflow Routes - API endpoints for Canvas Workflow Builder

Session 129: Phase 2 Implementation
Session 133: Curated LLM model selection + dynamic Ollama

Provides:
- /api/canvas/interception-configs - List available interception configs
- /api/canvas/output-configs - List available output/generation configs
- /api/canvas/llm-models - Curated LLM selection + dynamic Ollama models
- /api/canvas/workflows - Save/load workflow definitions (future)
"""
import logging
from pathlib import Path
from flask import Blueprint, jsonify, request
import json

from schemas.engine.model_selector import ModelSelector

logger = logging.getLogger(__name__)

# ============================================================================
# CURATED LLM MODELS - Small/Medium/Top per Provider
# ============================================================================
# DSGVO-compliant: local (Ollama), Mistral (EU-based)
# NOT DSGVO-compliant: Anthropic, Google, Meta, OpenAI (US-based)
# ============================================================================

CURATED_MODELS = {
    'anthropic': {
        'small': {'id': 'anthropic/claude-3-5-haiku-latest', 'name': 'Claude 3.5 Haiku'},
        'medium': {'id': 'anthropic/claude-3-5-sonnet-latest', 'name': 'Claude 3.5 Sonnet'},
        'top': {'id': 'anthropic/claude-sonnet-4-latest', 'name': 'Claude Sonnet 4'},
        'dsgvo': False
    },
    'mistral': {
        'small': {'id': 'mistral/ministral-8b-latest', 'name': 'Ministral 8B'},
        'medium': {'id': 'mistral/mistral-small-latest', 'name': 'Mistral Small 3.1'},
        'top': {'id': 'mistral/mistral-large-latest', 'name': 'Mistral Large'},
        'dsgvo': True  # EU-based
    },
    'google': {
        'small': {'id': 'google/gemma-3-4b-it', 'name': 'Gemma 3 4B'},
        'medium': {'id': 'google/gemini-2.0-flash', 'name': 'Gemini 2.0 Flash'},
        'top': {'id': 'google/gemini-2.5-pro', 'name': 'Gemini 2.5 Pro'},
        'dsgvo': False
    },
    'meta': {
        'small': {'id': 'meta/llama-3.2-3b-instruct', 'name': 'Llama 3.2 3B'},
        'medium': {'id': 'meta/llama-3.3-70b-instruct', 'name': 'Llama 3.3 70B'},
        'top': {'id': 'meta/llama-4-maverick', 'name': 'Llama 4 Maverick'},
        'dsgvo': False
    },
    'openai-oss': {
        'small': {'id': 'local/gpt-OSS:8b', 'name': 'GPT-OSS 8B (Lokal)'},
        'medium': {'id': 'local/gpt-OSS:20b', 'name': 'GPT-OSS 20B (Lokal)'},
        'top': {'id': 'local/gpt-OSS:120b', 'name': 'GPT-OSS 120B (Lokal)'},
        'dsgvo': True  # Lokal
    }
}

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
    Get curated LLM models + dynamic Ollama models for Canvas nodes

    Session 133: Replaced hardcoded config.py values with:
    1. Dynamic Ollama models (via ModelSelector.get_ollama_models())
    2. Curated models per provider (small/medium/top tiers)

    Provider prefixes:
    - local/ → Ollama / local models (DSGVO-compliant ✓)
    - anthropic/ → Anthropic Claude (NOT DSGVO-compliant ✗)
    - mistral/ → Mistral AI EU (DSGVO-compliant ✓)
    - google/ → Google AI (NOT DSGVO-compliant ✗)
    - meta/ → Meta AI (NOT DSGVO-compliant ✗)

    Returns:
        {
            "models": [...],
            "count": N,
            "ollamaCount": M  # Number of dynamic Ollama models
        }
    """
    selector = ModelSelector()
    models = []
    ollama_count = 0

    # 1. Dynamic Ollama models (all locally installed models)
    try:
        ollama_models = selector.get_ollama_models()
        for model_name in ollama_models:
            models.append({
                'id': f"local/{model_name}",
                'name': f"{model_name} (Lokal)",
                'provider': 'local',
                'tier': 'local',
                'dsgvoCompliant': True
            })
            ollama_count += 1
        logger.info(f"[Canvas LLM] Loaded {ollama_count} Ollama models")
    except Exception as e:
        logger.warning(f"[Canvas LLM] Failed to load Ollama models: {e}")

    # 2. Curated models (small/medium/top per provider)
    for provider, tiers in CURATED_MODELS.items():
        dsgvo = tiers.get('dsgvo', False)
        for tier in ['small', 'medium', 'top']:
            if tier in tiers:
                model = tiers[tier]
                models.append({
                    'id': model['id'],
                    'name': model['name'],
                    'provider': provider,
                    'tier': tier,
                    'dsgvoCompliant': dsgvo
                })

    logger.info(f"[Canvas LLM] Returning {len(models)} total models ({ollama_count} Ollama + {len(models) - ollama_count} curated)")

    return jsonify({
        'status': 'success',
        'models': models,
        'count': len(models),
        'ollamaCount': ollama_count
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
