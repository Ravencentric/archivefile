from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from ._errors import ArchiveMemberNotFoundError
from ._models import ArchiveMember

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from ._types import MemberLike, StrPath


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
    return Path(path).expanduser().resolve()


def get_member_name(member: MemberLike, /) -> str:
    """Get the member name from a string, path, or ArchiveMember."""

    match member:
        case str():
            return member

        case ArchiveMember():
            return member.name

        case os.PathLike():
            return Path(member).as_posix()

        case _:
            msg = (
                f"Unsupported type for 'member'. Expected 'str', 'PathLike', or 'ArchiveMember', "
                f"but got {type(member).__name__!r}."
            )
            raise TypeError(msg)


def validate_members(requested: Iterable[MemberLike], /, *, available: Iterable[str], archive: Path) -> Sequence[str]:
    """
    Validate and normalize requested archive members.

    Parameters
    ----------
    requested : Iterable[str]
        File names requested by the user. May contain duplicates.
        Order will be preserved.
    available : Iterable[str]
        All available member names in the archive.
    archive : str
        Path to the archive file, used in error reporting.

    Returns
    -------
    Sequence[str]
        Normalized, validated file names. Preserves the input order and
        removes duplicates.

    Raises
    ------
    ArchiveMemberNotFoundError
        If a requested file is not present in the archive.

    """
    available = set(available)
    seen: set[str] = set()
    out: list[str] = []

    for req in requested:
        name = get_member_name(req)
        if name not in available:
            raise ArchiveMemberNotFoundError(member=name, file=archive) from None
        if name not in seen:
            seen.add(name)
            out.append(name)

    return out
