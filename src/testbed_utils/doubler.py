"""A tiny doubling helper.

Pure Python, no I/O: ``double`` only returns a value.
"""

from __future__ import annotations


def double(n: int) -> int:
    """Return *n* multiplied by two.

    >>> double(3)
    6
    >>> double(-4)
    -8
    """
    return n * 2
