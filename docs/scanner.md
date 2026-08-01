# Scanner Module

## Purpose

The scanner module (`app/scanner.py`) discovers files in a directory,
extracts metadata for each one, and computes summary statistics. It does
not move, rename, or modify any files — it only reads and reports.

## Workflow

1. `scan()` is called with a target directory and a recursive flag.
2. `scan_directory()` validates the path exists and is a directory.
3. It iterates over entries (`Path.iterdir()` for non-recursive,
   `Path.rglob("*")` for recursive), skipping subdirectories, hidden
   files, and files inside hidden directories (e.g. `.venv`, `.git`).
4. For each remaining file, `get_file_info()` extracts metadata into a
   `FileInfo` object.
5. `collect_statistics()` computes totals, largest/smallest files, and
   average size across all `FileInfo` objects.
6. `scan()` returns both the file list and the statistics together.

## Functions

### `get_file_info(file_path: Path) -> FileInfo`
Extracts metadata (name, extension, size, timestamps, hidden status) for
a single file. Raises `ScanError` if metadata can't be read.

### `scan_directory(directory: Path, recursive: bool = False) -> List[FileInfo]`
Scans a directory and returns a `FileInfo` for every visible file found.
Raises `ScanError` if the directory doesn't exist or isn't a directory.
Permission errors on individual files are logged and skipped rather than
stopping the whole scan.

### `_has_hidden_parent(entry: Path, root: Path) -> bool`
Internal helper. Checks whether any folder between `entry` and `root` is
hidden, so recursive scans correctly skip everything inside folders like
`.venv` or `.git`, not just top-level dotfiles.

### `collect_statistics(files: List[FileInfo]) -> ScanStatistics`
Computes total file count, total size, largest file, smallest file, and
average size. Returns zeroed/`None` values safely if the list is empty.

### `scan(directory: Path, recursive: bool = False) -> tuple[List[FileInfo], ScanStatistics]`
Main entry point. Combines `scan_directory()` and `collect_statistics()`
into a single call.

## Inputs

- A `Path` to the directory to scan.
- A `recursive` boolean, typically read from `settings.json`'s
  `recursive_scan` key.

## Outputs

- A list of `FileInfo` objects (one per file found).
- A `ScanStatistics` object summarizing the scan.

## Known Limitations

- Permission-denied files are logged and skipped, but this behavior is
  not currently covered by an automated test (would require mocking
  filesystem permissions).
- No duplicate detection yet — planned for a later stage, once
  `FileInfo` gains a `sha256_hash` field.
- No file categorization by extension yet — `rules.json` is loaded by
  `main.py` but not yet applied to scan results.

## Future Improvements

- Add duplicate detection via file content hashing.
- Apply `rules.json` categories to scanned files.
- Add permission-error test coverage using `unittest.mock`.
- Consider a progress indicator for very large recursive scans.