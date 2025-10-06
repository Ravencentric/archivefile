from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._types import StrPath


class ArchiveFileError(Exception):
    """
    Base exception for all ArchiveFile errors.
    """

    __module__ = "archivefile"

    def __init_subclass__(cls) -> None:
        # Ensure subclasses also appear as part of the public 'archivefile' module
        # in tracebacks, instead of the internal implementation module.
        cls.__module__ = "archivefile"

    def __init__(self, message: str, /, *, file: StrPath) -> None:
        self._file = Path(file)
        super().__init__(message)

    @property
    def file(self) -> Path:
        """The archive file related to the error."""
        return self._file


class UnsupportedArchiveFormatError(ArchiveFileError):
    """
    Raised when the archive file format is unsupported or unrecognized.
    """

    def __init__(self, *, file: StrPath) -> None:
        filename = Path(file).as_posix()
        message = (
            f"Unsupported or unrecognized archive format for file: {filename!r}.\n"
            "If this is a 7z or rar archive, support is available via the optional "
            "extras 'archivefile[7z]' and 'archivefile[rar]'."
        )
        super().__init__(message, file=file)


class ArchiveMemberNotFoundError(ArchiveFileError):
    """
    Raised when a specified member (file or directory) is not found inside the archive file.
    """

    def __init__(self, *, member: str, file: StrPath) -> None:
        self._member = member
        filename = Path(file).as_posix()
        message = f"Archive member {member!r} not found in file: {filename!r}"
        super().__init__(message, file=file)

    @property
    def member(self) -> str:
        """The member that was not found."""
        return self._member


class ArchiveMemberNotAFileError(ArchiveFileError):
    """
    Raised when a specified member is not a file (e.g., it's a directory).
    """

    def __init__(self, *, member: str, file: StrPath) -> None:
        self._member = member
        filename = Path(file).as_posix()
        message = f"Archive member {member!r} in file {filename!r} exists but is not a file."
        super().__init__(message, file=file)

    @property
    def member(self) -> str:
        """The member that is not a file."""
        return self._member
