# toDo API Documentation

## Overview

The toDo API is a RESTful service for managing todo lists and tasks. It provides comprehensive functionality for user authentication, todo list management, task operations, and user administration.

**Base URL:** `http://localhost:5001`  
**Authentication:** JWT Bearer Token  
**Content Type:** `application/json`

## Table of Contents

1. [Authentication](#authentication)
2. [Todo Lists](#todo-lists)
3. [Todos (Nested)](#todos-nested)
4. [Todos (Simple)](#todos-simple)
5. [User Management](#user-management)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Integration Examples](#integration-examples)

---

## Authentication

### Register User

Create a new user account.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-07-27T10:30:00.000000"
  }
}
```

**Validation Rules:**
- Username: 3-50 characters, alphanumeric + underscore
- Email: Valid email format
- Password: Minimum 6 characters

---

### Login User

Authenticate user and receive access token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

---

### Get Current User

Get current authenticated user information.

**Endpoint:** `GET /auth/me`  
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2025-07-27T10:30:00.000000"
}
```

---

## Todo Lists

### Create Todo List

Create a new todo list for the authenticated user.

**Endpoint:** `POST /todolists`  
**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "My Work Tasks"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "My Work Tasks",
  "user_id": 1,
  "created_at": "2025-07-27T10:30:00.000000",
  "todos": []
}
```

---

### Get All Todo Lists

Retrieve all todo lists for the authenticated user.

**Endpoint:** `GET /todolists`  
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "My Work Tasks",
    "user_id": 1,
    "created_at": "2025-07-27T10:30:00.000000",
    "todos": [
      {
        "id": 1,
        "title": "Complete API documentation",
        "description": null,
        "completed": false,
        "order": 1,
        "todo_list_id": 1,
        "user_id": 1,
        "created_at": "2025-07-27T10:35:00.000000",
        "updated_at": "2025-07-27T10:35:00.000000"
      }
    ]
  }
]
```

---

### Get Specific Todo List

Retrieve a specific todo list by ID.

**Endpoint:** `GET /todolists/{list_id}`  
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "name": "My Work Tasks",
  "user_id": 1,
  "created_at": "2025-07-27T10:30:00.000000",
  "todos": [...]
}
```

---

### Update Todo List

Update todo list name.

**Endpoint:** `PUT /todolists/{list_id}`  
**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Updated List Name"
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Updated List Name",
  "user_id": 1,
  "created_at": "2025-07-27T10:30:00.000000",
  "todos": [...]
}
```

---

### Delete Todo List

Delete a todo list and all its todos.

**Endpoint:** `DELETE /todolists/{list_id}`  
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "TodoList deleted successfully"
}
```

---

## Todos (Nested)

Todos within specific todo lists. All nested todo endpoints require the list_id parameter.

### Get Todos from List

Get all todos from a specific todo list.

**Endpoint:** `GET /todolists/{list_id}/todos`  
**Headers:** `Authorization: Bearer <token>`  
**Query Parameters:**
- `completed` (optional): Filter by completion status (`true`, `false`)

**Response (200):**
```json
{
  "todos": [
    {
      "id": 1,
      "title": "Complete API documentation",
      "description": "Write comprehensive API docs",
      "completed": false,
      "order": 1,
      "todo_list_id": 1,
      "user_id": 1,
      "created_at": "2025-07-27T10:35:00.000000",
      "updated_at": "2025-07-27T10:35:00.000000"
    }
  ],
  "count": 1
}
```

---

### Create Todo in List

Create a new todo within a specific list.

**Endpoint:** `POST /todolists/{list_id}/todos`  
**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "New task",
  "description": "Optional description"
}
```

**Response (201):**
```json
{
  "message": "Todo created successfully",
  "todo": {
    "id": 2,
    "title": "New task",
    "description": "Optional description",
    "completed": false,
    "order": 2,
    "todo_list_id": 1,
    "user_id": 1,
    "created_at": "2025-07-27T10:40:00.000000",
    "updated_at": "2025-07-27T10:40:00.000000"
  }
}
```

---

### Get Specific Todo

Get a specific todo from a list.

**Endpoint:** `GET /todolists/{list_id}/todos/{todo_id}`  
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "todo": {
    "id": 1,
    "title": "Complete API documentation",
    "description": "Write comprehensive API docs",
    "completed": false,
    "order": 1,
    "todo_list_id": 1,
    "user_id": 1,
    "created_at": "2025-07-27T10:35:00.000000",
    "updated_at": "2025-07-27T10:35:00.000000"
  }
}
```

---

### Update Todo

Update a specific todo in a list.

**Endpoint:** `PUT /todolists/{list_id}/todos/{todo_id}`  
**Headers:** `Authorization: Bearer <token>`

**Request Body (partial updates allowed):**
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true,
  "order": 5
}
```

