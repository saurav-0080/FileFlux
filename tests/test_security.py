"""
Security tests for FileFlux.
"""

from pathlib import Path

import pytest

from app.safety import (
    resolve_conflict,
    safe_destination,
    validate_source_directory,
)


def test_protected_root():
    with pytest.raises(ValueError):
        validate_source_directory(Path("/"))


def test_protected_project_dir():
    project = Path(__file__).resolve().parent.parent
    with pytest.raises(ValueError):
        validate_source_directory(project)


def test_nonexistent_directory():
    with pytest.raises(ValueError):
        validate_source_directory(Path("/nonexistent_xyz_abc"))


def test_file_not_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("x")
    with pytest.raises(ValueError):
        validate_source_directory(f)


def test_valid_directory(tmp_path):
    result = validate_source_directory(tmp_path)
    assert result == tmp_path.resolve()


def test_path_traversal_blocked(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside" / "file.txt"
    with pytest.raises(ValueError):
        safe_destination(root, outside)


def test_path_within_root(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    dest = root / "subdir" / "file.txt"
    result = safe_destination(root, dest)
    assert str(result).startswith(str(root.resolve()))


def test_resolve_conflict_no_conflict(tmp_path):
    dest = tmp_path / "file.txt"
    assert resolve_conflict(dest) == dest


def test_resolve_conflict_with_conflict(tmp_path):
    dest = tmp_path / "file.txt"
    dest.write_text("x")
    result = resolve_conflict(dest)
    assert result == tmp_path / "file (1).txt"


def test_resolve_conflict_multiple(tmp_path):
    dest = tmp_path / "file.txt"
    dest.write_text("x")
    (tmp_path / "file (1).txt").write_text("x")
    result = resolve_conflict(dest)
    assert result == tmp_path / "file (2).txt"


def test_symlink_rejected(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    with pytest.raises(ValueError):
        validate_source_directory(link)
