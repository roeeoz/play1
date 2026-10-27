"""Pure text helpers for the guestbook package."""

from __future__ import annotations


def word_count(text: str) -> int:
    """Count whitespace-separated words in *text*.

    >>> word_count("The quick brown fox")
    4
    """
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")
    return len(text.split())
