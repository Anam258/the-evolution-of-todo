'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

// Define TypeScript interfaces
interface Task {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newTask, setNewTask] = useState({ title: '', description: '' });
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [editForm, setEditForm] = useState({ title: '', description: '' });

  // Fetch tasks on component mount
  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/tasks');
      if (response.data?.tasks) {
        setTasks(response.data.tasks);
      } else {
        setTasks(response);
      }
      setError(null);
    } catch (err) {
      setError('Failed to load tasks. Please try again.');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;

    try {
      const response = await apiClient.post('/tasks', {
        title: newTask.title,
        description: newTask.description || null,
        is_completed: false
      });

      setTasks([response.data || response, ...tasks]);
      setNewTask({ title: '', description: '' });
    } catch (err) {
      setError('Failed to create task. Please try again.');
      console.error('Error creating task:', err);
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      const updatedTask = { ...task, is_completed: !task.is_completed };
      const response = await apiClient.patch(`/tasks/${task.id}`, {
        is_completed: !task.is_completed
      });

      setTasks(tasks.map(t =>
        t.id === task.id ? response.data || response : t
      ));
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    }
  };

  const handleEditClick = (task: Task) => {
    setEditingTask(task);
    setEditForm({
      title: task.title,
      description: task.description || ''
    });
  };

  const handleUpdateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTask || !editForm.title.trim()) return;

    try {
      const response = await apiClient.put(`/tasks/${editingTask.id}`, {
        title: editForm.title,
        description: editForm.description || null
      });

      setTasks(tasks.map(t =>
        t.id === editingTask.id ? response.data || response : t
      ));
      setEditingTask(null);
      setEditForm({ title: '', description: '' });
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      await apiClient.delete(`/tasks/${taskId}`);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (err) {
      setError('Failed to delete task. Please try again.');
      console.error('Error deleting task:', err);
    }
  };

  const pendingTasks = tasks.filter(task => !task.is_completed);
  const completedTasks = tasks.filter(task => task.is_completed);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 mb-2">
            Nuralyx Flow
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Intelligent task management with authentication
          </p>
        </header>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Total Tasks</h3>
            <p className="text-3xl font-bold mt-2">{tasks.length}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Pending</h3>
            <p className="text-3xl font-bold text-orange-500 mt-2">{pendingTasks.length}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Completed</h3>
            <p className="text-3xl font-bold text-green-500 mt-2">{completedTasks.length}</p>
          </div>
        </div>

        {/* Create Task Form */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Create New Task</h2>
          <form onSubmit={handleCreateTask} className="space-y-4">
            <div>
              <input
                type="text"
                value={newTask.title}
                onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                placeholder="Task title..."
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                required
              />
            </div>
            <div>
              <textarea
                value={newTask.description}
                onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                placeholder="Task description (optional)..."
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                rows={2}
              />
            </div>
            <button
              type="submit"
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-lg hover:opacity-90 transition-opacity focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
            >
              Add Task
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 dark:bg-red-900/20 dark:border-red-800 dark:text-red-200">
            {error}
          </div>
        )}

        {/* Tasks Sections */}
        <div className="space-y-10">
          {/* Pending Tasks */}
          <section>
            <h2 className="text-2xl font-semibold mb-6 flex items-center text-gray-800 dark:text-white">
              <span className="mr-3">📋</span> Pending ({pendingTasks.length})
            </h2>
            {loading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-300">Loading tasks...</p>
              </div>
            ) : pendingTasks.length === 0 ? (
              <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
                <div className="text-5xl mb-4">🎉</div>
                <h3 className="text-xl font-medium text-gray-800 dark:text-white mb-2">All caught up!</h3>
                <p className="text-gray-600 dark:text-gray-300">No pending tasks. Great job!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pendingTasks.map((task) => (
                  <div
                    key={task.id}
                    className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <input
                        type="checkbox"
                        checked={task.is_completed}
                        onChange={() => handleToggleComplete(task)}
                        className="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="flex space-x-2 ml-2">
                        <button
                          onClick={() => handleEditClick(task)}
                          className="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
                          title="Edit task"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                          title="Delete task"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                    <h3 className="font-medium text-gray-800 dark:text-white mb-2">{task.title}</h3>
                    {task.description && (
                      <p className="text-gray-600 dark:text-gray-300 text-sm mb-3">{task.description}</p>
                    )}
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Created: {new Date(task.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Completed Tasks */}
          <section>
            <h2 className="text-2xl font-semibold mb-6 flex items-center text-gray-800 dark:text-white">
              <span className="mr-3">✅</span> Completed ({completedTasks.length})
            </h2>
            {completedTasks.length === 0 ? (
              <div className="text-center py-8 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
                <p className="text-gray-600 dark:text-gray-300">No completed tasks yet. Keep going!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {completedTasks.map((task) => (
                  <div
                    key={task.id}
                    className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-5 opacity-75"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <input
                        type="checkbox"
                        checked={task.is_completed}
                        onChange={() => handleToggleComplete(task)}
                        className="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="flex space-x-2 ml-2">
                        <button
                          onClick={() => handleEditClick(task)}
                          className="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
                          title="Edit task"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                          title="Delete task"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                    <h3 className="font-medium text-gray-800 dark:text-white mb-2 line-through">{task.title}</h3>
                    {task.description && (
                      <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-through">{task.description}</p>
                    )}
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Completed: {new Date(task.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Edit Task Modal */}
        {editingTask && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg max-w-md w-full p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Edit Task</h2>
              <form onSubmit={handleUpdateTask} className="space-y-4">
                <div>
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    required
                  />
                </div>
                <div>
                  <textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    rows={3}
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setEditingTask(null);
                      setEditForm({ title: '', description: '' });
                    }}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}