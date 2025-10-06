from __future__ import annotations

import os
from typing import TYPE_CHECKING, Literal, TypeAlias

if TYPE_CHECKING:
    from ._models import ArchiveMember

StrPath: TypeAlias = str | os.PathLike[str]
MemberLike: TypeAlias = "StrPath | ArchiveMember"
ErrorHandler: TypeAlias = Literal[
    "strict", "ignore", "replace", "backslashreplace", "surrogateescape", "xmlcharrefreplace", "namereplace"
]
