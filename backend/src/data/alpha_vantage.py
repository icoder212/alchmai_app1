"""Alpha Vantage API client"""
import requests
import time
import pandas as pd
from typing import Dict, Optional, List
from functools import wraps
from datetime import datetime, timedelta

from src.config import settings
from src.utils.logger import get_logger
from .cache import cache_manager

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter for Alpha Vantage API (5 calls per minute)"""
    
    def __init__(self, calls_per_minute: int = 5):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_called = 0.0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_called
        left_to_wait = self.min_interval - elapsed
        if left_to_wait > 0:
            time.sleep(left_to_wait)
        self.last_called = time.time()


# Global rate limiter
rate_limiter = RateLimiter(calls_per_minute=5)


def rate_limit(func):
    """Decorator to apply rate limiting"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        rate_limiter.wait_if_needed()
        return func(*args, **kwargs)
    return wrapper


class AlphaVantageClient:
    """Client for Alpha Vantage API"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.alpha_vantage_key
    
    @rate_limit
    def _make_request(self, params: Dict) -> Dict:
        """
        Make API request with rate limiting and error handling
        
        Args:
            params: Request parameters
            
        Returns:
            API response as dictionary
        """
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key is required. "
                "Please set ALPHA_VANTAGE_KEY in your .env file."
            )
        params["apikey"] = self.api_key
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage API Error: {data['Error Message']}")
            if "Note" in data:
                raise Exception(f"Alpha Vantage Rate Limit: {data['Note']}")
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage API request failed: {e}")
            raise
    
    def get_intraday_data(
        self,
        symbol: str,
        interval: str = "15min",
        outputsize: str = "compact"
    ) -> pd.DataFrame:
        """
        Get intraday time series data
        
        Args:
            symbol: Stock symbol
            interval: Time interval (1min, 5min, 15min, 30min, 60min)
            outputsize: compact (last 100) or full
            
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"alpha_vantage:intraday:{symbol}:{interval}"
        
        def fetch_data():
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize
            }
            
            data = self._make_request(params)
            
            # Parse time series data
            time_series_key = f"Time Series ({interval})"
            if time_series_key not in data:
                raise Exception(f"No time series data in response for {symbol}")
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df = pd.DataFrame.from_dict(time_series, orient="index")
            df.index = pd.to_datetime(df.index)
            df.columns = ["open", "high", "low", "close", "volume"]
            df = df.astype(float)
            df = df.sort_index()
            
            return df
        
        # Use cache (5 minute TTL for 15-min data)
        ttl = 300 if interval == "15min" else 60
        df = cache_manager.get_or_set(cache_key, fetch_data, ttl)
        
        return df
    
    def get_news_sentiment(self, symbol: str, limit: int = 50) -> List[Dict]:
        """
        Get news sentiment for a symbol
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of articles
            
        Returns:
            List of news articles with sentiment
        """
        cache_key = f"alpha_vantage:news:{symbol}:{limit}"
        
        def fetch_data():
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,
                "limit": limit
            }
            
            data = self._make_request(params)
            
            if "feed" not in data:
                return []
            
            return data["feed"]
        
        # Cache for 1 hour (news doesn't change frequently)
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=3600)
    
    def get_company_overview(self, symbol: str) -> Dict:
        """
        Get company overview and fundamentals
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Company overview data
        """
        cache_key = f"alpha_vantage:overview:{symbol}"
        
        def fetch_data():
            params = {
                "function": "OVERVIEW",
                "symbol": symbol
            }
            
            return self._make_request(params)
        
        # Cache for 1 day (company data doesn't change frequently)
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)


# Global client instance
alpha_vantage_client = AlphaVantageClient()
