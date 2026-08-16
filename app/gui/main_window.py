"""
Main window for FileFlux GUI — polished UI.
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

BG = "#1e1e2e"
SURFACE = "#2a2a3e"
ACCENT = "#7c6af7"
ACCENT2 = "#56cfb2"
TEXT = "#e0e0f0"
SUBTEXT = "#9090b0"
BTN_BG = "#3a3a5c"
BTN_HOV = "#5a5a8a"
FONT_HEAD = ("Helvetica", 20, "bold")
FONT_SUB = ("Helvetica", 11)
FONT_MONO = ("Courier", 10)


def _apply_ttk_styles():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Accent.TButton",
        background="#7c6af7",
        foreground="#ffffff",
        font=("Helvetica", 10),
        padding=6,
        relief="flat",
    )
    style.configure(
        "Green.TButton",
        background="#56cfb2",
        foreground="#ffffff",
        font=("Helvetica", 10),
        padding=6,
        relief="flat",
    )
    style.configure(
        "Dark.TButton",
        background="#3a3a5c",
        foreground="#ffffff",
        font=("Helvetica", 10),
        padding=6,
        relief="flat",
    )
    style.map("Accent.TButton", background=[("active", "#6a5ae0")])
    style.map("Green.TButton", background=[("active", "#45b89e")])
    style.map("Dark.TButton", background=[("active", "#4a4a7a")])


def _styled_btn(parent, text, command, color=None, width=12):
    if color == "#7c6af7":
        style = "Accent.TButton"
    elif color == "#56cfb2":
        style = "Green.TButton"
    else:
        style = "Dark.TButton"
    btn = ttk.Button(parent, text=text, command=command, style=style, width=width)
    return btn


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.configure(bg=BG)
        self.selected_path = tk.StringVar()
        self.dry_run = tk.BooleanVar()
        self.recursive = tk.BooleanVar()
        self.files = []
        self.stats = None
        self.last_report = None
        self._build_ui()

    def _build_ui(self):
        _apply_ttk_styles()
        self._build_header()
        self._build_path_bar()
        self._build_action_bar()
        self._build_stats_bar()
        self._build_file_table()
        self._build_log()
        self._build_bottom_bar()
        self._build_status_bar()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=SURFACE, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="FileFlux", font=FONT_HEAD, bg=SURFACE, fg=ACCENT).pack(
            side="left", padx=20
        )
        tk.Label(
            hdr, text="Smart File Organizer", font=FONT_SUB, bg=SURFACE, fg=SUBTEXT
        ).pack(side="left", padx=4)

    def _build_path_bar(self):
        bar = tk.Frame(self.root, bg=BG, pady=10)
        bar.pack(fill="x", padx=20)
        tk.Label(bar, text="Folder:", bg=BG, fg=SUBTEXT, font=FONT_SUB).pack(
            side="left", padx=(0, 6)
        )
        tk.Entry(
            bar,
            textvariable=self.selected_path,
            width=52,
            bg=SURFACE,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=FONT_SUB,
        ).pack(side="left", ipady=6)
        _styled_btn(bar, "Browse", self._browse, color=ACCENT, width=8).pack(
            side="left", padx=8
        )

    def _build_action_bar(self):
        bar = tk.Frame(self.root, bg=BG, pady=4)
        bar.pack(fill="x", padx=20)
        _styled_btn(bar, "Scan", self._scan, color=ACCENT2, width=10).pack(
            side="left", padx=(0, 6)
        )
        _styled_btn(bar, "Organize", self._organize, color=ACCENT, width=10).pack(
            side="left", padx=6
        )
        tk.Checkbutton(
            bar,
            text="Dry Run",
            variable=self.dry_run,
            bg=BG,
            fg=TEXT,
            selectcolor=SURFACE,
            activebackground=BG,
            activeforeground=TEXT,
            font=FONT_SUB,
        ).pack(side="left", padx=10)
        tk.Checkbutton(
            bar,
            text="Recursive",
            variable=self.recursive,
            bg=BG,
            fg=TEXT,
            selectcolor=SURFACE,
            activebackground=BG,
            activeforeground=TEXT,
            font=FONT_SUB,
        ).pack(side="left", padx=4)
        self.progress = ttk.Progressbar(bar, mode="indeterminate", length=140)
        self.progress.pack(side="right", padx=4)

    def _build_stats_bar(self):
        bar = tk.Frame(self.root, bg=SURFACE, pady=8)
        bar.pack(fill="x", padx=20, pady=(8, 0))
        self.stat_files = self._stat_card(bar, "Files", "—")
        self.stat_size = self._stat_card(bar, "Total Size", "—")
        self.stat_dups = self._stat_card(bar, "Duplicates", "—")
        self.stat_largest = self._stat_card(bar, "Largest File", "—")

    def _stat_card(self, parent, label, value):
        card = tk.Frame(parent, bg=BTN_BG, padx=16, pady=6)
        card.pack(side="left", padx=8)
        tk.Label(card, text=label, bg=BTN_BG, fg=SUBTEXT, font=("Helvetica", 9)).pack()
        val = tk.Label(
            card, text=value, bg=BTN_BG, fg=ACCENT2, font=("Helvetica", 13, "bold")
        )
        val.pack()
        return val

    def _build_file_table(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=8)
        tk.Label(
            frame, text="Scanned Files", bg=BG, fg=SUBTEXT, font=("Helvetica", 9)
        ).pack(anchor="w")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.Treeview",
            background=SURFACE,
            foreground=TEXT,
            fieldbackground=SURFACE,
            rowheight=24,
            font=("Helvetica", 10),
        )
        style.configure(
            "Dark.Treeview.Heading",
            background=BTN_BG,
            foreground=ACCENT,
            font=("Helvetica", 10, "bold"),
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", "#4a4a7a")],
            foreground=[("selected", "#ffffff")],
        )
        cols = ("Name", "Type", "Size", "Category")
        self.table = ttk.Treeview(
            frame, columns=cols, show="headings", style="Dark.Treeview", height=12
        )
        for col in cols:
            self.table.heading(col, text=col)
        self.table.column("Name", width=280)
        self.table.column("Type", width=70, anchor="center")
        self.table.column("Size", width=90, anchor="e")
        self.table.column("Category", width=120, anchor="center")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vsb.set)
        self.table.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def _build_log(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="x", padx=20, pady=(0, 4))
        tk.Label(
            frame, text="Activity Log", bg=BG, fg=SUBTEXT, font=("Helvetica", 9)
        ).pack(anchor="w")
        self.log_text = tk.Text(
            frame,
            height=5,
            state="disabled",
            wrap="word",
            bg=SURFACE,
            fg=TEXT,
            font=FONT_MONO,
            relief="flat",
            insertbackground=TEXT,
        )
        sb = tk.Scrollbar(frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        self.log_text.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")

    def _build_bottom_bar(self):
        bar = tk.Frame(self.root, bg=SURFACE, pady=8)
        bar.pack(fill="x", padx=0, pady=(4, 0))
        for label, cmd in [
            ("Duplicates", self._duplicates),
            ("History", self._history),
            ("Undo", self._undo),
            ("Report", self._view_report),
            ("About", self._about),
        ]:
            _styled_btn(bar, label, cmd, width=10).pack(side="left", padx=6, pady=2)

    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=BTN_BG, pady=3)
        bar.pack(fill="x")
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            bar,
            textvariable=self.status_var,
            bg=BTN_BG,
            fg=SUBTEXT,
            font=("Helvetica", 9),
            anchor="w",
        ).pack(side="left", padx=10)

    def _set_status(self, msg):
        self.status_var.set(msg)

    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_path.set(path)
            self._set_status("Selected: " + path)

    def _get_path(self):
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

    def _populate_table(self):
        self.table.delete(*self.table.get_children())
        try:
            rules = load_rules()
        except Exception:
            rules = {}
        from app.rule_engine import get_category

        for f in self.files:
            try:
                cat = get_category(f.extension, rules)
            except Exception:
                cat = "Other"
            self.table.insert(
                "",
                "end",
                values=(
                    f.name,
                    f.extension or "—",
                    format_size(f.size),
                    cat,
                ),
            )

    def _scan(self):
        path = self._get_path()
        if not path:
            return
        self.progress.start()
        self._set_status("Scanning...")
        self._log("Scanning: " + str(path))

        def run():
            try:
                files, stats = scan(path, recursive=self.recursive.get())
                self.files = files
                self.stats = stats
                self.root.after(0, lambda: self._on_scan_done(stats))
            except ScanError as e:
                self.root.after(0, lambda: messagebox.showerror("Scan Error", str(e)))
            finally:
                self.root.after(0, self.progress.stop)

        threading.Thread(target=run, daemon=True).start()

    def _on_scan_done(self, stats):
        self.stat_files.config(text=str(stats.total_files))
        self.stat_size.config(text=format_size(stats.total_size))
        largest = stats.largest_file
        if largest:
            name = (
                largest.name if len(largest.name) <= 18 else largest.name[:18] + "..."
            )
        else:
            name = "N/A"
        self.stat_largest.config(text=name)
        dups = sum(1 for f in self.files if f.is_duplicate)
        self.stat_dups.config(text=str(dups))
        self._populate_table()
        self._log(
            "Scan complete — "
            + str(stats.total_files)
            + " files, "
            + format_size(stats.total_size)
        )
        self._set_status("Scan complete — " + str(stats.total_files) + " files found")

    def _organize(self):
        path = self._get_path()
        if not path or not self.files:
            messagebox.showwarning("No Files", "Please scan a folder first.")
            return
        if self.dry_run.get():
            self._log("DRY RUN — No files will be moved.")
            try:
                rules = load_rules()
                from app.rule_engine import get_category

                for f in self.files:
                    cat = get_category(f.extension, rules)
                    self._log("  " + f.name + " -> " + cat + "/")
                self._log("Dry run complete.")
                self._set_status("Dry run complete")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            return
        if not messagebox.askyesno(
            "Confirm",
            "Organize " + str(len(self.files)) + " files in " + str(path) + "?",
        ):
            return
        self.progress.start()
        self._set_status("Organizing...")

        def run():
            try:
                rules = load_rules()
                org = Organizer(path, rules)
                org.organize(self.files)
                summary = org.create_summary(self.files, 0)
                self.root.after(0, lambda: self._on_organize_done(summary))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, self.progress.stop)

        threading.Thread(target=run, daemon=True).start()

    def _on_organize_done(self, summary):
        moved = summary["files_moved"]
        errors = summary["errors"]
        self._log("Organized — Moved: " + str(moved) + ", Errors: " + str(errors))
        self._set_status("Done — " + str(moved) + " files moved")
        messagebox.showinfo(
            "Done", "Files Moved: " + str(moved) + "\nErrors: " + str(errors)
        )

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
            "Total Moves   : "
            + str(stats["total_moves"])
            + "\n"
            + "Total Errors  : "
            + str(stats["total_errors"])
            + "\n"
            + "Total Sessions: "
            + str(stats["total_sessions"])
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
        if not messagebox.askyesno("Undo", "Undo session " + str(session_id) + "?"):
            database.close(conn)
            return
        manager = UndoManager(conn)
        result = manager.undo_last_session()
        database.close(conn)
        self._log("Undo complete — Restored: " + str(result["restored"]))
        self._set_status(
            "Undo complete — " + str(result["restored"]) + " files restored"
        )
        messagebox.showinfo(
            "Undo Complete",
            "Restored: "
            + str(result["restored"])
            + "\nSkipped: "
            + str(result["skipped"]),
        )

    def _about(self):
        messagebox.showinfo(
            "About FileFlux",
            "FileFlux v1.0.0\n\nA professional file organization tool.\n"
            "Built with Python + Tkinter + SQLite.\n\n"
            "github.com/saurav-0080/FileFlux",
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
            "Operation     : "
            + str(data.get("operation", "N/A")).title()
            + "\n"
            + "Files Scanned : "
            + str(data.get("files_scanned", 0))
            + "\n"
            + "Files Moved   : "
            + str(data.get("files_moved", 0))
            + "\n"
            + "Duplicates    : "
            + str(data.get("duplicates", 0))
            + "\n"
            + "Errors        : "
            + str(data.get("errors", 0))
            + "\n"
            + "Duration      : "
            + str(data.get("duration_seconds", 0))
            + "s\n"
            + "Status        : "
            + str(data.get("status", "N/A"))
        )
        messagebox.showinfo("Latest Report", msg)
