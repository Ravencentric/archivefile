from pathlib import Path

from archivefile import ArchiveFile

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


def test_read_text_file() -> None:
    for file in files:
        with ArchiveFile(file) as archive:
            member = archive.read_text("pyanilist-main/UNLICENSE")
            assert member.strip() == unlicense.strip()


def test_read_bytes_file() -> None:
    for file in files:
        with ArchiveFile(file) as archive:
            member = archive.read_bytes("pyanilist-main/UNLICENSE")
            assert member.decode().strip() == unlicense.strip()


def test_read_text_folder() -> None:
    for file in files:
        with ArchiveFile(file) as archive:
            member = archive.read_text("pyanilist-main/src/")
            assert member == ""


def test_read_bytes_folder() -> None:
    for file in files:
        with ArchiveFile(file) as archive:
            member = archive.read_bytes("pyanilist-main/src/")
            assert member == b""
