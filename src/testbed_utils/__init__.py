"""testbed_utils — a tiny, deliberately extendable text/date utility library.

This package exists as a fixture for deterministic coding-phase testing of the
Demerzel agent. Keep modules small and well-tested; canned tasks in README.md
target this code.
"""

from testbed_utils.claims import (
    AdjudicationResult,
    Claim,
    PolicyTerms,
    ReasonCode,
    YTDAccumulators,
    calculate_reimbursement,
)
from testbed_utils.dateutils import days_between, humanize_delta, is_weekend
from testbed_utils.pdfutils import extract_fields
from testbed_utils.textutils import slugify, truncate, word_count

__all__ = [
    "AdjudicationResult",
    "Claim",
    "PolicyTerms",
    "ReasonCode",
    "YTDAccumulators",
    "calculate_reimbursement",
    "days_between",
    "extract_fields",
    "humanize_delta",
    "is_weekend",
    "slugify",
    "truncate",
    "word_count",
]

__version__ = "0.1.0"
