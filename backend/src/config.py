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
    openai_model: str = "gpt-4o-mini"  # Cheaper for POC
    temperature: float = 0.3
    
    # Agent Weights
    fundamental_weight: float = 0.20
    economic_weight: float = 0.15
    technical_weight: float = 0.40
    sentiment_weight: float = 0.25
    
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
