from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, overload

if TYPE_CHECKING:
    from types import TracebackType

    from archivefile._enums import CompressionType
    from archivefile._models import ArchiveMember
    from archivefile._types import (
        CollectionOf,
        CompressionLevel,
        ErrorHandler,
        OpenArchiveMode,
        SortBy,
        StrPath,
        TableStyle,
        TreeStyle,
    )
    from typing_extensions import Generator, Self


class BaseArchiveAdapter(Protocol):
    @overload
    def __init__(
        self,
        file: StrPath,
        mode: OpenArchiveMode = "r",
        *,
        password: str | None = None,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
        **kwargs: Any,
    ) -> None: ...

    @overload
    def __init__(
        self,
        file: StrPath,
        mode: str = "r",
        *,
        password: str | None = None,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
        **kwargs: Any,
    ) -> None: ...

    def __init__(
        self,
        file: StrPath,
        mode: OpenArchiveMode | str = "r",
        *,
        password: str | None = None,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
        **kwargs: Any,
    ) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None: ...

    @property
    def file(self) -> Path: ...

    @property
    def mode(self) -> OpenArchiveMode: ...

    @property
    def password(self) -> str | None: ...

    def get_member(self, member: StrPath) -> ArchiveMember: ...

    def get_members(self) -> Generator[ArchiveMember]: ...

    def get_names(self) -> tuple[str, ...]: ...

    def print_tree(
        self,
        *,
        max_depth: int = 0,
        style: TreeStyle = "const",
    ) -> None: ...

    def print_table(
        self,
        *,
        title: str | None = None,
        style: TableStyle = "markdown",
        sort_by: SortBy = "name",
        descending: bool = False,
        **kwargs: Any,
    ) -> None: ...

    def extract(self, member: StrPath | ArchiveMember, *, destination: StrPath = Path.cwd()) -> Path: ...

    def extractall(
        self, *, destination: StrPath = Path.cwd(), members: CollectionOf[StrPath | ArchiveMember] | None = None
    ) -> Path: ...

    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes: ...

    def read_text(
        self,
        member: StrPath | ArchiveMember,
        *,
        encoding: str = "utf-8",
        errors: ErrorHandler = "strict",
    ) -> str: ...

    def write(
        self,
        file: StrPath,
        *,
        arcname: StrPath | None = None,
    ) -> None: ...

    def write_text(
        self,
        data: str,
        *,
        arcname: StrPath,
    ) -> None: ...

    def write_bytes(
        self,
        data: bytes,
        *,
        arcname: StrPath,
    ) -> None: ...

    def writeall(
        self,
        dir: StrPath,
        *,
        root: StrPath | None = None,
        glob: str = "*",
        recursive: bool = True,
    ) -> None: ...

    def close(self) -> None: ...

    def __repr__(self) -> str:
        password = '"********"' if self.password else None
        return f'{self.__class__.__name__}("{self.file}", "{self.mode}", password={password})'
