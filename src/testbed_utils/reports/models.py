from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

ClaimStatus = Literal["approved", "paid", "pending", "rejected"]


@dataclass
class Claim:
    claim_id: str
    customer_id: str
    submitted_at: date
    category: str
    submitted_amount: Decimal
    reimbursed_amount: Decimal
    status: ClaimStatus


@dataclass
class Customer:
    customer_id: str
    full_name: str
    policy_numbers: list[str]


@dataclass
class ReportRequest:
    customer_id: str
    year: int
    actor_id: str


@dataclass
class ReportConfig:
    logo_path: str
    disclaimer: str
    archive_base_path: str
    audit_log_path: str


class CustomerNotFound(Exception):
    pass
