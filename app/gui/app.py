"""
GUI entry point for FileFlux.

Initializes Tkinter and launches the main window.
"""

import tkinter as tk

from app.gui.main_window import MainWindow


def launch():
    """Launch the FileFlux desktop application."""
    root = tk.Tk()
    root.title("FileFlux")
    root.geometry("700x600")
    root.resizable(True, True)
    MainWindow(root)
    root.mainloop()
