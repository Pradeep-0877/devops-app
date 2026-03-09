from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.models.database import connect_to_mongodb, close_mongodb_connection
from app.api import auth, tasks, ai


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    settings.LOG_FILE,
    rotation="10 MB",
    retention="30 days",
    level=settings.LOG_LEVEL
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Database type: {settings.DATABASE_TYPE}")
    
    if settings.DATABASE_TYPE == "mongodb":
        await connect_to_mongodb()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    
    if settings.DATABASE_TYPE == "mongodb":
        await close_mongodb_connection()
    
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Enterprise Automation Platform with AI Integration",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.API_VERSION
    }


# Include routers
app.include_router(
    auth.router,
    prefix=f"/api/{settings.API_VERSION}/auth",
    tags=["Authentication"]
)

app.include_router(
    tasks.router,
    prefix=f"/api/{settings.API_VERSION}/tasks",
    tags=["Tasks"]
)

app.include_router(
    ai.router,
    prefix=f"/api/{settings.API_VERSION}/ai",
    tags=["AI"]
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
