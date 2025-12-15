"""
Flask routes for static pages
"""
from flask import Blueprint, current_app, send_from_directory
import os

# Create blueprint
static_bp = Blueprint('static', __name__)


@static_bp.route('/')
def index():
    """Serve the main index.html page"""
    return current_app.send_static_file('index.html')


@static_bp.route('/lora')
@static_bp.route('/lora/')
def lora_home():
    """Serve the LoRA configuration interface."""
    return current_app.send_static_file('lora/index.html')


@static_bp.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from the public directory and its subdirectories"""
    # Security check to prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        return "Invalid path", 403
    
    # Check if file exists in static folder
    file_path = os.path.join(current_app.static_folder, filename)
    if os.path.isfile(file_path):
        return send_from_directory(current_app.static_folder, filename)
    
    # If not found, return 404
    return "File not found", 404
