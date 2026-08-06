import { Claim, ClaimResult, Policy, ReasonCode, YtdState } from '@claim-engine/types';

function addDays(dateStr: string, days: number): string {
  const date = new Date(dateStr + 'T00:00:00Z');
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

function serviceYear(dateStr: string): number {
  return parseInt(dateStr.slice(0, 4), 10);
}

export function calculateReimbursement(
  policy: Policy,
  claim: Claim,
  ytdState: YtdState
): ClaimResult {
  // Step 1: Waiting period check
  const waitingPeriodEnd = addDays(policy.coverage_start_date, policy.waiting_period_days);
  if (claim.service_date < waitingPeriodEnd) {
    return {
      claim_id: claim.claim_id,
      reason_code: ReasonCode.WAITING_PERIOD_ACTIVE,
      reimbursed_amount: 0,
      patient_responsibility: claim.billed_amount,
      deductible_applied: 0,
      ceiling_remaining: Math.max(0, policy.annual_ceiling - ytdState.ceiling_consumed),
    };
  }

  // Step 2: Deductible application
  const deductibleRemaining = Math.max(0, policy.annual_deductible - ytdState.deductible_consumed);
  const deductibleApplied = Math.min(deductibleRemaining, claim.billed_amount);
  const postDeductibleAmount = claim.billed_amount - deductibleApplied;

  // Step 3: Coverage percentage
  const grossReimbursement = postDeductibleAmount * (policy.coverage_percentage / 100);

  // Step 4: Annual ceiling check
  const ceilingRemainingBefore = Math.max(0, policy.annual_ceiling - ytdState.ceiling_consumed);

  if (ceilingRemainingBefore === 0) {
    return {
      claim_id: claim.claim_id,
      reason_code: ReasonCode.ANNUAL_CEILING_EXHAUSTED,
      reimbursed_amount: 0,
      patient_responsibility: claim.billed_amount,
      deductible_applied: deductibleApplied,
      ceiling_remaining: 0,
    };
  }

  let reimbursedAmount: number;
  let reasonCode: ReasonCode;

  if (grossReimbursement > ceilingRemainingBefore) {
    reimbursedAmount = ceilingRemainingBefore;
    reasonCode = ReasonCode.PARTIALLY_CAPPED;
  } else {
    reimbursedAmount = grossReimbursement;
    reasonCode = ReasonCode.OK;
  }

  return {
    claim_id: claim.claim_id,
    reason_code: reasonCode,
    reimbursed_amount: reimbursedAmount,
    patient_responsibility: claim.billed_amount - reimbursedAmount,
    deductible_applied: deductibleApplied,
    ceiling_remaining: ceilingRemainingBefore - reimbursedAmount,
  };
}

export function processClaims(policy: Policy, claims: Claim[]): ClaimResult[] {
  if (claims.length === 0) {
    return [];
  }

  const results: ClaimResult[] = [];
  let currentYtdState: YtdState = {
    year: serviceYear(claims[0].service_date),
    deductible_consumed: 0,
    ceiling_consumed: 0,
  };

  for (const claim of claims) {
    const claimYear = serviceYear(claim.service_date);
    if (claimYear !== currentYtdState.year) {
      currentYtdState = {
        year: claimYear,
        deductible_consumed: 0,
        ceiling_consumed: 0,
      };
    }

    const result = calculateReimbursement(policy, claim, currentYtdState);
    currentYtdState = {
      ...currentYtdState,
      deductible_consumed: currentYtdState.deductible_consumed + result.deductible_applied,
      ceiling_consumed: currentYtdState.ceiling_consumed + result.reimbursed_amount,
    };
    results.push(result);
  }

  return results;
}
