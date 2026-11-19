# Plan — EG1-1: `testbed-hello` greets by name

## Context

EG1-1 adds an optional `--name NAME` option to the `testbed-hello` console script. `testbed-hello --name Alice` prints `Hello, Alice!`. With no arguments it still prints `Hello, world!`. `--help`, the rejection of unknown arguments and the `hello_world()` library function stay as they are. The spec's ACs cover five points: the named greeting (AC1), the unchanged default (AC2), unchanged help and bad-argument behaviour (AC3), the unchanged library function (AC4), and tests in a green `pytest` CI job (AC5). The change goes into `roeeoz/play1` on the work branch `halo/feat/eg1-1-20261119-135816` and merges into `main`. `spec.md`, `hld.md` and `work-items.md` sit next to this file in `stories/EG1-1/`. The design in `hld.md` §5 is the CLI contract this plan implements.

## Research findings

- **Entry point.** `pyproject.toml:17` defines `testbed-hello = "testbed_utils.hello:main"`. It needs no change.
- **Change surface.** `src/testbed_utils/hello.py:20-23`. `main()` builds `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)` with no arguments, calls `parser.parse_args()` and discards the result, then prints `hello_world()`.
- **Frozen contracts in the same file:**
  - `_DESCRIPTION` (`hello.py:8`), with a comment saying it must stay ≤76 characters.
  - `hello_world()` (`hello.py:11-17`), which returns `"Hello, world!"` and has the doctest `'Hello, world!'`.
- **Package export.** `src/testbed_utils/__init__.py:9` re-exports `hello_world`. It is read-only for this story.
- **Existing CLI tests (`tests/test_hello_cli.py`):**
  - The `run_main(args)` helper (`:12-22`) patches `sys.argv`, captures stdout and stderr, and turns `SystemExit` into an exit code. New tests reuse it.
  - `TestGreeting.test_prints_greeting` (`:25-30`) already covers the no-argument case, which is AC2.
  - `TestHelp.test_help` (`:33-40`) asserts that `usage:` and `_DESCRIPTION` are present and that `Hello, world!` is **absent** from the help output. The `--name` help string therefore must not contain `Hello, world!`.
  - `TestBadOption` (`:43-51`) checks `--bogus`, `-x` and `extra` (exit 2, empty stdout, `usage:` and `error` on stderr).
- **Library tests.** `tests/test_hello.py` checks the return value, the package export, and that `doctest.testmod(hello)` runs at least one example and none fail. Any new `>>>` example in `hello.py` would join that doctest run. The plan adds none.
- **No other callers.** `testbed-hello` and `testbed_utils.hello` are not used anywhere else outside `stories/`. The `qa/` and `hello-world/` scripts are unrelated.
- **Gate:**
  - `.factory/testing.md` declares `local-test-gate: pip install -q -e ".[test]" && pytest`.
  - CI (`.github/workflows/ci.yml`) has a `test` job that runs `pip install -e ".[test]"` and then `pytest` on Python 3.12, and a `gate` job that fails only if `CI_FAIL` exists.
  - The layout gate is `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`: source under `src/`, tests under `tests/`, no file over 200 KB.
  - No linter or formatter is configured. `.factory/memory/` does not exist.
- **Dependencies.** Stdlib `argparse` only. `pytest>=8` comes from the `test` extra.
- **Unknowns.** None remain. The `hld.md` design team ran the argparse edge cases (`--name=`, repeated values, a missing value, values that start with a dash) and recorded the results in `hld.md` §5.

## Locked decisions and assumptions

**Locked decisions**
- `--name NAME` is optional and long-only. It takes one value. There is no `-n`, no positional argument and no environment variable (spec Non-Goals; work item t1).
- NAME is inserted verbatim. `--name ""` prints `Hello, !`. There is no validation, trimming or fallback (spec §8, `hld.md` §6, t1 ACs).
- The default path runs only when `--name` is absent, and its output stays byte-for-byte `Hello, world!\n` (spec FR1, §7).
- The named greeting is built in `main()`. `hello_world()`, its doctest, `_DESCRIPTION` and the package export stay unchanged (`hld.md` §6; spec AC4).
- Repeated `--name A --name B` prints `Hello, B!`, and `--name` with no value exits 2 (t1 ACs; `hld.md` §5).
- Only `src/testbed_utils/hello.py` (`main()` only) and `tests/test_hello_cli.py` change (t1 "Owns").

**Assumptions**
- argparse's default prefix abbreviation stays enabled, so `--nam Bob` also works. Evidence: `hld.md` §6, and `--he` already works for `--help` today. If this is wrong, a prefix that exited 2 before now greets, and the fix is to set `allow_abbrev=False`. No test pins it either way.
- An absent option is detected with argparse's default of `None`, which is different from `""`. Evidence: argparse semantics as recorded in `hld.md` §5. If this is wrong, `--name ""` would fall back to `world`, and the empty-name test in step 2 would catch it.

## Solution proposal

Make the smallest change that fits the existing CLI: one more `add_argument` call on the parser in `main()`, plus a conditional print.

