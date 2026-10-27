# Implementation plan — PLAY-63: testbed-hello prints its version when invoked with --version

## Context

PLAY-63 adds a `--version` flag to the `testbed-hello` console script in the `roeeoz/play1` repository (branch `halo/feat/play-63`). When invoked with `--version` the script prints `0.1.0` to stdout and exits 0; all other invocations are unchanged. The acceptance criteria cover the happy path (`--version`), two preservation scenarios (no-args, `--help`), and one error scenario (`--bogus`). The approved `spec.md`, `hld.md` and `work-items.md` sit in `docs/plans/play-62/play-63/` beside this file.

## Research findings

**Change surface.** The sole production file is `src/testbed_utils/hello.py` (24 lines). The `main()` function at `hello.py:20-23` creates an `ArgumentParser`, calls `parse_args()`, and prints the greeting. The parser currently has no explicit arguments — only the implicit `--help`. Adding a `--version` action requires one `parser.add_argument` call between parser construction (`hello.py:21`) and `parse_args()` (`hello.py:22`).

**Test surface.** `tests/test_hello_cli.py` (52 lines) contains three test classes (`TestGreeting`, `TestHelp`, `TestBadOption`) using a `run_main` helper (`test_hello_cli.py:12-22`) that patches `sys.argv`, captures stdout/stderr via `redirect_stdout`/`redirect_stderr`, and catches `SystemExit`. The helper already returns `(exit_code, stdout, stderr)`, which is exactly the interface a new `TestVersion` class needs. argparse's built-in `'version'` action raises `SystemExit(0)`, so `run_main` will capture it correctly.

**Console script registration.** `pyproject.toml:17` registers `testbed-hello = "testbed_utils.hello:main"`. No change needed.

**Package version.** `pyproject.toml:7` declares `version = "0.1.0"`. The spec mandates a hardcoded literal `"0.1.0"` — no dynamic reading.

**Canonical gate.** `.factory/testing.md` declares `test-gate: pytest`. The CI workflow (`.github/workflows/ci.yml`) runs `pip install -e ".[test]"` then `pytest` on Python 3.12 / ubuntu-latest, with workflow-level `permissions: contents: read`. No linter, formatter, or type checker is configured.

**Existing test behavior.** `TestBadOption` parametrizes over `["--bogus", "-x", "extra"]` and asserts exit code 2, empty stdout, and `"usage:"` + `"error"` in stderr. Positional arguments like `"extra"` are already tested as unrecognized. After adding `--version`, argparse will still reject these identically.

**`--help` output.** Adding a `'version'` action will append a `--version` line to the help text. The existing `TestHelp` asserts `"usage:" in stdout`, `_DESCRIPTION in " ".join(stdout.split())`, and `"Hello, world!" not in stdout` — all remain true with the extra line.

**No unknowns remain.**

## Locked decisions and assumptions

**Locked decisions:**

- The version string is the hardcoded literal `"0.1.0"` — not read from `pyproject.toml` or any other source at runtime (spec.md §3, §7; hld.md §6).
- The target file is `src/testbed_utils/hello.py`; tests go in `tests/test_hello_cli.py` (spec.md §7; work-items.md t1).
- Use argparse's built-in `'version'` action (hld.md §6).
- Total diff under 300 changed lines (spec.md §6).

**Assumptions:**

- argparse's `'version'` action prints the version string to stdout (not stderr) and raises `SystemExit(0)`. Evidence: Python 3.10+ stdlib behavior; the `run_main` helper in `test_hello_cli.py` captures both streams and `SystemExit`. Consequence if wrong: AC scenario 1 would fail on stderr assertion — but this behavior is stable across all supported Python versions (3.10+).

## Solution proposal

Add one `parser.add_argument("--version", action="version", version="0.1.0")` call to `main()` in `src/testbed_utils/hello.py`, between parser construction and `parse_args()`. This is argparse's idiomatic version action: it prints the version string to stdout, raises `SystemExit(0)`, and automatically appears in `--help` output. No other production code changes.

Add a `TestVersion` class in `tests/test_hello_cli.py` with a single test method that calls the existing `run_main(["--version"])` and asserts: exit code is 0, stdout is `"0.1.0\n"`, and stderr is empty. This covers AC scenario 1. AC scenarios 2–4 are already covered by the existing `TestGreeting`, `TestHelp`, and `TestBadOption` classes — they serve as regression guards and need no modification.

Alternatives considered:

- Manual `sys.argv` inspection before argparse: rejected because it duplicates what argparse provides, adds code, and breaks argparse's unified `--help` rendering (hld.md §6).
- Dynamic version from `importlib.metadata`: rejected by the spec's locked decision on a hardcoded literal.

## Ordered implementation steps

1. **Add the `--version` argument to the parser in `src/testbed_utils/hello.py:21–22`.** Insert `parser.add_argument("--version", action="version", version="0.1.0")` on a new line between `parser = argparse.ArgumentParser(...)` and `parser.parse_args()`. This is the entire production change. Advances AC scenario 1. Existing test layer: `package-api` (`pytest`).

2. **Add a `TestVersion` class in `tests/test_hello_cli.py`.** Place it after `TestHelp` and before `TestBadOption`. The class has one method that calls `run_main(["--version"])` and asserts `exit_code == 0`, `stdout == "0.1.0\n"`, and `stderr == ""`. Advances AC scenario 1. Existing test layer: `package-api` (`pytest`).

3. **Run the canonical gate (`pytest`) to confirm all tests pass.** This verifies AC scenarios 1–4 and work-items.md AC 5 (all existing tests pass without modification). Existing test layer: `package-api`.

## Work-item mapping

| Step | Work item | Title |
|------|-----------|-------|
| 1 | t1 | Add --version flag to testbed-hello and test all acceptance scenarios |
| 2 | t1 | Add --version flag to testbed-hello and test all acceptance scenarios |
| 3 | t1 | Add --version flag to testbed-hello and test all acceptance scenarios |

All work items from `work-items.md` are covered.

## Verification and CI gate

The canonical gate is `pytest`, declared in `.factory/testing.md` (`test-gate: pytest`).

**Gate sequence (from a clean temporary worktree at the committed SHA):**

1. `pip install -e ".[test]"`
2. `pytest`

**Required test layers:**

| Layer | Class | Command | Required | Run by |
|-------|-------|---------|----------|--------|
| `package-api` | production-path | `pytest` | yes | canonical-gate |

**What the gate must show:** All tests pass, including the new `TestVersion` test and all pre-existing tests (`TestGreeting`, `TestHelp`, `TestBadOption`). No new CI configuration, no `.factory/testing.md` update, and no `.factory/delivery-assets` entry is needed — the change adds no binary deliverable and does not alter the gate command.

## Risks and scope guards

**Risks:**

- RK1 (accepted, per spec.md §6): The hardcoded `"0.1.0"` may drift from `pyproject.toml` `version` after a future release. Mitigation deferred to a future epic by PO decision.

**Scope guards — the implement phase must NOT:**

- Read the version dynamically from `pyproject.toml`, `importlib.metadata`, or any other source.
- Touch any file other than `src/testbed_utils/hello.py` and `tests/test_hello_cli.py`.
- Modify existing test classes or the `run_main` helper.
- Add `--version` to any other console script (`pdf-extract`, `testbed-num-summary`, `guestbook`).
- Add dependencies, linters, formatters, or type checkers.
- Delete, skip, disable, or weaken any existing test or CI check.

## Clarification outcomes

None.
