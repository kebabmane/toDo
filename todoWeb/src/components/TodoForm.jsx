import React, { useState } from 'react';

const TodoForm = ({ addTodo }) => {
  const [text, setText] = useState('');

  const handleSubmit = e => {
    e.preventDefault();
    if (!text.trim()) return;
    addTodo(text);
    setText('');
  };

  return (
    <form onSubmit={handleSubmit} className="mb-8">
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            className="w-full px-5 py-4 text-lg bg-white/70 border border-gray-200 rounded-2xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all duration-200 placeholder-gray-400"
            placeholder="✍️ What needs to be done?"
            value={text}
            onChange={e => setText(e.target.value)}
          />
        </div>
        <button 
          type="submit" 
          className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-2xl transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={!text.trim()}
        >
          <span className="flex items-center">
            ➕ Add
          </span>
        </button>
      </div>
    </form>
  );
};

export default TodoForm;