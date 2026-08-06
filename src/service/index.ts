import type { ClaimInput, ReimbursementResult } from '../types.js';
import { calculateReimbursement } from '../engine/index.js';
import { getPolicy, getYtdTotals, applyResult } from '../store/index.js';

export async function processClaim(input: ClaimInput): Promise<ReimbursementResult> {
  const year = input.service_date.getUTCFullYear();
  const policy = await getPolicy(input.policy_id);
  const totals = await getYtdTotals(input.policy_id, year);
  const result = calculateReimbursement(input, policy, totals);
  await applyResult(result, input.policy_id, year);
  return result;
}
