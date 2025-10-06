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

    from rarfile import RarInfo

    from .._types import MemberLike, StrPath


def is_rarfile(file: StrPath, /) -> bool:
    try:
        import rarfile

        return rarfile.is_rarfile(file) or rarfile.is_rarfile_sfx(file)  # type: ignore[no-any-return]
    except ModuleNotFoundError:
        return False


def _rarinfo_to_member(rarinfo: RarInfo, /) -> ArchiveMember:
    return ArchiveMember(
        name=rarinfo.filename,
        size=rarinfo.file_size,
        compressed_size=rarinfo.compress_size,
        is_dir=rarinfo.filename.endswith("/"),
        is_file=not rarinfo.filename.endswith("/"),
    )


class RarArchiveFile(AbstractArchiveFile):
    def __init__(self, file: StrPath, /, *, password: str | None = None) -> None:
        try:
            import rarfile
        except ModuleNotFoundError:  # pragma: no cover
            filename = Path(file).as_posix()
            msg = (
                f"Cannot open archive: {filename!r}\n"
                "RAR support requires the 'rarfile' package, which is not installed.\n"
                "To enable RAR support, install archivefile with the optional RAR dependencies: 'archivefile[rar]'"
            )
            raise ModuleNotFoundError(msg) from None

        super().__init__(file, password=password)
        self._RarFile = rarfile.RarFile
        self._NoRarEntry = rarfile.NoRarEntry
        self._rarfile = self._RarFile(self._file)

    def get_member(self, member: MemberLike, /) -> ArchiveMember:
        name = get_member_name(member)

        try:
            # ZipFile and TarFile raise KeyError but RarFile raises it's own NoRarEntry
            # So for consistency's sake, we'll also raise KeyError here
            rarinfo: RarInfo = self._rarfile.getinfo(name)
        except self._NoRarEntry:
            raise ArchiveMemberNotFoundError(member=name, file=self.file) from None

        return _rarinfo_to_member(rarinfo)

    def get_members(self) -> Iterator[ArchiveMember]:
        for rarinfo in self._rarfile.infolist():
            yield _rarinfo_to_member(rarinfo)

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._rarfile.namelist())

    def extract(self, member: MemberLike, /, *, destination: StrPath | None = None) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        name = get_member_name(member)

        try:
            # ZipFile and TarFile raise KeyError but RarFile raises it's own NoRarEntry
            # So for consistency's sake, we'll also raise KeyError here
            self._rarfile.extract(member=name, path=destination, pwd=self._password)
        except self._NoRarEntry:
            raise ArchiveMemberNotFoundError(member=name, file=self.file) from None

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
            names = validate_members(members, available=self._rarfile.namelist(), archive=self.file)
            self._rarfile.extractall(path=destination, members=names, pwd=self._password)
        else:
            self._rarfile.extractall(path=destination, pwd=self._password)

        return destination

    def read_bytes(self, member: MemberLike, /) -> bytes:
        name = get_member_name(member)

        try:
            data: bytes = self._rarfile.read(name, pwd=self._password)
        except self._NoRarEntry:
            # `name` simply does not exist in the archive.
            raise ArchiveMemberNotFoundError(member=name, file=self.file) from None
        except io.UnsupportedOperation:
            # `name` is NOT a file. So we cannot read it.
            raise ArchiveMemberNotAFileError(member=name, file=self.file) from None
        else:
            return data

    def close(self) -> None:
        self._rarfile.close()
