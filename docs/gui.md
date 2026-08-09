# GUI Documentation

## Architecture

The GUI is built with Tkinter and sits on top of the same core services
used by the CLI. No business logic lives in the GUI layer.

User
│
├── CLI
│
└── GUI
│
└── Core Services (Scanner, Organizer, DuplicateDetector, UndoManager)


## Screens

### Main Window
- Folder selector with Browse button
- Scan, Organize, and Dry Run controls
- Statistics panel
- Activity log
- Duplicates, History, Undo, and About buttons

## User Workflow

1. Click Browse to select a folder
2. Click Scan to discover files
3. Check Dry Run to preview without moving
4. Click Organize to move files
5. Click Undo to restore the last session
6. Click History to view statistics

## Threading

Long operations (scan, organize) run in a background thread to prevent
the GUI from freezing. Results are passed back to the main thread using
`root.after()` which is Tkinter's thread-safe callback mechanism.

## Error Handling

All exceptions are caught and displayed as friendly dialog boxes.
Detailed errors are written to the log file in logs/organizer.log.

## Future Improvements

- Progress bar with file count
- Duplicate file browser
- Settings dialog
- Dark/light theme toggle
- Drag and drop folder selection