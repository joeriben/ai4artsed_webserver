"""
Settings API Routes
Configuration management for AI4ArtsEd DevServer
"""
from flask import Blueprint, jsonify, request, session
from functools import wraps
import json
import logging
from pathlib import Path
from datetime import datetime, date
import config

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

# Path to user_settings.json
SETTINGS_FILE = Path(__file__).parent.parent.parent / "user_settings.json"

# Path to API key files
OPENROUTER_KEY_FILE = Path(__file__).parent.parent.parent / "openrouter.key"
ANTHROPIC_KEY_FILE = Path(__file__).parent.parent.parent / "anthropic.key"
OPENAI_KEY_FILE = Path(__file__).parent.parent.parent / "openai.key"

# Path to settings password file
SETTINGS_PASSWORD_FILE = Path(__file__).parent.parent.parent / "settings_password.key"

# Hardware Matrix - 2D Fill-Helper for UI (VRAM × DSGVO)
# This is NOT configuration - just preset values to help users fill the form
HARDWARE_MATRIX = {
    "vram_96": {
        "dsgvo_local": {
            "label": "96 GB VRAM (DSGVO, local only)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/llama3.2-vision:90b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_OPTIMIZATION_MODEL": "local/llama3.2-vision:90b",
                "STAGE3_MODEL": "local/llama3.2-vision:90b",
                "STAGE4_LEGACY_MODEL": "local/llama3.2-vision:90b",
                "CHAT_HELPER_MODEL": "local/llama3.2-vision:90b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "none",
            "DSGVO_CONFORMITY": True
        },
        "dsgvo_cloud": {
            "label": "96 GB VRAM (DSGVO, AWS Bedrock EU)",
            "models": {
                "STAGE1_TEXT_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE2_OPTIMIZATION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE3_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE4_LEGACY_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "CHAT_HELPER_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "bedrock",
            "DSGVO_CONFORMITY": True
        },
        "non_dsgvo": {
            "label": "96 GB VRAM (non-DSGVO, OpenRouter)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-3-5-sonnet",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE3_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "openrouter",
            "DSGVO_CONFORMITY": False
        }
    },
    "vram_32": {
        "dsgvo_local": {
            "label": "32 GB VRAM (DSGVO, local only)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/llama3.2-vision:90b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_OPTIMIZATION_MODEL": "local/llama3.2-vision:90b",
                "STAGE3_MODEL": "local/llama3.2-vision:90b",
                "STAGE4_LEGACY_MODEL": "local/llama3.2-vision:90b",
                "CHAT_HELPER_MODEL": "local/llama3.2-vision:90b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "none",
            "DSGVO_CONFORMITY": True
        },
        "dsgvo_cloud": {
            "label": "32 GB VRAM (DSGVO, AWS Bedrock EU)",
            "models": {
                "STAGE1_TEXT_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE2_OPTIMIZATION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE3_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE4_LEGACY_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "CHAT_HELPER_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "bedrock",
            "DSGVO_CONFORMITY": True
        },
        "non_dsgvo": {
            "label": "32 GB VRAM (non-DSGVO, OpenRouter)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:90b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-3-5-sonnet",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE3_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:90b"
            },
            "EXTERNAL_LLM_PROVIDER": "openrouter",
            "DSGVO_CONFORMITY": False
        }
    },
    "vram_24": {
        "dsgvo_local": {
            "label": "24 GB VRAM (DSGVO, local only)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/mistral-nemo",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "local/mistral-nemo",
                "STAGE2_OPTIMIZATION_MODEL": "local/mistral-nemo",
                "STAGE3_MODEL": "local/mistral-nemo",
                "STAGE4_LEGACY_MODEL": "local/mistral-nemo",
                "CHAT_HELPER_MODEL": "local/mistral-nemo",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            },
            "EXTERNAL_LLM_PROVIDER": "none",
            "DSGVO_CONFORMITY": True
        },
        "dsgvo_cloud": {
            "label": "24 GB VRAM (DSGVO, AWS Bedrock EU)",
            "models": {
                "STAGE1_TEXT_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE2_OPTIMIZATION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE3_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE4_LEGACY_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "CHAT_HELPER_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            },
            "EXTERNAL_LLM_PROVIDER": "bedrock",
            "DSGVO_CONFORMITY": True
        },
        "non_dsgvo": {
            "label": "24 GB VRAM (non-DSGVO, OpenRouter)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-3-5-sonnet",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE3_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            },
            "EXTERNAL_LLM_PROVIDER": "openrouter",
            "DSGVO_CONFORMITY": False
        }
    },
    "vram_16": {
        "dsgvo_local": {
            "label": "16 GB VRAM (DSGVO, local only)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/gemma:9b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "local/gemma:9b",
                "STAGE2_OPTIMIZATION_MODEL": "local/gemma:9b",
                "STAGE3_MODEL": "local/gemma:9b",
                "STAGE4_LEGACY_MODEL": "local/gemma:9b",
                "CHAT_HELPER_MODEL": "local/gemma:9b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            },
            "EXTERNAL_LLM_PROVIDER": "none",
            "DSGVO_CONFORMITY": True
        },
        "dsgvo_cloud": {
            "label": "16 GB VRAM (DSGVO, AWS Bedrock EU)",
            "models": {
                "STAGE1_TEXT_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE2_OPTIMIZATION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE3_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE4_LEGACY_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "CHAT_HELPER_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            },
            "EXTERNAL_LLM_PROVIDER": "bedrock",
            "DSGVO_CONFORMITY": True
        },
        "non_dsgvo": {
            "label": "16 GB VRAM (non-DSGVO, OpenRouter)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:11b",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-3-5-sonnet",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE3_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:11b"
            },
            "EXTERNAL_LLM_PROVIDER": "openrouter",
            "DSGVO_CONFORMITY": False
        }
    },
    "vram_8": {
        "dsgvo_local": {
            "label": "8 GB VRAM (DSGVO, local only)",
            "models": {
                "STAGE1_TEXT_MODEL": "local/gemma:2b",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:latest",
                "STAGE2_INTERCEPTION_MODEL": "local/gemma:2b",
                "STAGE2_OPTIMIZATION_MODEL": "local/gemma:2b",
                "STAGE3_MODEL": "local/gemma:2b",
                "STAGE4_LEGACY_MODEL": "local/gemma:2b",
                "CHAT_HELPER_MODEL": "local/gemma:2b",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:latest"
            },
            "EXTERNAL_LLM_PROVIDER": "none",
            "DSGVO_CONFORMITY": True
        },
        "dsgvo_cloud": {
            "label": "8 GB VRAM (DSGVO, AWS Bedrock EU)",
            "models": {
                "STAGE1_TEXT_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:latest",
                "STAGE2_INTERCEPTION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE2_OPTIMIZATION_MODEL": "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "STAGE3_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "STAGE4_LEGACY_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "CHAT_HELPER_MODEL": "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:latest"
            },
            "EXTERNAL_LLM_PROVIDER": "bedrock",
            "DSGVO_CONFORMITY": True
        },
        "non_dsgvo": {
            "label": "8 GB VRAM (non-DSGVO, OpenRouter)",
            "models": {
                "STAGE1_TEXT_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE1_VISION_MODEL": "local/llama3.2-vision:latest",
                "STAGE2_INTERCEPTION_MODEL": "openrouter/anthropic/claude-3-5-sonnet",
                "STAGE2_OPTIMIZATION_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE3_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "STAGE4_LEGACY_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "CHAT_HELPER_MODEL": "openrouter/anthropic/claude-3-5-haiku",
                "IMAGE_ANALYSIS_MODEL": "local/llama3.2-vision:latest"
            },
            "EXTERNAL_LLM_PROVIDER": "openrouter",
            "DSGVO_CONFORMITY": False
        }
    }
}


