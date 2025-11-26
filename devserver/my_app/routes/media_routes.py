"""
Media Routes - Serving images, audio, video from LOCAL STORAGE
Unified Media Storage: All media served from exports/json/ regardless of backend

Migration Status (Session 37):
- Updated to use LivePipelineRecorder metadata format (entities array)
- No longer depends on MediaStorage
- Supports both numbered filenames (06_output_image.png) and legacy (output_image.png)
"""
from flask import Blueprint, send_file, jsonify
import logging
from pathlib import Path

from my_app.services.pipeline_recorder import load_recorder
from config import JSON_STORAGE_DIR

logger = logging.getLogger(__name__)

# Blueprint erstellen
media_bp = Blueprint('media', __name__, url_prefix='/api/media')


def _find_entity_by_type(entities: list, media_type: str) -> dict:
    """
    Find entity in entities array by media type.

    Args:
        entities: List of entity records from metadata
        media_type: Type to search for ('image', 'audio', 'video')

    Returns:
        Entity dict or None
    """
    # Search for output_TYPE entities (e.g., output_image, output_audio)
    for entity in entities:
        entity_type = entity.get('type', '')
        if entity_type == f'output_{media_type}':
            return entity

    # Fallback: Search for just the type (legacy compatibility)
    for entity in entities:
        if entity.get('type') == media_type:
            return entity

    return None


