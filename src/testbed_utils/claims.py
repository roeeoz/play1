"""Health claim reimbursement domain types for F1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class Claim:
    claim_id: str
    policy_id: str
    service_date: date
    claim_amount: Decimal
    service_category: str


@dataclass(frozen=True)
class Policy:
    policy_id: str
    effective_date: date
    waiting_period_days: int
    covered_categories: tuple[str, ...]
    coverage_percentage: Decimal
    annual_deductible: Decimal
    annual_ceiling: Decimal


@dataclass(frozen=True)
class PolicyYearAccumulators:
    deductible_consumed: Decimal
    ceiling_consumed: Decimal


@dataclass(frozen=True)
class AuditInputs:
    claim_amount: Decimal
    service_date: date
    service_category: str
    effective_date: date
    waiting_period_days: int
    covered_categories: tuple[str, ...]
    coverage_percentage: Decimal
    annual_deductible: Decimal
    annual_ceiling: Decimal
    deductible_consumed_before: Decimal
    ceiling_consumed_before: Decimal


@dataclass(frozen=True)
class WaitingPeriodStep:
    rule: str
    result: Literal["PASSED", "FAILED"]
    detail: str


@dataclass(frozen=True)
class CoverageCheckStep:
    rule: str
    result: Literal["COVERED", "NOT_COVERED"]
    detail: str


@dataclass(frozen=True)
class DeductibleStep:
    rule: str
    deductible_applied: Decimal
    amount_after_deductible: Decimal


@dataclass(frozen=True)
class CoinsuranceStep:
    rule: str
    insurer_share: Decimal
    coverage_percentage: Decimal


@dataclass(frozen=True)
class AnnualCeilingStep:
    rule: str
    ceiling_applied: Decimal
    reimbursable_amount: Decimal


AuditStep = (
    WaitingPeriodStep
    | CoverageCheckStep
    | DeductibleStep
    | CoinsuranceStep
    | AnnualCeilingStep
)


@dataclass(frozen=True)
class AuditTrail:
    inputs: AuditInputs
    steps: tuple[AuditStep, ...]
    denial_reason: str | None


@dataclass(frozen=True)
class ReimbursementResult:
    claim_id: str
    policy_id: str
    reimbursable_amount: Decimal
    outcome: Literal["APPROVED", "DENIED"]
    updated_accumulators: PolicyYearAccumulators
    audit_trail: AuditTrail
