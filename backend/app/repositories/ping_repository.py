"""Repository for ping data operations."""
from typing import List, Optional
from ..config.database import db
from ..models.schemas import PingResult, Host, HostStatus
import time


class PingRepository:
    """Handle database operations for ping data."""

    def insert_ping_result(self, result: PingResult) -> None:
        """Insert a ping result into the database."""
        query = """
            INSERT INTO ping_results (host, timestamp, latency, success, error)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            result.host,
            result.timestamp,
            result.latency,
            1 if result.success else 0,
            result.error
        )
        db.execute_update(query, params)

    def get_ping_data(self, host: str, start_time: int, end_time: int, limit: int = 1000) -> List[PingResult]:
        """
        Get ping data for a host within a time range.

        Args:
            host: Hostname or IP address
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
            limit: Maximum number of records to return

        Returns:
            List of PingResult objects
        """
        query = """
            SELECT host, timestamp, latency, success, error
            FROM ping_results
            WHERE host = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
            LIMIT ?
        """
        rows = db.execute_query(query, (host, start_time, end_time, limit))

        return [
            PingResult(
                host=row["host"],
                timestamp=row["timestamp"],
                latency=row["latency"],
                success=bool(row["success"]),
                error=row["error"]
            )
            for row in rows
        ]

    def get_current_status(self) -> List[HostStatus]:
        """
        Get current status for all hosts.

        Returns:
            List of HostStatus objects with recent ping data
        """
        hosts = self.get_hosts()
        status_list = []

        for host in hosts:
            # Get most recent ping
            recent_query = """
                SELECT timestamp, latency, success
                FROM ping_results
                WHERE host = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """
            recent = db.execute_query(recent_query, (host.hostname,))

            # Calculate 24h statistics
            now = int(time.time() * 1000)
            day_ago = now - (24 * 60 * 60 * 1000)

            stats_query = """
                SELECT
                    AVG(latency) as avg_latency,
                    COUNT(*) as total_pings,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_pings
                FROM ping_results
                WHERE host = ? AND timestamp >= ?
            """
            stats = db.execute_query(stats_query, (host.hostname, day_ago))

            # Build status object
            status = HostStatus(
                id=host.id,
                hostname=host.hostname,
                display_name=host.display_name,
                enabled=host.enabled,
                last_ping=None,
                latency=None,
                success=False,
                last_24h_avg=None,
                uptime_24h=None
            )

            if recent:
                status.last_ping = recent[0]["timestamp"]
                status.latency = recent[0]["latency"]
                status.success = bool(recent[0]["success"])

            if stats and stats[0]["total_pings"] > 0:
                status.last_24h_avg = stats[0]["avg_latency"]
                success_rate = (stats[0]["successful_pings"] / stats[0]["total_pings"]) * 100
                status.uptime_24h = round(success_rate, 2)

            status_list.append(status)

        return status_list

    def get_hosts(self) -> List[Host]:
        """Get all hosts from the database."""
        query = """
            SELECT id, hostname, display_name, enabled, created_at
            FROM hosts
            ORDER BY display_name ASC
        """
        rows = db.execute_query(query)

        return [
            Host(
                id=row["id"],
                hostname=row["hostname"],
                display_name=row["display_name"],
                enabled=bool(row["enabled"]),
                created_at=row["created_at"]
            )
            for row in rows
        ]

    def get_host_by_id(self, host_id: int) -> Optional[Host]:
        """Get a specific host by ID."""
        query = """
            SELECT id, hostname, display_name, enabled, created_at
            FROM hosts
            WHERE id = ?
        """
        rows = db.execute_query(query, (host_id,))

        if not rows:
            return None

        row = rows[0]
        return Host(
            id=row["id"],
            hostname=row["hostname"],
            display_name=row["display_name"],
            enabled=bool(row["enabled"]),
            created_at=row["created_at"]
        )

    def get_host_by_hostname(self, hostname: str) -> Optional[Host]:
        """Get a specific host by hostname."""
        query = """
            SELECT id, hostname, display_name, enabled, created_at
            FROM hosts
            WHERE hostname = ?
        """
        rows = db.execute_query(query, (hostname,))

        if not rows:
            return None

        row = rows[0]
        return Host(
            id=row["id"],
            hostname=row["hostname"],
            display_name=row["display_name"],
            enabled=bool(row["enabled"]),
            created_at=row["created_at"]
        )

    def add_host(self, hostname: str, display_name: str) -> Host:
        """Add a new host to monitor."""
        created_at = int(time.time() * 1000)
        query = """
            INSERT INTO hosts (hostname, display_name, enabled, created_at)
            VALUES (?, ?, 1, ?)
        """
        host_id = db.execute_update(query, (hostname, display_name, created_at))

        return Host(
            id=host_id,
            hostname=hostname,
            display_name=display_name,
            enabled=True,
            created_at=created_at
        )

    def delete_host(self, host_id: int) -> bool:
        """
        Delete a host and all its ping data.

        Returns:
            True if host was deleted, False if not found
        """
        # First check if host exists
        host = self.get_host_by_id(host_id)
        if not host:
            return False

        # Delete ping data
        db.execute_update("DELETE FROM ping_results WHERE host = ?", (host.hostname,))

        # Delete host
        db.execute_update("DELETE FROM hosts WHERE id = ?", (host_id,))

        return True

    def delete_old_pings(self, retention_days: int) -> int:
        """
        Delete ping records older than retention_days.

        Returns:
            Number of records deleted
        """
        cutoff_time = int((time.time() - (retention_days * 24 * 60 * 60)) * 1000)

        # Count records to be deleted
        count_query = "SELECT COUNT(*) as count FROM ping_results WHERE timestamp < ?"
        result = db.execute_query(count_query, (cutoff_time,))
        count = result[0]["count"] if result else 0

        # Delete old records
        db.execute_update("DELETE FROM ping_results WHERE timestamp < ?", (cutoff_time,))

        return count

    def calculate_stats(self, host: str, start_time: int, end_time: int) -> dict:
        """
        Calculate statistics for ping data in a time range.

        Returns:
            Dictionary with avg_latency, min_latency, max_latency, success_rate
        """
        query = """
            SELECT
                AVG(latency) as avg_latency,
                MIN(latency) as min_latency,
                MAX(latency) as max_latency,
                COUNT(*) as total_pings,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_pings
            FROM ping_results
            WHERE host = ? AND timestamp BETWEEN ? AND ?
        """
        rows = db.execute_query(query, (host, start_time, end_time))

        if not rows or rows[0]["total_pings"] == 0:
            return {
                "avg_latency": None,
                "min_latency": None,
                "max_latency": None,
                "success_rate": 0.0
            }

        row = rows[0]
        success_rate = (row["successful_pings"] / row["total_pings"]) * 100 if row["total_pings"] > 0 else 0

        return {
            "avg_latency": round(row["avg_latency"], 2) if row["avg_latency"] else None,
            "min_latency": round(row["min_latency"], 2) if row["min_latency"] else None,
            "max_latency": round(row["max_latency"], 2) if row["max_latency"] else None,
            "success_rate": round(success_rate, 2)
        }


# Global repository instance
ping_repository = PingRepository()
