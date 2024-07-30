from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

import pytest
from archivefile import ArchiveFile, ArchiveMember

files = (
    Path("tests/test_data/source_BEST.rar"),
    Path("tests/test_data/source_BZIP2.7z"),
    Path("tests/test_data/source_BZIP2.zip"),
    Path("tests/test_data/source_DEFLATE.zip"),
    # Path("tests/test_data/source_DEFLATE64.zip"), # Deflate64 is not supported by ZipFile
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
    # Path("tests/test_data/source_PPMD.zip"), # PPMd is not supported by ZipFile
    Path("tests/test_data/source_STORE.7z"),
    Path("tests/test_data/source_LZMA_SOLID.7z"),
    Path("tests/test_data/source_LZMA2_SOLID.7z"),
    Path("tests/test_data/source_PPMD_SOLID.7z"),
    Path("tests/test_data/source_BZIP2_SOLID.7z"),
    Path("tests/test_data/source_STORE.rar"),
    Path("tests/test_data/source_STORE.zip"),
)

# Alias the pre-configured parametrize function for reusability
parametrize_files = pytest.mark.parametrize("file", files, ids=lambda x: x.name)


@parametrize_files
def test_extract(file: Path, tmp_path: Path) -> None:
    with ArchiveFile(file) as archive:
        member = archive.extract("pyanilist-main/README.md", destination=tmp_path)
        assert member.is_file()


@parametrize_files
def test_extract_without_context_manager(file: Path, tmp_path: Path) -> None:
    archive = ArchiveFile(file)
    extracted_file = archive.extract("pyanilist-main/README.md", destination=tmp_path)
    archive.close()
    assert extracted_file.is_file()


@parametrize_files
def test_extract_by_member(file: Path, tmp_path: Path) -> None:
    with ArchiveFile(file) as archive:
        member = [member for member in archive.get_members() if member.is_file][0]
        outfile = archive.extract(member, destination=tmp_path)
        assert outfile.is_file()


@parametrize_files
def test_extractall(file: Path, tmp_path: Path) -> None:
    with ZipFile("tests/test_data/source_STORE.zip") as archive:
        dest = tmp_path / uuid4().hex
        archive.extractall(path=dest)
        control = tuple((dest / "pyanilist-main").rglob("*"))

    with ArchiveFile(file) as archive:
        dest2 = tmp_path / uuid4().hex
        archive.extractall(destination=dest2)
        members = tuple((dest / "pyanilist-main").rglob("*"))
        assert control == members


@parametrize_files
def test_extractall_by_members(file: Path, tmp_path: Path) -> None:
    expected = [
        "pyanilist-main/.gitignore",
        "pyanilist-main/.pre-commit-config.yaml",
        "pyanilist-main/mkdocs.yml",
        "pyanilist-main/poetry.lock",
        "pyanilist-main/pyproject.toml",
    ]

    members = [
        "pyanilist-main/.gitignore",
        Path("pyanilist-main/.pre-commit-config.yaml"),
        ArchiveMember(name="pyanilist-main/mkdocs.yml"),
        "pyanilist-main/poetry.lock",
        "pyanilist-main/pyproject.toml",
    ]

    with ArchiveFile(file) as archive:
        folder = archive.extractall(destination=tmp_path, members=members) / "pyanilist-main"  # type: ignore
        assert len(members) == len(tuple(folder.rglob("*"))) == 5
        assert sorted(expected) == sorted([member.relative_to(tmp_path).as_posix() for member in folder.rglob("*")])
