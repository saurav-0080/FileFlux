"""Unit tests for hash_utils.py"""

from app.hash_utils import calculate_md5, calculate_sha256, verify_hash


def test_same_content_same_hash(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("hello world")
    f2.write_text("hello world")
    assert calculate_sha256(f1) == calculate_sha256(f2)


def test_different_content_different_hash(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("hello")
    f2.write_text("world")
    assert calculate_sha256(f1) != calculate_sha256(f2)


def test_empty_file_hash(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_bytes(b"")
    result = calculate_sha256(f)
    assert isinstance(result, str)
    assert len(result) == 64


def test_md5_same_content(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("test")
    f2.write_text("test")
    assert calculate_md5(f1) == calculate_md5(f2)


def test_verify_hash_correct(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("verify me")
    h = calculate_sha256(f)
    assert verify_hash(f, h) is True


def test_verify_hash_incorrect(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("verify me")
    assert verify_hash(f, "wronghash") is False
