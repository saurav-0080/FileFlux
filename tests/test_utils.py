"""Unit tests for app.utils"""

from pathlib import Path

from app.utils import format_size, get_file_extension, create_directory, is_hidden


def test_format_size_bytes():
    """Small sizes should be formatted in bytes."""
    assert format_size(500) == "500.0 B"


def test_format_size_megabytes():
    """Sizes over 1MB should be formatted in MB."""
    result = format_size(2500000)
    assert "MB" in result


def test_get_file_extension_lowercases():
    """Extensions should be extracted and lowercased."""
    assert get_file_extension(Path("photo.JPG")) == ".jpg"


def test_get_file_extension_no_extension():
    """Files with no extension should return an empty string."""
    assert get_file_extension(Path("README")) == ""


def test_is_hidden_true_for_dotfile():
    """Files starting with a dot should be detected as hidden."""
    assert is_hidden(Path(".gitignore")) is True


def test_is_hidden_false_for_normal_file():
    """Normal files should not be detected as hidden."""
    assert is_hidden(Path("main.py")) is False


def test_create_directory(tmp_path):
    """create_directory() should create a new folder successfully."""
    new_dir = tmp_path / "test_folder"
    create_directory(new_dir)
    assert new_dir.exists()
    assert new_dir.is_dir()