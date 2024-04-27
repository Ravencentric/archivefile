from pathlib import Path

from archivefile import ArchiveFile


def test_properties() -> None:
    file = "tests/test_data/source_GNU.tar"
    with ArchiveFile(file) as archive:
        assert archive.file == Path(file).resolve()
        assert archive.mode == "r"
        assert archive.handler == "TarFile"
        assert archive.password is None
