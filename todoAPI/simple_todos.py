from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Todo
from logging_config import logger

simple_todos_bp = Blueprint('simple_todos', __name__, url_prefix='/todos')

@simple_todos_bp.route('', methods=['GET'])
@jwt_required()
def get_todos():
    """Get all todos for the current user"""
    try:
        user_id = get_jwt_identity()
        completed = request.args.get('completed')
        
        query = Todo.query.filter_by(user_id=user_id)
        
        if completed is not None:
            completed_bool = completed.lower() in ('true', '1', 'yes')
            query = query.filter_by(completed=completed_bool)
        
        todos = query.order_by(Todo.order.asc()).all()
        
        return jsonify({
            'todos': [todo.to_dict() for todo in todos],
            'count': len(todos)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get todos: {e}")
        return jsonify({'error': 'Failed to get todos', 'details': str(e)}), 500

@simple_todos_bp.route('', methods=['POST'])
@jwt_required()
def create_todo():
    """Create a new todo"""
    try:
        user_id = get_jwt_identity()
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        # Validate required fields
        if not title:
            return jsonify({'error': 'Title must be between 1 and 200 characters'}), 400
        
        if len(title) > 200:
            return jsonify({'error': 'Title must be between 1 and 200 characters'}), 400
        
        # Get the highest order for this user and increment
        max_order = db.session.query(db.func.max(Todo.order)).filter_by(user_id=user_id).scalar() or 0
        
        todo = Todo(
            user_id=user_id,
            title=title,
            description=description if description else None,
            order=max_order + 1
        )
        
        db.session.add(todo)
        db.session.commit()
        
        logger.info(f"Todo created successfully: {todo.id} for user {user_id}")
        return jsonify({
            'message': 'Todo created successfully',
            'todo': todo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create todo: {e}")
        return jsonify({'error': 'Failed to create todo', 'details': str(e)}), 500

@simple_todos_bp.route('/<int:todo_id>', methods=['GET'])
@jwt_required()
def get_todo(todo_id):
    """Get a specific todo"""
    try:
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        return jsonify({'todo': todo.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Failed to get todo {todo_id}: {e}")
        return jsonify({'error': 'Failed to get todo', 'details': str(e)}), 500

@simple_todos_bp.route('/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    """Update a specific todo"""
    try:
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Update fields if provided
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({'error': 'Title must be between 1 and 200 characters'}), 400
            if len(title) > 200:
                return jsonify({'error': 'Title must be between 1 and 200 characters'}), 400
            todo.title = title
        
        if 'description' in data:
            description = data['description']
            todo.description = description.strip() if description else None
        
        if 'completed' in data:
            if not isinstance(data['completed'], bool):
                return jsonify({'error': 'Completed field must be a boolean'}), 400
            todo.completed = data['completed']
        
        db.session.commit()
        
        logger.info(f"Todo updated successfully: {todo_id}")
        return jsonify({
            'message': 'Todo updated successfully',
            'todo': todo.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update todo {todo_id}: {e}")
        return jsonify({'error': 'Failed to update todo', 'details': str(e)}), 500

@simple_todos_bp.route('/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    """Delete a specific todo"""
    try:
        user_id = get_jwt_identity()
        todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        db.session.delete(todo)
        db.session.commit()
        
        logger.info(f"Todo deleted successfully: {todo_id}")
        return jsonify({'message': 'Todo deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete todo {todo_id}: {e}")
        return jsonify({'error': 'Failed to delete todo', 'details': str(e)}), 500

@simple_todos_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_todo_stats():
    """Get todo statistics for the current user"""
    try:
        user_id = get_jwt_identity()
        
        total_todos = Todo.query.filter_by(user_id=user_id).count()
        completed_todos = Todo.query.filter_by(user_id=user_id, completed=True).count()
        pending_todos = total_todos - completed_todos
        
        return jsonify({
            'stats': {
                'total': total_todos,
                'completed': completed_todos,
                'pending': pending_todos,
                'completion_rate': round((completed_todos / total_todos * 100), 2) if total_todos > 0 else 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get todo stats: {e}")
        return jsonify({'error': 'Failed to get todo stats', 'details': str(e)}), 500

@simple_todos_bp.route('/reorder', methods=['PUT'])
@jwt_required()
def reorder_todos():
    """Reorder todos"""
    try:
        user_id = get_jwt_identity()
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        if not data or 'ordered_ids' not in data:
            return jsonify({'error': 'ordered_ids is required'}), 400
        
        ordered_ids = data['ordered_ids']
        
        if not isinstance(ordered_ids, list):
            return jsonify({'error': 'ordered_ids must be a list'}), 400
        
        # Update the order of each todo
        for index, todo_id in enumerate(ordered_ids):
            todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
            if todo:
                todo.order = index
        
        db.session.commit()
        
        logger.info(f"Todos reordered successfully for user {user_id}")
        return jsonify({'message': 'Todos reordered successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to reorder todos: {e}")
        return jsonify({'error': 'Failed to reorder todos', 'details': str(e)}), 500