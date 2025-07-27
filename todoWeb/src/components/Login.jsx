import React, { useState } from 'react';
import { login } from '../api';
import { Link } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

const Login = ({ setIsAuthenticated, setUser }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); // Clear previous errors
    try {
      const data = await login(username, password);
      setIsAuthenticated(true);
      const decodedToken = jwtDecode(data.access_token);
      setUser(decodedToken);
    } catch (error) {
      console.error('Failed to login:', error);
      setError('Invalid username or password. Please try again or register.');
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/50 p-8">
          <div className="text-center mb-8">
            <div className="text-5xl mb-4">🔑</div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Welcome Back
            </h2>
            <p className="text-gray-600 mt-2">Sign in to continue to toDo</p>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200">
              <p className="text-red-600 text-sm font-medium">⚠️ {error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2" htmlFor="username">
                Username
              </label>
              <input
                className="w-full px-4 py-3 bg-white/70 border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all duration-200 text-gray-800"
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2" htmlFor="password">
                Password
              </label>
              <input
                className="w-full px-4 py-3 bg-white/70 border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all duration-200 text-gray-800"
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-xl transition-all duration-200 transform hover:scale-[1.02] shadow-lg hover:shadow-xl"
              type="submit"
            >
              🚀 Sign In
            </button>
          </form>

          <div className="mt-8 text-center space-y-4">
            <Link 
              to="/forgot-password"
              className="block text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors duration-200"
            >
              Forgot your password?
            </Link>
            
            <div className="flex items-center justify-center space-x-2">
              <span className="text-gray-500 text-sm">Don't have an account?</span>
              <Link 
                to="/signup"
                className="text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors duration-200"
              >
                Sign up
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
