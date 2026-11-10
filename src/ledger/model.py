"""Record types of the ledger: transactions and the line-numbered error."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from decimal import Decimal

CURRENCIES = ("ILS", "USD", "EUR")


@dataclass(frozen=True)
class Transaction:
    """One ledger row, with its amount kept exactly as written."""

    id: str
    date: datetime.date
    amount: Decimal
    currency: str
    category: str
    memo: str


class LedgerError(Exception):
    """A ledger row (or the header) that cannot be read, by physical line."""

    def __init__(self, line: int, reason: str) -> None:
        super().__init__(line, reason)
        self.line = line
        self.reason = reason

    def __str__(self) -> str:
        return f"line {self.line}: {self.reason}"
