"""
Media Routes - Serving images, audio, video from LOCAL STORAGE
Unified Media Storage: All media served from media_storage/runs/ regardless of backend
"""
from flask import Blueprint, send_file, jsonify
import logging

from my_app.services.media_storage import get_media_storage_service

logger = logging.getLogger(__name__)

# Blueprint erstellen
media_bp = Blueprint('media', __name__, url_prefix='/api/media')

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
        media_storage = get_media_storage_service()

        # Get run metadata
        metadata = media_storage.get_metadata(run_id)
        if not metadata:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Find image output
        image_output = None
        for output in metadata.outputs:
            if output.type == 'image':
                image_output = output
                break

        if not image_output:
            return jsonify({"error": f"No image found for run {run_id}"}), 404

        # Get file path
        file_path = media_storage.get_media_path(run_id, image_output.filename)
        if not file_path or not file_path.exists():
            return jsonify({"error": f"Image file not found: {image_output.filename}"}), 404

        # Determine mimetype from format
        mimetype_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'gif': 'image/gif'
        }
        mimetype = mimetype_map.get(image_output.format, 'image/png')

        # Serve file directly from disk
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'{run_id}.{image_output.format}'
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
        media_storage = get_media_storage_service()

        # Get run metadata
        metadata = media_storage.get_metadata(run_id)
        if not metadata:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Find audio/music output
        audio_output = None
        for output in metadata.outputs:
            if output.type in ['audio', 'music']:
                audio_output = output
                break

        if not audio_output:
            return jsonify({"error": f"No audio found for run {run_id}"}), 404

        # Get file path
        file_path = media_storage.get_media_path(run_id, audio_output.filename)
        if not file_path or not file_path.exists():
            return jsonify({"error": f"Audio file not found: {audio_output.filename}"}), 404

        # Determine mimetype from format
        mimetype_map = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac'
        }
        mimetype = mimetype_map.get(audio_output.format, 'audio/mpeg')

        # Serve file directly from disk
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'{run_id}.{audio_output.format}'
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
        media_storage = get_media_storage_service()

        # Get run metadata
        metadata = media_storage.get_metadata(run_id)
        if not metadata:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Find video output
        video_output = None
        for output in metadata.outputs:
            if output.type == 'video':
                video_output = output
                break

        if not video_output:
            return jsonify({"error": f"No video found for run {run_id}"}), 404

        # Get file path
        file_path = media_storage.get_media_path(run_id, video_output.filename)
        if not file_path or not file_path.exists():
            return jsonify({"error": f"Video file not found: {video_output.filename}"}), 404

        # Determine mimetype from format
        mimetype_map = {
            'mp4': 'video/mp4',
            'webm': 'video/webm',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime'
        }
        mimetype = mimetype_map.get(video_output.format, 'video/mp4')

        # Serve file directly from disk
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'{run_id}.{video_output.format}'
        )

    except Exception as e:
        logger.error(f"Error serving video for run {run_id}: {e}")
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
        media_storage = get_media_storage_service()

        # Get run metadata
        metadata = media_storage.get_metadata(run_id)
        if not metadata:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Build response
        media_info = {
            'run_id': run_id,
            'schema': metadata.schema,
            'execution_mode': metadata.execution_mode,
            'timestamp': metadata.timestamp,
            'outputs': []
        }

        # Add output details
        for output in metadata.outputs:
            media_info['outputs'].append({
                'type': output.type,
                'filename': output.filename,
                'backend': output.backend,
                'config': output.config,
                'file_size_bytes': output.file_size_bytes,
                'format': output.format,
                'width': output.width,
                'height': output.height,
                'duration_seconds': output.duration_seconds
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
        media_storage = get_media_storage_service()

        # Get run metadata
        metadata = media_storage.get_metadata(run_id)
        if not metadata:
            return jsonify({"error": f"Run {run_id} not found"}), 404

        # Convert to dict (manually to handle dataclass properly)
        result = {
            'run_id': metadata.run_id,
            'user_id': metadata.user_id,
            'timestamp': metadata.timestamp,
            'schema': metadata.schema,
            'execution_mode': metadata.execution_mode,
            'input_text': metadata.input_text,
            'transformed_text': metadata.transformed_text,
            'outputs': [
                {
                    'type': output.type,
                    'filename': output.filename,
                    'backend': output.backend,
                    'config': output.config,
                    'file_size_bytes': output.file_size_bytes,
                    'format': output.format,
                    'width': output.width,
                    'height': output.height,
                    'duration_seconds': output.duration_seconds
                }
                for output in metadata.outputs
            ]
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error getting run metadata for {run_id}: {e}")
        return jsonify({"error": str(e)}), 500
