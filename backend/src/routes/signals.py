"""Signal generation routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from src.models.signal import SignalRequest, SignalResponse, TradingSignal
from src.utils.logger import get_logger
from src.routes.websocket import manager

router = APIRouter()
logger = get_logger(__name__)


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
        logger.info(f"Generating signal for {request.instrument}")
        
        # Import and use orchestrator
        from src.agents.orchestrator import TradingSignalOrchestrator
        orchestrator = TradingSignalOrchestrator()
        signal = orchestrator.generate_signal(request.instrument)
        
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
