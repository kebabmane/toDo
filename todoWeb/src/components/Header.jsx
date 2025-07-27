import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Header = ({ isAuthenticated, setIsAuthenticated, user }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    navigate('/login');
  };

  return (
    <header className="bg-white/90 backdrop-blur-md border-b border-white/50 shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-3xl">✨</span>
              <span>toDo</span>
            </Link>
          </h1>
          
          <nav className="flex items-center space-x-3">
            {isAuthenticated ? (
              <>
                {user && user.role === 'admin' && (
                  <Link
                    to="/user-management"
                    className="inline-flex items-center px-4 py-2 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-all duration-200 hover:scale-105"
                  >
                    👥 Admin
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center px-6 py-2 rounded-xl font-medium text-white bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  🚪 Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="inline-flex items-center px-6 py-2 rounded-xl font-medium text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  🔑 Login
                </Link>
                <Link
                  to="/signup"
                  className="inline-flex items-center px-4 py-2 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-all duration-200 hover:scale-105"
                >
                  ✍️ Sign Up
                </Link>
                <Link
                  to="/settings"
                  className="inline-flex items-center px-4 py-2 rounded-xl font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-all duration-200 hover:scale-105"
                >
                  ⚙️ Settings
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
