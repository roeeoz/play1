import { describe, expect, it } from 'vitest';
import { calculateReimbursement, processClaims } from '../index';
import type { Claim, Policy, YtdState } from '@claim-engine/types';
import { ReasonCode } from '@claim-engine/types';

const basePolicy: Policy = {
  coverage_start_date: '2024-01-01',
  waiting_period_days: 30,
  annual_deductible: 1000,
  coverage_percentage: 80,
  annual_ceiling: 5000,
};

const freshYtd2024: YtdState = {
  year: 2024,
  deductible_consumed: 0,
  ceiling_consumed: 0,
};

describe('calculateReimbursement', () => {
  // Scenario 1: service date before waiting period end
  it('returns WAITING_PERIOD_ACTIVE when service date is before waiting period end', () => {
    const claim: Claim = { claim_id: 'c1', service_date: '2024-01-15', billed_amount: 500 };
    const result = calculateReimbursement(basePolicy, claim, freshYtd2024);

    expect(result.reason_code).toBe(ReasonCode.WAITING_PERIOD_ACTIVE);
    expect(result.reimbursed_amount).toBe(0);
    expect(result.deductible_applied).toBe(0);
    expect(result.patient_responsibility).toBe(500);
    expect(result.ceiling_remaining).toBe(5000);
  });

  // Scenario 2: partial deductible then coverage percentage on remainder
  it('applies partial deductible and coverage percentage to the remainder', () => {
    const claim: Claim = { claim_id: 'c2', service_date: '2024-03-01', billed_amount: 800 };
    // 600 already consumed → 400 remaining deductible
    const ytd: YtdState = { year: 2024, deductible_consumed: 600, ceiling_consumed: 0 };
    // deductibleApplied = min(400, 800) = 400; postDeductible = 400; gross = 400 * 0.8 = 320
    const result = calculateReimbursement(basePolicy, claim, ytd);

    expect(result.reason_code).toBe(ReasonCode.OK);
    expect(result.deductible_applied).toBe(400);
    expect(result.reimbursed_amount).toBe(320);
    expect(result.patient_responsibility).toBe(480);
    expect(result.ceiling_remaining).toBe(4680);
  });

  // Scenario 3: deductible fully exhausted before this claim
  it('applies zero deductible when already exhausted, full billed subject to coverage %', () => {
    const claim: Claim = { claim_id: 'c3', service_date: '2024-06-01', billed_amount: 1000 };
    const ytd: YtdState = { year: 2024, deductible_consumed: 1000, ceiling_consumed: 320 };
    // deductibleApplied = 0; gross = 1000 * 0.8 = 800
    const result = calculateReimbursement(basePolicy, claim, ytd);

    expect(result.reason_code).toBe(ReasonCode.OK);
    expect(result.deductible_applied).toBe(0);
    expect(result.reimbursed_amount).toBe(800);
    expect(result.ceiling_remaining).toBe(5000 - 320 - 800); // 3880
  });

  // Scenario 4: gross reimbursement exceeds remaining ceiling → PARTIALLY_CAPPED
  it('caps reimbursement at remaining ceiling and returns PARTIALLY_CAPPED', () => {
    const claim: Claim = { claim_id: 'c4', service_date: '2024-06-01', billed_amount: 10000 };
    const ytd: YtdState = { year: 2024, deductible_consumed: 1000, ceiling_consumed: 320 };
    // deductibleApplied = 0; gross = 10000 * 0.8 = 8000; ceilingRemaining = 4680
    // 8000 > 4680 → PARTIALLY_CAPPED; reimbursed = 4680
    const result = calculateReimbursement(basePolicy, claim, ytd);

    expect(result.reason_code).toBe(ReasonCode.PARTIALLY_CAPPED);
    expect(result.reimbursed_amount).toBe(4680);
    expect(result.ceiling_remaining).toBe(0);
    expect(result.patient_responsibility).toBe(10000 - 4680);
    expect(result.deductible_applied).toBe(0);
  });

  // Scenario 5: already-exhausted ceiling — deductible_applied reflects Step 2 consumption
  it('returns ANNUAL_CEILING_EXHAUSTED with deductible_applied from Step 2 when ceiling exhausted', () => {
    const claim: Claim = { claim_id: 'c5', service_date: '2024-09-01', billed_amount: 2000 };
    // Deductible partially consumed (500 left); ceiling fully consumed
    const ytd: YtdState = { year: 2024, deductible_consumed: 500, ceiling_consumed: 5000 };
    // Step 2 runs: deductibleApplied = min(500, 2000) = 500
    // Step 4: ceilingRemaining = 0 → ANNUAL_CEILING_EXHAUSTED
    const result = calculateReimbursement(basePolicy, claim, ytd);

    expect(result.reason_code).toBe(ReasonCode.ANNUAL_CEILING_EXHAUSTED);
    expect(result.reimbursed_amount).toBe(0);
    expect(result.deductible_applied).toBe(500);
    expect(result.ceiling_remaining).toBe(0);
  });

  // Scenario 9: coverage_percentage of 0 → zero gross reimbursement, OK
  it('produces reimbursed_amount of 0 when coverage_percentage is 0', () => {
    const policy: Policy = { ...basePolicy, coverage_percentage: 0 };
    const claim: Claim = { claim_id: 'c9', service_date: '2024-03-01', billed_amount: 1000 };
    const ytd: YtdState = { year: 2024, deductible_consumed: 1000, ceiling_consumed: 0 };

    const result = calculateReimbursement(policy, claim, ytd);

    expect(result.reason_code).toBe(ReasonCode.OK);
    expect(result.reimbursed_amount).toBe(0);
    expect(result.deductible_applied).toBe(0);
    expect(result.patient_responsibility).toBe(1000);
  });

  // Scenario 10: annual_deductible of 0 → no deductible applied, full billed subject to coverage %
  it('applies zero deductible when annual_deductible is 0', () => {
    const policy: Policy = { ...basePolicy, annual_deductible: 0 };
    const claim: Claim = { claim_id: 'c10', service_date: '2024-03-01', billed_amount: 500 };

    const result = calculateReimbursement(policy, claim, freshYtd2024);

    expect(result.reason_code).toBe(ReasonCode.OK);
    expect(result.deductible_applied).toBe(0);
    expect(result.reimbursed_amount).toBe(400); // 500 * 0.8
    expect(result.patient_responsibility).toBe(100);
  });
});

