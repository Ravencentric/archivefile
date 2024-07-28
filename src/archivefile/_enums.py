from __future__ import annotations

from enum import IntEnum
from typing import Literal


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

    @classmethod
    def get(
        cls,
        key: str | int | CompressionType | None = None,
        default: Literal["stored", "deflated", "bzip2", "lzma"] = "stored",
    ) -> CompressionType:
        """
        Get the `CompressionType` by its name or number.
        Return the default if the key is missing or invalid.

        Parameters
        ----------
        key : str | int | CompressionType, optional
            They key to retrieve.

        Returns
        -------
        CompressionType
        """
        try:
            match key:
                case str():
                    return cls[key.upper()]

                case int():
                    return cls(key)

                case _:
                    return cls[default.upper()]
        except (KeyError, ValueError):
            return cls[default.upper()]
