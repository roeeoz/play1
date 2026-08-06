import { Pool } from 'pg';
import type { Policy, YtdTotals, ReimbursementResult } from '../types.js';

const pool = new Pool();

export function closePool(): Promise<void> {
  return pool.end();
}

export async function getPolicy(policy_id: string): Promise<Policy> {
  const result = await pool.query<{
    policy_id: string;
    coverage_pct: string;
    deductible: string;
    annual_ceiling: string;
    coverage_start: string;
    waiting_period_days: number;
  }>(
    'SELECT policy_id, coverage_pct, deductible, annual_ceiling, coverage_start, waiting_period_days FROM policies WHERE policy_id = $1',
    [policy_id],
  );
  const row = result.rows[0];
  if (!row) {
    throw new Error('POLICY_NOT_FOUND');
  }
  return {
    policy_id: row.policy_id,
    coverage_pct: Number(row.coverage_pct),
    deductible: Number(row.deductible),
    annual_ceiling: Number(row.annual_ceiling),
    coverage_start: new Date(row.coverage_start),
    waiting_period_days: row.waiting_period_days,
  };
}

export async function getYtdTotals(policy_id: string, year: number): Promise<YtdTotals> {
  const result = await pool.query<{
    ytd_deductible_consumed: string;
    ytd_ceiling_consumed: string;
  }>(
    'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2',
    [policy_id, year],
  );
  const row = result.rows[0];
  if (!row) {
    return { ytd_deductible_consumed: 0, ytd_ceiling_consumed: 0 };
  }
  return {
    ytd_deductible_consumed: Number(row.ytd_deductible_consumed),
    ytd_ceiling_consumed: Number(row.ytd_ceiling_consumed),
  };
}

function isUniqueViolation(err: unknown): boolean {
  return (
    typeof err === 'object' &&
    err !== null &&
    'code' in err &&
    (err as { code: string }).code === '23505'
  );
}

export async function applyResult(
  result: ReimbursementResult,
  policy_id: string,
  year: number,
): Promise<void> {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client
      .query(
        `INSERT INTO claims (claim_id, policy_id, reimbursement, reason, deductible_applied)
         VALUES ($1, $2, $3, $4, $5)`,
        [
          result.claim_id,
          policy_id,
          result.reimbursement,
          result.reason,
          result.deductible_applied,
        ],
      )
      .catch((err: unknown): never => {
        if (isUniqueViolation(err)) throw new Error('DUPLICATE_CLAIM');
        throw err;
      });
    await client.query(
      `INSERT INTO ytd_totals (policy_id, year, ytd_deductible_consumed, ytd_ceiling_consumed)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (policy_id, year) DO UPDATE SET
         ytd_deductible_consumed = ytd_totals.ytd_deductible_consumed + EXCLUDED.ytd_deductible_consumed,
         ytd_ceiling_consumed = ytd_totals.ytd_ceiling_consumed + EXCLUDED.ytd_ceiling_consumed`,
      [policy_id, year, result.deductible_applied, result.reimbursement],
    );
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK').catch(() => undefined);
    throw err;
  } finally {
    client.release();
  }
}
