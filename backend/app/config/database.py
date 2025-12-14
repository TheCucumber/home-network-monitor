"""Database configuration and initialization."""
import sqlite3
import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
from .settings import settings


# Database schema
SCHEMA = """
-- Core ping results table
CREATE TABLE IF NOT EXISTS ping_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    latency REAL,
    success INTEGER NOT NULL,
    error TEXT
);

-- Indexes for efficient time-range queries
CREATE INDEX IF NOT EXISTS idx_host_timestamp ON ping_results(host, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_timestamp ON ping_results(timestamp DESC);

-- Host configuration table
CREATE TABLE IF NOT EXISTS hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at INTEGER NOT NULL
);
"""


class Database:
    """Database connection manager."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialized = False

    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def initialize(self):
        """Initialize database with schema and WAL mode."""
        if self._initialized:
            return

        conn = sqlite3.connect(self.db_path)
        try:
            # Enable WAL mode for better concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache

            # Create schema
            conn.executescript(SCHEMA)
            conn.commit()

            print(f"Database initialized at {self.db_path}")
            self._initialized = True
        finally:
            conn.close()

    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()):
        """Execute a query and return results."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

    def execute_many(self, query: str, params_list: list):
        """Execute a query with multiple parameter sets."""
        with self.get_connection() as conn:
            conn.executemany(query, params_list)

    def execute_update(self, query: str, params: tuple = ()):
        """Execute an update/insert/delete query."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid

    def vacuum(self):
        """Run VACUUM to reclaim space."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("VACUUM")
            print("Database VACUUM completed")
        finally:
            conn.close()


# Global database instance
db = Database(settings.database_path)


def init_database():
    """Initialize the database (called on startup)."""
    db.initialize()
