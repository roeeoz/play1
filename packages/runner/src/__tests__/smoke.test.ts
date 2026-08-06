import { describe, it, expect } from "vitest";
import { runSettlement } from "../index";
import { ReasonCode } from "@claim-engine/types";
import type { ClaimResult } from "@claim-engine/types";

const policy = {
  policy_id: "POL-001",
  coverage_start_date: "2024-01-01",
  waiting_period_days: 30,
  coverage_percentage: 80,
  annual_deductible: 1000,
  annual_ceiling: 5000,
};

const claims = [
  {
    claim_id: "C-001",
    billed_amount: 500,
    service_date: "2024-01-15",
    submission_date: "2024-01-15",
  },
  {
    claim_id: "C-002",
    billed_amount: 600,
    service_date: "2024-02-15",
    submission_date: "2024-02-15",
  },
  {
    claim_id: "C-003",
    billed_amount: 800,
    service_date: "2024-03-01",
    submission_date: "2024-03-01",
  },
  {
    claim_id: "C-004",
    billed_amount: 10000,
    service_date: "2024-06-01",
    submission_date: "2024-06-01",
  },
  {
    claim_id: "C-005",
    billed_amount: 2000,
    service_date: "2024-09-01",
    submission_date: "2024-09-01",
  },
];

const expected: ClaimResult[] = [
  {
    claim_id: "C-001",
    reason_code: ReasonCode.WAITING_PERIOD_ACTIVE,
    reimbursed_amount: 0,
    patient_responsibility: 500,
    deductible_applied: 0,
    ceiling_remaining: 5000,
  },
  {
    claim_id: "C-002",
    reason_code: ReasonCode.OK,
    reimbursed_amount: 0,
    patient_responsibility: 600,
    deductible_applied: 600,
    ceiling_remaining: 5000,
  },
  {
    claim_id: "C-003",
    reason_code: ReasonCode.OK,
    reimbursed_amount: 320,
    patient_responsibility: 480,
    deductible_applied: 400,
    ceiling_remaining: 4680,
  },
  {
    claim_id: "C-004",
    reason_code: ReasonCode.PARTIALLY_CAPPED,
    reimbursed_amount: 4680,
    patient_responsibility: 5320,
    deductible_applied: 0,
    ceiling_remaining: 0,
  },
  {
    claim_id: "C-005",
    reason_code: ReasonCode.ANNUAL_CEILING_EXHAUSTED,
    reimbursed_amount: 0,
    patient_responsibility: 2000,
    deductible_applied: 0,
    ceiling_remaining: 0,
  },
];

describe("runSettlement smoke test", () => {
  const results = runSettlement({ policy, claims });

  it("returns exactly 5 results", () => {
    expect(results).toHaveLength(5);
  });

  expected.forEach((exp, i) => {
    it(`claim ${i} (${exp.reason_code}) matches expected`, () => {
      expect(results[i]).toEqual(exp);
    });
  });
});
