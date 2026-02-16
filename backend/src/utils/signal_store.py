"""In-memory signal storage for history"""
from typing import List, Optional
from datetime import datetime

from src.models.signal import TradingSignal
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SignalStore:
    """In-memory storage for signal history"""
    
    def __init__(self, max_signals: int = 100):
        """
        Initialize signal store
        
        Args:
            max_signals: Maximum number of signals to store (default 100)
        """
        self._signals: List[TradingSignal] = []
        self.max_signals = max_signals
        logger.info(f"SignalStore initialized with max_signals={max_signals}")
    
    def add_signal(self, signal: TradingSignal) -> None:
        """
        Add signal to history
        
        Args:
            signal: Trading signal to store
        """
        self._signals.insert(0, signal)  # Most recent first
        if len(self._signals) > self.max_signals:
            removed = self._signals.pop()
            logger.debug(f"Removed oldest signal: {removed.instrument} from {removed.timestamp}")
        
        logger.info(f"Stored signal: {signal.instrument} {signal.signal} (total: {len(self._signals)})")
    
    def get_recent(self, limit: int = 20) -> List[TradingSignal]:
        """
        Get recent signals
        
        Args:
            limit: Number of signals to return (default 20)
            
        Returns:
            List of recent trading signals
        """
        signals = self._signals[:limit]
        logger.debug(f"Retrieved {len(signals)} recent signals")
        return signals
    
    def get_by_instrument(self, instrument: str, limit: int = 10) -> List[TradingSignal]:
        """
        Get signals for specific instrument
        
        Args:
            instrument: Instrument symbol (e.g., 'AAPL')
            limit: Number of signals to return (default 10)
            
        Returns:
            List of trading signals for the instrument
        """
        filtered = [s for s in self._signals if s.instrument.upper() == instrument.upper()]
        signals = filtered[:limit]
        logger.debug(f"Retrieved {len(signals)} signals for {instrument}")
        return signals
    
    def get_count(self) -> int:
        """
        Get total number of stored signals
        
        Returns:
            Number of signals in store
        """
        return len(self._signals)
    
    def clear(self) -> None:
        """Clear all stored signals"""
        count = len(self._signals)
        self._signals.clear()
        logger.info(f"Cleared {count} signals from store")


# Global signal store instance
signal_store = SignalStore()
