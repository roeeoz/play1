import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { Pool } from 'pg';
import { processClaim } from './index.js';
import { closePool } from '../store/index.js';
import type { ClaimInput } from '../types.js';

// Skip entirely when no PostgreSQL is available (unit-test CI job has no DB service)
const HAS_DB = Boolean(process.env['PGHOST']);

// UTC-midnight Date factory
const d = (s: string) => new Date(`${s}T00:00:00Z`);

const POLICY_ID = 'e2e-p-001';
const POLICY_ID_2 = 'e2e-p-002';
const YEAR = 2025;

// Direct pool for DB verification — intentionally bypasses the store module
const verifyPool = new Pool();

async function getPersistedTotals(
  policyId: string,
  year: number,
): Promise<{ ytd_deductible_consumed: number; ytd_ceiling_consumed: number }> {
  const r = await verifyPool.query<{
    ytd_deductible_consumed: string;
    ytd_ceiling_consumed: string;
  }>(
    'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2',
    [policyId, year],
  );
  const row = r.rows[0];
  if (!row) return { ytd_deductible_consumed: 0, ytd_ceiling_consumed: 0 };
  return {
    ytd_deductible_consumed: Number(row.ytd_deductible_consumed),
    ytd_ceiling_consumed: Number(row.ytd_ceiling_consumed),
  };
}

