import { describe, it, expect } from "vitest";
import {
  parseAndValidatePolicy,
  parseAndValidateClaim,
  ValidationError,
} from "../index.js";

const validPolicy = {
  policy_id: "POL-001",
  coverage_start_date: "2024-01-01",
  waiting_period_days: 30,
  coverage_percentage: 80,
  annual_deductible: 500,
  annual_ceiling: 10000,
};

const validClaim = {
  claim_id: "CLM-001",
  billed_amount: 250.0,
  service_date: "2024-06-15",
  submission_date: "2024-06-20",
};

function without(
  obj: Record<string, unknown>,
  key: string,
): Record<string, unknown> {
  const result = { ...obj };
  delete result[key];
  return result;
}

function catchValidationError(fn: () => unknown): ValidationError {
  let caught: unknown;
  try {
    fn();
  } catch (e) {
    caught = e;
  }
  if (!(caught instanceof ValidationError)) {
    throw new Error(`Expected ValidationError but got: ${String(caught)}`);
  }
  return caught;
}

// Scenario 1: Valid policy returns typed object matching input exactly
describe("parseAndValidatePolicy", () => {
  it("returns a Policy matching input values with no extra properties", () => {
    const result = parseAndValidatePolicy(validPolicy);
    expect(result).toEqual(validPolicy);
    expect(Object.keys(result)).toEqual([
      "policy_id",
      "coverage_start_date",
      "waiting_period_days",
      "coverage_percentage",
      "annual_deductible",
      "annual_ceiling",
    ]);
  });

  // Scenario 3: null
  it("throws with field '$root' for null", () => {
    const err = catchValidationError(() => parseAndValidatePolicy(null));
    expect(err.field).toBe("$root");
  });

  // Scenario 4: non-object primitives
  it("throws with field '$root' for a number", () => {
    const err = catchValidationError(() => parseAndValidatePolicy(42));
    expect(err.field).toBe("$root");
  });

  it("throws with field '$root' for a string", () => {
    const err = catchValidationError(() => parseAndValidatePolicy("string"));
    expect(err.field).toBe("$root");
  });

  it("throws with field '$root' for a boolean", () => {
    const err = catchValidationError(() => parseAndValidatePolicy(true));
    expect(err.field).toBe("$root");
  });

  // Scenario 5: array
  it("throws with field '$root' for an array", () => {
    const err = catchValidationError(() => parseAndValidatePolicy([]));
    expect(err.field).toBe("$root");
  });

  // Scenario 6: each policy field missing individually
  it("throws naming 'policy_id' when policy_id is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy(without(validPolicy, "policy_id")),
    );
    expect(err.field).toBe("policy_id");
  });

  it("throws naming 'coverage_start_date' when coverage_start_date is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy(without(validPolicy, "coverage_start_date")),
    );
    expect(err.field).toBe("coverage_start_date");
  });

  it("throws naming 'waiting_period_days' when waiting_period_days is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy(without(validPolicy, "waiting_period_days")),
    );
    expect(err.field).toBe("waiting_period_days");
  });

  it("throws naming 'coverage_percentage' when coverage_percentage is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy(without(validPolicy, "coverage_percentage")),
    );
    expect(err.field).toBe("coverage_percentage");
  });

  it("throws naming 'annual_deductible' when annual_deductible is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy(without(validPolicy, "annual_deductible")),
    );
    expect(err.field).toBe("annual_deductible");
  });

  it("throws naming 'annual_ceiling' when annual_ceiling is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy(without(validPolicy, "annual_ceiling")),
    );
    expect(err.field).toBe("annual_ceiling");
  });

  // Scenario 8: coverage_percentage bounds
  it("throws for coverage_percentage: -1", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy({ ...validPolicy, coverage_percentage: -1 }),
    );
    expect(err.field).toBe("coverage_percentage");
  });

  it("throws for coverage_percentage: 101", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy({ ...validPolicy, coverage_percentage: 101 }),
    );
    expect(err.field).toBe("coverage_percentage");
  });

  it("succeeds for coverage_percentage: 0", () => {
    expect(() =>
      parseAndValidatePolicy({ ...validPolicy, coverage_percentage: 0 }),
    ).not.toThrow();
  });

  it("succeeds for coverage_percentage: 100", () => {
    expect(() =>
      parseAndValidatePolicy({ ...validPolicy, coverage_percentage: 100 }),
    ).not.toThrow();
  });

  // Scenario 10: annual_deductible bounds
  it("throws for annual_deductible: -0.01", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy({ ...validPolicy, annual_deductible: -0.01 }),
    );
    expect(err.field).toBe("annual_deductible");
  });

  it("succeeds for annual_deductible: 0", () => {
    expect(() =>
      parseAndValidatePolicy({ ...validPolicy, annual_deductible: 0 }),
    ).not.toThrow();
  });

  // Scenario 11: waiting_period_days constraints
  it("throws for waiting_period_days: -1", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy({ ...validPolicy, waiting_period_days: -1 }),
    );
    expect(err.field).toBe("waiting_period_days");
  });

  it("succeeds for waiting_period_days: 0", () => {
    expect(() =>
      parseAndValidatePolicy({ ...validPolicy, waiting_period_days: 0 }),
    ).not.toThrow();
  });

  it("throws for waiting_period_days: 1.5 (non-integer)", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy({ ...validPolicy, waiting_period_days: 1.5 }),
    );
    expect(err.field).toBe("waiting_period_days");
  });

  // Scenario 12 & 13: date validation
  it("throws for coverage_start_date: '2024-02-30' (invalid calendar date)", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy({
        ...validPolicy,
        coverage_start_date: "2024-02-30",
      }),
    );
    expect(err.field).toBe("coverage_start_date");
  });

  it("throws for coverage_start_date: 'not-a-date'", () => {
    const err = catchValidationError(() =>
      parseAndValidatePolicy({
        ...validPolicy,
        coverage_start_date: "not-a-date",
      }),
    );
    expect(err.field).toBe("coverage_start_date");
  });

  // Scenario 14: extra fields ignored
  it("ignores unknown extra fields and returns only declared fields", () => {
    const withExtras = { ...validPolicy, extra_field: "surprise", foo: 42 };
    const result = parseAndValidatePolicy(withExtras);
    expect(result).toEqual(validPolicy);
    expect("extra_field" in result).toBe(false);
    expect("foo" in result).toBe(false);
  });
});