@media_bp.route('/image/<run_id>', methods=['GET'])
def get_image(run_id: str):
    """
    Serve image from local storage by run_id

    Args:
        run_id: UUID of the pipeline run

    Returns:
        Image file or 404 error
    """
    try:
        # Load recorder from disk
        recorder = load_recorder(run_id, base_path=JSON_STORAGE_DIR)
        if not recorder:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Find image entity
        image_entity = _find_entity_by_type(recorder.metadata.get('entities', []), 'image')
        if not image_entity:
            return jsonify({"error": f"No image found for run {run_id}"}), 404

        # Get file path
        filename = image_entity['filename']
        file_path = recorder.run_folder / filename
        if not file_path.exists():
            return jsonify({"error": f"Image file not found: {filename}"}), 404

        # Determine mimetype from format (from entity metadata or filename extension)
        file_format = image_entity.get('metadata', {}).get('format', filename.split('.')[-1])
        mimetype_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'gif': 'image/gif'
        }
        mimetype = mimetype_map.get(file_format.lower(), 'image/png')

        # Serve file directly from disk
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'{run_id}.{file_format}'
        )

    except Exception as e:
        logger.error(f"Error serving image for run {run_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@media_bp.route('/audio/<run_id>', methods=['GET'])
def get_audio(run_id: str):
    """
    Serve audio from local storage by run_id

    Args:
        run_id: UUID of the pipeline run

    Returns:
        Audio file or 404 error
    """
    try:
        # Load recorder from disk
        recorder = load_recorder(run_id, base_path=JSON_STORAGE_DIR)
        if not recorder:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Find audio entity (try both 'audio' and 'music' types)
        audio_entity = _find_entity_by_type(recorder.metadata.get('entities', []), 'audio')
        if not audio_entity:
            audio_entity = _find_entity_by_type(recorder.metadata.get('entities', []), 'music')

        if not audio_entity:
            return jsonify({"error": f"No audio found for run {run_id}"}), 404

        # Get file path
        filename = audio_entity['filename']
        file_path = recorder.run_folder / filename
        if not file_path.exists():
            return jsonify({"error": f"Audio file not found: {filename}"}), 404

        # Determine mimetype from format
        file_format = audio_entity.get('metadata', {}).get('format', filename.split('.')[-1])
        mimetype_map = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac'
        }
        mimetype = mimetype_map.get(file_format.lower(), 'audio/mpeg')

        # Serve file directly from disk
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'{run_id}.{file_format}'
        )

    except Exception as e:
        logger.error(f"Error serving audio for run {run_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@media_bp.route('/video/<run_id>', methods=['GET'])
def get_video(run_id: str):
    """
    Serve video from local storage by run_id

    Args:
        run_id: UUID of the pipeline run

    Returns:
        Video file or 404 error
    """
    try:
        # Load recorder from disk
        recorder = load_recorder(run_id, base_path=JSON_STORAGE_DIR)
        if not recorder:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Find video entity
        video_entity = _find_entity_by_type(recorder.metadata.get('entities', []), 'video')
        if not video_entity:
            return jsonify({"error": f"No video found for run {run_id}"}), 404

        # Get file path
        filename = video_entity['filename']
        file_path = recorder.run_folder / filename
        if not file_path.exists():
            return jsonify({"error": f"Video file not found: {filename}"}), 404

        # Determine mimetype from format
        file_format = video_entity.get('metadata', {}).get('format', filename.split('.')[-1])
        mimetype_map = {
            'mp4': 'video/mp4',
            'webm': 'video/webm',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime'
        }
        mimetype = mimetype_map.get(file_format.lower(), 'video/mp4')

        # Serve file directly from disk
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'{run_id}.{file_format}'
        )

    except Exception as e:
        logger.error(f"Error serving video for run {run_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@media_bp.route('/3d/<run_id>', methods=['GET'])
def get_3d(run_id: str):
    """
    Serve 3D model from local storage by run_id

    Args:
        run_id: UUID of the pipeline run

    Returns:
        3D model file or 404 error
    """
    try:
        # Load recorder from disk
        recorder = load_recorder(run_id, base_path=JSON_STORAGE_DIR)
        if not recorder:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Find 3D entity
        model_entity = _find_entity_by_type(recorder.metadata.get('entities', []), '3d')
        if not model_entity:
            return jsonify({"error": f"No 3D model found for run {run_id}"}), 404

        # Get file path
        filename = model_entity['filename']
        file_path = recorder.run_folder / filename
        if not file_path.exists():
            return jsonify({"error": f"3D model file not found: {filename}"}), 404

        # Determine mimetype from format
        file_format = model_entity.get('metadata', {}).get('format', filename.split('.')[-1])
        mimetype_map = {
            'gltf': 'model/gltf+json',
            'glb': 'model/gltf-binary',
            'obj': 'model/obj',
            'stl': 'model/stl',
            'fbx': 'application/octet-stream',
            'usd': 'model/vnd.usd+zip',
            'usdz': 'model/vnd.usdz+zip'
        }
        mimetype = mimetype_map.get(file_format.lower(), 'application/octet-stream')

        # Serve file directly from disk
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,  # 3D models should download
            download_name=f'{run_id}.{file_format}'
        )

    except Exception as e:
        logger.error(f"Error serving 3D model for run {run_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@media_bp.route('/info/<run_id>', methods=['GET'])
def get_media_info(run_id: str):
    """
    Get metadata about media for a run

    Args:
        run_id: UUID of the pipeline run

    Returns:
        JSON with media metadata
    """
    try:
        # Load recorder from disk
        recorder = load_recorder(run_id, base_path=JSON_STORAGE_DIR)
        if not recorder:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Build response
        media_info = {
            'run_id': run_id,
            'schema': recorder.metadata.get('config_name', 'unknown'),
            'execution_mode': recorder.metadata.get('execution_mode', 'unknown'),
            'timestamp': recorder.metadata.get('timestamp', ''),
            'outputs': []
        }

        # Add output entities (filter for output_* types)
        for entity in recorder.metadata.get('entities', []):
            entity_type = entity.get('type', '')
            if entity_type.startswith('output_'):
                entity_meta = entity.get('metadata', {})
                # Get file size from disk
                file_path = recorder.run_folder / entity['filename']
                file_size = file_path.stat().st_size if file_path.exists() else 0

                media_info['outputs'].append({
                    'type': entity_type.replace('output_', ''),  # output_image → image
                    'filename': entity['filename'],
                    'backend': entity_meta.get('backend', 'unknown'),
                    'config': entity_meta.get('config', ''),
                    'file_size_bytes': file_size,
                    'format': entity_meta.get('format', ''),
                    'width': entity_meta.get('width'),
                    'height': entity_meta.get('height'),
                    'duration_seconds': entity_meta.get('duration_seconds')
                })

        return jsonify(media_info)

    except Exception as e:
        logger.error(f"Error getting media info for run {run_id}: {e}")
        return jsonify({"error": str(e)}), 500


@media_bp.route('/run/<run_id>', methods=['GET'])
def get_run_metadata(run_id: str):
    """
    Get complete run metadata including input/output text and media

    Args:
        run_id: UUID of the pipeline run

    Returns:
        JSON with complete run metadata
    """
    try:
        # Load recorder from disk
        recorder = load_recorder(run_id, base_path=JSON_STORAGE_DIR)
        if not recorder:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Build response
        result = {
            'run_id': recorder.run_id,
            'user_id': recorder.metadata.get('user_id', 'anonymous'),
            'timestamp': recorder.metadata.get('timestamp', ''),
            'schema': recorder.metadata.get('config_name', 'unknown'),
            'execution_mode': recorder.metadata.get('execution_mode', 'unknown'),
            'current_state': recorder.metadata.get('current_state', {}),
            'expected_outputs': recorder.metadata.get('expected_outputs', []),
            'entities': recorder.metadata.get('entities', [])
        }

        # Add text content from entities if available
        for entity in result['entities']:
            if entity['type'] == 'input':
                input_file = recorder.run_folder / entity['filename']
                if input_file.exists():
                    result['input_text'] = input_file.read_text(encoding='utf-8')
            elif entity['type'] == 'interception':
                output_file = recorder.run_folder / entity['filename']
                if output_file.exists():
                    result['transformed_text'] = output_file.read_text(encoding='utf-8')

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting run metadata for {run_id}: {e}")
        return jsonify({"error": str(e)}), 500
