from __future__ import annotations

import tarfile
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from tarfile import TarFile, is_tarfile
from tempfile import TemporaryDirectory
from types import TracebackType
from typing import Any
from zipfile import ZipFile, is_zipfile

from bigtree.tree.construct import list_to_tree
from py7zr import SevenZipFile, is_7zfile
from pydantic import validate_call
from rarfile import RarFile, RarInfo, is_rarfile
from typing_extensions import Literal, Self

from archivefile._enums import CommonExtensions, ZipCompression
from archivefile._exceptions import UnsupportedArchiveOperation
from archivefile._models import ArchiveMember
from archivefile._types import OpenArchiveMode, StrPath
from archivefile._utils import check_extension, filter_kwargs


class ArchiveFile:
    """The ArchiveFile Class provides a unified interface to zip, tar, rar, and 7zip archives."""

    @validate_call
    def __init__(
        self,
        file: StrPath,
        mode: OpenArchiveMode = "r",
        *,
        password: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Open an archive file.

        Parameters
        ----------
        file: StrPath
            Path to the archive file. This must be an existing file.
        mode: OpenArchiveMode, optional
            Specifies the mode for opening the archive file. Default is "r".
        password: str, optional
            Password for encrypted archive files. Default is None.
        kwargs: Any
            Keyword arugments to pass to the underlying ZipFile/TarFile/RarFile/SevenZipFile handler.
            Kwargs that are not relevent to the current handler will automatically
            be removed so you don't have to worry about accidentally passing ZipFile's kwargs to TarFile.
        """
        self._file = file.expanduser().resolve() if isinstance(file, Path) else Path(file).expanduser().resolve()
        self._mode = mode
        self._password = password
        self._kwargs = kwargs
        self._initialize_handler()

    def _initialize_handler(self) -> None:
        archive = self._file
        extensions = archive.suffixes
        kwargs = self._kwargs
        tarfile_mode = self._mode
        mode = self._mode[0]  # reduce stuff like `r:gz` or `w:gz` down to `r` and `w` for non tarfiles
        write = not mode.startswith("r")

        if not archive.exists():
            if write:
                if check_extension(extensions, CommonExtensions.TAR):
                    self._handler = tarfile.open(archive, mode=tarfile_mode, **filter_kwargs(TarFile, kwargs=kwargs))  # type: ignore
                    # https://docs.python.org/3/library/tarfile.html#supporting-older-python-versions
                    self._handler.extraction_filter = getattr(tarfile, "data_filter", (lambda member, path: member))

                elif check_extension(extensions, CommonExtensions.ZIP):
                    self._handler = ZipFile(archive, mode=mode, **filter_kwargs(ZipFile, kwargs=kwargs))  # type: ignore

                elif check_extension(extensions, CommonExtensions.SEVENZIP):
                    # SevenZip doesn't support mode='x' at all and only supports mode='a' on existing files
                    # Since 'x' and 'a' are equivalent to 'w' in this case (i.e, when archive file doesn't already exist)
                    # We can just set it to 'w'
                    self._handler = SevenZipFile(
                        archive, mode="w", password=self._password, **filter_kwargs(SevenZipFile, kwargs=kwargs)
                    )  # type: ignore

                elif check_extension(extensions, CommonExtensions.RAR):
                    raise UnsupportedArchiveOperation('Cannot write a rar file. Rar files only support mode="r"!')
                else:
                    raise UnsupportedArchiveOperation(f"Unsupported archive format: {archive.suffix}")
            else:
                raise FileNotFoundError(archive)

        elif is_tarfile(archive):
            self._handler = tarfile.open(archive, mode=tarfile_mode, **filter_kwargs(TarFile, kwargs=kwargs))  # type: ignore

        elif is_zipfile(archive):
            self._handler = ZipFile(archive, mode=mode, **filter_kwargs(ZipFile, kwargs=kwargs))  # type: ignore

        elif is_7zfile(archive):
            if mode == "x":
                raise FileExistsError(archive)

            self._handler = SevenZipFile(
                archive, mode=mode, password=self._password, **filter_kwargs(SevenZipFile, kwargs=kwargs)
            )  # type: ignore

        elif is_rarfile(archive):
            if mode != "r":
                raise UnsupportedArchiveOperation('RarFiles only support mode="r"!')
            self._handler = RarFile(archive, mode="r", **filter_kwargs(RarFile, kwargs=kwargs))

        else:
            raise UnsupportedArchiveOperation(f"Unsupported archive format: {archive.suffix}")

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self._handler.close()

    @property
    def file(self) -> Path:
        """Path to the archive file"""
        return self._file

    @property
    def mode(self) -> OpenArchiveMode:
        """Mode in which the archive file was opened"""
        return self._mode

    @property
    def password(self) -> str | None:
        """Archive password"""
        return self._password

    @property
    def handler(self) -> str:
        """Name of the handler used"""
        return self._handler.__class__.__name__

    @validate_call
    def get_member(self, member: StrPath) -> ArchiveMember:  # type: ignore
        """
        Get the ArchiveMember object for the member by it's name.

        Parameters
        ----------
        member: StrPath
            Name or path of the member as present in the archive.

        Returns
        -------
        ArchiveMember
            Represents a member of the archive.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar") as archive:
            archive.get_member("README.md")
            # ArchiveMember(name='README.md', size=3799, compressed_size=3799, datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc), checksum=5251, is_dir=False, is_file=True)
        ```
        """

        member = member.as_posix() if isinstance(member, Path) else member

        if isinstance(self._handler, TarFile):
            tarinfo = self._handler.getmember(member)
            return ArchiveMember(
                name=tarinfo.name,
                size=tarinfo.size,  # type: ignore
                compressed_size=tarinfo.size,  # type: ignore
                datetime=tarinfo.mtime,  # type: ignore
                checksum=tarinfo.chksum,
                is_dir=tarinfo.isdir(),
                is_file=tarinfo.isfile(),
            )

        elif isinstance(self._handler, ZipFile):
            zipinfo = self._handler.getinfo(member)
            return ArchiveMember(
                name=zipinfo.filename,
                size=zipinfo.file_size,  # type: ignore
                compressed_size=zipinfo.compress_size,  # type: ignore
                datetime=datetime(*zipinfo.date_time),
                checksum=zipinfo.CRC,
                is_dir=zipinfo.is_dir(),
                is_file=not zipinfo.is_dir(),
            )

        elif isinstance(self._handler, SevenZipFile):
            member_list = self._handler.list()
            # Unlike the rest, SevenZip member directories do not end with `/`, so we need to strip it out
            sevenzipinfo = [fileinfo for fileinfo in member_list if fileinfo.filename == member.removesuffix("/")][0]
            return ArchiveMember(
                name=sevenzipinfo.filename,
                size=sevenzipinfo.uncompressed,  # type: ignore
                # Sometimes sevenzip can return 0 for compressed size when there's no compression
                # in that case we simply return the uncompressed size instead.
                compressed_size=sevenzipinfo.compressed or sevenzipinfo.uncompressed,  # type: ignore
                datetime=sevenzipinfo.creationtime,  # type: ignore
                checksum=sevenzipinfo.crc32,
                is_dir=sevenzipinfo.is_directory,
                is_file=not sevenzipinfo.is_directory,
            )

        else:
            rarinfo: RarInfo = self._handler.getinfo(member)
            is_dir = True if rarinfo.filename.endswith("/") else False
            return ArchiveMember(
                name=rarinfo.filename,
                size=rarinfo.file_size,  # type: ignore
                compressed_size=rarinfo.compress_size,  # type: ignore
                datetime=datetime(*rarinfo.date_time),
                checksum=rarinfo.CRC,
                is_dir=is_dir,
                is_file=not is_dir,
            )

    @validate_call
    def get_members(self) -> tuple[ArchiveMember, ...]:
        """
        Retrieve all members from the archive as a tuple of ArchiveMember objects.

        Returns
        -------
        tuple[ArchiveMember, ...]
            Members of the archive as a tuple of ArchiveMember objects.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar") as archive:
            archive.get_members()
            # (
            #     ArchiveMember(name="project/pyproject.toml", size=1920, compressed_size=1920, datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc), checksum=6038, is_dir=False, is_file=True),
            #     ArchiveMember(name="project/src", size=0, compressed_size=0, datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc), checksum=4927, is_dir=True, is_file=False),
            # )
        ```
        """
        if isinstance(self._handler, TarFile):
            names = self._handler.getnames()
            return tuple([self.get_member(name) for name in names])

        elif isinstance(self._handler, ZipFile):
            names = self._handler.namelist()
            return tuple([self.get_member(name) for name in names])

        elif isinstance(self._handler, SevenZipFile):
            names = self._handler.getnames()
            return tuple([self.get_member(name) for name in names])

        else:
            names = self._handler.namelist()
            return tuple([self.get_member(name) for name in names])

    @validate_call
    def get_names(self) -> tuple[str, ...]:
        """
        Retrieve names of all members in the archive as a tuple of strings.

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
        if isinstance(self._handler, TarFile):
            return tuple(self._handler.getnames())

        elif isinstance(self._handler, ZipFile):
            return tuple(self._handler.namelist())

        elif isinstance(self._handler, SevenZipFile):
            return tuple(self._handler.getnames())

        else:
            return tuple(self._handler.namelist())

    def tree(
        self,
        max_depth: int = 0,
        style: Literal["ansi", "ascii", "const", "const_bold", "rounded", "double"] = "const",
    ) -> None:
        """
        Print the contents of the archive as a tree.

        Parameters
        ----------
        max_depth : int, optional
            Maximum depth to print.
        style : Literal["ansi", "ascii", "const", "const_bold", "rounded", "double"], optional
            The style of the tree

        Returns
        -------
        None

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar") as archive:
            archive.tree()
            # hello-world
            # ├── .github
            # │   └── workflows
            # │       ├── docs.yml
            # │       ├── release.yml
            # │       └── test.yml
            # ├── .gitignore
            # ├── docs
            # │   └── index.md
            # ├── pyproject.toml
            # ├── README.md
            # ├── src
            # │   └── hello-world
            # │       └── __init__.py
            # ├── tests
            # │   ├── test_hello_world.py
            # │   └── __init__.py
            # └── LICENSE
        ```
        """
        tree = list_to_tree(self.get_names())  # type: ignore
        tree.show(max_depth=max_depth, style=style)

    @validate_call
    def extract(self, member: StrPath | ArchiveMember, destination: StrPath = Path.cwd()) -> Path:
        """
        Extract a member from the archive.

        Parameters
        ----------
        member: StrPath, ArchiveMember
            Full name of the member to extract or an ArchiveMember object.
        destination: StrPath
            The path to the directory where the member will be extracted.
            If not specified, the current working directory is used as the default destination.

        Returns
        -------
        Path
            The path to the extracted file.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            file = archive.extract("hello-world/pyproject.toml")
            file.read_text()
            # [tool.poetry]
            # name = "hello-world"
            # version = "0.1.0"
            # description = ""
            # readme = "README.md"
            # packages = [{include = "hello_world", from = "src"}]
        ```
        """
        destination = destination if isinstance(destination, Path) else Path(destination)
        destination = destination.expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)

        if isinstance(member, ArchiveMember):
            member = member.name

        if isinstance(member, Path):
            # Do not expand/resolve member if the input is a path
            # since that can change the meaning of the name
            member = member.relative_to(member.anchor).as_posix()

        if isinstance(self._handler, TarFile):
            self._handler.extract(member=member, path=destination)
            return destination / member

        elif isinstance(self._handler, ZipFile):
            self._handler.extract(
                member=member, path=destination, pwd=self._password.encode() if self._password else None
            )
            return destination / member

        elif isinstance(self._handler, SevenZipFile):
            self._handler.extract(path=destination, targets=[member])
            return destination / member

        else:
            self._handler.extract(member=member, path=destination, pwd=self._password)
            return destination / member

    @validate_call
    def extractall(
        self, destination: StrPath = Path.cwd(), members: Iterable[StrPath | ArchiveMember] | None = None
    ) -> Path:
        """
        Extract all members of the archive to destination directory.

        Parameters
        ----------
        destination: StrPath
            The path to the directory where the members will be extracted to.
            If not specified, the current working directory is used as the default destination.
        members: Iterable[StrPath | ArchiveMember], optional
            Iterable of member names or ArchiveMember objects to extract.
            Default is None which will extract all members.

        Returns
        -------
        Path
            The path to the destination directory.

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
        destination = destination if isinstance(destination, Path) else Path(destination)
        destination = destination.expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)

        members = (
            [
                member.relative_to(member.anchor).as_posix()
                if isinstance(member, Path)
                else member.name
                if isinstance(member, ArchiveMember)
                else member
                for member in members
            ]
            if members
            else None
        )

        if isinstance(self._handler, TarFile):
            self._handler.extractall(path=destination, members=members)  # type: ignore
            return destination

        elif isinstance(self._handler, ZipFile):
            self._handler.extractall(
                path=destination, members=members, pwd=self._password.encode() if self._password else None
            )
            return destination

        elif isinstance(self._handler, SevenZipFile):
            # SevenZipFile doesn't have a members=[...] parameter like the rest
            if members:
                self._handler.extract(path=destination, targets=members)
            else:
                self._handler.extractall(path=destination)
            return destination

        else:
            self._handler.extractall(path=destination, members=members, pwd=self._password)
            return destination

    @validate_call
    def read_text(
        self,
        member: StrPath | ArchiveMember,
        encoding: str | None = "utf-8",
        errors: Literal[
            "strict", "ignore", "replace", "backslashreplace", "surrogateescape", "xmlcharrefreplace", "namereplace"
        ]
        | None = None,
    ) -> str:
        """
        Open the member in text mode, read it, and close the file.

        Parameters
        ----------
        member: StrPath, ArchiveMember
            Name or path of the member as present in the archive or an ArchiveMember object.
        encoding: str, optional
            Encoding used to read the file. Default is `utf-8`.
            Setting it to None will use platform-dependent encoding.
        errors: Literal["strict", "ignore", "replace", "backslashreplace", "surrogateescape", "xmlcharrefreplace", "namereplace"], optional
            String that specifies how encoding and decoding errors are to be handled.

        Returns
        -------
        str
            The contents of the file as a string.

        References
        ----------
        - [Standard Encodings](https://docs.python.org/3/library/codecs.html#standard-encodings)
        - [Error Handlers](https://docs.python.org/3/library/codecs.html#error-handlers)

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            archive.read_text("hello-world/pyproject.toml")
            # [tool.poetry]
            # name = "hello-world"
            # version = "0.1.0"
            # description = ""
            # readme = "README.md"
            # packages = [{include = "hello_world", from = "src"}]
        ```
        """
        tmpdir = TemporaryDirectory()
        data = self.extract(member, destination=tmpdir.name).read_text(encoding=encoding, errors=errors)

        try:
            tmpdir.cleanup()
        except:  # noqa: E722; # pragma: no cover
            pass

        return data

    @validate_call
    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes:
        """
        Open the member in bytes mode, read it, and close the file.

        Parameters
        ----------
        member: StrPath, ArchiveMember
            Name or path of the member as present in the archive or an ArchiveMember object.

        Returns
        -------
        bytes
            The contents of the file as bytes.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            archive.read_bytes("hello-world/pyproject.toml")
            # b'[tool.poetry]\\r\\nname = "hello-world"\\r\\nversion = "0.1.0"\\r\\ndescription = ""\\r\\nreadme = "README.md"\\r\\npackages = [{include = "hello_world", from = "src"}]\\r\\n'
        ```
        """
        tmpdir = TemporaryDirectory()
        data = self.extract(member, destination=tmpdir.name).read_bytes()

        try:
            tmpdir.cleanup()
        except:  # noqa: E722; # pragma: no cover
            pass

        return data

    @validate_call
    def write(
        self,
        file: StrPath,
        arcname: StrPath | None = None,
        compression_type: ZipCompression | None = None,
        compression_level: int | None = None,
    ) -> None:
        """
        Write a single file to the archive.

        Parameters
        ----------
        file : StrPath
            The path of the file to be added to the archive.
        arcname : StrPath, optional
            The name which the file will have in the archive.
            Default is the basename of the file.
        compression_type : ZipCompression, optional
            The compression method to be used. If None, the default compression
            method of the archive will be used.
            This ONLY applies to zip files and has no effect on other archives.
        compression_level : int, optional
            The compression level to be used. If None, the default compression
            level of the archive will be used.
            This ONLY applies to zip files and has no effect on other archives.

        Returns
        -------
        None

        Examples
        --------
        ```py
        from pathlib import Path

        from archivefile import ArchiveFile

        file = Path("hello.txt")
        file.write_text("world")

        with ArchiveFile("newarchive.zip", "w") as archive:
            archive.write(file)
            archive.get_names()
            # ('hello.txt',)
        ```
        """

        file = file if isinstance(file, Path) else Path(file)

        if arcname is None:
            arcname = file.name

        if not file.is_file():
            raise UnsupportedArchiveOperation(
                f"The specified file '{file}' either does not exist or is not a regular file!"
            )

        if isinstance(self._handler, TarFile):
            self._handler.add(file, arcname=arcname)

        elif isinstance(self._handler, ZipFile):
            self._handler.write(file, arcname=arcname, compress_type=compression_type, compresslevel=compression_level)

        elif isinstance(self._handler, SevenZipFile):
            arcname = arcname.as_posix() if isinstance(arcname, Path) else arcname
            self._handler.write(file, arcname=arcname)

        else:  # pragma: no cover
            # In reality, this can never happen since it'll exist in the constructor before ever reaching here
            raise UnsupportedArchiveOperation('Cannot write a rar file. Rar files only support mode="r"!')

    @validate_call
    def write_text(
        self,
        data: str,
        arcname: StrPath,
        encoding: str | None = "utf-8",
        errors: Literal[
            "strict", "ignore", "replace", "backslashreplace", "surrogateescape", "xmlcharrefreplace", "namereplace"
        ]
        | None = None,
        newline: Literal["", "\n", "\r", "\r\n"] | None = None,
        compression_type: ZipCompression | None = None,
        compression_level: int | None = None,
    ) -> None:
        """
        Write the string `data` to a file within the archive named `arcname`.

        Parameters
        ----------
        data: str
            The text data to write to the archive.
        arcname : StrPath, optional
            The name which the file will have in the archive.
        encoding: str, optional
            Encoding of the given data. Default is `utf-8`.
            Setting it to None will use platform-dependent encoding.
        errors: Literal["strict", "ignore", "replace", "backslashreplace", "surrogateescape", "xmlcharrefreplace", "namereplace"], optional
            String that specifies how encoding and decoding errors are to be handled.
        newline: Literal['', '\\n', '\\r', '\\r\\n'], optional
            If newline is None, any '\\n' characters written are translated to the system default line separator, `os.linesep`.
            If newline is '' or '\\n', no translation takes place.
            If newline is any of the other legal values, any '\\n' characters written are translated to the given string.
        compression_type : ZipCompression, optional
            The compression method to be used. If None, the default compression
            method of the archive will be used.
            This ONLY applies to zip files and has no effect on other archives.
        compression_level : int, optional
            The compression level to be used. If None, the default compression
            level of the archive will be used.
            This ONLY applies to zip files and has no effect on other archives.

        Returns
        -------
        None

        References
        ----------
        - [Encodings](https://docs.python.org/3/library/codecs.html#standard-encodings)
        - [Error Handlers](https://docs.python.org/3/library/codecs.html#error-handlers)
        - [newline](https://docs.python.org/3/library/functions.html#open)

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("newarchive.zip", "w") as archive:
            archive.write_text("hello world", arcname="textworld.txt")
            archive.get_names()
            # ('textworld.txt',)
            archive.read_text("textworld.txt")
            # 'hello world'
        ```
        """

        arcname = Path(arcname)
        tmpdir = TemporaryDirectory()
        tmppath = Path(tmpdir.name) / arcname.parent
        tmppath.mkdir(parents=True, exist_ok=True)
        tmpfile = tmppath / arcname.name
        tmpfile.touch(exist_ok=True)
        tmpfile.write_text(data=data, encoding=encoding, errors=errors, newline=newline)

        self.write(tmpfile, arcname=arcname, compression_type=compression_type, compression_level=compression_level)

        try:
            tmpdir.cleanup()
        except:  # noqa: E722; # pragma: no cover
            pass

    @validate_call
    def write_bytes(
        self,
        data: bytes,
        arcname: StrPath,
        compression_type: ZipCompression | None = None,
        compression_level: int | None = None,
    ) -> None:
        """
        Write the binary `data` to a file within the archive named `arcname`.

        Parameters
        ----------
        data: str
            The bytes data to write to the archive.
        arcname : StrPath, optional
            The name which the file will have in the archive.
        compression_type : ZipCompression, optional
            The compression method to be used. If None, the default compression
            method of the archive will be used.
            This ONLY applies to zip files and has no effect on other archives.
        compression_level : int, optional
            The compression level to be used. If None, the default compression
            level of the archive will be used.
            This ONLY applies to zip files and has no effect on other archives.

        Returns
        -------
        None

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("newarchive.zip", "w") as archive:
            archive.write_bytes(b"hello world", arcname="bytesworld.txt")
            archive.get_names()
            # ('bytesworld.txt',)
            archive.read_bytes("bytesworld.txt")
            # b'hello world'
        ```
        """

        arcname = Path(arcname)
        tmpdir = TemporaryDirectory()
        tmppath = Path(tmpdir.name) / arcname.parent
        tmppath.mkdir(parents=True, exist_ok=True)
        tmpfile = tmppath / arcname.name
        tmpfile.touch(exist_ok=True)
        tmpfile.write_bytes(data)

        self.write(tmpfile, arcname=arcname, compression_type=compression_type, compression_level=compression_level)

        try:
            tmpdir.cleanup()
        except:  # noqa: E722; # pragma: no cover
            pass

    @validate_call
    def writeall(
        self,
        dir: StrPath,
        root: StrPath | None = None,
        glob: str = "*",
        recursive: bool = True,
        compression_type: ZipCompression | None = None,
        compression_level: int | None = None,
    ) -> None:
        """
        Write a directory to the archive.

        Parameters
        ----------
        dir : StrPath
            The path of the directory to be added to the archive.
        root : StrPath
            Directory that will be the root directory of the archive, all paths in the archive will be relative to it.
            This MUST be a component of given directory path. Default is the parent of the given directory.
        glob : str, optional
            Only write files that match this glob pattern to the archive.
        recursive : bool, optional
            Recursively write all the files in the given directory. Default is True.
        compression_type : ZipCompression, optional
            The compression method to be used. If None, the default compression
            method of the archive will be used.
            This ONLY applies to zip files and has no effect on other archives.
        compression_level : int, optional
            The compression level to be used. If None, the default compression
            level of the archive will be used.
            This ONLY applies to zip files and has no effect on other archives.

        Returns
        -------
        None

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar.gz", "w:gz") as archive:
            archive.writeall(dir="hello-world/", glob="*.py")
            archive.tree()
            # hello-world
            # ├── src
            # │   └── hello_world
            # │       └── __init__.py
            # └── tests
            #     └── __init__.py
        ```
        """

        dir = dir.expanduser().resolve() if isinstance(dir, Path) else Path(dir).expanduser().resolve()

        if not dir.is_dir():
            raise UnsupportedArchiveOperation(
                f"The specified file '{dir}' either does not exist or is not a regular directory!"
            )

        if root is None:
            root = dir.parent
        else:
            root = Path(root).expanduser().resolve()

        if not dir.is_relative_to(root):
            raise ValueError(f"{dir} must be relative to {root}")

        files = tuple(dir.rglob(glob)) if recursive else tuple(dir.glob(glob))

        for file in files:
            arcname = file.relative_to(root)
            self.write(file, arcname=arcname, compression_type=compression_type, compression_level=compression_level)

    def close(self) -> None:
        self._handler.close()
