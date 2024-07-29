from __future__ import annotations

from pathlib import Path

import pytest
from archivefile import ArchiveFile

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

files = (
    Path("tests/test_data/source_BEST.rar"),
    Path("tests/test_data/source_BZIP2.7z"),
    Path("tests/test_data/source_BZIP2.zip"),
    Path("tests/test_data/source_DEFLATE.zip"),
    Path("tests/test_data/source_DEFLATE64.zip"),  # Deflate64 is not supported by ZipFile
    Path("tests/test_data/source_GNU.tar"),
    Path("tests/test_data/source_GNU.tar.bz2"),
    Path("tests/test_data/source_GNU.tar.gz"),
    Path("tests/test_data/source_GNU.tar.xz"),
    Path("tests/test_data/source_LZMA.7z"),
    Path("tests/test_data/source_LZMA.zip"),
    Path("tests/test_data/source_LZMA2.7z"),
    Path("tests/test_data/source_POSIX.tar"),
    Path("tests/test_data/source_POSIX.tar.bz2"),
    Path("tests/test_data/source_POSIX.tar.gz"),
    Path("tests/test_data/source_POSIX.tar.xz"),
    Path("tests/test_data/source_PPMD.7z"),
    Path("tests/test_data/source_PPMD.zip"),  # PPMd is not supported by ZipFile
    Path("tests/test_data/source_STORE.7z"),
    Path("tests/test_data/source_LZMA_SOLID.7z"),
    Path("tests/test_data/source_LZMA2_SOLID.7z"),
    Path("tests/test_data/source_PPMD_SOLID.7z"),
    Path("tests/test_data/source_BZIP2_SOLID.7z"),
    Path("tests/test_data/source_STORE.rar"),
    Path("tests/test_data/source_STORE.zip"),
)


def test_write_rar() -> None:
    with pytest.raises(NotImplementedError):
        with ArchiveFile("somerar.rar", "w") as archive:
            archive.read_text("somefile.txt")

    with pytest.raises(NotImplementedError):
        with ArchiveFile("tests/test_data/source_BEST.rar", "w") as archive:
            archive.print_tree()


def test_write_not_archive() -> None:
    with pytest.raises(NotImplementedError):
        with ArchiveFile("somefile.hello", "w") as archive:
            archive.read_text("somefile.txt")


def test_write_without_write_mode() -> None:
    with pytest.raises(FileNotFoundError):
        with ArchiveFile("somefile.zip", "r") as archive:
            archive.read_text("somefile.txt")


def test_write_mode_x_sevenzip(tmp_path: Path) -> None:
    file = tmp_path / "archive.7z"
    with ArchiveFile(file, "x") as archive:
        archive.write_text("abc1234", arcname="a.txt")

    with pytest.raises(FileExistsError):
        with ArchiveFile(file, "x") as archive:
            archive.write_text("abc1234", arcname="a.txt")


def test_existing_unsupported_archive(tmp_path: Path) -> None:
    file = tmp_path / "archive.yaml"
    file.touch()
    with pytest.raises(NotImplementedError):
        with ArchiveFile(file, "x") as archive:
            archive.write_text("abc1234", arcname="a.txt")


@pytest.mark.parametrize("file", files)
def test_missing_member(file: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.get_member("non-existent.member")


@pytest.mark.parametrize("file", files)
def test_missing_member_in_read_bytes(file: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.read_bytes("non-existent.member")


@pytest.mark.parametrize("file", files)
def test_missing_member_in_read_text(file: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.read_text("non-existent.member")


@pytest.mark.parametrize("file", files)
def test_missing_member_in_extract(file: Path) -> None:
    with pytest.raises(KeyError):
        with ArchiveFile(file) as archive:
            archive.extract("non-existent.member")


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_not_a_file(tmp_path: Path, mode: str, extension: str) -> None:
    with pytest.raises(ValueError):
        archive_file = tmp_path / f"somefile.{extension}"
        with ArchiveFile(archive_file, mode) as archive:
            archive.write(tmp_path)


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_not_a_dir(tmp_path: Path, mode: str, extension: str) -> None:
    with pytest.raises(ValueError):
        archive_file = tmp_path / f"somefile.{extension}"
        file = tmp_path / "somefile.txt"
        file.touch()
        with ArchiveFile(archive_file, mode) as archive:
            archive.writeall(file)


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_writeall_not_dir(tmp_path: Path, mode: str, extension: str) -> None:
    archive_dir = Path("src/archivefile").resolve()
    with pytest.raises(ValueError):
        dir = tmp_path / f"somefile.{extension}"
        with ArchiveFile(dir, mode) as archive:
            archive.writeall(archive_dir, root=tmp_path)
