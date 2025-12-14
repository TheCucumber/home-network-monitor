"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"

    # Ping Configuration
    ping_interval: int = 60  # seconds
    ping_timeout: int = 5    # seconds
    ping_retries: int = 2

    # Database Configuration
    database_path: str = "./data/pings.db"

    # Data Retention
    retention_days: int = 120
    cleanup_hour: int = 2  # 2 AM

    # Monitored Hosts
    monitored_hosts: str = "router.local,8.8.8.8,1.1.1.1"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_monitored_hosts_list(self) -> List[str]:
        """Parse and return list of monitored hosts."""
        return [host.strip() for host in self.monitored_hosts.split(",") if host.strip()]

    def get_cors_origins_list(self) -> List[str]:
        """Parse and return list of CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# Global settings instance
settings = Settings()
