"""Unit tests for duplicate_detector.py"""

from datetime import datetime

from app.duplicate_detector import DuplicateDetector
from app.models import FileInfo


def make_file(tmp_path, filename, content):
    f = tmp_path / filename
    f.write_text(content)
    return FileInfo(
        name=f.name,
        extension=f.suffix.lower(),
        path=f,
        parent_directory=tmp_path,
        size=f.stat().st_size,
        created_time=datetime.now(),
        modified_time=datetime.now(),
        is_hidden=False,
    )


def test_identical_files_marked_as_duplicates(tmp_path):
    f1 = make_file(tmp_path, "a.txt", "same content")
    f2 = make_file(tmp_path, "b.txt", "same content")
    detector = DuplicateDetector([f1, f2])
    detector.find_duplicates()
    assert f1.is_duplicate is False
    assert f2.is_duplicate is True


def test_different_files_not_duplicates(tmp_path):
    f1 = make_file(tmp_path, "a.txt", "content one")
    f2 = make_file(tmp_path, "b.txt", "content two")
    detector = DuplicateDetector([f1, f2])
    detector.find_duplicates()
    assert f1.is_duplicate is False
    assert f2.is_duplicate is False


def test_duplicate_of_field_set_correctly(tmp_path):
    f1 = make_file(tmp_path, "original.txt", "hello")
    f2 = make_file(tmp_path, "copy.txt", "hello")
    detector = DuplicateDetector([f1, f2])
    detector.find_duplicates()
    assert f2.duplicate_of == "original.txt"


def test_empty_file_duplicates(tmp_path):
    f1 = make_file(tmp_path, "empty1.txt", "")
    f2 = make_file(tmp_path, "empty2.txt", "")
    detector = DuplicateDetector([f1, f2])
    detector.find_duplicates()
    assert f2.is_duplicate is True


def test_group_duplicates(tmp_path):
    f1 = make_file(tmp_path, "a.txt", "same")
    f2 = make_file(tmp_path, "b.txt", "same")
    detector = DuplicateDetector([f1, f2])
    detector.find_duplicates()
    groups = detector.group_duplicates()
    assert len(groups) == 1
    assert len(groups[0]) == 2


def test_generate_duplicate_report_no_duplicates(tmp_path):
    f1 = make_file(tmp_path, "a.txt", "unique")
    detector = DuplicateDetector([f1])
    detector.find_duplicates()
    report = detector.generate_duplicate_report()
    assert "No duplicates found" in report
