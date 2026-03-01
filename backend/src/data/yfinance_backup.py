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

    def _flatten_columns(self, df):
        """
        Flatten MultiIndex columns that yfinance 1.x returns for some tickers.
        Returns the same df with single-level string columns, or None if df is bad.
        """
        if df is None or df.empty:
            return df
        # MultiIndex check: if columns have multiple levels, take only the first level
        if hasattr(df.columns, 'nlevels') and df.columns.nlevels > 1:
            df = df.copy()
            df.columns = [
                col[0] if isinstance(col, tuple) else col
                for col in df.columns
            ]
        return df

    def get_historical_data(
        self,
        symbol: str,
        period: str = "1d",
        interval: str = "15m"
    ) -> Optional[object]:
        """
        Get historical data as backup.

        Tries ticker.history() first. If it returns empty data (common for
        futures/indices with certain intervals in yfinance 1.x), falls back
        to yf.download() which is more robust for those asset types.

        Args:
            symbol: Stock/futures/index symbol (e.g. "GC=F", "^NDX", "AAPL")
            period: Period string (1d, 5d, 7d, 30d, 60d, 1y …)
            interval: Interval string (1m, 5m, 15m, 30m, 60m, 1d …)

        Returns:
            DataFrame with OHLCV data, or None on failure
        """
        # ── Attempt 1: ticker.history() ──────────────────────────────────────
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval, auto_adjust=True, actions=False)
            df = self._flatten_columns(df)
            if df is not None and not df.empty:
                logger.debug(f"yfinance ticker.history OK for {symbol} [{interval}/{period}]: {len(df)} rows")
                return df
            logger.debug(
                f"yfinance ticker.history returned empty for {symbol} [{interval}/{period}], trying download()"
            )
        except Exception as e:
            logger.warning(f"yfinance ticker.history error for {symbol}: {e}")

        # ── Attempt 2: yf.download() (more reliable for futures/indices) ─────
        try:
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                multi_level_index=False,   # yfinance 1.x: keep single-level columns
            )
            df = self._flatten_columns(df)
            if df is not None and not df.empty:
                logger.debug(f"yfinance download() OK for {symbol} [{interval}/{period}]: {len(df)} rows")
                return df
            logger.warning(f"yfinance download() also returned empty for {symbol} [{interval}/{period}]")
        except TypeError:
            # Older yfinance without multi_level_index parameter — try without it
            try:
                df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
                df = self._flatten_columns(df)
                if df is not None and not df.empty:
                    logger.debug(f"yfinance download() (compat) OK for {symbol}: {len(df)} rows")
                    return df
            except Exception as e2:
                logger.error(f"yfinance download() compat error for {symbol}: {e2}")
        except Exception as e:
            logger.error(f"yfinance download() error for {symbol}: {e}")

        logger.error(f"yfinance: no data available for {symbol} [{interval}/{period}]")
        return None


# Global backup instance
yfinance_backup = YFinanceBackup()
