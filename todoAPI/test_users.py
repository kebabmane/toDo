"""
Tests for user management endpoints (admin only)
"""
import pytest
import json
from models import User, UserRole, db


class TestGetUsers:
    """Test get users endpoint"""
    
    def test_get_users_success_admin(self, client, admin_headers, test_user):
        """Test successful retrieval of users by admin"""
        response = client.get('/users/', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that user data is properly formatted
        user_found = False
        for user in data:
            if user['username'] == test_user.username:
                user_found = True
                assert 'id' in user
                assert 'email' in user
                assert 'role' in user
                assert 'is_active' in user
                assert 'created_at' in user
                assert 'password' not in user  # Should not expose password
        
        assert user_found, "Test user should be in the users list"
    
    def test_get_users_forbidden_regular_user(self, client, auth_headers):
        """Test that regular users cannot access users endpoint"""
        response = client.get('/users/', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_get_users_no_auth(self, client):
        """Test getting users without authentication"""
        response = client.get('/users/')
        
        assert response.status_code == 401


class TestUpdateUser:
    """Test update user endpoint"""
    
    def test_update_user_role_success(self, client, admin_headers, test_user):
        """Test successful user role update by admin"""
        response = client.put(f'/users/{test_user.id}', 
                            json={'role': 'power_user'},
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['role'] == 'power_user'
        assert data['id'] == test_user.id
        
        # Verify in database
        updated_user = User.query.get(test_user.id)
        assert updated_user.role == UserRole.POWER_USER
    
    def test_update_user_is_active_success(self, client, admin_headers, test_user):
        """Test successful user activation status update"""
        response = client.put(f'/users/{test_user.id}', 
                            json={'is_active': False},
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['is_active'] == False
        assert data['id'] == test_user.id
        
        # Verify in database
        updated_user = User.query.get(test_user.id)
        assert updated_user.is_active == False
    
    def test_update_user_both_fields(self, client, admin_headers, test_user):
        """Test updating both role and is_active"""
        response = client.put(f'/users/{test_user.id}', 
                            json={'role': 'admin', 'is_active': False},
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['role'] == 'admin'
        assert data['is_active'] == False
    
    def test_update_user_invalid_role(self, client, admin_headers, test_user):
        """Test updating user with invalid role"""
        response = client.put(f'/users/{test_user.id}', 
                            json={'role': 'invalid_role'},
                            headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid role' in data['message']
    
    def test_update_user_not_found(self, client, admin_headers):
        """Test updating non-existent user"""
        response = client.put('/users/99999', 
                            json={'role': 'admin'},
                            headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_update_user_forbidden_regular_user(self, client, auth_headers, test_user):
        """Test that regular users cannot update other users"""
        response = client.put(f'/users/{test_user.id}', 
                            json={'role': 'admin'},
                            headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_update_user_no_auth(self, client, test_user):
        """Test updating user without authentication"""
        response = client.put(f'/users/{test_user.id}', 
                            json={'role': 'admin'})
        
        assert response.status_code == 401


class TestDeleteUser:
    """Test delete user endpoint"""
    
    def test_delete_user_success(self, client, admin_headers):
        """Test successful user deletion by admin"""
        # Create a user to delete
        user_to_delete = User(username='deleteme', email='delete@example.com')
        user_to_delete.set_password('password123')
        db.session.add(user_to_delete)
        db.session.commit()
        user_id = user_to_delete.id
        
        response = client.delete(f'/users/{user_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'User deleted'
        
        # Verify user is deleted from database
        deleted_user = User.query.get(user_id)
        assert deleted_user is None
    
    def test_delete_user_not_found(self, client, admin_headers):
        """Test deleting non-existent user"""
        response = client.delete('/users/99999', headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_delete_user_forbidden_regular_user(self, client, auth_headers, test_user):
        """Test that regular users cannot delete users"""
        response = client.delete(f'/users/{test_user.id}', headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_delete_user_no_auth(self, client, test_user):
        """Test deleting user without authentication"""
        response = client.delete(f'/users/{test_user.id}')
        
        assert response.status_code == 401


class TestAdminResetPassword:
    """Test admin password reset endpoint"""
    
    def test_admin_reset_password_success(self, client, admin_headers, test_user):
        """Test successful password reset by admin"""
        new_password = 'NewPassword123!'
        
        response = client.post(f'/users/{test_user.id}/reset-password',
                             json={'password': new_password},
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Password has been reset successfully.'
        
        # Verify password was changed
        updated_user = User.query.get(test_user.id)
        assert updated_user.check_password(new_password)
        assert not updated_user.check_password('password123')  # Old password
    
    def test_admin_reset_password_missing_password(self, client, admin_headers, test_user):
        """Test password reset without providing password"""
        response = client.post(f'/users/{test_user.id}/reset-password',
                             json={},
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Password is required' in data['message']
    
    def test_admin_reset_password_not_found(self, client, admin_headers):
        """Test password reset for non-existent user"""
        response = client.post('/users/99999/reset-password',
                             json={'password': 'NewPassword123!'},
                             headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_admin_reset_password_forbidden_regular_user(self, client, auth_headers, test_user):
        """Test that regular users cannot reset other users' passwords"""
        response = client.post(f'/users/{test_user.id}/reset-password',
                             json={'password': 'NewPassword123!'},
                             headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_admin_reset_password_no_auth(self, client, test_user):
        """Test password reset without authentication"""
        response = client.post(f'/users/{test_user.id}/reset-password',
                             json={'password': 'NewPassword123!'})
        
        assert response.status_code == 401