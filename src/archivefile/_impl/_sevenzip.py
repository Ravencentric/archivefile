from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

from .._errors import ArchiveMemberNotAFileError, ArchiveMemberNotFoundError
from .._models import ArchiveMember
from .._utils import get_member_name, realpath, validate_members
from ._abc import AbstractArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from py7zr import FileInfo
    from py7zr.io import Py7zIO, WriterFactory

    from .._types import MemberLike, StrPath
else:
    Py7zIO = object
    WriterFactory = object


def is_7zfile(file: StrPath, /) -> bool:
    try:
        import py7zr

        return py7zr.is_7zfile(file)  # type: ignore[arg-type]
    except ModuleNotFoundError:
        return False


class Py7zBytesIO(Py7zIO):
    def __init__(self, filename: str):
        self.filename = filename
        self._buffer = io.BytesIO()

    def write(self, s: bytes | bytearray) -> int:
        return self._buffer.write(s)

    def read(self, size: int | None = None) -> bytes:
        return self._buffer.read()

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._buffer.seek(offset, whence)

    def flush(self) -> None:  # pragma: no cover
        # Required by the abstract interface. Not used in this implementation.
        return self._buffer.flush()

    def size(self) -> int:  # pragma: no cover
        # Required by the abstract interface. Not used in this implementation.
        return self._buffer.getbuffer().nbytes


class BytesIOFactory(WriterFactory):
    def __init__(self) -> None:
        self.products: dict[str, Py7zBytesIO] = {}

    def create(self, filename: str) -> Py7zIO:
        product = Py7zBytesIO(filename)
        self.products[filename] = product
        return product

    def read(self, filename: str) -> bytes:
        return self.products[filename].read()


def _sevenzipinfo_to_member(sevenzipinfo: FileInfo, /) -> ArchiveMember:
    is_dir = sevenzipinfo.is_directory
    name = sevenzipinfo.filename

    if is_dir and not name.endswith("/"):
        name += "/"

    return ArchiveMember(
        name=name,
        size=sevenzipinfo.uncompressed,
        # Sometimes sevenzip can return 0 for compressed size when there's no compression.
        # In that case we simply return the uncompressed size instead.
        compressed_size=sevenzipinfo.compressed or sevenzipinfo.uncompressed,
        is_dir=is_dir,
        is_file=not is_dir,
    )


class SevenZipArchiveFile(AbstractArchiveFile):
    def __init__(self, file: StrPath, /, *, password: str | None = None) -> None:
        try:
            import py7zr
        except ModuleNotFoundError:  # pragma: no cover
            filename = Path(file).as_posix()
            msg = (
                f"Cannot open archive: {filename!r}\n"
                "7z support requires the 'py7zr' package, which is not installed.\n"
                "To enable 7z support, install archivefile with the optional 7z dependencies: 'archivefile[7z]'"
            )
            raise ModuleNotFoundError(msg) from None

        super().__init__(file, password=password)
        self._sevenzipfile = py7zr.SevenZipFile(self.file, password=self.password)

    def get_member(self, member: MemberLike, /) -> ArchiveMember:
        # TODO: Replace this implementation with SevenZipFile.getinfo
        # once py7zr releases a version that fixes this bug:
        # https://github.com/miurahr/py7zr/issues/675
        name = get_member_name(member).removesuffix("/")
        try:
            sevenzipinfo: FileInfo = next(member for member in self._sevenzipfile.list() if member.filename == name)
        except StopIteration:
            raise ArchiveMemberNotFoundError(member=name, file=self.file) from None

        return _sevenzipinfo_to_member(sevenzipinfo)

    def get_members(self) -> Iterator[ArchiveMember]:
        for sevenzipinfo in self._sevenzipfile.list():
            yield _sevenzipinfo_to_member(sevenzipinfo)

    def get_names(self) -> tuple[str, ...]:
        return tuple(member.name for member in self.get_members())

    def extract(self, member: MemberLike, /, *, destination: StrPath | None = None) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)
        name = get_member_name(member)

        if name in self._sevenzipfile.getnames():
            self._sevenzipfile.extract(path=destination, targets=[name], recursive=True)
        else:
            raise ArchiveMemberNotFoundError(member=name, file=self.file)

        self._sevenzipfile.reset()
        return destination / name

    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[MemberLike] | None = None,
    ) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        if members:
            names = validate_members(members, available=self._sevenzipfile.getnames(), archive=self.file)
            self._sevenzipfile.extract(path=destination, targets=names, recursive=True)
        else:
            self._sevenzipfile.extractall(path=destination)

        self._sevenzipfile.reset()
        return destination

    def read_bytes(self, member: MemberLike, /) -> bytes:
        name = get_member_name(member)

        # SevenZipFile listings do not preserve trailing `/`,
        # so we normalize the name for lookup while keeping
        # the original for clearer error messages.
        normname = name.removesuffix("/")

        if normname not in self._sevenzipfile.getnames():
            # `name` simply does not exist in the archive.
            raise ArchiveMemberNotFoundError(member=normname, file=self.file)

        factory = BytesIOFactory()
        self._sevenzipfile.extract(targets=[normname], factory=factory)
        self._sevenzipfile.reset()

        try:
            data = factory.read(normname)
        except KeyError:
            # `name` is NOT a file. So we cannot read it.
            raise ArchiveMemberNotAFileError(member=name, file=self.file) from None
        else:
            return data

    def close(self) -> None:
        self._sevenzipfile.close()  # type: ignore[no-untyped-call]
