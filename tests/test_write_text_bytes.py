from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from archivefile import ArchiveFile
from archivefile._enums import CommonExtensions

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
extensions = CommonExtensions.ZIP + CommonExtensions.TAR + CommonExtensions.SEVENZIP


def test_write_text(tmp_path: Path) -> None:
    for extension in extensions:
        for mode in modes:
            dir = tmp_path / f"{uuid4().hex[:10]}{extension}"
            data = "Hello World"
            with ArchiveFile(dir, mode) as archive:  # type: ignore
                archive.write_text(data, arcname="test.txt")

            with ArchiveFile(dir, "r") as archive:
                assert archive.read_text("test.txt") == data


def test_write_bytes(tmp_path: Path) -> None:
    for extension in extensions:
        for mode in modes:
            dir = tmp_path / f"{uuid4().hex[:10]}{extension}"
            data = b"Hello World"
            with ArchiveFile(dir, mode) as archive:  # type: ignore
                archive.write_bytes(data, arcname="test.dat")

            with ArchiveFile(dir, "r") as archive:
                assert archive.read_bytes("test.dat") == data
