"""Safety validator for trading signals"""
from typing import Tuple
from src.config import settings
from src.models.signal import TradingSignal
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SafetyValidator:
    """Validates trading signals for safety and sanity"""
    
    def validate(self, signal: TradingSignal) -> Tuple[bool, str]:
        """
        Validate generated signal
        
        Args:
            signal: Trading signal to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.info(f"Validating signal for {signal.instrument}")
        
        # Check confidence threshold
        if signal.confidence < settings.min_confidence:
            return False, f"Confidence too low: {signal.confidence}% (minimum: {settings.min_confidence}%)"
        
        # Check price points make sense
        if signal.signal == "BUY":
            if signal.stop_loss >= signal.entry_price:
                return False, "BUY signal but stop-loss above or equal to entry"
            if signal.take_profit <= signal.entry_price:
                return False, "BUY signal but take-profit below or equal to entry"
        elif signal.signal == "SELL":
            if signal.stop_loss <= signal.entry_price:
                return False, "SELL signal but stop-loss below or equal to entry"
            if signal.take_profit >= signal.entry_price:
                return False, "SELL signal but take-profit above or equal to entry"
        
        # Check risk-reward ratio
        if signal.signal == "BUY":
            risk = signal.entry_price - signal.stop_loss
            reward = signal.take_profit - signal.entry_price
        else:  # SELL
            risk = signal.stop_loss - signal.entry_price
            reward = signal.entry_price - signal.take_profit
        
        if risk <= 0:
            return False, f"Invalid risk calculation: {risk}"
        
        risk_reward_ratio = reward / risk
        if risk_reward_ratio < 1.0:
            return False, f"Poor risk-reward ratio: {risk_reward_ratio:.2f} (minimum: 1.0)"
        
        # Check price points are reasonable (not too far from current)
        if signal.current_price:
            price_deviation = abs(signal.entry_price - signal.current_price) / signal.current_price
            if price_deviation > 0.05:  # More than 5% deviation
                logger.warning(
                    f"Large price deviation: {price_deviation*100:.2f}% "
                    f"(entry: {signal.entry_price}, current: {signal.current_price})"
                )
        
        # Check all agent analyses are present
        required_agents = ["fundamental", "economic", "technical", "sentiment"]
        agent_analyses = [
            signal.fundamental_analysis,
            signal.economic_analysis,
            signal.technical_analysis,
            signal.sentiment_analysis
        ]
        
        for agent, analysis in zip(required_agents, agent_analyses):
            if analysis is None:
                return False, f"Missing {agent} analysis"
        
        logger.info(f"Signal validation passed for {signal.instrument}")
        return True, "Valid signal"
