from __future__ import annotations

from importlib import metadata

from typing_extensions import NamedTuple


class Version(NamedTuple):
    """Version tuple based on SemVer"""

    major: int
    """Major version number"""
    minor: int
    """Minor version number"""
    patch: int
    """Patch version number"""


def _get_version() -> str:
    """
    Get the version of archivefile
    """
    try:
        return metadata.version("archivefile")

    except metadata.PackageNotFoundError:
        return "0.0.0"
