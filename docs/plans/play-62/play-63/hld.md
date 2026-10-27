# High-Level Design — PLAY-63: testbed-hello --version

## 1. System Overview

- **What is being built:** A `--version` flag for the `testbed-hello` CLI that prints `0.1.0` to stdout and exits 0.
- **Problem:** No command-line way to discover the installed version of `testbed-hello`.
- **Key responsibility:** Extend the existing argparse-based CLI with a single version action.

## 2. Architecture Overview

- **Component:** `testbed_utils.hello` module — the sole module affected.
- **Boundary:** The change is confined to the `main()` function's argument parser setup.
- **External dependencies:** None. Uses only Python stdlib (`argparse`).
- **Repository:** `roeeoz/play1`.

## 3. Data Flow Design

1. User invokes `testbed-hello --version`.
2. `argparse` recognizes the `--version` action, prints `0.1.0` to stdout, raises `SystemExit(0)`.
3. Process terminates with exit code 0.

No async, no events, no state — a pure synchronous CLI action.

## 4. Component Breakdown

| Component | Responsibility | Repository |
|---|---|---|
| `src/testbed_utils/hello.py` | Register `--version` argument on the existing `ArgumentParser` | roeeoz/play1 |
| `tests/test_hello_cli.py` | Add `TestVersion` class covering all four acceptance scenarios | roeeoz/play1 |

## 5. Interface Contracts

- **CLI contract:** `testbed-hello --version` → stdout: `0.1.0\n`, exit code: 0, stderr: empty.
- No APIs, no events, no cross-repo contracts.

## 6. Key Technical Decisions

- **Use argparse's built-in `'version'` action** rather than manual `sys.argv` inspection. This is the idiomatic, minimal approach — one line, correct stdout/exit-code behavior, automatic inclusion in `--help`.
- **Hardcoded literal `"0.1.0"`** per the approved spec. No dynamic version reading.

## 7. Risks & Constraints

- **RK1 (accepted):** Hardcoded version may drift from `pyproject.toml` after a future release. Accepted by PO; deferred to a future epic.
- **`--help` output grows** to include a `--version` line. Existing tests assert properties (exit 0, description present, no greeting leakage) that remain true — no breakage.
