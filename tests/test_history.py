"""Unit tests for history.py"""

import pytest
from datetime import datetime
from pathlib import Path
from app import database, history
from app.models import FileInfo


def make_conn(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    conn = database.connect()
    database.create_tables(conn)
    return conn


def make_file_info(tmp_path, filename="test.pdf"):
    f = tmp_path / filename
    f.write_text("content")
    return FileInfo(
        name=f.name,
        extension=f.suffix.lower(),
        path=f,
        parent_directory=tmp_path,
        size=f.stat().st_size,
        created_time=datetime.now(),
        modified_time=datetime.now(),
        is_hidden=False,
        category="Documents",
        destination_path=tmp_path / "Documents" / filename,
        moved=True,
    )


def test_record_move(tmp_path, monkeypatch):
    conn = make_conn(tmp_path, monkeypatch)
    fi = make_file_info(tmp_path)
    history.record_move(conn, "S1", fi)
    row = database.fetch_one(conn, "SELECT * FROM file_history WHERE session_id = ?", ("S1",))
    assert row["filename"] == "test.pdf"
    assert row["status"] == "moved"


def test_get_last_session(tmp_path, monkeypatch):
    conn = make_conn(tmp_path, monkeypatch)
    fi = make_file_info(tmp_path)
    history.record_move(conn, "SESSION-001", fi)
    result = history.get_last_session(conn)
    assert result == "SESSION-001"


def test_get_history(tmp_path, monkeypatch):
    conn = make_conn(tmp_path, monkeypatch)
    fi = make_file_info(tmp_path)
    history.record_move(conn, "SESSION-002", fi)
    records = history.get_history(conn, "SESSION-002")
    assert len(records) == 1


def test_get_statistics(tmp_path, monkeypatch):
    conn = make_conn(tmp_path, monkeypatch)
    fi = make_file_info(tmp_path)
    history.record_move(conn, "SESSION-003", fi)
    stats = history.get_statistics(conn)
    assert stats["total_moves"] == 1
    assert stats["total_sessions"] == 1