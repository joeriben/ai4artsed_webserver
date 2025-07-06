"""
Flask routes for export operations
"""
import logging
from flask import Blueprint, jsonify, request, send_file
from datetime import datetime

from my_app.services.export_manager import export_manager
from my_app.utils.helpers import generate_timestamp

logger = logging.getLogger(__name__)

# Create blueprint
export_bp = Blueprint('export', __name__)


@export_bp.route('/api/export-session', methods=['POST'])
def export_session():
    """Export a completed session"""
    try:
        data = request.json
        prompt_id = data.get('prompt_id')
        user_id = data.get('user_id', 'DOE_J')
        workflow_name = data.get('workflow_name', 'Unknown Workflow')
        prompt_text = data.get('prompt', '')
        
        if not prompt_id:
            return jsonify({"error": "Keine Prompt-ID angegeben."}), 400
        
        logger.info(f"Exporting session {prompt_id} for user {user_id}")
        
        # Export session
        result = export_manager.export_session(
            prompt_id=prompt_id,
            user_id=user_id,
            workflow_name=workflow_name,
            prompt_text=prompt_text
        )
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error exporting session: {e}")
        return jsonify({"error": "Export fehlgeschlagen"}), 500


@export_bp.route('/api/download-session', methods=['POST'])
def download_session():
    """Download a session as ZIP file"""
    try:
        data = request.json
        prompt_id = data.get('prompt_id')
        user_id = data.get('user_id', 'DOE_J')
        workflow_name = data.get('workflow_name', 'Unknown Workflow')
        prompt_text = data.get('prompt', '')
        
        if not prompt_id:
            return jsonify({"error": "Keine Prompt-ID angegeben."}), 400
        
        logger.info(f"Creating download for session {prompt_id}")
        
        # Create ZIP file
        zip_data = export_manager.create_download_zip(
            prompt_id=prompt_id,
            user_id=user_id,
            workflow_name=workflow_name,
            prompt_text=prompt_text
        )
        
        if not zip_data:
            return jsonify({"error": "Download-Erstellung fehlgeschlagen"}), 500
        
        # Generate filename
        timestamp = generate_timestamp()
        session_id = prompt_id[:8]
        filename = f"ai4artsed_export_{user_id}_{timestamp}_{session_id}.zip"
        
        # Send file
        return send_file(
            io.BytesIO(zip_data),
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error creating download: {e}")
        return jsonify({"error": "Download fehlgeschlagen"}), 500


# Import required for send_file
import io
