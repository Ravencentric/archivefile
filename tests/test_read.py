from archivefile import ArchiveFile

unlicense = """\
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>
"""

def test_read_text() -> None:
    with ArchiveFile("tests/test_data/source_BEST.rar") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_BZIP2.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_BZIP2.zip") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_DEFLATE.zip") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_GNU.tar") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_GNU.tar.bz2") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_GNU.tar.gz") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_GNU.tar.xz") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA.zip") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA2.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_POSIX.tar") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_POSIX.tar.bz2") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_POSIX.tar.gz") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_POSIX.tar.xz") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_PPMD.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_STORE.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA_SOLID.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA2_SOLID.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_PPMD_SOLID.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_BZIP2_SOLID.7z") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_STORE.rar") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_STORE.zip") as archive:
        member = archive.read_text("pyanilist-main/UNLICENSE")
        assert member.strip() == unlicense.strip()


def test_read_bytes() -> None:
    with ArchiveFile("tests/test_data/source_BEST.rar") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_BZIP2.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_BZIP2.zip") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_DEFLATE.zip") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_GNU.tar") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_GNU.tar.bz2") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_GNU.tar.gz") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_GNU.tar.xz") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA.zip") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA2.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_POSIX.tar") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_POSIX.tar.bz2") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_POSIX.tar.gz") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_POSIX.tar.xz") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_PPMD.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_STORE.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA_SOLID.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_LZMA2_SOLID.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_PPMD_SOLID.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_BZIP2_SOLID.7z") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_STORE.rar") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()

    with ArchiveFile("tests/test_data/source_STORE.zip") as archive:
        member = archive.read_bytes("pyanilist-main/UNLICENSE")
        assert member.decode().strip() == unlicense.strip()
