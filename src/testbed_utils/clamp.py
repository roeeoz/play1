"""Clamp a numeric value to an inclusive range."""

from __future__ import annotations

_INVERTED_RANGE_MSG = "low must not exceed high, got low={low!r}, high={high!r}"


def clamp(value: float, low: float, high: float) -> float:
    """Return *value* bounded to the inclusive range [*low*, *high*].

    >>> clamp(5, 1, 10)
    5
    """
    if low > high:
        raise ValueError(_INVERTED_RANGE_MSG.format(low=low, high=high))
    return max(low, min(high, value))
