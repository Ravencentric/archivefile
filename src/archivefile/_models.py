from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class ArchiveMember:
    """
    Represents a member of an archive file.
    """

    name: str
    """Name of the archive member."""

    size: int
    """Uncompressed size of the archive member."""

    compressed_size: int
    """Compressed size of the archive member."""

    is_dir: bool
    """True if the archive member is a directory, False otherwise."""

    is_file: bool
    """True if the archive member is a file, False otherwise."""

    def __str__(self) -> str:
        return self.name
