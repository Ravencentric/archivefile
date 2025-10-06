from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from archivefile import ArchiveMemberNotAFileError

if TYPE_CHECKING:
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


def test_read_text_file(archive_file: ArchiveFile) -> None:
    member = archive_file.read_text("pyanilist-main/UNLICENSE")
    assert member.strip() == unlicense.strip()


def test_read_bytes_file(archive_file: ArchiveFile) -> None:
    member = archive_file.read_bytes("pyanilist-main/UNLICENSE")
    assert member.decode().strip() == unlicense.strip()


def test_read_text_folder(archive_file: ArchiveFile) -> None:
    filename = archive_file.file.as_posix()
    message = rf"Archive member 'pyanilist-main/src/' in file {filename!r} exists but is not a file."
    with pytest.raises(ArchiveMemberNotAFileError, match=message) as exc:
        archive_file.read_text("pyanilist-main/src/")

    assert exc.value.member == "pyanilist-main/src/"
    assert exc.value.file == archive_file.file


def test_read_bytes_folder(archive_file: ArchiveFile) -> None:
    filename = archive_file.file.as_posix()
    message = rf"Archive member 'pyanilist-main/src/' in file {filename!r} exists but is not a file."
    with pytest.raises(ArchiveMemberNotAFileError, match=message) as exc:
        archive_file.read_bytes("pyanilist-main/src/")

    assert exc.value.member == "pyanilist-main/src/"
    assert exc.value.file == archive_file.file
