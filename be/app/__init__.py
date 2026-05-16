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
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")


def create_app():
    """
    Application factory function.
    
    Creates and configures the Flask application with all necessary extensions,
    blueprints, and routes.
    
    Environment variables:
        - SECRET_KEY: Flask secret key for sessions
        - JWT_SECRET_KEY: Secret key for JWT token encoding/decoding
        - DATABASE_URL: PostgreSQL database connection string
        - UPLOAD_FOLDER: Directory for uploaded files (default: 'uploads')
        - MAX_CONTENT_LENGTH: Maximum upload size in bytes (default: 16MB)
        - POSTS_PER_PAGE: Number of posts per page (default: 10)
        
    Returns:
        Flask: Configured Flask application instance
        
    Raises:
        ValueError: If DATABASE_URL is not set
    """
    app = Flask(__name__)
    
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # Required environment variables
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or secret_key == 'change-this-secret-key':
        print("⚠️  WARNING: SECRET_KEY is not set or using default. Set a secure key in production!")
    app.config['SECRET_KEY'] = secret_key or 'dev-secret-key'

    jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret_key or jwt_secret_key == 'change-this-jwt-secret-key':
        print("⚠️  WARNING: JWT_SECRET_KEY is not set or using default. Set a secure key in production!")
    app.config['JWT_SECRET_KEY'] = jwt_secret_key or 'dev-jwt-secret-key'

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required. Please set it in your .env file.")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Optional environment variables with defaults
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    try:
        app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    except ValueError:
        print("⚠️  WARNING: MAX_CONTENT_LENGTH must be a valid integer. Using default (16MB).")
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    try:
        app.config['POSTS_PER_PAGE'] = int(os.getenv('POSTS_PER_PAGE', 10))
    except ValueError:
        print("⚠️  WARNING: POSTS_PER_PAGE must be a valid integer. Using default (10).")
        app.config['POSTS_PER_PAGE'] = 10

    os.makedirs(app.config['UPLOAD_FOLDER'], mode=0o755, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

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
         automatic_options=True,
         intercept_exceptions=False)

    socketio.init_app(app)

    from app.controllers import auth_controller as auth
    from app.controllers import campaigns_controller as campaigns
    from app.controllers import posts_controller as posts
    from app.controllers import invites_controller as invites
    from app.controllers import characters_controller as characters
    from app.controllers import export_controller as export
    from app.controllers import import_controller as import_ctrl
    from app.controllers import posts_viewed_status_controller as posts_viewed_status
    from app.controllers import notifications_controller as notifications
    from app.controllers import user_controller as user
    from app.events import socketio_events

    app.register_blueprint(auth.bp)
    app.register_blueprint(campaigns.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(invites.bp)
    app.register_blueprint(characters.bp)
    app.register_blueprint(export.bp)
    app.register_blueprint(import_ctrl.bp)
    app.register_blueprint(posts_viewed_status.bp)
    app.register_blueprint(notifications.bp)
    app.register_blueprint(user.bp)

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
