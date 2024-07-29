from __future__ import annotations

from pathlib import Path
from tarfile import is_tarfile
from zipfile import is_zipfile

from py7zr import is_7zfile
from rarfile import is_rarfile, is_rarfile_sfx

from archivefile._models import ArchiveMember
from archivefile._types import StrPath


def realpath(path: StrPath) -> Path:
    """
    Get the real path of a given file or directory.

    Parameters
    ----------
    path : str or Path
        A string representing a path or a Path object.

    Returns
    -------
    Path
        The path after expanding the user's home directory and resolving any symbolic links.
    """
    return path.expanduser().resolve() if isinstance(path, Path) else Path(path).expanduser().resolve()


def is_archive(file: StrPath) -> bool:
    """
    Check whether the given archive file is a supported archive or not.

    Parameters
    ---------
    file : StrPath
        Path to the archive file.

    Returns
    -------
    bool
        True if the archive is supported, False otherwise.
    """
    file = realpath(file)

    if file.exists():
        return is_tarfile(file) or is_zipfile(file) or is_rarfile(file) or is_rarfile_sfx(file) or is_7zfile(file)
    else:
        return False


def get_member_name(member: StrPath | ArchiveMember) -> str:
    """Get the member name from a string, path, or ArchiveMember"""

    match member:
        case ArchiveMember():
            return member.name

        case Path():
            return member.relative_to(member.anchor).as_posix()

        case _:
            return member


def clamp_compression_level(level: int) -> int:
    """
    Pretty simple method to clamp compression level to a valid range
    """
    return max(0, min(level, 9))
