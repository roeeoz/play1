import { Pool } from 'pg';
import type { Policy, YtdTotals, ReimbursementResult } from '../types.js';

const pool = new Pool({
  host: process.env['PGHOST'],
  port: process.env['PGPORT'] !== undefined ? parseInt(process.env['PGPORT'], 10) : undefined,
  database: process.env['PGDATABASE'],
  user: process.env['PGUSER'],
  password: process.env['PGPASSWORD'],
  allowExitOnIdle: true,
});

interface PolicyRow {
  policy_id: string;
  coverage_pct: string;
  deductible: string;
  annual_ceiling: string;
  coverage_start: Date;
  waiting_period_days: number;
}

interface YtdRow {
  ytd_deductible_consumed: string;
  ytd_ceiling_consumed: string;
}

function isPgUniqueViolation(err: unknown): boolean {
  return (
    typeof err === 'object' &&
    err !== null &&
    'code' in err &&
    (err as { code: unknown }).code === '23505'
  );
}

export async function getPolicy(policy_id: string): Promise<Policy> {
  const result = await pool.query<PolicyRow>(
    'SELECT * FROM policies WHERE policy_id = $1',
    [policy_id],
  );
  const row = result.rows[0];
  if (!row) {
    throw new Error('POLICY_NOT_FOUND');
  }
  return {
    policy_id: row.policy_id,
    coverage_pct: parseFloat(row.coverage_pct),
    deductible: parseFloat(row.deductible),
    annual_ceiling: parseFloat(row.annual_ceiling),
    coverage_start: row.coverage_start,
    waiting_period_days: row.waiting_period_days,
  };
}

export async function getYtdTotals(policy_id: string, year: number): Promise<YtdTotals> {
  const result = await pool.query<YtdRow>(
    'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2',
    [policy_id, year],
  );
  const row = result.rows[0];
  if (!row) {
    return { ytd_deductible_consumed: 0, ytd_ceiling_consumed: 0 };
  }
  return {
    ytd_deductible_consumed: parseFloat(row.ytd_deductible_consumed),
    ytd_ceiling_consumed: parseFloat(row.ytd_ceiling_consumed),
  };
}

export async function applyResult(
  result: ReimbursementResult,
  policy_id: string,
  year: number,
): Promise<void> {
  const client = await pool.connect();
  let transactionEnded = false;
  try {
    await client.query('BEGIN');

    try {
      await client.query(
        'INSERT INTO claim_log (claim_id, policy_id, year) VALUES ($1, $2, $3)',
        [result.claim_id, policy_id, year],
      );
    } catch (insertErr: unknown) {
      if (isPgUniqueViolation(insertErr)) {
        await client.query('ROLLBACK');
        transactionEnded = true;
        throw new Error('DUPLICATE_CLAIM');
      }
      throw insertErr;
    }

    // Acquire row-level lock to serialise concurrent applyResult calls for the same policy/year.
    await client.query(
      'SELECT ytd_deductible_consumed, ytd_ceiling_consumed FROM ytd_totals WHERE policy_id = $1 AND year = $2 FOR UPDATE',
      [policy_id, year],
    );

    await client.query(
      `INSERT INTO ytd_totals (policy_id, year, ytd_deductible_consumed, ytd_ceiling_consumed)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (policy_id, year) DO UPDATE SET
         ytd_deductible_consumed = ytd_totals.ytd_deductible_consumed + EXCLUDED.ytd_deductible_consumed,
         ytd_ceiling_consumed    = ytd_totals.ytd_ceiling_consumed    + EXCLUDED.ytd_ceiling_consumed`,
      [policy_id, year, result.deductible_applied, result.reimbursement],
    );

    await client.query('COMMIT');
    transactionEnded = true;
  } catch (err: unknown) {
    if (!transactionEnded) {
      await client.query('ROLLBACK').catch(() => undefined);
    }
    throw err;
  } finally {
    client.release();
  }
}
