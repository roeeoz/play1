"""CSV ledger parsing: the ``Transaction`` model and its validated parser."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Iterator

COLUMNS = ("id", "date", "amount", "currency", "category", "memo")
CURRENCIES = ("ILS", "USD", "EUR")

_AMOUNT_RE = re.compile(r"[+-]?[0-9]+(?:\.([0-9]+))?")
_DATE_RE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")


@dataclass(frozen=True)
class Transaction:
    """One validated ledger row."""

    id: str
    date: date
    amount: Decimal
    currency: str
    category: str
    memo: str


class LedgerError(Exception):
    """A ledger data error, located by the physical line where its record starts."""

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


def _records(lines: Iterable[str]) -> Iterator[tuple[int, list[str]]]:
    """Yield ``(start_line, stripped_fields)`` for every non-blank CSV record."""
    reader = csv.reader(_strip_bom(lines))
    end = 0
    for row in reader:
        start, end = end + 1, reader.line_num
        fields = [field.strip() for field in row]
        if not fields or (len(fields) == 1 and not fields[0]):
            continue
        yield start, fields


def _parse_date(text: str, line: int) -> date:
    match = _DATE_RE.fullmatch(text)
    if match is None:
        raise LedgerError(line, f"date '{text}' is not YYYY-MM-DD")
    try:
        return date(*(int(group) for group in match.groups()))
    except ValueError:
        raise LedgerError(line, f"date '{text}' is not a calendar date") from None


def _parse_amount(text: str, line: int) -> Decimal:
    match = _AMOUNT_RE.fullmatch(text)
    if match is None:
        raise LedgerError(line, f"amount '{text}' is not a number")
    fraction = match.group(1)
    if fraction is not None and len(fraction) > 2:
        raise LedgerError(line, f"amount '{text}' has more than 2 decimal places")
    amount = Decimal(text)
    if amount.is_zero():
        raise LedgerError(line, "amount must not be zero")
    return amount


def _column_index(header: list[str], line: int) -> dict[str, int]:
    index: dict[str, int] = {}
    for position, name in enumerate(header):
        if name in COLUMNS:
            if name in index:
                raise LedgerError(line, f"duplicate column '{name}'")
            index[name] = position
    missing = [name for name in COLUMNS if name not in index]
    if missing:
        raise LedgerError(line, f"missing column(s): {', '.join(missing)}")
    return index


def parse_lines(lines: Iterable[str]) -> list[Transaction]:
    """Parse ledger CSV text given as any iterable of lines.

    Raises ``LedgerError`` at the first row that cannot become a transaction.
    """
    records = _records(lines)
    try:
        header_line, header = next(records)
    except StopIteration:
        raise LedgerError(1, "missing header") from None
    index = _column_index(header, header_line)

    transactions: list[Transaction] = []
    seen: dict[str, int] = {}
    for line, fields in records:
        if len(fields) != len(header):
            raise LedgerError(line, f"expected {len(header)} fields, got {len(fields)}")
        tx_id = fields[index["id"]]
        if not tx_id:
            raise LedgerError(line, "empty id")
        if tx_id in seen:
            raise LedgerError(line, f"duplicate id '{tx_id}' (first seen on line {seen[tx_id]})")
        tx_date = _parse_date(fields[index["date"]], line)
        amount = _parse_amount(fields[index["amount"]], line)
        currency = fields[index["currency"]]
        if currency not in CURRENCIES:
            raise LedgerError(line, f"unknown currency '{currency}'")
        category = fields[index["category"]]
        if not category:
            raise LedgerError(line, "empty category")
        seen[tx_id] = line
        transactions.append(
            Transaction(tx_id, tx_date, amount, currency, category, fields[index["memo"]])
        )
    return transactions


def parse_csv(path) -> list[Transaction]:
    """Parse the ledger file at ``path`` (UTF-8, optional BOM)."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return parse_lines(handle)
