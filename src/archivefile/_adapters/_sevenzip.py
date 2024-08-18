from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, overload

from archivefile._adapters._base import BaseArchiveAdapter
from archivefile._models import ArchiveMember
from archivefile._utils import get_member_name, realpath
from py7zr import SevenZipFile

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
    from typing_extensions import Generator, Self


class SevenZipFileAdapter(BaseArchiveAdapter):
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

        # Bit of a hack to support 'x' and 'a' modes properly
        if self._mode == "x":
            if self._file.exists():
                # SevenZipFile doesn't support mode='x'
                # open for exclusive creation, failing if the file already exists
                # see: https://github.com/miurahr/py7zr/issues/587
                raise FileExistsError(self._file)
            else:
                # 'x' and 'w' are equivalent if the file doesn't exist
                self._mode = "w"

        if self._mode == "a" and not self._file.exists():
            # SevenZipFile only supports mode='a' on existing files
            # Since 'a' is equivalent to 'w' in this case (i.e, when archive file doesn't already exist)
            # We can just set it to 'w'
            self._mode = "w"

        self._sevenzipfile = SevenZipFile(self._file, mode=self._mode, password=self._password, **kwargs)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self._sevenzipfile.close()  # type: ignore

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
        # SevenZipFile doesn't support this, so this will always be None.
        # Only ZipFile supports this
        return None

    @property
    def compression_level(self) -> CompressionLevel | None:
        # SevenZipFile doesn't support this, so this will always be None.
        # Only ZipFile supports this
        return None

    @property
    def adapter(self) -> str:
        return self.__class__.__name__

    def get_member(self, member: StrPath | ArchiveMember) -> ArchiveMember:
        # Unlike the rest, SevenZip member directories do not end with `/`, so we need to strip it out
        # i.e, `spam/eggs/` in a ZipFile is equivalent to `spam/eggs` in SevenZipFile
        name = get_member_name(member).removesuffix("/")

        # SevenZipFile doesn't have an equivalent for `get_member` like the rest, so we hand craft it instead
        # https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/recipes.html#first_true
        sevenzipinfo = next(filter(lambda mem: mem.filename == name, self._sevenzipfile.list()), None)

        # ZipFile and TarFile raise KeyError
        # So for consistency (and because I like KeyError over None), we'll also raise KeyError here
        if sevenzipinfo is None:
            raise KeyError(f"{name} not found in {self._file}")

        return ArchiveMember(
            name=sevenzipinfo.filename,
            size=sevenzipinfo.uncompressed,
            # Sometimes sevenzip can return 0 for compressed size when there's no compression
            # in that case we simply return the uncompressed size instead.
            compressed_size=sevenzipinfo.compressed or sevenzipinfo.uncompressed,
            datetime=sevenzipinfo.creationtime,
            checksum=sevenzipinfo.crc32,
            is_dir=sevenzipinfo.is_directory,
            is_file=not sevenzipinfo.is_directory,
        )

    def get_members(self) -> Generator[ArchiveMember]:
        for sevenzipinfo in self._sevenzipfile.list():
            yield ArchiveMember(
                name=sevenzipinfo.filename,
                size=sevenzipinfo.uncompressed,
                # Sometimes sevenzip can return 0 for compressed size when there's no compression
                # in that case we simply return the uncompressed size instead.
                compressed_size=sevenzipinfo.compressed or sevenzipinfo.uncompressed,
                datetime=sevenzipinfo.creationtime,
                checksum=sevenzipinfo.crc32,
                is_dir=sevenzipinfo.is_directory,
                is_file=not sevenzipinfo.is_directory,
            )

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._sevenzipfile.getnames())

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

        # Unlike the rest, SevenZip member directories do not end with `/`, so we need to strip it out
        # i.e, `spam/eggs/` in a ZipFile is equivalent to `spam/eggs` in SevenZipFile
        name = get_member_name(member).removesuffix("/")

        if name in self.get_names():
            self._sevenzipfile.extract(path=destination, targets=[name], recursive=True)
        else:
            # ZipFile and TarFile raise KeyError but SevenZipFile does nothing
            # So for consistency's sake, we'll also raise KeyError here
            raise KeyError(f"{name} not found in {self._file}")

        self._sevenzipfile.reset()
        return destination / name

    def extractall(
        self, *, destination: StrPath = Path.cwd(), members: CollectionOf[StrPath | ArchiveMember] | None = None
    ) -> Path:
        destination = realpath(destination)
        destination.mkdir(parents=True, exist_ok=True)

        names: set[str] = set()
        if members:
            all_members = self._sevenzipfile.getnames()
            for member in members:
                # Unlike the rest, SevenZip member directories do not end with `/`, so we need to strip it out
                # i.e, `spam/eggs/` in a ZipFile is equivalent to `spam/eggs` in SevenZipFile
                name = get_member_name(member).removesuffix("/")
                if name in all_members:
                    names.add(name)
                else:
                    raise KeyError(f"{name} not found in {self._file}")

        if names:
            self._sevenzipfile.extract(path=destination, targets=names, recursive=True)
        else:
            self._sevenzipfile.extractall(path=destination)

        self._sevenzipfile.reset()
        return destination

    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes:
        # Unlike the rest, SevenZip member directories do not end with `/`, so we need to strip it out
        # i.e, `spam/eggs/` in a ZipFile is equivalent to `spam/eggs` in SevenZipFile
        name = get_member_name(member).removesuffix("/")

        if name not in self._sevenzipfile.getnames():
            raise KeyError(f"{name} not found in {self._file}")

        data = self._sevenzipfile.read(targets=[name])
        self._sevenzipfile.reset()

        match data:
            case dict():
                if fileobj := data.get(name):
                    return fileobj.read()  # type: ignore
                else:
                    return b""
            case _:  # pragma: no cover
                # We need this because SevenZipFile.read is typed as `dict | None`
                # but this case will never actually happen.
                # I couldn't get SevenZipFile to return anything but a dict,
                # so I'm assuming it's some edge case.
                return b""

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
        file = realpath(file)

        match arcname:
            case None:
                arcname = file.name
            case Path():
                arcname = arcname.relative_to(arcname.anchor).as_posix()

        if not file.is_file():
            raise ValueError(f"The specified file '{file}' either does not exist or is not a regular file!")

        self._sevenzipfile.write(file, arcname=arcname)

    def write_text(
        self,
        data: str,
        *,
        arcname: StrPath,
    ) -> None:
        self._sevenzipfile.writestr(data=data, arcname=get_member_name(arcname))

    def write_bytes(
        self,
        data: bytes,
        *,
        arcname: StrPath,
    ) -> None:
        self._sevenzipfile.writestr(data=data, arcname=get_member_name(arcname))

    def writeall(
        self,
        dir: StrPath,
        *,
        root: StrPath | None = None,
        glob: str = "*",
        recursive: bool = True,
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
            self.write(file, arcname=arcname)

    def close(self) -> None:
        self._sevenzipfile.close()  # type: ignore

    def __repr__(self) -> str:
        password = '"********"' if self.password else None
        return f'{self.__class__.__name__}("{self.file}", "{self.mode}", password={password})'
