from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from archivefile import ArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterator

NO_PY7ZR = find_spec("py7zr") is None
NO_RARFILE = find_spec("rarfile") is None


@pytest.fixture(
    params=[
        pytest.param(Path("tests/test_data/source_GNU.tar"), id="GNU.tar"),
        pytest.param(Path("tests/test_data/source_LZMA.zip"), id="LZMA.zip"),
        pytest.param(Path("tests/test_data/source_POSIX.tar.gz"), id="POSIX.tar.gz"),
        pytest.param(
            Path("tests/test_data/source_LZMA.7z"),
            marks=pytest.mark.skipif(NO_PY7ZR, reason="py7zr is not installed."),
            id="LZMA.7z",
        ),
        pytest.param(
            Path("tests/test_data/source_BEST.rar"),
            marks=pytest.mark.skipif(NO_RARFILE, reason="rarfile is not installed."),
            id="BEST.rar",
        ),
    ]
)
def archive_file(request: pytest.FixtureRequest) -> Iterator[ArchiveFile]:
    with ArchiveFile(request.param) as f:
        assert str(f) == repr(f) == f"ArchiveFile('{request.param.resolve().as_posix()}')"
        yield f
