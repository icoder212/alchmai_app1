"""yfinance backup data source"""
import yfinance as yf
from typing import Dict, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class YFinanceBackup:
    """Backup data source using yfinance (free, unofficial)"""
    
    def get_ticker_info(self, symbol: str) -> Dict:
        """
        Get ticker information as backup
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Ticker info dictionary
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract relevant fields - include multiple price fields for compatibility
            return {
                "symbol": symbol,
                "name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "revenue": info.get("totalRevenue"),
                "revenueGrowth": info.get("revenueGrowth"),        # e.g. 0.12 = 12% YoY growth
                "profit_margin": info.get("profitMargins"),        # e.g. 0.24 = 24%
                "earnings_growth": info.get("earningsGrowth"),     # e.g. 0.18 = 18% YoY EPS growth
                "debt_to_equity": info.get("debtToEquity"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "regularMarketPrice": info.get("regularMarketPrice"),
                "currentPrice": info.get("currentPrice"),
                "previousClose": info.get("previousClose"),
            }
        except Exception as e:
            logger.error(f"yfinance error for {symbol}: {e}")
            return {}
    
    def get_historical_data(
        self,
        symbol: str,
        period: str = "1d",
        interval: str = "15m"
    ) -> Optional[object]:
        """
        Get historical data as backup
        
        Args:
            symbol: Stock symbol
            period: Period (1d, 5d, 1mo, etc.)
            interval: Interval (1m, 5m, 15m, 1h, etc.)
            
        Returns:
            DataFrame with historical data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            return df
        except Exception as e:
            logger.error(f"yfinance historical data error for {symbol}: {e}")
            return None


# Global backup instance
yfinance_backup = YFinanceBackup()
