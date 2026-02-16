import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface SignalRequest {
  instrument: string;
}

export interface AgentAnalysis {
  agent: string;
  recommendation: string;
  score: number;
  reasoning: string;
  confidence: number;
}

export interface TradingSignal {
  instrument: string;
  signal: string;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  confidence: number;
  timestamp: string;
  fundamental_analysis: AgentAnalysis;
  economic_analysis: AgentAnalysis;
  technical_analysis: AgentAnalysis;
  sentiment_analysis: AgentAnalysis;
  execution_time: number;
  api_calls_made: number;
  current_price?: number;
  asset_class?: string;
}

export interface SignalResponse {
  success: boolean;
  signal?: TradingSignal;
  error?: string;
  message?: string;
}

export const api = {
  // Authentication
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);
    const response = await apiClient.post("/auth/login", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  register: async (email: string, password: string) => {
    const response = await apiClient.post("/auth/register", {
      email,
      password,
    });
    return response.data;
  },

  // Signals
  generateSignal: async (instrument: string): Promise<SignalResponse> => {
    const response = await apiClient.post<SignalResponse>("/signal", {
      instrument,
    });
    return response.data;
  },

  getSignals: async (skip: number = 0, limit: number = 20): Promise<TradingSignal[]> => {
    const response = await apiClient.get<TradingSignal[]>("/signals", {
      params: { skip, limit },
    });
    return response.data;
  },

  getSignal: async (signalId: number): Promise<TradingSignal> => {
    const response = await apiClient.get<TradingSignal>(`/signals/${signalId}`);
    return response.data;
  },

  // Signal history
  getSignalHistory: async (limit: number = 20, instrument?: string) => {
    try {
      const params = new URLSearchParams({ limit: limit.toString() });
      if (instrument) params.append('instrument', instrument);
      
      const response = await apiClient.get<TradingSignal[]>(`/history?${params}`);
      return {
        success: true,
        signals: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to fetch signal history',
        signals: []
      };
    }
  },
};

export default apiClient;
