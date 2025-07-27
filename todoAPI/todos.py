from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import db, Todo, TodoList
from logging_config import logger

todos_bp = Blueprint('todos', __name__, url_prefix='/todolists/<int:list_id>/todos')

@todos_bp.before_request
def before_request():
    """Check if the user owns the todolist before every request"""
    if request.method == 'OPTIONS':
        return

    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        list_id = request.view_args.get('list_id')
        
        if list_id:
            logger.debug(f"Checking access to list {list_id} for user {user_id}")
            todolist = TodoList.query.filter_by(id=list_id, user_id=user_id).first()
            if not todolist:
                logger.warning(f"User {user_id} tried to access non-existent or unauthorized list {list_id}")
                return jsonify({'error': 'TodoList not found or you do not have permission to access it'}), 404
            logger.debug(f"Access granted to list {list_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Authorization failed for todos endpoint: {e}")
        return jsonify({'error': 'Authorization failed', 'details': str(e)}), 401

@todos_bp.route('', methods=['GET'])
def get_todos(list_id):
    """Get all todos for a specific list"""
    user_id = get_jwt_identity()
    logger.info(f"Getting todos for list {list_id} for user {user_id}")
    
    try:
        completed = request.args.get('completed')
        logger.debug(f"Completed filter: {completed}")
        
        query = Todo.query.filter_by(todo_list_id=list_id)
        
        if completed is not None:
            completed_bool = completed.lower() in ('true', '1', 'yes')
            query = query.filter_by(completed=completed_bool)
            logger.debug(f"Filtering by completed: {completed_bool}")
        
        todos = query.order_by(Todo.order.asc()).all()
        logger.info(f"Found {len(todos)} todos in list {list_id}")
        
        return jsonify({
            'todos': [todo.to_dict() for todo in todos],
            'count': len(todos)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get todos for list {list_id}: {e}")
        return jsonify({'error': 'Failed to get todos', 'details': str(e)}), 500

@todos_bp.route('', methods=['POST'])
def create_todo(list_id):
    """Create a new todo in a specific list"""
    user_id = get_jwt_identity()
    logger.info(f"Creating todo in list {list_id} for user {user_id}")
    
    try:
        try:
            data = request.get_json(force=True)
            logger.debug(f"Parsed todo data: {data}")
        except Exception as e:
            logger.error(f"Failed to parse JSON for todo creation: {e}")
            return jsonify({'error': 'Request body must be JSON'}), 400
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        if 'title' not in data:
            logger.warning("Missing title field in todo creation request")
            return jsonify({'error': 'Missing required field: title'}), 400
        
        title = data['title'].strip()
        description = data.get('description', '').strip() if data.get('description') else None
        
        logger.debug(f"Creating todo with title: '{title}', description: '{description}'")
        
        if not title or len(title) > 200:
            logger.warning(f"Invalid title length: {len(title)}")
            return jsonify({'error': 'Title must be between 1 and 200 characters'}), 400
        
        max_order = db.session.query(db.func.max(Todo.order)).filter_by(todo_list_id=list_id).scalar() or 0
        logger.debug(f"Max order for list {list_id}: {max_order}")
        
        todo = Todo(
            user_id=user_id,  # Add required user_id field
            todo_list_id=list_id,
            title=title,
            description=description,
            completed=False,
            order=max_order + 1
        )
        
        try:
            db.session.add(todo)
            db.session.commit()
            logger.info(f"Todo created successfully with ID: {todo.id}")
        except Exception as e:
            logger.error(f"Database error creating todo: {e}")
            db.session.rollback()
            return jsonify({'error': 'Database error creating todo'}), 500
        
        logger.info(f"Todo {todo.id} created for list {list_id}")
        return jsonify({
            'message': 'Todo created successfully',
            'todo': todo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create todo for list {list_id}: {e}")
        return jsonify({'error': 'Failed to create todo', 'details': str(e)}), 500

@todos_bp.route('/<int:todo_id>', methods=['GET'])
def get_todo(list_id, todo_id):
    """Get a specific todo from a list"""
    try:
        todo = Todo.query.filter_by(id=todo_id, todo_list_id=list_id).first()
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        return jsonify({'todo': todo.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Failed to get todo {todo_id} for list {list_id}: {e}")
        return jsonify({'error': 'Failed to get todo', 'details': str(e)}), 500

@todos_bp.route('/<int:todo_id>', methods=['PUT'])
def update_todo(list_id, todo_id):
    """Update a specific todo in a list"""
    user_id = get_jwt_identity()
    logger.info(f"Updating todo {todo_id} in list {list_id} for user {user_id}")
    
    try:
        try:
            data = request.get_json(force=True)
            logger.debug(f"Update data: {data}")
        except Exception as e:
            logger.error(f"Failed to parse JSON for todo update: {e}")
            return jsonify({'error': 'Request body must be JSON'}), 400
            
        if not data:
            logger.warning("Empty update data received")
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        todo = Todo.query.filter_by(id=todo_id, todo_list_id=list_id).first()
        
        if not todo:
            logger.warning(f"Todo {todo_id} not found in list {list_id}")
            return jsonify({'error': 'Todo not found'}), 404
            
        logger.debug(f"Found todo: {todo.title} (completed: {todo.completed})")
        
        if 'title' in data:
            title = data['title'].strip()
            if not title or len(title) > 200:
                return jsonify({'error': 'Title must be between 1 and 200 characters'}), 400
            todo.title = title
        
        if 'description' in data:
            description = data['description'].strip() if data['description'] else None
            todo.description = description
        
        if 'completed' in data:
            if not isinstance(data['completed'], bool):
                logger.warning(f"Invalid completed value type: {type(data['completed'])}")
                return jsonify({'error': 'Completed field must be a boolean'}), 400
            
            was_completed = todo.completed
            todo.completed = data['completed']
            logger.info(f"Updating todo completion: {was_completed} -> {todo.completed}")

            if not was_completed and todo.completed:
                max_order = db.session.query(db.func.max(Todo.order)).filter_by(todo_list_id=list_id).scalar() or 0
                todo.order = max_order + 1
                logger.debug(f"Todo marked complete, moved to order {todo.order}")

        if 'order' in data:
            if not isinstance(data['order'], int):
                return jsonify({'error': 'Order field must be an integer'}), 400
            todo.order = data['order']
        
        try:
            db.session.commit()
            logger.info(f"Todo {todo_id} updated successfully for list {list_id}")
        except Exception as e:
            logger.error(f"Database error updating todo {todo_id}: {e}")
            db.session.rollback()
            return jsonify({'error': 'Database error updating todo'}), 500
        
        return jsonify({
            'message': 'Todo updated successfully',
            'todo': todo.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update todo {todo_id} for list {list_id}: {e}")
        return jsonify({'error': 'Failed to update todo', 'details': str(e)}), 500

@todos_bp.route('/<int:todo_id>', methods=['DELETE'])
def delete_todo(list_id, todo_id):
    """Delete a specific todo from a list"""
    try:
        todo = Todo.query.filter_by(id=todo_id, todo_list_id=list_id).first()
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        db.session.delete(todo)
        db.session.commit()
        
        logger.info(f"Todo {todo_id} deleted from list {list_id}")
        return jsonify({'message': 'Todo deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete todo {todo_id} from list {list_id}: {e}")
        return jsonify({'error': 'Failed to delete todo', 'details': str(e)}), 500

@todos_bp.route('/reorder', methods=['PUT'])
def reorder_todos(list_id):
    """Reorder all todos in a list"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        if 'ordered_ids' not in data or not isinstance(data['ordered_ids'], list):
            return jsonify({'error': 'Missing or invalid required field: ordered_ids (must be a list)'}), 400

        ordered_ids = data['ordered_ids']
        
        todos = Todo.query.filter_by(todo_list_id=list_id).all()
        todo_map = {todo.id: todo for todo in todos}

        if len(ordered_ids) != len(todos) or set(ordered_ids) != set(todo_map.keys()):
            return jsonify({'error': 'Provided IDs do not match todos in this list'}), 400

        for index, todo_id in enumerate(ordered_ids):
            if todo_id in todo_map:
                todo_map[todo_id].order = index

        db.session.commit()

        logger.info(f"Todos reordered for list {list_id}")
        return jsonify({'message': 'Todos reordered successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to reorder todos for list {list_id}: {e}")
        return jsonify({'error': 'Failed to reorder todos', 'details': str(e)}), 500
