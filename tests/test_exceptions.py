from pathlib import Path

import pytest
from archivefile import ArchiveFile, UnsupportedArchiveOperation


def test_write_rar() -> None:
    with pytest.raises(UnsupportedArchiveOperation):
        with ArchiveFile("somerar.rar", "w") as archive:
            archive.read_text("somefile.txt")

    with pytest.raises(UnsupportedArchiveOperation):
        with ArchiveFile("tests/test_data/source_BEST.rar", "w") as archive:
            archive.tree()


def test_write_not_archive() -> None:
    with pytest.raises(UnsupportedArchiveOperation):
        with ArchiveFile("somefile.hello", "w") as archive:
            archive.read_text("somefile.txt")


def test_write_without_write_mode() -> None:
    with pytest.raises(FileNotFoundError):
        with ArchiveFile("somefile.zip", "r") as archive:
            archive.read_text("somefile.txt")


def test_write_x_sevenzip(tmp_path: Path) -> None:
    file = tmp_path / "archive.7z"
    with ArchiveFile(file, "x") as archive:
        archive.write_text("abc1234", arcname="a.txt")

    with pytest.raises(FileExistsError):
        with ArchiveFile(file, "x") as archive:
            archive.write_text("abc1234", arcname="a.txt")


def test_existing_unsupported_archive(tmp_path: Path) -> None:
    file = tmp_path / "archive.yaml"
    file.touch()
    with pytest.raises(UnsupportedArchiveOperation):
        with ArchiveFile(file, "x") as archive:
            archive.write_text("abc1234", arcname="a.txt")


def test_write_not_a_file(tmp_path: Path) -> None:
    with pytest.raises(UnsupportedArchiveOperation):
        archive_file = tmp_path / "somefile.tar"
        with ArchiveFile(archive_file, "w") as archive:
            archive.write(tmp_path)


def test_write_not_a_dir(tmp_path: Path) -> None:
    with pytest.raises(UnsupportedArchiveOperation):
        archive_file = tmp_path / "somefile.tar"
        file = tmp_path / "somefile.txt"
        file.touch()
        with ArchiveFile(archive_file, "w") as archive:
            archive.writeall(file)


def test_writeall_not_dir(tmp_path: Path) -> None:
    archive_dir = Path("src/archivefile").resolve()
    with pytest.raises(ValueError):
        dir = tmp_path / "somefile.zip"
        with ArchiveFile(dir, "w") as archive:
            archive.writeall(archive_dir, root=tmp_path)
