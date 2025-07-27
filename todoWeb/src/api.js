const API_URL = 'http://localhost:5001';

export const setApiUrl = (url) => {
  // This function is now a no-op but is kept to avoid breaking imports
  // in other components. It can be removed later if desired.
  console.warn("setApiUrl is deprecated and no longer functions.");
};

const handleUnauthorized = () => {
  localStorage.removeItem('token');
  window.location.href = '/login';
};

const fetchWithAuth = async (url, options = {}) => {
  const token = getToken();
  const headers = {
    ...options.headers,
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    handleUnauthorized();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error('Request failed');
  }

  return response.json();
};


export const getToken = () => {
  return localStorage.getItem('token');
};

export const login = async (username, password) => {
  const data = await fetchWithAuth(`${API_URL}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  localStorage.setItem('token', data.access_token);
  return data;
};

export const register = async (username, email, password) => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password }),
  });

  if (!response.ok) {
    throw new Error('Request failed');
  }

  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data;
};

export const getTodoLists = async () => {
  const data = await fetchWithAuth(`${API_URL}/todolists`);
  return data;
};

export const createTodoList = async (name) => {
  return fetchWithAuth(`${API_URL}/todolists`, {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
};

export const updateTodoList = async (listId, updates) => {
  return fetchWithAuth(`${API_URL}/todolists/${listId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
};

export const deleteTodoList = async (listId) => {
  return fetchWithAuth(`${API_URL}/todolists/${listId}`, {
    method: 'DELETE',
  });
};

export const getTodos = async (listId) => {
  const data = await fetchWithAuth(`${API_URL}/todolists/${listId}/todos`);
  return data.todos;
};

export const createTodo = async (listId, text) => {
  return fetchWithAuth(`${API_URL}/todolists/${listId}/todos`, {
    method: 'POST',
    body: JSON.stringify({ title: text }),
  });
};

export const updateTodo = async (listId, todoId, updates) => {
  return fetchWithAuth(`${API_URL}/todolists/${listId}/todos/${todoId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
};

export const deleteTodo = async (listId, todoId) => {
  return fetchWithAuth(`${API_URL}/todolists/${listId}/todos/${todoId}`, {
    method: 'DELETE',
  });
};

export const reorderTodos = async (listId, orderedIds) => {
  return fetchWithAuth(`${API_URL}/todolists/${listId}/todos/reorder`, {
    method: 'PUT',
    body: JSON.stringify({ ordered_ids: orderedIds }),
  });
};

export const getUsers = async () => {
  return fetchWithAuth(`${API_URL}/users`);
};

export const updateUser = async (id, updates) => {
  return fetchWithAuth(`${API_URL}/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
};

export const deleteUser = async (id) => {
  return fetchWithAuth(`${API_URL}/users/${id}`, {
    method: 'DELETE',
  });
};

export const requestPasswordReset = async (email) => {
  return fetchWithAuth(`${API_URL}/auth/request-password-reset`, {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
};

export const resetPassword = async (token, password) => {
  return fetchWithAuth(`${API_URL}/auth/reset-password`, {
    method: 'POST',
    body: JSON.stringify({ token, password }),
  });
};

export const adminResetPassword = async (userId, password) => {
  return fetchWithAuth(`${API_URL}/users/${userId}/reset-password`, {
    method: 'POST',
    body: JSON.stringify({ password }),
  });
};
