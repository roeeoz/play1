"""Read a CSV ledger into transactions, stopping at the first malformed row.

``parse_csv`` decodes the whole file first and then shares ``parse_lines``'s
code path, so both entry points give the same transactions or the same error.
"""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Iterator

from ledger import errors, rules
from ledger.errors import LedgerError, LedgerReadError

COLUMNS = ("id", "date", "amount", "currency", "category", "memo")


@dataclass(frozen=True)
class Transaction:
    """One ledger row. A negative amount is an expense, a positive one income."""

    id: str
    date: date
    amount: Decimal
    currency: str
    category: str
    memo: str


def _prepared(lines: Iterable[str]) -> Iterator[str]:
    """Drop a leading BOM and give every line an ending."""
    first = True
    for line in lines:
        if first:
            first = False
            if line.startswith("\ufeff"):
                line = line[1:]
        if not line.endswith(("\n", "\r")):
            line += "\n"
        yield line


def _records(lines: Iterable[str]) -> Iterator[tuple[int, list[str]]]:
    """Yield ``(start_line, fields)`` for every non-blank CSV record."""
    reader = csv.reader(_prepared(lines), strict=True)
    while True:
        start = reader.line_num + 1
        try:
            record = next(reader)
        except StopIteration:
            return
        except csv.Error:
            raise LedgerError(start, errors.MALFORMED_RECORD) from None
        if not record or (len(record) == 1 and not record[0].strip()):
            continue
        yield start, record


def _header_positions(record: list[str]) -> dict[str, int]:
    names = [name.strip() for name in record]
    for column in COLUMNS:
        if column not in names:
            raise LedgerError(1, errors.MISSING_COLUMN.format(name=column))
    for column in COLUMNS:
        if names.count(column) > 1:
            raise LedgerError(1, errors.DUPLICATE_COLUMN.format(name=column))
    return {column: names.index(column) for column in COLUMNS}


def parse_lines(lines: Iterable[str]) -> list[Transaction]:
    """Parse ledger text given as lines, with or without their endings.

    Raises :class:`LedgerError` at the first malformed record; nothing is
    returned in that case.
    """
    records = _records(lines)
    header = next(records, None)
    if header is None:
        raise LedgerError(1, errors.MISSING_HEADER)
    positions = _header_positions(header[1])
    width = len(header[1])

    transactions: list[Transaction] = []
    seen: dict[str, int] = {}
    for line, record in records:
        if len(record) != width:
            raise LedgerError(line, errors.WRONG_FIELD_COUNT.format(n=len(record), m=width))
        field = {column: record[index].strip() for column, index in positions.items()}

        id_, reason = rules.check_id(field["id"])
        if reason is None and id_ in seen:
            reason = errors.DUPLICATE_ID.format(value=id_, line=seen[id_])
        if reason is None:
            when, reason = rules.check_date(field["date"])
        if reason is None:
            amount, reason = rules.check_amount(field["amount"])
        if reason is None:
            currency, reason = rules.check_currency(field["currency"])
        if reason is None:
            category, reason = rules.check_category(field["category"])
        if reason is not None:
            raise LedgerError(line, reason)

        seen[id_] = line
        transactions.append(
            Transaction(id_, when, amount, currency, category, field["memo"])
        )
    return transactions


def parse_csv(path: str | os.PathLike[str]) -> list[Transaction]:
    """Parse the UTF-8 ledger file at *path*.

    Raises :class:`LedgerReadError` when the file cannot be read or decoded —
    checked for the whole file before any row is validated — and
    :class:`LedgerError` at the first malformed record.
    """
    try:
        with open(path, encoding="utf-8-sig", newline="") as handle:
            content = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise LedgerReadError(f"cannot read ledger {os.fspath(path)!s}: {exc}") from exc
    return parse_lines(io.StringIO(content, newline=""))
