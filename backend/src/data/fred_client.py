"""FRED (Federal Reserve Economic Data) API client"""
from fredapi import Fred
from datetime import datetime, timedelta
from typing import Dict, Optional

from src.config import settings
from src.utils.logger import get_logger
from .cache import cache_manager

logger = get_logger(__name__)


class FREDClient:
    """Client for FRED API (free, no key required for public data)"""
    
    def __init__(self):
        """Initialize FRED client (no API key required for basic public data)"""
        # Note: fredapi requires an API key, but we'll handle gracefully if not available
        # For production, get a free key from https://fred.stlouisfed.org/docs/api/api_key.html
        try:
            # Try to use API key if available
            api_key = getattr(settings, 'fred_api_key', None) or "demo_key"
            self.fred = Fred(api_key=api_key)
        except Exception as e:
            logger.warning(f"FRED API initialization failed: {e}. Using fallback values.")
            self.fred = None
    
    # FRED series IDs
    SERIES_IDS = {
        "gdp": "GDP",
        "cpi": "CPIAUCSL",
        "unemployment": "UNRATE",
        "fed_rate": "DFF",
        "inflation": "CPIAUCSL",  # Same as CPI
    }
    
    def get_gdp_growth(self, start_date: Optional[datetime] = None) -> float:
        """
        Get GDP growth rate
        
        Args:
            start_date: Start date for data (default: 1 year ago)
            
        Returns:
            Latest GDP value
        """
        cache_key = "fred:gdp"
        
        def fetch_data():
            try:
                if self.fred is None:
                    logger.warning("FRED client not available, returning neutral value")
                    return 0.0
                
                if start_date is None:
                    observation_start = datetime.now() - timedelta(days=365)
                else:
                    observation_start = start_date
                
                gdp_series = self.fred.get_series(
                    self.SERIES_IDS["gdp"],
                    observation_start=observation_start.strftime("%Y-%m-%d")
                )
                if gdp_series is not None and len(gdp_series) > 0:
                    return float(gdp_series.iloc[-1])
                return 0.0
            except Exception as e:
                logger.error(f"FRED GDP error: {e}")
                return 0.0
        
        # Cache for 1 day
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)
    
    def get_inflation_rate(self, start_date: Optional[datetime] = None) -> float:
        """
        Get inflation rate (CPI)
        
        Args:
            start_date: Start date for data (default: 1 year ago)
            
        Returns:
            Latest CPI value or YoY inflation rate
        """
        cache_key = "fred:cpi"
        
        def fetch_data():
            try:
                if self.fred is None:
                    logger.warning("FRED client not available, returning neutral value")
                    return 0.0
                
                if start_date is None:
                    observation_start = datetime.now() - timedelta(days=365)
                else:
                    observation_start = start_date
                
                cpi_series = self.fred.get_series(
                    self.SERIES_IDS["cpi"],
                    observation_start=observation_start.strftime("%Y-%m-%d")
                )
                if cpi_series is not None and len(cpi_series) > 0:
                    # Calculate YoY inflation rate
                    if len(cpi_series) >= 12:
                        current = float(cpi_series.iloc[-1])
                        year_ago = float(cpi_series.iloc[-12])
                        inflation_rate = ((current - year_ago) / year_ago) * 100
                        return inflation_rate
                    return float(cpi_series.iloc[-1])
                return 0.0
            except Exception as e:
                logger.error(f"FRED CPI error: {e}")
                return 0.0
        
        # Cache for 1 day
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)
    
    def get_unemployment_rate(self, start_date: Optional[datetime] = None) -> float:
        """
        Get unemployment rate
        
        Args:
            start_date: Start date for data (default: 1 year ago)
            
        Returns:
            Latest unemployment rate
        """
        cache_key = "fred:unemployment"
        
        def fetch_data():
            try:
                if self.fred is None:
                    logger.warning("FRED client not available, returning neutral value")
                    return 0.0
                
                if start_date is None:
                    observation_start = datetime.now() - timedelta(days=365)
                else:
                    observation_start = start_date
                
                unemployment_series = self.fred.get_series(
                    self.SERIES_IDS["unemployment"],
                    observation_start=observation_start.strftime("%Y-%m-%d")
                )
                if unemployment_series is not None and len(unemployment_series) > 0:
                    return float(unemployment_series.iloc[-1])
                return 0.0
            except Exception as e:
                logger.error(f"FRED unemployment error: {e}")
                return 0.0
        
        # Cache for 1 day
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)
    
    def get_fed_funds_rate(self, start_date: Optional[datetime] = None) -> float:
        """
        Get Federal Funds Rate
        
        Args:
            start_date: Start date for data (default: 1 year ago)
            
        Returns:
            Latest Fed funds rate
        """
        cache_key = "fred:fed_rate"
        
        def fetch_data():
            try:
                if self.fred is None:
                    logger.warning("FRED client not available, returning neutral value")
                    return 0.0
                
                if start_date is None:
                    observation_start = datetime.now() - timedelta(days=365)
                else:
                    observation_start = start_date
                
                fed_rate_series = self.fred.get_series(
                    self.SERIES_IDS["fed_rate"],
                    observation_start=observation_start.strftime("%Y-%m-%d")
                )
                if fed_rate_series is not None and len(fed_rate_series) > 0:
                    return float(fed_rate_series.iloc[-1])
                return 0.0
            except Exception as e:
                logger.error(f"FRED Fed rate error: {e}")
                return 0.0
        
        # Cache for 1 day
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)
    
    def get_all_indicators(self) -> Dict[str, float]:
        """
        Get all economic indicators at once
        
        Returns:
            Dictionary with all indicators
        """
        return {
            "gdp_growth": self.get_gdp_growth(),
            "inflation": self.get_inflation_rate(),
            "unemployment": self.get_unemployment_rate(),
            "fed_rate": self.get_fed_funds_rate(),
        }


# Global client instance
fred_client = FREDClient()
