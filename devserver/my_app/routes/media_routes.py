"""
Media Routes - Serving images, audio, video from ComfyUI/other generators
Clean separation: Only media serving, no business logic
"""
from flask import Blueprint, send_file, jsonify
from io import BytesIO
import logging
import asyncio

logger = logging.getLogger(__name__)

# Blueprint erstellen
media_bp = Blueprint('media', __name__, url_prefix='/api/media')

@media_bp.route('/image/<prompt_id>', methods=['GET'])
def get_image(prompt_id: str):
    """
    Bild von ComfyUI abrufen
    
    Args:
        prompt_id: ComfyUI Prompt ID
        
    Returns:
        Image file or 404 error
    """
    try:
        from my_app.services.comfyui_client import get_comfyui_client
        
        # Async wrapper für sync Route
        async def fetch_image():
            client = get_comfyui_client()
            
            # History abrufen
            history = await client.get_history(prompt_id)
            if not history or prompt_id not in history:
                return None, "Image not found or not ready"
            
            # Generierte Bilder extrahieren
            images = await client.get_generated_images(history[prompt_id])
            if not images:
                return None, "No images found in history"
            
            # Erstes Bild holen
            first_image = images[0]
            image_data = await client.get_image(
                filename=first_image['filename'],
                subfolder=first_image.get('subfolder', ''),
                folder_type=first_image.get('type', 'output')
            )
            
            return image_data, None
        
        # Asyncio run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            image_data, error = loop.run_until_complete(fetch_image())
        finally:
            loop.close()
        
        if error:
            return jsonify({"error": error}), 404
        
        if not image_data:
            return jsonify({"error": "Failed to download image"}), 500
        
        # Als PNG zurückgeben
        return send_file(
            BytesIO(image_data),
            mimetype='image/png',
            as_attachment=False,
            download_name=f'{prompt_id}.png'
        )
        
    except Exception as e:
        logger.error(f"Error fetching image {prompt_id}: {e}")
        return jsonify({"error": str(e)}), 500


@media_bp.route('/audio/<prompt_id>', methods=['GET'])
def get_audio(prompt_id: str):
    """
    Audio von Generator abrufen (zukünftig: Stable Audio, etc.)
    
    Args:
        prompt_id: Generator Prompt ID
        
    Returns:
        Audio file or 404 error
    """
    # Placeholder für Audio-Support
    return jsonify({"error": "Audio support coming soon"}), 501


@media_bp.route('/video/<prompt_id>', methods=['GET'])
def get_video(prompt_id: str):
    """
    Video von Generator abrufen (zukünftig: AnimateDiff, etc.)
    
    Args:
        prompt_id: Generator Prompt ID
        
    Returns:
        Video file or 404 error
    """
    # Placeholder für Video-Support
    return jsonify({"error": "Video support coming soon"}), 501


@media_bp.route('/info/<prompt_id>', methods=['GET'])
def get_media_info(prompt_id: str):
    """
    Media-Metadaten abrufen
    
    Args:
        prompt_id: Generator Prompt ID
        
    Returns:
        JSON with media metadata
    """
    try:
        from my_app.services.comfyui_client import get_comfyui_client
        
        async def fetch_info():
            client = get_comfyui_client()
            history = await client.get_history(prompt_id)
            
            if not history or prompt_id not in history:
                return None
            
            images = await client.get_generated_images(history[prompt_id])
            
            if images:
                return {
                    "type": "image",
                    "count": len(images),
                    "files": images,
                    "prompt_id": prompt_id
                }
            
            return None
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            info = loop.run_until_complete(fetch_info())
        finally:
            loop.close()
        
        if info:
            return jsonify(info)
        else:
            return jsonify({"error": "Media info not found"}), 404
            
    except Exception as e:
        logger.error(f"Error fetching media info {prompt_id}: {e}")
        return jsonify({"error": str(e)}), 500
