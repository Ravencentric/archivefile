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

extensions = ("zip", "cbz") + ("tar", "tar.bz2", "tar.gz", "tar.xz", "cbt") + ("7z", "cb7")


ARCHIVE_DIR = Path("src/archivefile").resolve()


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_writeall(tmp_path: Path, mode: str, extension: str) -> None:
    dir = tmp_path / f"{uuid4()}.{extension}"
    with ArchiveFile(dir, mode) as archive:
        archive.writeall(ARCHIVE_DIR, glob="*.py")

    with ArchiveFile(dir, "r") as archive:
        dest = tmp_path / str(uuid4())
        dest.mkdir(parents=True, exist_ok=True)
        archive.extractall(destination=dest)

    assert len(tuple(ARCHIVE_DIR.rglob("*.py"))) == len(tuple(dest.rglob("*.*")))


@pytest.mark.parametrize("extension", extensions)
@pytest.mark.parametrize("mode", modes)
def test_writeall_with_root(tmp_path: Path, mode: str, extension: str) -> None:
    dir = tmp_path / f"{uuid4()}.{extension}"
    with ArchiveFile(dir, mode) as archive:
        archive.writeall(ARCHIVE_DIR, glob="*.py", root=ARCHIVE_DIR.parent.parent)

    with ArchiveFile(dir, "r") as archive:
        dest = tmp_path / str(uuid4())
        dest.mkdir(parents=True, exist_ok=True)
        archive.extractall(destination=dest)

    assert len(tuple(ARCHIVE_DIR.rglob("*.py"))) == len(tuple(dest.rglob("*.*")))
