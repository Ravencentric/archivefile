from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from archivefile import ArchiveFile


def test_get_members(archive_file: ArchiveFile) -> None:
    assert len(tuple(archive_file.get_members())) == 53


def test_get_members_without_context_manager(archive_file: ArchiveFile) -> None:
    total_members = len(tuple(archive_file.get_members()))
    assert total_members == 53


def test_get_names(archive_file: ArchiveFile) -> None:
    assert len(archive_file.get_names()) == 53


def test_get_names_without_context_manager(archive_file: ArchiveFile) -> None:
    total_members = len(archive_file.get_names())
    assert total_members == 53


def test_member_and_names(archive_file: ArchiveFile) -> None:
    names = tuple([member.name for member in archive_file.get_members()])
    assert archive_file.get_names() == names


def test_members_and_names_without_context_manager(archive_file: ArchiveFile) -> None:
    names = tuple([member.name for member in archive_file.get_members()])
    assert archive_file.get_names() == names


def test_get_member_files(archive_file: ArchiveFile) -> None:
    assert archive_file.file == archive_file.file.resolve()
    assert archive_file.password is None

    member = archive_file.get_member("pyanilist-main/README.md")
    assert "pyanilist-main/README.md" in archive_file.get_names()
    assert member.name == "pyanilist-main/README.md" == str(member)
    assert member.size == 3799
    assert member.is_dir is False
    assert member.is_file is True


def test_get_member_dirs(archive_file: ArchiveFile) -> None:
    assert archive_file.file == archive_file.file.resolve()
    assert archive_file.password is None

    member = archive_file.get_member("pyanilist-main/docs/")
    assert "pyanilist-main/docs/" in archive_file.get_names()
    assert member.name == "pyanilist-main/docs/" == str(member)
    assert member.size == 0
    assert member.compressed_size == 0
    assert member.is_dir is True
    assert member.is_file is False
