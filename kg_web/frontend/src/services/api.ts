import axios from 'axios';
import { Config, Task, KnowledgeGraphData, SampleData } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.config?.url, error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // 获取配置
  getConfig: (): Promise<Config> => {
    return api.get('/api/config').then(res => res.data);
  },

  // 更新配置
  updateConfig: (config: Config): Promise<{ status: string; message: string }> => {
    return api.post('/api/config', config).then(res => res.data);
  },

  // 获取示例数据
  getSampleData: (): Promise<SampleData> => {
    return api.get('/api/sample-data').then(res => res.data);
  },

  // 创建任务
  createTask: (textInput: { text: string }): Promise<{ task_id: string; message: string }> => {
    // 后端期望的是 texts 数组格式
    const payload = { texts: [textInput.text] };
    return api.post('/api/tasks/create', payload).then(res => res.data);
  },

  // 获取任务状态
  getTaskStatus: (taskId: string): Promise<Task> => {
    return api.get(`/api/tasks/${taskId}`).then(res => res.data);
  },

  // 获取所有任务
  getAllTasks: (): Promise<{ tasks: Task[] }> => {
    return api.get('/api/tasks').then(res => res.data);
  },

  // 获取知识图谱数据
  getKnowledgeGraph: (taskId: string): Promise<KnowledgeGraphData> => {
    return api.get(`/api/knowledge-graph/${taskId}`).then(res => res.data);
  },

  // 获取可视化图片URL
  getVisualizationUrl: (taskId: string): string => {
    return `${API_BASE_URL}/api/visualization/${taskId}`;
  },

  // 删除任务
  deleteTask: (taskId: string): Promise<{ status: string; message: string }> => {
    return api.delete(`/api/tasks/${taskId}`).then(res => res.data);
  },

  // 健康检查
  healthCheck: (): Promise<{ message: string; version: string }> => {
    return api.get('/').then(res => res.data);
  },
};