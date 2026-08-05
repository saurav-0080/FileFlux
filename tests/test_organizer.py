"""
Unit tests for organizer.py
"""

import pytest
from pathlib import Path
from datetime import datetime
from app.models import FileInfo
from app.organizer import Organizer

FAKE_RULES = {
    "Images": [".jpg", ".png"],
    "Videos": [".mp4", ".mov"],
    "Documents": [".pdf", ".docx"],
}


def make_file_info(tmp_path, filename="test.pdf"):
    """Helper to create a real file and matching FileInfo."""
    file = tmp_path / filename
    file.write_text("dummy content")
    return FileInfo(
        name=file.name,
        extension=file.suffix.lower(),
        path=file,
        parent_directory=tmp_path,
        size=file.stat().st_size,
        created_time=datetime.now(),
        modified_time=datetime.now(),
        is_hidden=False,
    )


def test_create_category_folder(tmp_path):
    org = Organizer(tmp_path, FAKE_RULES)
    folder = org.create_category_folder("Images")
    assert folder.exists()
    assert folder.name == "Images"


def test_handle_duplicate_name(tmp_path):
    existing = tmp_path / "resume.pdf"
    existing.write_text("original")
    org = Organizer(tmp_path, FAKE_RULES)
    result = org.handle_duplicate_name(existing)
    assert result.name == "resume(1).pdf"


def test_handle_duplicate_name_no_conflict(tmp_path):
    destination = tmp_path / "newfile.pdf"
    org = Organizer(tmp_path, FAKE_RULES)
    result = org.handle_duplicate_name(destination)
    assert result == destination


def test_move_file(tmp_path):
    file_info = make_file_info(tmp_path, "photo.jpg")
    file_info.category = "Images"
    org = Organizer(tmp_path, FAKE_RULES)
    result = org.move_file(file_info)
    assert result.moved is True
    assert result.destination_path.exists()


def test_create_summary(tmp_path):
    file_info = make_file_info(tmp_path, "doc.pdf")
    file_info.moved = True
    org = Organizer(tmp_path, FAKE_RULES)
    summary = org.create_summary([file_info], 1.5)
    assert summary["files_scanned"] == 1
    assert summary["files_moved"] == 1
    assert summary["errors"] == 0
    assert summary["time_taken"] == 1.5