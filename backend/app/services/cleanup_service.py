"""Service for database cleanup and maintenance."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from ..config.settings import settings
from ..config.database import db
from ..repositories.ping_repository import ping_repository

logger = logging.getLogger(__name__)


class CleanupService:
    """Handle database cleanup and maintenance tasks."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running = False
        self.last_cleanup = None
        self.last_vacuum = None

    def start(self):
        """Start the cleanup scheduler."""
        if self.running:
            logger.warning("Cleanup service already running")
            return

        logger.info(f"Starting cleanup service (runs daily at {settings.cleanup_hour}:00)")

        # Add daily cleanup job
        self.scheduler.add_job(
            self._run_cleanup,
            trigger=CronTrigger(hour=settings.cleanup_hour, minute=0),
            id="daily_cleanup",
            name="Daily database cleanup",
            replace_existing=True
        )

        # Add monthly vacuum job (first day of month at cleanup hour)
        self.scheduler.add_job(
            self._run_vacuum,
            trigger=CronTrigger(day=1, hour=settings.cleanup_hour, minute=30),
            id="monthly_vacuum",
            name="Monthly database VACUUM",
            replace_existing=True
        )

        self.scheduler.start()
        self.running = True
        logger.info("Cleanup service started")

    def stop(self):
        """Stop the cleanup scheduler."""
        if not self.running:
            return

        logger.info("Stopping cleanup service")
        self.scheduler.shutdown(wait=True)
        self.running = False
        logger.info("Cleanup service stopped")

    async def _run_cleanup(self):
        """Execute database cleanup - delete old ping records."""
        try:
            logger.info(f"Starting cleanup: deleting pings older than {settings.retention_days} days")

            deleted_count = ping_repository.delete_old_pings(settings.retention_days)

            self.last_cleanup = datetime.now()
            logger.info(f"Cleanup completed: deleted {deleted_count} old ping records")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)

    async def _run_vacuum(self):
        """Execute database VACUUM to reclaim space."""
        try:
            logger.info("Starting database VACUUM")

            db.vacuum()

            self.last_vacuum = datetime.now()
            logger.info("Database VACUUM completed successfully")

        except Exception as e:
            logger.error(f"Error during VACUUM: {e}", exc_info=True)

    def cleanup_now(self) -> dict:
        """
        Manually trigger cleanup immediately.

        Returns:
            Dictionary with cleanup results
        """
        try:
            deleted_count = ping_repository.delete_old_pings(settings.retention_days)
            self.last_cleanup = datetime.now()

            return {
                "success": True,
                "deleted_count": deleted_count,
                "timestamp": self.last_cleanup.isoformat()
            }
        except Exception as e:
            logger.error(f"Error in manual cleanup: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "deleted_count": 0
            }

    def vacuum_now(self) -> dict:
        """
        Manually trigger database VACUUM immediately.

        Returns:
            Dictionary with vacuum results
        """
        try:
            db.vacuum()
            self.last_vacuum = datetime.now()

            return {
                "success": True,
                "timestamp": self.last_vacuum.isoformat()
            }
        except Exception as e:
            logger.error(f"Error in manual vacuum: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_status(self) -> dict:
        """Get cleanup service status."""
        return {
            "running": self.running,
            "last_cleanup": self.last_cleanup.isoformat() if self.last_cleanup else None,
            "last_vacuum": self.last_vacuum.isoformat() if self.last_vacuum else None,
            "retention_days": settings.retention_days,
            "cleanup_hour": settings.cleanup_hour
        }


# Global cleanup service instance
cleanup_service = CleanupService()