- Declare `--name` with `metavar="NAME"` and the default `None`. Give it a short help string that does not contain `Hello, world!`, for example "name to greet instead of the world".
- Keep the result of `parse_args()`.
- If `args.name is None`, print `hello_world()` exactly as today.
- Otherwise print `f"Hello, {args.name}!"`.

All parse errors (missing value, unknown option, stray positional) stay with argparse's standard exit-2 handling. No new error code is added.

The main design choice is to compose the named greeting in the CLI layer. That leaves the library surface frozen, as `spec.md` and `hld.md` require.

Alternatives rejected:
- **A `name` parameter on `hello_world()`.** It changes the frozen library contract and its doctest (AC4).
- **A truthiness check (`if args.name:`).** It would send `--name ""` to `world`, which breaks the locked literal behaviour.
- **A positional name or a `-n` alias.** Both are excluded by the spec's Non-Goals.

## Ordered implementation steps

1. **Add the option in `src/testbed_utils/hello.py` `main()`.** Add `parser.add_argument("--name", metavar="NAME", help=...)` with the default `None`, and keep `args = parser.parse_args()`. Print `hello_world()` when `args.name is None`. Otherwise print `"Hello, " + args.name + "!"`. Do not touch `_DESCRIPTION`, `hello_world()`, its docstring or the module docstring.
   - Advances AC1 and AC2, and keeps AC3 and AC4 intact.
   - Test layer: `package-api` (pytest), through the tests in step 2 and the existing `tests/test_hello.py` and `tests/test_hello_cli.py`.
2. **Add tests to `tests/test_hello_cli.py`** using the existing `run_main` helper. Add a `TestName` class, or similar, with these cases:
   - `--name Alice` and `--name=Alice` print exactly `Hello, Alice!\n`, with empty stderr and exit 0 (AC1).
   - `--name "Ada Lovelace"` prints `Hello, Ada Lovelace!\n` (verbatim).
   - `--name ""` prints `Hello, !\n` (no fallback).
   - `--name A --name B` prints `Hello, B!\n`.
   - `--name` with no value exits 2, with stdout `""` and `usage:` and `error` on stderr (the error path in AC3).
   - `--help` output contains `--name NAME`. Add this as a new assertion in a new test. Leave the existing `test_help` unchanged; it still checks the description and that `Hello, world!` is absent (AC3).

   Leave `TestGreeting` and `TestBadOption` unchanged. They remain the regression proof for AC2 and AC3.
   - Advances AC5 (and AC1–AC3).
   - Test layer: `package-api` (pytest).
3. **Run the local gate once** with `pip install -q -e ".[test]" && pytest` from the repo root. The suite must be fully green, including `tests/test_hello.py` unmodified (AC4) and the doctest run.
   - Advances AC4 and AC5.
   - Test layer: `package-api`.

Implicit invariants:
- Authorization, tenancy and concurrency do not apply. This is a stateless local CLI.
- Validation and error paths are handled by argparse and covered in step 2.
- Dependencies come from the editable install with the `test` extra. No new dependency is needed.
- There are no generated deliverables or binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add optional --name NAME to testbed-hello with tests |
| 2 | t1 | Add optional --name NAME to testbed-hello with tests |
| 3 | t1 | Add optional --name NAME to testbed-hello with tests |

Every work item (t1) has steps.

## Verification and CI gate

- **Canonical gate.** Run `pip install -q -e ".[test]" && pytest` (`.factory/testing.md`) once locally from the repo root on the final tree. The provider CI `test` job, `pip install -e ".[test]"` then `pytest` on Python 3.12, is the authoritative run at the PR head.
- **Required layer.** `package-api` (pytest, production-path) runs in a pod. No other layers are declared.
- **The `gate` job** is green as long as no `CI_FAIL` file is added.
- **Layout gate.** Changes stay in `src/` and `tests/`, and every file is under 200 KB.
- **No CI configuration changes** are needed.
- **What "done" means.** `pytest` passes with no failures, and the output includes:
  - the new `--name` tests;
  - the unchanged `TestGreeting`, `TestHelp` and `TestBadOption` tests;
  - `tests/test_hello.py`, with the doctest attempting ≥1 example and 0 failures.

## Risks and scope guards

**Risks**
- *Help-test regression.* If the `--name` help string contains `Hello, world!`, `TestHelp.test_help` fails. Mitigation: phrase the help string without that text.
- *Empty-name fallback.* A truthiness check would silently send `""` to `world`. Mitigation: use an explicit `is None` check, pinned by the empty-name test.
- *Doctest drift.* A new `>>>` example in `hello.py` would join `doctest.testmod(hello)`. Mitigation: add no doctest examples.

**Do NOT**
- Change `hello_world()`, its docstring or doctest, `_DESCRIPTION`, the module docstring, or `src/testbed_utils/__init__.py`.
- Change `tests/test_hello.py`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/testing.md`, `qa/`, `hello-world/` or other console scripts.
- Add `-n`, a positional name, an environment-variable or config source, name validation or trimming, or `allow_abbrev=False`.
- Modify, skip or weaken the existing tests in `tests/test_hello_cli.py`. A failing check may be reported as blocked but never made green by editing it away.
- Add a `CI_FAIL` file or any new dependency.

## Clarification outcomes

None.
