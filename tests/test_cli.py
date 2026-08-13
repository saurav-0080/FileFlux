"""Unit tests for cli.py"""

from unittest.mock import patch

import pytest

from app.cli import build_parser, run_cli


def test_help_does_not_crash():
    parser = build_parser()
    assert parser is not None


def test_version_command(capsys):
    with patch("sys.argv", ["fileflux", "version"]):
        run_cli()
    captured = capsys.readouterr()
    assert "FileFlux" in captured.out
    assert "v" in captured.out


def test_scan_invalid_path(capsys):
    with patch("sys.argv", ["fileflux", "scan", "nonexistent_path_xyz"]):
        with pytest.raises(SystemExit) as exc:
            run_cli()
    assert exc.value.code == 3


def test_scan_valid_path(tmp_path, capsys):
    f = tmp_path / "test.pdf"
    f.write_text("content")
    with patch("sys.argv", ["fileflux", "scan", str(tmp_path)]):
        run_cli()
    captured = capsys.readouterr()
    assert "Files Found" in captured.out


def test_dry_run_does_not_move_files(tmp_path, capsys):
    f = tmp_path / "test.pdf"
    f.write_text("content")
    with patch("sys.argv", ["fileflux", "organize", str(tmp_path), "--dry-run"]):
        run_cli()
    assert f.exists()
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out


def test_organize_file_path_rejected(tmp_path, capsys):
    f = tmp_path / "file.txt"
    f.write_text("x")
    with patch("sys.argv", ["fileflux", "scan", str(f)]):
        with pytest.raises(SystemExit) as exc:
            run_cli()
    assert exc.value.code == 3
