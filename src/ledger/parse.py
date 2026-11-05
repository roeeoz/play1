"""Parse a UTF-8 CSV ledger into exact ``Transaction`` values.

Every row is validated at this edge; the first bad row raises ``LedgerError``
carrying its physical line number (the header is line 1, blank lines count).
"""

from __future__ import annotations

import csv
import datetime
import os
import re
from collections.abc import Iterable
from decimal import Decimal

from ledger.model import CURRENCIES, LedgerError, Transaction

COLUMNS = ("id", "date", "amount", "currency", "category", "memo")

_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_AMOUNT_RE = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")


def parse_csv(path: str | os.PathLike[str]) -> list[Transaction]:
    """Read the ledger at *path* (UTF-8, optional BOM) and parse it."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return parse_lines(handle)


def parse_lines(lines: Iterable[str]) -> list[Transaction]:
    """Parse ledger text given as any iterable of lines, in file order."""
    reader = csv.reader(lines)
    header: list[str] | None = None
    header_line = 1
    index: dict[str, int] = {}
    seen: dict[str, int] = {}
    transactions: list[Transaction] = []

    while True:
        start = reader.line_num + 1
        try:
            row = next(reader)
        except StopIteration:
            break
        fields = [field.strip() for field in row]
        if not any(fields):
            continue
        if header is None:
            if fields[0].startswith("\ufeff"):
                fields[0] = fields[0].lstrip("\ufeff").strip()
            header, header_line = fields, start
            missing = [name for name in COLUMNS if name not in header]
            if missing:
                raise LedgerError(header_line, f"missing column(s): {', '.join(missing)}")
            index = {name: header.index(name) for name in COLUMNS}
            continue
        transaction = _row_to_transaction(fields, start, len(header), index, seen)
        seen[transaction.id] = start
        transactions.append(transaction)

    if header is None:
        raise LedgerError(1, "missing header")
    return transactions


def _row_to_transaction(
    fields: list[str],
    line: int,
    width: int,
    index: dict[str, int],
    seen: dict[str, int],
) -> Transaction:
    if len(fields) != width:
        raise LedgerError(line, f"expected {width} fields, got {len(fields)}")
    value = {name: fields[i] for name, i in index.items()}

    tx_id = value["id"]
    if not tx_id:
        raise LedgerError(line, "empty id")
    if tx_id in seen:
        raise LedgerError(line, f"duplicate id '{tx_id}' (first seen on line {seen[tx_id]})")

    return Transaction(
        id=tx_id,
        date=_parse_date(value["date"], line),
        amount=_parse_amount(value["amount"], line),
        currency=_parse_currency(value["currency"], line),
        category=_parse_category(value["category"], line),
        memo=value["memo"],
    )


def _parse_date(text: str, line: int) -> datetime.date:
    if not _DATE_RE.fullmatch(text):
        raise LedgerError(line, f"date '{text}' is not YYYY-MM-DD")
    try:
        return datetime.date(int(text[:4]), int(text[5:7]), int(text[8:]))
    except ValueError:
        raise LedgerError(line, f"date '{text}' is not a calendar date") from None


def _parse_amount(text: str, line: int) -> Decimal:
    if not _AMOUNT_RE.fullmatch(text):
        raise LedgerError(line, f"amount '{text}' is not a number")
    amount = Decimal(text)
    if amount.as_tuple().exponent < -2:
        raise LedgerError(line, f"amount '{text}' has more than 2 decimal places")
    if amount == 0:
        raise LedgerError(line, "amount must not be zero")
    return amount


def _parse_currency(text: str, line: int) -> str:
    if text not in CURRENCIES:
        raise LedgerError(line, f"unknown currency '{text}'")
    return text


def _parse_category(text: str, line: int) -> str:
    if not text:
        raise LedgerError(line, "empty category")
    return text
