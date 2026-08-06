from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence, runtime_checkable

from testbed_utils.reports.models import Claim, Customer


@runtime_checkable
class ClaimsRepository(Protocol):
    def list(
        self,
        customer_id: str,
        date_from: date,
        date_to: date,
        statuses: Sequence[str],
    ) -> list[Claim]: ...

    def list_customers_with_claims(self, year: int) -> list[str]: ...


@runtime_checkable
class CustomerRepository(Protocol):
    def get(self, customer_id: str) -> Customer | None: ...
