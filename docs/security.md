# Security & Safety Documentation

## Protected Directories

FileFlux refuses to organize the following:
- System root (/)
- System directories: /bin, /sbin, /usr, /etc, /System, /Library
- User Library directory
- The FileFlux project directory itself

## Path Validation

All source directories are validated before any operation:
- Must exist and be a real directory
- Must be readable
- Must not be a symlink
- Must not be a protected path

## Path Traversal Prevention

Destination paths are always resolved and verified to remain
within the selected root directory.

## Symlink Policy

Symbolic links are not followed as source directories.
FileFlux will reject symlinks to prevent unintended access.

## File Conflict Handling

If a destination file already exists, FileFlux renames the
incoming file: report.pdf -> report (1).pdf, report (2).pdf, etc.
Files are never silently overwritten.

## Configuration

Invalid settings fall back to safe defaults.
Corrupt settings.json is logged and ignored.

## Logging

Logs include timestamp, level, module, and message.
File paths are logged for operation tracking.
Passwords, tokens, and secrets are never logged.

## Environment Variables

Copy .env.example to .env for local configuration.
Never commit .env to version control.

## Database

SQLite database is auto-created on first run.
Database errors are caught and reported cleanly.
