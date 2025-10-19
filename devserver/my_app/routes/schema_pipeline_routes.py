"""
Schema Pipeline Routes - API für Schema-basierte Pipeline-Execution
"""

from flask import Blueprint, request, jsonify
from pathlib import Path
import logging
import asyncio

# Schema-Engine importieren
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from schemas.engine.pipeline_executor import PipelineExecutor
from schemas.engine.prompt_interception_engine import PromptInterceptionEngine

logger = logging.getLogger(__name__)

# Blueprint erstellen
schema_bp = Blueprint('schema', __name__, url_prefix='/api/schema')

# Global Pipeline-Executor (wird bei App-Start initialisiert)
pipeline_executor = None

def init_schema_engine():
    """Schema-Engine initialisieren"""
    global pipeline_executor
    if pipeline_executor is None:
        schemas_path = Path(__file__).parent.parent.parent / "schemas"
        pipeline_executor = PipelineExecutor(schemas_path)
        
        # Config Loader initialisieren (ohne Legacy-Services vorerst)
        pipeline_executor.config_loader.initialize(schemas_path)
        
        logger.info("Schema-Engine initialisiert")

@schema_bp.route('/info', methods=['GET'])
def get_schema_info():
    """Schema-System Informationen"""
    try:
        init_schema_engine()
        
        available_schemas = pipeline_executor.get_available_schemas()
        
        return jsonify({
            'status': 'success',
            'schemas_available': len(available_schemas),
            'schemas': available_schemas,
            'engine_status': 'initialized'
        })
        
    except Exception as e:
        logger.error(f"Schema-Info Fehler: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@schema_bp.route('/pipeline/execute', methods=['POST'])
def execute_pipeline():
    """Schema-Pipeline ausführen"""
    try:
        # Request-Validation
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'JSON-Request erwartet'
            }), 400
        
        schema_name = data.get('schema')
        input_text = data.get('input_text')
        
        if not schema_name or not input_text:
            return jsonify({
                'status': 'error',
                'error': 'Parameter "schema" und "input_text" erforderlich'
            }), 400
        
        # Schema-Engine initialisieren
        init_schema_engine()
        
        # Pipeline ausführen (synchron für einfache Integration)
        result = asyncio.run(pipeline_executor.execute_pipeline(
            config_name=schema_name,  # config_name parameter (backward compatible variable name)
            input_text=input_text,
            user_input=data.get('user_input', input_text)
        ))
        
        # Response formatieren
        if result.status.value == 'completed':
            return jsonify({
                'status': 'success',
                'schema': schema_name,
                'input_text': input_text,
                'final_output': result.final_output,
                'steps_completed': len(result.steps),
                'execution_time': result.execution_time,
                'metadata': result.metadata
            })
        else:
            return jsonify({
                'status': 'error',
                'schema': schema_name,
                'error': result.error,
                'steps_completed': len([s for s in result.steps if s.status.value == 'completed']),
                'total_steps': len(result.steps)
            }), 500
            
    except Exception as e:
        logger.error(f"Pipeline-Execution Fehler: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@schema_bp.route('/pipeline/test', methods=['POST'])  
def test_pipeline():
    """Test-Endpoint für direkte Prompt-Interception"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'error': 'JSON-Request erwartet'}), 400
        
        input_prompt = data.get('input_prompt')
        style_prompt = data.get('style_prompt', '')
        input_context = data.get('input_context', '')
        model = data.get('model', 'local/gemma2:9b')
        
        if not input_prompt:
            return jsonify({'status': 'error', 'error': 'Parameter "input_prompt" erforderlich'}), 400
        
        # Direkte Prompt-Interception (für Tests)
        from schemas.engine.prompt_interception_engine import PromptInterceptionRequest
        engine = PromptInterceptionEngine()
        
        request_obj = PromptInterceptionRequest(
            input_prompt=input_prompt,
            input_context=input_context,
            style_prompt=style_prompt,
            model=model,
            debug=data.get('debug', False)
        )
        
        response = asyncio.run(engine.process_request(request_obj))
        
        if response.success:
            return jsonify({
                'status': 'success',
                'input_prompt': input_prompt,
                'output_str': response.output_str,
                'model_used': response.model_used,
                'metadata': {
                    'output_float': response.output_float,
                    'output_int': response.output_int,
                    'output_binary': response.output_binary
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'error': response.error
            }), 500
            
    except Exception as e:
        logger.error(f"Test-Pipeline Fehler: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@schema_bp.route('/schemas', methods=['GET'])
def list_schemas():
    """Verfügbare Schemas auflisten"""
    try:
        init_schema_engine()
        
        schemas = []
        for schema_name in pipeline_executor.get_available_schemas():
            schema_info = pipeline_executor.get_schema_info(schema_name)
            if schema_info:
                schemas.append(schema_info)
        
        return jsonify({
            'status': 'success',
            'schemas': schemas
        })
        
    except Exception as e:
        logger.error(f"Schema-List Fehler: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
