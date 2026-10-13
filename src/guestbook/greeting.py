"""Greeting formatting for guestbook entries.

Pure functions only — no Flask, no storage.
"""

from __future__ import annotations


def shout(name: str) -> str:
    """Return *name*'s greeting in uppercase.

    >>> shout('ada')
    'HELLO, ADA!'
    """
    return f"Hello, {name}!".upper()
