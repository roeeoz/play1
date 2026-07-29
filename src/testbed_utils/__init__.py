"""testbed_utils — a tiny, deliberately simple and genuinely extendable text/date utility library.

This package is a fixture for deterministic coding-phase testing of the Demerzel
agent. It exports text helpers (slugify, truncate, word_count) and date helpers
(days_between, is_weekend, humanize_delta). Keep modules small and well-tested;
canned tasks in README.md target this code.
"""

from testbed_utils.dateutils import days_between, humanize_delta, is_weekend
from testbed_utils.textutils import slugify, truncate, word_count

__all__ = [
    "days_between",
    "humanize_delta",
    "is_weekend",
    "slugify",
    "truncate",
    "word_count",
]

__version__ = "0.1.0"
