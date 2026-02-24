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
  timeframe?: string;
  model?: string;
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
  timeframe?: string;
  ai_explanation?: string;
}

export interface ChartCandle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface SignalResponse {
  success: boolean;
  signal?: TradingSignal;
  error?: string;
  message?: string;
}

export interface AssetTicker {
  symbol: string;
  price: number;
  change: number;
  change_type: 'positive' | 'negative';
  timestamp: string;
}

export interface PortfolioSummary {
  total_value: number;
  change_percent: number;
  change_type: 'positive' | 'negative';
  has_portfolio: boolean;
  timestamp: string;
}

export interface ActiveSignalsResponse {
  total: number;
  buy: number;
  hold: number;
  sell: number;
  timestamp: string;
}

export interface PerformanceMetrics {
  win_rate: number;
  win_rate_change: number;
  avg_return: number;
  avg_return_change: number;
  trades_per_month: number;
  trades_per_month_change: number;
  period: string;
  timestamp: string;
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
  generateSignal: async (instrument: string, timeframe: string = "15m", model: string = "gpt-4o-mini"): Promise<SignalResponse> => {
    const response = await apiClient.post<SignalResponse>("/signal", {
      instrument,
      timeframe,
      model,
    });
    return response.data;
  },

  getChartData: async (
    symbol: string,
    timeframe: string = "15m",
    window: string = "1D",
    assetClass: string = "stock"
  ): Promise<ChartCandle[]> => {
    try {
      const response = await apiClient.get<ChartCandle[]>(
        `/market/chart/${symbol}`,
        { params: { timeframe, window, asset_class: assetClass } }
      );
      return response.data;
    } catch (error: any) {
      console.error("Failed to fetch chart data:", error);
      return [];
    }
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

  // Market tickers
  getMarketTickers: async (): Promise<AssetTicker[]> => {
    try {
      const response = await apiClient.get<AssetTicker[]>("/market/tickers");
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch market tickers:', error);
      return [];
    }
  },

  // Portfolio summary
  getPortfolioSummary: async (): Promise<PortfolioSummary> => {
    try {
      const response = await apiClient.get<PortfolioSummary>("/portfolio/summary");
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch portfolio summary:', error);
      return {
        total_value: 0,
        change_percent: 0,
        change_type: 'positive',
        has_portfolio: false,
        timestamp: new Date().toISOString(),
      };
    }
  },

  // Active signals
  getActiveSignals: async (): Promise<ActiveSignalsResponse> => {
    try {
      const response = await apiClient.get<ActiveSignalsResponse>("/active");
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch active signals:', error);
      return {
        total: 0,
        buy: 0,
        hold: 0,
        sell: 0,
        timestamp: new Date().toISOString(),
      };
    }
  },

  // Performance metrics
  getPerformanceMetrics: async (): Promise<PerformanceMetrics> => {
    try {
      const response = await apiClient.get<PerformanceMetrics>("/performance/metrics");
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch performance metrics:', error);
      return {
        win_rate: 0,
        win_rate_change: 0,
        avg_return: 0,
        avg_return_change: 0,
        trades_per_month: 0,
        trades_per_month_change: 0,
        period: 'last_30_days',
        timestamp: new Date().toISOString(),
      };
    }
  },
};

export default apiClient;
