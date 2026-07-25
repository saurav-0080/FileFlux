# Smart File Organizer

A Python automation tool that scans a directory, organizes files into 
folders by type, detects and flags duplicates, and keeps a full log of 
every action so changes can be reviewed or undone.

## Problem It Solves

Downloads folders, desktops, and project directories accumulate 
hundreds of unsorted files over time. This tool automates the cleanup: 
sort by file type, catch duplicate copies wasting disk space, and keep 
a record of what moved where — without deleting anything blindly.

## Features

- **Organize by extension** — sorts files into folders (Images, Documents, 
  Videos, etc.) based on file type
- **Duplicate detection** — identifies duplicate files by content hash, 
  not just filename
- **Logging** — every file move is recorded in `logs/organizer.log` for 
  full traceability
- **Statistics** — summary report after each run (files moved, duplicates 
  found, space reclaimed)
- **Undo** — reverses the last organization run using the log, in case 
  something gets sorted wrong
- **SQLite persistence** — tracks file history in a local database instead 
  of relying only on log files

## Tech Stack

- Python 3
- SQLite (via `sqlite3`)
- pytest (testing)

## Project Status

🚧 In active development. Currently at project setup / foundation stage — 
core organizing logic not yet implemented.

## Installation

```bash
git clone <your-repo-url>
cd Smart-File-Organizer
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

*(Usage instructions will be expanded as core features are built.)*

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) 
for details.