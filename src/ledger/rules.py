"""Pure field rules for ledger rows.

Each rule takes an already-trimmed value and returns ``(cleaned, reason)``
where exactly one of the two is ``None`` — the same shape as
``guestbook.validation``. No float is ever created.
"""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal

from ledger import errors

CURRENCIES = ("ILS", "USD", "EUR")

# ASCII-only patterns: ``\d`` would accept non-ASCII digits, and
# ``date.fromisoformat`` accepts more forms on Python 3.11+ than on 3.10.
_AMOUNT_RE = re.compile(r"[+-]?[0-9]+(?:\.([0-9]+))?")
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def check_id(value: str) -> tuple[str | None, str | None]:
    if not value:
        return None, errors.EMPTY_ID
    return value, None


def check_date(value: str) -> tuple[date | None, str | None]:
    if _DATE_RE.fullmatch(value) is None:
        return None, errors.INVALID_DATE.format(value=value)
    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, errors.INVALID_DATE.format(value=value)


def check_amount(value: str) -> tuple[Decimal | None, str | None]:
    match = _AMOUNT_RE.fullmatch(value)
    if match is None:
        return None, errors.AMOUNT_NOT_A_NUMBER.format(value=value)
    decimals = match.group(1)
    if decimals is not None and len(decimals) > 2:
        return None, errors.AMOUNT_TOO_MANY_DECIMALS.format(value=value)
    return Decimal(value), None


def check_currency(value: str) -> tuple[str | None, str | None]:
    if value not in CURRENCIES:
        return None, errors.UNKNOWN_CURRENCY.format(value=value)
    return value, None


def check_category(value: str) -> tuple[str | None, str | None]:
    if not value:
        return None, errors.EMPTY_CATEGORY
    return value, None
