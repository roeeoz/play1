import dataclasses
from datetime import date
from decimal import Decimal


@dataclasses.dataclass(frozen=True)
class Claim:
    service_date: date
    claimed_amount: Decimal
    reimbursed_amount: Decimal
    status: str
    denial_reason: str | None = None


@dataclasses.dataclass(frozen=True)
class ReportData:
    customer_id: str
    year: int
    claims_in_year: tuple[Claim, ...]
    total_claimed: Decimal
    total_reimbursed: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "claims_in_year", tuple(self.claims_in_year))
