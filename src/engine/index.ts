import type { ClaimInput, Policy, ReasonCode, ReimbursementResult, YtdTotals } from '../types.js';

export function calculateReimbursement(
  input: ClaimInput,
  policy: Policy,
  totals: YtdTotals,
): ReimbursementResult {
  // Step 1: Waiting period — compare UTC midnight timestamps to avoid DST drift
  const coverageStartMs = Date.UTC(
    policy.coverage_start.getUTCFullYear(),
    policy.coverage_start.getUTCMonth(),
    policy.coverage_start.getUTCDate(),
  );
  const waitingEndMs = coverageStartMs + policy.waiting_period_days * 86400000;
  const serviceDateMs = Date.UTC(
    input.service_date.getUTCFullYear(),
    input.service_date.getUTCMonth(),
    input.service_date.getUTCDate(),
  );
  if (serviceDateMs < waitingEndMs) {
    return {
      claim_id: input.claim_id,
      reimbursement: 0,
      reason: 'WAITING_PERIOD',
      deductible_applied: 0,
      ytd_deductible_consumed: totals.ytd_deductible_consumed,
      ytd_ceiling_consumed: totals.ytd_ceiling_consumed,
    };
  }

  // Step 2: Deductible consumption
  const deductible_remaining = Math.max(0, policy.deductible - totals.ytd_deductible_consumed);
  if (input.billed_amount <= deductible_remaining) {
    return {
      claim_id: input.claim_id,
      reimbursement: 0,
      reason: 'DEDUCTIBLE_NOT_MET',
      deductible_applied: input.billed_amount,
      ytd_deductible_consumed: totals.ytd_deductible_consumed + input.billed_amount,
      ytd_ceiling_consumed: totals.ytd_ceiling_consumed,
    };
  }

  const deductible_applied = deductible_remaining;
  const post_deductible_amount = input.billed_amount - deductible_applied;

  // Step 3: Coverage calculation (unrounded intermediate)
  const covered_amount = post_deductible_amount * policy.coverage_pct;

  // Step 4: Annual ceiling cap
  const ceiling_remaining = Math.max(0, policy.annual_ceiling - totals.ytd_ceiling_consumed);
  const reimbursement_raw = Math.min(covered_amount, ceiling_remaining);

  const reason: ReasonCode =
    ceiling_remaining === 0
      ? 'ANNUAL_CEILING_REACHED'
      : reimbursement_raw < covered_amount
        ? 'PARTIAL_CEILING_CAP'
        : 'APPROVED';

  const reimbursement = Math.round(reimbursement_raw * 100) / 100;

  // Step 5: Assemble result — ytd_* fields reflect state after persistence
  return {
    claim_id: input.claim_id,
    reimbursement,
    reason,
    deductible_applied,
    ytd_deductible_consumed: totals.ytd_deductible_consumed + deductible_applied,
    ytd_ceiling_consumed: totals.ytd_ceiling_consumed + reimbursement,
  };
}
