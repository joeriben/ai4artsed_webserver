"""
Flask application factory and initialization
"""
import logging
import os
from flask import Flask, request
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
    # static_url_path=None disables Flask's automatic static file serving
    # We handle static files manually in static_routes.py for SPA support
    app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path=None)
    
    # Configure session
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Enable CORS with session support
    CORS(app, supports_credentials=True)

    # CRITICAL: Prevent API response caching (Cloudflare + Browser)
    # Without this, Cloudflare Edge and Safari cache API responses permanently
    @app.after_request
    def add_no_cache_headers(response):
        """
        Add no-cache headers to all API responses to prevent caching issues

        Problem: Cloudflare Tunnel + Safari cache API responses despite "Development Mode"
        Solution: Explicit Cache-Control headers on all /api/* routes

        Why this is needed:
        - Cloudflare Edge caches responses even in dev mode
        - Safari aggressively caches GET requests
        - Hard reload only clears HTML/CSS/JS cache, not API cache
        - Cached 404 responses persist across reloads
        """
        # Only add headers to API routes (not static assets)
        if request.path.startswith('/api/') or request.path.startswith('/pipeline_configs_'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

        return response

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
    from my_app.routes.chat_routes import chat_bp  # Session 82: Chat overlay helper

    # Register API blueprints FIRST (before static catch-all)
    app.register_blueprint(config_bp)
    app.register_blueprint(workflow_streaming_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(sse_bp)
    app.register_blueprint(schema_bp)  # New API: /api/schema/*
    app.register_blueprint(schema_compat_bp)  # Backward compatibility: /list_workflows, /workflow_metadata
    app.register_blueprint(media_bp)
    app.register_blueprint(execution_bp)  # Pipeline run history API: /api/runs/*
    app.register_blueprint(pipeline_bp)  # NEW: LivePipelineRecorder API: /api/pipeline/*
    app.register_blueprint(chat_bp)  # Session 82: Chat overlay helper: /api/chat/*

    # Register static blueprint LAST (catch-all for SPA routing)
    app.register_blueprint(static_bp)
    
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
