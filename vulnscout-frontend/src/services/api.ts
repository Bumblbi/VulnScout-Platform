import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api'; // Замените на ваш бэкенд URL

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const scanAPI = {
  // Создание задачи сканирования
  createTask: (data: {
    target: string;
    mode: 'black' | 'gray' | 'white';
    intensity: 'low' | 'medium' | 'high';
  }) => api.post('/scans', data),

  // Получение списка задач
  getTasks: () => api.get('/scans'),
  
  // Получение деталей задачи
  getTask: (id: string) => api.get(`/scans/${id}`),
  
  // Остановка задачи
  stopTask: (id: string) => api.post(`/scans/${id}/stop`),
  
  // Получение результатов сканирования
  getResults: (taskId: string) => api.get(`/results/${taskId}`),
  
  // Генерация отчета
  generateReport: (taskId: string, format: 'pdf' | 'html') => 
    api.get(`/reports/${taskId}`, { 
      params: { format },
      responseType: format === 'pdf' ? 'blob' : 'json'
    }),
};