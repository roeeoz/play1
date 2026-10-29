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


def truncate(text: str, n: int) -> str:
    """Truncate *text* to at most *n* characters using a Unicode ellipsis.

    Returns *text* unchanged when it already fits within *n* characters.
    Returns an empty string when *n* is zero or negative.

    >>> truncate("hello world", 8)
    'hello w…'
    """
    if n <= 0:
        return ""
    if len(text) <= n:
        return text
    return text[: n - 1] + "…"


def word_count(text: str) -> int:
    """Count whitespace-separated words in *text*.

    >>> word_count("the quick  brown fox")
    4
    """
    return len(text.split())
