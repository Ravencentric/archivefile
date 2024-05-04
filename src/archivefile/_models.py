from __future__ import annotations

from datetime import datetime as DateTime
from datetime import timezone
from typing import Any

from pydantic import BaseModel, ByteSize, ValidationInfo, field_validator


class ArchiveMember(BaseModel):
    """Represents a member of an archive file"""

    name: str = ""
    """Name of the archive member."""

    size: ByteSize = ByteSize(0)
    """Uncompressed size of the archive member."""

    compressed_size: ByteSize = ByteSize(0)
    """Compressed size of the archive member."""

    datetime: DateTime = DateTime.min
    """The time and date of the last modification to the archive member."""

    checksum: int = 0
    """CRC32 checksum if the archive is a ZipFile, RarFile, or SevenZipFile. Header checksum if archive is a TarFile."""

    is_dir: bool = False
    """True if the archive member is a directory, False otherwise."""

    is_file: bool = False
    """True if the archive member is a file, False otherwise."""

    @field_validator("datetime", mode="after")
    @classmethod
    def _set_timezone(cls, v: DateTime, info: ValidationInfo) -> DateTime:
        return v.replace(tzinfo=timezone.utc)

    @field_validator("*", mode="before")
    @classmethod
    def _use_default_value(cls, v: Any, info: ValidationInfo) -> Any:
        if v is None:
            return cls.model_fields[info.field_name].default  # type: ignore
        return v
