import pytest


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "test_gui" in str(item.fspath):
            item.add_marker(pytest.mark.skip(reason="GUI tests require a display"))
