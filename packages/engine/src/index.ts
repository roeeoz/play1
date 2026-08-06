import type { Policy, Claim, ClaimResult, YtdState } from "@claim-engine/types";
import { ReasonCode } from "@claim-engine/types";

const MS_PER_DAY = 24 * 60 * 60 * 1000;

export function calculateReimbursement(
  policy: Policy,
  claim: Claim,
  ytdState: YtdState,
): ClaimResult {
  const coverageStart = new Date(
    policy.coverage_start_date + "T00:00:00Z",
  ).getTime();
  const serviceDate = new Date(claim.service_date + "T00:00:00Z").getTime();

  // Rule 1: Waiting period check
  if (serviceDate < coverageStart + policy.waiting_period_days * MS_PER_DAY) {
    return {
      claim_id: claim.claim_id,
      reimbursed_amount: 0,
      patient_responsibility: claim.billed_amount,
      reason_code: ReasonCode.WAITING_PERIOD_ACTIVE,
      deductible_applied: 0,
      ceiling_remaining: policy.annual_ceiling - ytdState.ceiling_consumed,
    };
  }

  // Rule 4 (pre-check): Ceiling already exhausted
  if (ytdState.ceiling_consumed >= policy.annual_ceiling) {
    return {
      claim_id: claim.claim_id,
      reimbursed_amount: 0,
      patient_responsibility: claim.billed_amount,
      reason_code: ReasonCode.ANNUAL_CEILING_EXHAUSTED,
      deductible_applied: 0,
      ceiling_remaining: 0,
    };
  }

  // Rule 2: Deductible application
  const deductibleRemaining =
    policy.annual_deductible - ytdState.deductible_consumed;
  const deductibleApplied = Math.min(deductibleRemaining, claim.billed_amount);
  const postDeductible = claim.billed_amount - deductibleApplied;

  // Rule 3: Coverage percentage
  const gross = postDeductible * (policy.coverage_percentage / 100);

  // Rule 4: Ceiling check
  const ceilingRemainingBefore =
    policy.annual_ceiling - ytdState.ceiling_consumed;

  if (gross > ceilingRemainingBefore) {
    ytdState.deductible_consumed += deductibleApplied;
    ytdState.ceiling_consumed = policy.annual_ceiling;
    return {
      claim_id: claim.claim_id,
      reimbursed_amount: ceilingRemainingBefore,
      patient_responsibility: claim.billed_amount - ceilingRemainingBefore,
      reason_code: ReasonCode.PARTIALLY_CAPPED,
      deductible_applied: deductibleApplied,
      ceiling_remaining: 0,
    };
  }

  ytdState.deductible_consumed += deductibleApplied;
  ytdState.ceiling_consumed += gross;

  return {
    claim_id: claim.claim_id,
    reimbursed_amount: gross,
    patient_responsibility: claim.billed_amount - gross,
    reason_code: ReasonCode.OK,
    deductible_applied: deductibleApplied,
    ceiling_remaining: ceilingRemainingBefore - gross,
  };
}

export function processClaims(policy: Policy, claims: Claim[]): ClaimResult[] {
  const ytdState: YtdState = {
    year: 0,
    deductible_consumed: 0,
    ceiling_consumed: 0,
  };
  return claims.map((claim) => calculateReimbursement(policy, claim, ytdState));
}
