"""
Settings API Routes
Configuration management for AI4ArtsEd DevServer
"""
from flask import Blueprint, jsonify, request
import json
import logging
from pathlib import Path
import config

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

# Path to user_settings.json
SETTINGS_FILE = Path(__file__).parent.parent.parent / "user_settings.json"

# Path to openrouter.key
OPENROUTER_KEY_FILE = Path(__file__).parent.parent.parent / "openrouter.key"

# Hardware Matrix - 2D Fill-Helper for UI (VRAM × DSGVO)
# This is NOT configuration - just preset values to help users fill the form
HARDWARE_MATRIX = {
    "vram_96": {
        "dsgvo_compliant": {
            "label": "96 GB VRAM (DSGVO-compliant, local models)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/llama3.2-vision:90b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_OPTIMIZATION_MODEL": "local/llama3.2-vision:90b",
                "STAGE3_MODEL": "local/llama3.2-vision:90b",
                "STAGE4_LEGACY_MODEL": "local/llama3.2-vision:90b",
                "CHAT_HELPER_MODEL": "local/llama3.2-vision:90b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            }
        },
        "non_dsgvo": {
            "label": "96 GB VRAM (Cloud allowed)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-sonnet-4.5",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE3_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            }
        }
    },
    "vram_32": {
        "dsgvo_compliant": {
            "label": "32 GB VRAM (DSGVO-compliant)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/llama3.2-vision:90b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_OPTIMIZATION_MODEL": "local/llama3.2-vision:90b",
                "STAGE3_MODEL": "local/llama3.2-vision:90b",
                "STAGE4_LEGACY_MODEL": "local/llama3.2-vision:90b",
                "CHAT_HELPER_MODEL": "local/llama3.2-vision:90b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            }
        },
        "non_dsgvo": {
            "label": "32 GB VRAM (Cloud allowed)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-sonnet-4.5",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE3_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            }
        }
    },
    "vram_24": {
        "dsgvo_compliant": {
            "label": "24 GB VRAM (DSGVO-compliant, local models)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/mistral-nemo",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "local/mistral-nemo",
                "STAGE2_OPTIMIZATION_MODEL": "local/mistral-nemo",
                "STAGE3_MODEL": "local/mistral-nemo",
                "STAGE4_LEGACY_MODEL": "local/mistral-nemo",
                "CHAT_HELPER_MODEL": "local/mistral-nemo",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            }
        },
        "non_dsgvo": {
            "label": "24 GB VRAM (Cloud allowed)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-sonnet-4.5",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE3_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            }
        }
    },
    "vram_16": {
        "dsgvo_compliant": {
            "label": "16 GB VRAM (DSGVO-compliant, local models)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/gemma:9b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "local/gemma:9b",
                "STAGE2_OPTIMIZATION_MODEL": "local/gemma:9b",
                "STAGE3_MODEL": "local/gemma:9b",
                "STAGE4_LEGACY_MODEL": "local/gemma:9b",
                "CHAT_HELPER_MODEL": "local/gemma:9b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            }
        },
        "non_dsgvo": {
            "label": "16 GB VRAM (Cloud allowed)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-sonnet-4.5",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE3_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            }
        }
    },
    "vram_8": {
        "dsgvo_compliant": {
            "label": "8 GB VRAM (DSGVO-compliant, local only)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/gemma:2b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:latest",
                "STAGE2_INTERCEPTION_MODEL": "local/gemma:2b",
                "STAGE2_OPTIMIZATION_MODEL": "local/gemma:2b",
                "STAGE3_MODEL": "local/gemma:2b",
                "STAGE4_LEGACY_MODEL": "local/gemma:2b",
                "CHAT_HELPER_MODEL": "local/gemma:2b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:latest"
            }
        },
        "non_dsgvo": {
            "label": "8 GB VRAM (Cloud allowed)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:latest",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-sonnet-4.5",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE3_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-haiku-4.5",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:latest"
            }
        }
    }
}


@settings_bp.route('/', methods=['GET'])
def get_settings():
    """Get current configuration and hardware matrix"""
    try:
        # Collect all current config values
        current = {
            # General Settings
            "UI_MODE": config.UI_MODE,
            "DEFAULT_SAFETY_LEVEL": config.DEFAULT_SAFETY_LEVEL,
            "DEFAULT_LANGUAGE": config.DEFAULT_LANGUAGE,

            # Server Settings
            "HOST": config.HOST,
            "PORT": config.PORT,
            "THREADS": config.THREADS,

            # Model Configuration
            "STAGE1_TEXT_MODEL": config.STAGE1_TEXT_MODEL,
            "STAGE1_VISION_MODEL": config.STAGE1_VISION_MODEL,
            "STAGE2_INTERCEPTION_MODEL": config.STAGE2_INTERCEPTION_MODEL,
            "STAGE2_OPTIMIZATION_MODEL": config.STAGE2_OPTIMIZATION_MODEL,
            "STAGE3_MODEL": config.STAGE3_MODEL,
            "STAGE4_LEGACY_MODEL": config.STAGE4_LEGACY_MODEL,
            "CHAT_HELPER_MODEL": config.CHAT_HELPER_MODEL,
            "IMAGE_ANALYSIS_MODEL": config.IMAGE_ANALYSIS_MODEL,

            # API Configuration
            "LLM_PROVIDER": config.LLM_PROVIDER,
            "OLLAMA_API_BASE_URL": config.OLLAMA_API_BASE_URL,
            "LMSTUDIO_API_BASE_URL": config.LMSTUDIO_API_BASE_URL,
        }

        return jsonify({
            "current": current,
            "matrix": HARDWARE_MATRIX
        }), 200

    except Exception as e:
        logger.error(f"[SETTINGS] Error getting config: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/', methods=['POST'])
def save_settings():
    """Save all settings to user_settings.json"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract OpenRouter API Key if present (saved separately for security)
        openrouter_key = data.pop('OPENROUTER_API_KEY', None)
        if openrouter_key:
            OPENROUTER_KEY_FILE.parent.mkdir(exist_ok=True)
            with open(OPENROUTER_KEY_FILE, 'w') as f:
                f.write(openrouter_key.strip())
            logger.info("[SETTINGS] OpenRouter API Key updated")

        # Write all other settings to user_settings.json
        SETTINGS_FILE.parent.mkdir(exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"[SETTINGS] Saved {len(data)} settings to {SETTINGS_FILE.name}")

        return jsonify({
            "success": True,
            "message": "Configuration saved. Backend restart required to apply changes."
        }), 200

    except Exception as e:
        logger.error(f"[SETTINGS] Error saving config: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/openrouter-key', methods=['GET'])
def get_openrouter_key():
    """Get masked OpenRouter API Key for display"""
    try:
        if not OPENROUTER_KEY_FILE.exists():
            return jsonify({"exists": False}), 200

        with open(OPENROUTER_KEY_FILE) as f:
            key = f.read().strip()

        # Return masked version (show only first 7 and last 4 chars)
        if len(key) > 11:
            masked = f"{key[:7]}...{key[-4:]}"
        else:
            masked = "***"

        return jsonify({
            "exists": True,
            "masked": masked
        }), 200

    except Exception as e:
        logger.error(f"[SETTINGS] Error reading OpenRouter key: {e}")
        return jsonify({"error": str(e)}), 500
