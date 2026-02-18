"""FastAPI main application"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import settings
from src.utils.logger import get_logger
from src.routes import signals, auth
from src.routes.websocket import manager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Trading Signal System API")
    logger.info(f"Environment: {settings.openai_model}")
    yield
    # Shutdown
    logger.info("Shutting down Trading Signal System API")


# Initialize FastAPI app
app = FastAPI(
    title="Trading Signal Generator API",
    description="Multi-agent system for generating trading signals",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(signals.router, prefix="/api/v1", tags=["Signals"])

# New routers for enterprise UI
from src.routes import market, portfolio, performance
app.include_router(market.router, prefix="/api/v1/market", tags=["Market"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["Portfolio"])
app.include_router(performance.router, prefix="/api/v1/performance", tags=["Performance"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time signal updates"""
    from src.routes.websocket import manager
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")
            await websocket.send_json({"type": "pong", "message": "Connection active"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Trading Signal Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "trading-signal-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