# Authentication decorator
def require_settings_auth(f):
    """Decorator to protect settings routes with password authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('settings_authenticated', False):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


@settings_bp.route('/auth', methods=['POST'])
def authenticate():
    """Authenticate with settings password"""
    try:
        data = request.get_json()
        password = data.get('password', '')

        # Use default password if file doesn't exist (fresh production deploy)
        if not SETTINGS_PASSWORD_FILE.exists():
            correct_password = "ai4artsedadmin"
            logger.warning("[SETTINGS] No password file found, using default password")
        else:
            with open(SETTINGS_PASSWORD_FILE) as f:
                correct_password = f.read().strip()

        if password == correct_password:
            session['settings_authenticated'] = True
            session.permanent = True  # Remember across browser restarts
            logger.info("[SETTINGS] Authentication successful")
            return jsonify({"success": True}), 200
        else:
            logger.warning("[SETTINGS] Authentication failed - incorrect password")
            return jsonify({"error": "Incorrect password"}), 403

    except Exception as e:
        logger.error(f"[SETTINGS] Authentication error: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/logout', methods=['POST'])
def logout():
    """Clear settings authentication"""
    session.pop('settings_authenticated', None)
    logger.info("[SETTINGS] User logged out")
    return jsonify({"success": True}), 200


@settings_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if currently authenticated"""
    authenticated = session.get('settings_authenticated', False)
    return jsonify({"authenticated": authenticated}), 200


