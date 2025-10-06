from __future__ import annotations

import abc
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from .._models import ArchiveMember
    from .._types import ErrorHandler, MemberLike, StrPath


class AbstractArchiveFile(abc.ABC):
    def __init__(self, file: StrPath, /, *, password: str | None = None) -> None:
        self._file = Path(file)
        self._password = password
        super().__init__()

    @property
    def file(self) -> Path:
        return self._file

    @property
    def password(self) -> str | None:
        return self._password

    @abc.abstractmethod
    def get_member(self, member: MemberLike, /) -> ArchiveMember: ...

    @abc.abstractmethod
    def get_members(self) -> Iterator[ArchiveMember]: ...

    @abc.abstractmethod
    def get_names(self) -> tuple[str, ...]: ...

    @abc.abstractmethod
    def extract(self, member: MemberLike, /, *, destination: StrPath | None = None) -> Path: ...

    @abc.abstractmethod
    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[MemberLike] | None = None,
    ) -> Path: ...

    @abc.abstractmethod
    def read_bytes(self, member: MemberLike, /) -> bytes: ...

    def read_text(
        self,
        member: MemberLike,
        /,
        *,
        encoding: str = "utf-8",
        errors: ErrorHandler = "strict",
    ) -> str:
        return self.read_bytes(member).decode(encoding=encoding, errors=errors)

    @abc.abstractmethod
    def close(self) -> None: ...

    def __repr__(self) -> str:  # pragma: no cover
        file = self.file.as_posix()
        cls = self.__class__.__name__
        if self.password:
            return f"{cls}({file!r}, password='********')"
        return f"{cls}({file!r})"