**Response (200):**
```json
{
  "message": "Todo updated successfully",
  "todo": {
    "id": 1,
    "title": "Updated task title",
    "description": "Updated description",
    "completed": true,
    "order": 5,
    "todo_list_id": 1,
    "user_id": 1,
    "created_at": "2025-07-27T10:35:00.000000",
    "updated_at": "2025-07-27T10:45:00.000000"
  }
}
```

---

### Delete Todo

Delete a specific todo from a list.

**Endpoint:** `DELETE /todolists/{list_id}/todos/{todo_id}`  
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Todo deleted successfully"
}
```

---

### Reorder Todos

Reorder all todos in a specific list.

**Endpoint:** `PUT /todolists/{list_id}/todos/reorder`  
**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "ordered_ids": [3, 1, 2]
}
```

**Response (200):**
```json
{
  "message": "Todos reordered successfully"
}
```

**Note:** The `ordered_ids` array must contain ALL todo IDs from the list in the desired order.

---

## Todos (Simple)

Simple todo management without list association.

### Get All Todos

Get all todos for the authenticated user.

**Endpoint:** `GET /todos`  
**Headers:** `Authorization: Bearer <token>`  
**Query Parameters:**
- `completed` (optional): Filter by completion status (`true`, `false`)

**Response (200):**
```json
{
  "todos": [
    {
      "id": 1,
      "title": "Simple todo",
      "description": null,
      "completed": false,
      "order": 1,
      "todo_list_id": null,
      "user_id": 1,
      "created_at": "2025-07-27T10:35:00.000000",
      "updated_at": "2025-07-27T10:35:00.000000"
    }
  ],
  "count": 1
}
```

---

### Create Simple Todo

Create a standalone todo not associated with any list.

**Endpoint:** `POST /todos`  
**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Simple task",
  "description": "Optional description"
}
```

**Response (201):**
```json
{
  "message": "Todo created successfully",
  "todo": {
    "id": 1,
    "title": "Simple task",
    "description": "Optional description",
    "completed": false,
    "order": 1,
    "todo_list_id": null,
    "user_id": 1,
    "created_at": "2025-07-27T10:35:00.000000",
    "updated_at": "2025-07-27T10:35:00.000000"
  }
}
```

---

### Update Simple Todo

Update a standalone todo.

**Endpoint:** `PUT /todos/{todo_id}`  
**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Updated simple task",
  "completed": true
}
```

**Response (200):**
```json
{
  "message": "Todo updated successfully",
  "todo": {
    "id": 1,
    "title": "Updated simple task",
    "description": "Optional description",
    "completed": true,
    "order": 1,
    "todo_list_id": null,
    "user_id": 1,
    "created_at": "2025-07-27T10:35:00.000000",
    "updated_at": "2025-07-27T10:50:00.000000"
  }
}
```

---

### Delete Simple Todo

Delete a standalone todo.

**Endpoint:** `DELETE /todos/{todo_id}`  
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Todo deleted successfully"
}
```

---

## User Management

Admin-only endpoints for user management.

### Get All Users

Retrieve all users (admin only).

**Endpoint:** `GET /users`  
**Headers:** `Authorization: Bearer <admin_token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-07-27T10:30:00.000000"
  },
  {
    "id": 2,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2025-07-27T10:25:00.000000"
  }
]
```

---

### Update User

Update user role or status (admin only).

**Endpoint:** `PUT /users/{user_id}`  
**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "role": "admin",
  "is_active": false
}
```

**Response (200):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "admin",
  "is_active": false,
  "created_at": "2025-07-27T10:30:00.000000"
}
```

**Valid Roles:** `user`, `admin`

---

### Delete User

Delete a user account (admin only).

**Endpoint:** `DELETE /users/{user_id}`  
**Headers:** `Authorization: Bearer <admin_token>`

**Response (200):**
```json
{
  "message": "User deleted"
}
```

---

### Reset User Password

Reset a user's password (admin only).

**Endpoint:** `POST /users/{user_id}/reset-password`  
**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "password": "newpassword123"
}
```

**Response (200):**
```json
{
  "message": "Password has been reset successfully."
}
```

---

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses.

### Error Response Format

```json
{
  "error": "Error message",
  "details": "Additional error details (when available)"
}
```

### Common Status Codes

