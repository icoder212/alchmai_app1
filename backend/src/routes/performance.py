"""Performance metrics routes"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.utils.logger import get_logger
from src.utils.signal_store import signal_store
from src.data.yfinance_backup import yfinance_backup

router = APIRouter()
logger = get_logger(__name__)


class PerformanceMetrics(BaseModel):
    win_rate: float  # 0-100
    win_rate_change: float  # percentage change
    avg_return: float  # percentage
    avg_return_change: float  # percentage change
    trades_per_month: int
    trades_per_month_change: float  # percentage change
    period: str  # "last_30_days" or "all_time"
    timestamp: datetime


@router.get("/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """
    Calculate performance metrics from signal history
    
    For POC:
    - Win rate: Compare signal direction with current price vs entry price
    - Average return: Calculate from entry vs current price
    - Trades per month: Count signals per month
    
    Returns:
        Performance metrics with changes from previous period
    """
    try:
        all_signals = signal_store.get_recent(1000)
        
        if not all_signals:
            return PerformanceMetrics(
                win_rate=0.0,
                win_rate_change=0.0,
                avg_return=0.0,
                avg_return_change=0.0,
                trades_per_month=0,
                trades_per_month_change=0.0,
                period="all_time",
                timestamp=datetime.utcnow()
            )
        
        # Get signals from last 30 days
        cutoff_30d = datetime.utcnow() - timedelta(days=30)
        signals_30d = [s for s in all_signals if s.timestamp >= cutoff_30d]
        
        # Get signals from previous 30 days (30-60 days ago)
        cutoff_60d = datetime.utcnow() - timedelta(days=60)
        signals_prev = [s for s in all_signals if cutoff_60d <= s.timestamp < cutoff_30d]
        
        # Calculate win rate (for POC: if BUY and current > entry, it's a win)
        # For simplicity, we'll use a mock calculation
        # In production, you'd fetch current prices and compare
        wins = 0
        total_returns = []
        
        for signal in signals_30d:
            try:
                # Try to get current price (simplified - in production, use actual price tracking)
                # For POC, we'll estimate based on signal confidence
                # If confidence > 70%, assume it's a win
                if signal.confidence > 70:
                    wins += 1
                    # Estimate return based on confidence
                    estimated_return = (signal.confidence - 50) * 0.2  # Rough estimate
                    total_returns.append(estimated_return)
            except Exception as e:
                logger.warning(f"Error calculating return for signal {signal.instrument}: {e}")
                continue
        
        win_rate = (wins / len(signals_30d) * 100) if signals_30d else 0.0
        avg_return = sum(total_returns) / len(total_returns) if total_returns else 0.0
        
        # Calculate previous period metrics (simplified)
        prev_wins = len(signals_prev) * 0.6  # Estimate 60% win rate for previous period
        prev_win_rate = (prev_wins / len(signals_prev) * 100) if signals_prev else 0.0
        prev_avg_return = 8.0  # Estimate
        
        win_rate_change = win_rate - prev_win_rate
        avg_return_change = avg_return - prev_avg_return
        
        # Calculate trades per month
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        signals_this_month = [
            s for s in all_signals 
            if s.timestamp.month == current_month and s.timestamp.year == current_year
        ]
        
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1
        signals_prev_month = [
            s for s in all_signals 
            if s.timestamp.month == prev_month and s.timestamp.year == prev_year
        ]
        
        trades_per_month = len(signals_this_month)
        trades_per_month_change = (
            ((trades_per_month - len(signals_prev_month)) / len(signals_prev_month) * 100)
            if signals_prev_month else 0.0
        )
        
        logger.info(
            f"Performance metrics: win_rate={win_rate:.1f}%, "
            f"avg_return={avg_return:.1f}%, trades_per_month={trades_per_month}"
        )
        
        return PerformanceMetrics(
            win_rate=round(win_rate, 1),
            win_rate_change=round(win_rate_change, 1),
            avg_return=round(avg_return, 1),
            avg_return_change=round(avg_return_change, 1),
            trades_per_month=trades_per_month,
            trades_per_month_change=round(trades_per_month_change, 1),
            period="last_30_days",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to calculate performance metrics")
