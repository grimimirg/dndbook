"""Application factory and configuration module.

This module initializes the Flask application with all necessary extensions,
configuration, and blueprints for the D&D campaign book application.
"""

import os
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")


def create_app():
    """
    Application factory function.
    
    Creates and configures the Flask application with all necessary extensions,
    blueprints, and routes. Supports both mock data mode and database mode.
    
    Environment variables:
        - SECRET_KEY: Flask secret key for sessions
        - JWT_SECRET_KEY: Secret key for JWT token encoding/decoding
        - MOCK_DATA: Enable mock data mode (true/false)
        - DATABASE_URL: PostgreSQL database connection string
        - UPLOAD_FOLDER: Directory for uploaded files (default: 'uploads')
        - MAX_CONTENT_LENGTH: Maximum upload size in bytes (default: 16MB)
        - POSTS_PER_PAGE: Number of posts per page (default: 10)
        
    Returns:
        Flask: Configured Flask application instance
        
    Raises:
        ValueError: If DATABASE_URL is not set when MOCK_DATA is false
    """
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    app.config['MOCK_DATA'] = os.getenv('MOCK_DATA', 'false').lower() == 'true'

    database_url = os.getenv('DATABASE_URL')
    if not app.config['MOCK_DATA'] and not database_url:
        raise ValueError("DATABASE_URL must be set when MOCK_DATA is false")

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['POSTS_PER_PAGE'] = int(os.getenv('POSTS_PER_PAGE', 10))

    os.makedirs(app.config['UPLOAD_FOLDER'], mode=0o755, exist_ok=True)

    if not app.config['MOCK_DATA']:
        db.init_app(app)

    CORS(app,
         resources={
             r"/api/*": {
                 "origins": "*",
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": False,
                 "max_age": 3600
             },
             r"/uploads/*": {"origins": "*"}
         },
         automatic_options=True,  # Handle OPTIONS automatically
         intercept_exceptions=False)

    socketio.init_app(app)

    from app.controllers import auth_controller as auth
    from app.controllers import campaigns_controller as campaigns
    from app.controllers import posts_controller as posts
    from app.controllers import invites_controller as invites
    from app.controllers import characters_controller as characters
    from app.events import socketio_events

    app.register_blueprint(auth.bp)
    app.register_blueprint(campaigns.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(invites.bp)
    app.register_blueprint(characters.bp)

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """
        Serve uploaded files.
        
        Args:
            filename (str): Path to the file within the upload folder
            
        Returns:
            Response: File content with appropriate headers
        """
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app
