"""Configuration settings for the trading signal system"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    alpha_vantage_key: Optional[str] = None
    finnhub_key: Optional[str] = None
    fred_api_key: Optional[str] = None
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # Database
    database_url: str = "sqlite:///./trading_signals.db"
    
    # LLM Settings
    openai_model: str = "gpt-4o"  # Full GPT-4o for best reasoning quality
    temperature: float = 0.3
    
    # Agent Weights — calibrated for 15-minute intraday signals.
    # Technical dominates: price action & momentum are the only real-time signal
    #   on a 15-min chart (CMT Level II; Lo & MacKinlay 2001).
    # Sentiment is second: news breaks intraday and moves prices immediately.
    # Fundamental & Economic are directional filters only — their data is
    #   quarterly/monthly and carries no intraday edge on its own.
    fundamental_weight: float = 0.10   # Quarterly data — directional bias filter
    economic_weight: float = 0.10      # Monthly/static macro — backdrop filter
    technical_weight: float = 0.55     # Real-time 15-min price action (primary)
    sentiment_weight: float = 0.25     # Intraday news flow — immediate price impact
    
    # Thresholds
    min_confidence: float = 50.0
    
    # JWT Settings
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    # API Settings
    max_execution_time: int = 90  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
