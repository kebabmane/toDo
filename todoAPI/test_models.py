"""
Tests for database models
"""
import pytest
from datetime import datetime
from models import db, User, Todo


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self, app):
        """Test basic user creation"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password_hash is not None
            assert user.password_hash != 'password123'
            assert isinstance(user.created_at, datetime)
    
    def test_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            
            # Test setting and checking password
            user.set_password('mypassword')
            assert user.check_password('mypassword') is True
            assert user.check_password('wrongpassword') is False
            
            # Test that password is actually hashed
            assert user.password_hash != 'mypassword'
            assert len(user.password_hash) > 20  # Hashed passwords are long
    
    def test_user_to_dict(self, app):
        """Test user serialization to dictionary"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            # Check that all expected fields are present
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'email' in user_dict
            assert 'created_at' in user_dict
            
            # Check that password is NOT included
            assert 'password' not in user_dict
            assert 'password_hash' not in user_dict
            
            # Check values
            assert user_dict['username'] == 'testuser'
            assert user_dict['email'] == 'test@example.com'
            assert isinstance(user_dict['created_at'], str)  # Should be ISO format
    
    def test_user_unique_constraints(self, app):
        """Test that username and email must be unique"""
        with app.app_context():
            # Create first user
            user1 = User(username='testuser', email='test@example.com')
            user1.set_password('password123')
            db.session.add(user1)
            db.session.commit()
            
            # Try to create user with same username
            user2 = User(username='testuser', email='different@example.com')
            user2.set_password('password456')
            db.session.add(user2)
            
            with pytest.raises(Exception):  # Should raise IntegrityError
                db.session.commit()
            
            db.session.rollback()
            
            # Try to create user with same email
            user3 = User(username='differentuser', email='test@example.com')
            user3.set_password('password789')
            db.session.add(user3)
            
            with pytest.raises(Exception):  # Should raise IntegrityError
                db.session.commit()
    
    def test_user_todos_relationship(self, app):
        """Test relationship between User and Todo models"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Initially user should have no todos
            assert len(user.todos) == 0
            
            # Create todos for the user
            todo1 = Todo(user_id=user.id, title='Todo 1', completed=False)
            todo2 = Todo(user_id=user.id, title='Todo 2', completed=True)
            
            db.session.add(todo1)
            db.session.add(todo2)
            db.session.commit()
            
            # Refresh user from database
            db.session.refresh(user)
            
            # User should now have 2 todos
            assert len(user.todos) == 2
            assert todo1 in user.todos
            assert todo2 in user.todos
    
    def test_user_cascade_delete(self, app):
        """Test that deleting a user also deletes their todos"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Create todos for the user
            todo1 = Todo(user_id=user.id, title='Todo 1', completed=False)
            todo2 = Todo(user_id=user.id, title='Todo 2', completed=True)
            
            db.session.add(todo1)
            db.session.add(todo2)
            db.session.commit()
            
            todo1_id = todo1.id
            todo2_id = todo2.id
            
            # Delete the user
            db.session.delete(user)
            db.session.commit()
            
            # Todos should also be deleted due to cascade
            assert Todo.query.get(todo1_id) is None
            assert Todo.query.get(todo2_id) is None


class TestTodoModel:
    """Test Todo model functionality"""
    
    def test_todo_creation(self, app, test_user):
        """Test basic todo creation"""
        with app.app_context():
            todo = Todo(
                user_id=test_user.id,
                title='Test Todo',
                description='Test description',
                completed=False
            )
            
            db.session.add(todo)
            db.session.commit()
            
            assert todo.id is not None
            assert todo.user_id == test_user.id
            assert todo.title == 'Test Todo'
            assert todo.description == 'Test description'
            assert todo.completed is False
            assert isinstance(todo.created_at, datetime)
            assert isinstance(todo.updated_at, datetime)
    
    def test_todo_minimal_creation(self, app, test_user):
        """Test creating todo with minimal required fields"""
        with app.app_context():
            todo = Todo(
                user_id=test_user.id,
                title='Minimal Todo'
            )
            
            db.session.add(todo)
            db.session.commit()
            
            assert todo.title == 'Minimal Todo'
            assert todo.description is None
            assert todo.completed is False  # Should default to False
    
    def test_todo_to_dict(self, app, test_user):
        """Test todo serialization to dictionary"""
        with app.app_context():
            todo = Todo(
                user_id=test_user.id,
                title='Test Todo',
                description='Test description',
                completed=True
            )
            
            db.session.add(todo)
            db.session.commit()
            
            todo_dict = todo.to_dict()
            
            # Check that all expected fields are present
            assert 'id' in todo_dict
            assert 'user_id' in todo_dict
            assert 'title' in todo_dict
            assert 'description' in todo_dict
            assert 'completed' in todo_dict
            assert 'created_at' in todo_dict
            assert 'updated_at' in todo_dict
            
            # Check values
            assert todo_dict['title'] == 'Test Todo'
            assert todo_dict['completed'] is True
            assert isinstance(todo_dict['created_at'], str)
            assert isinstance(todo_dict['updated_at'], str)
    
    def test_todo_user_backref(self, app, test_user):
        """Test back-reference from Todo to User"""
        with app.app_context():
            todo = Todo(user_id=test_user.id, title='Test Todo')
            db.session.add(todo)
            db.session.commit()
            
            # Check that back-reference works
            assert todo.user is not None
            assert todo.user.id == test_user.id
            assert todo.user.username == 'testuser'
    
    def test_todo_onupdate_timestamp(self, app, test_user):
        """Test that updated_at timestamp is updated"""
        with app.app_context():
            todo = Todo(user_id=test_user.id, title='Test Todo')
            db.session.add(todo)
            db.session.commit()
            
            initial_updated_at = todo.updated_at
            
            # Update the todo
            todo.title = 'Updated Title'
            db.session.commit()
            
            # Check that updated_at has changed
            assert todo.updated_at > initial_updated_at
