import type { Policy, YtdTotals, ClaimInput, ReasonCode, ReimbursementResult } from './types.js';
import { describe, it, expect } from 'vitest';

describe('types module', () => {
  it('ReasonCode accepts all valid values', () => {
    const codes: ReasonCode[] = [
      'APPROVED',
      'WAITING_PERIOD',
      'DEDUCTIBLE_NOT_MET',
      'ANNUAL_CEILING_REACHED',
      'PARTIAL_CEILING_CAP',
    ];
    expect(codes).toHaveLength(5);
  });

  it('Policy interface has required fields', () => {
    const policy: Policy = {
      policy_id: 'p-001',
      coverage_pct: 0.8,
      deductible: 500,
      annual_ceiling: 10000,
      coverage_start: new Date('2025-01-01'),
      waiting_period_days: 30,
    };
    expect(policy.policy_id).toBe('p-001');
    expect(policy.coverage_pct).toBe(0.8);
  });

  it('ClaimInput interface has required fields', () => {
    const claim: ClaimInput = {
      claim_id: 'c-001',
      policy_id: 'p-001',
      billed_amount: 200,
      service_date: new Date('2025-03-01'),
    };
    expect(claim.claim_id).toBe('c-001');
    expect(claim.billed_amount).toBe(200);
  });

  it('YtdTotals interface has required fields', () => {
    const totals: YtdTotals = {
      ytd_deductible_consumed: 0,
      ytd_ceiling_consumed: 0,
    };
    expect(totals.ytd_deductible_consumed).toBe(0);
    expect(totals.ytd_ceiling_consumed).toBe(0);
  });

  it('ReimbursementResult interface has required fields', () => {
    const result: ReimbursementResult = {
      claim_id: 'c-001',
      reimbursement: 160,
      reason: 'APPROVED',
      deductible_applied: 0,
      ytd_deductible_consumed: 0,
      ytd_ceiling_consumed: 160,
    };
    expect(result.reimbursement).toBe(160);
    expect(result.reason).toBe('APPROVED');
  });
});
