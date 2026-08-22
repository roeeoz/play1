"""testbed_utils — a tiny, deliberately extendable text/date utility library.

This package exists as a fixture for deterministic coding-phase testing of the
Demerzel agent. Keep modules small and well-tested; canned tasks in README.md
target this code.
"""

from testbed_utils.dateutils import days_between, humanize_delta, is_weekend
from testbed_utils.pdfutils import extract_fields
from testbed_utils.textutils import slugify, truncate, word_count
from testbed_utils import reports  # noqa: F401 — make sub-package importable
from testbed_utils.reports.generator import generate_annual_claims_report
from testbed_utils.api import create_app

__all__ = [
    "days_between",
    "extract_fields",
    "generate_annual_claims_report",
    "create_app",
    "humanize_delta",
    "is_weekend",
    "reports",
    "slugify",
    "truncate",
    "word_count",
]

__version__ = "0.1.0"
