"""FastAPI routes for the network monitor API."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from ..models.schemas import (
    Host,
    HostCreate,
    HostsResponse,
    HostStatus,
    CurrentStatusResponse,
    PingDataResponse,
    PingResult
)
from ..repositories.ping_repository import ping_repository
from ..services.scheduler_service import scheduler_service
from ..services.cleanup_service import cleanup_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/hosts", response_model=HostsResponse)
async def get_hosts():
    """Get all configured hosts."""
    try:
        hosts = ping_repository.get_hosts()
        return HostsResponse(hosts=hosts)
    except Exception as e:
        logger.error(f"Error fetching hosts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch hosts")


@router.post("/hosts", response_model=Host, status_code=201)
async def add_host(host_create: HostCreate):
    """Add a new host to monitor."""
    try:
        # Check if hostname already exists
        existing = ping_repository.get_host_by_hostname(host_create.hostname)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Host '{host_create.hostname}' already exists"
            )

        # Add the host
        host = ping_repository.add_host(
            hostname=host_create.hostname,
            display_name=host_create.display_name
        )

        logger.info(f"Added new host: {host.hostname} ({host.display_name})")
        return host

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding host: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to add host")


@router.delete("/hosts/{host_id}", status_code=204)
async def delete_host(host_id: int):
    """Delete a host and all its ping data."""
    try:
        success = ping_repository.delete_host(host_id)
        if not success:
            raise HTTPException(status_code=404, detail="Host not found")

        logger.info(f"Deleted host with ID: {host_id}")
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting host: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete host")


@router.get("/current-status", response_model=CurrentStatusResponse)
async def get_current_status():
    """Get current status for all hosts with recent statistics."""
    try:
        status_list = ping_repository.get_current_status()
        return CurrentStatusResponse(hosts=status_list)
    except Exception as e:
        logger.error(f"Error fetching current status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch current status")


@router.get("/ping-data/{hostname}", response_model=PingDataResponse)
async def get_ping_data(
    hostname: str,
    start: int = Query(..., description="Start timestamp in milliseconds"),
    end: int = Query(..., description="End timestamp in milliseconds"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records")
):
    """
    Get ping data for a specific host within a time range.

    Args:
        hostname: Hostname or IP address
        start: Start timestamp in milliseconds
        end: End timestamp in milliseconds
        limit: Maximum number of records to return (default 1000, max 10000)
    """
    try:
        # Validate time range
        if start >= end:
            raise HTTPException(
                status_code=400,
                detail="Start time must be before end time"
            )

        # Get ping data
        data = ping_repository.get_ping_data(
            host=hostname,
            start_time=start,
            end_time=end,
            limit=limit
        )

        # Calculate statistics
        stats = ping_repository.calculate_stats(
            host=hostname,
            start_time=start,
            end_time=end
        )

        return PingDataResponse(
            host=hostname,
            data=data,
            stats=stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ping data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch ping data")


@router.post("/ping/{hostname}")
async def manual_ping(hostname: str):
    """Manually trigger a ping for a specific host."""
    try:
        result = scheduler_service.ping_now(hostname)
        return result
    except Exception as e:
        logger.error(f"Error in manual ping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to execute ping")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "scheduler_running": scheduler_service.running,
        "cleanup_running": cleanup_service.running
    }


@router.post("/admin/cleanup")
async def trigger_cleanup():
    """Manually trigger database cleanup (admin endpoint)."""
    try:
        result = cleanup_service.cleanup_now()
        return result
    except Exception as e:
        logger.error(f"Error in manual cleanup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to trigger cleanup")


@router.post("/admin/vacuum")
async def trigger_vacuum():
    """Manually trigger database VACUUM (admin endpoint)."""
    try:
        result = cleanup_service.vacuum_now()
        return result
    except Exception as e:
        logger.error(f"Error in manual vacuum: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to trigger vacuum")


@router.get("/admin/cleanup-status")
async def get_cleanup_status():
    """Get cleanup service status (admin endpoint)."""
    try:
        return cleanup_service.get_status()
    except Exception as e:
        logger.error(f"Error fetching cleanup status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch cleanup status")
