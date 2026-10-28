"""Clamp a numeric value to an inclusive range."""

from __future__ import annotations

_BOUNDS_MSG = "low must not be greater than high"


def clamp(value: float, low: float, high: float) -> float:
    """Return *value* bounded to the inclusive range [*low*, *high*].

    >>> clamp(15, 0, 10)
    10
    """
    if low > high:
        raise ValueError(_BOUNDS_MSG)
    return max(low, min(value, high))