@settings_bp.route('/', methods=['GET'])
@require_settings_auth
def get_settings():
    """Get current configuration and hardware matrix"""
    try:
        # Collect all current config values
        current = {
            # General Settings
            "UI_MODE": config.UI_MODE,
            "DEFAULT_SAFETY_LEVEL": config.DEFAULT_SAFETY_LEVEL,
            "DEFAULT_LANGUAGE": config.DEFAULT_LANGUAGE,

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
            "EXTERNAL_LLM_PROVIDER": config.EXTERNAL_LLM_PROVIDER,
            "DSGVO_CONFORMITY": config.DSGVO_CONFORMITY,
        }

        return jsonify({
            "current": current,
            "matrix": HARDWARE_MATRIX
        }), 200

    except Exception as e:
        logger.error(f"[SETTINGS] Error getting config: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/', methods=['POST'])
@require_settings_auth
def save_settings():
    """Save all settings to user_settings.json"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract API Keys if present (saved separately for security)
        openrouter_key = data.pop('OPENROUTER_API_KEY', None)
        if openrouter_key:
            OPENROUTER_KEY_FILE.parent.mkdir(exist_ok=True)
            with open(OPENROUTER_KEY_FILE, 'w') as f:
                f.write(openrouter_key.strip())
            logger.info("[SETTINGS] OpenRouter API Key updated")

        anthropic_key = data.pop('ANTHROPIC_API_KEY', None)
        if anthropic_key:
            ANTHROPIC_KEY_FILE.parent.mkdir(exist_ok=True)
            with open(ANTHROPIC_KEY_FILE, 'w') as f:
                f.write(anthropic_key.strip())
            logger.info("[SETTINGS] Anthropic API Key updated")

        openai_key = data.pop('OPENAI_API_KEY', None)
        if openai_key:
            OPENAI_KEY_FILE.parent.mkdir(exist_ok=True)
            with open(OPENAI_KEY_FILE, 'w') as f:
                f.write(openai_key.strip())
            logger.info("[SETTINGS] OpenAI API Key updated")

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
@require_settings_auth
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


@settings_bp.route('/anthropic-key', methods=['GET'])
@require_settings_auth
def get_anthropic_key():
    """Get masked Anthropic API Key for display"""
    try:
        if not ANTHROPIC_KEY_FILE.exists():
            return jsonify({"exists": False}), 200

        with open(ANTHROPIC_KEY_FILE) as f:
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
        logger.error(f"[SETTINGS] Error reading Anthropic key: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/openai-key', methods=['GET'])
@require_settings_auth
def get_openai_key():
    """Get masked OpenAI API Key for display"""
    try:
        if not OPENAI_KEY_FILE.exists():
            return jsonify({"exists": False}), 200

        with open(OPENAI_KEY_FILE) as f:
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
        logger.error(f"[SETTINGS] Error reading OpenAI key: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/aws-credentials', methods=['POST'])
@require_settings_auth
def upload_aws_credentials():
    """Upload AWS credentials CSV (from AWS IAM Console)"""
    try:
        if 'csv' not in request.files:
            return jsonify({"error": "No CSV file provided"}), 400

        file = request.files['csv']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Read CSV content
        import csv
        import io

        # Decode and remove BOM if present
        content = file.read().decode('utf-8-sig')  # utf-8-sig automatically strips BOM
        csv_reader = csv.DictReader(io.StringIO(content))

        # Parse AWS credentials (format: Access key ID,Secret access key)
        # Be flexible with column names (spaces, case)
        credentials = None
        for row in csv_reader:
            # Normalize column names (strip, lowercase)
            normalized_row = {k.strip().lower(): v.strip() for k, v in row.items()}

            # Look for access key and secret key (flexible matching)
            access_key = (
                normalized_row.get('access key id') or
                normalized_row.get('accesskeyid') or
                normalized_row.get('access_key_id')
            )
            secret_key = (
                normalized_row.get('secret access key') or
                normalized_row.get('secretaccesskey') or
                normalized_row.get('secret_access_key')
            )

            if access_key and secret_key:
                credentials = {
                    'access_key_id': access_key,
                    'secret_access_key': secret_key
                }
                break

        if not credentials:
            return jsonify({"error": "Invalid CSV format. Expected columns: 'Access key ID', 'Secret access key'"}), 400

        # Save credentials to setup_aws_env.sh
        env_script_path = Path(__file__).parent.parent.parent / "setup_aws_env.sh"
        env_script_content = f'''#!/bin/bash
# AWS Bedrock Environment Setup (Auto-generated from Settings Page)
# USAGE: source devserver/setup_aws_env.sh

export AWS_ACCESS_KEY_ID="{credentials['access_key_id']}"
export AWS_SECRET_ACCESS_KEY="{credentials['secret_access_key']}"
export AWS_DEFAULT_REGION="eu-central-1"

echo "✅ AWS Bedrock environment variables set"
echo "   Region: $AWS_DEFAULT_REGION"
echo "   Access Key: ${{AWS_ACCESS_KEY_ID:0:8}}..."
'''

        with open(env_script_path, 'w') as f:
            f.write(env_script_content)

        # Make executable
        import stat
        env_script_path.chmod(env_script_path.stat().st_mode | stat.S_IEXEC)

        logger.info(f"[SETTINGS] AWS credentials saved to {env_script_path.name}")

        return jsonify({
            "success": True,
            "message": "AWS credentials saved. Run 'source devserver/setup_aws_env.sh' and restart server."
        }), 200

    except Exception as e:
        logger.error(f"[SETTINGS] Error uploading AWS credentials: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/sessions', methods=['GET'])
@require_settings_auth
def get_sessions():
    """
    Get list of all sessions from /exports/json with pagination and filtering

    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 50, max: 500)
    - date: Filter by date (YYYY-MM-DD, default: today)
    - user_id: Filter by user ID
    - config_name: Filter by config name
    - safety_level: Filter by safety level
    - search: Search in run_id
    - sort: Sort field (timestamp, user_id, config_name, default: timestamp)
    - order: Sort order (asc, desc, default: desc)
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 500)
        date_filter = request.args.get('date', date.today().isoformat())
        user_filter = request.args.get('user_id', None)
        config_filter = request.args.get('config_name', None)
        safety_filter = request.args.get('safety_level', None)
        search_filter = request.args.get('search', None)
        sort_field = request.args.get('sort', 'timestamp')
        sort_order = request.args.get('order', 'desc')

        # Path to exports/json
        exports_path = Path(__file__).parent.parent.parent.parent / "exports" / "json"

        if not exports_path.exists():
            return jsonify({
                "sessions": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0
            }), 200

        # Collect all sessions
        all_sessions = []

        for session_dir in exports_path.iterdir():
            if not session_dir.is_dir():
                continue

            metadata_file = session_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)

                # Parse timestamp
                timestamp_str = metadata.get('timestamp', '')
                try:
                    timestamp_dt = datetime.fromisoformat(timestamp_str)
                except:
                    continue

                # Apply date filter (default: today)
                if date_filter:
                    session_date = timestamp_dt.date().isoformat()
                    if session_date != date_filter:
                        continue

                # Apply user filter
                if user_filter and metadata.get('user_id') != user_filter:
                    continue

                # Apply config filter
                if config_filter and metadata.get('config_name') != config_filter:
                    continue

                # Apply safety level filter
                if safety_filter and metadata.get('safety_level') != safety_filter:
                    continue

                # Apply search filter
                if search_filter and search_filter.lower() not in metadata.get('run_id', '').lower():
                    continue

                # Count media files and find first image for thumbnail
                media_count = 0
                thumbnail_path = None
                for entity in metadata.get('entities', []):
                    entity_type = entity.get('type', '')
                    if entity_type.startswith('output_'):
                        media_count += 1
                        # Find first image for thumbnail
                        if thumbnail_path is None and entity_type == 'output_image':
                            filename = entity.get('filename')
                            if filename:
                                thumbnail_path = f"/exports/json/{session_dir.name}/{filename}"

                # Build session summary
                session_summary = {
                    'run_id': metadata.get('run_id'),
                    'timestamp': timestamp_str,
                    'config_name': metadata.get('config_name'),
                    'execution_mode': metadata.get('execution_mode'),
                    'safety_level': metadata.get('safety_level'),
                    'user_id': metadata.get('user_id'),
                    'stage': metadata.get('current_state', {}).get('stage'),
                    'step': metadata.get('current_state', {}).get('step'),
                    'entity_count': len(metadata.get('entities', [])),
                    'media_count': media_count,
                    'session_dir': str(session_dir.name),
                    'thumbnail': thumbnail_path
                }

                all_sessions.append(session_summary)

            except Exception as e:
                logger.error(f"[SETTINGS] Error reading metadata from {session_dir.name}: {e}")
                continue

        # Sort sessions
        reverse = (sort_order == 'desc')
        if sort_field in ['timestamp', 'user_id', 'config_name', 'safety_level']:
            all_sessions.sort(key=lambda x: x.get(sort_field, ''), reverse=reverse)

        # Pagination
        total = len(all_sessions)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_sessions = all_sessions[start:end]

        # Collect unique values for filters
        unique_users = sorted(set(s['user_id'] for s in all_sessions if s.get('user_id')))
        unique_configs = sorted(set(s['config_name'] for s in all_sessions if s.get('config_name')))
        unique_safety_levels = sorted(set(s['safety_level'] for s in all_sessions if s.get('safety_level')))

        return jsonify({
            "sessions": paginated_sessions,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "filters": {
                "users": unique_users,
                "configs": unique_configs,
                "safety_levels": unique_safety_levels
            }
        }), 200

    except Exception as e:
        logger.error(f"[SETTINGS] Error getting sessions: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/sessions/<run_id>', methods=['GET'])
@require_settings_auth
def get_session_detail(run_id):
    """Get detailed information for a specific session"""
    try:
        exports_path = Path(__file__).parent.parent.parent.parent / "exports" / "json"
        session_dir = exports_path / run_id

        if not session_dir.exists():
            return jsonify({"error": "Session not found"}), 404

        metadata_file = session_dir / "metadata.json"
        if not metadata_file.exists():
            return jsonify({"error": "Metadata not found"}), 404

        with open(metadata_file) as f:
            metadata = json.load(f)

        # Read all entity files
        entities_with_content = []
        for entity in metadata.get('entities', []):
            entity_copy = entity.copy()
            filename = entity.get('filename')
            if filename:
                file_path = session_dir / filename
                if file_path.exists():
                    # For images, provide URL path
                    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                        entity_copy['image_url'] = f"/exports/json/{run_id}/{filename}"
                    # For text files, read content
                    elif file_path.suffix in ['.txt', '.json']:
                        try:
                            with open(file_path) as f:
                                entity_copy['content'] = f.read()
                        except:
                            entity_copy['content'] = None
            entities_with_content.append(entity_copy)

        metadata['entities'] = entities_with_content

        return jsonify(metadata), 200

    except Exception as e:
        logger.error(f"[SETTINGS] Error getting session detail: {e}")
        return jsonify({"error": str(e)}), 500
