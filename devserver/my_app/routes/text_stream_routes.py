"""
Text streaming routes for real-time text generation progress
Supports Stage 1-4 text streaming with SSE (Server-Sent Events)

ARCHITECTURE:
  Frontend (Vue) connects via EventSource to these endpoints
    → SSE stream with 'chunk' events (character-by-character text)
    → 'complete' event when done
    → 'error' event on failure

USAGE:
  - Stage 1: Translation + Safety → /api/text_stream/stage1/<run_id>
  - Stage 2: Prompt Interception → /api/text_stream/stage2/<run_id>
  - Stage 3: Final Safety Check → /api/text_stream/stage3/<run_id>
  - Stage 4: Text Output Generation → /api/text_stream/stage4/<run_id>
"""
import json
import logging
from flask import Blueprint, Response, request, current_app, stream_with_context
from my_app.services.ollama_service import ollama_service
from schemas.engine.prompt_interception_engine import PromptInterceptionEngine

logger = logging.getLogger(__name__)

# Create blueprint
text_stream_bp = Blueprint('text_stream', __name__)


def generate_sse_event(event_type: str, data: dict) -> str:
    """
    Generate SSE formatted event

    Args:
        event_type: Event name (e.g., 'chunk', 'complete', 'error')
        data: Event data dictionary

    Returns:
        SSE formatted string
    """
    event = f"event: {event_type}\n"
    event += f"data: {json.dumps(data)}\n\n"
    return event


@text_stream_bp.route('/api/text_stream/stage1/<run_id>')
def stream_stage1_translation(run_id: str):
    """
    Stream Stage 1 translation + safety check

    Query params:
        text: Text to translate (required)

    SSE Events:
        - connected: Initial connection established
        - chunk: Text chunk with accumulated text
        - complete: Final text with completion status
        - error: Error message

    Returns:
        SSE stream response
    """
    # Extract request data before generator
    text = request.args.get('text', '')

    def generate():
        try:

            if not text:
                yield generate_sse_event('error', {'message': 'Missing required parameter: text'})
                return

            # Send initial connection event
            yield generate_sse_event('connected', {
                'stage': 'stage1',
                'run_id': run_id,
                'status': 'streaming'
            })

            logger.info(f"[TEXT_STREAM] Stage 1 translation stream started for run {run_id}")

            # Stream translation
            accumulated = ""
            chunk_count = 0

            for chunk in ollama_service.translate_text_stream(text):
                accumulated += chunk
                chunk_count += 1

                yield generate_sse_event('chunk', {
                    'text_chunk': chunk,
                    'accumulated': accumulated,
                    'chunk_count': chunk_count
                })
                yield ''  # Force flush to bypass Waitress buffering

            logger.info(f"[TEXT_STREAM] Stage 1 translation complete: {len(accumulated)} chars, {chunk_count} chunks")

            # TODO: Run safety check on translated text (currently skipped for streaming UX)
            # For now, assume safe - full safety check happens in Stage 3

            # Send completion event
            yield generate_sse_event('complete', {
                'final_text': accumulated,
                'status': 'completed',
                'char_count': len(accumulated),
                'chunk_count': chunk_count
            })

        except Exception as e:
            logger.error(f"[TEXT_STREAM] Stage 1 streaming error: {e}")
            yield generate_sse_event('error', {
                'message': str(e),
                'stage': 'stage1'
            })

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable Nginx buffering
    # CORS handled by Flask-CORS globally (see my_app/__init__.py)
    return response


