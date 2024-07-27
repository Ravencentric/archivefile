from __future__ import annotations

from archivefile._utils import is_archive


def test_is_archive() -> None:
    assert is_archive("tests/test_data/source_BEST.rar") is True
    assert is_archive("tests/test_data/source_PPMD.zip") is True
    assert is_archive("src/archivefile/__init__.py") is False
    assert is_archive("non-existent-file.py") is False
