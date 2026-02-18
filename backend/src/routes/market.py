"""Market data routes"""
import time
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from src.utils.logger import get_logger
from src.data.yfinance_backup import yfinance_backup

router = APIRouter()
logger = get_logger(__name__)

# In-memory ticker cache — avoids hammering yfinance on every 30-second frontend poll
_TICKER_CACHE_TTL = 60  # seconds
_ticker_cache: Optional[List] = None
_ticker_cache_ts: float = 0.0


class TickerResponse(BaseModel):
    symbol: str
    price: float
    change: float  # percentage
    change_type: str  # "positive" or "negative"
    timestamp: datetime


@router.get("/tickers", response_model=List[TickerResponse])
async def get_market_tickers():
    """
    Get current prices for popular assets

    Returns:
        List of ticker data with prices and changes
    """
    global _ticker_cache, _ticker_cache_ts

    # Return cached data if still fresh
    if _ticker_cache is not None and (time.time() - _ticker_cache_ts) < _TICKER_CACHE_TTL:
        logger.debug("Returning cached market tickers")
        return _ticker_cache

    try:
        # Popular assets to track
        assets = [
            {"symbol": "AAPL", "yf_symbol": "AAPL"},
            {"symbol": "GOOGL", "yf_symbol": "GOOGL"},
            {"symbol": "BTC", "yf_symbol": "BTC-USD"},
            {"symbol": "ETH", "yf_symbol": "ETH-USD"},
            {"symbol": "Gold", "yf_symbol": "GC=F"},
            {"symbol": "Silver", "yf_symbol": "SI=F"},
        ]
        
        tickers = []
        
        for asset in assets:
            try:
                current_price = None
                prev_close = None
                
                # Try to get current price from ticker info first
                ticker_info = yfinance_backup.get_ticker_info(asset["yf_symbol"])
                if ticker_info and isinstance(ticker_info, dict) and len(ticker_info) > 0:
                    # Check for price in ticker info - try multiple field names
                    current_price = (
                        ticker_info.get('regularMarketPrice') or
                        ticker_info.get('currentPrice') or
                        ticker_info.get('current_price') or
                        ticker_info.get('previousClose')
                    )
                    prev_close = ticker_info.get('previousClose')
                
                # If no price from ticker info, try historical data
                if current_price is None or current_price <= 0:
                    logger.debug(f"Trying historical data for {asset['symbol']} (yf_symbol: {asset['yf_symbol']})")
                    hist = yfinance_backup.get_historical_data(asset["yf_symbol"], period="2d", interval="1d")
                    if hist is not None and not hist.empty and len(hist) > 0:
                        try:
                            # Get latest close price
                            current_price = float(hist['Close'].iloc[-1]) if 'Close' in hist.columns else float(hist['close'].iloc[-1])
                            # Get previous close if available
                            if len(hist) > 1:
                                prev_close = float(hist['Close'].iloc[-2]) if 'Close' in hist.columns else float(hist['close'].iloc[-2])
                            else:
                                prev_close = current_price
                            logger.debug(f"Got price from historical data for {asset['symbol']}: {current_price}")
                        except (KeyError, IndexError, ValueError) as e:
                            logger.warning(f"Error extracting price from historical data for {asset['symbol']}: {e}")
                            continue
                    else:
                        logger.warning(f"No historical data available for {asset['symbol']} (yf_symbol: {asset['yf_symbol']})")
                        continue
                
                # Validate we have a valid price
                if current_price is None or current_price <= 0:
                    logger.warning(f"Invalid price for {asset['symbol']}: {current_price}")
                    continue
                
                # Use current_price as prev_close if not available
                if prev_close is None or prev_close <= 0:
                    prev_close = current_price
                
                # Calculate change percentage
                change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
                change_type = "positive" if change_pct >= 0 else "negative"
                
                tickers.append(TickerResponse(
                    symbol=asset["symbol"],
                    price=round(current_price, 2),
                    change=round(change_pct, 2),
                    change_type=change_type,
                    timestamp=datetime.utcnow()
                ))
                logger.debug(f"Successfully added ticker for {asset['symbol']}: ${current_price:.2f} ({change_pct:+.2f}%)")
            except Exception as e:
                logger.warning(f"Failed to fetch ticker for {asset['symbol']} (yf_symbol: {asset['yf_symbol']}): {e}", exc_info=True)
                continue
        
        logger.info(f"Retrieved {len(tickers)} market tickers")

        # Store in cache
        _ticker_cache = tickers
        _ticker_cache_ts = time.time()

        return tickers

    except Exception as e:
        logger.error(f"Error fetching market tickers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch market tickers")
