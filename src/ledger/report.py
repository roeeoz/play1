"""Monthly report over parsed ledger transactions."""

from __future__ import annotations

import decimal
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Dict, Iterable, Mapping, Optional, Tuple

from ledger.parser import Transaction

# ILS per unit of each currency; fixed, never fetched.
RATES: Mapping[str, Decimal] = {
    "ILS": Decimal("1"),
    "USD": Decimal("3.70"),
    "EUR": Decimal("4.00"),
}

MONTH_RE = re.compile(r"[0-9]{4}-(0[1-9]|1[0-2])")

_CENT = Decimal("0.01")
_ZERO = Decimal("0.00")


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
    categories: Tuple[CategoryTotal, ...]

    def to_dict(self) -> dict:
        """JSON-ready form; amounts are strings so no precision is lost."""
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


def is_month(text: object) -> bool:
    """True when ``text`` is a ``YYYY-MM`` string with a month of 01-12."""
    return isinstance(text, str) and MONTH_RE.fullmatch(text) is not None


def _rate(rates: Mapping[str, object], currency: str) -> Decimal:
    if currency not in rates:
        raise ValueError(f"no rate for currency {currency!r}")
    rate = Decimal(rates[currency])
    if not rate > 0:
        raise ValueError(f"rate for {currency!r} must be positive")
    return rate


def _round(value: Decimal) -> Decimal:
    # Quantize once, half to even; adding 0.00 turns a signed -0.00 into 0.00.
    return value.quantize(_CENT, rounding=ROUND_HALF_EVEN) + _ZERO


def monthly_report(
    transactions: Iterable[Transaction],
    month: str,
    base: str = "ILS",
    top: Optional[int] = None,
    rates: Mapping[str, object] = RATES,
) -> MonthlyReport:
    """Total one calendar month by category in the ``base`` currency.

    Raises ValueError for invalid arguments (never LedgerError).
    """
    if not is_month(month):
        raise ValueError(f"month must be YYYY-MM, got {month!r}")
    if base not in rates:
        raise ValueError(f"unknown base currency {base!r}")
    if top is not None and (isinstance(top, bool) or not isinstance(top, int) or top < 1):
        raise ValueError(f"top must be an integer >= 1, got {top!r}")
    year, mon = int(month[:4]), int(month[5:])

    with decimal.localcontext() as ctx:
        ctx.prec = 28
        ctx.rounding = ROUND_HALF_EVEN
        base_rate = _rate(rates, base)
        income = expense = net = Decimal(0)
        count = 0
        sums: Dict[str, Decimal] = {}
        counts: Dict[str, int] = {}
        for tx in transactions:
            if (tx.date.year, tx.date.month) != (year, mon):
                continue
            value = tx.amount * _rate(rates, tx.currency) / base_rate
            count += 1
            net += value
            if value > 0:
                income += value
            else:
                expense += value
            sums[tx.category] = sums.get(tx.category, Decimal(0)) + value
            counts[tx.category] = counts.get(tx.category, 0) + 1

        categories = sorted(
            (CategoryTotal(name, _round(total), counts[name]) for name, total in sums.items()),
            key=lambda c: (-abs(c.total), c.name),
        )
        return MonthlyReport(
            month=month,
            base=base,
            count=count,
            income=_round(income),
            expense=_round(expense),
            net=_round(net),
            categories=tuple(categories[:top] if top is not None else categories),
        )
