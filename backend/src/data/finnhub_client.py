"""Finnhub API client"""
import finnhub
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.config import settings
from src.utils.logger import get_logger
from .cache import cache_manager

logger = get_logger(__name__)


class FinnhubClient:
    """Client for Finnhub API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.finnhub_key
        self.client = finnhub.Client(api_key=self.api_key) if self.api_key else None
    
    def _validate_client(self):
        """Validate that API key and client are available"""
        if not self.api_key or not self.client:
            raise ValueError(
                "Finnhub API key is required. "
                "Please set FINNHUB_KEY in your .env file."
            )
    
    def get_quote(self, symbol: str) -> Dict:
        """
        Get real-time quote
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Quote data (current price, high, low, open, etc.)
        """
        cache_key = f"finnhub:quote:{symbol}"
        
        def fetch_data():
            self._validate_client()
            try:
                quote = self.client.quote(symbol)
                return quote
            except Exception as e:
                logger.error(f"Finnhub quote error for {symbol}: {e}")
                raise
        
        # Cache for 1 minute (real-time data)
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=60)
    
    def get_company_profile(self, symbol: str) -> Dict:
        """
        Get company profile
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Company profile data
        """
        cache_key = f"finnhub:profile:{symbol}"
        
        def fetch_data():
            self._validate_client()
            try:
                profile = self.client.company_profile2(symbol=symbol)
                return profile
            except Exception as e:
                logger.error(f"Finnhub profile error for {symbol}: {e}")
                raise
        
        # Cache for 1 day
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)
    
    def get_company_financials(self, symbol: str, metric: str = "all") -> Dict:
        """
        Get company basic financials
        
        Args:
            symbol: Stock symbol
            metric: Financial metric (all, price, valuation, etc.)
            
        Returns:
            Financial data
        """
        cache_key = f"finnhub:financials:{symbol}:{metric}"
        
        def fetch_data():
            self._validate_client()
            try:
                financials = self.client.company_basic_financials(symbol, metric)
                return financials
            except Exception as e:
                logger.error(f"Finnhub financials error for {symbol}: {e}")
                raise
        
        # Cache for 1 day
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)
    
    def get_earnings(self, symbol: str, limit: int = 5) -> List[Dict]:
        """
        Get company earnings data
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of earnings reports
            
        Returns:
            List of earnings data
        """
        cache_key = f"finnhub:earnings:{symbol}:{limit}"
        
        def fetch_data():
            self._validate_client()
            try:
                earnings = self.client.company_earnings(symbol, limit=limit)
                # Handle both dict and list responses from Finnhub API
                if isinstance(earnings, dict):
                    return earnings.get("earnings", [])
                elif isinstance(earnings, list):
                    return earnings
                else:
                    logger.warning(f"Unexpected earnings format for {symbol}: {type(earnings)}")
                    return []
            except Exception as e:
                logger.error(f"Finnhub earnings error for {symbol}: {e}")
                raise
        
        # Cache for 1 day
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)
    
    def get_company_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        Get company news
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            List of news articles
        """
        cache_key = f"finnhub:news:{symbol}:{days}"
        
        def fetch_data():
            self._validate_client()
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                news = self.client.company_news(
                    symbol,
                    _from=start_date.strftime("%Y-%m-%d"),
                    to=end_date.strftime("%Y-%m-%d")
                )
                return news[:50]  # Limit to 50 articles
            except Exception as e:
                logger.error(f"Finnhub news error for {symbol}: {e}")
                raise
        
        # Cache for 1 hour
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=3600)
    
    def get_stock_candles(
        self,
        symbol: str,
        resolution: str = "15",
        days: int = 1
    ) -> Dict:
        """
        Get stock candle data
        
        Args:
            symbol: Stock symbol
            resolution: Time resolution (1, 5, 15, 30, 60, D, W, M)
            days: Number of days of data
            
        Returns:
            Candle data (o, h, l, c, v, t)
        """
        cache_key = f"finnhub:candles:{symbol}:{resolution}:{days}"
        
        def fetch_data():
            self._validate_client()
            try:
                end_time = int(time.time())
                start_time = end_time - (days * 86400)
                
                candles = self.client.stock_candles(
                    symbol,
                    resolution,
                    start_time,
                    end_time
                )
                return candles
            except Exception as e:
                logger.error(f"Finnhub candles error for {symbol}: {e}")
                raise
        
        # Cache for 5 minutes for 15-min data
        ttl = 300 if resolution == "15" else 60
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=ttl)


# Global client instance
finnhub_client = FinnhubClient()
