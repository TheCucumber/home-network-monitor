"""Service for executing ping operations."""
import time
from typing import Optional
from pythonping import ping
from ..models.schemas import PingResult
from ..config.settings import settings


class PingService:
    """Handle ping execution with retry logic."""

    def __init__(self, timeout: int = None, retries: int = None):
        """
        Initialize ping service.

        Args:
            timeout: Ping timeout in seconds (default from settings)
            retries: Number of retry attempts (default from settings)
        """
        self.timeout = timeout or settings.ping_timeout
        self.retries = retries or settings.ping_retries

    def execute_ping(self, host: str) -> PingResult:
        """
        Execute a ping to a host with retry logic.

        Args:
            host: Hostname or IP address to ping

        Returns:
            PingResult object with ping data
        """
        timestamp = int(time.time() * 1000)

        for attempt in range(self.retries + 1):
            try:
                # Execute ping (send 1 packet)
                response = ping(
                    host,
                    count=1,
                    timeout=self.timeout,
                    verbose=False
                )

                # Check if ping was successful
                if response.success():
                    # Get latency in milliseconds
                    latency_ms = response.rtt_avg_ms

                    return PingResult(
                        host=host,
                        timestamp=timestamp,
                        latency=round(latency_ms, 2),
                        success=True,
                        error=None
                    )
                else:
                    # Ping failed but no exception - timeout or unreachable
                    if attempt < self.retries:
                        continue

                    return PingResult(
                        host=host,
                        timestamp=timestamp,
                        latency=None,
                        success=False,
                        error="Host unreachable or timeout"
                    )

            except Exception as e:
                # Error occurred during ping
                if attempt < self.retries:
                    # Retry
                    time.sleep(0.1)  # Small delay before retry
                    continue

                # All retries exhausted
                return PingResult(
                    host=host,
                    timestamp=timestamp,
                    latency=None,
                    success=False,
                    error=str(e)
                )

        # Should not reach here, but handle it
        return PingResult(
            host=host,
            timestamp=timestamp,
            latency=None,
            success=False,
            error="Maximum retries exceeded"
        )

    async def execute_ping_async(self, host: str) -> PingResult:
        """
        Execute ping asynchronously (wraps sync ping).

        Args:
            host: Hostname or IP address to ping

        Returns:
            PingResult object with ping data
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute_ping, host)


# Global ping service instance
ping_service = PingService()
