from __future__ import annotations

from enum import Enum, IntEnum


class CompressionType(IntEnum):
    """Compression algorithms for ZipFile"""

    STORED = 0
    """The numeric constant for an uncompressed archive member."""
    DEFLATED = 8
    """
    The numeric constant for the usual ZIP compression method. 
    This requires the [zlib](https://docs.python.org/3/library/zlib.html#module-zlib) module.
    """
    BZIP2 = 12
    """
    The numeric constant for the BZIP2 compression method. 
    This requires the [bz2](https://docs.python.org/3/library/bz2.html#module-bz2) module.
    """
    LZMA = 14
    """
    The numeric constant for the LZMA compression method. 
    This requires the [lzma](https://docs.python.org/3/library/lzma.html#module-lzma) module.
    """


class CommonExtensions(tuple[str, ...], Enum):
    ZIP = (".zip", ".cbz")
    TAR = (".tar", ".tar.bz2", ".tar.gz", ".tar.xz", ".cbt")
    SEVENZIP = (".7z", ".cb7")
    RAR = (".rar", ".cbr")
