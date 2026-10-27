# Implementation plan — PLAY-67: Verify testbed-hello prints a usage line on --help and exits 0

| Field | Value |
| --- | --- |
| Work item | t1 — Assert program name in testbed-hello --help test |
| Repo | `roeeoz/play1` (`0fcb6992-968b-4373-a63d-0575b37433ef`) — checkout at `/workspace` |
| Tier | T1 (single work item, no dependencies) |
| Traces | R1–R3 · spec AC1–AC3 · HLD §1–§7 |
| Inputs read | `docs/plans/play-66/play-67/spec.md`, `hld.md`, `work-items.md`; `src/testbed_utils/hello.py`; `tests/test_hello_cli.py`; `pyproject.toml`; `.factory/testing.md`; `.github/workflows/ci.yml` |

## Context

PLAY-67 verifies that the existing `testbed-hello` console script satisfies the play1 discoverability standard (G2): it answers `--help` with a usage line containing the program name and exits 0, plain invocation keeps its greeting, and the test suite covers the `--help` behavior. The script (`src/testbed_utils/hello.py`) and its test (`tests/test_hello_cli.py`) already exist. The only gap found by the structure turn is that `TestHelp.test_help` asserts `"usage:" in stdout` but does not assert the program name `"testbed-hello"` appears in the output, as FR3 requires. The change is one assertion line added to the existing test method. The plan folder sits at `docs/plans/play-66/play-67/` on branch `halo/feat/play-67`; `spec.md`, `hld.md` and `work-items.md` are beside this file.

## Research findings

### Change surface

| Path | Line(s) | Action | What |
| --- | --- | --- | --- |
| `tests/test_hello_cli.py` | 38 | **edit** | Add `assert "testbed-hello" in stdout` after the existing `assert "usage:" in stdout` in `TestHelp.test_help` |

