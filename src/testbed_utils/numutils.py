"""Small numeric summary helpers.

Deliberately simple and genuinely extendable — pure Python, no numpy.
"""

from __future__ import annotations

from collections.abc import Iterable

_EMPTY_MSG = "numbers must not be empty"
_RANGE_MSG = "p must be between 0 and 100"


def mean(numbers: Iterable[float]) -> float:
    """Return the arithmetic mean of *numbers*.

    >>> mean([1, 2, 3, 4])
    2.5
    """
    data = list(numbers)
    if not data:
        raise ValueError(_EMPTY_MSG)
    return sum(data) / len(data)


def median(numbers: Iterable[float]) -> float:
    """Return the median of *numbers*.

    For an odd-length input this is the middle value; for an even-length
    input it is the mean of the two middle values.

    >>> median([3, 1, 2])
    2
    >>> median([1, 2, 3, 4])
    2.5
    """
    data = sorted(numbers)
    if not data:
        raise ValueError(_EMPTY_MSG)
    mid = len(data) // 2
    if len(data) % 2:
        return data[mid]
    return (data[mid - 1] + data[mid]) / 2


def percentile(numbers: Iterable[float], p: float) -> float:
    """Return the *p*-th percentile of *numbers*, linearly interpolated.

    Interpolation runs between the two nearest ranks. *p* must be in the
    inclusive range 0 to 100.

    >>> percentile([1, 2, 3, 4, 5], 90)
    4.6
    """
    data = sorted(numbers)
    if not data:
        raise ValueError(_EMPTY_MSG)
    if not 0 <= p <= 100:
        raise ValueError(_RANGE_MSG)
    rank = (len(data) - 1) * p / 100
    lower = int(rank)
    upper = min(lower + 1, len(data) - 1)
    return data[lower] + (data[upper] - data[lower]) * (rank - lower)
