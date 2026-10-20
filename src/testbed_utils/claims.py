"""Health claim reimbursement calculation engine.

Pure, stateless adjudication function for insurance claim settlement.
All arithmetic is integer-only (cents). Coverage rate is expressed in
basis points (0–10 000) so no floating-point appears anywhere in the
computation path.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum


class ReasonCode(str, Enum):
    PAID = "PAID"
    WAITING_PERIOD = "WAITING_PERIOD"
    DEDUCTIBLE_NOT_MET = "DEDUCTIBLE_NOT_MET"
    CEILING_EXHAUSTED = "CEILING_EXHAUSTED"
    ZERO_BILLED = "ZERO_BILLED"


@dataclass(frozen=True)
class PolicyTerms:
    policy_id: str
    coverage_rate_bps: int  # basis points 0–10 000; 10 000 = 100 %
    annual_deductible_cents: int
    annual_ceiling_cents: int | None  # None = uncapped
    waiting_period_days: int
    coverage_start_date: date

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be non-empty")
        if not (0 <= self.coverage_rate_bps <= 10000):
            raise ValueError("coverage_rate_bps must be in the range 0–10 000 inclusive")


@dataclass(frozen=True)
class YTDAccumulators:
    policy_year: int
    deductible_paid_cents: int
    insurer_paid_cents: int


@dataclass(frozen=True)
class Claim:
    claim_id: str
    billed_amount_cents: int
    service_date: date


@dataclass(frozen=True)
class AdjudicationResult:
    claim_id: str
    policy_id: str
    service_date: date
    eligible_cents: int
    deductible_applied_cents: int
    post_deductible_cents: int
    coinsurance_cents: int
    insurer_pays_cents: int
    patient_pays_cents: int
    reason_code: ReasonCode
    updated_deductible_paid_cents: int
    updated_insurer_paid_cents: int
    policy_year: int


def calculate_reimbursement(
    policy: PolicyTerms,
    ytd: YTDAccumulators,
    claim: Claim,
) -> AdjudicationResult:
    """Adjudicate a single health claim against the given policy and YTD totals.

    Pure and stateless: no I/O, no global state, identical inputs produce
    identical outputs. All arithmetic is integer cents; coverage_rate_bps is
    the insurer share in basis points (e.g. 8 000 = 80 %).
    """
    # 1. Waiting period check
    coverage_effective_date = policy.coverage_start_date + timedelta(days=policy.waiting_period_days)
    if claim.service_date < coverage_effective_date:
        return AdjudicationResult(
            claim_id=claim.claim_id,
            policy_id=policy.policy_id,
            service_date=claim.service_date,
            eligible_cents=0,
            deductible_applied_cents=0,
            post_deductible_cents=0,
            coinsurance_cents=0,
            insurer_pays_cents=0,
            patient_pays_cents=0,
            reason_code=ReasonCode.WAITING_PERIOD,
            updated_deductible_paid_cents=ytd.deductible_paid_cents,
            updated_insurer_paid_cents=ytd.insurer_paid_cents,
            policy_year=claim.service_date.year,
        )

    # 2. Eligible amount (billed = allowed; no fee schedule)
    eligible_cents = claim.billed_amount_cents

    # 3. Deductible application
    remaining_deductible_cents = max(0, policy.annual_deductible_cents - ytd.deductible_paid_cents)
    deductible_applied_cents = min(remaining_deductible_cents, eligible_cents)
    post_deductible_cents = eligible_cents - deductible_applied_cents

    # 4. Coinsurance (integer floor via integer division)
    coinsurance_cents = (post_deductible_cents * policy.coverage_rate_bps) // 10000

    # 5. Annual ceiling cap
    if policy.annual_ceiling_cents is None:
        insurer_pays_cents = coinsurance_cents
    else:
        remaining_ceiling_cents = max(0, policy.annual_ceiling_cents - ytd.insurer_paid_cents)
        insurer_pays_cents = min(coinsurance_cents, remaining_ceiling_cents)

    # 6. Patient responsibility
    patient_pays_cents = eligible_cents - insurer_pays_cents

    # 7. Reason code — priority: ZERO_BILLED > DEDUCTIBLE_NOT_MET > CEILING_EXHAUSTED > PAID
    if claim.billed_amount_cents == 0:
        reason_code = ReasonCode.ZERO_BILLED
    elif insurer_pays_cents == 0 and deductible_applied_cents == eligible_cents:
        reason_code = ReasonCode.DEDUCTIBLE_NOT_MET
    elif (
        insurer_pays_cents == 0
        and policy.annual_ceiling_cents is not None
        and ytd.insurer_paid_cents >= policy.annual_ceiling_cents
    ):
        reason_code = ReasonCode.CEILING_EXHAUSTED
    else:
        reason_code = ReasonCode.PAID

    return AdjudicationResult(
        claim_id=claim.claim_id,
        policy_id=policy.policy_id,
        service_date=claim.service_date,
        eligible_cents=eligible_cents,
        deductible_applied_cents=deductible_applied_cents,
        post_deductible_cents=post_deductible_cents,
        coinsurance_cents=coinsurance_cents,
        insurer_pays_cents=insurer_pays_cents,
        patient_pays_cents=patient_pays_cents,
        reason_code=reason_code,
        updated_deductible_paid_cents=ytd.deductible_paid_cents + deductible_applied_cents,
        updated_insurer_paid_cents=ytd.insurer_paid_cents + insurer_pays_cents,
        policy_year=claim.service_date.year,
    )