describe('processClaims', () => {
  // Scenario 8: empty array
  it('returns empty array for empty claims input', () => {
    expect(processClaims(basePolicy, [])).toEqual([]);
  });

  // Scenario 6: cross-year reset
  it('resets YtdState to zero when crossing a calendar year boundary', () => {
    const claims: Claim[] = [
      { claim_id: 'dec', service_date: '2024-12-15', billed_amount: 2000 },
      { claim_id: 'jan', service_date: '2025-01-15', billed_amount: 500 },
    ];
    const results = processClaims(basePolicy, claims);

    expect(results).toHaveLength(2);

    // Dec 2024: deductible=1000 consumed, gross = 1000*0.8 = 800
    expect(results[0].reason_code).toBe(ReasonCode.OK);
    expect(results[0].deductible_applied).toBe(1000);
    expect(results[0].reimbursed_amount).toBe(800);

    // Jan 2025: fresh YtdState — deductible resets; 500 < 1000 → all absorbed, gross = 0
    expect(results[1].reason_code).toBe(ReasonCode.OK);
    expect(results[1].deductible_applied).toBe(500);
    expect(results[1].reimbursed_amount).toBe(0);
  });

  // Scenario 7: five-claim fixture matching F4 smoke test values
  it('correctly sequences the five-claim fixture', () => {
    const policy: Policy = {
      coverage_start_date: '2024-01-01',
      waiting_period_days: 30,
      annual_deductible: 1000,
      coverage_percentage: 80,
      annual_ceiling: 5000,
    };
    const claims: Claim[] = [
      { claim_id: 'c1', service_date: '2024-01-15', billed_amount: 500 },
      { claim_id: 'c2', service_date: '2024-02-15', billed_amount: 600 },
      { claim_id: 'c3', service_date: '2024-03-01', billed_amount: 800 },
      { claim_id: 'c4', service_date: '2024-06-01', billed_amount: 10000 },
      { claim_id: 'c5', service_date: '2024-09-01', billed_amount: 2000 },
    ];

    const results = processClaims(policy, claims);
    expect(results).toHaveLength(5);

    // c1: waiting period active (2024-01-15 < 2024-01-31)
    expect(results[0].reason_code).toBe(ReasonCode.WAITING_PERIOD_ACTIVE);
    expect(results[0].reimbursed_amount).toBe(0);
    expect(results[0].deductible_applied).toBe(0);

    // c2: deductible=600 consumed, post-deductible=0, gross=0 → OK, reimbursed=0
    expect(results[1].reason_code).toBe(ReasonCode.OK);
    expect(results[1].reimbursed_amount).toBe(0);
    expect(results[1].deductible_applied).toBe(600);

    // c3: deductible remaining=400, applied=400, post=400, gross=320 → OK
    expect(results[2].reason_code).toBe(ReasonCode.OK);
    expect(results[2].reimbursed_amount).toBe(320);
    expect(results[2].deductible_applied).toBe(400);

    // c4: deductible exhausted, gross=8000, ceiling remaining=4680 → PARTIALLY_CAPPED
    expect(results[3].reason_code).toBe(ReasonCode.PARTIALLY_CAPPED);
    expect(results[3].reimbursed_amount).toBe(4680);

    // c5: ceiling=5000 exhausted → ANNUAL_CEILING_EXHAUSTED
    expect(results[4].reason_code).toBe(ReasonCode.ANNUAL_CEILING_EXHAUSTED);
    expect(results[4].reimbursed_amount).toBe(0);
  });
});