- **200** - Success
- **201** - Created
- **400** - Bad Request (validation errors, missing fields)
- **401** - Unauthorized (invalid or missing token)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found (resource doesn't exist)
- **429** - Too Many Requests (rate limit exceeded)
- **500** - Internal Server Error

### Example Error Responses

**400 Bad Request:**
```json
{
  "error": "Missing required fields: username, email, password"
}
```

**401 Unauthorized:**
```json
{
  "error": "Authorization token is required"
}
```

**404 Not Found:**
```json
{
  "error": "TodoList not found or you do not have permission to access it"
}
```

**429 Too Many Requests:**
```json
{
  "error": "Too Many Requests",
  "details": "100 per 1 minute"
}
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **10,000 requests per day**
- **1,000 requests per hour**
- **100 requests per minute**

Rate limits are applied per IP address. When exceeded, the API returns a 429 status code.

**Note:** OPTIONS requests (CORS preflight) are exempt from rate limiting.

---

## Integration Examples

### JavaScript/Node.js Example

```javascript
class TodoAPI {
  constructor(baseURL = 'http://localhost:5001') {
    this.baseURL = baseURL;
    this.token = null;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Request failed');
    }

    return response.json();
  }

  async login(username, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    
    this.token = response.access_token;
    return response;
  }

  async createTodoList(name) {
    return this.request('/todolists', {
      method: 'POST',
      body: JSON.stringify({ name })
    });
  }

  async getTodoLists() {
    return this.request('/todolists');
  }

  async createTodo(listId, title, description = null) {
    return this.request(`/todolists/${listId}/todos`, {
      method: 'POST',
      body: JSON.stringify({ title, description })
    });
  }

  async updateTodo(listId, todoId, updates) {
    return this.request(`/todolists/${listId}/todos/${todoId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async reorderTodos(listId, orderedIds) {
    return this.request(`/todolists/${listId}/todos/reorder`, {
      method: 'PUT',
      body: JSON.stringify({ ordered_ids: orderedIds })
    });
  }
}

// Usage example
const api = new TodoAPI();

async function example() {
  try {
    // Login
    await api.login('johndoe', 'password123');
    
    // Create a todo list
    const list = await api.createTodoList('My Project Tasks');
    
    // Add some todos
    await api.createTodo(list.id, 'Setup development environment');
    await api.createTodo(list.id, 'Write API documentation');
    
    // Get all lists
    const lists = await api.getTodoLists();
    console.log('Todo lists:', lists);
    
  } catch (error) {
    console.error('API Error:', error.message);
  }
}
```

### Python Example

```python
import requests
import json

class TodoAPI:
    def __init__(self, base_url='http://localhost:5001'):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        response = self.session.request(
            method, url, 
            headers=headers,
            json=data if data else None
        )
        
        if not response.ok:
            error_data = response.json()
            raise Exception(error_data.get('error', 'Request failed'))
        
        return response.json()
    
    def login(self, username, password):
        response = self._request('POST', '/auth/login', {
            'username': username,
            'password': password
        })
        self.token = response['access_token']
        return response
    
    def create_todo_list(self, name):
        return self._request('POST', '/todolists', {'name': name})
    
    def get_todo_lists(self):
        return self._request('GET', '/todolists')
    
    def create_todo(self, list_id, title, description=None):
        data = {'title': title}
        if description:
            data['description'] = description
        return self._request('POST', f'/todolists/{list_id}/todos', data)
    
    def update_todo(self, list_id, todo_id, **updates):
        return self._request('PUT', f'/todolists/{list_id}/todos/{todo_id}', updates)

# Usage example
api = TodoAPI()

try:
    # Login
    api.login('johndoe', 'password123')
    
    # Create a todo list
    todo_list = api.create_todo_list('Shopping List')
    
    # Add todos
    api.create_todo(todo_list['id'], 'Buy groceries')
    api.create_todo(todo_list['id'], 'Pick up dry cleaning')
    
    # Get all lists
    lists = api.get_todo_lists()
    print('Todo lists:', lists)
    
except Exception as e:
    print(f'API Error: {e}')
```

### cURL Examples

**Register and Login:**
```bash
# Register
curl -X POST http://localhost:5001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "email": "john@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "password": "password123"}'
```

**Working with Todo Lists:**
```bash
# Set token from login response
TOKEN="your_jwt_token_here"

# Create todo list
curl -X POST http://localhost:5001/todolists \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Work Tasks"}'

# Get all todo lists
curl -X GET http://localhost:5001/todolists \
  -H "Authorization: Bearer $TOKEN"

# Create todo in list
curl -X POST http://localhost:5001/todolists/1/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Complete project", "description": "Finish the main features"}'

# Update todo
curl -X PUT http://localhost:5001/todolists/1/todos/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"completed": true}'
```

---

## Best Practices

1. **Token Management**: Store JWT tokens securely and refresh them before expiration
2. **Error Handling**: Always handle API errors gracefully in your application
3. **Rate Limiting**: Implement retry logic with exponential backoff for rate-limited requests
4. **Validation**: Validate data on the client side before sending requests
5. **HTTPS**: Use HTTPS in production for secure token transmission
6. **Pagination**: For large datasets, consider implementing pagination (currently not implemented)

---

## Support

For questions or issues with the toDo API, please refer to the source code or contact the development team.

**Repository:** [toDo API](https://github.com/your-repo/todo-api)  
**Version:** 1.0.0  
**Last Updated:** July 27, 2025