"""Record types of the ledger: a transaction and the error a bad row raises."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from decimal import Decimal

CURRENCIES = ("ILS", "USD", "EUR")


@dataclass(frozen=True)
class Transaction:
    """One ledger row; ``amount`` is exact, positive for income, negative for expense."""

    id: str
    date: datetime.date
    amount: Decimal
    currency: str
    category: str
    memo: str


class LedgerError(Exception):
    """A ledger row (or the header) that cannot be read, at a physical line number."""

    def __init__(self, line: int, reason: str) -> None:
        super().__init__(line, reason)
        self.line = line
        self.reason = reason

    def __str__(self) -> str:
        return f"line {self.line}: {self.reason}"
