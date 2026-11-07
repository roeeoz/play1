"""Transaction model and validating CSV parser for the ledger.

A ledger is a UTF-8 CSV file whose header names the columns ``id``, ``date``,
``amount``, ``currency``, ``category`` and ``memo`` in any order. Parsing
returns the transactions in file order, or raises :class:`LedgerError` at the
first bad row with its physical line number (the header is line 1 and blank
lines count) and an exact reason.
"""

from __future__ import annotations

import csv
import datetime
import os
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Iterator

COLUMNS = ("id", "date", "amount", "currency", "category", "memo")
CURRENCIES = ("ILS", "USD", "EUR")

# ASCII-only on purpose: ``\d`` would accept full-width digits.
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_AMOUNT_RE = re.compile(r"[+-]?[0-9]+(?:\.([0-9]+))?")


@dataclass(frozen=True)
class Transaction:
    """One validated ledger row."""

    id: str
    date: datetime.date
    amount: Decimal
    currency: str
    category: str
    memo: str


class LedgerError(Exception):
    """A ledger row (or header) that cannot become a transaction."""

    def __init__(self, line: int, reason: str) -> None:
        super().__init__(line, reason)
        self.line = line
        self.reason = reason

    def __str__(self) -> str:
        return f"line {self.line}: {self.reason}"


def _strip_bom(lines: Iterable[str]) -> Iterator[str]:
    first = True
    for line in lines:
        if first:
            first = False
            if line.startswith("\ufeff"):
                line = line[1:]
        yield line


def _parse_date(text: str, line: int) -> datetime.date:
    if not _DATE_RE.fullmatch(text):
        raise LedgerError(line, f"date '{text}' is not YYYY-MM-DD")
    try:
        return datetime.date(int(text[0:4]), int(text[5:7]), int(text[8:10]))
    except ValueError:
        raise LedgerError(line, f"date '{text}' is not a calendar date") from None


def _parse_amount(text: str, line: int) -> Decimal:
    match = _AMOUNT_RE.fullmatch(text)
    if not match:
        raise LedgerError(line, f"amount '{text}' is not a number")
    fraction = match.group(1)
    if fraction is not None and len(fraction) > 2:
        raise LedgerError(line, f"amount '{text}' has more than 2 decimal places")
    amount = Decimal(text)
    if amount == 0:
        raise LedgerError(line, "amount must not be zero")
    return amount


def parse_lines(lines: Iterable[str]) -> list[Transaction]:
    """Parse ledger text given as an iterable of lines (e.g. a text stream)."""
    reader = csv.reader(_strip_bom(lines))
    index: dict[str, int] | None = None
    width = 0
    seen: dict[str, int] = {}
    transactions: list[Transaction] = []
    previous = 0
    for row in reader:
        start = previous + 1
        previous = reader.line_num
        fields = [field.strip() for field in row]
        if not any(fields):
            continue
        if index is None:
            index = {}
            for position, name in enumerate(fields):
                index.setdefault(name, position)
            missing = [name for name in COLUMNS if name not in index]
            if missing:
                raise LedgerError(1, f"missing column(s): {', '.join(missing)}")
            width = len(fields)
            continue
        if len(fields) != width:
            raise LedgerError(start, f"expected {width} fields, got {len(fields)}")
        values = {name: fields[index[name]] for name in COLUMNS}
        tid = values["id"]
        if not tid:
            raise LedgerError(start, "empty id")
        date = _parse_date(values["date"], start)
        amount = _parse_amount(values["amount"], start)
        currency = values["currency"]
        if currency not in CURRENCIES:
            raise LedgerError(start, f"unknown currency '{currency}'")
        if not values["category"]:
            raise LedgerError(start, "empty category")
        if tid in seen:
            raise LedgerError(
                start, f"duplicate id '{tid}' (first seen on line {seen[tid]})"
            )
        seen[tid] = start
        transactions.append(
            Transaction(
                id=tid,
                date=date,
                amount=amount,
                currency=currency,
                category=values["category"],
                memo=values["memo"],
            )
        )
    if index is None:
        raise LedgerError(1, "missing header")
    return transactions


def parse_csv(path: str | os.PathLike[str]) -> list[Transaction]:
    """Parse the ledger file at ``path`` (UTF-8, optional BOM)."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return parse_lines(handle)
