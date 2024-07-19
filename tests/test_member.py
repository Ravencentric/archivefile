from __future__ import annotations

from pathlib import Path

from archivefile import ArchiveFile

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
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 1224
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_BZIP2.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_BZIP2.zip") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 1336
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_BZIP2_SOLID.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_DEFLATE.zip") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 1168
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_DEFLATE64.zip") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 1170
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_GNU.tar") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 5251
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_GNU.tar.bz2") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 5251
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_GNU.tar.gz") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 5251
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_GNU.tar.xz") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 5251
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_LZMA.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_LZMA.zip") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 1230
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_LZMA2.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_LZMA2_SOLID.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_LZMA_SOLID.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_POSIX.tar") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 5251
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_POSIX.tar.bz2") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 5251
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_POSIX.tar.gz") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 5251
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_POSIX.tar.xz") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 5251
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_PPMD.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_PPMD.zip") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 1103
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_PPMD_SOLID.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_STORE.7z") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_STORE.rar") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True

    with ArchiveFile("tests/test_data/source_STORE.zip") as archive:
        member = archive.get_member("pyanilist-main/README.md")
        assert  member.name == "pyanilist-main/README.md"
        assert  member.size == 3799
        assert  member.compressed_size == 3799
        assert  member.checksum == 398102207
        assert  member.is_dir is False
        assert  member.is_file is True


def test_get_member_dirs() -> None:
    with ArchiveFile("tests/test_data/source_BEST.rar") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs/"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_BZIP2.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_BZIP2.zip") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs/"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_BZIP2_SOLID.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_DEFLATE.zip") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs/"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_DEFLATE64.zip") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs/"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_GNU.tar") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 5024
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_GNU.tar.bz2") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 5024
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_GNU.tar.gz") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 5024
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_GNU.tar.xz") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 5024
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_LZMA.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_LZMA.zip") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs/"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_LZMA2.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_LZMA2_SOLID.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_LZMA_SOLID.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_POSIX.tar") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 5024
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_POSIX.tar.bz2") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 5024
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_POSIX.tar.gz") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 5024
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_POSIX.tar.xz") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 5024
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_PPMD.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_PPMD.zip") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs/"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_PPMD_SOLID.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_STORE.7z") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_STORE.rar") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs/"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

    with ArchiveFile("tests/test_data/source_STORE.zip") as archive:
        member = archive.get_member("pyanilist-main/docs/")
        assert  member.name == "pyanilist-main/docs/"
        assert  member.size == 0
        assert  member.compressed_size == 0
        assert  member.checksum == 0
        assert  member.is_dir is True
        assert  member.is_file is False

