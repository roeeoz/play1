"""Parse a CSV ledger into exact ``Transaction`` values, failing on the first bad row."""

from __future__ import annotations

import csv
import datetime
import os
import re
from decimal import Decimal, InvalidOperation
from typing import Iterable

from ledger.model import CURRENCIES, LedgerError, Transaction

COLUMNS = ("id", "date", "amount", "currency", "category", "memo")

_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_NUMBER = re.compile(r"[+-]?[0-9]+(?:\.[0-9]+)?")


def parse_csv(path: str | os.PathLike) -> list[Transaction]:
    """Read the ledger file at ``path`` (UTF-8, optional BOM)."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return parse_lines(handle)


def parse_lines(lines: Iterable[str]) -> list[Transaction]:
    """Parse ledger text given as any iterable of lines, in file order."""
    reader = csv.reader(lines)
    header: dict[str, int] | None = None
    width = 0
    seen: dict[str, int] = {}
    transactions: list[Transaction] = []
    previous_end = 0
    for row in reader:
        line = previous_end + 1  # first physical line of this record
        previous_end = reader.line_num
        fields = [field.strip() for field in row]
        if not any(fields) and len(fields) <= 1:
            continue  # blank or whitespace-only line
        if header is None:
            if fields:
                fields[0] = fields[0].lstrip("\ufeff").strip()
            header = _read_header(fields, line)
            width = len(fields)
            continue
        transaction = _read_row(fields, header, width, line, seen)
        seen[transaction.id] = line
        transactions.append(transaction)
    if header is None:
        raise LedgerError(1, "missing header")
    return transactions


def _read_header(fields: list[str], line: int) -> dict[str, int]:
    index: dict[str, int] = {}
    for position, name in enumerate(fields):
        index.setdefault(name, position)
    missing = [name for name in COLUMNS if name not in index]
    if missing:
        raise LedgerError(line, f"missing column(s): {', '.join(missing)}")
    return {name: index[name] for name in COLUMNS}


def _read_row(
    fields: list[str],
    header: dict[str, int],
    width: int,
    line: int,
    seen: dict[str, int],
) -> Transaction:
    if len(fields) != width:
        raise LedgerError(line, f"expected {width} fields, got {len(fields)}")
    value = {name: fields[position] for name, position in header.items()}

    txn_id = value["id"]
    if not txn_id:
        raise LedgerError(line, "empty id")
    if txn_id in seen:
        raise LedgerError(
            line, f"duplicate id '{txn_id}' (first seen on line {seen[txn_id]})"
        )

    currency = value["currency"]
    category = value["category"]
    date = _read_date(value["date"], line)
    amount = _read_amount(value["amount"], line)
    if currency not in CURRENCIES:
        raise LedgerError(line, f"unknown currency '{currency}'")
    if not category:
        raise LedgerError(line, "empty category")
    return Transaction(txn_id, date, amount, currency, category, value["memo"])


def _read_date(text: str, line: int) -> datetime.date:
    if not _DATE.fullmatch(text):
        raise LedgerError(line, f"date '{text}' is not YYYY-MM-DD")
    year, month, day = (int(part) for part in text.split("-"))
    try:
        return datetime.date(year, month, day)
    except ValueError:
        raise LedgerError(line, f"date '{text}' is not a calendar date") from None


def _read_amount(text: str, line: int) -> Decimal:
    if not _NUMBER.fullmatch(text):
        raise LedgerError(line, f"amount '{text}' is not a number")
    try:
        amount = Decimal(text)
    except InvalidOperation:  # pragma: no cover - the pattern admits only decimals
        raise LedgerError(line, f"amount '{text}' is not a number") from None
    if amount.as_tuple().exponent < -2:
        raise LedgerError(line, f"amount '{text}' has more than 2 decimal places")
    if amount == 0:
        raise LedgerError(line, "amount must not be zero")
    return amount
