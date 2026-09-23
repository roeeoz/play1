"""Small date helpers.

Deliberately simple and genuinely extendable — canned Demerzel tasks add
functions here (see README.md).
"""

from __future__ import annotations

from datetime import date, timedelta


def days_between(start: date, end: date) -> int:
    """Whole days from *start* to *end* (negative if *end* precedes *start*).

    >>> days_between(date(2026, 1, 1), date(2026, 1, 8))
    7
    """
    return (end - start).days


def is_weekend(day: date) -> bool:
    """True if *day* falls on a Saturday or Sunday."""
    return day.weekday() >= 5


def business_days_between(start: date, end: date) -> int:
    """Business days (Monday to Friday) between *start* and *end*.

    The earlier date is counted and the later date is excluded, so a Monday
    to the following Monday yields 5. Argument order does not matter and the
    result is never negative, unlike :func:`days_between`, which is signed.

    >>> business_days_between(date(2026, 1, 5), date(2026, 1, 12))
    5
    """
    if start > end:
        start, end = end, start
    return sum(
        1
        for offset in range((end - start).days)
        if not is_weekend(start + timedelta(days=offset))
    )


def humanize_delta(delta: timedelta) -> str:
    """Render *delta* as a short human string: '3 days', '1 hour', '5 minutes'.

    Uses the largest non-zero unit among days, hours, minutes; anything under
    one minute is 'moments'. Negative deltas are rendered by magnitude with an
    'ago' suffix.

    >>> humanize_delta(timedelta(days=3))
    '3 days'
    >>> humanize_delta(timedelta(hours=-1))
    '1 hour ago'
    """
    seconds = delta.total_seconds()
    suffix = " ago" if seconds < 0 else ""
    seconds = abs(seconds)

    days, rem = divmod(int(seconds), 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60

    if days:
        text = f"{days} day" + ("s" if days != 1 else "")
    elif hours:
        text = f"{hours} hour" + ("s" if hours != 1 else "")
    elif minutes:
        text = f"{minutes} minute" + ("s" if minutes != 1 else "")
    else:
        text = "moments"
    return text + suffix
