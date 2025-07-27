import React, { useState } from 'react';

const TodoItem = ({ todo, updateTodo, deleteTodo, onDragStart, onDragEnd, onDragOver, onDrop, isDragging }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [text, setText] = useState(todo.title);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleUpdate = () => {
    updateTodo(todo.id, { title: text });
    setIsEditing(false);
  };

  const handleDelete = () => {
    deleteTodo(todo.id);
  };

  const handleToggleCompleted = () => {
    updateTodo(todo.id, { completed: !todo.completed });
  };

  const handleDragStart = (e) => {
    onDragStart(e, todo);
  };

  const handleDragEnd = (e) => {
    onDragEnd(e);
    setIsDragOver(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    onDragOver(e, todo);
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    // Only set to false if we're leaving the entire todo item
    const rect = e.currentTarget.getBoundingClientRect();
    const { clientX, clientY } = e;
    
    if (
      clientX < rect.left ||
      clientX > rect.right ||
      clientY < rect.top ||
      clientY > rect.bottom
    ) {
      setIsDragOver(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    onDrop(e, todo);
    setIsDragOver(false);
  };

  return (
    <div 
      draggable={!isEditing && !todo.completed}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`group mb-3 p-5 bg-white/80 backdrop-blur-sm rounded-2xl border transition-all duration-200 hover:shadow-lg cursor-grab active:cursor-grabbing ${
        isDragging ? 'opacity-50 scale-105 rotate-2 shadow-2xl' : ''
      } ${
        isDragOver ? 'border-blue-400 bg-blue-50/50 scale-102' : ''
      } ${
        todo.completed 
          ? 'border-gray-200 bg-gray-50/80' 
          : 'border-white/50 hover:border-blue-200 shadow-sm'
      } ${
        !isEditing && !todo.completed ? 'hover:cursor-grab' : ''
      }`}>
      
      {/* Drag Handle */}
      {!isEditing && !todo.completed && (
        <div className="absolute left-2 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-60 transition-opacity duration-200">
          <div className="flex flex-col space-y-1">
            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
            <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
          </div>
        </div>
      )}

      <div className="flex items-center gap-4 pl-4">
        {/* Custom Checkbox */}
        <div className="relative">
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={handleToggleCompleted}
            className="sr-only"
          />
          <div 
            onClick={handleToggleCompleted}
            className={`w-6 h-6 rounded-full border-2 cursor-pointer transition-all duration-200 flex items-center justify-center ${
              todo.completed
                ? 'bg-gradient-to-r from-green-400 to-blue-500 border-green-400'
                : 'border-gray-300 hover:border-blue-400'
            }`}
          >
            {todo.completed && (
              <span className="text-white text-sm font-bold">✓</span>
            )}
          </div>
        </div>

        {/* Todo Content */}
        <div className="flex-1">
          {isEditing ? (
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full px-4 py-2 bg-white border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all duration-200"
              autoFocus
            />
          ) : (
            <span className={`text-lg transition-all duration-200 ${
              todo.completed 
                ? 'text-gray-500 line-through' 
                : 'text-gray-800'
            }`}>
              {todo.title}
            </span>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-all duration-200">
          {isEditing ? (
            <>
              <button
                onClick={handleUpdate}
                className="p-2 bg-gradient-to-r from-green-400 to-green-600 hover:from-green-500 hover:to-green-700 text-white rounded-lg transition-all duration-200 transform hover:scale-105 shadow-sm hover:shadow-md"
                title="Save changes"
              >
                💾
              </button>
              <button
                onClick={() => {
                  setIsEditing(false);
                  setText(todo.title);
                }}
                className="p-2 bg-gradient-to-r from-gray-400 to-gray-600 hover:from-gray-500 hover:to-gray-700 text-white rounded-lg transition-all duration-200 transform hover:scale-105 shadow-sm hover:shadow-md"
                title="Cancel editing"
              >
                ❌
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="p-2 bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 text-white rounded-lg transition-all duration-200 transform hover:scale-105 shadow-sm hover:shadow-md"
                title="Edit todo"
              >
                ✏️
              </button>
              <button
                onClick={handleDelete}
                className="p-2 bg-gradient-to-r from-red-400 to-red-600 hover:from-red-500 hover:to-red-700 text-white rounded-lg transition-all duration-200 transform hover:scale-105 shadow-sm hover:shadow-md"
                title="Delete todo"
              >
                🗑️
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TodoItem;
