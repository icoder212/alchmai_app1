"""Signal generation routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from src.models.signal import SignalRequest, SignalResponse, TradingSignal
from src.utils.logger import get_logger
from src.routes.websocket import manager

router = APIRouter()
logger = get_logger(__name__)

# Singleton orchestrator — instantiated once so FinBERT loads only on first request
_orchestrator = None

def _get_orchestrator():
    """Return the singleton TradingSignalOrchestrator, creating it on first call."""
    global _orchestrator
    if _orchestrator is None:
        from src.agents.orchestrator import TradingSignalOrchestrator
        logger.info("Initializing TradingSignalOrchestrator singleton...")
        _orchestrator = TradingSignalOrchestrator()
        logger.info("TradingSignalOrchestrator singleton ready")
    return _orchestrator


class ActiveSignalsResponse(BaseModel):
    """Response model for active signals endpoint"""
    total: int
    buy: int
    hold: int
    sell: int
    timestamp: datetime


@router.post("/signal", response_model=SignalResponse)
async def generate_signal(
    request: SignalRequest,
    # current_user: User = Depends(get_current_user)  # Will be added when auth is ready
):
    """
    Generate trading signal for given instrument
    
    Args:
        request: SignalRequest with instrument symbol
        
    Returns:
        SignalResponse with generated signal or error
    """
    try:
        timeframe = request.timeframe or "15m"
        model = request.model or "gpt-4o-mini"
        logger.info(f"Generating signal for {request.instrument} on {timeframe} timeframe using {model}")

        # Use singleton orchestrator (FinBERT loads only once)
        orchestrator = _get_orchestrator()
        signal = orchestrator.generate_signal(request.instrument, timeframe=timeframe, model=model)
        
        # Store signal in history
        from src.utils.signal_store import signal_store
        signal_store.add_signal(signal)
        
        # Broadcast to WebSocket clients
        try:
            await manager.broadcast({
                "type": "new_signal",
                "data": signal.model_dump(mode='json')
            })
        except Exception as e:
            logger.warning(f"Failed to broadcast signal: {e}")
        
        return SignalResponse(
            success=True,
            signal=signal,
            message="Signal generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating signal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[TradingSignal])
async def get_signal_history(
    limit: int = 20,
    instrument: Optional[str] = None
):
    """
    Get signal generation history
    
    Args:
        limit: Number of signals to return (default 20, max 100)
        instrument: Filter by instrument symbol (optional)
        
    Returns:
        List of trading signals
    """
    from src.utils.signal_store import signal_store
    
    # Cap at 100
    limit = min(limit, 100)
    
    if instrument:
        signals = signal_store.get_by_instrument(instrument, limit)
    else:
        signals = signal_store.get_recent(limit)
    
    logger.info(f"Retrieved {len(signals)} signals from history (instrument={instrument}, limit={limit})")
    return signals


@router.get("/signals", response_model=List[TradingSignal])
async def get_signal_history_legacy(
    # current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """
    Get signal history (paginated) - Legacy endpoint
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of trading signals
    """
    from src.utils.signal_store import signal_store
    
    all_signals = signal_store.get_recent(100)
    signals = all_signals[skip:skip+limit]
    
    logger.info(f"Retrieved {len(signals)} signals from history (skip={skip}, limit={limit})")
    return signals


@router.get("/signals/{signal_id}", response_model=TradingSignal)
async def get_signal(signal_id: int):
    """
    Get specific signal by ID
    
    Args:
        signal_id: Signal ID
        
    Returns:
        Trading signal
    """
    # TODO: Implement database query
    raise HTTPException(status_code=404, detail="Signal not found")


@router.get("/active", response_model=ActiveSignalsResponse)
async def get_active_signals():
    """
    Get count of active signals from last 24 hours
    
    Returns:
        ActiveSignalsResponse with total, buy, hold, sell counts
    """
    from datetime import timedelta
    from src.utils.signal_store import signal_store
    
    try:
        # Get signals from last 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        all_signals = signal_store.get_recent(1000)  # Get more to filter by time
        
        # Filter by time
        recent_signals = [
            s for s in all_signals 
            if s.timestamp >= cutoff_time
        ]
        
        # Count by type
        buy_count = sum(1 for s in recent_signals if s.signal == "BUY")
        sell_count = sum(1 for s in recent_signals if s.signal == "SELL")
        hold_count = sum(1 for s in recent_signals if s.signal == "NEUTRAL" or s.signal == "HOLD")
        total = len(recent_signals)
        
        logger.info(f"Active signals: total={total}, buy={buy_count}, hold={hold_count}, sell={sell_count}")
        
        return ActiveSignalsResponse(
            total=total,
            buy=buy_count,
            hold=hold_count,
            sell=sell_count,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error counting active signals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to count active signals")
