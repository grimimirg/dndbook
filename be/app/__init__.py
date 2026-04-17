from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    app.config['MOCK_DATA'] = os.getenv('MOCK_DATA', 'false').lower() == 'true'
    
    database_url = os.getenv('DATABASE_URL')
    if not app.config['MOCK_DATA'] and not database_url:
        raise ValueError("DATABASE_URL must be set when MOCK_DATA is false")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['POSTS_PER_PAGE'] = int(os.getenv('POSTS_PER_PAGE', 10))
    
    # Create upload folder with proper permissions
    os.makedirs(app.config['UPLOAD_FOLDER'], mode=0o755, exist_ok=True)
    
    if not app.config['MOCK_DATA']:
        db.init_app(app)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    socketio.init_app(app)
    
    from app.routes import auth, campaigns, posts, invites
    app.register_blueprint(auth.bp)
    app.register_blueprint(campaigns.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(invites.bp)
    
    return app