describe.skipIf(!HAS_DB)('processClaim smoke test', () => {
  beforeAll(async () => {
    // Clean up any leftover test data, respecting FK order
    await verifyPool.query("DELETE FROM claims WHERE claim_id LIKE 'e2e-%'");
    await verifyPool.query("DELETE FROM ytd_totals WHERE policy_id LIKE 'e2e-%'");
    await verifyPool.query("DELETE FROM policies WHERE policy_id LIKE 'e2e-%'");

    // Policy 1 — main sequence: 80% coverage, $500 deductible, $10k ceiling, 30-day waiting
    await verifyPool.query(
      `INSERT INTO policies (policy_id, coverage_pct, deductible, annual_ceiling, coverage_start, waiting_period_days)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [POLICY_ID, 0.8, 500, 10000, '2025-01-01', 30],
    );

    // Policy 2 — concurrent test: 80% coverage, $0 deductible, $100k ceiling, no waiting
    await verifyPool.query(
      `INSERT INTO policies (policy_id, coverage_pct, deductible, annual_ceiling, coverage_start, waiting_period_days)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [POLICY_ID_2, 0.8, 0, 100000, '2024-01-01', 0],
    );
  });

  afterAll(async () => {
    await verifyPool.end();
    await closePool();
  });

  it('step 1: service date within waiting period → WAITING_PERIOD, totals unchanged', async () => {
    // coverage_start=2025-01-01, waiting=30 days → end=2025-01-31; Jan 15 is inside
    const claim: ClaimInput = {
      claim_id: 'e2e-c-001',
      policy_id: POLICY_ID,
      billed_amount: 100,
      service_date: d('2025-01-15'),
    };
    const result = await processClaim(claim);

    expect(result.reason).toBe('WAITING_PERIOD');
    expect(result.reimbursement).toBe(0);

    const totals = await getPersistedTotals(POLICY_ID, YEAR);
    expect(totals.ytd_deductible_consumed).toBe(0);
    expect(totals.ytd_ceiling_consumed).toBe(0);
  });

  it('step 2: billed amount fully absorbed by deductible → DEDUCTIBLE_NOT_MET, deductible total increases', async () => {
    // deductible=500, remaining=500; billed=300 ≤ 500 → DEDUCTIBLE_NOT_MET
    const claim: ClaimInput = {
      claim_id: 'e2e-c-002',
      policy_id: POLICY_ID,
      billed_amount: 300,
      service_date: d('2025-03-01'),
    };
    const result = await processClaim(claim);

    expect(result.reason).toBe('DEDUCTIBLE_NOT_MET');
    expect(result.reimbursement).toBe(0);
    expect(result.deductible_applied).toBe(300);

    const totals = await getPersistedTotals(POLICY_ID, YEAR);
    expect(totals.ytd_deductible_consumed).toBe(300);
    expect(totals.ytd_ceiling_consumed).toBe(0);
  });

  it('step 3: partial deductible exhaustion, covered amount below ceiling → APPROVED, both totals update', async () => {
    // deductible remaining = 500 - 300 = 200; billed=500 > 200 → deductible_applied=200
    // post_deductible = 300; covered = 300 * 0.8 = 240; ceiling_remaining=10000 → reimbursement=240
    const claim: ClaimInput = {
      claim_id: 'e2e-c-003',
      policy_id: POLICY_ID,
      billed_amount: 500,
      service_date: d('2025-04-01'),
    };
    const result = await processClaim(claim);

    expect(result.reason).toBe('APPROVED');
    expect(result.reimbursement).toBe(240);
    expect(result.deductible_applied).toBe(200);

    const totals = await getPersistedTotals(POLICY_ID, YEAR);
    expect(totals.ytd_deductible_consumed).toBe(500); // 300 + 200
    expect(totals.ytd_ceiling_consumed).toBe(240);
  });

  it('step 4: covered amount exceeds remaining ceiling → PARTIAL_CEILING_CAP, ceiling total reaches annual_ceiling', async () => {
    // deductible fully consumed; ceiling remaining = 10000 - 240 = 9760
    // billed=15000; deductible_applied=0; post=15000; covered=12000 > 9760 → PARTIAL_CEILING_CAP
    const claim: ClaimInput = {
      claim_id: 'e2e-c-004',
      policy_id: POLICY_ID,
      billed_amount: 15000,
      service_date: d('2025-05-01'),
    };
    const result = await processClaim(claim);

    expect(result.reason).toBe('PARTIAL_CEILING_CAP');
    expect(result.reimbursement).toBe(9760);

    const totals = await getPersistedTotals(POLICY_ID, YEAR);
    expect(totals.ytd_deductible_consumed).toBe(500);
    expect(totals.ytd_ceiling_consumed).toBe(10000); // 240 + 9760 = policy annual_ceiling
  });

  it('step 5: ceiling fully consumed → ANNUAL_CEILING_REACHED, totals unchanged', async () => {
    const claim: ClaimInput = {
      claim_id: 'e2e-c-005',
      policy_id: POLICY_ID,
      billed_amount: 1000,
      service_date: d('2025-06-01'),
    };
    const result = await processClaim(claim);

    expect(result.reason).toBe('ANNUAL_CEILING_REACHED');
    expect(result.reimbursement).toBe(0);

    const totals = await getPersistedTotals(POLICY_ID, YEAR);
    expect(totals.ytd_deductible_consumed).toBe(500);
    expect(totals.ytd_ceiling_consumed).toBe(10000); // unchanged
  });

  it('step 6: re-submitting claim from step 3 throws DUPLICATE_CLAIM, totals unchanged', async () => {
    const claim: ClaimInput = {
      claim_id: 'e2e-c-003', // same claim_id as step 3
      policy_id: POLICY_ID,
      billed_amount: 500,
      service_date: d('2025-04-01'),
    };
    await expect(processClaim(claim)).rejects.toThrow('DUPLICATE_CLAIM');

    const totals = await getPersistedTotals(POLICY_ID, YEAR);
    expect(totals.ytd_deductible_consumed).toBe(500);
    expect(totals.ytd_ceiling_consumed).toBe(10000); // unchanged
  });

  it('concurrent: two simultaneous processClaim calls both resolve, DB totals equal sum of reimbursements', async () => {
    // Policy 2: deductible=0, coverage_pct=0.8, no waiting period
    // Claim A: billed=1000 → covered=800; Claim B: billed=2000 → covered=1600
    const claimA: ClaimInput = {
      claim_id: 'e2e-c-concurrent-1',
      policy_id: POLICY_ID_2,
      billed_amount: 1000,
      service_date: d('2025-07-01'),
    };
    const claimB: ClaimInput = {
      claim_id: 'e2e-c-concurrent-2',
      policy_id: POLICY_ID_2,
      billed_amount: 2000,
      service_date: d('2025-07-01'),
    };

    const [resultA, resultB] = await Promise.all([processClaim(claimA), processClaim(claimB)]);

    expect(resultA.reason).toBe('APPROVED');
    expect(resultB.reason).toBe('APPROVED');

    const expectedTotal = resultA.reimbursement + resultB.reimbursement;

    const totals = await getPersistedTotals(POLICY_ID_2, YEAR);
    expect(totals.ytd_ceiling_consumed).toBe(expectedTotal);
  });
});
