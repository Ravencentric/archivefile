from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from archivefile import ArchiveFile, CompressionType

modes = (
    "w",
    "w:",
    "w:gz",
    "w:bz2",
    "w:xz",
    "x:",
    "x:",
    "x:gz",
    "x:bz2",
    "x:xz",
    "a",
    "a:",
)

extensions = ("zip", "cbz") + ("tar", "tar.bz2", "tar.gz", "tar.xz", "cbt") + ("7z", "cb7")


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_str(tmp_path: Path, mode: str, extension: str) -> None:
    archive_file = tmp_path / f"{uuid4()}.{extension}"
    file = tmp_path / "README.md"
    file.touch()
    text = "Hello World"
    file.write_text(text)

    with ArchiveFile(archive_file, mode=mode) as archive:
        archive.write(file)

    with ArchiveFile(archive_file) as archive:
        assert archive.read_text(file.name).strip() == text


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_str_with_compression(tmp_path: Path, mode: str, extension: str) -> None:
    archive_file = tmp_path / f"{uuid4()}.{extension}"
    file = tmp_path / "README.md"
    file.touch()
    text = "Hello World"
    file.write_text(text)

    with ArchiveFile(archive_file, mode=mode, compression_level=0, compression_type=CompressionType.BZIP2) as archive:
        archive.write(file)

    with ArchiveFile(archive_file) as archive:
        assert archive.read_text(file.name).strip() == text


@pytest.mark.parametrize("extension", ("zip", "cbz"))
@pytest.mark.parametrize("mode", modes)
def test_write_str_with_bzip2_compression(tmp_path: Path, mode: str, extension: str) -> None:
    archive_file = tmp_path / f"{uuid4()}.{extension}"
    file = tmp_path / "README.md"
    file.touch()
    text = "Hello World"
    file.write_text(text)

    with ArchiveFile(archive_file, mode=mode, compression_level=0, compression_type=CompressionType.BZIP2) as archive:
        assert archive.compression_level == 1
        archive.write(file)

    with ArchiveFile(archive_file) as archive:
        assert archive.read_text(file.name).strip() == text


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_zip_bytes(tmp_path: Path, mode: str, extension: str) -> None:
    archive_file = tmp_path / f"{uuid4()}.{extension}"
    file = tmp_path / "README.md"
    file.touch()
    text = b"Hello World"
    file.write_bytes(text)

    with ArchiveFile(archive_file, mode=mode) as archive:
        archive.write(file)

    with ArchiveFile(archive_file) as archive:
        assert archive.read_bytes(file.name) == text


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_bytes_with_compression(tmp_path: Path, mode: str, extension: str) -> None:
    archive_file = tmp_path / f"{uuid4()}.{extension}"
    file = tmp_path / "README.md"
    file.touch()
    text = b"Hello World"
    file.write_bytes(text)

    with ArchiveFile(
        archive_file, mode=mode, compression_level=1, compression_type=CompressionType.DEFLATED
    ) as archive:
        archive.write(file)

    with ArchiveFile(archive_file) as archive:
        assert archive.read_bytes(file.name) == text


@pytest.mark.parametrize("extension", ("zip", "cbz"))
@pytest.mark.parametrize("mode", modes)
def test_write_bytes_with_bzip2_compression(tmp_path: Path, mode: str, extension: str) -> None:
    archive_file = tmp_path / f"{uuid4()}.{extension}"
    file = tmp_path / "README.md"
    file.touch()
    text = b"Hello World"
    file.write_bytes(text)

    with ArchiveFile(
        archive_file, mode=mode, compression_level=0, compression_type=CompressionType.DEFLATED
    ) as archive:
        assert archive.compression_level == 0
        archive.write(file)

    with ArchiveFile(archive_file) as archive:
        assert archive.read_bytes(file.name) == text


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_str_by_arcname(tmp_path: Path, mode: str, extension: str) -> None:
    archive_file = tmp_path / f"{uuid4()}.{extension}"
    file = tmp_path / "README.md"
    file.touch()
    text = "Hello World"
    file.write_text(text)

    with ArchiveFile(archive_file, mode=mode) as archive:
        archive.write(file, arcname=file.resolve())

    with ArchiveFile(archive_file) as archive:
        assert archive.read_text(file.resolve()).strip() == text


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_zip_bytes_by_arcname(tmp_path: Path, mode: str, extension: str) -> None:
    archive_file = tmp_path / f"{uuid4()}.{extension}"
    file = tmp_path / "README.md"
    file.touch()
    text = b"Hello World"
    file.write_bytes(text)

    with ArchiveFile(archive_file, mode=mode) as archive:
        archive.write(file, arcname=file.resolve())

    with ArchiveFile(archive_file) as archive:
        assert archive.read_bytes(file.resolve()).strip() == text
