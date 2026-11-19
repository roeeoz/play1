"""Read and validate a CSV ledger.

A ledger is a UTF-8 CSV file whose header names the columns id, date, amount,
currency, category and memo in any order. Every data row becomes a
:class:`Transaction` with an exact ``Decimal`` amount, or parsing stops at the
first row that cannot, raising :class:`LedgerError` with the row's physical
line number and one fixed reason text per kind of error.

Rows are checked in a fixed order: field count, the first empty required field
(id, date, amount, currency, category), date, amount (pattern, then decimal
places), currency, duplicate id.
"""

from __future__ import annotations

import csv
import datetime
import os
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

REQUIRED = ("id", "date", "amount", "currency", "category", "memo")
NON_EMPTY = ("id", "date", "amount", "currency", "category")
CURRENCIES = frozenset({"ILS", "USD", "EUR"})

# ASCII-only patterns, checked before the stdlib parsers: Decimal() accepts
# "1e2", "NaN", "+5" and non-ASCII digits; date.fromisoformat accepts
# "20260301" and "2026-W10-1" on Python 3.11+.
_AMOUNT = re.compile(r"-?[0-9]+(?:\.([0-9]+))?")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")

# Large enough that an unterminated quote swallowing the rest of a file ends
# up as a field-count error instead of csv's "field larger than field limit";
# fits a C long on every platform.
_FIELD_SIZE_LIMIT = 2**31 - 1

_BOM = "\ufeff"


@dataclass(frozen=True)
class Transaction:
    """One validated ledger row; the strings are exactly as written."""

    id: str
    date: datetime.date
    amount: Decimal
    currency: str
    category: str
    memo: str


class LedgerError(Exception):
    """The first row of a ledger that cannot become a transaction.

    Deliberately not a ``ValueError``, so catching it never swallows a
    ``UnicodeDecodeError`` from reading the file.
    """

    def __init__(self, line: int, reason: str) -> None:
        super().__init__(f"{line}: {reason}")
        self.line = line
        self.reason = reason

    def __str__(self) -> str:
        return f"{self.line}: {self.reason}"


def _column_index(header: list[str], line: int) -> dict[str, int]:
    """Map each required column name to its index in *header*."""
    for name in REQUIRED:
        if name not in header:
            raise LedgerError(line, f"missing column '{name}'")
    seen: set[str] = set()
    for name in header:
        if name in REQUIRED:
            if name in seen:
                raise LedgerError(line, f"duplicate column '{name}'")
            seen.add(name)
    return {name: header.index(name) for name in REQUIRED}


def _parse_date(raw: str, line: int) -> datetime.date:
    if _DATE.fullmatch(raw):
        try:
            return datetime.date.fromisoformat(raw)
        except ValueError:
            pass
    raise LedgerError(line, f"invalid date '{raw}'")


def _parse_amount(raw: str, line: int) -> Decimal:
    match = _AMOUNT.fullmatch(raw)
    if match is None:
        raise LedgerError(line, f"invalid amount '{raw}'")
    decimals = match.group(1)
    if decimals is not None and len(decimals) > 2:
        raise LedgerError(line, f"amount '{raw}' has more than 2 decimal places")
    return Decimal(raw)


def _parse_row(
    row: list[str], line: int, width: int, columns: dict[str, int], seen_ids: dict[str, int]
) -> Transaction:
    """Validate one data row in the fixed check order."""
    if len(row) != width:
        raise LedgerError(line, f"expected {width} fields, got {len(row)}")
    values = {name: row[index] for name, index in columns.items()}
    for name in NON_EMPTY:
        if values[name] == "":
            raise LedgerError(line, f"missing {name}")
    date = _parse_date(values["date"], line)
    amount = _parse_amount(values["amount"], line)
    if values["currency"] not in CURRENCIES:
        raise LedgerError(line, f"unknown currency '{values['currency']}'")
    first_line = seen_ids.get(values["id"])
    if first_line is not None:
        raise LedgerError(
            line, f"duplicate id '{values['id']}' (first seen on line {first_line})"
        )
    seen_ids[values["id"]] = line
    return Transaction(
        id=values["id"],
        date=date,
        amount=amount,
        currency=values["currency"],
        category=values["category"],
        memo=values["memo"],
    )


def _strip_bom(lines: Iterable[str]) -> Iterable[str]:
    first = True
    for item in lines:
        if first and item.startswith(_BOM):
            item = item[len(_BOM):]
        first = False
        yield item


def parse_lines(lines: Iterable[str]) -> list[Transaction]:
    """Parse a ledger given as lines already in memory.

    *lines* yields one physical line per item, each with its line terminator
    as file iteration or ``str.splitlines(keepends=True)`` gives it. One
    leading BOM on the first line is ignored. Returns the transactions in file
    order, or raises :class:`LedgerError` at the first bad row.
    """
    csv.field_size_limit(_FIELD_SIZE_LIMIT)
    reader = csv.reader(_strip_bom(lines))
    columns: dict[str, int] | None = None
    width = 0
    seen_ids: dict[str, int] = {}
    transactions: list[Transaction] = []
    previous = 0
    for row in reader:
        line = previous + 1
        previous = reader.line_num
        if not row:
            continue
        if columns is None:
            columns = _column_index(row, line)
            width = len(row)
            continue
        transactions.append(_parse_row(row, line, width, columns, seen_ids))
    if columns is None:
        raise LedgerError(1, "missing header")
    return transactions


def parse_csv(path: str | os.PathLike[str]) -> list[Transaction]:
    """Parse the UTF-8 CSV ledger at *path*.

    ``OSError`` (missing or unreadable file) and ``UnicodeDecodeError``
    propagate unchanged; only data errors raise :class:`LedgerError`.
    """
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return parse_lines(handle)
