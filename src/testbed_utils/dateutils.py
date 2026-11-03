"""Small date helpers.

Deliberately simple and genuinely extendable — canned Demerzel tasks add
functions here (see README.md).
"""

from __future__ import annotations

import argparse
import sys
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


def date_range_days(start: str, end: str) -> int:
    """Return the absolute number of calendar days between two ISO 8601 dates.

    Each argument may carry an optional trailing ``Z`` which is stripped
    before parsing.

    >>> date_range_days("2024-01-01", "2024-01-10")
    9
    """
    try:
        start_date = date.fromisoformat(start.rstrip("Z"))
    except ValueError:
        raise ValueError(f"Invalid date: '{start}'")
    try:
        end_date = date.fromisoformat(end.rstrip("Z"))
    except ValueError:
        raise ValueError(f"Invalid date: '{end}'")
    return abs((start_date - end_date).days)


_DESCRIPTION = "Report the number of calendar days between two ISO 8601 dates."


def main():
    parser = argparse.ArgumentParser(
        prog="testbed-date-range", description=_DESCRIPTION,
    )
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD, optional trailing Z).")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD, optional trailing Z).")
    args = parser.parse_args()
    try:
        result = date_range_days(args.start_date, args.end_date)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(result)
