"""Base analyzer class"""
from abc import ABC, abstractmethod
from typing import Dict
from src.utils.logger import get_logger


class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def analyze(self, symbol: str, **kwargs) -> Dict:
        """
        Perform analysis on given symbol
        
        Args:
            symbol: Trading symbol
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with analysis results:
            {
                "recommendation": str,  # BUY, SELL, NEUTRAL
                "score": float,  # 0-100
                "reasoning": str,
                "confidence": float  # 0-100
            }
        """
        pass
    
    def _calculate_confidence(self, score: float) -> float:
        """
        Calculate confidence based on how far the score deviates from neutral (50).

        Mapping (score → confidence):
          50  → 50%   (neutral baseline — no strong conviction either way)
          60  → 60%   (mild signal)
          70  → 70%   (moderate signal)
          80  → 80%   (strong signal)
          90  → 90%   (very strong signal)
          100 → 100%  (maximum conviction)
          (symmetric for scores below 50)
        """
        deviation = abs(score - 50)  # 0 to 50
        # 50% base + scale deviation to add up to 50% more at maximum
        confidence = 50.0 + deviation
        return min(100.0, max(0.0, confidence))
