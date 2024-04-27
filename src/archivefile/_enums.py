from __future__ import annotations

from enum import Enum, IntEnum


class ZipCompression(IntEnum):
    ZIP_STORED = 0
    ZIP_DEFLATED = 8
    ZIP_BZIP2 = 12
    ZIP_LZMA = 14


class CommonExtensions(tuple[str, ...], Enum):
    ZIP = (".zip", ".cbz")
    TAR = (".tar", ".tar.bz2", ".tar.gz", ".tar.xz", ".cbt")
    SEVENZIP = (".7z", ".cb7")
    RAR = (".rar", ".cbr")
