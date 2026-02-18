"""Portfolio routes"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel

from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class PortfolioSummary(BaseModel):
    total_value: float
    change_percent: float
    change_type: str  # "positive" or "negative"
    has_portfolio: bool
    timestamp: datetime


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary():
    """
    Get portfolio summary
    
    For POC, returns empty portfolio data.
    Future: Integrate with actual portfolio management system.
    
    Returns:
        Portfolio summary with total value and change
    """
    try:
        # For POC, return empty portfolio
        # TODO: Integrate with actual portfolio management system
        return PortfolioSummary(
            total_value=0.0,
            change_percent=0.0,
            change_type="positive",
            has_portfolio=False,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio summary")
