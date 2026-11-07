"""Monthly report: fixed-rate conversion, category totals, half-even rounding."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Iterable, Mapping

from ledger.model import Transaction

# ILS per one unit of each currency; fixed, never fetched.
RATES = {"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}

_MONTH = re.compile(r"[0-9]{4}-(?:0[1-9]|1[0-2])")
_CENT = Decimal("0.01")


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
    categories: list[CategoryTotal]

    def to_dict(self) -> dict:
        """JSON-ready form; every amount is its two-place string."""
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


def is_month(text: str) -> bool:
    """True when ``text`` is ``YYYY-MM`` with a month of 01-12."""
    return isinstance(text, str) and _MONTH.fullmatch(text) is not None


def monthly_report(
    transactions: Iterable[Transaction],
    month: str,
    base: str = "ILS",
    rates: Mapping[str, Decimal] = RATES,
    top: int | None = None,
) -> MonthlyReport:
    """Total ``month``'s transactions by category in ``base`` currency."""
    if not is_month(month):
        raise ValueError(f"month {month!r} is not YYYY-MM")
    if base not in rates:
        raise ValueError(f"unknown base currency {base!r}")
    if top is not None and top < 1:
        raise ValueError(f"top must be at least 1, got {top}")

    year, mon = (int(part) for part in month.split("-"))
    income = expense = Decimal(0)
    sums: dict[str, Decimal] = defaultdict(Decimal)
    counts: dict[str, int] = defaultdict(int)
    count = 0
    for t in transactions:
        if (t.date.year, t.date.month) != (year, mon):
            continue
        value = t.amount * rates[t.currency] / rates[base]
        count += 1
        if value > 0:
            income += value
        else:
            expense += value
        sums[t.category] += value
        counts[t.category] += 1

    categories = sorted(
        (CategoryTotal(name, _round(total), counts[name]) for name, total in sums.items()),
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


def _round(value: Decimal) -> Decimal:
    rounded = value.quantize(_CENT, rounding=ROUND_HALF_EVEN)
    return rounded.copy_abs() if rounded.is_zero() else rounded
