from __future__ import annotations

from archivefile._core import ArchiveFile
from archivefile._enums import CompressionType
from archivefile._models import ArchiveMember
from archivefile._utils import is_archive
from archivefile._version import Version, _get_version

__version__ = _get_version()
__version_tuple__ = Version(*[int(i) for i in __version__.split(".")])

__all__ = [
    "ArchiveFile",
    "ArchiveMember",
    "is_archive",
    "CompressionType",
]
