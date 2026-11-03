# Feature Specification Document

## 1. Feature Overview

**Summary:** Add a CLI subcommand to testbed-utils that accepts two ISO 8601 dates (optionally with a trailing Z) and prints the absolute number of calendar days between them, backed by a new documented and tested pure-Python helper function in `dateutils.py`.

**Problem statement:** testbed-utils users currently have no CLI command to compute the number of days between two dates. The existing `days_between` function in `dateutils.py` is an internal helper that takes `date` objects and returns a signed integer — it is not user-facing, does not accept string input, and does not handle validation or the absolute-value semantics this feature requires.

**Target users:** testbed-utils CLI users (developers and maintainers) who need a quick, scriptable way to compute the calendar-day distance between two dates without writing Python.

---

## 2. Goals & Non-Goals

### Goals
- Provide a CLI subcommand that computes and prints the absolute number of calendar days between two ISO 8601 date inputs.
- Accept dates in either order and with an optional trailing Z.
- Validate inputs gracefully: invalid dates produce an error message and a non-zero exit, never an unhandled exception.
- Ship a public helper function in `dateutils.py` with a docstring containing a runnable example.
- Deliver pytest coverage for the happy path, the zero-day boundary, and the invalid-date error case.
- Establish the CLI entry point and parsing contract that story s2 (weekday listing) will extend.

### Non-Goals
- Listing weekdays in the date range (delivered by story s2, which depends on this story).
- Modifying the existing `days_between` function or any other existing business-day logic in `dateutils.py`.
- Changing the CI gate mechanism or the `CI_FAIL` marker.
- Introducing any new runtime dependency; the feature uses only the Python standard library.
- Time-of-day or timezone-offset arithmetic — a trailing Z is treated as a date-only marker, not a timezone invitation.

---

## 3. Functional Requirements

- **FR1 — Date parsing:** The subcommand accepts exactly two positional arguments, each an ISO 8601 date string (YYYY-MM-DD). An optional trailing Z on either argument (e.g. `2024-01-10Z`) is accepted and treated identically to the same date without the Z.
- **FR2 — Absolute day count:** The subcommand computes and prints the absolute number of calendar days between the two parsed dates. The two dates may be supplied in either chronological order; the result is always non-negative. Two identical dates yield a count of 0.
- **FR3 — Error handling:** When either argument is not a valid ISO 8601 date, the subcommand prints an error message to stderr and exits with a non-zero status code. No unhandled exception or Python traceback is shown to the user.
- **FR4 — Help text:** Invoking the subcommand with `--help` prints a one-line summary of what it does and exits with status 0.
- **FR5 — Public helper function:** A new public function is added to `dateutils.py` that accepts two date strings (ISO 8601, optional trailing Z), validates them, and returns the absolute day count as an integer. It raises an appropriate exception on invalid input. It carries a docstring with a runnable example.
- **FR6 — Console-script registration:** The subcommand is registered as a new entry in `pyproject.toml` `[project.scripts]`, following the repository's established naming and wiring conventions.
- **FR7 — Test coverage:** Pytest cases exist for the new public function covering: (a) happy path with two valid dates, (b) zero-day boundary with identical dates, (c) invalid-date error case. CLI-level tests cover the same scenarios through the entry point.
- **FR8 — No new dependencies:** The implementation uses only the Python standard library. No new entry is added to `[project.dependencies]` or `[project.optional-dependencies]`.

---

## 4. User Experience & Behavior

### Key user flow
1. User invokes the subcommand from a terminal, passing two ISO date strings as positional arguments.
2. The subcommand prints the absolute calendar-day count between the two dates to stdout and exits with status 0.

### Edge cases the user observes
- **Identical dates:** Output shows a count of 0; exit status 0.
- **Reversed order:** Dates supplied as `2024-01-10 2024-01-01` produce the same count as `2024-01-01 2024-01-10`.
- **Trailing Z:** `2024-01-10Z` is silently accepted as `2024-01-10`.
- **Invalid input:** A human-readable error message is printed to stderr (no Python traceback); exit status is non-zero.
- **Help:** `--help` prints a one-line summary of the subcommand's purpose; exit status 0.

### Output format
Plain text to stdout. The exact wording (e.g. whether the line reads `9` or `9 days`) is a design detail deferred to STRUCTURE; the product requirement is that the day count is printed as a single line of plain text.

---

## 5. Acceptance Criteria

1. **AC1 — Happy path (either order):** Given two valid ISO dates (e.g. `2024-01-01` and `2024-01-10`) supplied in either order, the subcommand prints the correct absolute day count between them and exits with status 0.
2. **AC2 — Zero-day boundary:** Given two identical ISO dates, the subcommand prints a day count of 0 and exits with status 0.
3. **AC3 — Invalid date error:** Given a date argument that is not a valid ISO 8601 date, the subcommand prints an error message to stderr and exits with a non-zero status, without raising an unhandled exception or showing a traceback.
4. **AC4 — Trailing Z acceptance:** Given an ISO date argument with a trailing Z (e.g. `2024-01-10Z`), the subcommand parses it as the same calendar date as `2024-01-10` and includes it correctly in the day count.
5. **AC5 — Help text:** Invoking the subcommand with `--help` prints a one-line summary of what it does and exits with status 0.
6. **AC6 — Docstring and tests:** The new public day-count function has a docstring containing a runnable example, and pytest cases exist for the happy path, the zero-day boundary, and the invalid-date error case.
7. **AC7 — Change footprint:** The change touches only `dateutils.py`, its tests, and the console-script entry point (including the `pyproject.toml` scripts entry and `__init__.py` re-export, per established repo practice), within 300 changed lines total.

---

## 6. Dependencies & Constraints (product-level)

- **Dependency on existing repo patterns:** The CLI entry point must follow the established `argparse` + `[project.scripts]` pattern used by the other testbed-utils subcommands.
- **Contract for s2:** This story establishes the date-parsing and validation logic that story s2 (weekday listing) will reuse. The public function's interface and the CLI's argument structure form the contract s2 builds on.
- **Stdlib-only constraint:** No new runtime dependency (epic constraint, aligned with engineering requirement R2).
- **CPython 3.10+ target:** The implementation must work on CPython 3.10 as declared in `pyproject.toml` (R1).
- **No secrets:** No tokens, passwords, or personal data in code, tests, or commits (R4).
- **Traceability:** The pull request must name this story and the epic PRD (R10 / R7).
- **CI gate untouched:** Neither the `test` job nor the `gate` job in CI is modified.

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, the exact public function signature and name, argument-parsing details, error-handling strategy, the trailing-Z stripping mechanism, output format wording, `__init__.py` wiring, and the test file organization are all deferred to the STRUCTURE stage. Technical constraints the product imposes: stdlib-only, CPython 3.10 compatibility, absolute (not signed) return value, and the established console-script pattern in the repo.

---

## 8. Open Questions

- **OQ1 — Exact output wording:** Whether the day-count line reads `9`, `9 days`, `Days: 9`, or another format is unspecified by the epic (A3 says "one line for the day count"). This is a low-risk design choice deferred to STRUCTURE.
- **OQ2 — Coverage measurement:** The epic requires module coverage at or above 90%, but no coverage tool is configured in the repo. The story delivers the required test cases (happy path, boundary, error); the numeric coverage assertion cannot be enforced until tooling is added (a pre-existing gap, not introduced by this story).