// Scenario 2: Valid claim returns typed object matching input exactly
describe("parseAndValidateClaim", () => {
  it("returns a Claim matching input values with no extra properties", () => {
    const result = parseAndValidateClaim(validClaim);
    expect(result).toEqual(validClaim);
    expect(Object.keys(result)).toEqual([
      "claim_id",
      "billed_amount",
      "service_date",
      "submission_date",
    ]);
  });

  // Scenario 3: null
  it("throws with field '$root' for null", () => {
    const err = catchValidationError(() => parseAndValidateClaim(null));
    expect(err.field).toBe("$root");
  });

  // Scenario 4: non-object primitives
  it("throws with field '$root' for a number", () => {
    const err = catchValidationError(() => parseAndValidateClaim(42));
    expect(err.field).toBe("$root");
  });

  it("throws with field '$root' for a string", () => {
    const err = catchValidationError(() => parseAndValidateClaim("string"));
    expect(err.field).toBe("$root");
  });

  it("throws with field '$root' for a boolean", () => {
    const err = catchValidationError(() => parseAndValidateClaim(true));
    expect(err.field).toBe("$root");
  });

  // Scenario 5: array
  it("throws with field '$root' for an array", () => {
    const err = catchValidationError(() => parseAndValidateClaim([]));
    expect(err.field).toBe("$root");
  });

  // Scenario 7: each claim field missing individually
  it("throws naming 'claim_id' when claim_id is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim(without(validClaim, "claim_id")),
    );
    expect(err.field).toBe("claim_id");
  });

  it("throws naming 'billed_amount' when billed_amount is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim(without(validClaim, "billed_amount")),
    );
    expect(err.field).toBe("billed_amount");
  });

  it("throws naming 'service_date' when service_date is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim(without(validClaim, "service_date")),
    );
    expect(err.field).toBe("service_date");
  });

  it("throws naming 'submission_date' when submission_date is missing", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim(without(validClaim, "submission_date")),
    );
    expect(err.field).toBe("submission_date");
  });

  // Scenario 9: billed_amount constraints
  it("throws for billed_amount: 0", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim({ ...validClaim, billed_amount: 0 }),
    );
    expect(err.field).toBe("billed_amount");
  });

  it("throws for billed_amount: -5", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim({ ...validClaim, billed_amount: -5 }),
    );
    expect(err.field).toBe("billed_amount");
  });

  it("succeeds for billed_amount: 0.01", () => {
    expect(() =>
      parseAndValidateClaim({ ...validClaim, billed_amount: 0.01 }),
    ).not.toThrow();
  });

  // Date validation on service_date and submission_date
  it("throws for service_date: '2024-02-30' (invalid calendar date)", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim({ ...validClaim, service_date: "2024-02-30" }),
    );
    expect(err.field).toBe("service_date");
  });

  it("throws for service_date: 'not-a-date'", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim({ ...validClaim, service_date: "not-a-date" }),
    );
    expect(err.field).toBe("service_date");
  });

  it("throws for submission_date: '2024-02-30' (invalid calendar date)", () => {
    const err = catchValidationError(() =>
      parseAndValidateClaim({
        ...validClaim,
        submission_date: "2024-02-30",
      }),
    );
    expect(err.field).toBe("submission_date");
  });

  it("succeeds for service_date: '2024-02-29' (valid leap day)", () => {
    expect(() =>
      parseAndValidateClaim({ ...validClaim, service_date: "2024-02-29" }),
    ).not.toThrow();
  });

  // Scenario 14: extra fields ignored
  it("ignores unknown extra fields and returns only declared fields", () => {
    const withExtras = { ...validClaim, extra: "ignored", num: 99 };
    const result = parseAndValidateClaim(withExtras);
    expect(result).toEqual(validClaim);
    expect("extra" in result).toBe(false);
    expect("num" in result).toBe(false);
  });
});

// instanceof check
describe("ValidationError", () => {
  it("thrown errors satisfy instanceof ValidationError and instanceof Error", () => {
    const err = catchValidationError(() => parseAndValidatePolicy(null));
    expect(err).toBeInstanceOf(ValidationError);
    expect(err).toBeInstanceOf(Error);
  });

  it("exposes field as a directly readable property", () => {
    const err = new ValidationError("some_field", "test message");
    expect(err.field).toBe("some_field");
    expect(err.message).toBe("test message");
    expect(err.name).toBe("ValidationError");
  });
});
