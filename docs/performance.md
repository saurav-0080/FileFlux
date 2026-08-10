# Performance

## Duplicate Detection Optimization

### Original Approach
Hash every file with SHA-256 regardless of size.

### Problem
SHA-256 is expensive on large files. Hashing 5,000 files unconditionally
wastes significant time — two files with different sizes can never be
identical, so hashing them for duplicate detection is pointless.

### Optimization
Files are grouped by size first. Only files that share the same size
are hashed. Files with unique sizes are skipped entirely.