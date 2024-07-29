from __future__ import annotations

import re
from pathlib import Path
from tarfile import is_tarfile
from types import TracebackType
from typing import Any, overload
from zipfile import is_zipfile

from py7zr import is_7zfile
from pydantic import validate_call
from rarfile import is_rarfile, is_rarfile_sfx
from typing_extensions import Generator, Self

from archivefile._adapters._base import BaseArchiveAdapter
from archivefile._adapters._rar import RarFileAdapter
from archivefile._adapters._sevenzip import SevenZipFileAdapter
from archivefile._adapters._tar import TarFileAdapter
from archivefile._adapters._zip import ZipFileAdapter
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
from archivefile._utils import realpath


class ArchiveFile(BaseArchiveAdapter):
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
        """
        Open an archive file.

        Parameters
        ----------
        file : StrPath
            Path to the archive file.
        mode : OpenArchiveMode, optional
            Specifies the mode for opening the archive file.
        password : str, optional
            Password for encrypted archive files.
        compression_type : CompressionType, optional
            The compression method to be used for writing zip files.
            Has no effect on reading zip files.
            Has no offect on archives other than zip files.
        compression_level : CompressionLevel, optional
            The compression level to be used for writing zip files.
            Has no effect on reading zip files.
            Has no offect on archives other than zip files.
        kwargs : Any
            Keyword arugments to pass to the underlying library.

        Returns
        -------
        None

        Raises
        ------
        NotImplementedError
            Raised when the archive format is unsupported

        References
        ----------
        ArchiveFile currently supports the following:

        - [`ZipFile`][zipfile.ZipFile]
        - [`TarFile`][tarfile.TarFile.open]
        - [`RarFile`][rarfile.RarFile]
        - [`SevenZipFile`][py7zr.SevenZipFile]
        """
        self._file = realpath(file)
        self._mode = mode
        self._password = password
        self._kwargs = kwargs
        self._compression_type = compression_type
        self._compression_level = compression_level
        self._initialize_adapter()

    def _initialize_adapter(self) -> None:
        if not self._file.exists():
            if not self._mode.startswith("r"):
                filename = self._file.name.lower()

                if re.search(r"\.(zip|cbz)$", filename):
                    adapter = ZipFileAdapter
                elif re.search(r"\.((tar(\.(bz2|gz|xz))?)|(cbt))$", filename):
                    adapter = TarFileAdapter  # type: ignore
                elif re.search(r"\.(7z|cb7)$", filename):
                    adapter = SevenZipFileAdapter  # type: ignore
                elif re.search(r"\.(rar|cbr)$", filename):
                    adapter = RarFileAdapter  # type: ignore
                else:
                    raise NotImplementedError(f"Unsupported archive format: {self._file}")
            else:
                raise FileNotFoundError(self._file)

        elif is_zipfile(self._file):
            adapter = ZipFileAdapter

        elif is_tarfile(self._file):
            adapter = TarFileAdapter  # type: ignore

        elif is_7zfile(self._file):
            adapter = SevenZipFileAdapter  # type: ignore

        elif is_rarfile(self._file) or is_rarfile_sfx(self._file):
            adapter = RarFileAdapter  # type: ignore

        else:
            raise NotImplementedError(f"Unsupported archive format: {self._file}")

        self._adapter = adapter(
            self._file,
            self._mode,
            password=self._password,
            compression_type=self._compression_type,
            compression_level=self._compression_level,
            **self._kwargs,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self._adapter.close()

    @property
    def file(self) -> Path:
        """Path to the archive file."""
        return self._adapter.file

    @property
    def mode(self) -> OpenArchiveMode:
        """Mode in which the archive file was opened."""
        return self._adapter.mode

    @property
    def password(self) -> str | None:
        """Archive password."""
        return self._adapter.password

    @property
    def compression_type(self) -> CompressionType | None:
        """Compression type used for writing."""
        return self._adapter.compression_type

    @property
    def compression_level(self) -> CompressionLevel | None:
        """Compression level used for writing."""
        return self._adapter.compression_level  # type: ignore

    @property
    def adapter(self) -> str:
        """Name of the underlying adapter class, useful for debugging."""
        return self._adapter.adapter

    @validate_call
    def get_member(self, member: StrPath) -> ArchiveMember:
        """
        Retrieve an ArchiveMember object by it's name.

        Parameters
        ----------
        member : StrPath
            Name of the member.

        Returns
        -------
        ArchiveMember
            Represents a member of the archive.

        Raises
        ------
        KeyError
            Member was not found in the archive.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar") as archive:
            archive.get_member("README.md")
            # ArchiveMember(name='README.md', size=3799, compressed_size=3799, datetime=datetime.datetime(2024, 4, 10, 20, 10, 57, tzinfo=datetime.timezone.utc), checksum=5251, is_dir=False, is_file=True)
        ```
        """
        return self._adapter.get_member(member)

    @validate_call
    def get_members(self) -> Generator[ArchiveMember]:
        """
        Retrieve all members of the archive as a tuple of ArchiveMember objects.

        Yields
        -------
        Generator[ArchiveMember]
            Members of the archive as a generator of ArchiveMember objects.

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
        return self._adapter.get_members()

    @validate_call
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
        return self._adapter.get_names()

    def print_tree(
        self,
        *,
        max_depth: int = 0,
        style: TreeStyle = "const",
    ) -> None:
        """
        Print the contents of the archive as a tree.

        Parameters
        ----------
        max_depth : int, optional
            Maximum depth to print.
        style : TreeStyle, optional
            The style of the tree.

        Returns
        -------
        None

        Notes
        -----
        The [`bigtree`](https://pypi.org/p/bigtree/) dependency is required to use this method.

        You can install it via either of these commands:

        - `pip install archivefile[bigtree]`
        - `pip install archivefile[all]`

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar.gz") as archive:
            archive.print_tree()
            # source.tar.gz
            # └── hello-world
            #     ├── pyproject.toml
            #     ├── README.md
            #     ├── src
            #     │   └── hello_world
            #     │       └── __init__.py
            #     └── tests
            #         └── __init__.py
        ```
        """
        self._adapter.print_tree(max_depth=max_depth, style=style)

    @validate_call
    def print_table(
        self,
        *,
        title: str | None = None,
        style: TableStyle = "markdown",
        sort_by: SortBy = "name",
        descending: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Print the contents of the archive as a table.

        Parameters
        ----------
        title : str, optional
            Title of the table. Defaults to archive file name.
        style : TableStyle, optional
            The style of the table.
        sort_by : SortBy, optional
            Key used to sort the table.
        descending : bool, optional
            If True, sorting will be in descending order.
        kwargs : Any
            Additional keyword arguments to be passed to the [`Table`][rich.table.Table] constructor.

        Returns
        -------
        None

        Notes
        -----
        The [`rich`](https://pypi.org/p/rich/) dependency is required to use this method.

        You can install it via either of these commands:

        - `pip install archivefile[rich]`
        - `pip install archivefile[all]`

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            archive.print_table()
            #                                                     source.zip
            #
            # | Name                                    | Date modified             | Type   | Size | Compressed Size |
            # |-----------------------------------------|---------------------------|--------|------|-----------------|
            # | hello-world/                            | 2024-05-02T09:41:24+00:00 | Folder | 0B   | 0B              |
            # | hello-world/README.md                   | 2024-05-02T09:41:24+00:00 | File   | 0B   | 0B              |
            # | hello-world/pyproject.toml              | 2024-05-02T09:41:24+00:00 | File   | 363B | 241B            |
            # | hello-world/src/                        | 2024-05-02T09:41:24+00:00 | Folder | 0B   | 0B              |
            # | hello-world/src/hello_world/            | 2024-05-02T09:41:24+00:00 | Folder | 0B   | 0B              |
            # | hello-world/src/hello_world/__init__.py | 2024-05-02T09:41:24+00:00 | File   | 0B   | 0B              |
            # | hello-world/tests/                      | 2024-05-02T09:41:24+00:00 | Folder | 0B   | 0B              |
            # | hello-world/tests/__init__.py           | 2024-05-02T09:41:24+00:00 | File   | 0B   | 0B              |
        ```
        """
        self._adapter.print_table(title=title, style=style, sort_by=sort_by, descending=descending, **kwargs)

    @validate_call
    def extract(self, member: StrPath | ArchiveMember, *, destination: StrPath = Path.cwd()) -> Path:
        """
        Extract a member of the archive.

        Parameters
        ----------
        member : StrPath, ArchiveMember
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
            Member was not found in the archive.

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
        return self._adapter.extract(member, destination=destination)

    @validate_call
    def extractall(
        self, *, destination: StrPath = Path.cwd(), members: CollectionOf[StrPath | ArchiveMember] | None = None
    ) -> Path:
        """
        Extract all the members of the archive to the destination directory.

        Parameters
        ----------
        destination : StrPath
            The path to the directory where the members will be extracted.
            If not specified, the current working directory is used as the default destination.
        members : CollectionOf[StrPath | ArchiveMember], optional
            Collection of member names or ArchiveMember objects to extract.
            Default is `None` which will extract all members.

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
        return self._adapter.extractall(destination=destination, members=members)

    @validate_call
    def read_bytes(self, member: StrPath | ArchiveMember) -> bytes:
        """
        Read the member in bytes mode.

        Parameters
        ----------
        member : StrPath, ArchiveMember
            Name of the member or an ArchiveMember object.

        Returns
        -------
        bytes
            The contents of the file as bytes.

        Raises
        ------
        KeyError
            Member was not found in the archive.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.zip") as archive:
            data = archive.read_bytes("hello-world/pyproject.toml")
            print(data)
            # b'[tool.poetry]\\r\\nname = "hello-world"\\r\\nversion = "0.1.0"\\r\\ndescription = ""\\r\\nreadme = "README.md"\\r\\npackages = [{include = "hello_world", from = "src"}]\\r\\n'
        ```
        """
        return self._adapter.read_bytes(member)

    @validate_call
    def read_text(
        self,
        member: StrPath | ArchiveMember,
        *,
        encoding: str = "utf-8",
        errors: ErrorHandler = "strict",
    ) -> str:
        """
        Read the member in text mode.

        Parameters
        ----------
        member : StrPath, ArchiveMember
            Name of the member or an ArchiveMember object.
        encoding : str, optional
            Encoding used to read the file. Default is `utf-8`.
            Setting it to `None` will use platform-dependent encoding.
        errors : ErrorHandler, optional
            String that specifies how encoding and decoding errors are to be handled.

        Returns
        -------
        str
            The contents of the file as a string.

        Raises
        ------
        KeyError
            Member was not found in the archive.

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
        return self._adapter.read_text(member, encoding=encoding, errors=errors)

    @validate_call
    def write(
        self,
        file: StrPath,
        *,
        arcname: StrPath | None = None,
    ) -> None:
        """
        Write a single file to the archive.

        Parameters
        ----------
        file : StrPath
            Path of the file.
        arcname : StrPath, optional
            Name which the file will have in the archive.
            Default is the basename of the file.

        Returns
        -------
        None

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("example.zip", "w") as archive:
            archive.write("/root/some/path/to/foo.txt")
            archive.write("bar.txt", arcname="baz.txt")
            archive.write("recipe/spam.txt", arcname="ingredients/spam.txt")
            archive.write("recipe/eggs.txt", arcname="ingredients/eggs.txt")
            archive.print_tree()
            # example.zip
            # ├── foo.txt
            # ├── baz.txt
            # └── ingredients
            #     ├── spam.txt
            #     └── eggs.txt
        ```
        """
        self._adapter.write(file, arcname=arcname)

    @validate_call
    def write_text(
        self,
        data: str,
        *,
        arcname: StrPath,
    ) -> None:
        """
        Write the string `data` to a file within the archive named `arcname`.

        Parameters
        ----------
        data : str
            The text data to write to the archive.
        arcname : StrPath, optional
            The name which the file will have in the archive.

        Returns
        -------
        None

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("newarchive.zip", "w") as archive:
            archive.write_text("spam and eggs", arcname="recipe.txt")
            members = archive.get_names()
            print(members)
            # ('recipe.txt',)
            text = archive.read_text("recipe.txt")
            print(text)
            # 'spam and eggs'
        ```
        """

        self._adapter.write_text(data, arcname=arcname)

    @validate_call
    def write_bytes(
        self,
        data: bytes,
        *,
        arcname: StrPath,
    ) -> None:
        """
        Write the bytes `data` to a file within the archive named `arcname`.

        Parameters
        ----------
        data: str
            The bytes data to write to the archive.
        arcname : StrPath, optional
            The name which the file will have in the archive.

        Returns
        -------
        None

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("skynet.7z", "w") as archive:
            archive.write_bytes(b"010010100101", arcname="terminator.py")
            members = archive.get_names()
            print(members)
            # ('terminator.py',)
            data = archive.read_bytes("terminator.py")
            print(data)
            # b"010010100101"
        ```
        """

        self._adapter.write_bytes(data, arcname=arcname)

    @validate_call
    def writeall(
        self,
        dir: StrPath,
        *,
        root: StrPath | None = None,
        glob: str = "*",
        recursive: bool = True,
    ) -> None:
        """
        Write a directory to the archive.

        Parameters
        ----------
        dir : StrPath
            Path of the directory.
        root : StrPath
            Directory that will be the root directory of the archive, all paths in the archive will be relative to it.
            This must be relative to given directory path. Default is the parent of the given directory.
        glob : str, optional
            Only write files that match this glob pattern to the archive.
        recursive : bool, optional
            Recursively write all the files in the given directory. Default is True.

        Returns
        -------
        None

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar.gz", "w:gz") as archive:
            archive.writeall(dir="hello-world/")
            archive.print_tree()
            # source.tar.gz
            # └── hello-world
            #     ├── pyproject.toml
            #     ├── README.md
            #     ├── src
            #     │   └── hello_world
            #     │       └── __init__.py
            #     └── tests
            #         └── __init__.py
        ```
        """

        self._adapter.writeall(
            dir,
            root=root,
            glob=glob,
            recursive=recursive,
        )

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
        self._adapter.close()

    def __repr__(self) -> str:
        password = '"********"' if self.password else None
        return f'{self.__class__.__name__}("{self.file}", "{self.mode}", password={password})'
