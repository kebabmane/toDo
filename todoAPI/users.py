from flask import Blueprint, jsonify, request
from models import db, User, UserRole
from decorators import role_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('', methods=['GET'])
@users_bp.route('/', methods=['GET'])
@role_required('admin')
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'role' in data:
        try:
            user.role = UserRole(data['role'])
        except ValueError:
            return jsonify({'message': 'Invalid role'}), 400
            
    if 'is_active' in data:
        user.is_active = data['is_active']
            
    db.session.commit()
    return jsonify(user.to_dict())

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

@users_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@role_required('admin')
def admin_reset_password(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'password' not in data:
        return jsonify({'message': 'Password is required'}), 400
        
    user.set_password(data['password'])
    db.session.commit()
    
    return jsonify({'message': 'Password has been reset successfully.'})
