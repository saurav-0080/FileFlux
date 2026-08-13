"""
Database connection and management for FileFlux.

Handles SQLite connection, table creation, and query execution.
The database is created automatically if it doesn't exist.
"""

import sqlite3
from pathlib import Path

from app.logger import setup_logger

logger = setup_logger()

DB_PATH = Path("database/organizer.db")


def connect() -> sqlite3.Connection:
    """Connect to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    logger.info("Database connected")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Create required tables if they don't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS file_history (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id       TEXT    NOT NULL,
            original_path    TEXT    NOT NULL,
            destination_path TEXT    NOT NULL,
            filename         TEXT    NOT NULL,
            category         TEXT,
            sha256_hash      TEXT,
            file_size        INTEGER,
            status           TEXT    NOT NULL,
            operation_time   TEXT    NOT NULL,
            undone           INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    logger.info("Tables created")


def execute(conn: sqlite3.Connection, query: str, params: tuple = ()) -> sqlite3.Cursor:
    """Execute a write query."""
    cursor = conn.execute(query, params)
    conn.commit()
    return cursor


def fetch_all(conn: sqlite3.Connection, query: str, params: tuple = ()):
    """Fetch all rows for a query."""
    return conn.execute(query, params).fetchall()


def fetch_one(conn: sqlite3.Connection, query: str, params: tuple = ()):
    """Fetch a single row for a query."""
    return conn.execute(query, params).fetchone()


def close(conn: sqlite3.Connection) -> None:
    """Close the database connection."""
    conn.close()
    logger.info("Database connection closed")
