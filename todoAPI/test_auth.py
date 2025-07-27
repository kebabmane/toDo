"""
Tests for authentication endpoints
"""
import pytest
import json
from flask_jwt_extended import decode_token
from models import User, db


class TestUserRegistration:
    """Test user registration endpoint"""
    
    def test_successful_registration(self, client):
        """Test successful user registration"""
        response = client.post('/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['message'] == 'User registered successfully'
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@example.com'
        assert 'password' not in data['user']
        assert 'id' in data['user']
        assert 'created_at' in data['user']
    
    def test_registration_missing_fields(self, client):
        """Test registration with missing required fields"""
        # Missing username
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert 'Missing required fields' in response.get_json()['error']
        
        # Missing email
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert 'Missing required fields' in response.get_json()['error']
        
        # Missing password
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com'
        })
        assert response.status_code == 400
        assert 'Missing required fields' in response.get_json()['error']
    
    def test_registration_invalid_email(self, client):
        """Test registration with invalid email format"""
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@missinglocal.com',
            'spaces in@email.com',
            'double@@domain.com'
        ]
        
        for email in invalid_emails:
            response = client.post('/auth/register', json={
                'username': 'testuser',
                'email': email,
                'password': 'password123'
            })
            assert response.status_code == 400
            assert 'Invalid email format' in response.get_json()['error']
    
    def test_registration_weak_password(self, client):
        """Test registration with weak password"""
        weak_passwords = ['123', 'abc', '12345', 'short']
        
        for password in weak_passwords:
            response = client.post('/auth/register', json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': password
            })
            assert response.status_code == 400
            assert 'Password must be at least 6 characters' in response.get_json()['error']
    
    def test_registration_short_username(self, client):
        """Test registration with short username"""
        response = client.post('/auth/register', json={
            'username': 'ab',  # Too short
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 400
        assert 'Username must be at least 3 characters' in response.get_json()['error']
    
    def test_registration_duplicate_username(self, client, test_user):
        """Test registration with existing username"""
        response = client.post('/auth/register', json={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'password123'
        })
        assert response.status_code == 409
        assert 'Username already exists' in response.get_json()['error']
    
    def test_registration_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        response = client.post('/auth/register', json={
            'username': 'differentuser',
            'email': 'test@example.com',  # Already exists
            'password': 'password123'
        })
        assert response.status_code == 409
        assert 'Email already exists' in response.get_json()['error']
    
    def test_registration_whitespace_handling(self, client):
        """Test registration with whitespace in username and email"""
        response = client.post('/auth/register', json={
            'username': '  spaceuser  ',
            'email': '  UPPER@EXAMPLE.COM  ',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['user']['username'] == 'spaceuser'
        assert data['user']['email'] == 'upper@example.com'


class TestUserLogin:
    """Test user login endpoint"""
    
    def test_successful_login_with_username(self, client, test_user):
        """Test successful login with username"""
        response = client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['message'] == 'Login successful'
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert 'password' not in data['user']
    
    def test_successful_login_with_email(self, client, test_user):
        """Test successful login with email"""
        response = client.post('/auth/login', json={
            'username': 'test@example.com',  # Using email as username
            'password': 'testpass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert 'access_token' in data
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        # Missing username
        response = client.post('/auth/login', json={
            'password': 'password123'
        })
        assert response.status_code == 400
        assert 'Missing required fields' in response.get_json()['error']
        
        # Missing password
        response = client.post('/auth/login', json={
            'username': 'testuser'
        })
        assert response.status_code == 400
        assert 'Missing required fields' in response.get_json()['error']
    
    def test_login_invalid_username(self, client, test_user):
        """Test login with invalid username"""
        response = client.post('/auth/login', json={
            'username': 'nonexistentuser',
            'password': 'testpass123'
        })
        assert response.status_code == 401
        assert 'Invalid username or password' in response.get_json()['error']
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password"""
        response = client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        assert 'Invalid username or password' in response.get_json()['error']
    
    def test_login_case_sensitivity(self, client, test_user):
        """Test login case sensitivity"""
        # Username should be case insensitive
        response = client.post('/auth/login', json={
            'username': 'TESTUSER',
            'password': 'testpass123'
        })
        assert response.status_code == 200
        
        # Email should work (case insensitive storage)
        response = client.post('/auth/login', json={
            'username': 'TEST@EXAMPLE.COM',
            'password': 'testpass123'
        })
        assert response.status_code == 200
    
    def test_jwt_token_validity(self, client, test_user, app):
        """Test that JWT tokens are valid and contain correct data"""
        response = client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        token = response.get_json()['access_token']
        
        # Decode token to verify contents
        with app.app_context():
            decoded = decode_token(token)
            assert decoded['sub'] == str(test_user.id)


class TestGetCurrentUser:
    """Test get current user endpoint"""
    
    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test successful retrieval of current user"""
        response = client.get('/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'user' in data
        assert data['user']['id'] == test_user.id
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
        assert 'password' not in data['user']
    
    def test_get_current_user_no_token(self, client):
        """Test get current user without authentication token"""
        response = client.get('/auth/me')
        
        assert response.status_code == 401
        assert 'Authorization token is required' in response.get_json()['error']
    
    def test_get_current_user_invalid_token(self, client):
        """Test get current user with invalid token"""
        response = client.get('/auth/me', headers={
            'Authorization': 'Bearer invalid-token'
        })
        
        assert response.status_code == 401
        assert 'Invalid token' in response.get_json()['error']
    
    def test_get_current_user_malformed_header(self, client):
        """Test get current user with malformed authorization header"""
        # Missing Bearer prefix
        response = client.get('/auth/me', headers={
            'Authorization': 'some-token'
        })
        assert response.status_code == 401
        
        # Wrong format
        response = client.get('/auth/me', headers={
            'Authorization': 'Basic some-token'
        })
        assert response.status_code == 401


class TestAuthenticationSecurity:
    """Test authentication security aspects"""
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed"""
        with app.app_context():
            user = User(username='hashtest', email='hash@example.com')
            user.set_password('testpassword')
            
            # Password should be hashed, not stored in plain text
            assert user.password_hash != 'testpassword'
            assert user.check_password('testpassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_isolation(self, client, auth_headers, auth_headers2, test_user, test_user2):
        """Test that users can only access their own data"""
        # User 1 should get their own data
        response = client.get('/auth/me', headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['user']['id'] == test_user.id
        
        # User 2 should get their own data
        response = client.get('/auth/me', headers=auth_headers2)
        assert response.status_code == 200
        assert response.get_json()['user']['id'] == test_user2.id
    
    def test_no_data_in_json_body(self, client):
        """Test endpoints with no JSON data"""
        response = client.post('/auth/register')
        assert response.status_code == 400
        
        response = client.post('/auth/login')
        assert response.status_code == 400
    
    def test_empty_json_body(self, client):
        """Test endpoints with empty JSON data"""
        response = client.post('/auth/register', json={})
        assert response.status_code == 400
        
        response = client.post('/auth/login', json={})
        assert response.status_code == 400
