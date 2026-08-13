"""
Unit tests for rule_engine.py
"""

from app.rule_engine import get_all_categories, get_category, is_supported

# A minimal fake rules dict — no need to load rules.json
FAKE_RULES = {
    "Images": [".jpg", ".png"],
    "Videos": [".mp4", ".mov"],
    "Documents": [".pdf", ".docx"],
}


def test_known_extension_returns_correct_category():
    assert get_category(".pdf", FAKE_RULES) == "Documents"


def test_known_extension_case_insensitive():
    assert get_category(".PDF", FAKE_RULES) == "Documents"


def test_unknown_extension_returns_others():
    assert get_category(".xyz", FAKE_RULES) == "Others"


def test_is_supported_known_extension():
    assert is_supported(".jpg", FAKE_RULES) is True


def test_is_supported_unknown_extension():
    assert is_supported(".abc", FAKE_RULES) is False


def test_get_all_categories_returns_all_keys():
    categories = get_all_categories(FAKE_RULES)
    assert set(categories) == {"Images", "Videos", "Documents"}
