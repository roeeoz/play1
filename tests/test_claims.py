"""Unit tests for the health claim reimbursement calculation engine.

All 11 mandatory adjudication scenarios are covered, plus boundary-value
cases. Every test asserts every field of the AdjudicationResult.
"""

from datetime import date, timedelta

import pytest

from testbed_utils import (
    AdjudicationResult,
    Claim,
    PolicyTerms,
    ReasonCode,
    YTDAccumulators,
    calculate_reimbursement,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

COVERAGE_START = date(2026, 1, 1)


def make_policy(
    *,
    policy_id: str = "POL-001",
    coverage_rate_bps: int = 8000,
    annual_deductible_cents: int = 100_000,
    annual_ceiling_cents: int | None = 500_000,
    waiting_period_days: int = 0,
    coverage_start_date: date = COVERAGE_START,
) -> PolicyTerms:
    return PolicyTerms(
        policy_id=policy_id,
        coverage_rate_bps=coverage_rate_bps,
        annual_deductible_cents=annual_deductible_cents,
        annual_ceiling_cents=annual_ceiling_cents,
        waiting_period_days=waiting_period_days,
        coverage_start_date=coverage_start_date,
    )


def make_ytd(
    *,
    policy_year: int = 2026,
    deductible_paid_cents: int = 0,
    insurer_paid_cents: int = 0,
) -> YTDAccumulators:
    return YTDAccumulators(
        policy_year=policy_year,
        deductible_paid_cents=deductible_paid_cents,
        insurer_paid_cents=insurer_paid_cents,
    )


def make_claim(
    *,
    claim_id: str = "CLM-001",
    billed_amount_cents: int = 50_000,
    service_date: date = date(2026, 6, 15),
) -> Claim:
    return Claim(
        claim_id=claim_id,
        billed_amount_cents=billed_amount_cents,
        service_date=service_date,
    )


# ---------------------------------------------------------------------------
# Test: full deductible (AC spec #2 / WI t2 AC #2)
# ---------------------------------------------------------------------------

class TestFullDeductible:
    def test_all_fields(self):
        policy = make_policy(annual_deductible_cents=100_000, coverage_rate_bps=8000)
        ytd = make_ytd(deductible_paid_cents=0)
        claim = make_claim(billed_amount_cents=80_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.claim_id == "CLM-001"
        assert r.policy_id == "POL-001"
        assert r.service_date == date(2026, 6, 15)
        assert r.eligible_cents == 80_000
        assert r.deductible_applied_cents == 80_000
        assert r.post_deductible_cents == 0
        assert r.coinsurance_cents == 0
        assert r.insurer_pays_cents == 0
        assert r.patient_pays_cents == 80_000
        assert r.reason_code == ReasonCode.DEDUCTIBLE_NOT_MET
        assert r.updated_deductible_paid_cents == 80_000
        assert r.updated_insurer_paid_cents == 0
        assert r.policy_year == 2026

    def test_billed_exactly_equals_deductible(self):
        policy = make_policy(annual_deductible_cents=100_000)
        ytd = make_ytd(deductible_paid_cents=0)
        claim = make_claim(billed_amount_cents=100_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.deductible_applied_cents == 100_000
        assert r.insurer_pays_cents == 0
        assert r.reason_code == ReasonCode.DEDUCTIBLE_NOT_MET
        assert r.updated_deductible_paid_cents == 100_000
        assert r.updated_insurer_paid_cents == 0


# ---------------------------------------------------------------------------
# Test: partial deductible (AC spec #3 / WI t2 AC #3)
# ---------------------------------------------------------------------------

class TestPartialDeductible:
    def test_all_fields(self):
        # 60k of 100k deductible already met; billed 100k
        # remaining deductible = 40k, applied = 40k
        # post_deductible = 60k, coinsurance = floor(60000*8000/10000) = 48000
        policy = make_policy(annual_deductible_cents=100_000, coverage_rate_bps=8000, annual_ceiling_cents=None)
        ytd = make_ytd(deductible_paid_cents=60_000)
        claim = make_claim(billed_amount_cents=100_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.eligible_cents == 100_000
        assert r.deductible_applied_cents == 40_000
        assert r.post_deductible_cents == 60_000
        assert r.coinsurance_cents == 48_000
        assert r.insurer_pays_cents == 48_000
        assert r.patient_pays_cents == 52_000
        assert r.reason_code == ReasonCode.PAID
        assert r.updated_deductible_paid_cents == 100_000
        assert r.updated_insurer_paid_cents == 48_000
        assert r.policy_year == 2026


# ---------------------------------------------------------------------------
# Test: zero deductible / deductible already fully paid (AC spec #3 / WI t2 AC #4)
# ---------------------------------------------------------------------------

class TestDeductibleAlreadyMet:
    def test_all_fields(self):
        policy = make_policy(annual_deductible_cents=100_000, coverage_rate_bps=8000, annual_ceiling_cents=None)
        ytd = make_ytd(deductible_paid_cents=100_000)
        claim = make_claim(billed_amount_cents=100_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.eligible_cents == 100_000
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 100_000
        assert r.coinsurance_cents == 80_000
        assert r.insurer_pays_cents == 80_000
        assert r.patient_pays_cents == 20_000
        assert r.reason_code == ReasonCode.PAID
        assert r.updated_deductible_paid_cents == 100_000
        assert r.updated_insurer_paid_cents == 80_000
        assert r.policy_year == 2026

    def test_zero_deductible_policy(self):
        policy = make_policy(annual_deductible_cents=0, coverage_rate_bps=8000, annual_ceiling_cents=None)
        ytd = make_ytd(deductible_paid_cents=0)
        claim = make_claim(billed_amount_cents=50_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 50_000
        assert r.insurer_pays_cents == 40_000
        assert r.reason_code == ReasonCode.PAID


# ---------------------------------------------------------------------------
# Test: ceiling — claim that hits exactly to the ceiling (WI t2 AC #5)
# ---------------------------------------------------------------------------

class TestCeilingPartiallyUsed:
    def test_claim_brings_total_exactly_to_ceiling(self):
        # Annual ceiling 500k; insurer already paid 460k; claim coinsurance = 40k
        # → insurer pays exactly 40k (remaining ceiling), reason PAID
        policy = make_policy(
            annual_deductible_cents=0,
            coverage_rate_bps=8000,
            annual_ceiling_cents=500_000,
        )
        ytd = make_ytd(deductible_paid_cents=0, insurer_paid_cents=460_000)
        claim = make_claim(billed_amount_cents=50_000)  # coinsurance = 40k

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.coinsurance_cents == 40_000
        assert r.insurer_pays_cents == 40_000
        assert r.patient_pays_cents == 10_000
        assert r.reason_code == ReasonCode.PAID
        assert r.updated_insurer_paid_cents == 500_000
        assert r.eligible_cents == 50_000
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 50_000
        assert r.policy_year == 2026


# ---------------------------------------------------------------------------
# Test: ceiling exhausted (AC spec #4 / WI t2 AC #6)
# ---------------------------------------------------------------------------

class TestCeilingExhausted:
    def test_all_fields(self):
        policy = make_policy(annual_deductible_cents=0, coverage_rate_bps=8000, annual_ceiling_cents=500_000)
        ytd = make_ytd(insurer_paid_cents=500_000)
        claim = make_claim(billed_amount_cents=100_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.eligible_cents == 100_000
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 100_000
        assert r.coinsurance_cents == 80_000
        assert r.insurer_pays_cents == 0
        assert r.patient_pays_cents == 100_000
        assert r.reason_code == ReasonCode.CEILING_EXHAUSTED
        assert r.updated_insurer_paid_cents == 500_000
        assert r.updated_deductible_paid_cents == 0
        assert r.policy_year == 2026

    def test_insurer_paid_exceeds_ceiling(self):
        policy = make_policy(annual_deductible_cents=0, coverage_rate_bps=8000, annual_ceiling_cents=500_000)
        ytd = make_ytd(insurer_paid_cents=600_000)
        claim = make_claim(billed_amount_cents=50_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.insurer_pays_cents == 0
        assert r.reason_code == ReasonCode.CEILING_EXHAUSTED


# ---------------------------------------------------------------------------
# Test: uncapped policy (AC spec #5 / WI t2 AC #7)
# ---------------------------------------------------------------------------

class TestUncappedPolicy:
    def test_all_fields_large_ytd(self):
        policy = make_policy(
            annual_deductible_cents=0,
            coverage_rate_bps=8000,
            annual_ceiling_cents=None,
        )
        ytd = make_ytd(insurer_paid_cents=999_999_999)
        claim = make_claim(billed_amount_cents=100_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.eligible_cents == 100_000
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 100_000
        assert r.coinsurance_cents == 80_000
        assert r.insurer_pays_cents == 80_000
        assert r.patient_pays_cents == 20_000
        assert r.reason_code == ReasonCode.PAID
        assert r.updated_insurer_paid_cents == 999_999_999 + 80_000
        assert r.policy_year == 2026


# ---------------------------------------------------------------------------
# Test: waiting period active (AC spec #1 / WI t2 AC #8)
# ---------------------------------------------------------------------------

class TestWaitingPeriodActive:
    def test_one_day_before_effective_date(self):
        policy = make_policy(waiting_period_days=30, coverage_start_date=date(2026, 1, 1))
        effective = date(2026, 1, 1) + timedelta(days=30)
        service = effective - timedelta(days=1)
        ytd = make_ytd(deductible_paid_cents=50_000, insurer_paid_cents=20_000)
        claim = make_claim(billed_amount_cents=80_000, service_date=service)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.eligible_cents == 0
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 0
        assert r.coinsurance_cents == 0
        assert r.insurer_pays_cents == 0
        assert r.patient_pays_cents == 0
        assert r.reason_code == ReasonCode.WAITING_PERIOD
        # Accumulators unchanged
        assert r.updated_deductible_paid_cents == 50_000
        assert r.updated_insurer_paid_cents == 20_000
        assert r.policy_year == service.year

    def test_service_before_coverage_start(self):
        policy = make_policy(waiting_period_days=0, coverage_start_date=date(2026, 6, 1))
        claim = make_claim(billed_amount_cents=10_000, service_date=date(2026, 5, 31))

        r = calculate_reimbursement(policy, make_ytd(), claim)

        assert r.reason_code == ReasonCode.WAITING_PERIOD
        assert r.insurer_pays_cents == 0
        assert r.eligible_cents == 0


# ---------------------------------------------------------------------------
# Test: waiting period just expired — effective date itself (WI t2 AC #9)
# ---------------------------------------------------------------------------

class TestWaitingPeriodExpired:
    def test_service_on_effective_date(self):
        policy = make_policy(
            waiting_period_days=30,
            coverage_start_date=date(2026, 1, 1),
            annual_deductible_cents=0,
            coverage_rate_bps=8000,
            annual_ceiling_cents=None,
        )
        effective = date(2026, 1, 1) + timedelta(days=30)
        claim = make_claim(billed_amount_cents=100_000, service_date=effective)

        r = calculate_reimbursement(policy, make_ytd(), claim)

        assert r.reason_code == ReasonCode.PAID
        assert r.insurer_pays_cents == 80_000
        assert r.eligible_cents == 100_000
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 100_000
        assert r.coinsurance_cents == 80_000
        assert r.patient_pays_cents == 20_000
        assert r.policy_year == effective.year


# ---------------------------------------------------------------------------
# Test: zero-billed claim (WI t2 AC #10)
# ---------------------------------------------------------------------------

class TestZeroBilled:
    def test_all_fields(self):
        policy = make_policy(annual_deductible_cents=0, coverage_rate_bps=8000, annual_ceiling_cents=None)
        ytd = make_ytd()
        claim = make_claim(billed_amount_cents=0)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.eligible_cents == 0
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 0
        assert r.coinsurance_cents == 0
        assert r.insurer_pays_cents == 0
        assert r.patient_pays_cents == 0
        assert r.reason_code == ReasonCode.ZERO_BILLED
        assert r.updated_deductible_paid_cents == 0
        assert r.updated_insurer_paid_cents == 0
        assert r.policy_year == 2026


# ---------------------------------------------------------------------------
# Test: 100 % coverage rate (WI t2 AC #11)
# ---------------------------------------------------------------------------

class TestFullCoverageRate:
    def test_all_fields(self):
        policy = make_policy(
            coverage_rate_bps=10_000,
            annual_deductible_cents=0,
            annual_ceiling_cents=None,
        )
        ytd = make_ytd()
        claim = make_claim(billed_amount_cents=75_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.eligible_cents == 75_000
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 75_000
        assert r.coinsurance_cents == 75_000
        assert r.insurer_pays_cents == 75_000
        assert r.patient_pays_cents == 0
        assert r.reason_code == ReasonCode.PAID
        assert r.updated_insurer_paid_cents == 75_000
        assert r.policy_year == 2026

    def test_with_ceiling(self):
        policy = make_policy(
            coverage_rate_bps=10_000,
            annual_deductible_cents=0,
            annual_ceiling_cents=50_000,
        )
        ytd = make_ytd(insurer_paid_cents=30_000)
        claim = make_claim(billed_amount_cents=75_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.insurer_pays_cents == 20_000  # capped by remaining ceiling
        assert r.reason_code == ReasonCode.PAID
        assert r.updated_insurer_paid_cents == 50_000


# ---------------------------------------------------------------------------
# Test: 0 % coverage rate with deductible met (WI t2 AC #12)
# ---------------------------------------------------------------------------

class TestZeroCoverageRate:
    def test_all_fields(self):
        policy = make_policy(
            coverage_rate_bps=0,
            annual_deductible_cents=0,
            annual_ceiling_cents=None,
        )
        ytd = make_ytd()
        claim = make_claim(billed_amount_cents=50_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.eligible_cents == 50_000
        assert r.deductible_applied_cents == 0
        assert r.post_deductible_cents == 50_000
        assert r.coinsurance_cents == 0
        assert r.insurer_pays_cents == 0
        assert r.patient_pays_cents == 50_000
        assert r.reason_code == ReasonCode.PAID
        assert r.updated_insurer_paid_cents == 0
        assert r.policy_year == 2026


# ---------------------------------------------------------------------------
# Test: accumulator invariants (WI t2 AC #13)
# ---------------------------------------------------------------------------

class TestAccumulatorInvariants:
    def test_updated_deductible_invariant(self):
        policy = make_policy(annual_deductible_cents=100_000, annual_ceiling_cents=None)
        ytd = make_ytd(deductible_paid_cents=70_000)
        claim = make_claim(billed_amount_cents=50_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.updated_deductible_paid_cents == ytd.deductible_paid_cents + r.deductible_applied_cents

    def test_updated_insurer_invariant(self):
        policy = make_policy(annual_deductible_cents=0, annual_ceiling_cents=None)
        ytd = make_ytd(insurer_paid_cents=100_000)
        claim = make_claim(billed_amount_cents=50_000)

        r = calculate_reimbursement(policy, ytd, claim)

        assert r.updated_insurer_paid_cents == ytd.insurer_paid_cents + r.insurer_pays_cents


# ---------------------------------------------------------------------------
# Test: validation errors (WI t1 AC #16)
# ---------------------------------------------------------------------------

class TestValidation:
    def test_empty_policy_id_raises(self):
        with pytest.raises(ValueError, match="policy_id"):
            PolicyTerms(
                policy_id="",
                coverage_rate_bps=8000,
                annual_deductible_cents=0,
                annual_ceiling_cents=None,
                waiting_period_days=0,
                coverage_start_date=date(2026, 1, 1),
            )

    def test_coverage_rate_above_max_raises(self):
        with pytest.raises(ValueError):
            PolicyTerms(
                policy_id="P1",
                coverage_rate_bps=10_001,
                annual_deductible_cents=0,
                annual_ceiling_cents=None,
                waiting_period_days=0,
                coverage_start_date=date(2026, 1, 1),
            )

    def test_coverage_rate_negative_raises(self):
        with pytest.raises(ValueError):
            PolicyTerms(
                policy_id="P1",
                coverage_rate_bps=-1,
                annual_deductible_cents=0,
                annual_ceiling_cents=None,
                waiting_period_days=0,
                coverage_start_date=date(2026, 1, 1),
            )

    def test_boundary_rates_valid(self):
        for bps in (0, 10_000):
            p = PolicyTerms(
                policy_id="P1",
                coverage_rate_bps=bps,
                annual_deductible_cents=0,
                annual_ceiling_cents=None,
                waiting_period_days=0,
                coverage_start_date=date(2026, 1, 1),
            )
            assert p.coverage_rate_bps == bps


# ---------------------------------------------------------------------------
# Test: determinism (WI t1 AC #15)
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_identical_inputs_identical_outputs(self):
        policy = make_policy()
        ytd = make_ytd(deductible_paid_cents=50_000)
        claim = make_claim(billed_amount_cents=80_000)

        r1 = calculate_reimbursement(policy, ytd, claim)
        r2 = calculate_reimbursement(policy, ytd, claim)

        assert r1 == r2


# ---------------------------------------------------------------------------
# Test: top-level namespace exports (WI t1 AC #1)
# ---------------------------------------------------------------------------

class TestTopLevelExports:
    def test_all_public_names_importable(self):
        import testbed_utils

        for name in (
            "calculate_reimbursement",
            "PolicyTerms",
            "YTDAccumulators",
            "Claim",
            "AdjudicationResult",
            "ReasonCode",
        ):
            assert hasattr(testbed_utils, name), f"{name} not in testbed_utils namespace"
