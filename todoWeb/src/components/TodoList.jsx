import React, { useState } from 'react';
import TodoItem from './TodoItem';

const TodoList = ({ todos, updateTodo, deleteTodo, reorderTodos }) => {
  const [draggedTodo, setDraggedTodo] = useState(null);
  const [dragOverTodo, setDragOverTodo] = useState(null);
  
  const pendingTodos = todos.filter(todo => !todo.completed);
  const completedTodos = todos.filter(todo => todo.completed);

  const handleDragStart = (e, todo) => {
    setDraggedTodo(todo);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target.outerHTML);
  };

  const handleDragEnd = (e) => {
    setDraggedTodo(null);
    setDragOverTodo(null);
  };

  const handleDragOver = (e, targetTodo) => {
    e.preventDefault();
    if (draggedTodo && draggedTodo.id !== targetTodo.id) {
      setDragOverTodo(targetTodo);
    }
  };

  const handleDrop = (e, targetTodo) => {
    e.preventDefault();
    
    if (!draggedTodo || draggedTodo.id === targetTodo.id) {
      return;
    }

    // Only allow reordering within the same completion status
    if (draggedTodo.completed !== targetTodo.completed) {
      return;
    }

    // Find indices within the filtered arrays (pending or completed)
    const relevantTodos = draggedTodo.completed ? completedTodos : pendingTodos;
    const draggedIndex = relevantTodos.findIndex(todo => todo.id === draggedTodo.id);
    const targetIndex = relevantTodos.findIndex(todo => todo.id === targetTodo.id);

    if (draggedIndex === -1 || targetIndex === -1) {
      return;
    }

    // Create new reordered array for the relevant section
    const newRelevantTodos = [...relevantTodos];
    const [removed] = newRelevantTodos.splice(draggedIndex, 1);
    newRelevantTodos.splice(targetIndex, 0, removed);

    // Reconstruct the full todos array maintaining the other section's order
    let newTodos;
    if (draggedTodo.completed) {
      newTodos = [...pendingTodos, ...newRelevantTodos];
    } else {
      newTodos = [...newRelevantTodos, ...completedTodos];
    }

    // Call the reorder function with the complete list
    reorderTodos(newTodos);
  };

  if (todos.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="text-6xl mb-6">🎯</div>
        <h3 className="text-2xl font-semibold text-gray-600 mb-2">All caught up!</h3>
        <p className="text-gray-500">No tasks yet. Add one above to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Pending Todos */}
      {pendingTodos.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700 flex items-center">
              <span className="w-2 h-2 bg-orange-400 rounded-full mr-3"></span>
              Pending ({pendingTodos.length})
            </h3>
            {pendingTodos.length > 1 && (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                🖱️ Drag to reorder
              </span>
            )}
          </div>
          <div>
            {pendingTodos.map((todo) => (
              <TodoItem
                key={todo.id}
                todo={todo}
                updateTodo={updateTodo}
                deleteTodo={deleteTodo}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                isDragging={draggedTodo?.id === todo.id}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed Todos */}
      {completedTodos.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-500 mb-4 flex items-center">
            <span className="w-2 h-2 bg-green-400 rounded-full mr-3"></span>
            Completed ({completedTodos.length})
          </h3>
          <div>
            {completedTodos.map((todo) => (
              <TodoItem
                key={todo.id}
                todo={todo}
                updateTodo={updateTodo}
                deleteTodo={deleteTodo}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                isDragging={draggedTodo?.id === todo.id}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TodoList;
