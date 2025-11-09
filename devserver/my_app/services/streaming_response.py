"""
Streaming response utilities to prevent Cloudflare timeouts
"""
import json
import time
import logging
from typing import Generator, Dict, Any
from flask import Response

logger = logging.getLogger(__name__)


def create_streaming_response(workflow_execution_func, *args, **kwargs) -> Response:
    """
    Create a streaming response that sends keep-alive messages to prevent timeouts
    
    Args:
        workflow_execution_func: The function to execute the workflow
        *args, **kwargs: Arguments to pass to the workflow function
        
    Returns:
        Flask Response object with streaming content
    """
    def generate():
        try:
            # Send initial status
            yield f"data: {json.dumps({'status': 'starting', 'message': 'Workflow wird gestartet...'})}\n\n"
            
            # Start workflow execution in background
            import threading
            result = {'done': False, 'data': None, 'error': None}
            
            def execute_workflow():
                try:
                    result['data'] = workflow_execution_func(*args, **kwargs)
                    result['done'] = True
                except Exception as e:
                    result['error'] = str(e)
                    result['done'] = True
            
            thread = threading.Thread(target=execute_workflow)
            thread.start()
            
            # Send keep-alive messages every 30 seconds
            start_time = time.time()
            message_count = 0
            
            while not result['done']:
                elapsed = time.time() - start_time
                message_count += 1
                
                # Send progress update
                yield f"data: {json.dumps({
                    'status': 'processing',
                    'message': f'Workflow läuft... ({int(elapsed)}s)',
                    'elapsed': elapsed,
                    'keepAlive': message_count
                })}\n\n"
                
                # Wait 30 seconds before next keep-alive
                for _ in range(30):
                    if result['done']:
                        break
                    time.sleep(1)
            
            # Send final result
            if result['error']:
                yield f"data: {json.dumps({
                    'status': 'error',
                    'error': result['error']
                })}\n\n"
            else:
                yield f"data: {json.dumps({
                    'status': 'completed',
                    'result': result['data']
                })}\n\n"
                
        except Exception as e:
            logger.error(f"Streaming response error: {e}")
            yield f"data: {json.dumps({
                'status': 'error',
                'error': str(e)
            })}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # Disable Nginx buffering
            'Access-Control-Allow-Origin': '*'
        }
    )


def create_polling_endpoint(check_status_func) -> Dict[str, Any]:
    """
    Create a fast polling endpoint that checks status without blocking
    
    Args:
        check_status_func: Function that checks the current status
        
    Returns:
        Status dictionary
    """
    try:
        status = check_status_func()
        return {
            'success': True,
            'status': status,
            'timestamp': time.time()
        }
    except Exception as e:
        logger.error(f"Polling error: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        }
