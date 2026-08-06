# Duplicate Detection Module

## SHA-256 Explanation

SHA-256 is a cryptographic hash function that produces a unique 64-character
hex string for any given input. Two files with identical content will always
produce the same hash. This makes it reliable for duplicate detection — unlike
filenames, which can be the same while content differs, or different while
content is identical.

MD5 is faster but has known collision vulnerabilities. SHA-256 is preferred
for integrity checks.

## Algorithm

1. Scan files and group them by file size
2. Skip any size group with only one file — it cannot have a duplicate
3. For each remaining group, calculate SHA-256 hash per file
4. Store hashes in a dictionary — key: hash, value: first FileInfo seen
5. If a hash already exists in the dictionary, mark the file as a duplicate
6. Record which original file it duplicates in `duplicate_of`

## Time Complexity

- Grouping by size: O(n)
- Hashing: O(k) per file where k is file size
- Dictionary lookup: O(1)
- Overall: O(n + total bytes hashed)

The size-grouping optimization means most files are never hashed at all,
dramatically reducing runtime on large directories.

## Memory Usage

Files are read in 8192-byte chunks. At no point is an entire file loaded
into memory. This makes the engine safe to run on multi-GB files.

## Future Improvements

- Allow user to delete or move duplicates after detection
- Export duplicate report to a file
- Add MD5 fallback option via config
- Track duplicates in SQLite for history across runs
- Add a threshold — ignore duplicates below a minimum file size