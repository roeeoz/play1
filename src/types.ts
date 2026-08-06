export interface Policy {
  policy_id: string;
  coverage_pct: number; // 0–1, e.g. 0.8 for 80%
  deductible: number; // monetary USD
  annual_ceiling: number; // monetary USD
  coverage_start: Date;
  waiting_period_days: number;
}

export interface YtdTotals {
  ytd_deductible_consumed: number;
  ytd_ceiling_consumed: number;
}

export interface ClaimInput {
  claim_id: string;
  policy_id: string;
  billed_amount: number;
  service_date: Date;
}

export type ReasonCode =
  | 'APPROVED'
  | 'WAITING_PERIOD'
  | 'DEDUCTIBLE_NOT_MET'
  | 'ANNUAL_CEILING_REACHED'
  | 'PARTIAL_CEILING_CAP';

export interface ReimbursementResult {
  claim_id: string;
  reimbursement: number;
  reason: ReasonCode;
  deductible_applied: number;
  ytd_deductible_consumed: number;
  ytd_ceiling_consumed: number;
}