@text_stream_bp.route('/api/text_stream/stage2/<run_id>')
def stream_stage2_interception(run_id: str):
    """
    Stream Stage 2 prompt interception (pedagogical transformation)

    Query params:
        prompt: Input prompt (required)
        context: Input context (optional, default: "")
        style_prompt: Style/task prompt (optional, default: "")
        model: Model to use (optional, default: from config)

    SSE Events:
        - connected: Initial connection established
        - chunk: Text chunk with accumulated text
        - complete: Final text with completion status
        - error: Error message

    Returns:
        SSE stream response
    """
    # IMPORTANT: Extract all request data BEFORE the generator
    # (request context not available inside generator)
    import config  # Import module, not attribute (for runtime access to user_settings.json)
    prompt = request.args.get('prompt', '')
    context = request.args.get('context', '')
    style_prompt = request.args.get('style_prompt', '')
    model = request.args.get('model', config.STAGE2_INTERCEPTION_MODEL)  # Reads user_settings.json override

    def generate():
        try:
            if not prompt:
                yield generate_sse_event('error', {'message': 'Missing required parameter: prompt'})
                return

            # Send initial connection event
            yield generate_sse_event('connected', {
                'stage': 'stage2',
                'run_id': run_id,
                'status': 'streaming',
                'model': model
            })

            logger.info(f"[TEXT_STREAM] Stage 2 interception stream started for run {run_id} with model {model}")

            # Build full prompt
            engine = PromptInterceptionEngine()
            full_prompt = engine.build_full_prompt(prompt, context, style_prompt)

            accumulated = ""
            chunk_count = 0

            # Route to appropriate streaming method based on model prefix
            if model.startswith("mistral/"):
                # Mistral streaming
                real_model = engine.extract_model_name(model)
                for chunk in engine._call_mistral_stream(full_prompt, real_model, debug=False):
                    accumulated += chunk
                    chunk_count += 1

                    yield generate_sse_event('chunk', {
                        'text_chunk': chunk,
                        'accumulated': accumulated,
                        'chunk_count': chunk_count
                    })
                    yield ''  # Force flush to bypass Waitress buffering

            elif model.startswith("local/") or not any(model.startswith(p) for p in ["mistral/", "openai/", "anthropic/", "bedrock/", "openrouter/"]):
                # Ollama streaming (local models)
                from config import OLLAMA_API_BASE_URL
                import requests

                real_model = engine.extract_model_name(model)

                payload = {
                    "model": real_model,
                    "prompt": full_prompt,
                    "stream": True
                }

                response = requests.post(
                    f"{OLLAMA_API_BASE_URL}/api/generate",
                    json=payload,
                    stream=True,
                    timeout=90
                )
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            text_chunk = data.get("response", "")
                            done = data.get("done", False)

                            if text_chunk:
                                accumulated += text_chunk
                                chunk_count += 1

                                yield generate_sse_event('chunk', {
                                    'text_chunk': text_chunk,
                                    'accumulated': accumulated,
                                    'chunk_count': chunk_count
                                })
                                yield ''  # Force flush to bypass Waitress buffering

                            if done:
                                break
                        except json.JSONDecodeError:
                            continue

            else:
                # Unsupported model for streaming (fallback to error)
                yield generate_sse_event('error', {
                    'message': f'Streaming not yet supported for model: {model}',
                    'fallback': 'batch'
                })
                return

            logger.info(f"[TEXT_STREAM] Stage 2 interception complete: {len(accumulated)} chars, {chunk_count} chunks")

            # Send completion event
            yield generate_sse_event('complete', {
                'final_text': accumulated,
                'status': 'completed',
                'char_count': len(accumulated),
                'chunk_count': chunk_count,
                'model_used': model
            })

        except Exception as e:
            logger.error(f"[TEXT_STREAM] Stage 2 streaming error: {e}")
            yield generate_sse_event('error', {
                'message': str(e),
                'stage': 'stage2'
            })

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable Nginx buffering
    # CORS handled by Flask-CORS globally (see my_app/__init__.py)
    return response


@text_stream_bp.route('/api/text_stream/stage3/<run_id>')
def stream_stage3_safety(run_id: str):
    """
    Stream Stage 3 final safety check

    Note: Safety checks typically return very short responses (SAFE/BLOCKED),
    so streaming may not provide significant UX benefit. This endpoint is
    provided for consistency.

    Query params:
        text: Text to check (required)

    SSE Events:
        - connected: Initial connection established
        - chunk: Text chunk with accumulated text
        - complete: Final text with safety status
        - error: Error message

    Returns:
        SSE stream response
    """
    # Extract request data before generator
    text = request.args.get('text', '')

    def generate():
        try:

            if not text:
                yield generate_sse_event('error', {'message': 'Missing required parameter: text'})
                return

            # Send initial connection event
            yield generate_sse_event('connected', {
                'stage': 'stage3',
                'run_id': run_id,
                'status': 'streaming'
            })

            logger.info(f"[TEXT_STREAM] Stage 3 safety check stream started for run {run_id}")

            # Stream safety check
            accumulated = ""
            chunk_count = 0

            for chunk in ollama_service.check_safety_gpt_oss_stream(text, keep_alive="10m"):
                accumulated += chunk
                chunk_count += 1

                yield generate_sse_event('chunk', {
                    'text_chunk': chunk,
                    'accumulated': accumulated,
                    'chunk_count': chunk_count
                })
                yield ''  # Force flush to bypass Waitress buffering

            logger.info(f"[TEXT_STREAM] Stage 3 safety check complete: {len(accumulated)} chars")

            # Parse safety response (SAFE: ... or BLOCKED: ...)
            is_safe = accumulated.startswith("SAFE:")

            # Send completion event
            yield generate_sse_event('complete', {
                'final_text': accumulated,
                'status': 'completed',
                'is_safe': is_safe,
                'char_count': len(accumulated),
                'chunk_count': chunk_count
            })

        except Exception as e:
            logger.error(f"[TEXT_STREAM] Stage 3 streaming error: {e}")
            yield generate_sse_event('error', {
                'message': str(e),
                'stage': 'stage3'
            })

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable Nginx buffering
    # CORS handled by Flask-CORS globally (see my_app/__init__.py)
    return response


