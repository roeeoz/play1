"""Monthly report over parsed ledger transactions.

Amounts are converted to the base currency at fixed rates (expressed in ILS
per unit) as ``amount * rates[currency] / rates[base]`` at full precision.
Every figure is summed exactly and then quantized once, independently, to two
places with ``ROUND_HALF_EVEN``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext
from typing import Iterable, Mapping

from ledger.parser import Transaction

RATES: Mapping[str, Decimal] = {
    "ILS": Decimal("1"),
    "USD": Decimal("3.70"),
    "EUR": Decimal("4.00"),
}

_MONTH_RE = re.compile(r"[0-9]{4}-(0[1-9]|1[0-2])")
_CENT = Decimal("0.01")
# The default context's precision (28 digits), pinned so a caller's global
# context can neither lower it nor be changed by us.
_CONTEXT = Context(prec=28, rounding=ROUND_HALF_EVEN)


def _check_month(month: object) -> str:
    """Return ``month`` if it is ``YYYY-MM`` with a month of 01-12."""
    if not isinstance(month, str) or not _MONTH_RE.fullmatch(month):
        raise ValueError(f"month {month!r} is not YYYY-MM")
    return month


@dataclass(frozen=True)
class CategoryTotal:
    """One category's total in the base currency and its transaction count."""

    name: str
    total: Decimal
    count: int


@dataclass(frozen=True)
class MonthlyReport:
    """Totals for one month in one base currency."""

    month: str
    base: str
    count: int
    income: Decimal
    expense: Decimal
    net: Decimal
    categories: list[CategoryTotal] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Plain-data form with amounts as strings, keys in a fixed order."""
        return {
            "month": self.month,
            "base": self.base,
            "count": self.count,
            "income": str(self.income),
            "expense": str(self.expense),
            "net": str(self.net),
            "categories": [
                {"name": c.name, "total": str(c.total), "count": c.count}
                for c in self.categories
            ],
        }


def monthly_report(
    transactions: Iterable[Transaction],
    month: str,
    base: str = "ILS",
    top: int | None = None,
    rates: Mapping[str, Decimal] = RATES,
) -> MonthlyReport:
    """Total ``month``'s transactions by category in ``base``.

    Raises ``ValueError`` for a malformed month, an unknown base or a ``top``
    below 1.
    """
    _check_month(month)
    if base not in rates:
        raise ValueError(f"unknown base currency {base!r}")
    if top is not None and top < 1:
        raise ValueError(f"top must be at least 1, got {top}")
    year, mon = int(month[:4]), int(month[5:7])

    with localcontext(_CONTEXT):
        income = expense = net = Decimal(0)
        totals: dict[str, Decimal] = {}
        counts: dict[str, int] = {}
        count = 0
        for tx in transactions:
            if (tx.date.year, tx.date.month) != (year, mon):
                continue
            value = tx.amount * rates[tx.currency] / rates[base]
            count += 1
            net += value
            if value > 0:
                income += value
            else:
                expense += value
            totals[tx.category] = totals.get(tx.category, Decimal(0)) + value
            counts[tx.category] = counts.get(tx.category, 0) + 1

        def cents(value: Decimal) -> Decimal:
            return value.quantize(_CENT, rounding=ROUND_HALF_EVEN)

        categories = sorted(
            (CategoryTotal(name, cents(total), counts[name])
             for name, total in totals.items()),
            key=lambda c: (-abs(c.total), c.name),
        )
        return MonthlyReport(
            month=month,
            base=base,
            count=count,
            income=cents(income),
            expense=cents(expense),
            net=cents(net),
            categories=categories[:top] if top is not None else categories,
        )
