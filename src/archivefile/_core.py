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

from py7zr import SevenZipFile, is_7zfile
from pydantic import validate_call
from rarfile import RarFile, RarInfo, is_rarfile
from typing_extensions import Literal, Self

from archivefile._enums import CommonExtensions, CompressionType
from archivefile._exceptions import UnsupportedArchiveOperation
from archivefile._models import ArchiveMember
from archivefile._types import CompressionLevel, ErrorHandler, OpenArchiveMode, SortBy, StrPath, TableStyle, TreeStyle
from archivefile._utils import check_extension, filter_kwargs, realpath


class ArchiveFile:
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
        file : StrPath
            Path to the archive file.
        mode : OpenArchiveMode, optional
            Specifies the mode for opening the archive file.
        password : str, optional
            Password for encrypted archive files.
        kwargs : Any
            Keyword arugments to pass to the underlying handler.
            Kwargs that are not relevent to the current handler will automatically
            be removed so you don't have to worry about accidentally passing ZipFile's kwargs to TarFile.

        Returns
        -------
        None

        References
        ----------
        ArchiveFile currently supports the following handlers:

        - [`ZipFile`][zipfile.ZipFile]
        - [`TarFile`][tarfile.TarFile.open]
        - [`RarFile`][rarfile.RarFile]
        - [`SevenZipFile`][py7zr.SevenZipFile]
        """
        self._file = realpath(file)
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
                    self._handler = tarfile.open(archive, mode=tarfile_mode, **filter_kwargs(TarFile, kwargs=kwargs))
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
            self._handler = tarfile.open(archive, mode=tarfile_mode, **filter_kwargs(TarFile, kwargs=kwargs))

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
        """Path to the archive file."""
        return self._file

    @property
    def mode(self) -> OpenArchiveMode:
        """Mode in which the archive file was opened."""
        return self._mode

    @property
    def password(self) -> str | None:
        """Archive password."""
        return self._password

    @property
    def handler(self) -> str:
        """Name of the handler used."""
        return self._handler.__class__.__name__

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
                size=zipinfo.file_size,
                compressed_size=zipinfo.compress_size,
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
                size=sevenzipinfo.uncompressed,
                # Sometimes sevenzip can return 0 for compressed size when there's no compression
                # in that case we simply return the uncompressed size instead.
                compressed_size=sevenzipinfo.compressed or sevenzipinfo.uncompressed,
                datetime=sevenzipinfo.creationtime,
                checksum=sevenzipinfo.crc32,
                is_dir=sevenzipinfo.is_directory,
                is_file=not sevenzipinfo.is_directory,
            )

        else:
            rarinfo: RarInfo = self._handler.getinfo(member)
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

    @validate_call
    def get_members(self) -> tuple[ArchiveMember, ...]:
        """
        Retrieve all members of the archive as a tuple of ArchiveMember objects.

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
        if isinstance(self._handler, TarFile):
            return tuple(self._handler.getnames())

        elif isinstance(self._handler, ZipFile):
            return tuple(self._handler.namelist())

        elif isinstance(self._handler, SevenZipFile):
            return tuple(self._handler.getnames())

        else:
            return tuple(self._handler.namelist())

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
        try:
            from bigtree.tree.construct import list_to_tree
        except ModuleNotFoundError:  # pragma: no cover
            raise ModuleNotFoundError("The 'print_tree()' method requires the 'bigtree' dependency.")

        paths = [f"{self.file.name}/{member}" for member in self.get_names()]
        tree = list_to_tree(paths)  # type: ignore
        tree.show(max_depth=max_depth, style=style)

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
        destination = realpath(destination)
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
        self, *, destination: StrPath = Path.cwd(), members: Iterable[StrPath | ArchiveMember] | None = None
    ) -> Path:
        """
        Extract all the members of the archive to the destination directory.

        Parameters
        ----------
        destination : StrPath
            The path to the directory where the members will be extracted.
            If not specified, the current working directory is used as the default destination.
        members : Iterable[StrPath | ArchiveMember], optional
            Iterable of member names or ArchiveMember objects to extract.
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
        destination = realpath(destination)
        destination.mkdir(parents=True, exist_ok=True)

        names: list[str] = []
        if members:
            for member in members:
                if isinstance(member, ArchiveMember):
                    names.append(member.name)
                elif isinstance(member, Path):
                    names.append(member.relative_to(member.anchor).as_posix())
                else:
                    names.append(member)

        if isinstance(self._handler, TarFile):
            if names:
                tar_members = [self._handler.getmember(name) for name in names]
                self._handler.extractall(path=destination, members=tar_members)
            else:
                self._handler.extractall(path=destination)
            return destination

        elif isinstance(self._handler, ZipFile):
            password = self._password.encode() if self._password else None

            if names:
                self._handler.extractall(path=destination, members=names, pwd=password)
            else:
                self._handler.extractall(path=destination, pwd=password)
            return destination

        elif isinstance(self._handler, SevenZipFile):
            # SevenZipFile doesn't have a members=[...] parameter like the rest
            if names:
                self._handler.extract(path=destination, targets=names)
            else:
                self._handler.extractall(path=destination)
            return destination

        else:
            if names:
                self._handler.extractall(path=destination, members=names, pwd=self._password)
            else:
                self._handler.extractall(path=destination, members=names, pwd=self._password)
            return destination

    @validate_call
    def read_text(
        self,
        member: StrPath | ArchiveMember,
        *,
        encoding: str | None = "utf-8",
        errors: ErrorHandler | None = None,
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
        with TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            return self.extract(member, destination=tmpdir).read_text(encoding=encoding, errors=errors)

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
        with TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            return self.extract(member, destination=tmpdir).read_bytes()

    @validate_call
    def write(
        self,
        file: StrPath,
        *,
        arcname: StrPath | None = None,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
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
        compression_type : CompressionType, optional
            The compression method to be used. If `None`, the default compression
            method of the archive will be used.
        compression_level : CompressionLevel, optional
            The compression level to be used. If `None`, the default compression
            level of the archive will be used.

        Returns
        -------
        None

        Notes
        -----
        Both the `compression_type` and `compression_level` parameters
        only apply to zip files and have no effect on other archive formats.

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

        file = realpath(file)

        if arcname is None:
            arcname = file.name

        if not file.is_file():
            raise UnsupportedArchiveOperation(
                f"The specified file '{file}' either does not exist or is not a regular file!"
            )

        if isinstance(self._handler, TarFile):
            self._handler.add(file, arcname=arcname)

        elif isinstance(self._handler, ZipFile):
            if compression_type == CompressionType.BZIP2:
                if compression_level == 0:
                    compression_level = 1

            self._handler.write(file, arcname=arcname, compress_type=compression_type, compresslevel=compression_level)

        elif isinstance(self._handler, SevenZipFile):
            arcname = arcname.as_posix() if isinstance(arcname, Path) else arcname
            self._handler.write(file, arcname=arcname)

        else:  # pragma: no cover
            # In reality, this can never happen since it'll exit in the constructor before ever reaching here
            raise UnsupportedArchiveOperation('Cannot write a rar file. Rar files only support mode="r"!')

    @validate_call
    def write_text(
        self,
        data: str,
        *,
        arcname: StrPath,
        encoding: str | None = "utf-8",
        errors: ErrorHandler | None = None,
        newline: Literal["", "\n", "\r", "\r\n"] | None = None,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
    ) -> None:
        """
        Write the string `data` to a file within the archive named `arcname`.

        Parameters
        ----------
        data : str
            The text data to write to the archive.
        arcname : StrPath, optional
            The name which the file will have in the archive.
        encoding : str, optional
            Encoding of the given data. Default is `utf-8`.
            Setting it to `None` will use platform-dependent encoding.
        errors : ErrorHandler, optional
            String that specifies how encoding and decoding errors are to be handled.
        newline : Literal['', '\\n', '\\r', '\\r\\n'], optional
            If newline is `None`, any `\\n` characters written are translated to the system default line separator, [`os.linesep`][os.linesep].
            If newline is `''` or `\\n`, no translation takes place.
            If newline is any of the other legal values, any `\\n` characters written are translated to the given string.
        compression_type : CompressionType, optional
            The compression method to be used. If `None`, the default compression
            method of the archive will be used.
        compression_level : CompressionLevel, optional
            The compression level to be used. If `None`, the default compression
            level of the archive will be used.

        Returns
        -------
        None

        Notes
        -----
        Both the `compression_type` and `compression_level` parameters
        only apply to zip files and have no effect on other archive formats.

        References
        ----------
        - [Encodings](https://docs.python.org/3/library/codecs.html#standard-encodings)
        - [Error Handlers](https://docs.python.org/3/library/codecs.html#error-handlers)
        - [Newline](https://docs.python.org/3/library/functions.html#open)

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

        arcname = Path(arcname)

        with TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            tmppath = Path(tmpdir) / arcname.parent
            tmppath.mkdir(parents=True, exist_ok=True)
            tmpfile = tmppath / arcname.name
            tmpfile.touch(exist_ok=True)
            tmpfile.write_text(data=data, encoding=encoding, errors=errors, newline=newline)

            self.write(tmpfile, arcname=arcname, compression_type=compression_type, compression_level=compression_level)

    @validate_call
    def write_bytes(
        self,
        data: bytes,
        *,
        arcname: StrPath,
        compression_type: CompressionType | None = None,
        compression_level: CompressionLevel | None = None,
    ) -> None:
        """
        Write the bytes `data` to a file within the archive named `arcname`.

        Parameters
        ----------
        data: str
            The bytes data to write to the archive.
        arcname : StrPath, optional
            The name which the file will have in the archive.
        compression_type : CompressionType, optional
            The compression method to be used. If `None`, the default compression
            method of the archive will be used.
        compression_level : CompressionLevel, optional
            The compression level to be used. If `None`, the default compression
            level of the archive will be used.

        Returns
        -------
        None

        Notes
        -----
        Both the `compression_type` and `compression_level` parameters
        only apply to zip files and have no effect on other archive formats.

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

        arcname = Path(arcname)

        with TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            tmppath = Path(tmpdir) / arcname.parent
            tmppath.mkdir(parents=True, exist_ok=True)
            tmpfile = tmppath / arcname.name
            tmpfile.touch(exist_ok=True)
            tmpfile.write_bytes(data)

            self.write(tmpfile, arcname=arcname, compression_type=compression_type, compression_level=compression_level)

    @validate_call
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
        compression_type : CompressionType, optional
            The compression method to be used. If `None`, the default compression
            method of the archive will be used.
        compression_level : CompressionLevel, optional
            The compression level to be used. If `None`, the default compression
            level of the archive will be used.

        Returns
        -------
        None

        Notes
        -----
        Both the `compression_type` and `compression_level` parameters
        only apply to zip files and have no effect on other archive formats.

        Examples
        --------
        ```py
        from archivefile import ArchiveFile

        with ArchiveFile("source.tar.gz", "w:gz") as archive:
            archive.writeall(dir="hello-world/", glob="*.py")
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

        dir = realpath(dir)

        if not dir.is_dir():
            raise UnsupportedArchiveOperation(
                f"The specified file '{dir}' either does not exist or is not a regular directory!"
            )

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
        self._handler.close()
