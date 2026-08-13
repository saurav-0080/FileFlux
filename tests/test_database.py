"""Unit tests for database.py"""

from app import database


def test_connect_creates_connection(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    conn = database.connect()
    assert conn is not None
    database.close(conn)


def test_create_tables_succeeds(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    conn = database.connect()
    database.create_tables(conn)
    result = database.fetch_all(
        conn, "SELECT name FROM sqlite_master WHERE type='table'"
    )
    table_names = [r["name"] for r in result]
    assert "file_history" in table_names
    database.close(conn)


def test_execute_and_fetch(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    conn = database.connect()
    database.create_tables(conn)
    database.execute(
        conn,
        """
        INSERT INTO file_history (session_id, original_path, destination_path,
        filename, status, operation_time, undone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        ("S1", "/orig", "/dest", "file.txt", "moved", "2026-01-01", 0),
    )
    row = database.fetch_one(
        conn, "SELECT * FROM file_history WHERE session_id = ?", ("S1",)
    )
    assert row["filename"] == "file.txt"
    database.close(conn)
