import api from './api';

export const authService = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  refreshToken: async (refreshToken) => {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
};

export const taskService = {
  getTasks: async () => {
    const response = await api.get('/tasks/');
    return response.data;
  },

  getTask: async (taskId) => {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },

  createTask: async (taskData) => {
    const response = await api.post('/tasks/', taskData);
    return response.data;
  },

  updateTask: async (taskId, taskData) => {
    const response = await api.put(`/tasks/${taskId}`, taskData);
    return response.data;
  },

  deleteTask: async (taskId) => {
    const response = await api.delete(`/tasks/${taskId}`);
    return response.data;
  },

  executeTask: async (taskId, parameters = {}) => {
    const response = await api.post(`/tasks/${taskId}/execute`, {
      task_id: taskId,
      parameters,
    });
    return response.data;
  },

  getTaskExecutions: async (taskId) => {
    const response = await api.get(`/tasks/${taskId}/executions`);
    return response.data;
  },

  getExecution: async (executionId) => {
    const response = await api.get(`/tasks/executions/${executionId}`);
    return response.data;
  },
};

export const aiService = {
  processPrompt: async (prompt, context = {}) => {
    const response = await api.post('/ai/prompt', { prompt, context });
    return response.data;
  },

  generateTask: async (prompt) => {
    const response = await api.post('/ai/generate-task', { prompt });
    return response.data;
  },

  optimizeScript: async (scriptContent, language = 'python') => {
    const response = await api.post('/ai/optimize-script', {
      script_content: scriptContent,
      language,
    });
    return response.data;
  },
};
