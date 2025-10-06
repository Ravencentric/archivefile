from __future__ import annotations

import tarfile
from pathlib import Path
from typing import TYPE_CHECKING

from .._errors import ArchiveMemberNotAFileError, ArchiveMemberNotFoundError
from .._models import ArchiveMember
from .._utils import get_member_name, realpath, validate_members
from ._abc import AbstractArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from .._types import MemberLike, StrPath


def _tarinfo_to_member(tarinfo: tarfile.TarInfo, /) -> ArchiveMember:
    is_dir = tarinfo.isdir()
    name = tarinfo.name
    if is_dir and not name.endswith("/"):
        name += "/"

    return ArchiveMember(
        name=name,
        size=tarinfo.size,
        compressed_size=tarinfo.size,
        is_dir=is_dir,
        is_file=tarinfo.isfile(),
    )


class TarArchiveFile(AbstractArchiveFile):
    def __init__(self, file: StrPath, /, *, password: str | None = None) -> None:
        super().__init__(file, password=password)
        self._tarfile = tarfile.TarFile.open(self.file)
        # https://docs.python.org/3/library/tarfile.html#supporting-older-python-versions
        self._tarfile.extraction_filter = getattr(tarfile, "data_filter", (lambda member, path: member))

    def get_member(self, member: MemberLike, /) -> ArchiveMember:
        name = get_member_name(member)
        try:
            tarinfo = self._tarfile.getmember(name)
        except KeyError:
            raise ArchiveMemberNotFoundError(member=name, file=self.file) from None

        return _tarinfo_to_member(tarinfo)

    def get_members(self) -> Iterator[ArchiveMember]:
        for tarinfo in self._tarfile.getmembers():
            yield _tarinfo_to_member(tarinfo)

    def get_names(self) -> tuple[str, ...]:
        return tuple(member.name for member in self.get_members())

    def extract(self, member: MemberLike, /, *, destination: StrPath | None = None) -> Path:
        destination = realpath(destination) if destination else Path.cwd()
        destination.mkdir(parents=True, exist_ok=True)

        name = get_member_name(member)
        try:
            self._tarfile.extract(member=name, path=destination)
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
            members = validate_members(members, available=self._tarfile.getnames(), archive=self.file)
            self._tarfile.extractall(path=destination, members=members)  # type: ignore[arg-type]
        else:
            self._tarfile.extractall(path=destination)

        return destination

    def read_bytes(self, member: MemberLike, /) -> bytes:
        name = get_member_name(member)

        try:
            fileobj = self._tarfile.extractfile(name)
        except KeyError:
            # `name` simply does not exist in the archive.
            raise ArchiveMemberNotFoundError(member=name, file=self.file) from None

        if fileobj is None:
            # `name` is NOT a file. So we cannot read it.
            raise ArchiveMemberNotAFileError(member=name, file=self.file) from None

        return fileobj.read()

    def close(self) -> None:
        self._tarfile.close()
