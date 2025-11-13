"""
Main application module for ArqLeads System.
FastAPI application setup and configuration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import init_db, check_database_health
from app.core.rate_limit import limiter

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting ArqLeads System...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AI Provider: {settings.AI_PROVIDER}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Check database health
    if check_database_health():
        logger.info("✅ Database health check passed")
    else:
        logger.warning("⚠️ Database health check failed")
    
    logger.info("✨ ArqLeads System ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down ArqLeads System...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema de Captación Automatizada de Leads para Estudios de Arquitectura",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else None,
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "components": {
            "database": "up" if db_healthy else "down",
            "api": "up",
        },
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
    }


# Ping endpoint
@app.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"message": "pong"}


# Import and include API routers
from app.api.chat import router as chat_router
from app.api.leads import router as leads_router
from app.api.analytics import router as analytics_router

# Mount API routers
app.include_router(
    chat_router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["Chat"]
)

app.include_router(
    leads_router,
    prefix=f"{settings.API_V1_STR}/leads",
    tags=["Leads"]
)

app.include_router(
    analytics_router,
    prefix=f"{settings.API_V1_STR}/analytics",
    tags=["Analytics"]
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
    )