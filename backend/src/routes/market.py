"""Market data routes"""
import time
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from src.utils.logger import get_logger
from src.data.yfinance_backup import yfinance_backup
from src.analyzers.technical import TIMEFRAME_CONFIG
from src.config import settings

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
            {"symbol": "Gold",   "yf_symbol": "GC=F"},
            {"symbol": "NAS100", "yf_symbol": "^NDX"},
            {"symbol": "GBPUSD", "yf_symbol": "GBPUSD=X"},
            {"symbol": "TSLA",   "yf_symbol": "TSLA"},
            {"symbol": "DJI",    "yf_symbol": "^DJI"},
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


@router.get("/config/weights")
async def get_config_weights():
    """
    Return the current agent weights as configured in .env so the frontend
    can display them accurately without hardcoding.
    """
    return {
        "fundamental": round(settings.fundamental_weight * 100),
        "economic":    round(settings.economic_weight    * 100),
        "technical":   round(settings.technical_weight   * 100),
        "sentiment":   round(settings.sentiment_weight   * 100),
    }


def _to_yfinance_symbol(symbol: str, asset_class: str) -> str:
    """Convert a normalised signal symbol to a yfinance-compatible symbol."""
    if asset_class == "forex":
        return f"{symbol}=X"
    commodity_map = {
        "XAUUSD": "GC=F", "XAGUSD": "SI=F",
        "Gold": "GC=F", "Silver": "SI=F",
        "CL": "CL=F", "NG": "NG=F",
        # Indices
        "NAS100": "^NDX",  # NASDAQ 100
        "DJI": "^DJI",     # Dow Jones Industrial Average
    }
    if symbol in commodity_map:
        return commodity_map[symbol]
    if asset_class == "crypto" and "USD" not in symbol:
        return f"{symbol}-USD"
    return symbol


@router.get("/chart/{symbol}")
async def get_chart_data(
    symbol: str,
    timeframe: str = "15m",
    asset_class: str = "stock",
):
    """
    Return OHLCV candle data for the chart.

    Always loads the maximum available history for the selected timeframe so
    the user can scroll freely through all past price action.

    yfinance limits: 1m → max 7 days, 5m/15m/30m/60m → max 60 days, 1d → unlimited.
    """
    # Maximum history per timeframe (respects yfinance hard limits)
    CHART_HISTORY = {
        "1m":  "7d",   # yfinance hard limit for 1-min data
        "5m":  "60d",  # yfinance hard limit for sub-hour data
        "15m": "60d",
        "30m": "60d",
        "1h":  "60d",
        "4h":  "60d",  # fetched as 1h then resampled to 4h
        "1D":  "1y",   # 1 year of daily candles
    }
    try:
        cfg = TIMEFRAME_CONFIG.get(timeframe, TIMEFRAME_CONFIG["15m"])
        interval = cfg["interval"]
        period = CHART_HISTORY.get(timeframe, "60d")

        yf_symbol = _to_yfinance_symbol(symbol, asset_class)
        df = yfinance_backup.get_historical_data(yf_symbol, period=period, interval=interval)

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No chart data available for {symbol}")

        # Normalise column names — safely handles MultiIndex (tuple) columns
        df.columns = [
            (col[0] if isinstance(col, tuple) else col).lower()
            for col in df.columns
        ]

        # 4h: resample 1h data into 4-hour bars (yfinance has no native 4h interval)
        if timeframe == "4h":
            df = df.resample("4h").agg({
                "open": "first", "high": "max",
                "low": "min",   "close": "last",
                "volume": "sum",
            }).dropna()

        # Build lightweight-charts compatible OHLCV list
        candles = []
        for ts, row in df.iterrows():
            try:
                # Convert pandas Timestamp to Unix seconds
                unix_ts = int(ts.timestamp())
                candles.append({
                    "time":   unix_ts,
                    "open":   round(float(row["open"]),  4),
                    "high":   round(float(row["high"]),  4),
                    "low":    round(float(row["low"]),   4),
                    "close":  round(float(row["close"]), 4),
                    "volume": round(float(row.get("volume", 0)), 0),
                })
            except Exception:
                continue

        logger.info(f"Chart data: {len(candles)} candles for {symbol} [{timeframe}]")
        return candles

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chart data for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch chart data")
