import { describe, expect, it } from 'vitest';
import { calculateReimbursement } from './index.js';
import type { ClaimInput, Policy, YtdTotals } from '../types.js';

// Build a UTC-midnight Date from an ISO date string to avoid DST influence
const d = (s: string) => new Date(`${s}T00:00:00Z`);

const BASE_POLICY: Policy = {
  policy_id: 'p-001',
  coverage_pct: 0.8,
  deductible: 500,
  annual_ceiling: 10_000,
  coverage_start: d('2025-01-01'),
  waiting_period_days: 30,
};

const ZERO_TOTALS: YtdTotals = { ytd_deductible_consumed: 0, ytd_ceiling_consumed: 0 };

function claim(overrides: Partial<ClaimInput> = {}): ClaimInput {
  return {
    claim_id: 'c-001',
    policy_id: 'p-001',
    billed_amount: 1000,
    service_date: d('2025-03-01'),
    ...overrides,
  };
}

describe('calculateReimbursement', () => {
  describe('Step 1 — waiting period', () => {
    it('rejects service date one day before waiting period ends', () => {
      // coverage_start=2025-01-01, waiting=30 days → end=2025-01-31
      const result = calculateReimbursement(
        claim({ service_date: d('2025-01-30') }),
        BASE_POLICY,
        ZERO_TOTALS,
      );
      expect(result.reason).toBe('WAITING_PERIOD');
      expect(result.reimbursement).toBe(0);
      expect(result.deductible_applied).toBe(0);
      expect(result.ytd_deductible_consumed).toBe(0);
      expect(result.ytd_ceiling_consumed).toBe(0);
    });

    it('allows service date exactly on the last day of the waiting period', () => {
      // 2025-01-31 is the first allowed day (30 days after Jan 1)
      const result = calculateReimbursement(
        claim({ service_date: d('2025-01-31') }),
        BASE_POLICY,
        ZERO_TOTALS,
      );
      expect(result.reason).not.toBe('WAITING_PERIOD');
    });

    it('never triggers WAITING_PERIOD when waiting_period_days = 0', () => {
      const policy = { ...BASE_POLICY, waiting_period_days: 0 };
      const result = calculateReimbursement(
        claim({ service_date: d('2025-01-01') }),
        policy,
        ZERO_TOTALS,
      );
      expect(result.reason).not.toBe('WAITING_PERIOD');
    });
  });

  describe('Step 2 — deductible consumption', () => {
    it('returns DEDUCTIBLE_NOT_MET when billed amount equals remaining deductible exactly', () => {
      // deductible=500, ytd_consumed=0 → remaining=500, billed=500
      const result = calculateReimbursement(
        claim({ billed_amount: 500 }),
        BASE_POLICY,
        ZERO_TOTALS,
      );
      expect(result.reason).toBe('DEDUCTIBLE_NOT_MET');
      expect(result.reimbursement).toBe(0);
      expect(result.deductible_applied).toBe(500);
      expect(result.ytd_deductible_consumed).toBe(500);
      expect(result.ytd_ceiling_consumed).toBe(0);
    });

    it('produces non-zero reimbursement when billed is one cent above remaining deductible', () => {
      // deductible=500, remaining=500, billed=500.01 → deductible_applied=500, post=0.01
      const result = calculateReimbursement(
        claim({ billed_amount: 500.01 }),
        BASE_POLICY,
        ZERO_TOTALS,
      );
      expect(result.reason).not.toBe('DEDUCTIBLE_NOT_MET');
      expect(result.deductible_applied).toBe(500);
      expect(result.reimbursement).toBeGreaterThan(0);
    });

    it('skips deductible entirely when already fully consumed', () => {
      // ytd_deductible_consumed=500 equals policy.deductible → remaining=0
      const totals: YtdTotals = { ytd_deductible_consumed: 500, ytd_ceiling_consumed: 0 };
      const result = calculateReimbursement(claim({ billed_amount: 200 }), BASE_POLICY, totals);
      expect(result.deductible_applied).toBe(0);
      expect(result.reimbursement).toBeGreaterThan(0);
    });

    it('guards against corrupted totals where ytd_deductible exceeds policy deductible', () => {
      // ytd=600 > deductible=500 → clamp to 0, full billed passes through
      const totals: YtdTotals = { ytd_deductible_consumed: 600, ytd_ceiling_consumed: 0 };
      const result = calculateReimbursement(claim({ billed_amount: 200 }), BASE_POLICY, totals);
      expect(result.deductible_applied).toBe(0);
    });
  });

  describe('Step 4 — annual ceiling cap', () => {
    it('returns APPROVED when covered amount equals ceiling remaining exactly', () => {
      // deductible already consumed; billed=200, post=200, covered=160
      // ytd_ceiling=9840 → remaining=160, min(160,160)=160 → APPROVED
      const totals: YtdTotals = { ytd_deductible_consumed: 500, ytd_ceiling_consumed: 9840 };
      const result = calculateReimbursement(claim({ billed_amount: 200 }), BASE_POLICY, totals);
      expect(result.reason).toBe('APPROVED');
      expect(result.reimbursement).toBe(160);
    });

    it('returns PARTIAL_CEILING_CAP when covered amount exceeds ceiling remaining by one cent', () => {
      // covered=160, ytd_ceiling=9840.01 → remaining=159.99, 160>159.99
      const totals: YtdTotals = { ytd_deductible_consumed: 500, ytd_ceiling_consumed: 9840.01 };
      const result = calculateReimbursement(claim({ billed_amount: 200 }), BASE_POLICY, totals);
      expect(result.reason).toBe('PARTIAL_CEILING_CAP');
      expect(result.reimbursement).toBe(159.99);
    });

    it('returns ANNUAL_CEILING_REACHED when ceiling is exactly exhausted', () => {
      const totals: YtdTotals = { ytd_deductible_consumed: 500, ytd_ceiling_consumed: 10_000 };
      const result = calculateReimbursement(claim({ billed_amount: 200 }), BASE_POLICY, totals);
      expect(result.reason).toBe('ANNUAL_CEILING_REACHED');
      expect(result.reimbursement).toBe(0);
    });

    it('guards against corrupted totals where ytd_ceiling exceeds annual ceiling', () => {
      const totals: YtdTotals = { ytd_deductible_consumed: 500, ytd_ceiling_consumed: 10_100 };
      const result = calculateReimbursement(claim({ billed_amount: 200 }), BASE_POLICY, totals);
      expect(result.reason).toBe('ANNUAL_CEILING_REACHED');
      expect(result.reimbursement).toBe(0);
    });
  });

  describe('Full scenarios and edge cases', () => {
    it('full happy path: partially consumed deductible, coverage within ceiling', () => {
      // deductible=500, ytd_consumed=200 → remaining=300
      // billed=700 > 300 → deductible_applied=300, post=400
      // covered=400*0.8=320, ceiling_remaining=10000, reimbursement=320
      const totals: YtdTotals = { ytd_deductible_consumed: 200, ytd_ceiling_consumed: 0 };
      const result = calculateReimbursement(claim({ billed_amount: 700 }), BASE_POLICY, totals);
      expect(result.reason).toBe('APPROVED');
      expect(result.reimbursement).toBe(320);
      expect(result.deductible_applied).toBe(300);
      expect(result.ytd_deductible_consumed).toBe(500);
      expect(result.ytd_ceiling_consumed).toBe(320);
    });

    it('coverage_pct = 1.0 reimburses full post-deductible amount', () => {
      const policy = { ...BASE_POLICY, coverage_pct: 1.0 };
      const totals: YtdTotals = { ytd_deductible_consumed: 500, ytd_ceiling_consumed: 0 };
      const result = calculateReimbursement(claim({ billed_amount: 300 }), policy, totals);
      expect(result.reason).toBe('APPROVED');
      expect(result.reimbursement).toBe(300);
    });

    it('coverage_pct = 0.0 gives APPROVED with zero reimbursement and unchanged ceiling totals', () => {
      const policy = { ...BASE_POLICY, coverage_pct: 0.0 };
      const totals: YtdTotals = { ytd_deductible_consumed: 500, ytd_ceiling_consumed: 0 };
      const result = calculateReimbursement(claim({ billed_amount: 300 }), policy, totals);
      expect(result.reason).toBe('APPROVED');
      expect(result.reimbursement).toBe(0);
      expect(result.ytd_ceiling_consumed).toBe(0);
    });

    it('rounds correctly without surfacing an IEEE 754 artifact', () => {
      // 100.10 * 0.3 = 30.030000000000001 in IEEE 754; output must be 30.03
      const policy = { ...BASE_POLICY, deductible: 0, coverage_pct: 0.3 };
      const result = calculateReimbursement(
        claim({ billed_amount: 100.1 }),
        policy,
        ZERO_TOTALS,
      );
      expect(result.reimbursement).toBe(30.03);
    });
  });
});
