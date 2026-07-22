"""testbed_utils — a tiny, deliberately extendable text/date utility library
used as a fixture for deterministic coding-phase testing of the Demerzel agent;
exports text helpers (slugify, truncate, word_count) and date helpers
(days_between, humanize_delta, is_weekend).
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
