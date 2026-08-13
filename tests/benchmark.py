"""
Performance benchmark for FileFlux.

Generates test directories with different file counts,
then measures scan time, hash time, and organization time.
Run directly: python3 tests/benchmark.py
"""

import os
import random
import shutil
import time
from pathlib import Path

from app.duplicate_detector import DuplicateDetector
from app.scanner import scan

BENCHMARK_DIR = Path("benchmark_data")
SIZES = {
    "small": 100,
    "medium": 1_000,
    "large": 5_000,
}

EXTENSIONS = [".jpg", ".png", ".pdf", ".txt", ".mp4", ".docx", ".zip", ".csv"]


def generate_files(directory: Path, count: int) -> None:
    """Generate dummy files with random content in a directory."""
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        ext = random.choice(EXTENSIONS)
        filename = f"file_{i:05d}{ext}"
        file_path = directory / filename
        # Random size between 1 KB and 50 KB
        size = random.randint(1024, 51200)
        file_path.write_bytes(os.urandom(size))


def setup_benchmark_data() -> None:
    """Create benchmark directories and populate with dummy files."""
    print("Setting up benchmark data...")
    for name, count in SIZES.items():
        target = BENCHMARK_DIR / name
        if target.exists():
            shutil.rmtree(target)
        print(f"  Generating {count} files in benchmark_data/{name}/")
        generate_files(target, count)
    print("Done.\n")


def run_benchmark(label: str, directory: Path) -> None:
    """Run and print benchmark results for a single directory."""
    print(f"Benchmark: {label} ({SIZES[label]} files)")
    print("─" * 40)

    # Scan time
    t0 = time.perf_counter()
    files, stats = scan(directory, recursive=False)
    scan_time = time.perf_counter() - t0

    # Hash time (duplicate detection)
    t1 = time.perf_counter()
    detector = DuplicateDetector(files)
    detector.find_duplicates()
    hash_time = time.perf_counter() - t1

    total_time = scan_time + hash_time

    print(f"Files          : {stats.total_files}")
    print(f"Scan Time      : {scan_time:.3f} sec")
    print(f"Hash Time      : {hash_time:.3f} sec")
    print(f"Total          : {total_time:.3f} sec")
    print()


def cleanup() -> None:
    """Remove benchmark data directory."""
    if BENCHMARK_DIR.exists():
        shutil.rmtree(BENCHMARK_DIR)
    print("Benchmark data cleaned up.")


if __name__ == "__main__":
    setup_benchmark_data()
    for size_label in SIZES:
        run_benchmark(size_label, BENCHMARK_DIR / size_label)
