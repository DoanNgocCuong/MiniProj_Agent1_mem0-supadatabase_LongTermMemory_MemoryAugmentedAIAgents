import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TOKEN = process.env.REACT_APP_API_TOKEN || 'mem0-fullstack-token';

// Khởi tạo Axios với config mặc định
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_TOKEN}`
  }
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