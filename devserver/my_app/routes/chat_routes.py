"""
Chat Routes - Interactive LLM Help System with Session Context Awareness

Session 82: Implements persistent chat overlay for:
1. General system guidance (no context)
2. System usage help (basic context)
3. Prompt consultation (full session context)
"""

from flask import Blueprint, request, jsonify
from pathlib import Path
import logging
import json
import os
import requests
from datetime import datetime

# Import config (EXACT pattern from other routes)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import JSON_STORAGE_DIR, CHAT_HELPER_MODEL

logger = logging.getLogger(__name__)

# Blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Load interface reference guide
INTERFACE_REFERENCE = ""
try:
    reference_path = Path(__file__).parent.parent.parent / "trashy_interface_reference.txt"
    if reference_path.exists():
        with open(reference_path, 'r', encoding='utf-8') as f:
            INTERFACE_REFERENCE = f.read()
        logger.info("Loaded interface reference guide for Träshy")
    else:
        logger.warning(f"Interface reference not found: {reference_path}")
except Exception as e:
    logger.error(f"Failed to load interface reference: {e}")

# System Prompt Templates
GENERAL_SYSTEM_PROMPT = f"""You are an AI assistant for the AI for Arts Education Lab, an educational tool for creative AI experimentation in art education (ages 8–17). You are contacted in the context of an ongoing art–AI workshop; educators are present. You ALWAYS respond in the language in which you were addressed.

Your role:
- Explain how the system works
- Help users understand interface elements
- Provide guidance for prompt creation
- Answer questions about AI concepts in age-appropriate language

Keep answers:
- Short and clear (2–3 sentences preferred)
- Age-appropriate (mostly students aged 9–15)
- Encouraging and pedagogically supportive

Use the following operating instructions for this – but remember to formulate them in a way that is appropriate for the target group, i.e. uncomplicated and action-oriented.

IF YOU DON'T KNOW WHAT TO DO NEXT, THEN REFER TO THE COURSE INSTRUCTOR WHO IS PRESENT. YOU NEVER HALLUCINATE SOLUTIONS WHEN YOU ARE UNCERTAIN, BUT INSTEAD REFER TO THE COURSE INSTRUCTOR. IT IS COMPLETELY OKAY NOT TO KNOW EVERYTHING.

{INTERFACE_REFERENCE}"""

SESSION_SYSTEM_PROMPT_TEMPLATE = f"""You are an AI assistant for the AI for Arts Education Lab, an educational tool for creative AI experimentation in art education (ages 8–17). You are contacted in the context of an ongoing art–AI workshop; educators are present. You ALWAYS respond in the language in which you were addressed.

Current session context:
- Media type: {{media_type}}
- Model/Config: {{config_name}}
- Safety level: {{safety_level}}
- Original input: "{{input_text}}"
- Transformed prompt: "{{interception_text}}"
- Session stage: {{current_stage}}

Your role:
- Help refine their current prompt
- Explain what the pedagogical transformation did
- Suggest creative improvements specific to THEIR work
- Answer questions about their current session

Keep answers:
- SHORT and clear (2-4 sentences)
- Age-appropriate (students aged 9-15)
- Focused on THEIR specific work
- Constructive and encouraging

Use the following operating instructions – formulate in a way appropriate for the target group.

IF YOU DON'T KNOW WHAT TO DO NEXT, THEN REFER TO THE COURSE INSTRUCTOR WHO IS PRESENT. YOU NEVER HALLUCINATE SOLUTIONS WHEN YOU ARE UNCERTAIN, BUT INSTEAD REFER TO THE COURSE INSTRUCTOR. IT IS COMPLETELY OKAY NOT TO KNOW EVERYTHING.

{INTERFACE_REFERENCE}"""


