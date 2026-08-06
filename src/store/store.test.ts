import { describe, it, expect, beforeEach, afterAll } from 'vitest';
import { Pool } from 'pg';
import { getPolicy, getYtdTotals, applyResult } from './index.js';
import type { ReimbursementResult } from '../types.js';

const pgConfigured = Boolean(process.env['PGHOST']);

// Separate pool for test setup/assertions — uses same PG* env vars as the store pool.
const db = new Pool({ allowExitOnIdle: true });

const POLICY_ID = 'test-policy-001';
const YEAR = 2026;

const BASE_RESULT: ReimbursementResult = {
  claim_id: 'claim-001',
  reimbursement: 100,
  reason: 'APPROVED',
  deductible_applied: 50,
  ytd_deductible_consumed: 50,
  ytd_ceiling_consumed: 100,
};

interface YtdRow {
  ytd_deductible_consumed: string;
  ytd_ceiling_consumed: string;
}

interface CountRow {
  count: string;
}

beforeEach(async () => {
  if (!pgConfigured) return;
  await db.query('TRUNCATE TABLE claim_log, ytd_totals, policies');
  await db.query(
    `INSERT INTO policies (policy_id, coverage_pct, deductible, annual_ceiling, coverage_start, waiting_period_days)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [POLICY_ID, 0.8, 500.0, 10000.0, '2026-01-01', 30],
  );
});

afterAll(async () => {
  await db.end();
});

describe.skipIf(!pgConfigured)('getPolicy', () => {
  it('returns correctly typed Policy when row exists', async () => {
    const policy = await getPolicy(POLICY_ID);
    expect(policy.policy_id).toBe(POLICY_ID);
    expect(policy.coverage_pct).toBe(0.8);
    expect(policy.deductible).toBe(500);
    expect(policy.annual_ceiling).toBe(10000);
    expect(policy.coverage_start).toBeInstanceOf(Date);
    expect(policy.waiting_period_days).toBe(30);
  });

  it('throws POLICY_NOT_FOUND for an unknown policy_id', async () => {
    await expect(getPolicy('does-not-exist')).rejects.toThrow('POLICY_NOT_FOUND');
  });
});

describe.skipIf(!pgConfigured)('getYtdTotals', () => {
  it('returns zeros for a new policy/year without inserting a row', async () => {
    const totals = await getYtdTotals(POLICY_ID, YEAR);
    expect(totals.ytd_deductible_consumed).toBe(0);
    expect(totals.ytd_ceiling_consumed).toBe(0);

    const { rows } = await db.query<CountRow>(
      'SELECT COUNT(*) AS count FROM ytd_totals WHERE policy_id = $1 AND year = $2',
      [POLICY_ID, YEAR],
    );
    expect(parseInt(rows[0]?.count ?? '0', 10)).toBe(0);
  });

  it('returns updated totals after applyResult', async () => {
    await applyResult(BASE_RESULT, POLICY_ID, YEAR);
    const totals = await getYtdTotals(POLICY_ID, YEAR);
    expect(totals.ytd_deductible_consumed).toBe(50);
    expect(totals.ytd_ceiling_consumed).toBe(100);
  });

  it('returns zeros for year N+1 when year N has a row (lazy calendar-year reset)', async () => {
    await applyResult(BASE_RESULT, POLICY_ID, YEAR);

    const totals = await getYtdTotals(POLICY_ID, YEAR + 1);
    expect(totals.ytd_deductible_consumed).toBe(0);
    expect(totals.ytd_ceiling_consumed).toBe(0);

    const { rows } = await db.query<CountRow>(
      'SELECT COUNT(*) AS count FROM ytd_totals WHERE policy_id = $1 AND year = $2',
      [POLICY_ID, YEAR + 1],
    );
    expect(parseInt(rows[0]?.count ?? '0', 10)).toBe(0);
  });
});

describe.skipIf(!pgConfigured)('applyResult', () => {
  it('increments totals and inserts claim_log row for a unique claim', async () => {
    await applyResult(BASE_RESULT, POLICY_ID, YEAR);

    const { rows } = await db.query<YtdRow>(
      'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2',
      [POLICY_ID, YEAR],
    );
    const row = rows[0];
    expect(row).toBeDefined();
    expect(parseFloat(row?.ytd_deductible_consumed ?? '0')).toBe(50);
    expect(parseFloat(row?.ytd_ceiling_consumed ?? '0')).toBe(100);

    const log = await db.query<CountRow>(
      'SELECT COUNT(*) AS count FROM claim_log WHERE claim_id = $1',
      [BASE_RESULT.claim_id],
    );
    expect(parseInt(log.rows[0]?.count ?? '0', 10)).toBe(1);
  });

  it('two concurrent calls on the same policy/year both succeed with correct summed totals', async () => {
    const r1: ReimbursementResult = {
      ...BASE_RESULT,
      claim_id: 'claim-concurrent-1',
      deductible_applied: 100,
      reimbursement: 200,
      ytd_deductible_consumed: 100,
      ytd_ceiling_consumed: 200,
    };
    const r2: ReimbursementResult = {
      ...BASE_RESULT,
      claim_id: 'claim-concurrent-2',
      deductible_applied: 150,
      reimbursement: 300,
      ytd_deductible_consumed: 250,
      ytd_ceiling_consumed: 500,
    };

    await Promise.all([applyResult(r1, POLICY_ID, YEAR), applyResult(r2, POLICY_ID, YEAR)]);

    const { rows } = await db.query<YtdRow>(
      'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2',
      [POLICY_ID, YEAR],
    );
    const row = rows[0];
    expect(row).toBeDefined();
    expect(parseFloat(row?.ytd_deductible_consumed ?? '0')).toBe(250); // 100 + 150
    expect(parseFloat(row?.ytd_ceiling_consumed ?? '0')).toBe(500); // 200 + 300
  });

  it('throws DUPLICATE_CLAIM and leaves totals unchanged on a repeated claim_id', async () => {
    await applyResult(BASE_RESULT, POLICY_ID, YEAR);

    const before = await db.query<YtdRow>(
      'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2',
      [POLICY_ID, YEAR],
    );

    await expect(applyResult(BASE_RESULT, POLICY_ID, YEAR)).rejects.toThrow('DUPLICATE_CLAIM');

    const after = await db.query<YtdRow>(
      'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2',
      [POLICY_ID, YEAR],
    );
    expect(after.rows[0]?.ytd_deductible_consumed).toBe(before.rows[0]?.ytd_deductible_consumed);
    expect(after.rows[0]?.ytd_ceiling_consumed).toBe(before.rows[0]?.ytd_ceiling_consumed);
  });

  it('inserts claim_log row and leaves totals at zero for a WAITING_PERIOD result', async () => {
    const zeroResult: ReimbursementResult = {
      claim_id: 'claim-waiting-period',
      reimbursement: 0,
      reason: 'WAITING_PERIOD',
      deductible_applied: 0,
      ytd_deductible_consumed: 0,
      ytd_ceiling_consumed: 0,
    };

    await applyResult(zeroResult, POLICY_ID, YEAR);

    const log = await db.query<CountRow>(
      'SELECT COUNT(*) AS count FROM claim_log WHERE claim_id = $1',
      [zeroResult.claim_id],
    );
    expect(parseInt(log.rows[0]?.count ?? '0', 10)).toBe(1);

    const { rows } = await db.query<YtdRow>(
      'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2',
      [POLICY_ID, YEAR],
    );
    // A row may be upserted with zero values — totals must not be positive.
    if (rows.length > 0) {
      expect(parseFloat(rows[0]?.ytd_deductible_consumed ?? '0')).toBe(0);
      expect(parseFloat(rows[0]?.ytd_ceiling_consumed ?? '0')).toBe(0);
    }
  });
});
