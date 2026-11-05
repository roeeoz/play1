"""CSV parsing of a ledger into exact ``Transaction`` values."""

from __future__ import annotations

import csv
import datetime
import os
import re
from decimal import Decimal, InvalidOperation
from typing import Iterable

from ledger.model import CURRENCIES, LedgerError, Transaction

COLUMNS = ("id", "date", "amount", "currency", "category", "memo")

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def parse_csv(path: str | os.PathLike) -> list[Transaction]:
    """Parse the ledger file at ``path`` (UTF-8, optional BOM)."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return parse_lines(handle)


def parse_lines(lines: Iterable[str]) -> list[Transaction]:
    """Parse ledger text given as an iterable of lines, in file order."""
    reader = csv.reader(lines)
    header: list[str] | None = None
    index: dict[str, int] = {}
    seen: dict[str, int] = {}
    transactions: list[Transaction] = []
    start = 1  # physical line on which the next record starts
    for row in reader:
        line = start
        start = reader.line_num + 1
        if not any(field.strip() for field in row):
            continue
        fields = [field.strip() for field in row]
        if header is None:
            header = fields
            missing = [name for name in COLUMNS if name not in header]
            if missing:
                raise LedgerError(line, f"missing column(s): {', '.join(missing)}")
            index = {name: header.index(name) for name in COLUMNS}
            continue
        transactions.append(_transaction(fields, len(header), index, seen, line))
    if header is None:
        raise LedgerError(1, "missing header")
    return transactions


def _transaction(
    fields: list[str],
    width: int,
    index: dict[str, int],
    seen: dict[str, int],
    line: int,
) -> Transaction:
    if len(fields) != width:
        raise LedgerError(line, f"expected {width} fields, got {len(fields)}")
    value = {name: fields[i] for name, i in index.items()}

    tid = value["id"]
    if not tid:
        raise LedgerError(line, "empty id")
    if tid in seen:
        raise LedgerError(
            line, f"duplicate id '{tid}' (first seen on line {seen[tid]})"
        )

    text = value["date"]
    if not _DATE_RE.fullmatch(text):
        raise LedgerError(line, f"date '{text}' is not YYYY-MM-DD")
    try:
        date = datetime.date.fromisoformat(text)
    except ValueError:
        raise LedgerError(line, f"date '{text}' is not a calendar date") from None

    amount = _amount(value["amount"], line)

    currency = value["currency"]
    if currency not in CURRENCIES:
        raise LedgerError(line, f"unknown currency '{currency}'")

    category = value["category"]
    if not category:
        raise LedgerError(line, "empty category")

    seen[tid] = line
    return Transaction(tid, date, amount, currency, category, value["memo"])


def _amount(text: str, line: int) -> Decimal:
    try:
        amount = Decimal(text)
    except InvalidOperation:
        amount = None
    if amount is None or not amount.is_finite():
        raise LedgerError(line, f"amount '{text}' is not a number")
    if amount.as_tuple().exponent < -2:
        raise LedgerError(line, f"amount '{text}' has more than 2 decimal places")
    if amount == 0:
        raise LedgerError(line, "amount must not be zero")
    return amount
