"""Small numeric statistics helpers.

Deliberately simple and genuinely extendable — canned Demerzel tasks add
functions here (see README.md).
"""

from __future__ import annotations

from typing import Sequence


def mean(data: Sequence[float]) -> float:
    """Return the arithmetic mean of *data*.

    Raises ``ValueError`` for an empty sequence.

    >>> mean([1, 2, 3, 4, 5])
    3.0
    """
    if not data:
        raise ValueError("mean requires at least one data point")
    return sum(data) / len(data)


def median(data: Sequence[float]) -> float:
    """Return the median value of *data*.

    Raises ``ValueError`` for an empty sequence.

    >>> median([3, 1, 2])
    2
    >>> median([1, 2, 3, 4])
    2.5
    """
    if not data:
        raise ValueError("median requires at least one data point")
    sorted_data = sorted(data)
    mid = len(sorted_data) // 2
    if len(sorted_data) % 2 == 1:
        return sorted_data[mid]
    return (sorted_data[mid - 1] + sorted_data[mid]) / 2


def summarize(data: Sequence[float]) -> dict[str, float]:
    """Return a summary dict for *data* with count, min, max, mean, and median.

    Raises ``ValueError`` for an empty sequence.

    >>> s = summarize([1, 2, 3, 4, 5])
    >>> s['mean']
    3.0
    >>> s['count']
    5
    """
    if not data:
        raise ValueError("summarize requires at least one data point")
    return {
        "count": len(data),
        "min": min(data),
        "max": max(data),
        "mean": mean(data),
        "median": median(data),
    }
