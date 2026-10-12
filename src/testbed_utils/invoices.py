"""Invoice helpers — net-amount calculation for invoice lines."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Any


def invoice_net_amount(lines: Iterable[Any]) -> Decimal:
    """Return the net amount of an invoice: the sum of each line's ``amount``.

    Returns ``Decimal(0)`` when *lines* is empty.

    >>> from types import SimpleNamespace
    >>> invoice_net_amount([SimpleNamespace(amount=Decimal("10.00")),
    ...                     SimpleNamespace(amount=Decimal("5.50"))])
    Decimal('15.50')
    """
    total = Decimal(0)
    for line in lines:
        total += line.amount
    return total
