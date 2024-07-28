from __future__ import annotations

import pytest
from archivefile._utils import clamp_compression_level, is_archive


def test_is_archive() -> None:
    assert is_archive("tests/test_data/source_BEST.rar") is True
    assert is_archive("tests/test_data/source_PPMD.zip") is True
    assert is_archive("src/archivefile/__init__.py") is False
    assert is_archive("non-existent-file.py") is False


@pytest.mark.parametrize(
    "level,expected",
    [
        (-1212, 0),
        (-5, 0),
        (-1, 0),
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 9),
        (11, 9),
        (1123, 9),
    ],
)
def test_clamp_compression_level(level: int, expected: int) -> None:
    assert clamp_compression_level(level) == expected
