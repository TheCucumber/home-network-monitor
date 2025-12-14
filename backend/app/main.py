"""FastAPI application entry point."""
import logging
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config.settings import settings
from .config.database import init_database, db
from .repositories.ping_repository import ping_repository
from .services.scheduler_service import scheduler_service
from .services.cleanup_service import cleanup_service
from .routers import api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Starting Home Network Monitor backend")

    # Initialize database
    logger.info("Initializing database...")
    init_database()

    # Initialize monitored hosts from environment
    logger.info("Initializing monitored hosts...")
    monitored_hosts = settings.get_monitored_hosts_list()
    for hostname in monitored_hosts:
        existing = ping_repository.get_host_by_hostname(hostname)
        if not existing:
            # Add with hostname as display name (can be customized later)
            display_name = hostname.split('.')[0].title() if '.' in hostname else hostname
            ping_repository.add_host(hostname, display_name)
            logger.info(f"Added host: {hostname} ({display_name})")

    # Start ping scheduler
    logger.info("Starting ping scheduler...")
    scheduler_service.start()

    # Start cleanup service
    logger.info("Starting cleanup service...")
    cleanup_service.start()

    logger.info("Backend startup complete")

    yield

    # Shutdown
    logger.info("Shutting down backend...")

    # Stop schedulers
    scheduler_service.stop()
    cleanup_service.stop()

    logger.info("Backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Home Network Monitor API",
    description="API for monitoring network hosts with ping latency tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Home Network Monitor API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
