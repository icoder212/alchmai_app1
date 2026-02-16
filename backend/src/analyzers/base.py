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
        Calculate confidence based on score
        
        Args:
            score: Analysis score (0-100)
            
        Returns:
            Confidence level (0-100)
        """
        # Confidence is higher when score is further from neutral (50)
        if score >= 50:
            # Positive signal: confidence increases with score
            confidence = 50 + ((score - 50) * 0.5)
        else:
            # Negative signal: confidence increases as score decreases
            confidence = 50 + ((50 - score) * 0.5)
        
        return min(100, max(0, confidence))
