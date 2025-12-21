"""
Flask application factory and initialization
"""
import logging
import os
from flask import Flask, request
from flask_cors import CORS

from config import LOG_LEVEL, LOG_FORMAT, PUBLIC_DIR, DISABLE_API_CACHE, CACHE_STRATEGY


def _load_user_settings():
    """Load user settings from user_settings.json and override config.py defaults"""
    try:
        import json
        from pathlib import Path
        import config

        settings_file = Path(__file__).parent.parent / "user_settings.json"

        if not settings_file.exists():
            logging.info("[CONFIG] No user_settings.json found, using defaults")
            return

        with open(settings_file) as f:
            data = json.load(f)

        if not data:
            logging.info("[CONFIG] user_settings.json is empty, using defaults")
            return

        logging.info(f"[CONFIG] Loading user settings from {settings_file.name}")

        # Override config values
        count = 0
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
                count += 1
            else:
                logging.warning(f"[CONFIG] Unknown setting '{key}' ignored")

        logging.info(f"[CONFIG] {count} user settings applied successfully")

    except Exception as e:
        logging.error(f"[CONFIG] Error loading user settings: {e}")


def create_app():
    """
    Create and configure the Flask application

    Returns:
        Flask app instance
    """
    # Configure logging
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

    # Load user settings BEFORE creating app
    _load_user_settings()
    
    # Create Flask app
    # static_url_path=None disables Flask's automatic static file serving
    # We handle static files manually in static_routes.py for SPA support
    app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path=None)
    
    # Configure session
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Production (PORT=17801) uses HTTPS via Cloudflare → Secure cookies required
    # Development (PORT=17802) uses HTTP → Secure=False
    is_production = os.environ.get('PORT') == '17801'
    app.config['SESSION_COOKIE_SECURE'] = is_production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

    # Enable CORS with session support
    # Must explicitly set origins when using credentials (cannot use wildcard)
    CORS(app,
         supports_credentials=True,
         origins=['http://localhost:17802', 'http://127.0.0.1:17802', 'http://localhost:5173', 'https://lab.ai4artsed.org'],
         allow_headers=['Content-Type'],
         expose_headers=['Set-Cookie'])

    # Environment-based API caching strategy
    @app.after_request
    def add_cache_headers(response):
        """
        Add cache headers to API responses based on environment

        Development (DISABLE_API_CACHE=true):
        - Aggressive no-cache headers to prevent stale data during development
        - Fixes: Cloudflare Edge + Safari caching issues

        Production (DISABLE_API_CACHE=false):
        - Intelligent caching for GET requests (configs/models: 5min)
        - POST/SSE requests are never cached (browser default)
        - Reduces server load and improves performance
        """
        # Only add headers to API routes (not static assets)
        if request.path.startswith('/api/') or request.path.startswith('/pipeline_configs_'):
            if DISABLE_API_CACHE:
                # Development: Disable all caching
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            else:
                # Production: Enable intelligent caching for GET requests
                for route_prefix, cache_header in CACHE_STRATEGY.items():
                    if request.path.startswith(route_prefix):
                        response.headers['Cache-Control'] = cache_header
                        break
                # If no cache strategy matched, don't add headers (browser default)

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
    from my_app.routes.settings_routes import settings_bp  # Settings configuration API
    from my_app.routes.text_stream_routes import text_stream_bp  # Text streaming for typewriter effect

    # Register API blueprints FIRST (before static catch-all)
    app.register_blueprint(config_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(workflow_streaming_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(sse_bp)
    app.register_blueprint(schema_bp)  # New API: /api/schema/*
    app.register_blueprint(schema_compat_bp)  # Backward compatibility: /list_workflows, /workflow_metadata
    app.register_blueprint(media_bp)
    app.register_blueprint(execution_bp)  # Pipeline run history API: /api/runs/*
    app.register_blueprint(pipeline_bp)  # NEW: LivePipelineRecorder API: /api/pipeline/*
    app.register_blueprint(chat_bp)  # Session 82: Chat overlay helper: /api/chat/*
    app.register_blueprint(text_stream_bp)  # Text streaming: /api/text_stream/*

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
