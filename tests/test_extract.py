from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4
from zipfile import ZipFile

if TYPE_CHECKING:
    from archivefile import ArchiveFile


def test_extract(archive_file: ArchiveFile, tmp_path: Path) -> None:
    member = archive_file.extract("pyanilist-main/README.md", destination=tmp_path)
    assert member.is_file()


def test_extract_without_context_manager(archive_file: ArchiveFile, tmp_path: Path) -> None:
    extracted_file = archive_file.extract("pyanilist-main/README.md", destination=tmp_path)
    assert extracted_file.is_file()


def test_extract_by_member(archive_file: ArchiveFile, tmp_path: Path) -> None:
    member = next(member for member in archive_file.get_members() if member.is_file)
    outfile = archive_file.extract(member, destination=tmp_path)
    assert outfile.is_file()


def test_extractall(archive_file: ArchiveFile, tmp_path: Path) -> None:
    with ZipFile("tests/test_data/source_LZMA.zip") as archive:
        dest = tmp_path / uuid4().hex
        archive.extractall(path=dest)
        control = tuple((dest / "pyanilist-main").rglob("*"))

    dest2 = tmp_path / uuid4().hex
    archive_file.extractall(destination=dest2)
    members = tuple((dest / "pyanilist-main").rglob("*"))
    assert control == members


def test_extractall_by_members(archive_file: ArchiveFile, tmp_path: Path) -> None:
    expected = [
        "pyanilist-main/.gitignore",
        "pyanilist-main/.pre-commit-config.yaml",
        "pyanilist-main/poetry.lock",
        "pyanilist-main/pyproject.toml",
    ]

    members: list[str | Path] = [
        "pyanilist-main/.gitignore",
        Path("pyanilist-main/.pre-commit-config.yaml"),
        "pyanilist-main/poetry.lock",
        "pyanilist-main/pyproject.toml",
    ]

    folder = archive_file.extractall(destination=tmp_path, members=members) / "pyanilist-main"
    assert len(members) == len(tuple(folder.rglob("*"))) == 4
    assert sorted(expected) == sorted([member.relative_to(tmp_path).as_posix() for member in folder.rglob("*")])
