# Feature Specification Document

## 1. Feature Overview

**Summary:** Verify that the existing `testbed-hello` console script satisfies the play1 discoverability standard: it answers `--help` with a one-line usage summary containing the program name and exits 0, plain invocation retains its current greeting, and the project's test suite covers the `--help` behavior.

**Problem statement:** Developers and agents working with the play1 testbed need to discover available console scripts and their usage without reading source code. The discoverability standard (G2 in "play1 — goals and success metrics") requires every console script to answer `--help` with a one-line summary and exit 0. This story verifies `testbed-hello` meets that standard and that a test covers it.

**Target users / actors:** Developers or agents working with the play1 testbed who need to discover available console scripts and their usage.

---

## 2. Goals & Non-Goals

### Goals
- Confirm that `testbed-hello --help` prints a usage line containing the program name "testbed-hello" to stdout and exits with code 0.
- Confirm that `testbed-hello` invoked without arguments prints its current greeting output unchanged and exits with code 0.
- Confirm that the project's test suite includes a test that invokes `testbed-hello --help`, asserts stdout contains a usage line, and asserts exit code 0.
- If any of the above are not yet satisfied, make the minimal change to satisfy them.

### Non-Goals
- Adding any flag other than `--help` — no new arguments, options, or subcommands.
- Modifying any other console script in the repository — only `testbed-hello` is in scope.
- Packaging, distribution, or installation changes.
- Rewriting the script from Python to bash or any other language.
- Changing the script's greeting behavior.

---

## 3. Functional Requirements

- **FR1 (traces to R1):** When invoked with `--help`, `testbed-hello` shall print a usage line containing the program name "testbed-hello" to stdout and exit with code 0.
- **FR2 (traces to R2):** When invoked without arguments, `testbed-hello` shall produce its current greeting output ("Hello, world!\n") unchanged to stdout and exit with code 0.
- **FR3 (traces to R3):** The project's test suite shall include a test that invokes `testbed-hello` with `--help`, asserts that stdout contains a usage line including the program name, and asserts that the exit code is 0.

**Inputs:** Command-line invocation of `testbed-hello` with `--help` or with no arguments.

**Outputs:**
- With `--help`: a usage line on stdout containing "testbed-hello", exit code 0.
- Without arguments: the greeting "Hello, world!\n" on stdout, exit code 0.

**Edge cases:**
- The argument parser may render the usage line as `usage: testbed-hello [-h]` rather than `usage: testbed-hello [--help]`. Per RK1, the parser's default format is accepted as satisfying the requirement because `-h` and `--help` are the short and long forms of the same flag.

---

## 4. User Experience & Behavior

**Key user flow:**
1. A developer or agent invokes `testbed-hello --help` at the command line.
2. The script prints a usage line (e.g., `usage: testbed-hello [-h]`) and a brief description to stdout.
3. The script exits with code 0.
4. The developer now knows the script's name and invocation without reading source code.

**Plain invocation flow:**
1. A developer or agent invokes `testbed-hello` without arguments.
2. The script prints "Hello, world!" to stdout.
3. The script exits with code 0.

**States the user observes:**
- `--help` invocation: usage summary printed, shell returns to prompt with exit code 0.
- Plain invocation: greeting printed, shell returns to prompt with exit code 0.

---

## 5. Acceptance Criteria

1. **Scenario 1 — Happy path: --help prints a usage summary.** Given the testbed-hello console script is installed, When a user invokes `testbed-hello --help`, Then stdout contains a usage line that includes the program name "testbed-hello", And the exit code is 0.

2. **Scenario 2 — Happy path: plain invocation prints the current greeting.** Given the testbed-hello console script is installed, When a user invokes `testbed-hello` without arguments, Then stdout prints the script's current greeting output unchanged ("Hello, world!\n"), And the exit code is 0.

3. **Scenario 3 — Edge case: a test covers the --help behavior.** Given the project's test suite, When the test suite runs, Then a test that invokes `testbed-hello` with `--help` passes, And the test asserts that stdout contains a usage line including the program name and that the exit code is 0.

---

## 6. Dependencies & Constraints (product-level)

**Dependencies:**
- The `testbed-hello` console entry point exists in the repository (`pyproject.toml` line 17, `src/testbed_utils/hello.py`).
- pytest is available as the test runner (`pyproject.toml` under the test extra).

**Constraints:**
- The change must not exceed 300 changed lines (G3).
- The test must be pure — no network, clock, or filesystem dependency outside test fixtures (G4).
- The test job must finish in under 60 seconds (G4).
- No secrets in the repository (R4).
- The pull request must name the story (PLAY-67) and its Epic PRD for traceability (R7).
- CI must be green before merge (R3).

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, data model, error-handling strategy, and implementation approach are deferred to the STRUCTURE stage. The product constraint is that the existing Python console entry point using argparse is the implementation; no language or framework change is in scope.

---

## 8. Open Questions

None — all functional requirements, acceptance criteria, and scope boundaries are fully specified by the story, the Epic PRD, and the intake assessment.
