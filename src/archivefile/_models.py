from __future__ import annotations

from datetime import datetime as DateTime
from datetime import timezone
from typing import Any

from pydantic import BaseModel, ByteSize, ValidationInfo, field_validator


class ArchiveMember(BaseModel):
    name: str = ""
    size: ByteSize = ByteSize(0)
    compressed_size: ByteSize = ByteSize(0)
    datetime: DateTime = DateTime.min
    checksum: int = 0
    is_dir: bool = False
    is_file: bool = False

    @field_validator("datetime", mode="after")
    @classmethod
    def set_timezone(cls, v: DateTime, info: ValidationInfo) -> DateTime:
            return v.replace(tzinfo=timezone.utc)

    @field_validator("*", mode="before")
    @classmethod
    def use_default_value(cls, v: Any, info: ValidationInfo) -> Any:
        if v is None:
            return cls.model_fields[info.field_name].default # type: ignore
        return v