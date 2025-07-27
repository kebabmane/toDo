from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, UserRole, PasswordResetToken
from decorators import token_required
import re
from logging_config import logger
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength.
    Requires at least 6 characters.
    """
    if len(password) < 6:
        return False
    return True

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    logger.info(f"Registration attempt from {request.remote_addr}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request content type: {request.content_type}")
    
    try:
        try:
            data = request.get_json(force=True)
            logger.debug(f"Parsed JSON data: {data}")
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        if not data:
            logger.warning("Empty JSON data received")
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Validate required fields
        missing_fields = [k for k in ('username', 'email', 'password') if k not in data]
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return jsonify({'error': 'Missing required fields: username, email, password'}), 400
        
        username = data['username'].strip().lower()
        email = data['email'].strip().lower()
        password = data['password']
        
        logger.info(f"Registration validation for username: {username}, email: {email}")
        
        # Validate input
        if not username or len(username) < 3:
            logger.warning(f"Invalid username length: {len(username)}")
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not validate_email(email):
            logger.warning(f"Invalid email format: {email}")
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(password):
            logger.warning(f"Invalid password length: {len(password)}")
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # If no users exist, make the first one an admin
        is_first_user = User.query.count() == 0
        logger.info(f"Is first user: {is_first_user}")
        
        # Check if user already exists
        if not is_first_user:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                logger.warning(f"Username already exists: {username}")
                return jsonify({'error': 'Username already exists'}), 409
            
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                logger.warning(f"Email already exists: {email}")
                return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        logger.info(f"Creating new user: {username}")
        user = User(username=username, email=email)
        user.set_password(password)
        
        if is_first_user:
            user.role = UserRole.ADMIN
            logger.info(f"Setting user {username} as admin (first user)")
        
        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"User {username} saved to database with ID: {user.id}")
        except Exception as e:
            logger.error(f"Database error while creating user: {e}")
            db.session.rollback()
            return jsonify({'error': 'Database error during registration'}), 500
        
        # Create access token
        try:
            access_token = create_access_token(identity=str(user.id))
            logger.info(f"Access token created for user {username}")
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            return jsonify({'error': 'Error creating access token'}), 500
        
        logger.info(f"User '{username}' registered successfully")
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected registration error: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({'error': 'Request body must be JSON'}), 400
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Validate required fields
        if not all(k in data for k in ('username', 'password')):
            return jsonify({'error': 'Missing required fields: username, password'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find user by username or email (case-insensitive)
        user = User.query.filter(
            (User.username == username.lower()) | (User.email == username.lower())
        ).first()
        
        # Verify user and password
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create access token with additional claims
        additional_claims = {'role': user.role.value}
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        
        logger.info(f"User '{username}' logged in successfully")
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login failed for user '{data.get('username', 'N/A')}': {e}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    return jsonify({'user': current_user.to_dict()}), 200

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request a password reset token"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
        
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Still return a success message to prevent email enumeration
        return jsonify({'message': 'If a user with that email exists, a password reset token has been sent.'}), 200
        
    # Generate a secure token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Store the token in the database
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.session.add(reset_token)
    db.session.commit()
    
    # In a real application, you would email this token to the user
    # For this example, we'll return it in the response
    return jsonify({
        'message': 'Password reset token generated successfully.',
        'reset_token': token
    }), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with a valid token"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400
        
    # Find the token in the database
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    # Check if the token is valid and not expired
    if not reset_token or reset_token.is_expired():
        return jsonify({'error': 'Invalid or expired token'}), 400
        
    user = reset_token.user
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Set the new password
    user.set_password(new_password)
    
    # Invalidate the token
    db.session.delete(reset_token)
    db.session.commit()
    
    return jsonify({'message': 'Password has been reset successfully.'}), 200