def get_openrouter_credentials():
    """
    Get OpenRouter credentials (copied pattern from prompt_interception_engine.py)
    Returns: (api_url, api_key)
    """
    api_url = "https://openrouter.ai/api/v1/chat/completions"

    # 1. Try Environment Variable
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if api_key:
        logger.debug("OpenRouter API Key from environment variable")
        return api_url, api_key

    # 2. Try Key-File (devserver/openrouter.key)
    try:
        # Relative to devserver root
        key_file = Path(__file__).parent.parent.parent / "openrouter.key"
        if key_file.exists():
            # Read file and skip comment lines
            lines = key_file.read_text().strip().split('\n')
            api_key = None
            for line in lines:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#') and not line.startswith('//'):
                    # Check if this looks like an API key (starts with sk-)
                    if line.startswith("sk-"):
                        api_key = line
                        break

            if api_key:
                logger.info(f"OpenRouter API Key loaded from {key_file}")
                return api_url, api_key
            else:
                logger.error(f"No valid API key found in {key_file} (looking for lines starting with 'sk-')")
        else:
            logger.warning(f"OpenRouter key file not found: {key_file}")
    except Exception as e:
        logger.warning(f"Failed to read openrouter.key: {e}")

    # 3. No key found
    logger.error("OpenRouter API Key not found! Set OPENROUTER_API_KEY environment variable or create devserver/openrouter.key file")
    return api_url, ""


def call_openrouter_chat(messages: list, temperature: float = 0.7, max_tokens: int = 500):
    """
    Call OpenRouter API for chat (pattern from prompt_interception_engine.py)

    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Temperature for generation
        max_tokens: Max tokens to generate

    Returns:
        Response content string
    """
    try:
        # Get model from config
        model_string = CHAT_HELPER_MODEL  # e.g., "openrouter/anthropic/claude-haiku-4.5"

        # Extract model name (remove "openrouter/" prefix if present)
        if model_string.startswith("openrouter/"):
            model = model_string[len("openrouter/"):]
        else:
            model = model_string

        logger.info(f"[CHAT] Calling OpenRouter with model: {model}")

        api_url, api_key = get_openrouter_credentials()

        if not api_key:
            raise Exception("OpenRouter API Key not configured")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info(f"[CHAT] OpenRouter Success: {len(content)} chars")
            return content
        else:
            error_msg = f"API Error: {response.status_code}\n{response.text}"
            logger.error(f"[CHAT] OpenRouter Error: {error_msg}")
            raise Exception(error_msg)

    except Exception as e:
        logger.error(f"[CHAT] OpenRouter call failed: {e}", exc_info=True)
        raise


