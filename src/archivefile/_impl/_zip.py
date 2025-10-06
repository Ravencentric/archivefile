from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from zipfile import ZipFile, ZipInfo

from .._errors import ArchiveMemberNotAFileError, ArchiveMemberNotFoundError
from .._models import ArchiveMember
from .._utils import get_member_name, realpath, validate_members
from ._abc import AbstractArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from .._types import MemberLike, StrPath


def _zipinfo_to_member(zipinfo: ZipInfo, /) -> ArchiveMember:
    return ArchiveMember(
        name=zipinfo.filename,
        size=zipinfo.file_size,
        compressed_size=zipinfo.compress_size,
        is_dir=zipinfo.is_dir(),
        is_file=not zipinfo.is_dir(),
    )


class ZipArchiveFile(AbstractArchiveFile):
    def __init__(self, file: StrPath, /, *, password: str | None = None) -> None:
        super().__init__(file, password=password)
        self._encoded_password = password.encode() if password else None
        self._zipfile = ZipFile(self.file)

    def get_member(self, member: MemberLike, /) -> ArchiveMember:
        name = get_member_name(member)
        try:
            zipinfo = self._zipfile.getinfo(name)
        except KeyError:
            raise ArchiveMemberNotFoundError(member=name, file=self.file) from None

        return _zipinfo_to_member(zipinfo)

    def get_members(self) -> Iterator[ArchiveMember]:
        for zipinfo in self._zipfile.filelist:
            yield _zipinfo_to_member(zipinfo)

    def get_names(self) -> tuple[str, ...]:
        return tuple(self._zipfile.namelist())

    def extract(self, member: MemberLike, /, *, destination: StrPath | None = None) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        name = get_member_name(member)
        try:
            self._zipfile.extract(member=name, path=destination, pwd=self._encoded_password)
        except KeyError:
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
            members = validate_members(members, available=self._zipfile.namelist(), archive=self.file)
            self._zipfile.extractall(path=destination, members=members)
        else:
            self._zipfile.extractall(path=destination)

        return destination

    def read_bytes(self, member: MemberLike, /) -> bytes:
        member = self.get_member(member)

        if member.is_dir:
            # `name` is NOT a file. So we cannot read it.
            raise ArchiveMemberNotAFileError(member=member.name, file=self.file) from None

        # At this point, `self.get_member(member)` ensures the member exists,
        # and the `if member.is_dir` check ensures it is a regular file.
        # Therefore, reading its contents here is safe.
        return self._zipfile.read(member.name, pwd=self._encoded_password)

    def close(self) -> None:
        self._zipfile.close()
