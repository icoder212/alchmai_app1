"""Technical analysis analyzer for 15-minute charts"""
import pandas as pd
import pandas_ta_classic as ta
from typing import Dict, Tuple

from .base import BaseAnalyzer
from src.data.alpha_vantage import alpha_vantage_client
from src.data.finnhub_client import finnhub_client

class TechnicalAnalyzer(BaseAnalyzer):
    """Analyzes 15-minute technical indicators"""
    
    def analyze(self, symbol: str, **kwargs) -> Dict:
        """
        Perform technical analysis on 15-min chart
        
        Args:
            symbol: Trading symbol
            **kwargs: Additional parameters (asset_class, etc.)
            
        Returns:
            Dict with recommendation, score, price points
        """
        self.logger.info(f"Starting technical analysis for {symbol}")
        
        # Get asset class for symbol conversion
        asset_class = kwargs.get('asset_class', 'stock')
        
        # Get 15-minute data
        df = self._get_15min_data(symbol, asset_class)
        
        if df.empty:
            self.logger.warning(f"No data available for {symbol}")
            return self._neutral_response("No data available")
        
        # Calculate indicators
        df = self._calculate_indicators(df)
        
        # Get latest values
        latest = df.iloc[-1]
        current_price = latest['close']
        
        # Generate signals
        signals = self._generate_signals(df, latest)
        
        # Determine overall recommendation
        recommendation, score = self._determine_recommendation(signals)
        
        # Calculate price points
        entry, sl, tp = self._calculate_price_points(current_price, recommendation)
        
        reasoning = self._format_reasoning(signals)
        confidence = self._calculate_confidence(score)
        
        self.logger.info(
            f"Technical analysis complete: {recommendation} "
            f"(score: {score:.1f}, confidence: {confidence:.1f}%)"
        )
        
        return {
            "recommendation": recommendation,
            "score": score,
            "reasoning": reasoning,
            "confidence": confidence,
            "entry_price": entry,
            "stop_loss": sl,
            "take_profit": tp,
            "indicators": {
                "rsi": round(latest['rsi'], 2) if 'rsi' in latest.index and pd.notna(latest['rsi']) else None,
                "macd": round(latest['macd'], 4) if 'macd' in latest.index and pd.notna(latest['macd']) else None,
                "macd_signal": round(latest['macd_signal'], 4) if 'macd_signal' in latest.index and pd.notna(latest['macd_signal']) else None,
                "sma_20": round(latest['sma_20'], 2) if 'sma_20' in latest.index and pd.notna(latest['sma_20']) else None,
                "ema_50": round(latest['ema_50'], 2) if 'ema_50' in latest.index and pd.notna(latest['ema_50']) else None,
                "bb_upper": round(latest['bb_upper'], 2) if 'bb_upper' in latest.index and pd.notna(latest['bb_upper']) else None,
                "bb_lower": round(latest['bb_lower'], 2) if 'bb_lower' in latest.index and pd.notna(latest['bb_lower']) else None,
                "current_price": round(current_price, 2)
            }
        }
    
    def _get_15min_data(self, symbol: str, asset_class: str = "stock") -> pd.DataFrame:
        """Fetch 15-minute OHLCV data with yfinance as primary source"""
        # Priority 1: yfinance (free, reliable, no API key needed)
        try:
            from ..data.yfinance_backup import yfinance_backup
            
            # Convert symbol to yfinance format
            yf_symbol = self._convert_to_yfinance_symbol(symbol, asset_class)
            
            # Use 5 days to get ~100+ candles (enough for all indicators including EMA50)
            # 5 days * 6.5 trading hours * 4 candles per hour = ~130 candles
            df = yfinance_backup.get_historical_data(yf_symbol, period="5d", interval="15m")
            if df is not None and not df.empty:
                # yfinance returns columns: Open, High, Low, Close, Volume
                # Rename to lowercase for consistency
                df.columns = [col.lower() for col in df.columns]
                self.logger.info(f"yfinance: {len(df)} candles for {yf_symbol} (original: {symbol})")
                return df
        except Exception as e:
            self.logger.warning(f"yfinance failed for {symbol}: {e}")
        
        # Priority 2: Try Alpha Vantage as fallback
        try:
            df = alpha_vantage_client.get_intraday_data(symbol, interval="15min")
            if not df.empty:
                self.logger.info(f"Alpha Vantage: {len(df)} candles for {symbol}")
                return df
        except Exception as e:
            self.logger.warning(f"Alpha Vantage failed: {e}")
        
        # Priority 3: Try Finnhub as last resort
        try:
            candles = finnhub_client.get_stock_candles(symbol, resolution="15", days=1)
            if candles and "c" in candles and len(candles["c"]) > 0:
                # Convert to DataFrame
                df = pd.DataFrame({
                    "open": candles["o"],
                    "high": candles["h"],
                    "low": candles["l"],
                    "close": candles["c"],
                    "volume": candles["v"]
                }, index=pd.to_datetime(candles["t"], unit="s"))
                self.logger.info(f"Finnhub: {len(df)} candles for {symbol}")
                return df
        except Exception as e:
            self.logger.warning(f"Finnhub candles failed: {e}")
        
        return pd.DataFrame()
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        self.logger.info(f"Calculating indicators with {len(df)} data points")
        calculated_indicators = []
        
        try:
            # RSI (14-period) - needs at least 14 data points
            if len(df) >= 14:
                rsi_result = ta.rsi(df['close'], length=14)
                if rsi_result is not None:
                    if isinstance(rsi_result, pd.DataFrame):
                        df['rsi'] = rsi_result.iloc[:, 0]
                    else:
                        df['rsi'] = rsi_result
                    calculated_indicators.append('RSI')
                else:
                    self.logger.warning("RSI calculation returned None")
            else:
                self.logger.warning(f"Insufficient data for RSI (need 14, have {len(df)})")
            
            # MACD - needs at least 26 data points
            if len(df) >= 26:
                macd = ta.macd(df['close'])
                if macd is not None and not macd.empty:
                    # Try different possible column names
                    for col in macd.columns:
                        if 'MACD_' in col and 'h' not in col and 's' not in col.lower():
                            df['macd'] = macd[col]
                        elif 'MACDs' in col or 'signal' in col.lower():
                            df['macd_signal'] = macd[col]
                        elif 'MACDh' in col or 'hist' in col.lower():
                            df['macd_hist'] = macd[col]
                    if 'macd' in df.columns:
                        calculated_indicators.append('MACD')
                else:
                    self.logger.warning("MACD calculation returned None or empty")
            else:
                self.logger.warning(f"Insufficient data for MACD (need 26, have {len(df)})")
            
            # Moving Averages
            if len(df) >= 20:
                sma_result = ta.sma(df['close'], length=20)
                if sma_result is not None:
                    if isinstance(sma_result, pd.DataFrame):
                        df['sma_20'] = sma_result.iloc[:, 0]
                    else:
                        df['sma_20'] = sma_result
                    calculated_indicators.append('SMA20')
            else:
                self.logger.warning(f"Insufficient data for SMA20 (need 20, have {len(df)})")
            
            if len(df) >= 50:
                ema_result = ta.ema(df['close'], length=50)
                if ema_result is not None:
                    if isinstance(ema_result, pd.DataFrame):
                        df['ema_50'] = ema_result.iloc[:, 0]
                    else:
                        df['ema_50'] = ema_result
                    calculated_indicators.append('EMA50')
            else:
                self.logger.warning(f"Insufficient data for EMA50 (need 50, have {len(df)})")
            
            # Bollinger Bands - needs at least 20 data points
            if len(df) >= 20:
                bbands = ta.bbands(df['close'], length=20)
                if bbands is not None and not bbands.empty:
                    self.logger.debug(f"Bollinger Bands columns: {bbands.columns.tolist()}")
                    # Try to find the correct column names
                    for col in bbands.columns:
                        col_lower = col.lower()
                        if 'upper' in col_lower or col.startswith('BBU'):
                            df['bb_upper'] = bbands[col]
                        elif 'lower' in col_lower or col.startswith('BBL'):
                            df['bb_lower'] = bbands[col]
                        elif 'middle' in col_lower or 'mid' in col_lower or col.startswith('BBM'):
                            df['bb_middle'] = bbands[col]
                    if 'bb_upper' in df.columns:
                        calculated_indicators.append('Bollinger Bands')
            else:
                self.logger.warning(f"Insufficient data for Bollinger Bands (need 20, have {len(df)})")
        
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}", exc_info=True)
        
        self.logger.info(f"Successfully calculated indicators: {', '.join(calculated_indicators) if calculated_indicators else 'None'}")
        return df
    
    def _generate_signals(self, df: pd.DataFrame, latest: pd.Series) -> list:
        """Generate buy/sell signals from indicators"""
        signals = []
        
        # RSI signals - check if column exists first
        if 'rsi' in latest.index and pd.notna(latest['rsi']):
            if latest['rsi'] < 30:
                signals.append(("BUY", "RSI oversold", 0.8))
            elif latest['rsi'] > 70:
                signals.append(("SELL", "RSI overbought", 0.8))
        
        # MACD signals - check if columns exist first
        if 'macd' in latest.index and 'macd_signal' in latest.index:
            if pd.notna(latest['macd']) and pd.notna(latest['macd_signal']):
                if latest['macd'] > latest['macd_signal']:
                    signals.append(("BUY", "MACD bullish crossover", 0.7))
                else:
                    signals.append(("SELL", "MACD bearish", 0.7))
        
        # Price vs SMA - check if column exists first
        if 'sma_20' in latest.index and pd.notna(latest['sma_20']):
            if latest['close'] > latest['sma_20']:
                signals.append(("BUY", "Price above SMA20", 0.6))
            else:
                signals.append(("SELL", "Price below SMA20", 0.6))
        
        # Price vs EMA - check if column exists first
        if 'ema_50' in latest.index and pd.notna(latest['ema_50']):
            if latest['close'] > latest['ema_50']:
                signals.append(("BUY", "Price above EMA50", 0.6))
            else:
                signals.append(("SELL", "Price below EMA50", 0.6))
        
        # Bollinger Bands - check if columns exist first
        if 'bb_lower' in latest.index and 'bb_upper' in latest.index:
            if pd.notna(latest['bb_lower']) and pd.notna(latest['bb_upper']):
                if latest['close'] <= latest['bb_lower']:
                    signals.append(("BUY", "Price at lower Bollinger Band", 0.7))
                elif latest['close'] >= latest['bb_upper']:
                    signals.append(("SELL", "Price at upper Bollinger Band", 0.7))
        
        return signals
    
    def _determine_recommendation(self, signals: list) -> Tuple[str, float]:
        """Aggregate signals into final recommendation"""
        if not signals:
            return "NEUTRAL", 50.0
        
        buy_score = sum(w for s, r, w in signals if s == "BUY")
        sell_score = sum(w for s, r, w in signals if s == "SELL")
        
        total = buy_score + sell_score
        if total == 0:
            return "NEUTRAL", 50.0
        
        if buy_score > sell_score:
            score = 50 + (buy_score / total) * 50  # Scale to 50-100
            return "BUY", min(100, score)
        elif sell_score > buy_score:
            score = 50 - (sell_score / total) * 50  # Scale to 0-50
            return "SELL", max(0, score)
        else:
            return "NEUTRAL", 50.0
    
    def _calculate_price_points(
        self,
        current_price: float,
        recommendation: str
    ) -> Tuple[float, float, float]:
        """Calculate entry, stop-loss, take-profit"""
        entry = current_price
        
        if recommendation == "BUY":
            stop_loss = entry * 0.985   # 1.5% below
            take_profit = entry * 1.02   # 2% above
        elif recommendation == "SELL":
            stop_loss = entry * 1.015    # 1.5% above
            take_profit = entry * 0.98   # 2% below
        else:  # NEUTRAL
            stop_loss = entry * 0.985
            take_profit = entry * 1.02
        
        return (
            round(entry, 2),
            round(stop_loss, 2),
            round(take_profit, 2)
        )
    
    def _format_reasoning(self, signals: list) -> str:
        """Format signals into readable string"""
        if not signals:
            return "No clear technical signals"
        
        reasons = [reason for _, reason, _ in signals]
        return " | ".join(reasons)
    
    def _convert_to_yfinance_symbol(self, symbol: str, asset_class: str) -> str:
        """
        Convert normalized symbol to yfinance format
        
        Args:
            symbol: Normalized symbol (e.g., "XAUUSD", "AAPL")
            asset_class: Asset class
            
        Returns:
            yfinance-compatible symbol
        """
        # Forex pairs: Add =X suffix
        if asset_class == "forex":
            return f"{symbol}=X"
        
        # Commodities: Special mappings
        commodity_map = {
            "XAUUSD": "GC=F",  # Gold futures
            "XAGUSD": "SI=F",  # Silver futures
            "CL": "CL=F",      # Crude oil futures
            "NG": "NG=F",      # Natural gas futures
        }
        if symbol in commodity_map:
            return commodity_map[symbol]
        
        # Crypto: Add -USD suffix if not present
        if asset_class == "crypto" and "USD" not in symbol:
            return f"{symbol}-USD"
        
        # Stocks: Use as-is
        return symbol
    
    def _neutral_response(self, reason: str) -> Dict:
        """Return neutral response"""
        return {
            "recommendation": "NEUTRAL",
            "score": 50.0,
            "reasoning": reason,
            "confidence": 0.0,
            "entry_price": 0.0,
            "stop_loss": 0.0,
            "take_profit": 0.0,
            "indicators": {}
        }
