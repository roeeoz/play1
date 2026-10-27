# Feature Specification Document

## 1. Feature Overview

**Summary.** Add a `--version` flag to the `testbed-hello` console script so that it prints the literal string `0.1.0` to standard output and exits with code 0.

**Problem statement.** Developers and automation agents using the `testbed-hello` script currently have no command-line way to discover which version is installed. They must inspect source files or package metadata, which is inconvenient and error-prone in automated pipelines.

**Target users / actors.** Developers and automation agents that invoke `testbed-hello` to verify which version of the script is present in an environment.

---

## 2. Goals & Non-Goals

### Goals

- G-A: A developer can run `testbed-hello --version` and see the version string printed to standard output, confirming the installed version without inspecting source or metadata.
- G-B: The flag follows the same convention the script already uses for `--help` — print a line to stdout and exit 0 — so version reporting is discoverable alongside usage help.
- G-C: All existing behavior of the script (no-args greeting, `--help`, error on unrecognized options) is preserved exactly.

### Non-Goals

- Reading the version dynamically from `pyproject.toml` or any other source at runtime. The version is the hardcoded literal `"0.1.0"`.
- Adding `--version` to any other console script in the repository (`pdf-extract`, `testbed-num-summary`, `guestbook`).
- Changing the script's behavior for any invocation other than `--version`.
- Creating additional console scripts, modules, or shell wrappers.

---

## 3. Functional Requirements

- **FR1 (traces to R1):** When invoked with `--version`, the `testbed-hello` script shall print exactly the string `0.1.0` to standard output and exit with code 0. Nothing shall be printed to standard error.
- **FR2 (traces to R2):** When invoked without `--version` — including no arguments, `--help`, positional text, or any unrecognized option — the script's behavior shall be identical to its current behavior: same output, same streams, same exit codes.

**Inputs:** The `--version` flag passed as a command-line argument to `testbed-hello`.

**Outputs:** The string `0.1.0` followed by a newline, printed to standard output.

**Edge cases:**
- No-arguments invocation continues to print `Hello, world!` and exit 0.
- `--help` continues to print the usage message and exit 0.
- Unrecognized options (e.g., `--bogus`) continue to print a usage error to standard error and exit with code 2.

---

## 4. User Experience & Behavior

**Key user flow:**
1. The user (developer or automation agent) runs `testbed-hello --version` in their terminal or CI pipeline.
2. The script prints `0.1.0` to standard output and exits immediately with code 0.
3. The user reads or captures the output to confirm the installed version.

**States the user observes:**
- *Before*: The script has no `--version` flag; invoking it with `--version` would cause an unrecognized-option error (exit 2).
- *After*: The script recognizes `--version`, prints the version string, and exits cleanly.

**User-facing edge cases:**
- If the user passes both `--version` and other arguments or flags, the behavior is determined by argparse's built-in precedence (version action takes priority and prints the version). This is standard CLI convention and requires no special product specification.
- All non-`--version` invocations produce exactly the same output and exit codes as today.

---

## 5. Acceptance Criteria

1. **Scenario 1 — Happy path: `--version` prints the version string and exits 0.** Given the `testbed-hello` console script is installed, when the user invokes it with the `--version` flag, then the script prints exactly `0.1.0` to standard output, and the script exits with code 0, and nothing is printed to standard error.

2. **Scenario 2 — Edge case: no-arguments behavior is unchanged.** Given the `testbed-hello` console script is installed, when the user invokes it with no arguments, then the script prints `Hello, world!` to standard output and exits with code 0, and the output and exit code are identical to the current behavior.

3. **Scenario 3 — Edge case: `--help` behavior is unchanged.** Given the `testbed-hello` console script is installed, when the user invokes it with `--help`, then the script prints its usage message to standard output and exits with code 0, and the usage message includes the one-line description, and the output and exit code are identical to the current behavior.

4. **Scenario 4 — Error case: unrecognized option is still rejected.** Given the `testbed-hello` console script is installed, when the user invokes it with an unrecognized option such as `--bogus`, then the script prints a usage error to standard error and exits with code 2, and the behavior is identical to the current behavior.

---

## 6. Dependencies & Constraints (product-level)

- **No external dependencies.** The feature requires no new runtime or test dependencies.
- **Traceability (engineering requirement R7):** The pull request must name PLAY-63 and the epic PRD.
- **Size guardrail (goal G3):** The change must not exceed 300 changed lines. Expected: well under 50.
- **CI gate (engineering requirement R3):** The pull request merges only with all required checks green (pytest suite passing).
- **Accepted risk RK1:** The hardcoded version string `0.1.0` may drift from the package version in `pyproject.toml` after a future release. This is accepted by the PO and deferred to a future epic.

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, implementation approach, data model, error-handling strategy, performance, security, and the PR-level breakdown are produced by the tech lead in the STRUCTURE stage from this approved product spec.

**Product-imposed technical constraints to carry forward:**
- The version string is the hardcoded literal `"0.1.0"` — it must not be read from `pyproject.toml` or any other source at runtime.
- The target file is `src/testbed_utils/hello.py`, registered as the `testbed-hello` console script in `pyproject.toml`.
- Tests belong in `tests/test_hello_cli.py`, using the existing test harness.

---

## 8. Open Questions

None. All product requirements are fully specified.
