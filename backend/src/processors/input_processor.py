"""Input processor for normalizing and validating user input"""
from typing import Dict, Optional
from datetime import datetime

from src.utils.helpers import validate_symbol, normalize_symbol, get_asset_class
from src.utils.logger import get_logger
from src.data.finnhub_client import finnhub_client
from src.data.alpha_vantage import alpha_vantage_client

logger = get_logger(__name__)


class InputProcessor:
    """Processes and validates user input for trading signals"""
    
    def process(self, user_input: str) -> Dict:
        """
        Process user input: validate, normalize, and fetch current price
        
        Args:
            user_input: User-provided instrument name (e.g., "Apple", "AAPL", "Gold")
            
        Returns:
            Dictionary with processed data:
            {
                "symbol": str,
                "asset_class": str,
                "current_price": float,
                "timestamp": datetime
            }
        """
        logger.info(f"Processing input: {user_input}")
        
        # Normalize symbol
        symbol = normalize_symbol(user_input)
        
        if not symbol:
            raise ValueError(f"Invalid instrument name: {user_input}")
        
        # Validate symbol format
        if not validate_symbol(symbol):
            raise ValueError(f"Invalid symbol format: {symbol}")
        
        # Determine asset class
        asset_class = get_asset_class(symbol)
        
        # Fetch current market price
        current_price = self._fetch_current_price(symbol, asset_class)
        
        if current_price is None or current_price <= 0:
            raise ValueError(f"Could not fetch current price for {symbol}")
        
        logger.info(
            f"Processed input: {user_input} -> {symbol} "
            f"({asset_class}) @ ${current_price:.2f}"
        )
        
        return {
            "symbol": symbol,
            "asset_class": asset_class,
            "current_price": current_price,
            "timestamp": datetime.utcnow()
        }
    
    def _fetch_current_price(self, symbol: str, asset_class: str) -> Optional[float]:
        """
        Fetch current market price from available sources
        
        Args:
            symbol: Normalized symbol
            asset_class: Asset class (stock, forex, commodity, crypto)
            
        Returns:
            Current price or None
        """
        # Try Finnhub first (most reliable)
        try:
            quote = finnhub_client.get_quote(symbol)
            if quote and "c" in quote and quote["c"] > 0:
                return float(quote["c"])
        except Exception as e:
            logger.warning(f"Finnhub price fetch failed for {symbol}: {e}")
        
        # Try Alpha Vantage as backup
        try:
            df = alpha_vantage_client.get_intraday_data(symbol, interval="15min", outputsize="compact")
            if not df.empty:
                return float(df["close"].iloc[-1])
        except Exception as e:
            logger.warning(f"Alpha Vantage price fetch failed for {symbol}: {e}")
        
        # Try yfinance as final fallback (works for stocks, forex, commodities)
        logger.info(f"Trying yfinance fallback for {symbol} (asset_class: {asset_class})")
        try:
            from src.data.yfinance_backup import yfinance_backup
            
            # Convert symbol to yfinance format if needed
            yf_symbol = self._convert_to_yfinance_symbol(symbol, asset_class)
            logger.info(f"Converted {symbol} to yfinance symbol: {yf_symbol}")
            
            # Try ticker.info first (works for most stocks)
            ticker_info = yfinance_backup.get_ticker_info(yf_symbol)
            if ticker_info:
                # Try different price fields
                price = (
                    ticker_info.get('regularMarketPrice') or
                    ticker_info.get('currentPrice') or
                    ticker_info.get('previousClose')
                )
                if price and price > 0:
                    logger.info(f"yfinance price from ticker.info successful for {yf_symbol}: ${price}")
                    return float(price)
                else:
                    logger.debug(f"yfinance: ticker_info exists but no valid price for {yf_symbol}")
            
            # Fallback: Use historical data to get latest close price (works for futures/commodities)
            logger.info(f"Trying yfinance historical data for {yf_symbol}")
            hist_data = yfinance_backup.get_historical_data(yf_symbol, period="1d", interval="1d")
            if hist_data is not None and not hist_data.empty:
                latest_close = hist_data['Close'].iloc[-1]
                if latest_close and latest_close > 0:
                    logger.info(f"yfinance price from history successful for {yf_symbol}: ${latest_close}")
                    return float(latest_close)
                else:
                    logger.warning(f"yfinance: historical data has invalid close price for {yf_symbol}")
            else:
                logger.warning(f"yfinance: historical data is None or empty for {yf_symbol}")
                
        except Exception as e:
            logger.error(f"yfinance price fetch exception for {symbol}: {e}", exc_info=True)
        
        # If all sources fail, return None
        logger.error(f"Could not fetch price for {symbol} from any source")
        return None
    
    def _convert_to_yfinance_symbol(self, symbol: str, asset_class: str) -> str:
        """
        Convert normalized symbol to yfinance format
        
        Args:
            symbol: Normalized symbol (e.g., "XAUUSD", "AAPL")
            asset_class: Asset class
            
        Returns:
            yfinance-compatible symbol
        """
        # Commodities: Special mappings - CHECK FIRST!
        commodity_map = {
            "XAUUSD": "GC=F",  # Gold futures
            "XAGUSD": "SI=F",  # Silver futures
            "CL": "CL=F",      # Crude oil futures
            "NG": "NG=F",      # Natural gas futures
        }
        if symbol in commodity_map:
            return commodity_map[symbol]
        
        # Forex pairs: Add =X suffix
        if asset_class == "forex":
            return f"{symbol}=X"
        
        # Crypto: Add -USD suffix if not present
        if asset_class == "crypto" and "USD" not in symbol:
            return f"{symbol}-USD"
        
        # Stocks: Use as-is
        return symbol
