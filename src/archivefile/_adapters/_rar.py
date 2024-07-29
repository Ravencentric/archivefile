from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload

from archivefile._adapters._base import BaseArchiveAdapter
from archivefile._models import ArchiveMember
from archivefile._utils import get_member_name, realpath
from rarfile import NoRarEntry, RarFile

if TYPE_CHECKING:
    from types import TracebackType

    from archivefile._enums import CompressionType
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
    from rarfile import RarInfo
    from typing_extensions import Generator, Self


class RarFileAdapter(BaseArchiveAdapter):
    # fmt: off
    @overload
    def __init__(self, file: StrPath, mode: OpenArchiveMode = "r", *, password: str | None = None, compression_type: CompressionType | None = None, compression_level: CompressionLevel | None = None, **kwargs: Any) -> None: ...

    @overload
    def __init__(self, file: StrPath, mode: OpenArchiveMode = "r", *, password: str | None = None, compression_type: CompressionType | None = None, compression_level: int | None = None, **kwargs: Any) -> None: ...

    @overload
    def __init__(self, file: StrPath, mode: str = "r", *, password: str | None = None, compression_type: CompressionType | None = None, compression_level: CompressionLevel | None = None, **kwargs: Any) -> None: ...

    @overload
    def __init__(self, file: StrPath, mode: str = "r", *, password: str | None = None, compression_type: CompressionType | None = None, compression_level: int | None = None, **kwargs: Any) -> None: ...
    # fmt: on

    def __init__(
        self,
        file: StrPath,
        mode: OpenArchiveMode | str = "r",
        *,
        password: str | None = None,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | int | None = None,
        **kwargs: Any,
    ) -> None:
        self._file = realpath(file)
        self._mode = mode[0]
        self._password = password

        if self._mode == "r":
            self._rarfile = RarFile(self._file, mode=self._mode, **kwargs)
        else:
            raise NotImplementedError('Cannot write to a rar file. Rar files only support mode="r"!')

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self._rarfile.close()

    @property
    def file(self) -> Path:
        return self._file

    @property
    def mode(self) -> OpenArchiveMode:
        return self._mode  # type: ignore

    @property
    def password(self) -> str | None:
        return self._password

    @property
    def compression_type(self) -> CompressionType | None:
        # RarFile doesn't support writing, so this will always be None
        return None

    @property
    def compression_level(self) -> CompressionLevel | None:
        # RarFile doesn't support writing, so this will always be None
        return None

    @property
    def adapter(self) -> str:
        return self.__class__.__name__

    def get_member(self, member: StrPath) -> ArchiveMember:
        name = get_member_name(member)

        try:
            # ZipFile and TarFile raise KeyError but RarFile raises it's own NoRarEntry
            # So for consistency's sake, we'll also raise KeyError here
            rarinfo: RarInfo = self._rarfile.getinfo(name)
        except NoRarEntry:
            raise KeyError(f"{name} not found in {self._file}")

        is_dir = True if rarinfo.filename.endswith("/") else False
        return ArchiveMember(
            name=rarinfo.filename,
            size=rarinfo.file_size,
            compressed_size=rarinfo.compress_size,
            datetime=datetime(*rarinfo.date_time),
            checksum=rarinfo.CRC,
            is_dir=is_dir,
            is_file=not is_dir,
        )

    def get_members(self) -> Generator[ArchiveMember]:
        return (
            ArchiveMember(
                name=rarinfo.filename,
                size=rarinfo.file_size,
                compressed_size=rarinfo.compress_size,
                datetime=datetime(*rarinfo.date_time),
                checksum=rarinfo.CRC,
                is_dir=True if rarinfo.filename.endswith("/") else False,
                is_file=False if rarinfo.filename.endswith("/") else True,
            )
            for rarinfo in self._rarfile.infolist()
        )

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._rarfile.namelist())

    def print_tree(
        self,
        *,
        max_depth: int = 0,
        style: TreeStyle = "const",
    ) -> None:
        try:
            from bigtree.tree.construct import list_to_tree
        except ModuleNotFoundError:
            raise ModuleNotFoundError("The 'print_tree()' method requires the 'bigtree' dependency.")

        paths = [f"{self.file.name}/{member}" for member in self.get_names()]
        tree = list_to_tree(paths)  # type: ignore
        tree.show(max_depth=max_depth, style=style)

    def print_table(
        self,
        *,
        title: str | None = None,
        style: TableStyle = "markdown",
        sort_by: SortBy = "name",
        descending: bool = False,
        **kwargs: Any,
    ) -> None:
        try:
            from rich import box as RichBox
            from rich import print as richprint
            from rich.table import Table as RichTable
        except ModuleNotFoundError:
            raise ModuleNotFoundError("The 'print_table()' method requires the 'rich' dependency.")

        if title is None:
            title = self.file.name

        members = self.get_members()
        table = RichTable(title=title, box=getattr(RichBox, style.upper()), **kwargs)
        table.add_column("Name", no_wrap=True)
        table.add_column("Date modified", no_wrap=True)
        table.add_column("Type", no_wrap=True)
        table.add_column("Size", no_wrap=True)
        table.add_column("Compressed Size", no_wrap=True)
        for member in sorted(members, key=lambda member: getattr(member, sort_by), reverse=descending):
            table.add_row(
                member.name,
                member.datetime.isoformat(),
                "File" if member.is_file else "Folder",
                member.size.human_readable(),
                member.compressed_size.human_readable(),
            )
        richprint(table)

    def extract(self, member: StrPath | ArchiveMember, *, destination: StrPath = Path.cwd()) -> Path:
        destination = realpath(destination)
        destination.mkdir(parents=True, exist_ok=True)

        name = get_member_name(member)

        try:
            # ZipFile and TarFile raise KeyError but RarFile raises it's own NoRarEntry
            # So for consistency's sake, we'll also raise KeyError here
            self._rarfile.extract(member=name, path=destination, pwd=self._password)
        except NoRarEntry:
            raise KeyError(f"{name} not found in {self._file}")

        return destination / name

    def extractall(
        self, *, destination: StrPath = Path.cwd(), members: CollectionOf[StrPath | ArchiveMember] | None = None
    ) -> Path:
        destination = realpath(destination)
        destination.mkdir(parents=True, exist_ok=True)

        names: set[str] = set()
        if members:
            all_members = self._rarfile.namelist()
            for member in members:
                name = get_member_name(member)
                if name in all_members:
                    names.add(name)
                else:
                    raise KeyError(f"{name} not found in {self._file}")

        self._rarfile.extractall(path=destination, members=names, pwd=self._password)
        return destination

    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes:
        name = get_member_name(member)

        if name.endswith("/"):
            return b""

        try:
            # ZipFile and TarFile raise KeyError but RarFile raises it's own NoRarEntry
            # So for consistency's sake, we'll also raise KeyError here
            return self._rarfile.read(name, pwd=self._password)
        except NoRarEntry:
            raise KeyError(f"{name} not found in {self._file}")

    def read_text(
        self,
        member: StrPath | ArchiveMember,
        *,
        encoding: str = "utf-8",
        errors: ErrorHandler = "strict",
    ) -> str:
        return self.read_bytes(member).decode(encoding, errors)

    def write(
        self,
        file: StrPath,
        *,
        arcname: StrPath | None = None,
    ) -> None:
        raise NotImplementedError('Cannot write to a rar file. Rar files only support mode="r"!')

    def write_text(
        self,
        data: str,
        *,
        arcname: StrPath,
    ) -> None:
        raise NotImplementedError('Cannot write to a rar file. Rar files only support mode="r"!')

    def write_bytes(
        self,
        data: bytes,
        *,
        arcname: StrPath,
    ) -> None:
        raise NotImplementedError('Cannot write to a rar file. Rar files only support mode="r"!')

    def writeall(
        self,
        dir: StrPath,
        *,
        root: StrPath | None = None,
        glob: str = "*",
        recursive: bool = True,
    ) -> None:
        raise NotImplementedError('Cannot write to a rar file. Rar files only support mode="r"!')

    def close(self) -> None:
        self._rarfile.close()

    def __repr__(self) -> str:
        password = '"********"' if self.password else None
        return f'{self.__class__.__name__}("{self.file}", "{self.mode}", password={password})'
