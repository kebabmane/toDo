from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User

def token_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = get_jwt_identity()
        current_user = User.query.filter_by(id=user_id).first()
        if not current_user:
            return jsonify({"message": "User not found!"}), 404
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            current_user = User.query.filter_by(id=user_id).first()
            if not current_user or current_user.role.value != role:
                return jsonify({"error": "Admins only!"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
