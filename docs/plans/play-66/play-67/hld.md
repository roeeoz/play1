# High-Level Design — PLAY-67: Verify testbed-hello prints a usage line on --help and exits 0

## 1. System Overview

- **What is being built:** A verification pass confirming that `testbed-hello` meets the play1 discoverability standard (G2), with one assertion added to close the only gap found.
- **Problem:** The existing `--help` test asserts `"usage:" in stdout` but does not assert the program name "testbed-hello" appears in the output, as FR3 requires.
- **Key responsibility:** Close the assertion gap so the test suite fully verifies the discoverability contract.

## 2. Architecture Overview

- **No new components.** The script (`src/testbed_utils/hello.py`) and its test (`tests/test_hello_cli.py`) already exist.
- **Boundary:** Only `tests/test_hello_cli.py` is modified. `src/testbed_utils/hello.py` is consumed read-only — no change needed (argparse already sets `prog="testbed-hello"`).
- **External dependencies:** None new. pytest is already declared.

## 3. Data Flow Design

- `testbed-hello --help` → argparse prints `usage: testbed-hello [-h]` + description to stdout → `sys.exit(0)`.
- `testbed-hello` (no args) → prints `Hello, world!` to stdout → exits 0.
- Test helper `run_main()` patches `sys.argv`, captures stdout/stderr via `io.StringIO`, catches `SystemExit`.

## 4. Component Breakdown

| Component | Responsibility | Change | Repository |
|---|---|---|---|
| `src/testbed_utils/hello.py` | Console entry point | None — already satisfies FR1/FR2 | roeeoz/play1 |
| `tests/test_hello_cli.py` | CLI test suite | Add one assertion for program name | roeeoz/play1 |

## 5. Interface Contracts

- **CLI interface:** Unchanged. `testbed-hello --help` prints usage + description, exits 0. `testbed-hello` prints greeting, exits 0.
- **Test interface:** `run_main(args)` → `(exit_code, stdout, stderr)`. No change to this helper.

## 6. Key Technical Decisions

- **Two-commit structure (test-first):** Per developer request, the PR uses two commits: (1) add the assertion to the test, (2) adjust the script only if the test fails. Research indicates the script already passes, so the second commit may be unnecessary.
- **Add assertion to existing test rather than a new test method.** The `test_help` method already invokes `--help` and captures output; adding one `assert` line is the minimal, idiomatic change.
- **Assert substring `"testbed-hello"` rather than a full usage line regex.** The program name is the spec requirement; the exact format is an argparse implementation detail accepted per RK1.

## 7. Risks & Constraints

- **Risk:** Essentially none. The assertion is a pure string containment check on deterministic argparse output.
- **Constraint:** Must not modify `src/testbed_utils/hello.py` unless the new test assertion fails. `.factory/testing.md` notes "Shared fixture repo — don't touch `testbed_utils`" beyond in-scope modules, and the script needs no change.
- **CI:** `pytest` is the only gate. No linter, formatter, or type checker configured.
