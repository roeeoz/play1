"""Error types and the fixed reason texts of the ledger parser.

Every reason text lives here so the parser and its callers (the report and the
command line) can never drift apart: callers print ``LedgerError.reason``
unchanged.
"""

from __future__ import annotations

# Header problems — always reported on line 1.
MISSING_HEADER = "missing header"
MISSING_COLUMN = "missing column '{name}'"
DUPLICATE_COLUMN = "duplicate column '{name}'"

# Row problems.
WRONG_FIELD_COUNT = "row has {n} fields, expected {m}"
EMPTY_ID = "empty id"
DUPLICATE_ID = "duplicate id '{value}' (first seen on line {line})"
INVALID_DATE = "invalid date '{value}'"
AMOUNT_NOT_A_NUMBER = "amount '{value}' is not a number"
AMOUNT_TOO_MANY_DECIMALS = "amount '{value}' has more than 2 decimal places"
UNKNOWN_CURRENCY = "unknown currency '{value}'"
EMPTY_CATEGORY = "empty category"

# CSV quoting that the strict reader cannot split into fields.
MALFORMED_RECORD = "malformed CSV record"


class LedgerError(Exception):
    """A data error at a physical line of the ledger.

    ``str(error)`` is ``"{line}: {reason}"``; ``line`` and ``reason`` are also
    available separately.
    """

    def __init__(self, line: int, reason: str) -> None:
        super().__init__(f"{line}: {reason}")
        self.line = line
        self.reason = reason

    def __reduce__(self):
        return (type(self), (self.line, self.reason))


class LedgerReadError(Exception):
    """The ledger file could not be opened or is not valid UTF-8.

    Deliberately not a :class:`LedgerError`: it has no line number. The
    underlying ``OSError`` or ``UnicodeDecodeError`` is chained as the cause.
    """
