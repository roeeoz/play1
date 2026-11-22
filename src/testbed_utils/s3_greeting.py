"""Standalone farewell greeting, matching greetlib's ``farewell`` text."""

from __future__ import annotations

FAREWELL_FORMAT = "goodbye, {name}"


def farewell(name: str = "world") -> str:
    """Return a farewell for ``name``; a blank name becomes ``world``.

    >>> farewell("Ada")
    'goodbye, Ada'
    """
    name = name.strip() or "world"
    return FAREWELL_FORMAT.format(name=name)
