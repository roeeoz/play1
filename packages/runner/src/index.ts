import { readFileSync } from "fs";
import { processClaims } from "@claim-engine/engine";
import {
  parseAndValidatePolicy,
  parseAndValidateClaim,
  ValidationError,
} from "@claim-engine/input";
import type { ClaimResult, Policy, Claim } from "@claim-engine/types";

export function runSettlement(input: unknown): ClaimResult[] {
  if (typeof input !== "object" || input === null || Array.isArray(input)) {
    throw new Error("Expected an object with 'policy' and 'claims'");
  }
  const obj = input as Record<string, unknown>;

  if (!Array.isArray(obj["claims"])) {
    throw new Error("'claims' must be an array");
  }

  const policy = parseAndValidatePolicy(obj["policy"]);
  const claims = (obj["claims"] as unknown[]).map((c) =>
    parseAndValidateClaim(c),
  );
  return processClaims(policy, claims);
}

function writeStderr(data: Record<string, unknown>): void {
  process.stderr.write(JSON.stringify(data) + "\n");
}

function main(): void {
  const filePath = process.argv[2];
  let rawText: string;
  try {
    rawText = filePath
      ? readFileSync(filePath, "utf8")
      : readFileSync(0, "utf8");
  } catch (e) {
    writeStderr({ error: "Read error", message: String(e) });
    process.exit(1);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(rawText);
  } catch (e) {
    writeStderr({ error: "Invalid JSON", message: (e as SyntaxError).message });
    process.exit(1);
  }

  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    writeStderr({
      error: "Invalid input structure",
      field: "$root",
      message: "Expected an object with 'policy' and 'claims'",
    });
    process.exit(1);
  }

  const obj = parsed as Record<string, unknown>;

  if (!Array.isArray(obj["claims"])) {
    writeStderr({
      error: "Invalid input structure",
      field: "claims",
      message: "'claims' must be an array",
    });
    process.exit(1);
  }

  let policy: Policy;
  try {
    policy = parseAndValidatePolicy(obj["policy"]);
  } catch (e) {
    if (e instanceof ValidationError) {
      writeStderr({
        error: "Policy validation error",
        field: e.field,
        message: e.message,
      });
      process.exit(1);
    }
    throw e;
  }

  const rawClaims = obj["claims"] as unknown[];
  const claims: Claim[] = [];
  for (let i = 0; i < rawClaims.length; i++) {
    try {
      claims.push(parseAndValidateClaim(rawClaims[i]));
    } catch (e) {
      if (e instanceof ValidationError) {
        writeStderr({
          error: "Claim validation error",
          index: i,
          field: e.field,
          message: e.message,
        });
        process.exit(1);
      }
      throw e;
    }
  }

  const results = processClaims(policy, claims);
  process.stdout.write(JSON.stringify(results, null, 2) + "\n");
  process.exit(0);
}

// Only invoke CLI when this file is the main entry point (CJS), not when imported
if (typeof require !== "undefined" && require.main === module) {
  main();
}
