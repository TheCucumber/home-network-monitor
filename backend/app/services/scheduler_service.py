"""Scheduler service for periodic ping execution."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import List
import logging

from ..config.settings import settings
from ..repositories.ping_repository import ping_repository
from ..services.ping_service import ping_service

logger = logging.getLogger(__name__)


class SchedulerService:
    """Manage periodic ping execution for all hosts."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)

    def start(self):
        """Start the ping scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return

        logger.info(f"Starting ping scheduler with {settings.ping_interval}s interval")

        # Add ping job
        self.scheduler.add_job(
            self._ping_all_hosts,
            trigger=IntervalTrigger(seconds=settings.ping_interval),
            id="ping_all_hosts",
            name="Ping all monitored hosts",
            replace_existing=True
        )

        self.scheduler.start()
        self.running = True
        logger.info("Ping scheduler started")

    def stop(self):
        """Stop the ping scheduler."""
        if not self.running:
            return

        logger.info("Stopping ping scheduler")
        self.scheduler.shutdown(wait=True)
        self.executor.shutdown(wait=True)
        self.running = False
        logger.info("Ping scheduler stopped")

    async def _ping_all_hosts(self):
        """Execute pings for all monitored hosts."""
        try:
            # Get all enabled hosts
            hosts = ping_repository.get_hosts()
            enabled_hosts = [h for h in hosts if h.enabled]

            if not enabled_hosts:
                logger.debug("No enabled hosts to ping")
                return

            logger.debug(f"Pinging {len(enabled_hosts)} hosts")

            # Execute pings concurrently
            tasks = [
                self._ping_and_store(host.hostname)
                for host in enabled_hosts
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes and failures
            successes = sum(1 for r in results if isinstance(r, bool) and r)
            failures = len(results) - successes

            logger.info(f"Ping round completed: {successes} successful, {failures} failed")

        except Exception as e:
            logger.error(f"Error in ping scheduler: {e}", exc_info=True)

    async def _ping_and_store(self, host: str) -> bool:
        """
        Ping a single host and store the result.

        Returns:
            True if ping was successful, False otherwise
        """
        try:
            # Execute ping asynchronously
            result = await ping_service.execute_ping_async(host)

            # Store result in database
            ping_repository.insert_ping_result(result)

            if result.success:
                logger.debug(f"Ping to {host}: {result.latency}ms")
            else:
                logger.warning(f"Ping to {host} failed: {result.error}")

            return result.success

        except Exception as e:
            logger.error(f"Error pinging {host}: {e}", exc_info=True)
            return False

    def ping_now(self, host: str) -> dict:
        """
        Manually trigger a ping for a specific host.

        Args:
            host: Hostname or IP to ping

        Returns:
            Dictionary with ping result
        """
        try:
            result = ping_service.execute_ping(host)
            ping_repository.insert_ping_result(result)

            return {
                "success": result.success,
                "latency": result.latency,
                "timestamp": result.timestamp,
                "error": result.error
            }
        except Exception as e:
            logger.error(f"Error in manual ping: {e}", exc_info=True)
            return {
                "success": False,
                "latency": None,
                "timestamp": None,
                "error": str(e)
            }


# Global scheduler instance
scheduler_service = SchedulerService()
