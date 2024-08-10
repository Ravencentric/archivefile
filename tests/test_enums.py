from __future__ import annotations

from archivefile import CompressionType


def test_compression_type_enum() -> None:
    assert CompressionType.get("stored") is CompressionType.STORED
    assert CompressionType.get("DEFLATED") is CompressionType.DEFLATED
    assert CompressionType.get("bziP2") is CompressionType.BZIP2
    assert CompressionType.get("lzMa") is CompressionType.LZMA

    assert CompressionType.get(0) is CompressionType.STORED
    assert CompressionType.get(8) is CompressionType.DEFLATED
    assert CompressionType.get(12) is CompressionType.BZIP2
    assert CompressionType.get(14) is CompressionType.LZMA

    assert CompressionType.get(CompressionType.STORED) is CompressionType.STORED
    assert CompressionType.get(CompressionType.DEFLATED) is CompressionType.DEFLATED
    assert CompressionType.get(CompressionType.BZIP2) is CompressionType.BZIP2
    assert CompressionType.get(CompressionType.LZMA) is CompressionType.LZMA

    assert CompressionType.get(999999999999) is CompressionType.STORED
    assert CompressionType.get("non-existent-key") is CompressionType.STORED
    assert CompressionType.get(999999999999, "bzip2") is CompressionType.BZIP2
    assert CompressionType.get("non-existent-key", "lzma") is CompressionType.LZMA
