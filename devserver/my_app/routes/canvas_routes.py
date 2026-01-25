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
    Execute a canvas workflow - Phase 2/3 Implementation

    Session 133: Basic execution for LLM nodes (interception, translation)

    Request Body:
    {
        "nodes": [...],       # CanvasNode[]
        "connections": [...], # CanvasConnection[]
        "workflow": {...}     # Full workflow metadata (optional)
    }

    Returns:
    {
        "status": "success",
        "results": {
            "<nodeId>": {
                "type": "input|interception|translation|generation|collector",
                "output": "...",  # Text output for LLM nodes
                "error": null     # Or error message if failed
            },
            ...
        },
        "collectorOutput": [...],  # All outputs collected at collector node
        "executionOrder": [...]    # Node IDs in execution order
    }
    """
    from schemas.engine.prompt_interception_engine import PromptInterceptionEngine, PromptInterceptionRequest

    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'error': 'JSON request expected'}), 400

        nodes = data.get('nodes', [])
        connections = data.get('connections', [])

        if not nodes:
            return jsonify({'status': 'error', 'error': 'No nodes provided'}), 400

        logger.info(f"[Canvas Execute] Starting execution with {len(nodes)} nodes, {len(connections)} connections")

        # Build node lookup and adjacency
        node_map = {n['id']: n for n in nodes}
        # incoming[nodeId] = list of source node IDs
        incoming = {n['id']: [] for n in nodes}
        # outgoing[nodeId] = list of target node IDs
        outgoing = {n['id']: [] for n in nodes}

        for conn in connections:
            source_id = conn.get('sourceId')
            target_id = conn.get('targetId')
            if source_id and target_id:
                incoming[target_id].append(source_id)
                outgoing[source_id].append(target_id)

        # Topological sort (Kahn's algorithm)
        in_degree = {nid: len(incoming[nid]) for nid in node_map}
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        execution_order = []

        while queue:
            nid = queue.pop(0)
            execution_order.append(nid)
            for target in outgoing[nid]:
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)

        if len(execution_order) != len(nodes):
            return jsonify({'status': 'error', 'error': 'Cycle detected in workflow'}), 400

        logger.info(f"[Canvas Execute] Execution order: {execution_order}")

        # Execute nodes in order
        results = {}
        engine = PromptInterceptionEngine()

        for node_id in execution_order:
            node = node_map[node_id]
            node_type = node.get('type')

            logger.info(f"[Canvas Execute] Processing node {node_id} (type: {node_type})")

            try:
                if node_type == 'input':
                    # Input node: just pass through the prompt text
                    prompt_text = node.get('promptText', '')
                    results[node_id] = {
                        'type': 'input',
                        'output': prompt_text,
                        'error': None
                    }
                    logger.info(f"[Canvas Execute] Input node: '{prompt_text[:50]}...'")

                elif node_type == 'interception':
                    # Interception node: transform text with LLM
                    # Get input from connected source node
                    source_ids = incoming[node_id]
                    input_text = ''
                    for src_id in source_ids:
                        if src_id in results and results[src_id].get('output'):
                            input_text = results[src_id]['output']
                            break

                    llm_model = node.get('llmModel', 'local/mistral-nemo')
                    context_prompt = node.get('contextPrompt', '')

                    if not input_text:
                        results[node_id] = {
                            'type': 'interception',
                            'output': '',
                            'error': 'No input text from source node'
                        }
                    else:
                        # Call LLM
                        req = PromptInterceptionRequest(
                            input_prompt=input_text,
                            style_prompt=context_prompt,
                            model=llm_model,
                            debug=True
                        )
                        response = asyncio.run(engine.process_request(req))

                        results[node_id] = {
                            'type': 'interception',
                            'output': response.output_str if response.success else '',
                            'error': response.error if not response.success else None,
                            'model': response.model_used
                        }
                        logger.info(f"[Canvas Execute] Interception result: '{response.output_str[:50] if response.output_str else 'empty'}' (model: {response.model_used})")

                elif node_type == 'translation':
                    # Translation node: translate with LLM
                    source_ids = incoming[node_id]
                    input_text = ''
                    for src_id in source_ids:
                        if src_id in results and results[src_id].get('output'):
                            input_text = results[src_id]['output']
                            break

                    llm_model = node.get('llmModel', 'local/mistral-nemo')
                    translation_prompt = node.get('translationPrompt', 'Translate to English:')

                    if not input_text:
                        results[node_id] = {
                            'type': 'translation',
                            'output': '',
                            'error': 'No input text from source node'
                        }
                    else:
                        # Call LLM with translation prompt
                        req = PromptInterceptionRequest(
                            input_prompt=input_text,
                            style_prompt=translation_prompt,
                            model=llm_model,
                            debug=True
                        )
                        response = asyncio.run(engine.process_request(req))

                        results[node_id] = {
                            'type': 'translation',
                            'output': response.output_str if response.success else '',
                            'error': response.error if not response.success else None,
                            'model': response.model_used
                        }
                        logger.info(f"[Canvas Execute] Translation result: '{response.output_str[:50] if response.output_str else 'empty'}'")

                elif node_type == 'generation':
                    # Generation node: call actual media generation
                    # Session 133: Integrated with execute_generation_stage4 helper
                    source_ids = incoming[node_id]
                    input_text = ''
                    for src_id in source_ids:
                        if src_id in results and results[src_id].get('output'):
                            input_text = results[src_id]['output']
                            break

                    config_id = node.get('configId')

                    # Validate
                    if not config_id:
                        results[node_id] = {
                            'type': 'generation',
                            'output': None,
                            'error': 'No output config selected'
                        }
                        continue

                    if not input_text:
                        results[node_id] = {
                            'type': 'generation',
                            'output': None,
                            'error': 'No input text from source node'
                        }
                        continue

                    # Import helper and config
                    from my_app.routes.schema_pipeline_routes import execute_generation_stage4
                    from config import DEFAULT_SAFETY_LEVEL
                    import uuid
                    import time

                    # Create shared run_id for all generations in this Canvas workflow
                    if 'canvas_run_id' not in locals():
                        canvas_run_id = f"run_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"

                    try:
                        # Call generation helper
                        gen_result = asyncio.run(execute_generation_stage4(
                            prompt=input_text,
                            output_config=config_id,
                            safety_level=DEFAULT_SAFETY_LEVEL,
                            run_id=canvas_run_id,
                            device_id=None,  # Auto-generated
                            input_text='',  # No original user input in Canvas context
                            context_prompt='',
                            interception_result='',
                            interception_config=''
                        ))

                        if gen_result['success']:
                            results[node_id] = {
                                'type': 'generation',
                                'output': gen_result['media_output'],
                                'error': None,
                                'configId': config_id
                            }
                            logger.info(f"[Canvas Execute] Generation success: {gen_result['media_output']['url']}")
                        else:
                            results[node_id] = {
                                'type': 'generation',
                                'output': None,
                                'error': gen_result.get('error', 'Generation failed'),
                                'configId': config_id
                            }
                            logger.error(f"[Canvas Execute] Generation error: {gen_result.get('error')}")

                    except Exception as e:
                        logger.error(f"[Canvas Execute] Generation exception: {e}")
                        results[node_id] = {
                            'type': 'generation',
                            'output': None,
                            'error': str(e),
                            'configId': config_id
                        }

                elif node_type == 'evaluation':
                    # Session 134: Evaluation nodes - LLM-based judgment
                    source_ids = incoming[node_id]
                    input_text = ''
                    for src_id in source_ids:
                        if src_id in results and results[src_id].get('output'):
                            output = results[src_id]['output']
                            # Handle text or media inputs
                            if isinstance(output, str):
                                input_text = output
                            elif isinstance(output, dict) and output.get('url'):
                                # For media, describe what we're evaluating
                                input_text = f"[Evaluating generated media: {output.get('media_type', 'image')} at {output.get('url')}]"
                            break

                    llm_model = node.get('llmModel', 'local/mistral-nemo')
                    evaluation_prompt = node.get('evaluationPrompt', '')
                    output_type = node.get('outputType', 'all')

                    if not input_text:
                        results[node_id] = {
                            'type': 'evaluation',
                            'outputs': {
                                'passthrough': '',
                                'commented': '',
                                'commentary': 'ERROR: No input from source node'
                            },
                            'metadata': {
                                'binary': None,
                                'score': None,
                                'active_path': None
                            },
                            'error': 'No input from source node'
                        }
                    else:
                        # Build evaluation instruction
                        # Session 134: ALWAYS request binary+commentary (for fork nodes), optionally request score
                        evaluation_instruction = f"{evaluation_prompt}\n\nProvide your evaluation in the following format:\n"
                        evaluation_instruction += "COMMENTARY: [Your detailed evaluation and feedback]\n"
                        evaluation_instruction += "BINARY: [true/false - does this pass the evaluation criteria?]\n"
                        if output_type in ['score', 'all']:
                            evaluation_instruction += "SCORE: [0-10]\n"

                        # Call LLM
                        req = PromptInterceptionRequest(
                            input_prompt=input_text,
                            style_prompt=evaluation_instruction,
                            model=llm_model,
                            debug=True
                        )
                        response = asyncio.run(engine.process_request(req))

                        if response.success:
                            # Parse evaluation output
                            commentary = ''
                            score = None
                            binary_result = None

                            # Extract commentary
                            if 'COMMENTARY:' in response.output_str:
                                commentary_match = response.output_str.split('COMMENTARY:')[1].split('\n')[0].strip()
                                commentary = commentary_match or response.output_str
                            else:
                                commentary = response.output_str

                            # Extract score (use output_float if available)
                            if response.output_float is not None:
                                score = float(response.output_float)
                            elif 'SCORE:' in response.output_str:
                                try:
                                    score_match = response.output_str.split('SCORE:')[1].split('\n')[0].strip()
                                    score = float(score_match)
                                except (ValueError, IndexError):
                                    pass

                            # Extract binary (use output_binary if available)
                            if response.output_binary is not None:
                                binary_result = response.output_binary
                            elif 'BINARY:' in response.output_str:
                                binary_match = response.output_str.split('BINARY:')[1].split('\n')[0].strip().lower()
                                binary_result = binary_match in ['true', 'yes', '1', 'pass']
                            else:
                                # Fallback: If no binary found, default to True (pass)
                                binary_result = True
                                logger.warning(f"[Canvas Execute] Evaluation {node_id}: No binary result found, defaulting to True")

                            # Session 134 Refactored: 3 separate TEXT outputs
                            # 1. Passthrough: original input (active if binary=true)
                            # 2. Commented: input + feedback (active if binary=false)
                            # 3. Commentary: just the commentary (always active, for display/collector)

                            passthrough_text = input_text  # Original unchanged
                            commented_text = f"{input_text}\n\nFEEDBACK: {commentary}"  # Input + feedback
                            commentary_text = commentary  # Just commentary

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
                                    'active_path': 'passthrough' if binary_result else 'commented'
                                },
                                'error': None,
                                'model': response.model_used
                            }
                            logger.info(f"[Canvas Execute] Evaluation result: binary={binary_result}, score={score}, active_path={'passthrough' if binary_result else 'commented'}")
                        else:
                            results[node_id] = {
                                'type': 'evaluation',
                                'outputs': {
                                    'passthrough': '',
                                    'commented': '',
                                    'commentary': ''
                                },
                                'metadata': {
                                    'binary': None,
                                    'score': None,
                                    'active_path': None
                                },
                                'error': response.error,
                                'model': response.model_used
                            }

                elif node_type == 'display':
                    # Session 134: Display node - pass-through with display data
                    source_ids = incoming[node_id]
                    input_data = None
                    for src_id in source_ids:
                        if src_id in results and results[src_id].get('output'):
                            input_data = results[src_id]['output']
                            break

                    display_title = node.get('title', 'Display')
                    display_mode = node.get('displayMode', 'inline')

                    if input_data is not None:
                        # Pass through the input data unchanged
                        results[node_id] = {
                            'type': 'display',
                            'output': input_data,  # Pass-through
                            'error': None,
                            'displayData': {
                                'title': display_title,
                                'mode': display_mode,
                                'content': input_data,
                                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
                            }
                        }
                        logger.info(f"[Canvas Execute] Display node: title='{display_title}', mode='{display_mode}'")
                    else:
                        results[node_id] = {
                            'type': 'display',
                            'output': None,
                            'error': 'No input from source node'
                        }

                elif node_type == 'collector':
                    # Collector node: gather all inputs
                    # Session 134: Handle both old format (output) and new format (outputs+metadata)
                    source_ids = incoming[node_id]
                    collected = []
                    for src_id in source_ids:
                        if src_id in results:
                            result = results[src_id]
                            # For evaluation nodes: include outputs and metadata
                            if result.get('type') == 'evaluation':
                                collected.append({
                                    'nodeId': src_id,
                                    'nodeType': result.get('type'),
                                    'output': {
                                        'outputs': result.get('outputs'),
                                        'metadata': result.get('metadata')
                                    },
                                    'error': result.get('error')
                                })
                            else:
                                # Other nodes: use 'output' field as before
                                collected.append({
                                    'nodeId': src_id,
                                    'nodeType': result.get('type'),
                                    'output': result.get('output'),
                                    'error': result.get('error')
                                })

                    results[node_id] = {
                        'type': 'collector',
                        'output': collected,
                        'error': None
                    }
                    logger.info(f"[Canvas Execute] Collector gathered {len(collected)} outputs")

                else:
                    results[node_id] = {
                        'type': node_type,
                        'output': None,
                        'error': f'Unknown node type: {node_type}'
                    }

            except Exception as e:
                logger.error(f"[Canvas Execute] Error processing node {node_id}: {e}")
                results[node_id] = {
                    'type': node_type,
                    'output': None,
                    'error': str(e)
                }

        # Find collector output
        collector_output = []
        for node in nodes:
            if node.get('type') == 'collector' and node['id'] in results:
                collector_output = results[node['id']].get('output', [])
                break

        logger.info(f"[Canvas Execute] Execution complete. Collector has {len(collector_output)} items.")

        return jsonify({
            'status': 'success',
            'results': results,
            'collectorOutput': collector_output,
            'executionOrder': execution_order
        })

    except Exception as e:
        logger.error(f"[Canvas Execute] Fatal error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
