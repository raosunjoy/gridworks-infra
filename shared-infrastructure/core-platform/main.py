"""
GridWorks - AI-Powered Financial Infrastructure Platform
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.whatsapp.webhook import whatsapp_router
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 GridWorks starting up...")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("📴 GridWorks shutting down...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="GridWorks API",
        description="AI-Powered Financial Infrastructure Platform - Democratizing Financial Markets Globally",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include routers
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(whatsapp_router, prefix="/whatsapp")
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to GridWorks API",
            "description": "AI-Powered Financial Infrastructure Platform",
            "version": "1.0.0",
            "docs": "/docs" if settings.DEBUG else "Contact support for API documentation"
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "GridWorks API",
            "version": "1.0.0"
        }
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )