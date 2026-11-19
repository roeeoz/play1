"""Monthly report over parsed ledger transactions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext
from typing import Iterable, Mapping

from ledger.parser import Transaction

RATES: Mapping[str, Decimal] = {
    "ILS": Decimal("1"),
    "USD": Decimal("3.70"),
    "EUR": Decimal("4.00"),
}

MONTH_RE = re.compile(r"[0-9]{4}-(?:0[1-9]|1[0-2])")

_CENT = Decimal("0.01")
_ZERO = Decimal("0")


def _context() -> Context:
    return Context(prec=60, rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True)
class CategoryTotal:
    name: str
    total: Decimal
    count: int


@dataclass(frozen=True)
class Report:
    month: str
    base: str
    count: int
    income: Decimal
    expense: Decimal
    net: Decimal
    categories: list

    def to_dict(self) -> dict:
        """JSON-ready form: amounts as two-place strings, keys in a fixed order."""
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


def _round(value: Decimal) -> Decimal:
    """Quantize once to two places, half to even; never ``-0.00``."""
    rounded = value.quantize(_CENT, rounding=ROUND_HALF_EVEN)
    if rounded.is_zero():
        rounded = rounded.copy_abs()
    return rounded


def monthly_report(
    transactions: Iterable[Transaction],
    month: str,
    base: str = "ILS",
    top: int | None = None,
    rates: Mapping[str, Decimal] = RATES,
) -> Report:
    """Total ``month`` (``YYYY-MM``) by category in ``base``.

    Raises ``ValueError`` for a bad ``month``, an unknown ``base``, a ``top``
    below 1, or a transaction in the month whose currency has no rate.
    """
    if not isinstance(month, str) or MONTH_RE.fullmatch(month) is None:
        raise ValueError(f"month {month!r} is not YYYY-MM")
    if base not in rates:
        raise ValueError(f"unknown base currency {base!r}")
    if top is not None and (isinstance(top, bool) or not isinstance(top, int) or top < 1):
        raise ValueError(f"top must be an integer of at least 1, got {top!r}")
    year, mon = int(month[:4]), int(month[5:])

    count = 0
    income = expense = _ZERO
    sums: dict[str, Decimal] = {}
    counts: dict[str, int] = {}
    with localcontext(_context()):
        base_rate = Decimal(rates[base])
        for tx in transactions:
            if (tx.date.year, tx.date.month) != (year, mon):
                continue
            if tx.currency not in rates:
                raise ValueError(f"no rate for currency {tx.currency!r}")
            value = tx.amount * Decimal(rates[tx.currency]) / base_rate
            count += 1
            if value > 0:
                income += value
            else:
                expense += value
            sums[tx.category] = sums.get(tx.category, _ZERO) + value
            counts[tx.category] = counts.get(tx.category, 0) + 1

        categories = [CategoryTotal(name, _round(total), counts[name]) for name, total in sums.items()]
        categories.sort(key=lambda c: (-abs(c.total), c.name))
        if top is not None:
            categories = categories[:top]
        return Report(
            month=month,
            base=base,
            count=count,
            income=_round(income),
            expense=_round(expense),
            net=_round(income + expense),
            categories=categories,
        )
