"""Economic analysis analyzer"""
from typing import Dict

from .base import BaseAnalyzer
from src.data.fred_client import fred_client

class EconomicAnalyzer(BaseAnalyzer):
    """Analyzes macroeconomic conditions"""
    
    def analyze(self, symbol: str, asset_class: str = "stock", **kwargs) -> Dict:
        """
        Perform economic analysis
        
        Args:
            symbol: Trading symbol
            asset_class: Asset class (stock, forex, commodity, crypto)
            **kwargs: Additional parameters
            
        Returns:
            Dict with recommendation, score, reasoning
        """
        self.logger.info(f"Starting economic analysis for {symbol} ({asset_class})")
        
        try:
            # Get macro indicators
            indicators = fred_client.get_all_indicators()
            
            gdp_growth = indicators.get("gdp_growth", 0)
            inflation = indicators.get("inflation", 0)
            unemployment = indicators.get("unemployment", 0)
            fed_rate = indicators.get("fed_rate", 0)
            
            # Generate recommendation
            score = self._calculate_economic_score(
                gdp_growth, inflation, unemployment, fed_rate, asset_class
            )
            
            # Convert to BUY/SELL/NEUTRAL (economic is BULLISH/BEARISH)
            if score > 60:
                recommendation = "BUY"  # BULLISH economic conditions
            elif score < 40:
                recommendation = "SELL"  # BEARISH economic conditions
            else:
                recommendation = "NEUTRAL"
            
            confidence = self._calculate_confidence(score)
            
            reasoning = self._format_reasoning(
                gdp_growth, inflation, unemployment, fed_rate
            )
            
            self.logger.info(
                f"Economic analysis complete: {recommendation} "
                f"(score: {score:.1f}, confidence: {confidence:.1f}%)"
            )
            
            return {
                "recommendation": recommendation,
                "score": score,
                "reasoning": reasoning,
                "confidence": confidence
            }
        except Exception as e:
            self.logger.error(f"Economic analysis error: {e}")
            return self._neutral_response(f"Error in economic analysis: {str(e)}")
    
    def _calculate_economic_score(
        self,
        gdp_growth: float,
        inflation: float,
        unemployment: float,
        fed_rate: float,
        asset_class: str
    ) -> float:
        """Calculate overall economic score (0-100)"""
        score = 50.0  # Start neutral
        
        # GDP Growth (positive is good for stocks)
        if gdp_growth > 3:
            score += 20  # Strong growth
        elif gdp_growth > 2:
            score += 10  # Moderate growth
        elif gdp_growth > 0:
            score += 5   # Positive growth
        else:
            score -= 15  # Negative growth (recession)
        
        # Inflation (moderate is okay, high is bad)
        if 1.5 <= inflation <= 3.0:
            score += 10  # Healthy inflation
        elif inflation < 1.5:
            score += 5   # Low inflation (deflation risk)
        elif inflation > 5:
            score -= 20  # High inflation (bad)
        elif inflation > 3:
            score -= 10  # Elevated inflation
        
        # Unemployment (lower is better)
        if unemployment < 4:
            score += 15  # Very low unemployment
        elif unemployment < 5:
            score += 10  # Low unemployment
        elif unemployment < 6:
            score += 5   # Moderate unemployment
        else:
            score -= 15  # High unemployment
        
        # Fed Rate (depends on asset class)
        if asset_class == "stock":
            # Lower rates are generally better for stocks
            if fed_rate < 2:
                score += 10
            elif fed_rate < 4:
                score += 5
            else:
                score -= 10  # High rates can hurt stocks
        elif asset_class == "forex":
            # Higher rates can strengthen currency
            if fed_rate > 4:
                score += 10
            elif fed_rate > 2:
                score += 5
        
        return max(0, min(100, score))
    
    def _format_reasoning(
        self,
        gdp_growth: float,
        inflation: float,
        unemployment: float,
        fed_rate: float
    ) -> str:
        """Format reasoning string"""
        return (
            f"GDP: {gdp_growth:.2f}% | "
            f"Inflation: {inflation:.2f}% | "
            f"Unemployment: {unemployment:.2f}% | "
            f"Fed Rate: {fed_rate:.2f}%"
        )
    
    def _neutral_response(self, reason: str) -> Dict:
        """Return neutral response"""
        return {
            "recommendation": "NEUTRAL",
            "score": 50.0,
            "reasoning": reason,
            "confidence": 0.0
        }