def load_session_context(run_id: str) -> dict:
    """
    Load session context from exports/json/{run_id}/

    Returns dict with:
    - success: bool
    - context: dict with session data (if success=True)
    - error: str (if success=False)
    """
    try:
        session_path = JSON_STORAGE_DIR / run_id

        if not session_path.exists():
            logger.warning(f"Session path not found: {session_path}")
            return {"success": False, "error": "Session not found"}

        context = {}

        # Load metadata.json
        metadata_path = session_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                context['metadata'] = metadata
                context['config_name'] = metadata.get('config_name', 'unknown')
                context['safety_level'] = metadata.get('safety_level', 'unknown')
                context['current_stage'] = metadata.get('current_state', {}).get('stage', 'unknown')

        # Load 03_input.txt
        input_path = session_path / "03_input.txt"
        if input_path.exists():
            with open(input_path, 'r', encoding='utf-8') as f:
                context['input_text'] = f.read().strip()

        # Load 06_interception.txt
        interception_path = session_path / "06_interception.txt"
        if interception_path.exists():
            with open(interception_path, 'r', encoding='utf-8') as f:
                context['interception_text'] = f.read().strip()

        # Load 02_config_used.json
        config_used_path = session_path / "02_config_used.json"
        if config_used_path.exists():
            with open(config_used_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                context['media_type'] = config_data.get('output_config', {}).get('media_type', 'unknown')

        logger.info(f"Session context loaded for run_id={run_id}")
        return {"success": True, "context": context}

    except Exception as e:
        logger.error(f"Error loading session context: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def load_chat_history(run_id: str) -> list:
    """Load chat history from exports/json/{run_id}/chat_history.json"""
    try:
        history_path = JSON_STORAGE_DIR / run_id / "chat_history.json"
        if history_path.exists():
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
                logger.info(f"Loaded {len(history)} messages from chat history")
                return history
        return []
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        return []


def save_chat_history(run_id: str, history: list):
    """Save chat history to exports/json/{run_id}/chat_history.json"""
    try:
        session_path = JSON_STORAGE_DIR / run_id
        if not session_path.exists():
            logger.warning(f"Session path not found for saving history: {session_path}")
            return

        history_path = session_path / "chat_history.json"
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved chat history with {len(history)} messages")
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")


def build_system_prompt(context: dict = None) -> str:
    """
    Build system prompt based on available context

    Args:
        context: Session context dict (or None for general mode)

    Returns:
        System prompt string
    """
    if context is None:
        return GENERAL_SYSTEM_PROMPT

    # Session mode - fill template
    return SESSION_SYSTEM_PROMPT_TEMPLATE.format(
        media_type=context.get('media_type', 'unbekannt'),
        config_name=context.get('config_name', 'unbekannt'),
        safety_level=context.get('safety_level', 'unbekannt'),
        input_text=context.get('input_text', '[noch nicht eingegeben]'),
        interception_text=context.get('interception_text', '[noch nicht transformiert]'),
        current_stage=context.get('current_stage', 'unbekannt')
    )


@chat_bp.route('', methods=['POST'])
def chat():
    """
    Chat endpoint with session context awareness

    POST /api/chat
    Body: {
        "message": "User's question",
        "run_id": "optional-uuid"  // If provided, loads session context
    }

    Response: {
        "reply": "Assistant's response",
        "context_used": true/false,
        "run_id": "uuid"  // Echoed back
    }
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        run_id = data.get('run_id')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Load session context if run_id provided
        context = None
        context_used = False

        if run_id:
            result = load_session_context(run_id)
            if result['success']:
                context = result['context']
                context_used = True
                logger.info(f"Using session context for run_id={run_id}")
            else:
                logger.warning(f"Could not load context for run_id={run_id}: {result.get('error')}")

        # Build system prompt
        system_prompt = build_system_prompt(context)

        # Load chat history (priority: run_id file > request history > empty)
        history = []
        if run_id:
            history = load_chat_history(run_id)
        elif 'history' in data and isinstance(data['history'], list):
            history = data['history']
            logger.info(f"Using history from request: {len(history)} messages")

        # Build messages for LLM
        messages = [{"role": "system", "content": system_prompt}]

        # Add history (skip system messages from history, we have fresh one)
        for msg in history:
            if msg['role'] != 'system':
                messages.append({"role": msg['role'], "content": msg['content']})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Call OpenRouter API
        logger.info(f"Calling OpenRouter with {len(messages)} messages (context_used={context_used})")

        assistant_reply = call_openrouter_chat(
            messages=messages,
            temperature=0.7,
            max_tokens=500  # Keep responses concise
        )

        # Save to history (if run_id provided)
        if run_id:
            timestamp = datetime.utcnow().isoformat()
            history.append({
                "role": "user",
                "content": user_message,
                "timestamp": timestamp
            })
            history.append({
                "role": "assistant",
                "content": assistant_reply,
                "timestamp": timestamp
            })
            save_chat_history(run_id, history)

        return jsonify({
            "reply": assistant_reply,
            "context_used": context_used,
            "run_id": run_id
        })

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@chat_bp.route('/history/<run_id>', methods=['GET'])
def get_history(run_id: str):
    """
    Get chat history for a session

    GET /api/chat/history/{run_id}

    Response: {
        "history": [...],
        "run_id": "uuid"
    }
    """
    try:
        history = load_chat_history(run_id)
        return jsonify({
            "history": history,
            "run_id": run_id
        })
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@chat_bp.route('/clear/<run_id>', methods=['DELETE'])
def clear_history(run_id: str):
    """
    Clear chat history for a session

    DELETE /api/chat/clear/{run_id}

    Response: {
        "success": true,
        "run_id": "uuid"
    }
    """
    try:
        history_path = JSON_STORAGE_DIR / run_id / "chat_history.json"
        if history_path.exists():
            history_path.unlink()
            logger.info(f"Cleared chat history for run_id={run_id}")

        return jsonify({
            "success": True,
            "run_id": run_id
        })
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500
