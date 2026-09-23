# Feature Specification Document

## 1. Feature Overview

**Summary:** Add a new `business_days_between` helper function to the testbed-utils `dateutils` module, alongside the existing `days_between`, `is_weekend`, and `humanize_delta` helpers. It counts the number of Monday-through-Friday (business) days within the span between two dates, and ships with automated pytest coverage.

**Problem statement:** The upcoming `date-span` CLI (US-02) and any future caller need a reusable, tested way to compute business-day counts between two dates, without each caller re-implementing weekday-counting logic.

**Target users / actors:** Developers maintaining or extending testbed-utils. This story's direct "user" is a developer calling the helper from code (the future `date-span` CLI, or any other future caller) — there is no end-user-facing surface in this story.

---

## 2. Goals & Non-Goals

### Goals
- Provide a `business_days_between` helper that returns the count of business days (Mon–Fri) within the span between two dates.
- Match all five pinned scenarios in the acceptance criteria exactly (full week = 5, weekend-only = 0, single business day = 1, identical dates = 0, reversed order = same value as chronological order).
- Ship with automated pytest coverage exercising all five scenarios.

### Non-Goals
- Building the `date-span` console script or its `--json` output mode (US-02).
- README documentation (US-03).
- Timezone-aware handling, holiday calendars, or date-range inputs other than two calendar dates.
- Validating or rejecting reversed date order — explicitly resolved as "accept either order, return the same count" per acceptance criterion 5.

---

## 3. Functional Requirements

- **FR1:** `business_days_between` shall accept a start date and an end date and return the integer count of weekdays (Monday–Friday) within the span. The counting convention is fully determined by the acceptance criteria's concrete examples (see §5): the count behaves as a half-open span, consistent with how the existing `days_between` helper counts whole days between two dates — a Monday-to-following-Monday span (7 calendar days) yields 5 business days, not 4 or 6.
- **FR2:** `business_days_between` shall return `0` when the span falls entirely on a weekend.
- **FR3:** `business_days_between` shall return `0` when the start and end dates are identical.
- **FR4:** `business_days_between` shall return the same value regardless of whether the start/end arguments are given in chronological or reversed order.
- **FR5:** The `business_days_between` helper shall be added to the `dateutils` module alongside the existing `days_between`, `is_weekend`, and `humanize_delta` helpers, without modifying those existing helpers.
- **FR6:** Automated pytest tests shall cover: full business week, weekend-only span, single business day, identical dates, and reversed date order — each asserting the exact value required by the acceptance criteria.

**Inputs:** two dates representing the span endpoints (exact parameter type is a technical/API decision — see §7/§8).
**Outputs:** a single integer: the business-day count.
**Core workflow:** a caller invokes `business_days_between(start, end)` and receives the integer count.
**Edge cases covered:** identical dates, reversed argument order, weekend-only span (all pinned by acceptance criteria in §5).

---

## 4. User Experience & Behavior

This story has no end-user-facing UI, CLI, or visual surface. Its "user" is another piece of code (the future `date-span` CLI from US-02, or any other future caller) invoking the helper directly. There is no console output, output formatting, or interaction affordance associated with this story — those belong to US-02 and US-03. The only observable behavior is the function's return value under the scenarios enumerated in §5.

---

## 5. Acceptance Criteria

1. **AC1 — Happy path, full business week:** Given start = 2024-01-01 (Monday) and end = 2024-01-08 (the following Monday), `business_days_between(2024-01-01, 2024-01-08)` returns `5`.
2. **AC2 — Boundary, weekend-only span:** Given start = 2024-01-06 (Saturday) and end = 2024-01-07 (Sunday), `business_days_between(2024-01-06, 2024-01-07)` returns `0`.
3. **AC3 — Boundary, single business day:** Given start = 2024-01-01 (Monday) and end = 2024-01-02 (Tuesday), `business_days_between(2024-01-01, 2024-01-02)` returns `1`.
4. **AC4 — Edge case, identical dates:** Given the same date passed as both start and end, `business_days_between` returns `0`.
5. **AC5 — Edge case, reversed date order:** Given a start date chronologically after the end date, `business_days_between` returns the same value as when called with the dates in chronological order.
6. **AC6 — Testable, automated coverage:** Running the project's pytest suite includes passing tests for all five scenarios above (AC1–AC5).
7. **AC7 — Scope boundary:** This story introduces no `date-span` console script, no `--json` output mode, and no README changes — those remain scoped to US-02 and US-03 respectively.

---

## 6. Dependencies & Constraints (product-level)

- Depends on the existing `dateutils` module (`days_between`, `is_weekend`, `humanize_delta`) remaining present and unchanged — stated precondition.
- This helper's name and its behavior under the five pinned scenarios form the contract that the subsequent US-02 (`date-span` CLI) will consume; any behavioral change after this story merges is a breaking change for that dependent story.
- No new third-party dependency is introduced (epic-level constraint carried through to this story).

---

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. Flagged for the STRUCTURE stage's attention:
- The parameter type for `start`/`end` (native `date` objects vs. ISO date strings) is not stated in the story text. The existing sibling helpers (`days_between`, `is_weekend`) take `date` objects, but the epic's to-be process description implies the CLI parses ISO strings before calling helpers — STRUCTURE should resolve this signature.
- Whether `business_days_between` should be re-exported at the package level (`__init__.py`) alongside its sibling helpers, matching the existing convention for `days_between`/`is_weekend`/`humanize_delta`.
- The internal algorithm/implementation approach for weekday counting.

---

## 8. Open Questions (if any remain)

- *(For STRUCTURE, non-blocking)* Should `business_days_between`'s parameters be typed as `date` objects (matching sibling helpers' signatures) or ISO strings (matching the CLI's parse-first flow described in the epic)? This does not block this story's acceptance criteria, which are expressed in terms of concrete date values regardless of representation, but it is a contract STRUCTURE must pin down before US-02 can be built against it.
- *(For STRUCTURE, non-blocking)* Should the new helper be added to `dateutils`'s package-level export list for consistency with its siblings?
