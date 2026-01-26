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
import asyncio
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
    Execute a canvas workflow using simple Tracer approach.

    Session 134: Complete rewrite - Tracer follows connections through the graph,
    passing data between nodes. At forks (evaluation), the score determines the path.

    Data Types:
    - text: string
    - image: dict with url, media_type, etc.

    Node Signatures:
    - input: () → text
    - interception: text → text
    - translation: text → text
    - generation: text → image
    - evaluation: text|image → text (+ decides output path)
    - display: text|image → (terminal)
    - collector: text|image → (terminal)
    """
    from schemas.engine.prompt_interception_engine import PromptInterceptionEngine, PromptInterceptionRequest
    import time
    import uuid

    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'error': 'JSON request expected'}), 400

        nodes = data.get('nodes', [])
        connections = data.get('connections', [])

        if not nodes:
            return jsonify({'status': 'error', 'error': 'No nodes provided'}), 400

        logger.info(f"[Canvas Tracer] Starting with {len(nodes)} nodes, {len(connections)} connections")

        # Build graph
        node_map = {n['id']: n for n in nodes}
        # outgoing[node_id] = [(target_id, label), ...]
        outgoing = {n['id']: [] for n in nodes}
        for conn in connections:
            src = conn.get('sourceId')
            tgt = conn.get('targetId')
            label = conn.get('label')  # 'passthrough', 'commented', 'commentary', 'feedback', or None
            if src and tgt:
                outgoing[src].append({'target': tgt, 'label': label})

        # Find input node
        input_node = None
        for n in nodes:
            if n.get('type') == 'input':
                input_node = n
                break

        if not input_node:
            return jsonify({'status': 'error', 'error': 'No input node found'}), 400

        # Execution state
        results = {}
        collector_items = []
        execution_trace = []
        engine = PromptInterceptionEngine()
        canvas_run_id = f"run_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"

        # Safety limit for feedback loops
        MAX_TOTAL_EXECUTIONS = 50
        execution_count = [0]  # Use list for nonlocal mutation

        def execute_node(node, input_data, data_type, source_node_id=None, source_node_type=None):
            """Execute a single node and return (output_data, output_type, metadata)"""
            node_id = node['id']
            node_type = node.get('type')

            logger.info(f"[Canvas Tracer] Executing {node_id} ({node_type})")

            if node_type == 'input':
                output = node.get('promptText', '')
                results[node_id] = {'type': 'input', 'output': output, 'error': None}
                return output, 'text', None

            elif node_type == 'interception':
                llm_model = node.get('llmModel', 'local/mistral-nemo')
                context_prompt = node.get('contextPrompt', '')

                if not input_data:
                    results[node_id] = {'type': 'interception', 'output': '', 'error': 'No input'}
                    return '', 'text', None

                req = PromptInterceptionRequest(
                    input_prompt=input_data,
                    style_prompt=context_prompt,
                    model=llm_model,
                    debug=True
                )
                response = asyncio.run(engine.process_request(req))
                output = response.output_str if response.success else ''
                results[node_id] = {
                    'type': 'interception',
                    'output': output,
                    'error': response.error if not response.success else None,
                    'model': response.model_used
                }
                logger.info(f"[Canvas Tracer] Interception: '{output[:50]}...'")
                return output, 'text', None

            elif node_type == 'translation':
                llm_model = node.get('llmModel', 'local/mistral-nemo')
                translation_prompt = node.get('translationPrompt', 'Translate to English:')

                if not input_data:
                    results[node_id] = {'type': 'translation', 'output': '', 'error': 'No input'}
                    return '', 'text', None

                req = PromptInterceptionRequest(
                    input_prompt=input_data,
                    style_prompt=translation_prompt,
                    model=llm_model,
                    debug=True
                )
                response = asyncio.run(engine.process_request(req))
                output = response.output_str if response.success else ''
                results[node_id] = {
                    'type': 'translation',
                    'output': output,
                    'error': response.error if not response.success else None,
                    'model': response.model_used
                }
                return output, 'text', None

            elif node_type == 'generation':
                # Session 136: Use execute_stage4_generation_only directly
                # Canvas handles translation via Translation node, so we skip Stage 3 entirely
                from my_app.routes.schema_pipeline_routes import execute_stage4_generation_only
                from config import DEFAULT_SAFETY_LEVEL

                config_id = node.get('configId')
                if not config_id:
                    results[node_id] = {'type': 'generation', 'output': None, 'error': 'No config'}
                    return None, 'image', None

                if not input_data:
                    results[node_id] = {'type': 'generation', 'output': None, 'error': 'No input'}
                    return None, 'image', None

                try:
                    # Call Stage 4 only - prompt is already translated by Canvas Translation node
                    gen_result = asyncio.run(execute_stage4_generation_only(
                        prompt=input_data,
                        output_config=config_id,
                        safety_level=DEFAULT_SAFETY_LEVEL,
                        run_id=canvas_run_id,
                        device_id=None
                    ))
                    if gen_result['success']:
                        output = gen_result['media_output']
                        results[node_id] = {'type': 'generation', 'output': output, 'error': None, 'configId': config_id}
                        logger.info(f"[Canvas Tracer] Generation: {output['url']}")
                        return output, 'image', None
                    else:
                        results[node_id] = {'type': 'generation', 'output': None, 'error': gen_result.get('error'), 'configId': config_id}
                        return None, 'image', None
                except Exception as e:
                    results[node_id] = {'type': 'generation', 'output': None, 'error': str(e), 'configId': config_id}
                    return None, 'image', None

            elif node_type == 'evaluation':
                llm_model = node.get('llmModel', 'local/mistral-nemo')
                evaluation_prompt = node.get('evaluationPrompt', '')
                output_type_setting = node.get('outputType', 'all')

                # Convert input to text for evaluation
                if isinstance(input_data, dict) and input_data.get('url'):
                    eval_input = f"[Media: {input_data.get('media_type', 'image')} at {input_data.get('url')}]"
                else:
                    eval_input = input_data or ''

                if not eval_input:
                    results[node_id] = {
                        'type': 'evaluation',
                        'outputs': {'passthrough': '', 'commented': '', 'commentary': ''},
                        'metadata': {'binary': None, 'score': None, 'active_path': None},
                        'error': 'No input'
                    }
                    return '', 'text', {'binary': None, 'score': None, 'active_path': None}

                # Build evaluation instruction
                instruction = f"{evaluation_prompt}\n\n"
                instruction += "Provide your evaluation in the following format:\n\n"
                instruction += "COMMENTARY: [Your detailed evaluation and feedback]\n"
                if output_type_setting in ['score', 'all']:
                    instruction += "SCORE: [Numeric score from 0 to 10 only]\n"
                instruction += "\nIMPORTANT: SCORE must be 0-10. Scores < 5 = FAILED, >= 5 = PASSED."

                req = PromptInterceptionRequest(
                    input_prompt=eval_input,
                    style_prompt=instruction,
                    model=llm_model,
                    debug=True
                )
                response = asyncio.run(engine.process_request(req))

                if not response.success:
                    results[node_id] = {
                        'type': 'evaluation',
                        'outputs': {'passthrough': '', 'commented': '', 'commentary': ''},
                        'metadata': {'binary': None, 'score': None, 'active_path': None},
                        'error': response.error
                    }
                    return '', 'text', {'binary': None, 'score': None, 'active_path': None}

                # Parse response
                commentary = ''
                score = None

                if 'COMMENTARY:' in response.output_str:
                    parts = response.output_str.split('COMMENTARY:')[1]
                    commentary = parts.split('SCORE:')[0].strip() if 'SCORE:' in parts else parts.strip()
                else:
                    commentary = response.output_str

                if response.output_float is not None:
                    score = float(response.output_float)
                elif 'SCORE:' in response.output_str:
                    import re
                    score_part = response.output_str.split('SCORE:')[1].split('\n')[0]
                    nums = re.findall(r'\d+\.?\d*', score_part)
                    if nums:
                        score = float(nums[0])

                if score is not None and (score < 0 or score > 10):
                    score = None

                binary_result = score >= 5.0 if score is not None else False
                active_path = 'passthrough' if binary_result else 'commented'

                passthrough_text = eval_input
                commented_text = f"{eval_input}\n\nFEEDBACK: {commentary}"
                commentary_text = commentary

                results[node_id] = {
                    'type': 'evaluation',
                    'outputs': {
                        'passthrough': passthrough_text,
                        'commented': commented_text,
                        'commentary': commentary_text
                    },
                    'metadata': {
                        'binary': binary_result,
                        'score': score,
                        'active_path': active_path
                    },
                    'error': None,
                    'model': response.model_used
                }
                logger.info(f"[Canvas Tracer] Evaluation: score={score}, binary={binary_result}, path={active_path}")

                # Return the appropriate output based on binary result
                output_text = passthrough_text if binary_result else commented_text
                return output_text, 'text', {'binary': binary_result, 'score': score, 'active_path': active_path}

            elif node_type == 'display':
                # Session 135: Display node (tap/observer) - records but doesn't propagate in flow
                display_title = node.get('title', 'Display')
                display_mode = node.get('displayMode', 'inline')
                results[node_id] = {
                    'type': 'display',
                    'output': input_data,
                    'error': None,
                    'displayData': {
                        'title': display_title,
                        'mode': display_mode,
                        'content': input_data,
                        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
                    }
                }
                logger.info(f"[Canvas Tracer] Display (tap): '{display_title}'")
                # Return None to signal this is a tap/observer (not part of main flow)
                return None, data_type, None

            elif node_type == 'collector':
                # Collector gathers what arrives - use old format for frontend compatibility
                # Include metadata from source node if available (e.g., evaluation score/binary)
                source_result = results.get(source_node_id, {}) if source_node_id else {}
                source_metadata = source_result.get('metadata')

                collector_item = {
                    'nodeId': source_node_id or node_id,
                    'nodeType': source_node_type or data_type,
                    'output': input_data,
                    'error': None
                }

                # For evaluation nodes, wrap output with metadata for frontend
                if source_node_type == 'evaluation' and source_metadata:
                    collector_item['output'] = {
                        'text': input_data,
                        'metadata': source_metadata
                    }

                collector_items.append(collector_item)
                results[node_id] = {
                    'type': 'collector',
                    'output': collector_items,
                    'error': None
                }
                logger.info(f"[Canvas Tracer] Collector: {len(collector_items)} items")
                return input_data, data_type, None  # Terminal

            else:
                results[node_id] = {'type': node_type, 'output': None, 'error': f'Unknown type: {node_type}'}
                return None, 'text', None

        def trace(node_id, input_data, data_type, source_node_id=None, source_node_type=None):
            """Trace through the graph starting from node_id with given input"""
            execution_count[0] += 1
            if execution_count[0] > MAX_TOTAL_EXECUTIONS:
                logger.warning(f"[Canvas Tracer] Max executions ({MAX_TOTAL_EXECUTIONS}) reached, stopping")
                return

            node = node_map.get(node_id)
            if not node:
                return

            execution_trace.append(node_id)

            # Execute this node (pass source info for collector)
            output_data, output_type, metadata = execute_node(node, input_data, data_type, source_node_id, source_node_type)

            # Get outgoing connections
            next_conns = outgoing.get(node_id, [])
            if not next_conns:
                return  # Terminal node

            node_type = node.get('type')

            # For evaluation nodes: filter connections based on score
            if node_type == 'evaluation' and metadata:
                active_path = metadata.get('active_path')  # 'passthrough' or 'commented'
                filtered_conns = []
                for conn in next_conns:
                    label = conn.get('label')
                    # Include if: no label, commentary (always), matches active_path, or feedback when commented
                    if not label:
                        filtered_conns.append(conn)
                    elif label == 'commentary':
                        filtered_conns.append(conn)
                    elif label == active_path:
                        filtered_conns.append(conn)
                    elif label == 'feedback' and active_path == 'commented':
                        filtered_conns.append(conn)
                next_conns = filtered_conns
                logger.info(f"[Canvas Tracer] Evaluation fork: active_path={active_path}, following {len(next_conns)} connections")

            # Session 135: Separate display nodes from flow (tap/observer pattern)
            display_conns = []
            flow_conns = []
            for conn in next_conns:
                target_node = node_map.get(conn['target'])
                if target_node and target_node.get('type') == 'display':
                    display_conns.append(conn)
                else:
                    flow_conns.append(conn)

            # Session 135: Execute display nodes in parallel (fire-and-forget)
            for conn in display_conns:
                target_id = conn['target']
                target_node = node_map.get(target_id)
                if not target_node:
                    continue
                # Execute display but don't recurse
                execute_node(target_node, output_data, output_type, node_id, node_type)

            # Follow each active flow connection (non-display)
            for conn in flow_conns:
                target_id = conn['target']
                target_node = node_map.get(target_id)
                if not target_node:
                    continue

                # Data type compatibility check
                target_type = target_node.get('type')
                accepts_text = target_type in ['interception', 'translation', 'generation', 'evaluation', 'collector']
                accepts_image = target_type in ['evaluation', 'collector']

                if output_type == 'text' and not accepts_text:
                    logger.warning(f"[Canvas Tracer] Type mismatch: {node_id} outputs text, {target_id} ({target_type}) doesn't accept it")
                    continue
                if output_type == 'image' and not accepts_image:
                    logger.warning(f"[Canvas Tracer] Type mismatch: {node_id} outputs image, {target_id} ({target_type}) doesn't accept it")
                    continue

                # For evaluation with specific output paths
                if node_type == 'evaluation' and metadata:
                    conn_label = conn.get('label')
                    # Get the right output based on connection label
                    if conn_label == 'commentary':
                        trace_data = results[node_id]['outputs']['commentary']
                    elif conn_label == 'passthrough':
                        trace_data = results[node_id]['outputs']['passthrough']
                    elif conn_label in ['commented', 'feedback']:
                        trace_data = results[node_id]['outputs']['commented']
                    else:
                        trace_data = output_data
                else:
                    trace_data = output_data

                # Recurse - pass source node info for collector
                trace(target_id, trace_data, output_type, node_id, node_type)

        # Start tracing from input
        input_text = input_node.get('promptText', '')
        logger.info(f"[Canvas Tracer] Starting from input: '{input_text[:50]}...'")
        trace(input_node['id'], None, 'text')  # Input node doesn't receive data

        logger.info(f"[Canvas Tracer] Complete. {execution_count[0]} executions, {len(collector_items)} collected items")
        logger.info(f"[Canvas Tracer] Trace: {' -> '.join(execution_trace)}")

        return jsonify({
            'status': 'success',
            'results': results,
            'collectorOutput': collector_items,
            'executionOrder': execution_trace
        })

    except Exception as e:
        logger.error(f"[Canvas Tracer] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
