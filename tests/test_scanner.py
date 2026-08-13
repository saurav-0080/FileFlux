"""Unit tests for app.scanner"""

from pathlib import Path

import pytest

from app.exceptions import ScanError
from app.scanner import collect_statistics, scan, scan_directory


def test_scan_empty_directory(tmp_path):
    """Scanning an empty directory should return an empty list."""
    results = scan_directory(tmp_path, recursive=False)
    assert results == []


def test_scan_single_file(tmp_path):
    """A directory with one file should return one FileInfo."""
    (tmp_path / "test.txt").write_text("hello")
    results = scan_directory(tmp_path, recursive=False)
    assert len(results) == 1
    assert results[0].name == "test.txt"


def test_scan_multiple_files(tmp_path):
    """A directory with several files should return all of them."""
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("bb")
    (tmp_path / "c.txt").write_text("ccc")
    results = scan_directory(tmp_path, recursive=False)
    assert len(results) == 3


def test_scan_nested_folders_recursive(tmp_path):
    """Recursive scan should find files inside subdirectories."""
    subfolder = tmp_path / "sub"
    subfolder.mkdir()
    (tmp_path / "top.txt").write_text("top")
    (subfolder / "nested.txt").write_text("nested")

    results = scan_directory(tmp_path, recursive=True)
    names = {f.name for f in results}
    assert names == {"top.txt", "nested.txt"}


def test_scan_nested_folders_non_recursive(tmp_path):
    """Non-recursive scan should NOT find files inside subdirectories."""
    subfolder = tmp_path / "sub"
    subfolder.mkdir()
    (tmp_path / "top.txt").write_text("top")
    (subfolder / "nested.txt").write_text("nested")

    results = scan_directory(tmp_path, recursive=False)
    names = {f.name for f in results}
    assert names == {"top.txt"}


def test_scan_skips_hidden_files(tmp_path):
    """Hidden files (starting with a dot) should be excluded."""
    (tmp_path / "visible.txt").write_text("visible")
    (tmp_path / ".hidden.txt").write_text("hidden")

    results = scan_directory(tmp_path, recursive=False)
    names = {f.name for f in results}
    assert names == {"visible.txt"}


def test_scan_skips_hidden_directory_contents(tmp_path):
    """Files inside a hidden directory should be excluded on recursive scan."""
    hidden_folder = tmp_path / ".hidden_dir"
    hidden_folder.mkdir()
    (hidden_folder / "inside.txt").write_text("inside")
    (tmp_path / "visible.txt").write_text("visible")

    results = scan_directory(tmp_path, recursive=True)
    names = {f.name for f in results}
    assert names == {"visible.txt"}


def test_scan_invalid_path_raises_error():
    """Scanning a path that doesn't exist should raise ScanError."""
    with pytest.raises(ScanError):
        scan_directory(Path("/this/path/does/not/exist/at/all"), recursive=False)


def test_scan_file_instead_of_directory_raises_error(tmp_path):
    """Scanning a file path (not a directory) should raise ScanError."""
    file_path = tmp_path / "notadirectory.txt"
    file_path.write_text("content")
    with pytest.raises(ScanError):
        scan_directory(file_path, recursive=False)


def test_collect_statistics_empty_list():
    """Statistics on an empty file list should not crash."""
    stats = collect_statistics([])
    assert stats.total_files == 0
    assert stats.total_size == 0
    assert stats.largest_file is None
    assert stats.smallest_file is None
    assert stats.average_size == 0.0


def test_collect_statistics_correct_totals(tmp_path):
    """Statistics should correctly compute totals, largest, and smallest."""
    (tmp_path / "small.txt").write_text("a")
    (tmp_path / "big.txt").write_text("a" * 100)

    files = scan_directory(tmp_path, recursive=False)
    stats = collect_statistics(files)

    assert stats.total_files == 2
    assert stats.largest_file.name == "big.txt"
    assert stats.smallest_file.name == "small.txt"


def test_scan_wrapper_returns_files_and_stats(tmp_path):
    """The scan() wrapper should return both a file list and statistics."""
    (tmp_path / "file.txt").write_text("content")
    files, stats = scan(tmp_path, recursive=False)
    assert len(files) == 1
    assert stats.total_files == 1
