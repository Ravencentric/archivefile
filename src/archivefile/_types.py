from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import AfterValidator
from typing_extensions import Annotated, Literal, TypeAlias, Union


def to_utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc)


UTCDateTime = Annotated[datetime, AfterValidator(to_utc)]
"""Datetime that's always in UTC."""

StrPath: TypeAlias = Union[str, Path]

OpenArchiveMode: TypeAlias = Literal[
    "r",
    "r:*",
    "r:",
    "r:gz",
    "r:bz2",
    "r:xz",
    "w",
    "w:",
    "w:gz",
    "w:bz2",
    "w:xz",
    "x",
    "x:",
    "x:",
    "x:gz",
    "x:bz2",
    "x:xz",
    "a",
    "a:",
]

TreeStyle: TypeAlias = Literal["ansi", "ascii", "const", "const_bold", "rounded", "double"]

TableStyle: TypeAlias = Literal[
    "ascii",
    "ascii2",
    "ascii_double_head",
    "square",
    "square_double_head",
    "minimal",
    "minimal_heavy_head",
    "minimal_double_head",
    "simple",
    "simple_head",
    "simple_heavy",
    "horizontals",
    "rounded",
    "heavy",
    "heavy_edge",
    "heavy_head",
    "double",
    "double_edge",
    "markdown",
]

SortBy: TypeAlias = Literal["name", "datetime", "size", "compressed_size", "checksum"]

ErrorHandler: TypeAlias = Literal[
    "strict", "ignore", "replace", "backslashreplace", "surrogateescape", "xmlcharrefreplace", "namereplace"
]

CompressionLevel: TypeAlias = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
