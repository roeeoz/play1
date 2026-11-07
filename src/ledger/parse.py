"""Parse a CSV ledger into ``Transaction`` values, validating every row."""

from __future__ import annotations

import csv
import datetime
import re
from decimal import Decimal, InvalidOperation
from os import PathLike
from typing import Iterable

from .model import CURRENCIES, LedgerError, Transaction

COLUMNS = ("id", "date", "amount", "currency", "category", "memo")

_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_AMOUNT_RE = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")


def parse_csv(path: str | PathLike[str]) -> list[Transaction]:
    """Read the ledger at ``path`` (UTF-8, optional BOM) and parse it."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return parse_lines(handle)


def parse_lines(lines: Iterable[str]) -> list[Transaction]:
    """Parse ledger text given as an iterable of lines, in file order.

    Raises ``LedgerError`` at the first bad header or row, carrying the
    physical line number (header = 1, blank lines count).
    """
    reader = csv.reader(lines)
    index: dict[str, int] | None = None
    width = 0
    seen: dict[str, int] = {}
    transactions: list[Transaction] = []
    end = 0  # physical line the previous record ended on
    for raw in reader:
        line = end + 1  # a record starts on the line after the previous one
        end = reader.line_num
        fields = [field.strip() for field in raw]
        if not any(fields):
            continue  # blank or whitespace-only line
        if index is None:
            index = _read_header(fields, line)
            width = len(fields)
            continue
        if len(fields) != width:
            raise LedgerError(line, f"expected {width} fields, got {len(fields)}")
        transaction = _read_row({name: fields[i] for name, i in index.items()}, line, seen)
        seen[transaction.id] = line
        transactions.append(transaction)
    if index is None:
        raise LedgerError(1, "missing header")
    return transactions


def _read_header(fields: list[str], line: int) -> dict[str, int]:
    missing = [name for name in COLUMNS if name not in fields]
    if missing:
        raise LedgerError(line, f"missing column(s): {', '.join(missing)}")
    return {name: fields.index(name) for name in COLUMNS}


def _read_row(row: dict[str, str], line: int, seen: dict[str, int]) -> Transaction:
    tid = row["id"]
    if not tid:
        raise LedgerError(line, "empty id")
    if tid in seen:
        raise LedgerError(line, f"duplicate id '{tid}' (first seen on line {seen[tid]})")
    date = _read_date(row["date"], line)
    amount = _read_amount(row["amount"], line)
    currency = row["currency"]
    if currency not in CURRENCIES:
        raise LedgerError(line, f"unknown currency '{currency}'")
    category = row["category"]
    if not category:
        raise LedgerError(line, "empty category")
    return Transaction(tid, date, amount, currency, category, row["memo"])


def _read_date(text: str, line: int) -> datetime.date:
    if not _DATE_RE.fullmatch(text):
        raise LedgerError(line, f"date '{text}' is not YYYY-MM-DD")
    try:
        return datetime.date(int(text[0:4]), int(text[5:7]), int(text[8:10]))
    except ValueError:
        raise LedgerError(line, f"date '{text}' is not a calendar date") from None


def _read_amount(text: str, line: int) -> Decimal:
    if not _AMOUNT_RE.fullmatch(text):
        raise LedgerError(line, f"amount '{text}' is not a number")
    try:
        amount = Decimal(text)
    except InvalidOperation:  # pragma: no cover - the pattern admits only numbers
        raise LedgerError(line, f"amount '{text}' is not a number") from None
    exponent = amount.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -2:
        raise LedgerError(line, f"amount '{text}' has more than 2 decimal places")
    if amount == 0:
        raise LedgerError(line, "amount must not be zero")
    return amount
