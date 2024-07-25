from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from archivefile import ArchiveFile, CompressionType
from archivefile._enums import CommonExtensions

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


def test_write_zip_str(tmp_path: Path) -> None:
    for extension in CommonExtensions.ZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = "Hello World"
            file.write_text(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file)

            with ArchiveFile(archive_file) as archive:
                assert archive.read_text(file.name).strip() == text


def test_write_zip_str_with_compression(tmp_path: Path) -> None:
    for extension in CommonExtensions.ZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = "Hello World"
            file.write_text(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file, compression_level=0, compression_type=CompressionType.BZIP2)

            with ArchiveFile(archive_file) as archive:
                assert archive.read_text(file.name).strip() == text


def test_write_zip_bytes(tmp_path: Path) -> None:
    for extension in CommonExtensions.ZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = b"Hello World"
            file.write_bytes(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file)

            with ArchiveFile(archive_file) as archive:
                assert archive.read_bytes(file.name) == text


def test_write_zip_bytes_with_compression(tmp_path: Path) -> None:
    for extension in CommonExtensions.ZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = b"Hello World"
            file.write_bytes(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file, compression_level=1, compression_type=CompressionType.DEFLATED)

            with ArchiveFile(archive_file) as archive:
                assert archive.read_bytes(file.name) == text


def test_write_zip_str_by_arcname(tmp_path: Path) -> None:
    for extension in CommonExtensions.ZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = "Hello World"
            file.write_text(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file, arcname=file.resolve())

            with ArchiveFile(archive_file) as archive:
                assert archive.read_text(file.resolve()).strip() == text


def test_write_zip_bytes_by_arcname(tmp_path: Path) -> None:
    for extension in CommonExtensions.ZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = b"Hello World"
            file.write_bytes(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file, arcname=file.resolve())

            with ArchiveFile(archive_file) as archive:
                assert archive.read_bytes(file.resolve()).strip() == text


def test_write_tar_str(tmp_path: Path) -> None:
    for extension in CommonExtensions.TAR:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = "Hello World"
            file.write_text(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file)

            with ArchiveFile(archive_file) as archive:
                assert archive.read_text(file.name).strip() == text


def test_write_tar_bytes(tmp_path: Path) -> None:
    for extension in CommonExtensions.TAR:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = b"Hello World"
            file.write_bytes(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file)

            with ArchiveFile(archive_file) as archive:
                assert archive.read_bytes(file.name).strip() == text


def test_write_zip_tar_by_arcname(tmp_path: Path) -> None:
    for extension in CommonExtensions.TAR:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = "Hello World"
            file.write_text(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file, arcname=file.resolve())

            with ArchiveFile(archive_file) as archive:
                assert archive.read_text(file.resolve()).strip() == text


def test_write_tar_bytes_by_arcname(tmp_path: Path) -> None:
    for extension in CommonExtensions.TAR:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = b"Hello World"
            file.write_bytes(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file, arcname=file.resolve())

            with ArchiveFile(archive_file) as archive:
                assert archive.read_bytes(file.resolve()).strip() == text


def test_write_7z_str(tmp_path: Path) -> None:
    for extension in CommonExtensions.SEVENZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = "Hello World"
            file.write_text(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file)

            with ArchiveFile(archive_file) as archive:
                assert archive.read_text(file.name).strip() == text


def test_write_7z_bytes(tmp_path: Path) -> None:
    for extension in CommonExtensions.SEVENZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = b"Hello World"
            file.write_bytes(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file)

            with ArchiveFile(archive_file) as archive:
                assert archive.read_bytes(file.name).strip() == text


def test_write_7z_tar_by_arcname(tmp_path: Path) -> None:
    for extension in CommonExtensions.SEVENZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = "Hello World"
            file.write_text(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file, arcname=file.resolve())

            with ArchiveFile(archive_file) as archive:
                assert archive.read_text(file.resolve()).strip() == text


def test_write_7z_bytes_by_arcname(tmp_path: Path) -> None:
    for extension in CommonExtensions.SEVENZIP:
        for mode in modes:
            archive_file = tmp_path / f"{uuid4().hex[:10]}{extension}"
            file = tmp_path / "README.md"
            file.touch()
            text = b"Hello World"
            file.write_bytes(text)

            with ArchiveFile(archive_file, mode=mode) as archive:  # type: ignore
                archive.write(file, arcname=file.resolve())

            with ArchiveFile(archive_file) as archive:
                assert archive.read_bytes(file.resolve()).strip() == text
