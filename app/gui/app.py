"""
GUI entry point for FileFlux.
"""

import tkinter as tk

from app.gui.main_window import MainWindow


def launch():
    root = tk.Tk()
    root.title("FileFlux")
    root.geometry("900x700")
    root.minsize(800, 600)
    root.resizable(True, True)
    root.configure(bg="#1e1e2e")
    MainWindow(root)
    root.mainloop()
