from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from archivefile import ArchiveFile

modes = (
    "w",
    "w:",
    "w:gz",
    "w:bz2",
    "w:xz",
    "x:",
    "x:",
    "x:gz",
    "x:bz2",
    "x:xz",
    "a",
    "a:",
)

extensions = ("tar", "tar.bz2", "tar.gz", "tar.xz", "cbt") + ("7z", "cb7") + ("zip", "cbz")


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_text(tmp_path: Path, mode: str, extension: str) -> None:
    dir = tmp_path / f"{uuid4()}.{extension}"
    data = "Hello World"
    with ArchiveFile(dir, mode) as archive:
        print(archive)
        archive.write_text(data, arcname="test.txt")

    with ArchiveFile(dir, "r") as archive:
        assert archive.read_text("test.txt") == data


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_write_bytes(tmp_path: Path, mode: str, extension: str) -> None:
    dir = tmp_path / f"{uuid4()}.{extension}"
    data = b"Hello World"
    with ArchiveFile(dir, mode) as archive:
        archive.write_bytes(data, arcname=Path("test.dat"))

    with ArchiveFile(dir, "r") as archive:
        assert archive.read_bytes("test.dat") == data
