"""
Tests for todo endpoints
"""
import pytest
import json
from models import Todo, db


class TestGetTodos:
    """Test get todos endpoint"""
    
    def test_get_todos_success(self, client, auth_headers, test_user, sample_todo):
        """Test successful retrieval of todos"""
        response = client.get('/todos', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'todos' in data
        assert 'count' in data
        assert data['count'] == 1
        assert len(data['todos']) == 1
        assert data['todos'][0]['id'] == sample_todo.id
        assert data['todos'][0]['title'] == 'Test Todo'
    
    def test_get_todos_empty_list(self, client, auth_headers):
        """Test getting todos when user has none"""
        response = client.get('/todos', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['todos'] == []
        assert data['count'] == 0
    
    def test_get_todos_no_auth(self, client):
        """Test getting todos without authentication"""
        response = client.get('/todos')
        
        assert response.status_code == 401
        assert 'Authorization token is required' in response.get_json()['error']
    
    def test_get_todos_filter_completed(self, client, auth_headers, test_user, sample_todo, completed_todo):
        """Test filtering todos by completion status"""
        # Get only completed todos
        response = client.get('/todos?completed=true', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 1
        assert data['todos'][0]['completed'] is True
        
        # Get only incomplete todos
        response = client.get('/todos?completed=false', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 1
        assert data['todos'][0]['completed'] is False
        
        # Get all todos
        response = client.get('/todos', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 2
    
    def test_get_todos_user_isolation(self, client, auth_headers, auth_headers2, test_user, test_user2, sample_todo):
        """Test that users only see their own todos"""
        # User 1 should see their todo
        response = client.get('/todos', headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['count'] == 1
        
        # User 2 should see no todos
        response = client.get('/todos', headers=auth_headers2)
        assert response.status_code == 200
        assert response.get_json()['count'] == 0


class TestCreateTodo:
    """Test create todo endpoint"""
    
    def test_create_todo_success(self, client, auth_headers):
        """Test successful todo creation"""
        todo_data = {
            'title': 'New Todo',
            'description': 'This is a new todo'
        }
        
        response = client.post('/todos', json=todo_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['message'] == 'Todo created successfully'
        assert 'todo' in data
        assert data['todo']['title'] == 'New Todo'
        assert data['todo']['description'] == 'This is a new todo'
        assert data['todo']['completed'] is False
        assert 'id' in data['todo']
        assert 'created_at' in data['todo']
        assert 'updated_at' in data['todo']
    
    def test_create_todo_minimal(self, client, auth_headers):
        """Test creating todo with only title"""
        todo_data = {'title': 'Minimal Todo'}
        
        response = client.post('/todos', json=todo_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['todo']['title'] == 'Minimal Todo'
        assert data['todo']['description'] is None
        assert data['todo']['completed'] is False
    
    def test_create_todo_no_auth(self, client):
        """Test creating todo without authentication"""
        response = client.post('/todos', json={'title': 'Test'})
        
        assert response.status_code == 401
        assert 'Authorization token is required' in response.get_json()['error']
    
    def test_create_todo_missing_title(self, client, auth_headers):
        """Test creating todo without title"""
        response = client.post('/todos', json={}, headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Request body must be JSON' in response.get_json()['error']
    
    def test_create_todo_empty_title(self, client, auth_headers):
        """Test creating todo with empty title"""
        response = client.post('/todos', json={'title': ''}, headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Title must be between 1 and 200 characters' in response.get_json()['error']
    
    def test_create_todo_title_too_long(self, client, auth_headers):
        """Test creating todo with title too long"""
        long_title = 'a' * 201  # 201 characters
        response = client.post('/todos', json={'title': long_title}, headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Title must be between 1 and 200 characters' in response.get_json()['error']
    
    def test_create_todo_whitespace_handling(self, client, auth_headers):
        """Test creating todo with whitespace in title"""
        response = client.post('/todos', json={
            'title': '  Spaced Title  ',
            'description': '  Spaced Description  '
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['todo']['title'] == 'Spaced Title'
        assert data['todo']['description'] == 'Spaced Description'


class TestGetSingleTodo:
    """Test get single todo endpoint"""
    
    def test_get_todo_success(self, client, auth_headers, sample_todo):
        """Test successful retrieval of single todo"""
        response = client.get(f'/todos/{sample_todo.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'todo' in data
        assert data['todo']['id'] == sample_todo.id
        assert data['todo']['title'] == 'Test Todo'
        assert data['todo']['description'] == 'This is a test todo'
    
    def test_get_todo_not_found(self, client, auth_headers):
        """Test getting non-existent todo"""
        response = client.get('/todos/999', headers=auth_headers)
        
        assert response.status_code == 404
        assert 'Todo not found' in response.get_json()['error']
    
    def test_get_todo_no_auth(self, client, sample_todo):
        """Test getting todo without authentication"""
        response = client.get(f'/todos/{sample_todo.id}')
        
        assert response.status_code == 401
        assert 'Authorization token is required' in response.get_json()['error']
    
    def test_get_todo_user_isolation(self, client, auth_headers2, sample_todo):
        """Test that users can't access other users' todos"""
        response = client.get(f'/todos/{sample_todo.id}', headers=auth_headers2)
        
        assert response.status_code == 404
        assert 'Todo not found' in response.get_json()['error']


class TestUpdateTodo:
    """Test update todo endpoint"""
    
    def test_update_todo_title(self, client, auth_headers, sample_todo):
        """Test updating todo title"""
        update_data = {'title': 'Updated Title'}
        
        response = client.put(f'/todos/{sample_todo.id}', 
                            json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['message'] == 'Todo updated successfully'
        assert data['todo']['title'] == 'Updated Title'
        assert data['todo']['description'] == 'This is a test todo'  # Unchanged
        assert data['todo']['completed'] is False  # Unchanged
    
    def test_update_todo_description(self, client, auth_headers, sample_todo):
        """Test updating todo description"""
        update_data = {'description': 'Updated description'}
        
        response = client.put(f'/todos/{sample_todo.id}', 
                            json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['todo']['description'] == 'Updated description'
        assert data['todo']['title'] == 'Test Todo'  # Unchanged
    
    def test_update_todo_completed(self, client, auth_headers, sample_todo):
        """Test updating todo completion status"""
        update_data = {'completed': True}
        
        response = client.put(f'/todos/{sample_todo.id}', 
                            json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['todo']['completed'] is True
        assert data['todo']['title'] == 'Test Todo'  # Unchanged
    
    def test_update_todo_multiple_fields(self, client, auth_headers, sample_todo):
        """Test updating multiple todo fields"""
        update_data = {
            'title': 'New Title',
            'description': 'New description',
            'completed': True
        }
        
        response = client.put(f'/todos/{sample_todo.id}', 
                            json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['todo']['title'] == 'New Title'
        assert data['todo']['description'] == 'New description'
        assert data['todo']['completed'] is True
    
    def test_update_todo_not_found(self, client, auth_headers):
        """Test updating non-existent todo"""
        response = client.put('/todos/999', 
                            json={'title': 'New Title'}, headers=auth_headers)
        
        assert response.status_code == 404
        assert 'Todo not found' in response.get_json()['error']
    
    def test_update_todo_no_auth(self, client, sample_todo):
        """Test updating todo without authentication"""
        response = client.put(f'/todos/{sample_todo.id}', 
                            json={'title': 'New Title'})
        
        assert response.status_code == 401
        assert 'Authorization token is required' in response.get_json()['error']
    
    def test_update_todo_no_data(self, client, auth_headers, sample_todo):
        """Test updating todo with no data"""
        response = client.put(f'/todos/{sample_todo.id}', headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Request body must be JSON' in response.get_json()['error']
    
    def test_update_todo_invalid_title(self, client, auth_headers, sample_todo):
        """Test updating todo with invalid title"""
        # Empty title
        response = client.put(f'/todos/{sample_todo.id}', 
                            json={'title': ''}, headers=auth_headers)
        assert response.status_code == 400
        assert 'Title must be between 1 and 200 characters' in response.get_json()['error']
        
        # Title too long
        long_title = 'a' * 201
        response = client.put(f'/todos/{sample_todo.id}', 
                            json={'title': long_title}, headers=auth_headers)
        assert response.status_code == 400
        assert 'Title must be between 1 and 200 characters' in response.get_json()['error']
    
    def test_update_todo_invalid_completed(self, client, auth_headers, sample_todo):
        """Test updating todo with invalid completed value"""
        response = client.put(f'/todos/{sample_todo.id}', 
                            json={'completed': 'not-a-boolean'}, headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Completed field must be a boolean' in response.get_json()['error']
    
    def test_update_todo_user_isolation(self, client, auth_headers2, sample_todo):
        """Test that users can't update other users' todos"""
        response = client.put(f'/todos/{sample_todo.id}', 
                            json={'title': 'Hacked'}, headers=auth_headers2)
        
        assert response.status_code == 404
        assert 'Todo not found' in response.get_json()['error']
    
    def test_update_todo_clear_description(self, client, auth_headers, sample_todo):
        """Test clearing todo description"""
        response = client.put(f'/todos/{sample_todo.id}', 
                            json={'description': ''}, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['description'] is None


class TestDeleteTodo:
    """Test delete todo endpoint"""
    
    def test_delete_todo_success(self, client, auth_headers, sample_todo):
        """Test successful todo deletion"""
        response = client.delete(f'/todos/{sample_todo.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Todo deleted successfully'
        
        # Verify todo is actually deleted
        response = client.get(f'/todos/{sample_todo.id}', headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_todo_not_found(self, client, auth_headers):
        """Test deleting non-existent todo"""
        response = client.delete('/todos/999', headers=auth_headers)
        
        assert response.status_code == 404
        assert 'Todo not found' in response.get_json()['error']
    
    def test_delete_todo_no_auth(self, client, sample_todo):
        """Test deleting todo without authentication"""
        response = client.delete(f'/todos/{sample_todo.id}')
        
        assert response.status_code == 401
        assert 'Authorization token is required' in response.get_json()['error']
    
    def test_delete_todo_user_isolation(self, client, auth_headers2, sample_todo):
        """Test that users can't delete other users' todos"""
        response = client.delete(f'/todos/{sample_todo.id}', headers=auth_headers2)
        
        assert response.status_code == 404
        assert 'Todo not found' in response.get_json()['error']


class TestTodoStats:
    """Test todo statistics endpoint"""
    
    def test_stats_with_todos(self, client, auth_headers, app, test_user):
        """Test stats with various todos"""
        with app.app_context():
            # Create test todos
            todos = [
                Todo(user_id=test_user.id, title='Todo 1', completed=True),
                Todo(user_id=test_user.id, title='Todo 2', completed=True),
                Todo(user_id=test_user.id, title='Todo 3', completed=False),
                Todo(user_id=test_user.id, title='Todo 4', completed=False),
                Todo(user_id=test_user.id, title='Todo 5', completed=False),
            ]
            
            for todo in todos:
                db.session.add(todo)
            db.session.commit()
        
        response = client.get('/todos/stats', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'stats' in data
        stats = data['stats']
        assert stats['total'] == 5
        assert stats['completed'] == 2
        assert stats['pending'] == 3
        assert stats['completion_rate'] == 40.0
    
    def test_stats_no_todos(self, client, auth_headers):
        """Test stats when user has no todos"""
        response = client.get('/todos/stats', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        stats = data['stats']
        assert stats['total'] == 0
        assert stats['completed'] == 0
        assert stats['pending'] == 0
        assert stats['completion_rate'] == 0
    
    def test_stats_all_completed(self, client, auth_headers, app, test_user):
        """Test stats when all todos are completed"""
        with app.app_context():
            todos = [
                Todo(user_id=test_user.id, title='Todo 1', completed=True),
                Todo(user_id=test_user.id, title='Todo 2', completed=True),
            ]
            
            for todo in todos:
                db.session.add(todo)
            db.session.commit()
        
        response = client.get('/todos/stats', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        stats = data['stats']
        assert stats['total'] == 2
        assert stats['completed'] == 2
        assert stats['pending'] == 0
        assert stats['completion_rate'] == 100.0
    
    def test_stats_no_auth(self, client):
        """Test stats without authentication"""
        response = client.get('/todos/stats')
        
        assert response.status_code == 401
        assert 'Authorization token is required' in response.get_json()['error']
    
    def test_stats_user_isolation(self, client, auth_headers, auth_headers2, sample_todo):
        """Test that stats are isolated per user"""
        # User 1 should see their todo in stats
        response = client.get('/todos/stats', headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['stats']['total'] == 1
        
        # User 2 should see no todos in stats
        response = client.get('/todos/stats', headers=auth_headers2)
        assert response.status_code == 200
        assert response.get_json()['stats']['total'] == 0


class TestTodoEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_invalid_todo_id_format(self, client, auth_headers):
        """Test with invalid todo ID formats"""
        invalid_ids = ['abc', '12.5', 'null', '']
        
        for invalid_id in invalid_ids:
            response = client.get(f'/todos/{invalid_id}', headers=auth_headers)
            assert response.status_code == 404
    
    def test_large_todo_id(self, client, auth_headers):
        """Test with very large todo ID"""
        response = client.get('/todos/999999999999999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_malformed_json_requests(self, client, auth_headers):
        """Test with malformed JSON in requests"""
        # Test create with malformed JSON
        response = client.post('/todos', 
                             data='{"title": "test"',  # Invalid JSON
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400
    
    def test_unicode_content(self, client, auth_headers):
        """Test with Unicode content in todos"""
        unicode_data = {
            'title': '测试待办事项 🚀',
            'description': 'Тест описание with émojis 📝'
        }
        
        response = client.post('/todos', json=unicode_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['todo']['title'] == '测试待办事项 🚀'
        assert data['todo']['description'] == 'Тест описание with émojis 📝'
