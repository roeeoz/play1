"""Invoice calculation helpers."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Any


def invoice_tax_total(lines: Iterable[Any]) -> Decimal:
    return sum((line.tax for line in lines), start=Decimal("0"))
