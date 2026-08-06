export enum ReasonCode {
  OK = "OK",
  WAITING_PERIOD_ACTIVE = "WAITING_PERIOD_ACTIVE",
  ANNUAL_CEILING_EXHAUSTED = "ANNUAL_CEILING_EXHAUSTED",
  PARTIALLY_CAPPED = "PARTIALLY_CAPPED",
}

export interface Policy {
  policy_id: string;
  coverage_start_date: string;
  waiting_period_days: number;
  coverage_percentage: number;
  annual_deductible: number;
  annual_ceiling: number;
}

export interface Claim {
  claim_id: string;
  billed_amount: number;
  service_date: string;
  submission_date: string;
}

export interface YtdState {
  year: number;
  deductible_consumed: number;
  ceiling_consumed: number;
}

export interface ClaimResult {
  claim_id: string;
  reimbursed_amount: number;
  patient_responsibility: number;
  reason_code: ReasonCode;
  deductible_applied: number;
  ceiling_remaining: number;
}
