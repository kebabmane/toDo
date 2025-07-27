from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, TodoList, Todo
from logging_config import logger

todolists_bp = Blueprint('todolists_bp', __name__)

@todolists_bp.route('/todolists', methods=['POST'])
@jwt_required()
def create_todolist():
    """Create a new todo list"""
    user_id = get_jwt_identity()
    logger.info(f"Creating todolist for user {user_id}")
    
    try:
        data = request.get_json(force=True)
        logger.debug(f"Todolist creation data: {data}")
    except Exception as e:
        logger.error(f"Failed to parse JSON for todolist creation: {e}")
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    name = data.get('name')

    if not name:
        logger.warning("Missing name field in todolist creation")
        return jsonify({'error': 'Name is required'}), 400

    try:
        new_list = TodoList(name=name, user_id=user_id)
        db.session.add(new_list)
        db.session.commit()
        logger.info(f"Todolist created successfully with ID: {new_list.id}")
        return jsonify(new_list.to_dict()), 201
    except Exception as e:
        logger.error(f"Database error creating todolist: {e}")
        db.session.rollback()
        return jsonify({'error': 'Database error creating todolist'}), 500

@todolists_bp.route('/todolists', methods=['GET'])
@jwt_required()
def get_todolists():
    """Get all todo lists for the current user"""
    user_id = get_jwt_identity()
    todolists = TodoList.query.filter_by(user_id=user_id).all()
    return jsonify([l.to_dict() for l in todolists]), 200

@todolists_bp.route('/todolists/<int:list_id>', methods=['GET'])
@jwt_required()
def get_todolist(list_id):
    """Get a specific todo list"""
    user_id = get_jwt_identity()
    todolist = TodoList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    return jsonify(todolist.to_dict()), 200

@todolists_bp.route('/todolists/<int:list_id>', methods=['PUT'])
@jwt_required()
def update_todolist(list_id):
    """Update a todo list's name"""
    user_id = get_jwt_identity()
    todolist = TodoList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    todolist.name = name
    db.session.commit()

    return jsonify(todolist.to_dict()), 200

@todolists_bp.route('/todolists/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_todolist(list_id):
    """Delete a todo list"""
    user_id = get_jwt_identity()
    todolist = TodoList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    
    db.session.delete(todolist)
    db.session.commit()

    return jsonify({'message': 'Todo list deleted'}), 200
