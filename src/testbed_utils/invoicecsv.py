"""Build invoice-export CSV text from a list of invoice records."""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable, Mapping
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

_HEADER = ("number", "customer", "date", "amount", "status")
_CENTS = Decimal("0.01")


def _format_date(value: date) -> str:
    """Return *value* as YYYY-MM-DD; a datetime contributes only its calendar date."""
    if isinstance(value, datetime):
        value = value.date()
    return value.isoformat()


def _format_amount(value: Decimal | int | float) -> str:
    """Return *value* with exactly two decimals, rounded half-up, no symbols."""
    return str(Decimal(str(value)).quantize(_CENTS, rounding=ROUND_HALF_UP))


def invoices_to_csv(invoices: Iterable[Mapping[str, Any]]) -> str:
    """Return CSV text for *invoices*: a fixed header, then one row per invoice.

    Each invoice is a mapping with keys ``number``, ``customer``, ``date``
    (a :class:`datetime.date`), ``amount`` (``Decimal``, ``int`` or ``float``)
    and ``status``. Dates are rendered as ISO 8601, amounts with two decimals
    rounded half-up, and fields containing a comma are double-quoted. Every
    line ends with a newline; an empty list yields the header line only.

    >>> from datetime import date
    >>> from decimal import Decimal
    >>> print(invoices_to_csv([]), end="")
    number,customer,date,amount,status
    >>> print(invoices_to_csv([{
    ...     "number": "INV-1", "customer": "Acme, Inc.",
    ...     "date": date(2026, 3, 1), "amount": Decimal("1250.5"), "status": "paid",
    ... }]), end="")
    number,customer,date,amount,status
    INV-1,"Acme, Inc.",2026-03-01,1250.50,paid
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(_HEADER)
    for invoice in invoices:
        writer.writerow(
            (
                str(invoice["number"]),
                str(invoice["customer"]),
                _format_date(invoice["date"]),
                _format_amount(invoice["amount"]),
                str(invoice["status"]),
            )
        )
    return buffer.getvalue()
