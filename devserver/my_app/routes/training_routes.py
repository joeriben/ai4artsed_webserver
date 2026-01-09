import time
import json
import traceback
from typing import List
from flask import Blueprint, request, jsonify, Response, stream_with_context
from my_app.services.training_service import training_service

# Define Blueprint
training_bp = Blueprint('training', __name__)

@training_bp.route('/api/training/start', methods=['POST'])
def start_training():
    try:
        project_name = request.form.get('project_name')
        trigger_word = request.form.get('trigger_word', '')
        
        if not project_name:
            return jsonify({"message": "project_name is required"}), 400
            
        if 'images' not in request.files:
            return jsonify({"message": "No images provided"}), 400
            
        uploaded_files = request.files.getlist('images')
        
        class FileWrapper:
            def __init__(self, storage):
                self.filename = storage.filename
                self.file = storage.stream

        wrapped_images = [FileWrapper(f) for f in uploaded_files]

        result = training_service.create_project(project_name, wrapped_images, trigger_word)
        
        success = training_service.start_training_process(project_name)
        
        if not success:
            return jsonify({"message": "Training could not be started (already running?)"}), 400
            
        return jsonify({"message": "Training started", "details": result})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": str(e)}), 500

@training_bp.route('/api/training/stop', methods=['POST'])
def stop_training():
    success = training_service.stop_training()
    return jsonify({"message": "Training stopped", "success": success})

@training_bp.route('/api/training/delete', methods=['POST'])
def delete_project():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"message": "Invalid JSON"}), 400
            
        project_name = data.get('project_name')
        if not project_name:
            return jsonify({"message": "Project name required"}), 400
            
        success = training_service.delete_project_files(project_name)
        if success:
            return jsonify({"message": "Project files deleted successfully"})
        else:
            return jsonify({"message": "Could not delete files (training in progress?)"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@training_bp.route('/api/training/status', methods=['GET'])
def get_training_status():
    return jsonify(training_service.get_status())

@training_bp.route('/api/training/events')
def training_events():
    def event_stream():
        last_log_index = 0
        while True:
            status = training_service.get_status()
            
            # Check for new logs
            logs = status["log_lines"]
            if len(logs) > last_log_index:
                new_lines = logs[last_log_index:]
                last_log_index = len(logs)
                
                # Send log batch
                yield f"event: log\ndata: {json.dumps(new_lines)}\n\n"
            
            # Send status update
            yield f"event: status\ndata: {json.dumps({'is_training': status['is_training'], 'error': status['error']})}\n\n"
            
            if not status["is_training"] and len(logs) == last_log_index:
                yield f"event: done\ndata: {json.dumps({'message': 'Training finished'})}\n\n"
                break
                
            time.sleep(1)

    return Response(stream_with_context(event_stream()), content_type='text/event-stream')