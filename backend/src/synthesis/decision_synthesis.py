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
        
        # Adjust price points based on final signal to ensure they're correct
        # This handles cases where technical analysis says SELL but final signal is BUY (or vice versa)
        if final_signal == "BUY":
            # For BUY: stop_loss must be below entry, take_profit must be above entry
            if stop_loss >= entry_price:
                stop_loss = entry_price * 0.985  # 1.5% below entry
            if take_profit <= entry_price:
                take_profit = entry_price * 1.02  # 2% above entry
        elif final_signal == "SELL":
            # For SELL: stop_loss must be above entry, take_profit must be below entry
            if stop_loss <= entry_price:
                stop_loss = entry_price * 1.015  # 1.5% above entry
            if take_profit >= entry_price:
                take_profit = entry_price * 0.98  # 2% below entry
        
        # Calculate confidence using only applicable agents.
        # An agent is considered "not applicable" when it returns confidence=0 AND
        # recommendation=NEUTRAL (e.g. Fundamental for commodities/forex/crypto).
        # We re-normalize the weights across applicable agents so that N/A pillars
        # do not unfairly drag the overall confidence down below the minimum threshold.
        agent_results = {
            "fundamental": fundamental,
            "economic": economic,
            "technical": technical,
            "sentiment": sentiment,
        }
        applicable_weight_sum = 0.0
        weighted_confidence_sum = 0.0
        for agent_name, result in agent_results.items():
            w = self.weights[agent_name]
            conf = result["confidence"]
            rec = result["recommendation"]
            # Skip agents that are explicitly N/A (0 confidence + NEUTRAL)
            if conf == 0.0 and rec == "NEUTRAL":
                continue
            applicable_weight_sum += w
            weighted_confidence_sum += conf * w

        if applicable_weight_sum > 0:
            confidence = weighted_confidence_sum / applicable_weight_sum
        else:
            # All agents are N/A — fall back to simple average
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
