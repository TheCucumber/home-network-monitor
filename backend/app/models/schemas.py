"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List


class PingResult(BaseModel):
    """Ping result data model."""
    host: str
    timestamp: int  # Unix timestamp in milliseconds
    latency: Optional[float] = None  # Latency in milliseconds, None for failures
    success: bool
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "host": "8.8.8.8",
                "timestamp": 1702468800000,
                "latency": 12.5,
                "success": True,
                "error": None
            }
        }


class Host(BaseModel):
    """Host configuration model."""
    id: Optional[int] = None
    hostname: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    enabled: bool = True
    created_at: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "hostname": "router.local",
                "display_name": "Home Router",
                "enabled": True,
                "created_at": 1702468800000
            }
        }


class HostCreate(BaseModel):
    """Model for creating a new host."""
    hostname: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "hostname": "192.168.1.1",
                "display_name": "Router"
            }
        }


class HostStatus(BaseModel):
    """Host status with recent ping statistics."""
    id: int
    hostname: str
    display_name: str
    enabled: bool
    last_ping: Optional[int] = None  # Unix timestamp in milliseconds
    latency: Optional[float] = None
    success: bool = False
    last_24h_avg: Optional[float] = None
    uptime_24h: Optional[float] = None  # Percentage

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "hostname": "8.8.8.8",
                "display_name": "Google DNS",
                "enabled": True,
                "last_ping": 1702468800000,
                "latency": 12.5,
                "success": True,
                "last_24h_avg": 15.2,
                "uptime_24h": 99.8
            }
        }


class PingDataRequest(BaseModel):
    """Request model for ping data retrieval."""
    host: str
    start: int  # Unix timestamp in milliseconds
    end: int    # Unix timestamp in milliseconds

    class Config:
        json_schema_extra = {
            "example": {
                "host": "8.8.8.8",
                "start": 1702468800000,
                "end": 1702555200000
            }
        }


class PingDataResponse(BaseModel):
    """Response model for ping data."""
    host: str
    data: List[PingResult]
    stats: dict

    class Config:
        json_schema_extra = {
            "example": {
                "host": "8.8.8.8",
                "data": [
                    {
                        "host": "8.8.8.8",
                        "timestamp": 1702468800000,
                        "latency": 12.5,
                        "success": True,
                        "error": None
                    }
                ],
                "stats": {
                    "avg_latency": 15.2,
                    "min_latency": 8.1,
                    "max_latency": 45.3,
                    "success_rate": 99.2
                }
            }
        }


class HostsResponse(BaseModel):
    """Response model for hosts list."""
    hosts: List[Host]


class CurrentStatusResponse(BaseModel):
    """Response model for current status of all hosts."""
    hosts: List[HostStatus]
