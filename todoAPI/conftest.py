"""
Test configuration and fixtures for the Todo API
"""
import pytest
import tempfile
import os
from app import create_app
from models import db, User, Todo, UserRole


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create app with test configuration
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'JWT_SECRET_KEY': 'test-jwt-secret',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
    })
    
    # Create the database and tables
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.drop_all()
    
    # Clean up temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        # Merge the user object with the session to avoid DetachedInstanceError
        yield db.session.merge(user)


@pytest.fixture
def test_user2(app):
    """Create a second test user for isolation testing."""
    with app.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('testpass456')
        db.session.add(user)
        db.session.commit()
        # Merge the user object with the session to avoid DetachedInstanceError
        yield db.session.merge(user)


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for API requests."""
    # Login to get JWT token
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def auth_headers2(client, test_user2):
    """Get authentication headers for second test user."""
    response = client.post('/auth/login', json={
        'username': 'testuser2',
        'password': 'testpass456'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_todo(app, test_user):
    """Create a sample todo for testing."""
    with app.app_context():
        todo = Todo(
            user_id=test_user.id,
            title='Test Todo',
            description='This is a test todo',
            completed=False
        )
        db.session.add(todo)
        db.session.commit()
        yield db.session.merge(todo)


@pytest.fixture
def completed_todo(app, test_user):
    """Create a completed todo for testing."""
    with app.app_context():
        todo = Todo(
            user_id=test_user.id,
            title='Completed Todo',
            description='This todo is completed',
            completed=True
        )
        db.session.add(todo)
        db.session.commit()
        yield db.session.merge(todo)


@pytest.fixture
def admin_user(app):
    """Create an admin test user in the database."""
    with app.app_context():
        user = User(username='adminuser', email='admin@example.com')
        user.set_password('adminpass123')
        user.role = UserRole.ADMIN
        db.session.add(user)
        db.session.commit()
        yield db.session.merge(user)


@pytest.fixture
def admin_headers(client, admin_user):
    """Get authentication headers for admin API requests."""
    response = client.post('/auth/login', json={
        'username': 'adminuser',
        'password': 'adminpass123'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}
