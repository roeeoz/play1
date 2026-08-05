from datetime import date
from decimal import Decimal

from testbed_utils import (
    Claim,
    Policy,
    PolicyYearAccumulators,
    calculate_reimbursement,
)

# Synthetic fixture data — no real policy, claim, or personal records.

_BASE_POLICY = Policy(
    policy_id="POL-SYNTH-001",
    effective_date=date(2024, 1, 1),
    waiting_period_days=30,
    covered_categories=("DENTAL", "VISION", "GENERAL"),
    coverage_percentage=Decimal("80"),
    annual_deductible=Decimal("500"),
    annual_ceiling=Decimal("10000"),
)

_ZERO_ACCUMULATORS = PolicyYearAccumulators(
    deductible_consumed=Decimal("0"),
    ceiling_consumed=Decimal("0"),
)

# Service date after waiting period ends (2024-01-01 + 30 days = 2024-01-31)
_ELIGIBLE_DATE = date(2024, 2, 15)


class TestCalculateReimbursement:
    def test_waiting_period_not_met(self):
        # service_date before effective_date + 30 days
        claim = Claim(
            claim_id="CLM-SYNTH-001",
            policy_id="POL-SYNTH-001",
            service_date=date(2024, 1, 15),
            claim_amount=Decimal("200"),
            service_category="DENTAL",
        )
        result = calculate_reimbursement(claim, _BASE_POLICY, _ZERO_ACCUMULATORS)

        assert result.outcome == "DENIED"
        assert result.reimbursable_amount == Decimal("0")
        assert result.audit_trail.denial_reason == "WAITING_PERIOD_NOT_MET"
        assert len(result.audit_trail.steps) == 1
        assert result.audit_trail.steps[0].rule == "WAITING_PERIOD"
        assert result.audit_trail.steps[0].result == "FAILED"

    def test_service_not_covered(self):
        # service_category absent from covered_categories
        claim = Claim(
            claim_id="CLM-SYNTH-002",
            policy_id="POL-SYNTH-001",
            service_date=_ELIGIBLE_DATE,
            claim_amount=Decimal("300"),
            service_category="COSMETIC",
        )
        result = calculate_reimbursement(claim, _BASE_POLICY, _ZERO_ACCUMULATORS)

        assert result.outcome == "DENIED"
        assert result.reimbursable_amount == Decimal("0")
        assert result.audit_trail.denial_reason == "SERVICE_NOT_COVERED"
        assert len(result.audit_trail.steps) == 2
        assert result.audit_trail.steps[0].rule == "WAITING_PERIOD"
        assert result.audit_trail.steps[1].rule == "COVERAGE_CHECK"
        assert result.audit_trail.steps[1].result == "NOT_COVERED"

    def test_claim_fully_consumed_by_deductible(self):
        # claim_amount <= remaining_deductible → reimbursable_amount = 0
        claim = Claim(
            claim_id="CLM-SYNTH-003",
            policy_id="POL-SYNTH-001",
            service_date=_ELIGIBLE_DATE,
            claim_amount=Decimal("200"),
            service_category="DENTAL",
        )
        result = calculate_reimbursement(claim, _BASE_POLICY, _ZERO_ACCUMULATORS)

        assert result.outcome == "APPROVED"
        assert result.reimbursable_amount == Decimal("0")
        assert result.audit_trail.denial_reason is None
        assert len(result.audit_trail.steps) == 5
        deductible_step = result.audit_trail.steps[2]
        assert deductible_step.rule == "DEDUCTIBLE"
        assert deductible_step.deductible_applied == Decimal("200")
        assert deductible_step.amount_after_deductible == Decimal("0")

    def test_claim_partially_consumed_by_deductible(self):
        # claim_amount > remaining_deductible; ceiling not exceeded
        # deductible_consumed=400 → remaining=100; claim=600
        # deductible_applied=100, amount_after=500, insurer_share=500*80/100=400
        accumulators = PolicyYearAccumulators(
            deductible_consumed=Decimal("400"),
            ceiling_consumed=Decimal("0"),
        )
        claim = Claim(
            claim_id="CLM-SYNTH-004",
            policy_id="POL-SYNTH-001",
            service_date=_ELIGIBLE_DATE,
            claim_amount=Decimal("600"),
            service_category="DENTAL",
        )
        result = calculate_reimbursement(claim, _BASE_POLICY, accumulators)

        assert result.outcome == "APPROVED"
        assert result.reimbursable_amount == Decimal("400")
        assert result.audit_trail.denial_reason is None
        assert len(result.audit_trail.steps) == 5
        deductible_step = result.audit_trail.steps[2]
        assert deductible_step.deductible_applied == Decimal("100")
        assert deductible_step.amount_after_deductible == Decimal("500")

    def test_deductible_fully_consumed(self):
        # deductible_consumed == annual_deductible → deductible_applied = 0
        accumulators = PolicyYearAccumulators(
            deductible_consumed=Decimal("500"),
            ceiling_consumed=Decimal("0"),
        )
        claim = Claim(
            claim_id="CLM-SYNTH-005",
            policy_id="POL-SYNTH-001",
            service_date=_ELIGIBLE_DATE,
            claim_amount=Decimal("1000"),
            service_category="DENTAL",
        )
        result = calculate_reimbursement(claim, _BASE_POLICY, accumulators)

        assert result.outcome == "APPROVED"
        assert result.audit_trail.denial_reason is None
        assert len(result.audit_trail.steps) == 5
        deductible_step = result.audit_trail.steps[2]
        assert deductible_step.deductible_applied == Decimal("0")
        assert deductible_step.amount_after_deductible == Decimal("1000")
        # insurer_share = 1000 * 80/100 = 800
        assert result.reimbursable_amount == Decimal("800")

    def test_insurer_share_exceeds_remaining_ceiling(self):
        # remaining_ceiling = 300; insurer_share = 800 → capped at 300
        accumulators = PolicyYearAccumulators(
            deductible_consumed=Decimal("500"),
            ceiling_consumed=Decimal("9700"),
        )
        claim = Claim(
            claim_id="CLM-SYNTH-006",
            policy_id="POL-SYNTH-001",
            service_date=_ELIGIBLE_DATE,
            claim_amount=Decimal("1000"),
            service_category="DENTAL",
        )
        result = calculate_reimbursement(claim, _BASE_POLICY, accumulators)

        assert result.outcome == "APPROVED"
        assert result.reimbursable_amount == Decimal("300")
        assert result.audit_trail.denial_reason is None
        assert len(result.audit_trail.steps) == 5
        ceiling_step = result.audit_trail.steps[4]
        assert ceiling_step.rule == "ANNUAL_CEILING"
        assert ceiling_step.reimbursable_amount == Decimal("300")

    def test_annual_ceiling_exhausted(self):
        # ceiling_consumed == annual_ceiling → reimbursable_amount = 0; outcome still APPROVED
        accumulators = PolicyYearAccumulators(
            deductible_consumed=Decimal("500"),
            ceiling_consumed=Decimal("10000"),
        )
        claim = Claim(
            claim_id="CLM-SYNTH-007",
            policy_id="POL-SYNTH-001",
            service_date=_ELIGIBLE_DATE,
            claim_amount=Decimal("500"),
            service_category="DENTAL",
        )
        result = calculate_reimbursement(claim, _BASE_POLICY, accumulators)

        assert result.outcome == "APPROVED"
        assert result.reimbursable_amount == Decimal("0")
        assert result.audit_trail.denial_reason is None
        assert len(result.audit_trail.steps) == 5

    def test_zero_deductible_policy(self):
        # annual_deductible = 0 → deductible_applied = 0; full claim goes to coinsurance
        policy = Policy(
            policy_id="POL-SYNTH-002",
            effective_date=date(2024, 1, 1),
            waiting_period_days=0,
            covered_categories=("GENERAL",),
            coverage_percentage=Decimal("70"),
            annual_deductible=Decimal("0"),
            annual_ceiling=Decimal("5000"),
        )
        claim = Claim(
            claim_id="CLM-SYNTH-008",
            policy_id="POL-SYNTH-002",
            service_date=date(2024, 1, 1),
            claim_amount=Decimal("1000"),
            service_category="GENERAL",
        )
        result = calculate_reimbursement(claim, policy, _ZERO_ACCUMULATORS)

        assert result.outcome == "APPROVED"
        assert result.audit_trail.denial_reason is None
        assert len(result.audit_trail.steps) == 5
        deductible_step = result.audit_trail.steps[2]
        assert deductible_step.deductible_applied == Decimal("0")
        assert deductible_step.amount_after_deductible == Decimal("1000")
        # insurer_share = 1000 * 70/100 = 700
        assert result.reimbursable_amount == Decimal("700")

    def test_hundred_percent_coverage(self):
        # coverage_percentage = 100 → reimbursable_amount == amount_after_deductible (subject to ceiling)
        policy = Policy(
            policy_id="POL-SYNTH-003",
            effective_date=date(2024, 1, 1),
            waiting_period_days=0,
            covered_categories=("GENERAL",),
            coverage_percentage=Decimal("100"),
            annual_deductible=Decimal("0"),
            annual_ceiling=Decimal("50000"),
        )
        claim = Claim(
            claim_id="CLM-SYNTH-009",
            policy_id="POL-SYNTH-003",
            service_date=date(2024, 1, 1),
            claim_amount=Decimal("1500"),
            service_category="GENERAL",
        )
        result = calculate_reimbursement(claim, policy, _ZERO_ACCUMULATORS)

        assert result.outcome == "APPROVED"
        assert result.reimbursable_amount == Decimal("1500")
        assert result.audit_trail.denial_reason is None
        assert len(result.audit_trail.steps) == 5

    def test_zero_claim_amount(self):
        # claim_amount = 0 → reimbursable_amount = 0; accumulators unchanged in value
        claim = Claim(
            claim_id="CLM-SYNTH-010",
            policy_id="POL-SYNTH-001",
            service_date=_ELIGIBLE_DATE,
            claim_amount=Decimal("0"),
            service_category="DENTAL",
        )
        result = calculate_reimbursement(claim, _BASE_POLICY, _ZERO_ACCUMULATORS)

        assert result.outcome == "APPROVED"
        assert result.reimbursable_amount == Decimal("0")
        assert result.audit_trail.denial_reason is None
        assert len(result.audit_trail.steps) == 5
        assert result.updated_accumulators.deductible_consumed == _ZERO_ACCUMULATORS.deductible_consumed
        assert result.updated_accumulators.ceiling_consumed == _ZERO_ACCUMULATORS.ceiling_consumed
