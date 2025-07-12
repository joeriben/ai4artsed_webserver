"""
Flask application factory and initialization
"""
import logging
from flask import Flask
from flask_cors import CORS

from config import LOG_LEVEL, LOG_FORMAT, PUBLIC_DIR


def create_app():
    """
    Create and configure the Flask application
    
    Returns:
        Flask app instance
    """
    # Configure logging
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    
    # Create Flask app
    app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="")
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from my_app.routes.workflow_routes import workflow_bp
    from my_app.routes.workflow_streaming_routes import workflow_streaming_bp
    from my_app.routes.export_routes import export_bp
    from my_app.routes.static_routes import static_bp
    from my_app.routes.config_routes import config_bp
    
    app.register_blueprint(static_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(workflow_bp)
    app.register_blueprint(workflow_streaming_bp)
    app.register_blueprint(export_bp)
    
    # Configure logging filter for ComfyUI proxy
    class ComfyUIFilter(logging.Filter):
        def filter(self, record):
            # Suppress successful GET requests for the ComfyUI proxy to reduce log spam
            if "GET /comfyui/" in record.getMessage() and " 200 " in record.getMessage():
                return False
            return True
    
    log = logging.getLogger('werkzeug')
    log.addFilter(ComfyUIFilter())
    
    # Store pending exports in app context (in production, use a proper database)
    app.pending_exports = {}
    
    return app