No other file changes. Specifically **not** touched: `src/testbed_utils/hello.py`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/testing.md`, any other test file.

### Contracts touched

**CLI contract (read-only, no change):**
- `src/testbed_utils/hello.py:21` — `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)`. The `prog="testbed-hello"` argument causes argparse to emit `usage: testbed-hello [-h]` on `--help`. This is deterministic and hardcoded.
- `pyproject.toml:17` — `testbed-hello = "testbed_utils.hello:main"` declares the console entry point.

**Test contract (edited):**
- `tests/test_hello_cli.py:12–22` — helper `run_main(args)` patches `sys.argv`, captures stdout/stderr via `io.StringIO`, catches `SystemExit`, returns `(exit_code, stdout, stderr)`. No change needed.
- `tests/test_hello_cli.py:34–40` — `TestHelp.test_help` currently asserts exit code 0, empty stderr, `"usage:"` in stdout, `_DESCRIPTION` in stdout, and `"Hello, world!"` not in stdout. The new assertion sits after line 38.

### Existing tests and gate

The `package-api` layer (`.factory/testing.md`) is the sole test layer. Gate command: `pytest`, run from the repo root after `pip install -e ".[test]"`. No linter, formatter, type checker, or coverage tool. CI (`.github/workflows/ci.yml`) runs `pytest` on Python 3.12 on `ubuntu-latest` with `permissions: contents: read`. The `gate` job checks only for a `CI_FAIL` marker file.

Existing test classes in `tests/test_hello_cli.py`:
- `TestGreeting.test_prints_greeting` — covers plain invocation (AC2/FR2).
- `TestHelp.test_help` — covers `--help` output and exit code (AC1/FR1, AC3/FR3 with the gap).
- `TestBadOption.test_unrecognized_option` — covers bad flags.

### What exists versus what must be created

Everything exists. The script satisfies FR1 and FR2. The test satisfies AC1 and AC2. AC3 is partially satisfied — the test invokes `--help` and checks `"usage:"` and exit code 0, but does not assert the program name `"testbed-hello"` appears in stdout. One assertion closes the gap.

### Unknowns after research

None. The output of `testbed-hello --help` is deterministic (`prog="testbed-hello"` is hardcoded at `hello.py:21`), so the substring `"testbed-hello"` is guaranteed in stdout.

## Locked decisions and assumptions

### Locked decisions

| Decision | Source |
| --- | --- |
| Only `tests/test_hello_cli.py` is modified; no change to `src/testbed_utils/hello.py` | HLD §2, §7; work-items.md t1 AC5 |
| Assert substring `"testbed-hello"` rather than a full usage-line regex | HLD §6 — the program name is the spec requirement; exact format is an argparse detail accepted per RK1 |
| Add the assertion to the existing `test_help` method, not a new test method | HLD §6 — the method already invokes `--help` and captures output; one `assert` line is the minimal change |
| The parser's default `usage: testbed-hello [-h]` satisfies FR1 | Epic PRD RK1; spec §3 edge cases |

### Assumptions

None. Every decision traces to a locked source.

## Solution proposal

Add one assertion — `assert "testbed-hello" in stdout` — to the existing `TestHelp.test_help` method in `tests/test_hello_cli.py`, immediately after the existing `assert "usage:" in stdout` at line 38. This closes the only gap between the current test suite and FR3 (the test must assert that stdout contains a usage line including the program name).

No alternative was considered because the HLD already decided the approach (§6): add to the existing test rather than create a new method, and assert substring rather than regex. The change is one line, in one file, following the exact pattern of adjacent assertions.

## Ordered implementation steps

1. **Add the program-name assertion to `TestHelp.test_help`.**
   - File: `tests/test_hello_cli.py:38` — insert `assert "testbed-hello" in stdout` after the existing `assert "usage:" in stdout` line.
   - Advances: AC1 (FR1 — the test now fully verifies the usage line includes the program name), AC3 (FR3 — the test asserts both a usage line and the program name).
   - Test layer: `package-api` (`pytest`) — the modified test itself is the coverage.
   - Implicit invariants: none applicable (no authorization, concurrency, or data validation involved — pure string containment on deterministic output).

2. **Run the gate.**
   - Command: `pip install -e ".[test]" && pytest` from the repo root.
   - Confirms: all existing tests still pass (no regression), the new assertion passes, AC2 (FR2 — `TestGreeting.test_prints_greeting` is unchanged and green).

3. **Commit.**
   - One commit on the checked-out branch with a message citing PLAY-67 and work item t1.
   - No `CI_FAIL` file created.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1 | t1 | Assert program name in testbed-hello --help test |
| 2 | t1 | Assert program name in testbed-hello --help test |
| 3 | t1 | Assert program name in testbed-hello --help test |

All steps belong to the single work item. No planning gap.

## Verification and CI gate

Run from the repo root after an editable install:

```bash
pip install -e ".[test]"
pytest
```

Expected:
- `pytest` — entire suite passes; `tests/test_hello_cli.py::TestHelp::test_help` passes with the new assertion; `TestGreeting::test_prints_greeting` and `TestBadOption` remain green; all other test files unchanged and green.
- `git diff --stat` shows exactly one file (`tests/test_hello_cli.py`), one inserted line, well under the 300-changed-line cap (G3).
- No `CI_FAIL` file exists at the repo root.
- No `.factory/testing.md` change needed — the gate command and test layers are unchanged.
- No `.factory/delivery-assets` obligation — no binary deliverable.

Provider CI (`.github/workflows/ci.yml`) runs `pytest` on Python 3.12 on `ubuntu-latest` with `permissions: contents: read`. No change to CI configuration needed.

## Risks and scope guards

| Risk / guard | Handling |
| --- | --- |
| **Scope lock.** Only `tests/test_hello_cli.py` changes. | Do not modify `src/testbed_utils/hello.py`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/testing.md`, or any other file. |
| **No new flags.** | Do not add arguments, options, or subcommands to `testbed-hello`. |
| **No greeting change.** | Do not alter the script's greeting behavior or `_DESCRIPTION`. |
| **No new test methods or test files.** | Add the assertion to the existing `test_help` method, not a new method or file. |
| **Gate integrity.** | Do not create `CI_FAIL`. Do not weaken, skip, or disable any existing assertion in the test suite. |
| **Essentially zero risk.** | The assertion is a pure string containment check on deterministic argparse output (`prog="testbed-hello"` is hardcoded). No environment dependency, no flakiness vector. |

## Clarification outcomes

None — no question was needed. Every decision traces to the spec, HLD, or work-items breakdown without conflict.
