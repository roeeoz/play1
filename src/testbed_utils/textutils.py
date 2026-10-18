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

    Accents are stripped via Unicode NFKD normalization.  Non-Latin characters
    (CJK, Cyrillic, etc.) are silently dropped because full transliteration
    would require a third-party library.

    >>> slugify("Hello, World!")
    'hello-world'
    >>> slugify("Héllo Wörld! Café résumé")
    'hello-world-cafe-resume'
    """
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    stripped = _SLUG_STRIP_RE.sub("", ascii_text).strip().lower()
    return _SLUG_COLLAPSE_RE.sub("-", stripped).strip("-")


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
