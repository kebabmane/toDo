import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, User, Todo, TodoList
from auth import auth_bp
from todos import todos_bp
from users import users_bp
from todolists import todolists_bp
from simple_todos import simple_todos_bp
from logging_config import logger

def create_app():
    """Create and configure the Flask application"""
    load_dotenv()
    app = Flask(__name__)
    
    # CORS configuration
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    
    # Database configuration - use instance folder for SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Disable CSRF protection for API usage
    app.config['JWT_CSRF_CHECK_FORM'] = False
    app.config['JWT_CSRF_IN_COOKIES'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize migrations directory
    basedir = os.path.abspath(os.path.dirname(__file__))
    migrate = Migrate(app, db, directory=os.path.join(basedir, 'migrations'))
    
    # Create tables and run migrations in app context
    with app.app_context():
        try:
            from flask_migrate import upgrade
            logger.info("Running database migrations...")
            upgrade()
            logger.info("Database migrations completed successfully")
        except Exception as e:
            logger.warning(f"Migration failed: {e}")
            logger.info("Creating tables directly...")
            try:
                db.create_all()
                logger.info("Tables created successfully")
            except Exception as create_error:
                logger.error(f"Failed to create tables: {create_error}")
                raise
        
    jwt = JWTManager(app)
    
    # Custom rate limit function that ignores OPTIONS requests
    def rate_limit_key():
        if request.method == 'OPTIONS':
            return None  # Don't rate limit OPTIONS requests
        return get_remote_address()
    
    limiter = Limiter(
        rate_limit_key,
        app=app,
        default_limits=["10000 per day", "1000 per hour", "100 per minute"],
        storage_uri="memory://",
    )
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(todos_bp)
    app.register_blueprint(simple_todos_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(todolists_bp)

    # Request logging middleware
    @app.before_request
    def log_request_info():
        logger.info(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request args: {dict(request.args)}")
        if request.content_type and 'application/json' in request.content_type:
            logger.debug(f"Request content type: {request.content_type}")
            if hasattr(request, 'data') and request.data:
                logger.debug(f"Request data length: {len(request.data)} bytes")

    @app.after_request
    def log_response_info(response):
        logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
        if response.status_code >= 400:
            logger.warning(f"Error response {response.status_code}: {response.get_data(as_text=True)[:200]}")
        return response
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is required'}), 401
    
    # Debug endpoint for frontend troubleshooting
    @app.route('/debug')
    def debug_endpoint():
        return jsonify({
            'status': 'debug_working',
            'message': 'Debug endpoint is functional',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    # Root endpoint
    @app.route('/')
    def health_check():
        return jsonify({
            'message': 'ToDo API is running',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'register': 'POST /auth/register',
                    'login': 'POST /auth/login',
                    'me': 'GET /auth/me'
                },
                'todos': {
                    'list': 'GET /todos',
                    'create': 'POST /todos',
                    'get': 'GET /todos/:id',
                    'update': 'PUT /todos/:id',
                    'delete': 'DELETE /todos/:id',
                    'stats': 'GET /todos/stats'
                },
                'todolists': {
                    'list': 'GET /todolists',
                    'create': 'POST /todolists',
                    'get': 'GET /todolists/:id',
                    'update': 'PUT /todolists/:id',
                    'delete': 'DELETE /todolists/:id',
                    'todos': {
                        'list': 'GET /todolists/:id/todos',
                        'create': 'POST /todolists/:id/todos',
                        'get': 'GET /todolists/:id/todos/:todoId',
                        'update': 'PUT /todolists/:id/todos/:todoId',
                        'delete': 'DELETE /todolists/:id/todos/:todoId'
                    }
                }
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment variable (for Docker)
    port = int(os.environ.get('PORT', 5001))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
