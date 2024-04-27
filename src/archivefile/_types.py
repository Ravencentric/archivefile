from __future__ import annotations

from pathlib import Path

from typing_extensions import Literal, TypeAlias

StrPath: TypeAlias = str | Path

OpenArchiveMode: TypeAlias = Literal[
    "r", "r:*", "r:", "r:gz", "r:bz2", "r:xz",
    "w", "w:", "w:gz", "w:bz2", "w:xz",
    "x", "x:", "x:", "x:gz", "x:bz2", "x:xz",
    "a", "a:",
]
