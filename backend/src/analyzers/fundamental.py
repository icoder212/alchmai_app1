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
            # Get fundamental data
            profile = self._get_company_profile(symbol)
            financials = self._get_financials(symbol)
            earnings = self._get_latest_earnings(symbol)
            
            # Calculate metrics
            pe_ratio = self._calculate_pe_ratio(financials, profile)
            revenue_growth = self._calculate_revenue_growth(financials)
            debt_ratio = self._calculate_debt_ratio(financials)
            profit_margin = self._calculate_profit_margin(financials)
            
            # Generate recommendation
            score = self._calculate_fundamental_score(
                pe_ratio, revenue_growth, debt_ratio, profit_margin
            )
            
            recommendation = "BUY" if score > 60 else "SELL" if score < 40 else "NEUTRAL"
            confidence = self._calculate_confidence(score)
            
            reasoning = self._format_reasoning(
                pe_ratio, revenue_growth, debt_ratio, profit_margin
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
    
    def _get_company_profile(self, symbol: str) -> Dict:
        """Get company profile"""
        try:
            return finnhub_client.get_company_profile(symbol)
        except Exception:
            # Try Alpha Vantage
            try:
                return alpha_vantage_client.get_company_overview(symbol)
            except Exception:
                # Try yfinance backup
                return yfinance_backup.get_ticker_info(symbol)
    
    def _get_financials(self, symbol: str) -> Dict:
        """Get company financials"""
        try:
            return finnhub_client.get_company_financials(symbol, metric="all")
        except Exception:
            # Try yfinance backup
            return yfinance_backup.get_ticker_info(symbol)
    
    def _get_latest_earnings(self, symbol: str) -> list:
        """Get latest earnings data"""
        try:
            return finnhub_client.get_earnings(symbol, limit=5)
        except Exception:
            return []
    
    def _calculate_pe_ratio(self, financials: Dict, profile: Dict) -> Optional[float]:
        """Calculate P/E ratio"""
        # Try multiple sources
        pe = (
            financials.get("metric", {}).get("peRatio") or
            profile.get("pe") or
            profile.get("trailingPE") or
            financials.get("pe_ratio")
        )
        return float(pe) if pe else None
    
    def _calculate_revenue_growth(self, financials: Dict) -> Optional[float]:
        """Calculate revenue growth (quarter-over-quarter)"""
        try:
            revenue_data = financials.get("metric", {}).get("revenueGrowth", {})
            if revenue_data:
                # Get latest quarter growth
                if isinstance(revenue_data, dict):
                    values = [v for v in revenue_data.values() if v is not None]
                    if values:
                        return float(values[-1]) * 100  # Convert to percentage
                elif isinstance(revenue_data, (int, float)):
                    return float(revenue_data) * 100
        except Exception:
            pass
        return None
    
    def _calculate_debt_ratio(self, financials: Dict) -> Optional[float]:
        """Calculate debt-to-equity ratio"""
        try:
            debt_equity = (
                financials.get("metric", {}).get("debtEquityRatio") or
                financials.get("debt_to_equity")
            )
            return float(debt_equity) if debt_equity else None
        except Exception:
            return None
    
    def _calculate_profit_margin(self, financials: Dict) -> Optional[float]:
        """Calculate profit margin"""
        try:
            margin = (
                financials.get("metric", {}).get("profitMargin", {}) or
                financials.get("profit_margin")
            )
            if margin:
                if isinstance(margin, dict):
                    values = [v for v in margin.values() if v is not None]
                    if values:
                        return float(values[-1]) * 100
                elif isinstance(margin, (int, float)):
                    return float(margin) * 100
        except Exception:
            pass
        return None
    
    def _calculate_fundamental_score(
        self,
        pe_ratio: Optional[float],
        revenue_growth: Optional[float],
        debt_ratio: Optional[float],
        profit_margin: Optional[float]
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
        
        # Debt ratio (lower is better)
        if debt_ratio is not None:
            if debt_ratio < 0.5:
                score += 10  # Low debt
            elif debt_ratio < 1.0:
                score += 5   # Moderate debt
            else:
                score -= 10  # High debt
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
        
        # Normalize if we have factors
        if factors > 0:
            score = score / (1 + (factors - 1) * 0.1)  # Slight normalization
        
        return max(0, min(100, score))
    
    def _format_reasoning(
        self,
        pe_ratio: Optional[float],
        revenue_growth: Optional[float],
        debt_ratio: Optional[float],
        profit_margin: Optional[float]
    ) -> str:
        """Format reasoning string"""
        parts = []
        
        if pe_ratio is not None:
            parts.append(f"P/E: {pe_ratio:.2f}")
        if revenue_growth is not None:
            parts.append(f"Revenue Growth: {revenue_growth:.2f}%")
        if debt_ratio is not None:
            parts.append(f"Debt/Equity: {debt_ratio:.2f}")
        if profit_margin is not None:
            parts.append(f"Profit Margin: {profit_margin:.2f}%")
        
        return " | ".join(parts) if parts else "Limited fundamental data available"
    
    def _neutral_response(self, reason: str) -> Dict:
        """Return neutral response"""
        return {
            "recommendation": "NEUTRAL",
            "score": 50.0,
            "reasoning": reason,
            "confidence": 0.0
        }
