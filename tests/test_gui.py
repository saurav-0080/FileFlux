"""Unit tests for GUI components."""

import tkinter as tk
from unittest.mock import patch

import pytest

from app.gui.main_window import MainWindow


@pytest.fixture
def window():
    root = tk.Tk()
    root.withdraw()  # hide window during tests
    app = MainWindow(root)
    yield app
    root.destroy()


def test_gui_launches(window):
    assert window is not None


def test_initial_stats_label(window):
    assert "No scan yet" in window.stats_label.cget("text")


def test_browse_sets_path(window):
    with patch("tkinter.filedialog.askdirectory", return_value="/tmp"):
        window._browse()
    assert window.selected_path.get() == "/tmp"


def test_scan_without_path_shows_warning(window):
    window.selected_path.set("")
    with patch("tkinter.messagebox.showwarning") as mock_warn:
        window._scan()
        mock_warn.assert_called_once()


def test_organize_without_scan_shows_warning(window):
    window.selected_path.set("/tmp")
    window.files = []
    with patch("tkinter.messagebox.showwarning") as mock_warn:
        window._organize()
        mock_warn.assert_called_once()


def test_duplicates_without_scan_shows_warning(window):
    window.files = []
    with patch("tkinter.messagebox.showwarning") as mock_warn:
        window._duplicates()
        mock_warn.assert_called_once()


def test_about_dialog(window):
    with patch("tkinter.messagebox.showinfo") as mock_info:
        window._about()
        mock_info.assert_called_once()
        assert "FileFlux" in mock_info.call_args[0][1]
