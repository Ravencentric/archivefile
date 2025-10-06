from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from archivefile import ArchiveFile, ArchiveMemberNotFoundError, UnsupportedArchiveFormatError

if TYPE_CHECKING:
    from pathlib import Path


def test_non_existent_file_error(tmp_path: Path) -> None:
    archive_path = tmp_path / "foo.zip"
    with pytest.raises(FileNotFoundError, match=re.escape(str(archive_path))):
        ArchiveFile(archive_path)


def test_unsupported_archive_format_error(tmp_path: Path) -> None:
    archive_path = tmp_path / "foo.zip"
    archive_path.write_text("This is not a valid archive format.")
    filename = archive_path.as_posix()
    message = (
        f"Unsupported or unrecognized archive format for file: {filename!r}.\n"
        "If this is a 7z or rar archive, support is available via the optional "
        "extras 'archivefile[7z]' and 'archivefile[rar]'."
    )
    with pytest.raises(UnsupportedArchiveFormatError, match=re.escape(message)) as exc:
        ArchiveFile(archive_path)

    assert exc.value.file == archive_path


def test_bad_type_member(archive_file: ArchiveFile) -> None:
    message = "Unsupported type for 'member'. Expected 'str', 'PathLike', or 'ArchiveMember', but got 'object'."
    with pytest.raises(TypeError, match=message):
        archive_file.get_member(object())  # type: ignore[arg-type]


def test_missing_member(archive_file: ArchiveFile) -> None:
    filename = archive_file.file.as_posix()
    message = re.escape(f"Archive member 'non-existent.member' not found in file: {filename!r}")
    with pytest.raises(ArchiveMemberNotFoundError, match=message) as exc:
        archive_file.get_member("non-existent.member")

    assert exc.value.file == archive_file.file


def test_missing_member_in_read_bytes(archive_file: ArchiveFile) -> None:
    filename = archive_file.file.as_posix()
    message = re.escape(f"Archive member 'non-existent.member' not found in file: {filename!r}")
    with pytest.raises(ArchiveMemberNotFoundError, match=message) as exc:
        archive_file.read_bytes("non-existent.member")

    assert exc.value.member == "non-existent.member"
    assert exc.value.file == archive_file.file


def test_missing_member_in_read_text(archive_file: ArchiveFile) -> None:
    filename = archive_file.file.as_posix()
    message = re.escape(f"Archive member 'non-existent.member' not found in file: {filename!r}")
    with pytest.raises(ArchiveMemberNotFoundError, match=message) as exc:
        archive_file.read_text("non-existent.member")

    assert exc.value.member == "non-existent.member"
    assert exc.value.file == archive_file.file


def test_missing_member_in_extract(archive_file: ArchiveFile) -> None:
    filename = archive_file.file.as_posix()
    message = re.escape(f"Archive member 'non-existent.member' not found in file: {filename!r}")
    with pytest.raises(ArchiveMemberNotFoundError, match=message) as exc:
        archive_file.extract("non-existent.member")

    assert exc.value.member == "non-existent.member"
    assert exc.value.file == archive_file.file


def test_missing_member_in_extractall(archive_file: ArchiveFile, tmp_path: Path) -> None:
    filename = archive_file.file.as_posix()
    message = re.escape(f"Archive member 'non-existent.member' not found in file: {filename!r}")
    with pytest.raises(ArchiveMemberNotFoundError, match=message) as exc:
        archive_file.extractall(destination=tmp_path, members=["non-existent.member"])

    assert exc.value.member == "non-existent.member"
    assert exc.value.file == archive_file.file
