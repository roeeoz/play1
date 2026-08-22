"""In-memory fake implementations of repository protocols for testing."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Sequence

from testbed_utils.reports.models import Claim, Customer


class FakeClaimsRepository:
    def __init__(self, claims: list[Claim] | None = None) -> None:
        self._claims: list[Claim] = claims or []

    def add(self, claim: Claim) -> None:
        self._claims.append(claim)

    def list(
        self,
        customer_id: str,
        date_from: date,
        date_to: date,
        statuses: Sequence[str],
    ) -> list[Claim]:
        return [
            c for c in self._claims
            if c.customer_id == customer_id
            and date_from <= c.submitted_at <= date_to
            and c.status in statuses
        ]

    def list_customers_with_claims(self, year: int) -> list[str]:
        jan1 = date(year, 1, 1)
        dec31 = date(year, 12, 31)
        seen: set[str] = set()
        result = []
        for c in self._claims:
            if jan1 <= c.submitted_at <= dec31 and c.customer_id not in seen:
                seen.add(c.customer_id)
                result.append(c.customer_id)
        return result


class FakeCustomerRepository:
    def __init__(self, customers: list[Customer] | None = None) -> None:
        self._customers: dict[str, Customer] = {
            c.customer_id: c for c in (customers or [])
        }

    def add(self, customer: Customer) -> None:
        self._customers[customer.customer_id] = customer

    def get(self, customer_id: str) -> Customer | None:
        return self._customers.get(customer_id)


def make_claim(
    *,
    claim_id: str = "C001",
    customer_id: str = "CU1",
    submitted_at: date = date(2024, 1, 15),
    category: str = "hospitalization",
    submitted_amount: Decimal = Decimal("1000.00"),
    reimbursed_amount: Decimal = Decimal("800.00"),
    status: str = "approved",
) -> Claim:
    return Claim(
        claim_id=claim_id,
        customer_id=customer_id,
        submitted_at=submitted_at,
        category=category,
        submitted_amount=submitted_amount,
        reimbursed_amount=reimbursed_amount,
        status=status,  # type: ignore[arg-type]
    )


def make_customer(
    *,
    customer_id: str = "CU1",
    full_name: str = "ישראל ישראלי",
    policy_numbers: list[str] | None = None,
) -> Customer:
    return Customer(
        customer_id=customer_id,
        full_name=full_name,
        policy_numbers=policy_numbers or ["POL-001"],
    )
