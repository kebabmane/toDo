"""
Integration tests for full user workflows
"""
import pytest
from models import db, User, Todo


class TestFullWorkflow:
    """Test a complete user workflow from registration to todo management"""
    
    def test_full_user_workflow(self, client):
        """
        Test the full workflow:
        1. Register a new user
        2. Login with the new user
        3. Create a new todo
        4. Get the list of todos
        5. Get the specific todo
        6. Update the todo
        7. Delete the todo
        8. Verify the todo is gone
        """
        # 1. Register a new user
        register_response = client.post('/auth/register', json={
            'username': 'workflow_user',
            'email': 'workflow@example.com',
            'password': 'workflow_password'
        })
        assert register_response.status_code == 201
        register_data = register_response.get_json()
        assert 'access_token' in register_data
        
        # 2. Login with the new user
        login_response = client.post('/auth/login', json={
            'username': 'workflow_user',
            'password': 'workflow_password'
        })
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        assert 'access_token' in login_data
        
        auth_headers = {'Authorization': f"Bearer {login_data['access_token']}"}
        
        # 3. Create a new todo
        create_response = client.post('/todos', json={
            'title': 'My First Todo',
            'description': 'This is part of a workflow test'
        }, headers=auth_headers)
        assert create_response.status_code == 201
        create_data = create_response.get_json()
        assert 'todo' in create_data
        todo_id = create_data['todo']['id']
        
        # 4. Get the list of todos
        list_response = client.get('/todos', headers=auth_headers)
        assert list_response.status_code == 200
        list_data = list_response.get_json()
        assert list_data['count'] == 1
        assert list_data['todos'][0]['id'] == todo_id
        
        # 5. Get the specific todo
        get_response = client.get(f'/todos/{todo_id}', headers=auth_headers)
        assert get_response.status_code == 200
        get_data = get_response.get_json()
        assert get_data['todo']['title'] == 'My First Todo'
        
        # 6. Update the todo
        update_response = client.put(f'/todos/{todo_id}', json={
            'title': 'Updated Todo Title',
            'completed': True
        }, headers=auth_headers)
        assert update_response.status_code == 200
        update_data = update_response.get_json()
        assert update_data['todo']['title'] == 'Updated Todo Title'
        assert update_data['todo']['completed'] is True
        
        # 7. Delete the todo
        delete_response = client.delete(f'/todos/{todo_id}', headers=auth_headers)
        assert delete_response.status_code == 200
        assert 'Todo deleted successfully' in delete_response.get_json()['message']
        
        # 8. Verify the todo is gone
        verify_response = client.get(f'/todos/{todo_id}', headers=auth_headers)
        assert verify_response.status_code == 404


class TestErrorHandlingAndSecurity:
    """Test various error handling and security scenarios"""
    
    def test_database_rollback_on_registration_failure(self, app, client):
        """Test that database is rolled back if registration fails midway"""
        with app.app_context():
            # Pre-populate with a user
            user = User(username='existing_user', email='existing@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            initial_user_count = User.query.count()
        
        # This registration should fail due to duplicate username
        response = client.post('/auth/register', json={
            'username': 'existing_user',
            'email': 'new@example.com',
            'password': 'password123'
        })
        assert response.status_code == 409
        
        with app.app_context():
            # The user count should not have changed
            assert User.query.count() == initial_user_count
    
    def test_database_rollback_on_todo_creation_failure(self, client, auth_headers, app):
        """Test that database is rolled back if todo creation fails"""
        with app.app_context():
            initial_todo_count = Todo.query.count()
        
        # This request is invalid because the title is empty
        response = client.post('/todos', json={'title': ''}, headers=auth_headers)
        assert response.status_code == 400
        
        with app.app_context():
            # The todo count should not have changed
            assert Todo.query.count() == initial_todo_count
    
    def test_api_root_and_error_handlers(self, client):
        """Test the root endpoint and common error handlers"""
        # Test root endpoint
        response = client.get('/')
        assert response.status_code == 200
        assert 'ToDo API is running' in response.get_json()['message']
        
        # Test 404 Not Found
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        assert 'Endpoint not found' in response.get_json()['error']
        
        # Test 405 Method Not Allowed
        response = client.post('/')  # Root doesn't allow POST
        assert response.status_code == 405
        assert 'Method not allowed' in response.get_json()['error']
