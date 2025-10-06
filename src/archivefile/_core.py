from __future__ import annotations

from tarfile import is_tarfile
from typing import TYPE_CHECKING
from zipfile import is_zipfile

from archivefile._utils import realpath

from ._errors import UnsupportedArchiveFormatError
from ._impl._rar import RarArchiveFile, is_rarfile
from ._impl._sevenzip import SevenZipArchiveFile, is_7zfile
from ._impl._tar import TarArchiveFile
from ._impl._zip import ZipArchiveFile

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path

    from typing_extensions import Self

    from ._impl._abc import AbstractArchiveFile
    from ._models import ArchiveMember
    from ._types import ErrorHandler, MemberLike, StrPath


def is_archive(file: StrPath) -> bool:
    """
    Check whether the given archive file is a supported archive or not.

    Parameters
    ----------
    file : StrPath
        Path to the archive file.

    Returns
    -------
    bool
        True if the archive is supported, False otherwise.

    """
    file = realpath(file)

    if not file.is_file():
        return False

    return is_tarfile(file) or is_zipfile(file) or is_7zfile(file) or is_rarfile(file)


class ArchiveFile:
    __slots__ = ("_impl",)

    def __init__(self, file: StrPath, /, *, password: str | None = None) -> None:
        """
        Open an archive file.

        Parameters
        ----------
        file : StrPath
            Path to the archive file.
        password : str, optional
            Password for encrypted archive files.

        Raises
        ------
        UnsupportedArchiveFormatError
            Raised if the archive format is unsupported

        Notes
        -----
        ArchiveFile currently supports the following:

        - [`ZipFile`][zipfile.ZipFile]
        - [`TarFile`][tarfile.TarFile.open]
        - [`RarFile`][rarfile.RarFile] - requires `archivefile[rar]`
        - [`SevenZipFile`][py7zr.SevenZipFile] - requires `archivefile[7z]`

        """
        file = realpath(file)
        if not file.is_file():
            raise FileNotFoundError(file)

        implmentation: type[AbstractArchiveFile]

        if is_zipfile(file):
            implmentation = ZipArchiveFile
        elif is_tarfile(file):
            implmentation = TarArchiveFile
        elif is_7zfile(file):
            implmentation = SevenZipArchiveFile
        elif is_rarfile(file):
            implmentation = RarArchiveFile
        else:
            raise UnsupportedArchiveFormatError(file=file)

        self._impl = implmentation(file, password=password)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @property
    def file(self) -> Path:
        """Path to the archive file."""
        return self._impl.file

    @property
    def password(self) -> str | None:
        """Archive password."""
        return self._impl.password

    def get_member(self, member: MemberLike, /) -> ArchiveMember:
        """
        Retrieve an ArchiveMember object by it's name.

        Parameters
        ----------
        member : MemberLike
            Name of the member.

        Returns
        -------
        ArchiveMember
            Represents a member of the archive.

        Raises
        ------
        KeyError
            Raised if the member is not found in the archive.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar") as archive:
            archive.get_member("README.md")
            # ArchiveMember(
            #     name="README.md",
            #     size=3799,
            #     compressed_size=3799,
            #     datetime=datetime.datetime(2024, 4, 10, 20, 10, 57),
            #     is_dir=False,
            #     is_file=True,
            # )
        ```

        """
        return self._impl.get_member(member)

    def get_members(self) -> Iterator[ArchiveMember]:
        """
        Retrieve all members of the archive as a generator of `ArchiveMember` objects.

        Yields
        ------
        ArchiveMember
            Each member of the archive as an `ArchiveMember` object.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar") as archive:
            for member in archive.get_members():
                print(member.name)
                # project/pyproject.toml
                # project/src
        ```

        """
        yield from self._impl.get_members()

    def get_names(self) -> tuple[str, ...]:
        """
        Retrieve all members of the archive as a tuple of strings.

        Returns
        -------
        tuple[str, ...]
            Members of the archive as a tuple of strings.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar") as archive:
            archive.get_names()
            # (
            #     "project/pyproject.toml",
            #     "project/src",
            # )
        ```

        """
        return self._impl.get_names()

    def extract(self, member: MemberLike, /, *, destination: StrPath | None = None) -> Path:
        """
        Extract a member of the archive.

        Parameters
        ----------
        member : MemberLike
            Name of the member or an ArchiveMember object.
        destination : StrPath
            The path to the directory where the member will be extracted.
            If not specified, the current working directory is used as the default destination.

        Returns
        -------
        Path
            The path to the extracted file.

        Raises
        ------
        KeyError
            Raised if the member is not found in the archive.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            file = archive.extract("hello-world/pyproject.toml")
            print(file.read_text())
            # [tool.poetry]
            # name = "hello-world"
            # version = "0.1.0"
            # description = ""
            # readme = "README.md"
            # packages = [{include = "hello_world", from = "src"}]
        ```

        """
        return self._impl.extract(member, destination=destination)

    def extractall(
        self,
        *,
        destination: StrPath | None = None,
        members: Iterable[MemberLike] | None = None,
    ) -> Path:
        """
        Extract all the members of the archive to the destination directory.

        Parameters
        ----------
        destination : StrPath
            The path to the directory where the members will be extracted.
            If not specified, the current working directory is used as the default destination.
        members : CollectionOf[MemberLike], optional
            Collection of member names or ArchiveMember objects to extract.
            Default is `None` which will extract all members.

        Returns
        -------
        Path
            The path to the destination directory.

        Raises
        ------
        KeyError
            Raised if any member in members was not found in the archive.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            outdir = archive.extractall()

        for file in outdir.rglob("*"):
            print(file)
            # /source/hello-world
            # /source/hello-world/pyproject.toml
            # /source/hello-world/README.md
            # /source/hello-world/src
            # /source/hello-world/tests
            # /source/hello-world/src/hello_world
            # /source/hello-world/src/hello_world/__init__.py
            # /source/hello-world/tests/__init__.py
        ```

        """
        return self._impl.extractall(destination=destination, members=members)

    def read_bytes(self, member: MemberLike, /) -> bytes:
        """
        Read the member in bytes mode.

        Parameters
        ----------
        member : MemberLike
            Name of the member or an ArchiveMember object.

        Returns
        -------
        bytes
            The contents of the file as bytes.

        Raises
        ------
        KeyError
            Raised if the member is not found in the archive.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            data = archive.read_bytes("hello-world/pyproject.toml")
            print(data)
            # b'[tool.poetry]\\r\\nname = "hello-world"\\r\\nversion = "0.1.0" [...]'
        ```

        """
        return self._impl.read_bytes(member)

    def read_text(
        self,
        member: MemberLike,
        /,
        *,
        encoding: str = "utf-8",
        errors: ErrorHandler = "strict",
    ) -> str:
        """
        Read the member in text mode.

        Parameters
        ----------
        member : MemberLike
            Name of the member or an ArchiveMember object.
        encoding : str, optional
            Encoding used to read the file. Default is `utf-8`.
        errors : ErrorHandler, optional
            String that specifies how encoding and decoding errors are to be handled.

        Returns
        -------
        str
            The contents of the file as a string.

        Raises
        ------
        KeyError
            Raised if the member is not found in the archive.

        References
        ----------
        - [Standard Encodings](https://docs.python.org/3/library/codecs.html#standard-encodings)
        - [Error Handlers](https://docs.python.org/3/library/codecs.html#error-handlers)

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            text = archive.read_text("hello-world/pyproject.toml")
            print(text)
            # [tool.poetry]
            # name = "hello-world"
            # version = "0.1.0"
            # description = ""
            # readme = "README.md"
            # packages = [{include = "hello_world", from = "src"}]
        ```

        """
        return self._impl.read_text(member, encoding=encoding, errors=errors)

    def close(self) -> None:
        """
        Close the archive file.

        Returns
        -------
        None

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        archive = ArchiveFile("skynet.zip", "w")
        archive.write_bytes(b"01010101001", arcname="terminator.py")
        archive.close()
        ```

        """
        self._impl.close()

    def __repr__(self) -> str:  # pragma: no cover
        file = self.file.as_posix()
        cls = self.__class__.__name__
        if self.password:
            return f"{cls}({file!r}, password='********')"
        return f"{cls}({file!r})"
