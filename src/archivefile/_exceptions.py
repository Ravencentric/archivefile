class ArchiveFileError(Exception):
    """Base exception"""

class UnsupportedArchiveOperation(ArchiveFileError):
    """Tried to do an unsupported operation"""