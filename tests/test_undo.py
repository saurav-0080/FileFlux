"""Unit tests for undo.py"""

import pytest
from datetime import datetime
from pathlib import Path
from app import database, history
from app.models import FileInfo
from app.undo import UndoManager


def make_conn(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    conn = database.connect()
    database.create_tables(conn)
    return conn


def test_undo_no_session(tmp_path, monkeypatch):
    conn = make_conn(tmp_path, monkeypatch)
    manager = UndoManager(conn)
    result = manager.undo_last_session()
    assert result["restored"] == 0


def test_undo_restores_file(tmp_path, monkeypatch):
    conn = make_conn(tmp_path, monkeypatch)

    # Create original and destination
    original = tmp_path / "original" / "file.txt"
    original.parent.mkdir()
    original.write_text("hello")

    dest = tmp_path / "Documents" / "file.txt"
    dest.parent.mkdir()

    # Simulate a move
    import shutil
    shutil.move(str(original), str(dest))

    # Record in database
    database.execute(conn, """
        INSERT INTO file_history (session_id, original_path, destination_path,
        filename, status, operation_time, undone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("S1", str(original), str(dest), "file.txt", "moved", datetime.now().isoformat(), 0))

    manager = UndoManager(conn)
    result = manager.undo_last_session()
    assert result["restored"] == 1
    assert result["failed"] == 0


def test_undo_skips_missing_file(tmp_path, monkeypatch):
    conn = make_conn(tmp_path, monkeypatch)

    database.execute(conn, """
        INSERT INTO file_history (session_id, original_path, destination_path,
        filename, status, operation_time, undone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("S2", "/nonexistent/original.txt", "/nonexistent/dest.txt",
          "original.txt", "moved", datetime.now().isoformat(), 0))

    manager = UndoManager(conn)
    result = manager.undo_last_session()
    assert result["skipped"] == 1