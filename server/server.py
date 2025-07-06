#!/usr/bin/env python3
"""
AI4ArtsEd Web Server - Main Entry Point

This is the main entry point for the AI4ArtsEd web server.
It uses the Flask application factory pattern with a modular structure.
"""

from waitress import serve
from my_app import create_app
from config import HOST, PORT, THREADS


def main():
    """Main entry point for the server"""
    # Create Flask app
    app = create_app()
    
    # Run the server with Waitress
    print(f"Starting AI4ArtsEd Web Server with Waitress on http://{HOST}:{PORT}")
    print(f"Using {THREADS} threads")
    print("Press Ctrl+C to stop the server")
    
    serve(
        app,
        host=HOST,
        port=PORT,
        threads=THREADS,
        url_scheme='http'
    )


if __name__ == "__main__":
    main()
