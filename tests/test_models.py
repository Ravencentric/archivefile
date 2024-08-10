from __future__ import annotations

from archivefile import ArchiveMember


def test__str__() -> None:
    assert ArchiveMember(name="src/main/").name == str(ArchiveMember(name="src/main/"))
    assert ArchiveMember(name="src/main").name == str(ArchiveMember(name="src/main"))
    assert ArchiveMember(name="src/main.py").name == str(ArchiveMember(name="src/main.py"))
