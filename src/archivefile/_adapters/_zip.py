from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload
from zipfile import ZipFile

from archivefile._adapters._base import BaseArchiveAdapter
from archivefile._enums import CompressionType
from archivefile._models import ArchiveMember
from archivefile._utils import get_member_name, realpath

if TYPE_CHECKING:
    from types import TracebackType

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


class ZipFileAdapter(BaseArchiveAdapter):
    @overload
    def __init__(
        self, file: StrPath, mode: OpenArchiveMode = "r", *, password: str | None = None, **kwargs: Any
    ) -> None: ...

    @overload
    def __init__(self, file: StrPath, mode: str = "r", *, password: str | None = None, **kwargs: Any) -> None: ...

    def __init__(
        self, file: StrPath, mode: OpenArchiveMode | str = "r", *, password: str | None = None, **kwargs: Any
    ) -> None:
        self._file = realpath(file)
        self._mode = mode[0]
        self._password = password
        self._pwd = password.encode() if password else None
        self._zipfile = ZipFile(self._file, mode=self._mode, **kwargs)  # type: ignore

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self._zipfile.close()

    @property
    def file(self) -> Path:
        return self._file

    @property
    def mode(self) -> OpenArchiveMode:
        return self._mode  # type: ignore

    @property
    def password(self) -> str | None:
        return self._password

    def get_member(self, member: StrPath) -> ArchiveMember:
        name = get_member_name(member)
        zipinfo = self._zipfile.getinfo(name)

        return ArchiveMember(
            name=zipinfo.filename,
            size=zipinfo.file_size,
            compressed_size=zipinfo.compress_size,
            datetime=datetime(*zipinfo.date_time),
            checksum=zipinfo.CRC,
            is_dir=zipinfo.is_dir(),
            is_file=not zipinfo.is_dir(),
        )

    def get_members(self) -> Generator[ArchiveMember]:
        return (
            ArchiveMember(
                name=zipinfo.filename,
                size=zipinfo.file_size,
                compressed_size=zipinfo.compress_size,
                datetime=datetime(*zipinfo.date_time),
                checksum=zipinfo.CRC,
                is_dir=zipinfo.is_dir(),
                is_file=not zipinfo.is_dir(),
            )
            for zipinfo in self._zipfile.filelist
        )

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._zipfile.namelist())

    def print_tree(
        self,
        *,
        max_depth: int = 0,
        style: TreeStyle = "const",
    ) -> None:
        try:
            from bigtree.tree.construct import list_to_tree
        except ModuleNotFoundError:  # pragma: no cover
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
        except ModuleNotFoundError:  # pragma: no cover
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
        self._zipfile.extract(member=name, path=destination, pwd=self._pwd)
        return destination / name

    def extractall(
        self, *, destination: StrPath = Path.cwd(), members: CollectionOf[StrPath | ArchiveMember] | None = None
    ) -> Path:
        destination = realpath(destination)
        destination.mkdir(parents=True, exist_ok=True)

        names: list[str] = []
        if members:
            for member in members:
                names.append(get_member_name(member))

        if names:
            self._zipfile.extractall(path=destination, members=names, pwd=self._pwd)
        else:
            self._zipfile.extractall(path=destination, pwd=self._pwd)

        return destination

    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes:
        name = get_member_name(member)
        return self._zipfile.read(name, pwd=self._pwd)  # type: ignore

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
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
    ) -> None:
        file = realpath(file)

        if arcname is None:
            arcname = file.name

        if not file.is_file():
            raise ValueError(f"The specified file '{file}' either does not exist or is not a regular file!")

        if compression_type == CompressionType.BZIP2:
            if compression_level == 0:
                compression_level = 1

        self._zipfile.write(file, arcname=arcname, compress_type=compression_type, compresslevel=compression_level)

    def write_text(
        self,
        data: str,
        *,
        arcname: StrPath,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
    ) -> None:
        self._zipfile.writestr(
            get_member_name(arcname), data, compress_type=compression_type, compresslevel=compression_level
        )

    def write_bytes(
        self,
        data: bytes,
        *,
        arcname: StrPath,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
    ) -> None:
        self._zipfile.writestr(
            get_member_name(arcname), data, compress_type=compression_type, compresslevel=compression_level
        )

    def writeall(
        self,
        dir: StrPath,
        *,
        root: StrPath | None = None,
        glob: str = "*",
        recursive: bool = True,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
    ) -> None:
        dir = realpath(dir)

        if not dir.is_dir():
            raise ValueError(f"The specified file '{dir}' either does not exist or is not a regular directory!")

        if root is None:
            root = dir.parent
        else:
            root = realpath(root)

        if not dir.is_relative_to(root):
            raise ValueError(f"{dir} must be relative to {root}")

        files = dir.rglob(glob) if recursive else dir.glob(glob)

        for file in files:
            arcname = file.relative_to(root)
            self.write(file, arcname=arcname, compression_type=compression_type, compression_level=compression_level)

    def close(self) -> None:
        self._zipfile.close()

    def __repr__(self) -> str:
        password = '"********"' if self.password else None
        return f'{self.__class__.__name__}("{self.file}", "{self.mode}", password={password})'