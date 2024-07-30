from __future__ import annotations

from pathlib import Path

import pytest
from archivefile import ArchiveFile, CompressionType
from archivefile._adapters._rar import RarFileAdapter
from archivefile._adapters._sevenzip import SevenZipFileAdapter
from archivefile._adapters._tar import TarFileAdapter
from archivefile._adapters._zip import ZipFileAdapter


@pytest.mark.parametrize(
    "file,compression_type,compression_level,adapter",
    [
        (Path("tests/test_data/source_GNU.tar"), None, None, "TarFileAdapter"),
        (Path("tests/test_data/source_STORE.7z"), None, None, "SevenZipFileAdapter"),
        (Path("tests/test_data/source_STORE.rar"), None, None, "RarFileAdapter"),
        (Path("tests/test_data/source_STORE.zip"), CompressionType.STORED, None, "ZipFileAdapter"),
    ],
    ids=lambda x: x.name if isinstance(x, Path) else x,  # https://github.com/pytest-dev/pytest/issues/8283
)
def test_core_properties(
    file: Path, compression_type: CompressionType | None, compression_level: int | None, adapter: str
) -> None:
    with ArchiveFile(file) as archive:
        assert archive.file == file.resolve()
        assert archive.mode == "r"
        assert archive.password is None
        assert archive.compression_type == compression_type
        assert archive.compression_level == compression_level
        assert archive.adapter == adapter


def test_rar_handler_properties() -> None:
    file = "tests/test_data/source_STORE.rar"
    with RarFileAdapter(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.password is None
        assert archive.compression_type is None
        assert archive.compression_level is None
        assert archive.adapter == "RarFileAdapter"


def test_zip_handler_properties() -> None:
    file = "tests/test_data/source_STORE.zip"
    with ZipFileAdapter(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.password is None
        assert archive.compression_type is CompressionType.STORED
        assert archive.compression_level is None
        assert archive.adapter == "ZipFileAdapter"


def test_tar_handler_properties() -> None:
    file = "tests/test_data/source_GNU.tar"
    with TarFileAdapter(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.password is None
        assert archive.compression_type is None
        assert archive.compression_level is None
        assert archive.adapter == "TarFileAdapter"


def test_sevenzip_handler_properties() -> None:
    file = "tests/test_data/source_LZMA.7z"
    with SevenZipFileAdapter(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.password is None
        assert archive.compression_type is None
        assert archive.compression_level is None
        assert archive.adapter == "SevenZipFileAdapter"
