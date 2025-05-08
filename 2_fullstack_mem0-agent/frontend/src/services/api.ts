import axios from 'axios';
import supabase from './auth';

const API_URL = process.env.NODE_ENV === 'production' 
  ? 'http://backend:8000'  // Trong Docker, dùng tên service
  : 'http://localhost:25048'; // Khi phát triển local
const API_TOKEN = process.env.REACT_APP_API_TOKEN || 'mem0-fullstack-token';

// Khởi tạo Axios với config mặc định
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Thêm interceptor để tự động thêm token vào mỗi request
api.interceptors.request.use(async (config) => {
  // Ưu tiên dùng Supabase session token nếu có
  const { data } = await supabase.auth.getSession();
  
  if (data.session?.access_token) {
    config.headers['Authorization'] = `Bearer ${data.session.access_token}`;
  } else {
    // Fallback dùng API_TOKEN nếu không có session
    config.headers['Authorization'] = `Bearer ${API_TOKEN}`;
  }
  
  return config;
});

// Interface cho các requests và responses
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  user_id: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

export interface Memory {
  memory: string;
  created_at: string;
  metadata: {
    user_id: string;
  };
}

// API functions
export const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>('/api/chat', request);
  return response.data;
};

export const getSessions = async (userId: string): Promise<string[]> => {
  const response = await api.get<{sessions: string[]}>(`/api/sessions/${userId}`);
  return response.data.sessions;
};

export const getMessages = async (sessionId: string): Promise<any[]> => {
  const response = await api.get<{messages: any[]}>(`/api/messages/${sessionId}`);
  return response.data.messages;
};

export const searchMemories = async (userId: string, query: string, limit = 3): Promise<Memory[]> => {
  const response = await api.post<{memories: Memory[]}>('/api/memories/search', {
    user_id: userId, 
    query,
    limit
  });
  return response.data.memories;
};

export const clearMemories = async (userId: string): Promise<{success: boolean}> => {
  const response = await api.delete<{success: boolean}>(`/api/memories/${userId}`);
  return response.data;
};

export const healthCheck = async (): Promise<{status: string}> => {
  const response = await api.get<{status: string}>('/health');
  return response.data;
};

export default api; 