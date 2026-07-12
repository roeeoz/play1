"""Small text helpers.

Deliberately simple and genuinely extendable — canned Demerzel tasks add
functions here (see README.md).
"""

from __future__ import annotations

import re
import unicodedata

_SLUG_STRIP_RE = re.compile(r"[^\w\s-]")
_SLUG_COLLAPSE_RE = re.compile(r"[-\s]+")


def slugify(text: str) -> str:
    """Convert *text* to a lowercase, ASCII, hyphen-separated slug.

    >>> slugify("Hello, World!")
    'hello-world'
    """
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    stripped = _SLUG_STRIP_RE.sub("", ascii_text).strip().lower()
    return _SLUG_COLLAPSE_RE.sub("-", stripped)


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate *text* to at most *max_length* characters, appending *suffix*.

    The suffix counts toward the limit. Text that already fits is returned
    unchanged.

    >>> truncate("hello world", 8)
    'hello...'
    """
    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return suffix[:max_length]
    return text[: max_length - len(suffix)] + suffix


def word_count(text: str) -> int:
    """Count whitespace-separated words in *text*.

    >>> word_count("the quick  brown fox")
    4
    """
    return len(text.split())


_ROMAN_NUMERALS = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]


def romanize(n: int) -> str:
    """Convert a positive integer *n* to its Roman numeral representation.

    >>> romanize(2024)
    'MMXXIV'
    >>> romanize(4)
    'IV'
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n must be an integer")
    if n < 1 or n > 3999:
        raise ValueError("n must be between 1 and 3999")
    result = []
    for value, numeral in _ROMAN_NUMERALS:
        while n >= value:
            result.append(numeral)
            n -= value
    return "".join(result)
