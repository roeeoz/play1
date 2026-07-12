"""Small numeric helpers.

Deliberately simple and genuinely extendable — canned Demerzel tasks add
functions here (see README.md).
"""

from __future__ import annotations


def clamp(value: float, lo: float, hi: float) -> float:
    """Return *value* clamped to the closed interval [*lo*, *hi*].

    Raises ValueError if *lo* > *hi* (invalid dimension bounds).

    >>> clamp(5, 1, 10)
    5
    >>> clamp(-3, 0, 100)
    0
    >>> clamp(200, 0, 100)
    100
    """
    if lo > hi:
        raise ValueError(f"lo must be <= hi, got lo={lo!r}, hi={hi!r}")
    return max(lo, min(hi, value))
