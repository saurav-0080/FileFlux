"""
Main window for FileFlux GUI.
"""

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app import database, history
from app.config import load_rules
from app.duplicate_detector import DuplicateDetector
from app.exceptions import ScanError
from app.organizer import Organizer
from app.scanner import scan
from app.undo import UndoManager
from app.utils import format_size


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.selected_path = tk.StringVar()
        self.dry_run = tk.BooleanVar()
        self.files = []
        self.stats = None
        self.last_report = None
        self._build_ui()

    def _build_ui(self):
        tk.Label(self.root, text="FileFlux", font=("Helvetica", 18, "bold")).pack(
            pady=10
        )

        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=20, pady=5)
        tk.Entry(frame, textvariable=self.selected_path, width=55).pack(
            side="left", padx=5
        )
        tk.Button(frame, text="Browse", command=self._browse).pack(side="left")

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Scan", width=12, command=self._scan).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="Organize", width=12, command=self._organize).pack(
            side="left", padx=5
        )
        tk.Checkbutton(btn_frame, text="Dry Run", variable=self.dry_run).pack(
            side="left", padx=5
        )

        stats_frame = tk.LabelFrame(self.root, text="Statistics", padx=10, pady=10)
        stats_frame.pack(fill="x", padx=20, pady=5)
        self.stats_label = tk.Label(stats_frame, text="No scan yet.", justify="left")
        self.stats_label.pack(anchor="w")

        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=20, pady=5)

        log_frame = tk.LabelFrame(self.root, text="Activity", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.log_text = tk.Text(log_frame, height=10, state="disabled", wrap="word")
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10)
        tk.Button(
            bottom_frame, text="Duplicates", width=12, command=self._duplicates
        ).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="History", width=12, command=self._history).pack(
            side="left", padx=5
        )
        tk.Button(bottom_frame, text="Undo", width=12, command=self._undo).pack(
            side="left", padx=5
        )
        tk.Button(bottom_frame, text="About", width=12, command=self._about).pack(
            side="left", padx=5
        )
        tk.Button(
            bottom_frame, text="View Report", width=12, command=self._view_report
        ).pack(side="left", padx=5)

    def _log(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_path.set(path)

    def _get_path(self) -> Path:
        p = self.selected_path.get().strip()
        if not p:
            messagebox.showwarning("No Folder", "Please select a folder first.")
            return None
        path = Path(p)
        if not path.exists() or not path.is_dir():
            messagebox.showerror(
                "Invalid Path", "The selected path is not a valid directory."
            )
            return None
        return path

    def _scan(self):
        path = self._get_path()
        if not path:
            return
        self.progress.start()
        self._log(f"Scanning: {path}")

        def run():
            try:
                files, stats = scan(path, recursive=False)
                self.files = files
                self.stats = stats
                self.root.after(0, lambda: self._on_scan_done(stats))
            except ScanError:
                self.root.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
            finally:
                self.root.after(0, self.progress.stop)

        threading.Thread(target=run, daemon=True).start()

    def _on_scan_done(self, stats):
        self.stats_label.config(
            text=(
                f"Files Found : {stats.total_files}\n"
                f"Total Size  : {format_size(stats.total_size)}\n"
                f"Largest     : {stats.largest_file.name if stats.largest_file else 'N/A'}"
            )
        )
        self._log(f"Scan complete. {stats.total_files} files found.")

    def _organize(self):
        path = self._get_path()
        if not path or not self.files:
            messagebox.showwarning("No Files", "Please scan a folder first.")
            return

        if self.dry_run.get():
            self._log("DRY RUN — No files will be moved.")
            try:
                rules = load_rules()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
            from app.rule_engine import get_category

            for f in self.files:
                cat = get_category(f.extension, rules)
                self._log(f"  {f.name} → {cat}/")
            self._log("Dry run complete. 0 files moved.")
            return

        if not messagebox.askyesno(
            "Confirm", f"Organize {len(self.files)} files in {path}?"
        ):
            return

        self.progress.start()

        def run():
            try:
                rules = load_rules()
                org = Organizer(path, rules)
                org.organize(self.files)
                summary = org.create_summary(self.files, 0)
                self.root.after(0, lambda: self._on_organize_done(summary))
            except Exception:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, self.progress.stop)

        threading.Thread(target=run, daemon=True).start()

    def _on_organize_done(self, summary):
        self._log(
            f"Organized. Moved: {summary['files_moved']}, Errors: {summary['errors']}"
        )
        messagebox.showinfo(
            "Done",
            f"Files Moved: {summary['files_moved']}\nErrors: {summary['errors']}",
        )
        self._log("Tip: Click 'View Report' to see the full operation report.")

    def _duplicates(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please scan a folder first.")
            return
        detector = DuplicateDetector(self.files)
        detector.find_duplicates()
        report = detector.generate_duplicate_report()
        self._log(report)
        messagebox.showinfo("Duplicates", report)

    def _history(self):
        conn = database.connect()
        database.create_tables(conn)
        stats = history.get_statistics(conn)
        database.close(conn)
        msg = (
            f"Total Moves   : {stats['total_moves']}\n"
            f"Total Errors  : {stats['total_errors']}\n"
            f"Total Sessions: {stats['total_sessions']}"
        )
        messagebox.showinfo("History", msg)

    def _undo(self):
        conn = database.connect()
        database.create_tables(conn)
        session_id = history.get_last_session(conn)
        if not session_id:
            messagebox.showinfo("Undo", "No session found to undo.")
            database.close(conn)
            return
        if not messagebox.askyesno("Undo", f"Undo session {session_id}?"):
            database.close(conn)
            return
        manager = UndoManager(conn)
        result = manager.undo_last_session()
        database.close(conn)
        self._log(f"Undo complete. Restored: {result['restored']}")
        messagebox.showinfo(
            "Undo Complete",
            f"Restored: {result['restored']}\nSkipped: {result['skipped']}",
        )

    def _about(self):
        messagebox.showinfo(
            "About FileFlux",
            "FileFlux v0.1.0\n\nA professional file organization tool.\n\nBuilt with Python + Tkinter + SQLite.",
        )

    def _view_report(self):
        from app.reports import load_latest_report

        data = load_latest_report()
        if not data:
            messagebox.showinfo(
                "No Report", "No report found. Run an organize operation first."
            )
            return
        msg = (
            f"Operation       : {data.get('operation', 'N/A').title()}\n"
            f"Files Scanned   : {data.get('files_scanned', 0)}\n"
            f"Files Moved     : {data.get('files_moved', 0)}\n"
            f"Duplicates      : {data.get('duplicates', 0)}\n"
            f"Errors          : {data.get('errors', 0)}\n"
            f"Duration        : {data.get('duration_seconds', 0)}s\n"
            f"Status          : {data.get('status', 'N/A')}"
        )
        messagebox.showinfo("Latest Report", msg)
