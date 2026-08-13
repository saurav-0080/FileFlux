# FileFlux

A Python automation tool that scans a directory, organizes files into
folders by type, detects duplicates, and keeps a full log of every
action so changes can be reviewed or undone.

## Problem It Solves

Downloads folders, desktops, and project directories accumulate
hundreds of unsorted files over time. This tool automates the cleanup:
sort by file type, handle duplicate filenames safely, and keep a record
of what moved where — without deleting anything blindly.

## Features

- ✔ Organize files by extension — sorts into Images, Documents, Videos, etc.
- ✔ Recursive scanning — optionally scan subfolders
- ✔ Automatic folder creation — category folders created on the fly
- ✔ Duplicate filename handling — never overwrites existing files
- ✔ Logging — every move recorded in `logs/organizer.log`
- ✔ Statistics — summary report after each run (files moved, errors, time taken)
- ✔ Duplicate detection — identifies duplicate files by content hash
- ✔ Undo — reverses the last organize run using the move log
- ✔ SQLite persistence — tracks file history in a local database

## Tech Stack

- Python 3
- SQLite (via `sqlite3`)
- pytest (testing)

## Project Status

🚧 In active development. Core organizing engine complete — duplicate
detection and undo functionality in progress.

## Installation

```bash
git clone <your-repo-url>
cd Smart-File-Organizer
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py
```

Enter the folder path when prompted, then confirm to organize.

## CLI Usage

```bash
python main.py scan ~/Downloads
python main.py organize ~/Downloads --dry-run
python main.py organize ~/Downloads
python main.py duplicates ~/Downloads
python main.py undo
python main.py history
python main.py version
python main.py --help
```

## Desktop GUI

FileFlux includes a desktop interface built with Tkinter.

```bash
python main.py gui
```

Features: folder selection, scanning, dry-run preview, organizing,
duplicate detection, undo, history, and activity logging.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE)
for details.
## CI Status
![CI](https://github.com/saurav-0080/FileFlux/actions/workflows/ci.yml/badge.svg)
