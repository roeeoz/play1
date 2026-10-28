"""Range-clamping helper.

Pure Python, no external dependencies — clamp a numeric value to a closed
interval.
"""

from __future__ import annotations

_RANGE_MSG = "low must not be greater than high"


def clamp(value: float, low: float, high: float) -> float:
    """Return *value* bounded to the closed interval [*low*, *high*].

    Raises :class:`ValueError` when *low* is strictly greater than *high*.

    >>> clamp(5, 1, 10)
    5
    """
    if low > high:
        raise ValueError(_RANGE_MSG)
    return max(low, min(value, high))
