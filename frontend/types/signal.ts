export interface AgentAnalysis {
  agent: string;
  recommendation: "BUY" | "SELL" | "NEUTRAL";
  score: number;
  reasoning: string;
  confidence: number;
}

export interface TradingSignal {
  instrument: string;
  signal: "BUY" | "SELL";
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

export interface SignalRequest {
  instrument: string;
}
