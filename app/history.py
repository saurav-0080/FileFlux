"""
History recording for FileFlux.

Records every file operation into the SQLite database so moves
can be reviewed and undone later.
"""

from datetime import datetime
from app import database
from app.models import FileInfo
from app.logger import setup_logger

logger = setup_logger()


def record_move(conn, session_id: str, file_info: FileInfo) -> None:
    """
    Record a successful file move in the database.

    Args:
        conn: Active SQLite connection.
        session_id: The current session identifier.
        file_info: The FileInfo object after a successful move.
    """
    database.execute(conn, """
        INSERT INTO file_history (
            session_id, original_path, destination_path,
            filename, category, sha256_hash, file_size,
            status, operation_time, undone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        str(file_info.path),
        str(file_info.destination_path),
        file_info.name,
        file_info.category,
        file_info.sha256_hash,
        file_info.size,
        "moved",
        datetime.now().isoformat(),
        0,
    ))
    logger.info(f"Recording file move: {file_info.name}")


def record_error(conn, session_id: str, file_info: FileInfo) -> None:
    """
    Record a failed file move in the database.

    Args:
        conn: Active SQLite connection.
        session_id: The current session identifier.
        file_info: The FileInfo object after a failed move.
    """
    database.execute(conn, """
        INSERT INTO file_history (
            session_id, original_path, destination_path,
            filename, category, sha256_hash, file_size,
            status, operation_time, undone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        str(file_info.path),
        "",
        file_info.name,
        file_info.category,
        file_info.sha256_hash,
        file_info.size,
        "failed",
        datetime.now().isoformat(),
        0,
    ))
    logger.info(f"Recording file error: {file_info.name}")


def get_last_session(conn) -> str :
    """
    Get the most recent session ID from the database.

    Returns:
        The session ID string, or None if no sessions exist.
    """
    row = database.fetch_one(conn, """
        SELECT session_id FROM file_history
        ORDER BY operation_time DESC LIMIT 1
    """)
    return row["session_id"] if row else None


def get_history(conn, session_id: str) -> list:
    """
    Get all records for a given session.

    Args:
        session_id: The session to retrieve.

    Returns:
        List of database rows.
    """
    return database.fetch_all(conn, """
        SELECT * FROM file_history
        WHERE session_id = ? AND undone = 0
        ORDER BY operation_time ASC
    """, (session_id,))


def get_statistics(conn) -> dict:
    """
    Get overall statistics from the database.

    Returns:
        Dict with total moves, errors, and sessions.
    """
    total = database.fetch_one(conn, "SELECT COUNT(*) as count FROM file_history WHERE status = 'moved'")
    errors = database.fetch_one(conn, "SELECT COUNT(*) as count FROM file_history WHERE status = 'failed'")
    sessions = database.fetch_one(conn, "SELECT COUNT(DISTINCT session_id) as count FROM file_history")
    return {
        "total_moves": total["count"],
        "total_errors": errors["count"],
        "total_sessions": sessions["count"],
    }