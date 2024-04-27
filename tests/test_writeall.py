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
archive_dir = Path(r"src\archivefile")

def test_writeall(tmp_path: Path) -> None:
    for extension in CommonExtensions.ZIP:
        for mode in modes:
            dir = tmp_path / f"{uuid4().hex[:10]}{extension}"
            with ArchiveFile(dir, mode) as archive: # type: ignore
                archive.writeall(archive_dir, glob="*.py")

            with ArchiveFile(dir, "r") as archive:
                dest = tmp_path / uuid4().hex[:10]
                dest.mkdir(parents=True, exist_ok=True)
                archive.extractall(dest)

            assert len(tuple(archive_dir.rglob("*.py"))) == len(tuple(dest.rglob("*.*")))

def test_writeall_with_root(tmp_path: Path) -> None:
    for extension in CommonExtensions.ZIP:
        for mode in modes:
            dir = tmp_path / f"{uuid4().hex[:10]}{extension}"
            with ArchiveFile(dir, mode) as archive:  # type: ignore
                archive.writeall(archive_dir, glob="*.py", root=archive_dir.parent.parent)

            with ArchiveFile(dir, "r") as archive:
                dest = tmp_path / uuid4().hex[:10]
                dest.mkdir(parents=True, exist_ok=True)
                archive.extractall(dest)

            assert len(tuple(archive_dir.rglob("*.py"))) == len(tuple(dest.rglob("*.*")))
