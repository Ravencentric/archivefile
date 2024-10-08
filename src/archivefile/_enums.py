from __future__ import annotations

from enum import IntEnum
from typing import Literal, overload


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

    @overload
    @classmethod
    def get(
        cls,
        key: str | int | None = None,
        default: Literal["stored", "deflated", "bzip2", "lzma"] = "stored",
    ) -> CompressionType: ...

    @overload
    @classmethod
    def get(cls, key: str | int | None = None, default: str | int = "stored") -> CompressionType: ...

    @classmethod
    def get(
        cls,
        key: str | int | None = None,
        default: Literal["stored", "deflated", "bzip2", "lzma"] | str | int = "stored",
    ) -> CompressionType:
        """
        Get the `CompressionType` by its name or number.
        Return the default if the key is missing or invalid.

        Parameters
        ----------
        key : str | int, optional
            The key to retrieve.
        default : Literal["stored", "deflated", "bzip2", "lzma"] | str | int, optional
            The default value to return if the key is missing or invalid.

        Returns
        -------
        CompressionType
            The `CompressionType` corresponding to the key.
        """
        try:
            match key:
                case str():
                    return cls[key.upper()]

                case int():
                    return cls(key)

                case _:
                    return cls[default.upper()] if isinstance(default, str) else cls(default)
        except (KeyError, ValueError):
            return cls[default.upper()] if isinstance(default, str) else cls(default)
