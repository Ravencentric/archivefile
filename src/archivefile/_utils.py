from __future__ import annotations

import inspect
from collections.abc import Iterable
from pathlib import Path
from tarfile import is_tarfile
from typing import Any, Callable
from zipfile import is_zipfile

from py7zr import is_7zfile
from rarfile import is_rarfile, is_rarfile_sfx

from archivefile._enums import CommonExtensions
from archivefile._types import StrPath


def realpath(path: StrPath) -> Path:
    """
    Get the real path of a given file or directory.

    Parameters
    ----------
    path : str or Path
        A string representing a path or a Path object.

    Returns
    -------
    Path
        The path after expanding the user's home directory and resolving any symbolic links.
    """
    return path.expanduser().resolve() if isinstance(path, Path) else Path(path).expanduser().resolve()


def filter_kwargs(callabe: Callable[..., Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Filters out keyword arguments that are not accepted by the class constructor.

    Parameters
    ---------
    callabe : Callable[..., Any]
        The callable to check against.
    kwargs : dict[str, Any]
        A dictionary of keyword arguments to filter.

    Returns
    -------
    dict[str, Any]
        A dictionary of keyword arguments that are accepted by the callable.
    """
    parameters = inspect.signature(callabe).parameters.keys()
    return {
        parameter: value
        for parameter, value in kwargs.items()
        if parameter in parameters  # We only want to keep parameters accepted by the callable
        and parameter
        not in ("file", "mode", "name")  # We remove these because they are already handled by ArchiveFile constructor
    }


def is_archive(file: StrPath) -> bool:
    """
    Check whether the given archive file is a supported archive or not.

    Parameters
    ---------
    file : StrPath
        Path to the archive file.

    Returns
    -------
    bool
        True if the archive is supported, False otherwise.
    """
    file = realpath(file)

    if file.exists():
        return is_tarfile(file) or is_zipfile(file) or is_rarfile(file) or is_rarfile_sfx(file) or is_7zfile(file)
    else:
        return False


def check_extension(extensions: Iterable[str], whitelist: CommonExtensions) -> bool:
    """
    Check given extensions against a whitelist of extensions.

    Parameters
    ---------
    extensions : Iterable[str]
        Extensions to check.
    whitelist : CommonExtensions
        Whitelist of extensions to check against the given extensions.

    Returns
    -------
    bool
        True if the extension is whitelisted, False otherwise.
    """

    for extension in extensions:
        if extension in whitelist.value:
            return True

    return False
