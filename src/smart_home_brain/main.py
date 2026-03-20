#!/usr/bin/env python3
"""
Smart Home AI Brain - Main Entry Point
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.device_manager import DeviceManager
from .core.pattern_learner import PatternLearner
from .api.routes import devices, chat, health
from .ai.llm_client import LLMClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
device_manager: DeviceManager = None
pattern_learner: PatternLearner = None
llm_client: LLMClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    global device_manager, pattern_learner, llm_client
    
    logger.info("🚀 Starting Smart Home AI Brain...")
    
    # Initialize device manager
    device_manager = DeviceManager()
    await device_manager.discover_devices()
    logger.info(f"✅ Discovered {len(device_manager.devices)} devices")
    
    # Initialize pattern learner
    pattern_learner = PatternLearner()
    await pattern_learner.load_patterns()
    logger.info("✅ Pattern learner initialized")
    
    # Initialize LLM client
    llm_client = LLMClient()
    await llm_client.initialize()
    logger.info("✅ LLM client initialized")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Smart Home AI Brain...")
    await device_manager.cleanup()
    await llm_client.cleanup()


# Create FastAPI app
app = FastAPI(
    title="Smart Home AI Brain",
    description="Sistema inteligente de automatización del hogar con IA",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Smart Home AI Brain",
        "version": "0.1.0",
        "status": "running",
        "devices": len(device_manager.devices) if device_manager else 0,
    }


def main():
    """Main entry point."""
    import uvicorn
    uvicorn.run(
        "smart_home_brain.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()