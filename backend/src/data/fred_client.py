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
        Get GDP YoY growth rate (%).

        FRED "GDP" series returns nominal GDP in billions of dollars (e.g. 31490 = $31.49T).
        We calculate the year-over-year percentage change using 4 quarters (1 year) of lag.
        Fetches 2 years of data to guarantee at least 5 quarterly data points.

        Returns:
            YoY GDP growth rate as a percentage (e.g. 2.5 = 2.5%)
        """
        cache_key = "fred:gdp"

        def fetch_data():
            try:
                if self.fred is None:
                    logger.warning("FRED client not available, returning neutral value")
                    return 2.5  # neutral / average US growth

                # Fetch 2 years to guarantee ≥5 quarterly observations
                obs_start = datetime.now() - timedelta(days=730)
                gdp_series = self.fred.get_series(
                    self.SERIES_IDS["gdp"],
                    observation_start=obs_start.strftime("%Y-%m-%d")
                )
                gdp_series = gdp_series.dropna() if gdp_series is not None else None
                if gdp_series is not None and len(gdp_series) >= 5:
                    # GDP is quarterly — 4 periods back = 1 year ago
                    current   = float(gdp_series.iloc[-1])
                    year_ago  = float(gdp_series.iloc[-5])
                    growth    = ((current - year_ago) / year_ago) * 100
                    return round(growth, 2)
                # Fallback: not enough data — return reasonable default
                logger.warning("FRED GDP: insufficient quarterly data, using default 2.5%")
                return 2.5
            except Exception as e:
                logger.error(f"FRED GDP error: {e}")
                return 2.5

        # Cache for 1 day
        return cache_manager.get_or_set(cache_key, fetch_data, ttl=86400)
    
    def get_inflation_rate(self, start_date: Optional[datetime] = None) -> float:
        """
        Get YoY inflation rate (CPI % change).

        FRED "CPIAUCSL" returns the raw CPI index level (e.g. 326 is the index, not 326%).
        CPI data is published with a ~6-week lag so a 365-day window can return only 11
        monthly observations, causing the old code to fall back to the raw index level.
        We now fetch 15 months to always guarantee ≥13 monthly data points.

        Returns:
            YoY CPI inflation rate as a percentage (e.g. 2.8 = 2.8%)
        """
        cache_key = "fred:cpi"

        def fetch_data():
            try:
                if self.fred is None:
                    logger.warning("FRED client not available, returning neutral value")
                    return 2.5  # neutral / average US inflation

                # Fetch 15 months to guarantee ≥13 monthly observations despite CPI lag
                obs_start = datetime.now() - timedelta(days=456)
                cpi_series = self.fred.get_series(
                    self.SERIES_IDS["cpi"],
                    observation_start=obs_start.strftime("%Y-%m-%d")
                )
                cpi_series = cpi_series.dropna() if cpi_series is not None else None
                if cpi_series is not None and len(cpi_series) >= 13:
                    current   = float(cpi_series.iloc[-1])
                    year_ago  = float(cpi_series.iloc[-13])
                    inflation_rate = ((current - year_ago) / year_ago) * 100
                    return round(inflation_rate, 2)
                elif cpi_series is not None and len(cpi_series) >= 2:
                    # Fewer points than expected — calculate with what we have
                    current  = float(cpi_series.iloc[-1])
                    earliest = float(cpi_series.iloc[0])
                    months   = max(1, len(cpi_series) - 1)
                    annualised = ((current - earliest) / earliest) * (12 / months) * 100
                    return round(annualised, 2)
                logger.warning("FRED CPI: insufficient data, using default 2.5%")
                return 2.5
            except Exception as e:
                logger.error(f"FRED CPI error: {e}")
                return 2.5

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
