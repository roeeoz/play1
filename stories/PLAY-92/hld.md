# HLD: PLAY-92, personalised greeting for `testbed-hello` (`--name`)

Traceability: story PLAY-92, epic "ברכה אישית ל-testbed-hello" (Epic PRD v1, R1–R6, RK1–RK3). Plan folder: `stories/PLAY-92/` (the authority is `spec.md`).

## 1. System Overview
- **What:** one optional option, `--name NAME`, on the existing console script `testbed-hello` (`testbed_utils.hello:main`).
- **Problem:** the tool always prints `Hello, world!`. A developer can't get a greeting addressed to another name.
- **Responsibilities:**
  - parse `--name`;
  - trim the value and fall back to `world` when it is blank;
  - print one greeting line;
  - keep the help screen and every error path exactly as they behave today.

## 2. Architecture Overview
- **One component:** the `src/testbed_utils/hello.py` module in repo `roeeoz/play1`. It holds the CLI entry point, the argparse parser and the greeting logic.
- **Unchanged boundaries:**
  - the public `hello_world()` keeps returning `Hello, world!`, stays exported from `testbed_utils/__init__.py` and stays doctested;
  - the entry point in `pyproject.toml` is untouched;
  - other modules (e.g. `numsummary.py`) are untouched.
- **External dependencies:** none new. `argparse` is in the standard library. Python floor is 3.10.
- **Supporting files:**
  - `tests/test_hello_cli.py`, the in-process `run_main` harness;
  - `tests/test_hello.py`, only if a new public helper is added;
  - `CHANGELOG.md`, new, required by repo-gate rule PLAY-G4.

## 3. Data Flow Design
The whole flow is synchronous and runs in one process, with no I/O beyond stdout and stderr:
1. Read `argv`.
2. argparse parses it:
   - `--help` prints usage, the one-line description and the options, then exits 0;
   - a malformed command (`--name` with no value, an unknown option, an extra word) prints usage and an error on stderr, then exits 2;
   - otherwise parsing yields `name`, which is either None or a string.
3. Pick the greeting:
   - `name` is None, or blank after `strip()`, so print `Hello, world!` (same bytes as `hello_world()`);
   - otherwise print `Hello, <stripped name>!`.
4. Exit 0.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `testbed_utils.hello` (CLI and greeting) | Parse `--name`, trim it, fall back, print | In: argv. Out: one stdout line, or help/usage text, and an exit status | roeeoz/play1 |
| `tests/test_hello_cli.py` | Run the acceptance criteria in-process through `run_main` | In: arg lists. Out: assertions on stdout, stderr and exit code | roeeoz/play1 |
| `CHANGELOG.md` | Satisfy the repo gate (an entry under `## Unreleased`) | n/a | roeeoz/play1 |

## 5. Interface Contracts
- **CLI usage:** `testbed-hello [-h] [--name NAME]`.
- **Output:**
  - stdout is exactly one line, `Hello, <name>!\n`, or exactly `Hello, world!\n`;
  - on success stderr is empty.
- **Exit codes:**
  - 0 for a greeting or `--help`;
  - 2 for a malformed command (argparse's default, unchanged).
- **Python API:** `hello_world()` is unchanged. Any new public helper is the implementer's choice, but it must have a docstring with a `>>>` example (G2) plus happy-path, boundary and error tests (G1). `test_doctests_pass` runs that example automatically.
- **No cross-repo contracts.**

## 6. Key Technical Decisions
- **Rely on argparse for error paths (FR4, FR6):** argparse already reports a missing value with "expected one argument" and exit 2, so the code adds no custom validation and does not catch `SystemExit`.
- **Trim in application code:** argparse does not strip values, so the code calls `str.strip()`. That also strips Unicode whitespace (tabs, NBSP), so a value made only of those falls back to `world`, which is consistent with FR3.
- **Keep `allow_abbrev` at its default:** turning it off would change today's `--h` behaviour and violate R6. As a side effect, `--nam` is accepted.
- **`-`-prefixed names and repeated `--name`:** keep argparse's defaults (`--name=-Al` is required; the last `--name` wins). This matches the spec's working assumptions. Neither case gets an acceptance criterion.
- **`_DESCRIPTION`:** it may be reworded but must stay ≤ 76 characters (the existing guard for RK3). The `--name` help text must not contain the literal `Hello, world!`, because the help test asserts it is absent.
- **Alternative considered:** changing `hello_world()` to take a name. Rejected: the spec requires its contract and doctest to stay as they are.

## 7. Risks & Constraints
- **RK1, default output drift:** guarded by the existing byte-exact test (`stdout == "Hello, world!\n"`, empty stderr), which must keep passing.
- **RK2, whitespace in names:** handled by trimming the start and end only, keeping inner whitespace and letter case.
- **RK3, help summary wrapping:** the current help test collapses whitespace, so it would not catch wrapping. This ticket tightens it to check that the summary sits on exactly one stdout line.
- **Python versions:** CI runs only Python 3.12, while the floor is 3.10. Avoid syntax newer than 3.10; `from __future__ import annotations` is already present.
- **Repo gate PLAY-G4:** the PR must create `CHANGELOG.md` with a line under `## Unreleased`.
- **Coverage:** the ≥ 90% target is not measured in CI and can only be checked by hand.
- **Size and determinism:** well under the 300 changed-line limit. Tests run in-process with no network, clock or file access, and use placeholder names (Alice, Bob, Ada Lovelace) only.
- **Scale and security:** not applicable. It is a single-line local CLI with no data at rest.
