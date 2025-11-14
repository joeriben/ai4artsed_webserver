"""
Flask routes for serving Vue.js SPA (Single Page Application)

This module handles:
1. Static assets (*.js, *.css, images) with explicit MIME types
2. Vue Router's HTML5 history mode (serving index.html for all non-file routes)
3. API route passthrough (handled by other blueprints)

Architecture:
- Production builds are served from dist/ folder (config.PUBLIC_DIR)
- ES modules require explicit MIME type setting for browser compatibility
- SPA routing requires serving index.html for all non-asset paths
"""
from flask import Blueprint, current_app, send_from_directory
import os
import mimetypes

# Create blueprint
static_bp = Blueprint('static', __name__)


@static_bp.route('/', defaults={'path': ''})
@static_bp.route('/<path:path>')
def serve_spa(path):
    """
    Serve Vue.js SPA with proper routing and MIME types

    Handles three cases:
    1. Static assets (assets/*.js, assets/*.css, favicon.ico) → serve with explicit MIME type
    2. API routes (start with 'api/' or specific endpoints) → pass through to other blueprints
    3. All other paths (Vue routes like /select, /execute/:id) → serve index.html

    Args:
        path: Request path (empty string for root)

    Returns:
        Flask response with correct MIME type or index.html for SPA routing
    """
    # Security check to prevent directory traversal attacks
    if '..' in path or path.startswith('/'):
        return "Invalid path", 403

    # Case 1: API routes - these are handled by other blueprints
    # This route is evaluated AFTER all specific blueprints, so API routes
    # will never reach here. This comment documents the expected behavior.
    # API patterns: /api/*, /pipeline_configs_*, /comfyui/*, etc.

    # Case 2: Static assets - serve with explicit MIME type
    # Critical for ES modules (.js files) which must have correct Content-Type
    # PWA files: registerSW.js, sw.js, workbox-*.js, manifest.webmanifest, icons
    if (path.startswith('assets/') or
        path.startswith('workbox-') or
        path in ['favicon.ico', 'robots.txt', 'registerSW.js', 'sw.js',
                 'manifest.webmanifest', 'icon-192x192.png', 'icon-512x512.png',
                 'apple-touch-icon.png']):
        file_path = os.path.join(current_app.static_folder, path)
        if os.path.isfile(file_path):
            # Explicit MIME type setting (critical for ES modules)
            # Python's mimetypes.guess_type() returns (type, encoding)
            mime_type = mimetypes.guess_type(path)[0]

            # Fallback MIME types for common extensions if guess_type fails
            if mime_type is None:
                if path.endswith('.js'):
                    mime_type = 'application/javascript'
                elif path.endswith('.css'):
                    mime_type = 'text/css'
                elif path.endswith('.json'):
                    mime_type = 'application/json'
                elif path.endswith('.webmanifest'):
                    mime_type = 'application/manifest+json'
                elif path.endswith('.png'):
                    mime_type = 'image/png'
                elif path.endswith('.jpg') or path.endswith('.jpeg'):
                    mime_type = 'image/jpeg'
                elif path.endswith('.svg'):
                    mime_type = 'image/svg+xml'
                elif path.endswith('.ico'):
                    mime_type = 'image/x-icon'

            # Serve the file with explicit MIME type and cache headers
            # Assets have content hashes in filename (e.g., index-Bprq4S1F.js)
            # so they can be cached aggressively - new builds get new filenames
            response = send_from_directory(
                current_app.static_folder,
                path,
                mimetype=mime_type
            )

            # Set aggressive caching for hashed assets (overwrite Flask's default)
            if path.startswith('assets/') or path.startswith('workbox-'):
                # Cache for 1 year (immutable assets with content hash)
                # New builds generate new filenames, so old cached files become unused automatically
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            elif path in ['sw.js', 'registerSW.js']:
                # Service Worker files must NOT be cached (critical for updates)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            else:
                # Shorter cache for other static files (favicon, icons, manifest)
                response.headers['Cache-Control'] = 'public, max-age=3600'

            return response

        # Asset file not found - return 404
        return "File not found", 404

    # Case 3: All other paths - serve index.html (SPA routing)
    # This includes:
    # - / (root)
    # - /select (property selection view)
    # - /execute/:configId (pipeline execution view)
    # - /about (about view)
    # Vue Router handles client-side routing after index.html loads

    # Important: index.html should NOT be cached aggressively
    # because it contains references to hashed assets that change with each build
    response = current_app.send_static_file('index.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
