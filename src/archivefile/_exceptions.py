from __future__ import annotations


class ArchiveFileError(Exception):
    """Base exception."""


class UnsupportedArchiveOperation(ArchiveFileError):
    """Tried to do an unsupported operation."""
