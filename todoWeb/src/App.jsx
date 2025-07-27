import React, { useState, useEffect } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import Header from './components/Header';
import TodoList from './components/TodoList';
import TodoForm from './components/TodoForm';
import Login from './components/Login';
import Signup from './components/Signup';
import UserManagement from './components/UserManagement';
import ApiSettings from './components/ApiSettings';
import ForgotPassword from './components/ForgotPassword';
import ResetPassword from './components/ResetPassword';
import { jwtDecode } from 'jwt-decode';
import {
  getToken,
  setApiUrl,
  getTodoLists,
  createTodoList,
  deleteTodoList,
  getTodos,
  createTodo,
  updateTodo as apiUpdateTodo,
  deleteTodo as apiDeleteTodo,
  reorderTodos as apiReorderTodos,
} from './api';

const AdminRoute = ({ user, children }) => {
  if (!user || user.role !== 'admin') {
    return <Navigate to="/" />;
  }
  return children;
};

function App() {
  const [todoLists, setTodoLists] = useState([]);
  const [selectedList, setSelectedList] = useState(null);
  const [todos, setTodos] = useState([]);
  const [newListName, setNewListName] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(!!getToken());
  const [user, setUser] = useState(null);

  const handleApiUrlSet = (url) => {
    // This function is now a no-op but is kept to avoid breaking imports
    // in other components. It can be removed later if desired.
    console.warn("handleApiUrlSet is deprecated and no longer functions.");
  };

  useEffect(() => {
    if (isAuthenticated) {
      const token = getToken();
      if (token) {
        const decodedToken = jwtDecode(token);
        setUser(decodedToken);
      }
      fetchTodoLists();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (selectedList) {
      fetchTodos(selectedList.id);
    } else {
      setTodos([]);
    }
  }, [selectedList]);

  const fetchTodoLists = async () => {
    try {
      const fetchedLists = await getTodoLists();
      setTodoLists(fetchedLists);
      if (fetchedLists.length > 0) {
        setSelectedList(fetchedLists[0]);
      }
    } catch (error) {
      console.error('Failed to fetch todo lists:', error);
      alert('Failed to fetch todo lists. Please try again later.');
    }
  };

  const fetchTodos = async (listId) => {
    try {
      const fetchedTodos = await getTodos(listId);
      setTodos(fetchedTodos);
    } catch (error) {
      console.error('Failed to fetch todos:', error);
      setTodos([]); // Clear todos on error
      alert('Failed to fetch todos. Please try again later.');
    }
  };

  const handleCreateList = async (e) => {
    e.preventDefault();
    if (!newListName.trim()) return;
    try {
      const newList = await createTodoList(newListName);
      setTodoLists([...todoLists, newList]);
      setNewListName('');
      setSelectedList(newList);
    } catch (error) {
      console.error('Failed to create todo list:', error);
      alert('Failed to create todo list. Please try again later.');
    }
  };

  const handleDeleteList = async (listId) => {
    try {
      await deleteTodoList(listId);
      const updatedLists = todoLists.filter((list) => list.id !== listId);
      setTodoLists(updatedLists);
      if (selectedList && selectedList.id === listId) {
        setSelectedList(updatedLists.length > 0 ? updatedLists[0] : null);
      }
    } catch (error) {
      console.error('Failed to delete todo list:', error);
      alert('Failed to delete todo list. Please try again later.');
    }
  };

  const addTodo = async (text) => {
    if (!selectedList) return;
    try {
      const response = await createTodo(selectedList.id, text);
      setTodos([...todos, response.todo]);
    } catch (error) {
      console.error('Failed to add todo:', error);
      alert('Failed to add todo. Please try again later.');
    }
  };

  const updateTodo = async (id, updates) => {
    if (!selectedList) return;
    try {
      await apiUpdateTodo(selectedList.id, id, updates);
      fetchTodos(selectedList.id);
    } catch (error) {
      console.error('Failed to update todo:', error);
      alert('Failed to update todo. Please try again later.');
    }
  };

  const deleteTodo = async (id) => {
    if (!selectedList) return;
    try {
      await apiDeleteTodo(selectedList.id, id);
      setTodos(todos.filter((todo) => todo.id !== id));
    } catch (error) {
      console.error('Failed to delete todo:', error);
      alert('Failed to delete todo. Please try again later.');
    }
  };

  const reorderTodos = async (reorderedTodos) => {
    if (!selectedList) return;
    try {
      setTodos(reorderedTodos);
      const orderedIds = reorderedTodos.map((todo) => todo.id);
      await apiReorderTodos(selectedList.id, orderedIds);
    } catch (error) {
      console.error('Failed to reorder todos:', error);
      fetchTodos(selectedList.id);
      alert('Failed to reorder todos. Please try again later.');
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <Header
          isAuthenticated={isAuthenticated}
          setIsAuthenticated={setIsAuthenticated}
          user={user}
        />
        <div className="container mx-auto p-6">
        <Routes>
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
                  {/* Sidebar - Todo Lists */}
                  <div className="lg:col-span-1 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/50 p-6">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                      Lists
                    </h2>
                    
                    {/* Create List Form */}
                    <form onSubmit={handleCreateList} className="mb-6">
                      <div className="relative">
                        <input
                          type="text"
                          value={newListName}
                          onChange={(e) => setNewListName(e.target.value)}
                          placeholder="New list name"
                          className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all duration-200 bg-white/70"
                        />
                      </div>
                      <button 
                        type="submit" 
                        className="w-full mt-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 transform hover:scale-[1.02] shadow-lg hover:shadow-xl"
                      >
                        ✨ Create List
                      </button>
                    </form>
                    
                    {/* Todo Lists */}
                    <div className="space-y-2">
                      {todoLists.map((list) => (
                        <div
                          key={list.id}
                          className={`group relative p-4 rounded-xl cursor-pointer transition-all duration-200 ${
                            selectedList?.id === list.id 
                              ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 shadow-md' 
                              : 'bg-white/60 hover:bg-white/80 border border-gray-100 hover:border-gray-200 hover:shadow-md'
                          }`}
                          onClick={() => setSelectedList(list)}
                        >
                          <div className="flex items-center justify-between">
                            <span className={`font-medium truncate ${
                              selectedList?.id === list.id ? 'text-blue-900' : 'text-gray-700'
                            }`}>
                              {list.name}
                            </span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteList(list.id);
                              }}
                              className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 transition-all duration-200 p-1 rounded-md hover:bg-red-50"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Main Content - Todos */}
                  <div className="lg:col-span-3">
                    {selectedList ? (
                      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/50 p-8">
                        <div className="flex items-center justify-between mb-8">
                          <h2 className="text-3xl font-bold text-gray-800 flex items-center">
                            <span className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mr-4"></span>
                            {selectedList.name}
                          </h2>
                          <div className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                            {todos.length} {todos.length === 1 ? 'task' : 'tasks'}
                          </div>
                        </div>
                        
                        <TodoForm addTodo={addTodo} />
                        <TodoList
                          todos={todos}
                          updateTodo={updateTodo}
                          deleteTodo={deleteTodo}
                          reorderTodos={reorderTodos}
                        />
                      </div>
                    ) : (
                      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/50 p-12 text-center">
                        <div className="text-6xl mb-6">📝</div>
                        <h3 className="text-2xl font-semibold text-gray-700 mb-4">No List Selected</h3>
                        <p className="text-gray-500 text-lg">Select a list from the sidebar or create a new one to get started.</p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to="/" />
              ) : (
                <Login setIsAuthenticated={setIsAuthenticated} setUser={setUser} />
              )
            }
          />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/user-management"
            element={
              <AdminRoute user={user}>
                <UserManagement />
              </AdminRoute>
            }
          />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/settings" element={<ApiSettings onApiUrlSet={handleApiUrlSet} />} />
        </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
