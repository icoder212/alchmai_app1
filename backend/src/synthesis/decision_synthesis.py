"""Decision synthesis logic for combining agent recommendations"""
from typing import Dict, List
from src.config import settings
from src.models.signal import AgentAnalysis, TradingSignal
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DecisionSynthesizer:
    """Synthesizes final trading signal from all agent analyses"""
    
    def __init__(self):
        self.weights = {
            "fundamental": settings.fundamental_weight,
            "economic": settings.economic_weight,
            "technical": settings.technical_weight,
            "sentiment": settings.sentiment_weight,
        }
        logger.info(f"Decision synthesizer initialized with weights: {self.weights}")
    
    def synthesize(
        self,
        fundamental: Dict,
        economic: Dict,
        technical: Dict,
        sentiment: Dict,
        current_price: float,
        symbol: str
    ) -> TradingSignal:
        """
        Synthesize final signal from all agent analyses
        
        Args:
            fundamental: Fundamental analysis result
            economic: Economic analysis result
            technical: Technical analysis result
            sentiment: Sentiment analysis result
            current_price: Current market price
            symbol: Trading symbol
            
        Returns:
            TradingSignal with final recommendation
        """
        logger.info(f"Synthesizing signal for {symbol}")
        
        # Convert agent recommendations to scores
        # BUY = positive, SELL = negative, NEUTRAL = 0
        def recommendation_to_score(rec: str, score: float) -> float:
            """Convert recommendation to signed score"""
            if rec == "BUY":
                return score  # 0-100, positive
            elif rec == "SELL":
                return -score  # -100 to 0, negative
            else:  # NEUTRAL
                return 0
        
        # Calculate weighted scores
        fund_score = recommendation_to_score(
            fundamental["recommendation"],
            fundamental["score"]
        ) * self.weights["fundamental"]
        
        econ_score = recommendation_to_score(
            economic["recommendation"],
            economic["score"]
        ) * self.weights["economic"]
        
        tech_score = recommendation_to_score(
            technical["recommendation"],
            technical["score"]
        ) * self.weights["technical"]
        
        sent_score = recommendation_to_score(
            sentiment["recommendation"],
            sentiment["score"]
        ) * self.weights["sentiment"]
        
        # Sum weighted scores
        total_score = fund_score + econ_score + tech_score + sent_score
        
        # Determine final signal
        if total_score > 10:  # Threshold for BUY
            final_signal = "BUY"
            final_score = min(100, 50 + abs(total_score))
        elif total_score < -10:  # Threshold for SELL
            final_signal = "SELL"
            final_score = max(0, 50 - abs(total_score))
        else:
            final_signal = "NEUTRAL"
            final_score = 50.0
        
        # Use technical analysis price points (most accurate for 15-min signals)
        # Fallback to current_price if technical prices are invalid (0.0)
        entry_price = technical.get("entry_price", 0.0)
        stop_loss = technical.get("stop_loss", 0.0)
        take_profit = technical.get("take_profit", 0.0)
        
        # Use current_price if technical prices are invalid
        if entry_price <= 0:
            entry_price = current_price
        if stop_loss <= 0:
            stop_loss = current_price * 0.985 if final_signal == "BUY" else current_price * 1.015
        if take_profit <= 0:
            take_profit = current_price * 1.02 if final_signal == "BUY" else current_price * 0.98
        
        # Adjust if signal is SELL (override technical values)
        if final_signal == "SELL":
            stop_loss = current_price * 1.015
            take_profit = current_price * 0.98
        
        # Calculate confidence (weighted average of agent confidences)
        confidence = (
            fundamental["confidence"] * self.weights["fundamental"] +
            economic["confidence"] * self.weights["economic"] +
            technical["confidence"] * self.weights["technical"] +
            sentiment["confidence"] * self.weights["sentiment"]
        )
        
        # Create agent analysis objects
        fundamental_analysis = AgentAnalysis(
            agent="fundamental",
            recommendation=fundamental["recommendation"],
            score=fundamental["score"],
            reasoning=fundamental["reasoning"],
            confidence=fundamental["confidence"]
        )
        
        economic_analysis = AgentAnalysis(
            agent="economic",
            recommendation=economic["recommendation"],
            score=economic["score"],
            reasoning=economic["reasoning"],
            confidence=economic["confidence"]
        )
        
        technical_analysis = AgentAnalysis(
            agent="technical",
            recommendation=technical["recommendation"],
            score=technical["score"],
            reasoning=technical["reasoning"],
            confidence=technical["confidence"]
        )
        
        sentiment_analysis = AgentAnalysis(
            agent="sentiment",
            recommendation=sentiment["recommendation"],
            score=sentiment["score"],
            reasoning=sentiment["reasoning"],
            confidence=sentiment["confidence"]
        )
        
        logger.info(
            f"Signal synthesized: {final_signal} "
            f"(score: {final_score:.1f}, confidence: {confidence:.1f}%)"
        )
        
        return TradingSignal(
            instrument=symbol,
            signal=final_signal,
            entry_price=round(entry_price, 2),
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            confidence=round(confidence, 2),
            fundamental_analysis=fundamental_analysis,
            economic_analysis=economic_analysis,
            technical_analysis=technical_analysis,
            sentiment_analysis=sentiment_analysis,
            current_price=round(current_price, 2),
            execution_time=0.0,  # Will be set by orchestrator
            api_calls_made=0  # Will be tracked by orchestrator
        )
