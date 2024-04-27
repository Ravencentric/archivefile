from tarfile import TarFile
from zipfile import ZipFile

from archivefile._enums import CommonExtensions
from archivefile._utils import check_extension, filter_kwargs, is_archive
from py7zr import SevenZipFile


def test_filter_kwargs() -> None:
    zipfile_kwargs = {
        "file": None,
        "mode": "r",
        "compression": "ZIP_STORED",
        "allowZip64": True,
        "compresslevel": None,
        "strict_timestamps": True,
        "metadata_encoding": None,
    }

    tarfile_kwargs = {
        "name": None,
        "mode": "r",
        "fileobj": None,
        "format": None,
        "tarinfo": None,
        "dereference": None,
        "ignore_zeros": None,
        "encoding": None,
        "errors": "surrogateescape",
        "pax_headers": None,
        "debug": None,
        "errorlevel": None,
        "copybufsize": None,
    }

    sevenzipfile_kwargs = {
        "file": None,
        "mode": "r",
        "filters": None,
        "dereference": None,
        "password": None,
        "header_encryption": False,
        "blocksize": None,
        "mp": False,
    }

    kwargs = zipfile_kwargs | tarfile_kwargs | sevenzipfile_kwargs

    assert filter_kwargs(ZipFile, kwargs=kwargs) == {
        "compression": "ZIP_STORED",
        "allowZip64": True,
        "compresslevel": None,
        "strict_timestamps": True,
        "metadata_encoding": None,
    }

    assert filter_kwargs(TarFile, kwargs=kwargs) == {
        "fileobj": None,
        "format": None,
        "tarinfo": None,
        "dereference": None,
        "ignore_zeros": None,
        "encoding": None,
        "errors": "surrogateescape",
        "pax_headers": None,
        "debug": None,
        "errorlevel": None,
        "copybufsize": None,
    }

    assert filter_kwargs(SevenZipFile, kwargs=kwargs) == {
        "filters": None,
        "dereference": None,
        "password": None,
        "header_encryption": False,
        "blocksize": None,
        "mp": False,
    }


def test_is_archive() -> None:
    assert is_archive("tests/test_data/source_BEST.rar") is True
    assert is_archive("tests/test_data/source_PPMD.zip") is True
    assert is_archive(r"src\archivefile\__init__.py") is False
    assert is_archive(r"non-existent-file.py") is False


def test_check_extension() -> None:
    assert check_extension([".zip", ".cbz"], CommonExtensions.ZIP) is True
    assert check_extension([".txt", ".py"], CommonExtensions.ZIP) is False
