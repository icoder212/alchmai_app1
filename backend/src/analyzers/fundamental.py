"""Fundamental analysis analyzer"""
from typing import Dict, Optional

from .base import BaseAnalyzer
from src.data.finnhub_client import finnhub_client
from src.data.alpha_vantage import alpha_vantage_client
from src.data.yfinance_backup import yfinance_backup

class FundamentalAnalyzer(BaseAnalyzer):
    """Analyzes company fundamentals and financials"""
    
    def analyze(self, symbol: str, asset_class: Optional[str] = None, **kwargs) -> Dict:
        """
        Perform fundamental analysis
        
        Args:
            symbol: Trading symbol
            asset_class: Asset class (stock, forex, commodity, crypto)
            **kwargs: Additional parameters
            
        Returns:
            Dict with recommendation, score, reasoning
        """
        self.logger.info(f"Starting fundamental analysis for {symbol}")
        
        # For non-stocks, return neutral
        if asset_class and asset_class != "stock":
            return self._neutral_response(f"Fundamental analysis not applicable for {asset_class}")
        
        try:
            # Get fundamental data — single yfinance call, shared across profile + financials
            yf_data = yfinance_backup.get_ticker_info(symbol) or {}
            profile = self._get_company_profile(symbol, yf_data)
            financials = self._get_financials(symbol, yf_data)

            # Calculate metrics
            pe_ratio = self._calculate_pe_ratio(financials, profile)
            revenue_growth = self._calculate_revenue_growth(financials)
            debt_ratio = self._calculate_debt_ratio(financials)
            profit_margin = self._calculate_profit_margin(financials)
            earnings_growth = self._calculate_earnings_growth(financials)

            # Generate recommendation
            score = self._calculate_fundamental_score(
                pe_ratio, revenue_growth, debt_ratio, profit_margin, earnings_growth
            )

            recommendation = "BUY" if score > 60 else "SELL" if score < 40 else "NEUTRAL"
            confidence = self._calculate_confidence(score)

            reasoning = self._format_reasoning(
                pe_ratio, revenue_growth, debt_ratio, profit_margin, earnings_growth
            )
            
            self.logger.info(
                f"Fundamental analysis complete: {recommendation} "
                f"(score: {score:.1f}, confidence: {confidence:.1f}%)"
            )
            
            return {
                "recommendation": recommendation,
                "score": score,
                "reasoning": reasoning,
                "confidence": confidence
            }
        except Exception as e:
            self.logger.error(f"Fundamental analysis error for {symbol}: {e}")
            return self._neutral_response(f"Error in fundamental analysis: {str(e)}")
    
    def _has_useful_data(self, data: Dict) -> bool:
        """
        Check if a data dict contains at least one of the specific fields
        this analyzer actually reads.

        Finnhub free tier returns 132 metric keys but the ones we need
        (peRatio, debtEquityRatio, profitMargin, revenueGrowth) are all None.
        Only revenueGrowth5Y has a value — but we don't use that key.
        So we must check the exact fields we read, not just any(metric.values()).

        yfinance returns flat keys: pe_ratio, profit_margin, debt_to_equity, revenueGrowth.
        """
        if not data:
            return False

        # Check the exact Finnhub metric keys this analyzer reads
        metric = data.get("metric", {})
        if isinstance(metric, dict):
            finnhub_keys = ["peRatio", "debtEquityRatio", "profitMargin", "revenueGrowth"]
            if any(metric.get(k) is not None for k in finnhub_keys):
                return True

        # Check yfinance flat keys
        yf_keys = ["pe_ratio", "profit_margin", "debt_to_equity", "revenueGrowth"]
        if any(data.get(k) is not None for k in yf_keys):
            return True

        return False

    def _get_company_profile(self, symbol: str, yf_data: Dict) -> Dict:
        """Get company profile — tries Finnhub, then yfinance (pre-fetched, no duplicate call)"""
        try:
            profile = finnhub_client.get_company_profile(symbol) or {}
            if profile.get("name") or profile.get("ticker"):
                return profile
        except Exception:
            pass

        # Use the pre-fetched yfinance data — no second HTTP call
        return yf_data

    def _get_financials(self, symbol: str, yf_data: Dict) -> Dict:
        """Get company financials — tries Finnhub for the exact fields we need, falls back to yfinance"""
        try:
            finnhub_data = finnhub_client.get_company_financials(symbol, metric="all") or {}
        except Exception:
            finnhub_data = {}

        # Only use Finnhub data if it actually has the specific fields we read.
        # Free tier returns 132 metric keys but peRatio/debtEquityRatio/profitMargin
        # are all None — only revenueGrowth5Y has a value which we don't use.
        if self._has_useful_data(finnhub_data):
            return finnhub_data

        # Use the pre-fetched yfinance data — no second HTTP call
        return yf_data
    
    def _get_latest_earnings(self, symbol: str) -> list:
        """Get latest earnings data"""
        try:
            return finnhub_client.get_earnings(symbol, limit=5)
        except Exception:
            return []
    
    def _calculate_pe_ratio(self, financials: Dict, profile: Dict) -> Optional[float]:
        """Calculate P/E ratio — checks Finnhub metric format then yfinance flat keys"""
        try:
            pe = (
                financials.get("metric", {}).get("peRatio") or   # Finnhub
                profile.get("pe") or                              # Finnhub profile
                profile.get("trailingPE") or                      # yfinance direct
                financials.get("pe_ratio") or                     # yfinance via backup
                profile.get("pe_ratio")                           # yfinance via profile
            )
            return float(pe) if pe else None
        except Exception:
            return None

    def _calculate_revenue_growth(self, financials: Dict) -> Optional[float]:
        """Calculate revenue growth — checks Finnhub metric then yfinance revenueGrowth"""
        try:
            # Finnhub nested format
            revenue_data = financials.get("metric", {}).get("revenueGrowth", {})
            if revenue_data:
                if isinstance(revenue_data, dict):
                    values = [v for v in revenue_data.values() if v is not None]
                    if values:
                        return float(values[-1]) * 100
                elif isinstance(revenue_data, (int, float)):
                    return float(revenue_data) * 100

            # yfinance flat key (revenueGrowth is already a ratio e.g. 0.12 = 12%)
            rg = financials.get("revenueGrowth")
            if rg is not None:
                return float(rg) * 100
        except Exception:
            pass
        return None

    def _calculate_debt_ratio(self, financials: Dict) -> Optional[float]:
        """Calculate debt-to-equity ratio — checks Finnhub metric then yfinance flat keys"""
        try:
            # Use explicit None check — 0.0 is valid data and must not be treated as missing
            metric_val = financials.get("metric", {}).get("debtEquityRatio")
            yf_val = financials.get("debt_to_equity")
            debt_equity = metric_val if metric_val is not None else yf_val
            return float(debt_equity) if debt_equity is not None else None
        except Exception:
            return None

    def _calculate_earnings_growth(self, financials: Dict) -> Optional[float]:
        """Calculate earnings (EPS) growth — yfinance earningsGrowth key"""
        try:
            eg = financials.get("earnings_growth")
            if eg is not None:
                return float(eg) * 100  # e.g. 0.183 → 18.3%
        except Exception:
            pass
        return None

    def _calculate_profit_margin(self, financials: Dict) -> Optional[float]:
        """Calculate profit margin — checks Finnhub metric then yfinance flat keys"""
        try:
            # Finnhub nested format
            margin = financials.get("metric", {}).get("profitMargin", {})
            if margin:
                if isinstance(margin, dict):
                    values = [v for v in margin.values() if v is not None]
                    if values:
                        return float(values[-1]) * 100
                elif isinstance(margin, (int, float)):
                    return float(margin) * 100

            # yfinance flat key (profitMargins is already a ratio e.g. 0.24 = 24%)
            pm = financials.get("profit_margin")
            if pm is not None:
                return float(pm) * 100
        except Exception:
            pass
        return None
    
    def _calculate_fundamental_score(
        self,
        pe_ratio: Optional[float],
        revenue_growth: Optional[float],
        debt_ratio: Optional[float],
        profit_margin: Optional[float],
        earnings_growth: Optional[float] = None
    ) -> float:
        """Calculate overall fundamental score (0-100)"""
        score = 50.0  # Start neutral
        factors = 0

        # P/E ratio (lower is better, but not too low)
        if pe_ratio is not None:
            if 10 <= pe_ratio <= 25:
                score += 15  # Good range
            elif pe_ratio < 10:
                score += 5   # Might be too cheap (value trap)
            elif pe_ratio > 25:
                score -= 10  # Overvalued
            factors += 1

        # Revenue growth (positive is good)
        if revenue_growth is not None:
            if revenue_growth > 10:
                score += 20  # Strong growth
            elif revenue_growth > 5:
                score += 10  # Moderate growth
            elif revenue_growth > 0:
                score += 5   # Positive growth
            else:
                score -= 15  # Declining revenue
            factors += 1

        # Earnings (EPS) growth — strong EPS growth is bullish
        if earnings_growth is not None:
            if earnings_growth > 15:
                score += 15  # Strong EPS growth
            elif earnings_growth > 5:
                score += 8   # Moderate EPS growth
            elif earnings_growth > 0:
                score += 3   # Positive EPS growth
            else:
                score -= 10  # EPS contraction
            factors += 1

        # Debt ratio (lower is better)
        # Note: yfinance debtToEquity is in percentage form (e.g. 102.63 = 102.63%)
        # Finnhub debtEquityRatio is in decimal form (e.g. 1.02 = 102%)
        # We normalise to percentage form for scoring
        if debt_ratio is not None:
            if debt_ratio < 50:
                score += 10  # Low debt (< 50%)
            elif debt_ratio < 100:
                score += 5   # Moderate debt (50-100%)
            else:
                score -= 10  # High debt (> 100%)
            factors += 1

        # Profit margin (higher is better)
        if profit_margin is not None:
            if profit_margin > 20:
                score += 15  # High margin
            elif profit_margin > 10:
                score += 10  # Good margin
            elif profit_margin > 5:
                score += 5   # Decent margin
            else:
                score -= 10  # Low margin
            factors += 1

        return max(0, min(100, score))
    
    def _format_reasoning(
        self,
        pe_ratio: Optional[float],
        revenue_growth: Optional[float],
        debt_ratio: Optional[float],
        profit_margin: Optional[float],
        earnings_growth: Optional[float] = None
    ) -> str:
        """Format reasoning string"""
        parts = []

        if pe_ratio is not None:
            parts.append(f"P/E: {pe_ratio:.2f}")
        if revenue_growth is not None:
            parts.append(f"Revenue Growth: {revenue_growth:.2f}%")
        if earnings_growth is not None:
            parts.append(f"EPS Growth: {earnings_growth:.2f}%")
        if profit_margin is not None:
            parts.append(f"Profit Margin: {profit_margin:.2f}%")
        if debt_ratio is not None:
            parts.append(f"Debt/Equity: {debt_ratio:.2f}%")

        return " | ".join(parts) if parts else "Limited fundamental data available"
    
    def _neutral_response(self, reason: str) -> Dict:
        """Return neutral response"""
        return {
            "recommendation": "NEUTRAL",
            "score": 50.0,
            "reasoning": reason,
            "confidence": 0.0
        }
