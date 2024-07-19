from __future__ import annotations

import datetime
from pathlib import Path

from archivefile import ArchiveFile, ArchiveMember
from pydantic import ByteSize

files = (
    Path("tests/test_data/source_BEST.rar"),
    Path("tests/test_data/source_BZIP2.7z"),
    Path("tests/test_data/source_BZIP2.zip"),
    Path("tests/test_data/source_DEFLATE.zip"),
    Path("tests/test_data/source_DEFLATE64.zip"),
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
    Path("tests/test_data/source_PPMD.zip"),
    Path("tests/test_data/source_STORE.7z"),
    Path("tests/test_data/source_LZMA_SOLID.7z"),
    Path("tests/test_data/source_LZMA2_SOLID.7z"),
    Path("tests/test_data/source_PPMD_SOLID.7z"),
    Path("tests/test_data/source_BZIP2_SOLID.7z"),
    Path("tests/test_data/source_STORE.rar"),
    Path("tests/test_data/source_STORE.zip"),
)


def test_get_members() -> None:
    for file in files:
        with ArchiveFile(file) as archive:
            assert len(archive.get_members()) == 53


def test_get_members_without_context_manager() -> None:
    for file in files:
        archive = ArchiveFile(file)
        total_members = len(archive.get_members())
        archive.close()
        assert total_members == 53


def test_get_names() -> None:
    for file in files:
        with ArchiveFile(file) as archive:
            assert len(archive.get_names()) == 53


def test_get_names_without_context_manager() -> None:
    for file in files:
        archive = ArchiveFile(file)
        total_members = len(archive.get_names())
        archive.close()
        assert total_members == 53


def test_member_and_names() -> None:
    for file in files:
        with ArchiveFile(file) as archive:
            names = tuple([member.name for member in archive.get_members()])
            assert archive.get_names() == names


def test_members_and_names_without_context_manager() -> None:
    for file in files:
        archive = ArchiveFile(file)
        names = tuple([member.name for member in archive.get_members()])
        assert archive.get_names() == names
        archive.close()


def test_get_member_files() -> None:
    with ArchiveFile("tests/test_data/source_BEST.rar") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(1224),
            datetime=datetime.datetime(2024, 4, 10, 14, 40, 57, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_BZIP2.7z") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_BZIP2.zip") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(1336),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_DEFLATE.zip") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(1168),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_DEFLATE64.zip") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(1170),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_GNU.tar") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5251,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_GNU.tar.bz2") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5251,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_GNU.tar.gz") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5251,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_GNU.tar.xz") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5251,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_LZMA.7z") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_LZMA.zip") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(1230),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_LZMA2.7z") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_POSIX.tar") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5251,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_POSIX.tar.bz2") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5251,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_POSIX.tar.gz") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5251,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_POSIX.tar.xz") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5251,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_PPMD.7z") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_PPMD.zip") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(1103),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_STORE.7z") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_STORE.rar") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 14, 40, 57, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )

    with ArchiveFile("tests/test_data/source_STORE.zip") as archive:
        assert archive.get_member("pyanilist-main/README.md") == ArchiveMember(
            name="pyanilist-main/README.md",
            size=ByteSize(3799),
            compressed_size=ByteSize(3799),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=398102207,
            is_dir=False,
            is_file=True,
        )


def test_get_member_dirs() -> None:
    with ArchiveFile("tests/test_data/source_BEST.rar") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs/",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 14, 40, 57, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_BZIP2.7z") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_BZIP2.zip") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs/",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_DEFLATE.zip") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs/",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_DEFLATE64.zip") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs/",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_GNU.tar") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5024,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_GNU.tar.bz2") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5024,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_GNU.tar.gz") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5024,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_GNU.tar.xz") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5024,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_LZMA.7z") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_LZMA.zip") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs/",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_LZMA2.7z") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_POSIX.tar") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5024,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_POSIX.tar.bz2") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5024,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_POSIX.tar.gz") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5024,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_POSIX.tar.xz") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=5024,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_PPMD.7z") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_PPMD.zip") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs/",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_STORE.7z") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_STORE.rar") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs/",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 14, 40, 57, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )

    with ArchiveFile("tests/test_data/source_STORE.zip") as archive:
        assert archive.get_member("pyanilist-main/docs/") == ArchiveMember(
            name="pyanilist-main/docs/",
            size=ByteSize(0),
            compressed_size=ByteSize(0),
            datetime=datetime.datetime(2024, 4, 10, 20, 10, 58, tzinfo=datetime.timezone.utc),
            checksum=0,
            is_dir=True,
            is_file=False,
        )
