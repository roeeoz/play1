"""Monthly report: fixed-rate conversion, category totals, half-even rounding."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Iterable, Mapping

from ledger.model import Transaction

# ILS per one unit of each currency; fixed, never fetched.
RATES: Mapping[str, Decimal] = {
    "ILS": Decimal("1"),
    "USD": Decimal("3.70"),
    "EUR": Decimal("4.00"),
}

_MONTH_RE = re.compile(r"(\d{4})-(0[1-9]|1[0-2])")
_CENT = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True)
class CategoryTotal:
    name: str
    total: Decimal
    count: int


@dataclass(frozen=True)
class MonthlyReport:
    month: str
    base: str
    count: int
    income: Decimal
    expense: Decimal
    net: Decimal
    categories: list[CategoryTotal] = field(default_factory=list)

    def to_dict(self) -> dict:
        """JSON-ready shape; every amount is its two-place string."""
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
    rates: Mapping[str, Decimal] = RATES,
    top: int | None = None,
) -> MonthlyReport:
    """Total one ``YYYY-MM`` month by category in ``base`` currency."""
    match = _MONTH_RE.fullmatch(month) if isinstance(month, str) else None
    if match is None:
        raise ValueError(f"month {month!r} is not YYYY-MM")
    if base not in rates:
        raise ValueError(f"unknown base currency {base!r}")
    if top is not None and top < 1:
        raise ValueError(f"top must be at least 1, got {top}")
    year, mon = int(match.group(1)), int(match.group(2))

    income = expense = Decimal(0)
    totals: dict[str, Decimal] = {}
    counts: dict[str, int] = {}
    count = 0
    for tx in transactions:
        if tx.date.year != year or tx.date.month != mon:
            continue
        value = tx.amount * Decimal(rates[tx.currency]) / Decimal(rates[base])
        count += 1
        if value > 0:
            income += value
        else:
            expense += value
        totals[tx.category] = totals.get(tx.category, Decimal(0)) + value
        counts[tx.category] = counts.get(tx.category, 0) + 1

    categories = sorted(
        (CategoryTotal(name, _round(total), counts[name]) for name, total in totals.items()),
        key=lambda c: (-abs(c.total), c.name),
    )
    if top is not None:
        categories = categories[:top]
    return MonthlyReport(
        month=month,
        base=base,
        count=count,
        income=_round(income),
        expense=_round(expense),
        net=_round(income + expense),
        categories=categories,
    )
