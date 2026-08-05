# Organizer Module Documentation

## Workflow

The following steps happen in order when the user runs the app:

1. User provides a folder path
2. Config and rules are loaded from `settings.json` and `rules.json`
3. Scanner scans the folder and returns a list of `FileInfo` objects
4. Rule engine assigns a category to each file based on its extension
5. Organizer creates category subfolders inside the target folder
6. Each file is moved to its category subfolder safely
7. A summary report is printed showing counts and time taken

---

## Rule Engine

**File:** `app/rule_engine.py`

The rule engine answers one question: given a file extension, which category does it belong to?

- Categories and extensions are defined in `config/rules.json`
- Nothing is hardcoded — adding a new file type only requires editing `rules.json`

### Functions

| Function | Description |
|---|---|
| `get_category(extension, rules)` | Returns the category for a given extension, or "Others" if not found |
| `is_supported(extension, rules)` | Returns True if the extension is explicitly covered by rules |
| `get_all_categories(rules)` | Returns a list of all category names defined in rules |

### Example

```
.pdf  →  Documents
.jpg  →  Images
.mp4  →  Videos
.xyz  →  Others
```

---

## Organizer

**File:** `app/organizer.py`

The `Organizer` class handles all filesystem changes. The scanner only reads — the organizer is the only module that moves files.

### Class: `Organizer`

**Constructor arguments:**
- `base_directory` — the folder being organized
- `rules` — the rules dictionary from `load_rules()`

### Methods

| Method | Description |
|---|---|
| `organize(files)` | Main entry point — categorizes and moves all files |
| `move_file(file_info)` | Moves a single file safely, handles errors |
| `create_category_folder(category)` | Creates a subfolder if it doesn't exist |
| `generate_destination(file_info)` | Returns the planned destination path for a file |
| `handle_duplicate_name(destination)` | Resolves filename conflicts without overwriting |
| `create_summary(files, elapsed)` | Returns a summary dict after organizing is complete |

---

## Folder Creation

- Category subfolders are created automatically inside the target folder
- Example: if an image is found, `Images/` is created automatically
- Folders are never assumed to exist — `mkdir(parents=True, exist_ok=True)` is used
- The organizer tracks which folders were created during the session

### Example

```
Downloads/
    Images/
    Videos/
    Documents/
    Others/
```

---

## Duplicate Naming Strategy

The organizer never overwrites an existing file.

If a file with the same name already exists at the destination, a counter is appended to the filename stem:

```
resume.pdf      (original, already exists)
resume(1).pdf   (first duplicate)
resume(2).pdf   (second duplicate)
resume(3).pdf   (third duplicate)
```

### How it works

1. Check if the destination path already exists
2. If not, proceed with the original filename
3. If yes, try `stem(1).suffix`, then `stem(2).suffix`, and so on
4. Continue until a non-existing filename is found
5. Log the resolution

---

## Error Handling

The organizer handles the following errors gracefully:

| Error | Handling |
|---|---|
| `PermissionError` | Caught, logged as warning, file marked as not moved |
| `OSError` | Caught, logged as warning, file marked as not moved |
| Missing rules file | Raises `ConfigurationError` at startup |
| Invalid extension | Falls back to "Others" category |
| Missing target folder | Raises `ScanError` via scanner |

Failed files are recorded in `FileInfo.error_message` and counted in the summary report under `errors`.

---

## Future Improvements

- **Dry Run Mode** — preview planned moves without touching the filesystem (`--dry-run` flag)
- **Undo functionality** — reverse a previous organize operation using a move log
- **Recursive organization** — organize files inside subfolders as well
- **Custom rules via CLI** — allow users to pass a custom rules file at runtime
- **Progress bar** — show real-time progress for large folders
- **Duplicate detection** — identify files with identical content (not just name) using hash comparison