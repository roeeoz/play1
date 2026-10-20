"""Health claim reimbursement domain types and calculation engine for F1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
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


def calculate_reimbursement(
    claim: Claim,
    policy: Policy,
    accumulators: PolicyYearAccumulators,
) -> ReimbursementResult:
    """Pure function: adjudicate a health claim and return the reimbursable amount with a full audit trail."""
    ZERO = Decimal("0")

    audit_inputs = AuditInputs(
        claim_amount=claim.claim_amount,
        service_date=claim.service_date,
        service_category=claim.service_category,
        effective_date=policy.effective_date,
        waiting_period_days=policy.waiting_period_days,
        covered_categories=policy.covered_categories,
        coverage_percentage=policy.coverage_percentage,
        annual_deductible=policy.annual_deductible,
        annual_ceiling=policy.annual_ceiling,
        deductible_consumed_before=accumulators.deductible_consumed,
        ceiling_consumed_before=accumulators.ceiling_consumed,
    )

    steps: list[WaitingPeriodStep | CoverageCheckStep | DeductibleStep | CoinsuranceStep | AnnualCeilingStep] = []

    # Step 1: Waiting period check
    eligibility_date = policy.effective_date + timedelta(days=policy.waiting_period_days)
    if claim.service_date < eligibility_date:
        steps.append(WaitingPeriodStep(
            rule="WAITING_PERIOD",
            result="FAILED",
            detail=f"Service date {claim.service_date} is before eligibility date {eligibility_date}",
        ))
        return ReimbursementResult(
            claim_id=claim.claim_id,
            policy_id=claim.policy_id,
            reimbursable_amount=ZERO,
            outcome="DENIED",
            updated_accumulators=accumulators,
            audit_trail=AuditTrail(
                inputs=audit_inputs,
                steps=tuple(steps),
                denial_reason="WAITING_PERIOD_NOT_MET",
            ),
        )
    steps.append(WaitingPeriodStep(
        rule="WAITING_PERIOD",
        result="PASSED",
        detail=f"Service date {claim.service_date} is on or after eligibility date {eligibility_date}",
    ))

    # Step 2: Coverage check
    if claim.service_category not in policy.covered_categories:
        steps.append(CoverageCheckStep(
            rule="COVERAGE_CHECK",
            result="NOT_COVERED",
            detail=f"Service category '{claim.service_category}' is not in covered categories",
        ))
        return ReimbursementResult(
            claim_id=claim.claim_id,
            policy_id=claim.policy_id,
            reimbursable_amount=ZERO,
            outcome="DENIED",
            updated_accumulators=accumulators,
            audit_trail=AuditTrail(
                inputs=audit_inputs,
                steps=tuple(steps),
                denial_reason="SERVICE_NOT_COVERED",
            ),
        )
    steps.append(CoverageCheckStep(
        rule="COVERAGE_CHECK",
        result="COVERED",
        detail=f"Service category '{claim.service_category}' is covered",
    ))

    # Step 3: Deductible application
    remaining_deductible = max(ZERO, policy.annual_deductible - accumulators.deductible_consumed)
    deductible_applied = min(claim.claim_amount, remaining_deductible)
    amount_after_deductible = claim.claim_amount - deductible_applied
    steps.append(DeductibleStep(
        rule="DEDUCTIBLE",
        deductible_applied=deductible_applied,
        amount_after_deductible=amount_after_deductible,
    ))

    # Step 4: Coinsurance application
    insurer_share = amount_after_deductible * (policy.coverage_percentage / Decimal("100"))
    steps.append(CoinsuranceStep(
        rule="COINSURANCE",
        insurer_share=insurer_share,
        coverage_percentage=policy.coverage_percentage,
    ))

    # Step 5: Annual ceiling check
    remaining_ceiling = max(ZERO, policy.annual_ceiling - accumulators.ceiling_consumed)
    reimbursable_amount = min(insurer_share, remaining_ceiling)
    steps.append(AnnualCeilingStep(
        rule="ANNUAL_CEILING",
        ceiling_applied=reimbursable_amount,
        reimbursable_amount=reimbursable_amount,
    ))

    return ReimbursementResult(
        claim_id=claim.claim_id,
        policy_id=claim.policy_id,
        reimbursable_amount=reimbursable_amount,
        outcome="APPROVED",
        updated_accumulators=PolicyYearAccumulators(
            deductible_consumed=accumulators.deductible_consumed + deductible_applied,
            ceiling_consumed=accumulators.ceiling_consumed + reimbursable_amount,
        ),
        audit_trail=AuditTrail(
            inputs=audit_inputs,
            steps=tuple(steps),
            denial_reason=None,
        ),
    )
