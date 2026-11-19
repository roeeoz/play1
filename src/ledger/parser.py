"""Transaction model and validating CSV parser for a ledger file."""

from __future__ import annotations

import csv
import datetime
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Iterator, List

COLUMNS = ("id", "date", "amount", "currency", "category", "memo")
CURRENCIES = ("ILS", "USD", "EUR")

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
    """A ledger row (or the header) that cannot be parsed."""

    def __init__(self, line: int, reason: str) -> None:
        super().__init__(line, reason)
        self.line = line
        self.reason = reason

    def __str__(self) -> str:
        return f"line {self.line}: {self.reason}"


class _LineCounter:
    """Feeds lines to csv.reader while counting the physical lines consumed."""

    def __init__(self, lines: Iterable[str]) -> None:
        self.count = 0
        self._lines = iter(lines)

    def __iter__(self) -> Iterator[str]:
        for line in self._lines:
            if self.count == 0 and line.startswith("\ufeff"):
                line = line[1:]
            self.count += 1
            yield line


def _is_blank(record: List[str]) -> bool:
    return not record or (len(record) == 1 and not record[0].strip())


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
    value = Decimal(text)
    if value == 0:
        raise LedgerError(line, "amount must not be zero")
    return value


def _read_header(record: List[str], line: int) -> dict:
    names = [name.strip() for name in record]
    index = {}
    for position, name in enumerate(names):
        if name in index:
            raise LedgerError(line, f"duplicate column '{name}'")
        index[name] = position
    missing = [name for name in COLUMNS if name not in index]
    if missing:
        raise LedgerError(line, f"missing column(s): {', '.join(missing)}")
    return index


def parse_lines(lines: Iterable[str]) -> List[Transaction]:
    """Parse ledger text given as an iterable of lines.

    Raises LedgerError at the first bad row, carrying its physical start line.
    """
    counter = _LineCounter(lines)
    reader = csv.reader(counter, strict=True)
    header = None
    width = 0
    seen: dict = {}
    transactions: List[Transaction] = []
    while True:
        start = counter.count + 1
        try:
            record = next(reader)
        except StopIteration:
            break
        except csv.Error as exc:
            raise LedgerError(start, f"malformed CSV: {exc}") from None
        if _is_blank(record):
            continue
        if header is None:
            header = _read_header(record, start)
            width = len(record)
            continue
        if len(record) != width:
            raise LedgerError(start, f"expected {width} fields, got {len(record)}")
        field = {name: record[header[name]].strip() for name in COLUMNS}
        tx_id = field["id"]
        if not tx_id:
            raise LedgerError(start, "empty id")
        if tx_id in seen:
            raise LedgerError(
                start, f"duplicate id '{tx_id}' (first seen on line {seen[tx_id]})"
            )
        date = _parse_date(field["date"], start)
        amount = _parse_amount(field["amount"], start)
        currency = field["currency"]
        if currency not in CURRENCIES:
            raise LedgerError(start, f"unknown currency '{currency}'")
        if not field["category"]:
            raise LedgerError(start, "empty category")
        seen[tx_id] = start
        transactions.append(
            Transaction(
                id=tx_id,
                date=date,
                amount=amount,
                currency=currency,
                category=field["category"],
                memo=field["memo"],
            )
        )
    if header is None:
        raise LedgerError(1, "missing header")
    return transactions


def parse_csv(path) -> List[Transaction]:
    """Parse the ledger file at ``path`` (UTF-8, optional BOM)."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return parse_lines(handle)
