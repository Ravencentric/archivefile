"""Compatibility module to for older python versions"""

import sys

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata

__all__ = ["metadata"]
