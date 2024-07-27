from __future__ import annotations

from pathlib import Path

import pytest
from archivefile import ArchiveFile
from archivefile._adapters._rar import RarFileAdapter
from archivefile._adapters._sevenzip import SevenZipFileAdapter
from archivefile._adapters._tar import TarFileAdapter
from archivefile._adapters._zip import ZipFileAdapter

files = (
    Path("tests/test_data/source_GNU.tar"),
    Path("tests/test_data/source_STORE.7z"),
    Path("tests/test_data/source_STORE.rar"),
    Path("tests/test_data/source_STORE.zip"),
)


@pytest.mark.parametrize("file", files)
def test_core_properties(file: Path) -> None:
    with ArchiveFile(file) as archive:
        assert archive.file == file.resolve()
        assert archive.mode == "r"
        assert archive.password is None


def test_rar_handler_properties() -> None:
    file = "tests/test_data/source_STORE.rar"
    with RarFileAdapter(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.password is None


def test_zip_handler_properties() -> None:
    file = "tests/test_data/source_STORE.zip"
    with ZipFileAdapter(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.password is None


def test_tar_handler_properties() -> None:
    file = "tests/test_data/source_GNU.tar"
    with TarFileAdapter(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.password is None


def test_sevenzip_handler_properties() -> None:
    file = "tests/test_data/source_LZMA.7z"
    with SevenZipFileAdapter(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.password is None
