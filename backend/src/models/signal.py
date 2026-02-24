"""Pydantic models for trading signals"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class AgentAnalysis(BaseModel):
    """Analysis result from a single agent"""
    agent: str = Field(..., description="Agent name (fundamental, economic, technical, sentiment)")
    recommendation: str = Field(..., description="BUY, SELL, or NEUTRAL")
    score: float = Field(..., ge=0, le=100, description="Score from 0-100")
    reasoning: str = Field(..., description="Explanation of the recommendation")
    confidence: float = Field(..., ge=0, le=100, description="Confidence level 0-100%")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent": "technical",
                "recommendation": "BUY",
                "score": 75.0,
                "reasoning": "RSI oversold, MACD bullish crossover, Price above SMA20",
                "confidence": 75.0
            }
        }


class TradingSignal(BaseModel):
    """Complete trading signal with all analyses"""
    instrument: str = Field(..., description="Trading instrument symbol")
    signal: str = Field(..., description="BUY or SELL")
    entry_price: float = Field(..., gt=0, description="Entry price point")
    stop_loss: float = Field(..., gt=0, description="Stop-loss level")
    take_profit: float = Field(..., gt=0, description="Take-profit target")
    confidence: float = Field(..., ge=0, le=100, description="Overall confidence score 0-100%")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Signal generation timestamp")
    
    # Individual agent analyses
    fundamental_analysis: AgentAnalysis
    economic_analysis: AgentAnalysis
    technical_analysis: AgentAnalysis
    sentiment_analysis: AgentAnalysis
    
    # Metadata
    execution_time: float = Field(..., ge=0, description="Execution time in seconds")
    api_calls_made: int = Field(default=0, ge=0, description="Number of API calls made")
    
    # Additional data
    current_price: Optional[float] = Field(None, description="Current market price")
    asset_class: Optional[str] = Field(None, description="Asset class (stock, forex, commodity, crypto)")
    timeframe: Optional[str] = Field("15m", description="Signal timeframe (1m, 5m, 15m, 30m, 1h, 1D)")

    # GPT-4o plain-English narrative explaining the full decision
    ai_explanation: Optional[str] = Field(None, description="GPT-4o plain-English explanation of the signal")

    class Config:
        json_schema_extra = {
            "example": {
                "instrument": "AAPL",
                "signal": "BUY",
                "entry_price": 175.50,
                "stop_loss": 174.80,
                "take_profit": 177.20,
                "confidence": 75.0,
                "timestamp": "2026-02-12T10:30:00Z",
                "execution_time": 45.2,
                "api_calls_made": 12
            }
        }


class SignalRequest(BaseModel):
    """Request model for generating a trading signal"""
    instrument: str = Field(..., min_length=1, max_length=20, description="Instrument name or symbol")
    timeframe: Optional[str] = Field("15m", description="Signal timeframe (1m, 5m, 15m, 30m, 1h, 1D)")
    model: Optional[str] = Field("gpt-4o-mini", description="OpenAI model to use for AI explanation")

    class Config:
        json_schema_extra = {
            "example": {
                "instrument": "AAPL",
                "timeframe": "15m",
                "model": "gpt-4o-mini"
            }
        }


class SignalResponse(BaseModel):
    """Response model for signal generation"""
    success: bool = Field(..., description="Whether signal generation was successful")
    signal: Optional[TradingSignal] = Field(None, description="Generated trading signal")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    message: Optional[str] = Field(None, description="Additional message")


class UserCreate(BaseModel):
    """User registration model"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserLogin(BaseModel):
    """User login model"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
