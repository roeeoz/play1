export enum ReasonCode {
  OK = 'OK',
  WAITING_PERIOD_ACTIVE = 'WAITING_PERIOD_ACTIVE',
  ANNUAL_CEILING_EXHAUSTED = 'ANNUAL_CEILING_EXHAUSTED',
  PARTIALLY_CAPPED = 'PARTIALLY_CAPPED',
}

export interface Policy {
  coverage_start_date: string;
  waiting_period_days: number;
  annual_deductible: number;
  coverage_percentage: number;
  annual_ceiling: number;
}

export interface Claim {
  claim_id: string;
  service_date: string;
  billed_amount: number;
}

export interface YtdState {
  year: number;
  deductible_consumed: number;
  ceiling_consumed: number;
}

export interface ClaimResult {
  claim_id: string;
  reason_code: ReasonCode;
  reimbursed_amount: number;
  patient_responsibility: number;
  deductible_applied: number;
  ceiling_remaining: number;
}
