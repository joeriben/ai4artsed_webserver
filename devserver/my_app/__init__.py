"""
Flask application factory and initialization
"""
import logging
import os
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
    
    # Configure session
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Enable CORS with session support
    CORS(app, supports_credentials=True)
    
    # Register blueprints
    from my_app.routes.workflow_streaming_routes import workflow_streaming_bp
    from my_app.routes.export_routes import export_bp
    from my_app.routes.static_routes import static_bp
    from my_app.routes.config_routes import config_bp
    from my_app.routes.sse_routes import sse_bp
    from my_app.routes.schema_pipeline_routes import schema_bp, schema_compat_bp
    from my_app.routes.media_routes import media_bp
    from my_app.routes.execution_routes import execution_bp
    from my_app.routes.pipeline_routes import pipeline_bp  # NEW: LivePipelineRecorder API

    app.register_blueprint(static_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(workflow_streaming_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(sse_bp)
    app.register_blueprint(schema_bp)  # New API: /api/schema/*
    app.register_blueprint(schema_compat_bp)  # Backward compatibility: /list_workflows, /workflow_metadata
    app.register_blueprint(media_bp)
    app.register_blueprint(execution_bp)  # Pipeline run history API: /api/runs/*
    app.register_blueprint(pipeline_bp)  # NEW: LivePipelineRecorder API: /api/pipeline/*
    
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
