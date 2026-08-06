import type { Policy, Claim } from "@claim-engine/types";

export class ValidationError extends Error {
  constructor(
    public readonly field: string,
    message: string,
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

const DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;

function isValidDate(str: string): boolean {
  if (!DATE_REGEX.test(str)) return false;
  const d = new Date(str);
  if (isNaN(d.getTime())) return false;
  const [year, month, day] = str.split("-").map(Number);
  return (
    d.getUTCFullYear() === year &&
    d.getUTCMonth() + 1 === month &&
    d.getUTCDate() === day
  );
}

function assertPlainObject(
  raw: unknown,
): asserts raw is Record<string, unknown> {
  if (raw === null || Array.isArray(raw) || typeof raw !== "object") {
    throw new ValidationError("$root", "Input must be a plain object");
  }
}

export function parseAndValidatePolicy(raw: unknown): Policy {
  assertPlainObject(raw);

  const obj = raw as Record<string, unknown>;

  if (typeof obj["policy_id"] !== "string" || obj["policy_id"].trim() === "") {
    throw new ValidationError(
      "policy_id",
      "policy_id must be a non-empty string",
    );
  }

  if (
    typeof obj["coverage_start_date"] !== "string" ||
    !isValidDate(obj["coverage_start_date"])
  ) {
    throw new ValidationError(
      "coverage_start_date",
      "coverage_start_date must be a valid YYYY-MM-DD date",
    );
  }

  if (
    typeof obj["waiting_period_days"] !== "number" ||
    !isFinite(obj["waiting_period_days"]) ||
    obj["waiting_period_days"] % 1 !== 0 ||
    obj["waiting_period_days"] < 0
  ) {
    throw new ValidationError(
      "waiting_period_days",
      "waiting_period_days must be a finite non-negative integer",
    );
  }

  if (
    typeof obj["coverage_percentage"] !== "number" ||
    !isFinite(obj["coverage_percentage"]) ||
    obj["coverage_percentage"] < 0 ||
    obj["coverage_percentage"] > 100
  ) {
    throw new ValidationError(
      "coverage_percentage",
      "coverage_percentage must be a finite number between 0 and 100 inclusive",
    );
  }

  if (
    typeof obj["annual_deductible"] !== "number" ||
    !isFinite(obj["annual_deductible"]) ||
    obj["annual_deductible"] < 0
  ) {
    throw new ValidationError(
      "annual_deductible",
      "annual_deductible must be a finite non-negative number",
    );
  }

  if (
    typeof obj["annual_ceiling"] !== "number" ||
    !isFinite(obj["annual_ceiling"]) ||
    obj["annual_ceiling"] < 0
  ) {
    throw new ValidationError(
      "annual_ceiling",
      "annual_ceiling must be a finite non-negative number",
    );
  }

  return {
    policy_id: obj["policy_id"],
    coverage_start_date: obj["coverage_start_date"],
    waiting_period_days: obj["waiting_period_days"],
    coverage_percentage: obj["coverage_percentage"],
    annual_deductible: obj["annual_deductible"],
    annual_ceiling: obj["annual_ceiling"],
  };
}

export function parseAndValidateClaim(raw: unknown): Claim {
  assertPlainObject(raw);

  const obj = raw as Record<string, unknown>;

  if (typeof obj["claim_id"] !== "string" || obj["claim_id"].trim() === "") {
    throw new ValidationError(
      "claim_id",
      "claim_id must be a non-empty string",
    );
  }

  if (
    typeof obj["billed_amount"] !== "number" ||
    !isFinite(obj["billed_amount"]) ||
    obj["billed_amount"] <= 0
  ) {
    throw new ValidationError(
      "billed_amount",
      "billed_amount must be a finite strictly positive number",
    );
  }

  if (
    typeof obj["service_date"] !== "string" ||
    !isValidDate(obj["service_date"])
  ) {
    throw new ValidationError(
      "service_date",
      "service_date must be a valid YYYY-MM-DD date",
    );
  }

  if (
    typeof obj["submission_date"] !== "string" ||
    !isValidDate(obj["submission_date"])
  ) {
    throw new ValidationError(
      "submission_date",
      "submission_date must be a valid YYYY-MM-DD date",
    );
  }

  return {
    claim_id: obj["claim_id"],
    billed_amount: obj["billed_amount"],
    service_date: obj["service_date"],
    submission_date: obj["submission_date"],
  };
}