@text_stream_bp.route('/api/text_stream/stage4/<run_id>')
def stream_stage4_output(run_id: str):
    """
    Stream Stage 4 text output generation (e.g., code generation, creative writing)

    Query params:
        prompt: Input prompt (required)
        model: Model to use (optional, default: from config)

    SSE Events:
        - connected: Initial connection established
        - chunk: Text chunk with accumulated text
        - complete: Final text with completion status
        - error: Error message

    Returns:
        SSE stream response
    """
    # Extract request data before generator
    import config  # Import module, not attribute (for runtime access to user_settings.json)
    prompt = request.args.get('prompt', '')
    model = request.args.get('model', config.STAGE4_LEGACY_MODEL)  # Reads user_settings.json override

    def generate():
        try:

            if not prompt:
                yield generate_sse_event('error', {'message': 'Missing required parameter: prompt'})
                return

            # Send initial connection event
            yield generate_sse_event('connected', {
                'stage': 'stage4',
                'run_id': run_id,
                'status': 'streaming',
                'model': model
            })

            logger.info(f"[TEXT_STREAM] Stage 4 output generation stream started for run {run_id}")

            accumulated = ""
            chunk_count = 0

            # For Stage 4, we use direct Ollama API call (simpler than full interception engine)
            from config import OLLAMA_API_BASE_URL
            import requests

            # Extract model name
            real_model = model.replace("local/", "") if model.startswith("local/") else model

            payload = {
                "model": real_model,
                "prompt": prompt,
                "stream": True
            }

            response = requests.post(
                f"{OLLAMA_API_BASE_URL}/api/generate",
                json=payload,
                stream=True,
                timeout=120  # Longer timeout for text generation
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        text_chunk = data.get("response", "")
                        done = data.get("done", False)

                        if text_chunk:
                            accumulated += text_chunk
                            chunk_count += 1

                            yield generate_sse_event('chunk', {
                                'text_chunk': text_chunk,
                                'accumulated': accumulated,
                                'chunk_count': chunk_count
                            })
                            yield ''  # Force flush to bypass Waitress buffering

                        if done:
                            break
                    except json.JSONDecodeError:
                        continue

            logger.info(f"[TEXT_STREAM] Stage 4 output generation complete: {len(accumulated)} chars, {chunk_count} chunks")

            # Send completion event
            yield generate_sse_event('complete', {
                'final_text': accumulated,
                'status': 'completed',
                'char_count': len(accumulated),
                'chunk_count': chunk_count,
                'model_used': model
            })

        except Exception as e:
            logger.error(f"[TEXT_STREAM] Stage 4 streaming error: {e}")
            yield generate_sse_event('error', {
                'message': str(e),
                'stage': 'stage4'
            })

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable Nginx buffering
    # CORS handled by Flask-CORS globally (see my_app/__init__.py)
    return response


@text_stream_bp.route('/api/text_stream/optimize/<run_id>')
def stream_optimization(run_id: str):
    """
    Stream prompt optimization (model-specific transformation)

    Query params:
        input_text: Text to optimize (required)
        optimization_instruction: Optimization rules from output chunk (required)
        output_config: Output config ID (for metadata, required)
        model: Model to use (optional, default: from config)

    SSE Events:
        - connected: Initial connection established
        - chunk: Text chunk with accumulated text
        - complete: Final text with completion status
        - error: Error message

    Returns:
        SSE stream response
    """
    # IMPORTANT: Extract all request data BEFORE the generator
    # (request context not available inside generator)
    import config  # Import module, not attribute (for runtime access to user_settings.json)
    input_text = request.args.get('input_text', '')
    optimization_instruction = request.args.get('optimization_instruction', '')
    output_config = request.args.get('output_config', '')
    model = request.args.get('model', config.STAGE2_INTERCEPTION_MODEL)  # Reads user_settings.json override

    def generate():
        try:
            if not input_text:
                yield generate_sse_event('error', {'message': 'Missing required parameter: input_text'})
                return

            # Send initial connection event
            yield generate_sse_event('connected', {
                'stage': 'optimize',
                'run_id': run_id,
                'status': 'streaming',
                'model': model,
                'output_config': output_config
            })

            # If no optimization_instruction, just return input unchanged (no LLM call needed)
            if not optimization_instruction or optimization_instruction.strip() == '':
                logger.info(f"[TEXT_STREAM] No optimization needed for {run_id}, returning input unchanged")

                # Send complete event immediately with unchanged input
                yield generate_sse_event('complete', {
                    'final_text': input_text,
                    'status': 'completed',
                    'char_count': len(input_text),
                    'chunk_count': 0,
                    'model_used': model,
                    'output_config': output_config,
                    'optimization_applied': False
                })
                return

            logger.info(f"[TEXT_STREAM] Optimization stream started for run {run_id} with model {model}")

            # Build full prompt for optimization
            # Uses same structure as execute_optimization() function
            engine = PromptInterceptionEngine()
            style_prompt = "Transform the INPUT according to the rules provided by the CONTEXT. Preserve structural aspects of the INPUT and follow all instructions in the CONTEXT precisely."
            full_prompt = engine.build_full_prompt(input_text, optimization_instruction, style_prompt)

            accumulated = ""
            chunk_count = 0

            # Route to appropriate streaming method based on model prefix
            if model.startswith("mistral/"):
                # Mistral streaming
                real_model = engine.extract_model_name(model)
                for chunk in engine._call_mistral_stream(full_prompt, real_model, debug=False):
                    accumulated += chunk
                    chunk_count += 1

                    yield generate_sse_event('chunk', {
                        'text_chunk': chunk,
                        'accumulated': accumulated,
                        'chunk_count': chunk_count
                    })
                    yield ''  # Force flush to bypass Waitress buffering

            elif model.startswith("local/") or not any(model.startswith(p) for p in ["mistral/", "openai/", "anthropic/", "bedrock/", "openrouter/"]):
                # Ollama streaming (local models)
                from config import OLLAMA_API_BASE_URL
                import requests

                real_model = engine.extract_model_name(model)

                payload = {
                    "model": real_model,
                    "prompt": full_prompt,
                    "stream": True
                }

                response = requests.post(
                    f"{OLLAMA_API_BASE_URL}/api/generate",
                    json=payload,
                    stream=True,
                    timeout=90
                )
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            text_chunk = data.get("response", "")
                            done = data.get("done", False)

                            if text_chunk:
                                accumulated += text_chunk
                                chunk_count += 1

                                yield generate_sse_event('chunk', {
                                    'text_chunk': text_chunk,
                                    'accumulated': accumulated,
                                    'chunk_count': chunk_count
                                })
                                yield ''  # Force flush to bypass Waitress buffering

                            if done:
                                break
                        except json.JSONDecodeError:
                            continue

            else:
                # Unsupported model for streaming (fallback to error)
                yield generate_sse_event('error', {
                    'message': f'Streaming not yet supported for model: {model}',
                    'fallback': 'batch'
                })
                return

            logger.info(f"[TEXT_STREAM] Optimization complete: {len(accumulated)} chars, {chunk_count} chunks")

            # Send completion event
            yield generate_sse_event('complete', {
                'final_text': accumulated,
                'status': 'completed',
                'char_count': len(accumulated),
                'chunk_count': chunk_count,
                'model_used': model,
                'output_config': output_config
            })

        except Exception as e:
            logger.error(f"[TEXT_STREAM] Optimization streaming error: {e}")
            yield generate_sse_event('error', {
                'message': str(e),
                'stage': 'optimize'
            })

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable Nginx buffering
    # CORS handled by Flask-CORS globally (see my_app/__init__.py)
    return response
