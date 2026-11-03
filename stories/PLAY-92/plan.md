# Plan: PLAY-92, `--name` option for `testbed-hello`

## Context

PLAY-92 adds one optional option, `--name NAME`, to the `testbed-hello` console script in `roeeoz/play1`. The change lands on branch `halo/feat/play-92`. With a name that is not blank after trimming, the tool prints `Hello, <trimmed name>!`. With no `--name`, or a blank one, it prints exactly `Hello, world!\n`. `--help`, the error for a missing value, and the errors for unknown options or extra words keep argparse's behaviour: exit 0 for help, exit 2 for errors, and no greeting in either case. The help screen must now list `--name`, and its summary must still fit on one line. The approved requirement is `spec.md`, the design is `hld.md`, and the single work item `t1` is in `work-items.md`. All three files sit beside this file in `stories/PLAY-92/`.

## Research findings

- **Change surface:** `src/testbed_utils/hello.py` (23 lines).
  - `_DESCRIPTION` (`hello.py:8`) is `"Print a hello-world greeting to standard output."` (49 characters). The comment at `hello.py:7` caps it at 76 characters.
  - `hello_world()` (`hello.py:11-17`) returns `"Hello, world!"`. Its doctest is `>>> hello_world()`.
  - `main()` (`hello.py:20-23`) builds `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)`, calls `parse_args()` and discards the result, then calls `print(hello_world())`.
  - `from __future__ import annotations` is already present (`hello.py:3`).
- **Contracts:**
  - Entry point `testbed-hello = "testbed_utils.hello:main"` (`pyproject.toml`, `[project.scripts]`).
  - Package root export: `from testbed_utils.hello import hello_world` (`src/testbed_utils/__init__.py:9`), with `"hello_world"` in `__all__` (`__init__.py:17`).
  - `requires-python = ">=3.10"`.
  - argparse exits with status 2 on malformed commands.
- **Existing tests:**
  - `tests/test_hello_cli.py`:
    - `run_main(args)` (`:12-22`) patches `sys.argv`, captures stdout and stderr, and converts `SystemExit` into an exit code;
    - `TestGreeting.test_prints_greeting` (`:25-30`) checks byte-exact `GREETING = "Hello, world!\n"` and empty stderr;
    - `TestHelp.test_help` (`:33-40`) checks for `_DESCRIPTION` only after collapsing whitespace (`" ".join(stdout.split())`), so it would not catch the summary wrapping onto a second line;
    - `TestBadOption` (`:43-51`) parametrizes `--bogus`, `-x` and `extra`, and expects exit 2, empty stdout, and `usage:` and `error` in stderr.
  - `tests/test_hello.py` covers the return value, the root export (`:12-14`), the presence of a docstring example (`:18-25`), and `doctest.testmod(hello)` (`:27-30`).
- **Gate:** `.factory/testing.md` declares one required layer, `package-api`: `pytest`, run after `pip install -e ".[test]"`.
  - CI (`.github/workflows/ci.yml`, job `test`) runs only Python 3.12.
  - No linter, formatter, type checker or coverage tool is configured.
  - Job `gate` fails only if `CI_FAIL` exists at the repo root.
- **Repo gate:** rule 4 of `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (finding id `PLAY-G4`) requires a line under `## Unreleased` in `CHANGELOG.md`. `CHANGELOG.md` does not exist yet and must be created.
- **External data:** none.
- **Exists vs. new:** the parser, the harness and the tests for help and errors already exist. The new pieces are the `--name` argument, the trim-and-fallback logic, the new tests, the tightened help assertion and `CHANGELOG.md`.
- **Unknowns remaining:** none that block the work. The PM has not yet confirmed the PRD §7 decisions on trimming and on treating a missing value as an error. The spec and the story both adopt them, so they are treated as locked (see `spec.md` §8).

## Locked decisions and assumptions

**Locked decisions**
- Output with a non-blank name is `Hello, <name>!`. The name has leading and trailing whitespace stripped, its inner whitespace and letter case are kept. Source: `spec.md` FR1 and `work-items.md` t1 AC1 and AC4.
- With no `--name`, output is byte-exact `Hello, world!\n` and stderr is empty. Source: FR2 and t1 AC2.
- An empty or whitespace-only name falls back to `Hello, world!`. Source: FR3 and t1 AC3.
- `--name` with no value exits 2 with usage and an error on stderr. Source: FR4 and t1 AC5. Unknown options and extra words behave as today. Source: FR6 and t1 AC6.
- `--help` exits 0 with a one-line summary and a `--name` entry. The test must assert the single line directly. Source: FR5 and t1 AC7.
- `hello_world()` keeps its contract, its export and its doctest. Source: `hld.md` §2 and t1 AC8.
- Error handling stays with argparse: no custom validation and no catching of `SystemExit`. `allow_abbrev` keeps its default. Source: `hld.md` §6.
- No new dependencies. The code must run on Python 3.10 and later. Source: t1 AC10.
- `CHANGELOG.md` gets an entry under `## Unreleased`. Source: t1 AC12 and repo-gate `PLAY-G4`.

**Assumptions**
- **No new public helper.** The trim-and-fallback logic stays inline in `main()`.
  - Evidence: `hld.md` §5 leaves this to the implementer, and the logic is two lines.
  - If wrong: a public helper would trigger t1 AC9, meaning a `>>>` docstring plus tests in `tests/test_hello.py`. That adds work but conflicts with nothing.
- **Help is rendered at 80 columns in tests.** argparse reads `COLUMNS` through `shutil.get_terminal_size()`.
  - Evidence: the comment at `hello.py:7` assumes 80 columns.
  - If wrong: a narrow `COLUMNS` in some environment could wrap the summary and fail the tightened help test. The test pins `COLUMNS=80` with `unittest.mock.patch.dict(os.environ, ...)`, which is in-process and touches no files.
- **`--name -Al` is not supported.** Such a value must be passed as `--name=-Al`. A repeated `--name` lets the last value win.
  - Evidence: `spec.md` §8 Q2 and Q3, and `hld.md` §6.
  - If wrong: special parsing would be needed. That is out of scope here.

## Solution proposal

Extend the existing argparse parser in `main()` without restructuring the module.
- Add `parser.add_argument("--name", ...)` with `default=None`, `metavar="NAME"` and a short help text. The help text must not contain the literal `Hello, world!` (see `test_help` at `test_hello_cli.py:40`). Wording along the lines of "name to greet; blank or omitted greets the world" works.
- Keep the result of `parse_args()`.
- Compute `name = (args.name or "").strip()`.
- If `name` is non-empty, print `f"Hello, {name}!"`. Otherwise print `hello_world()`, so the default bytes still come from the same function that produces them today (RK1).
- Optionally reword `_DESCRIPTION` to mention a name, for example "Print a greeting (to world, or to --name) on standard output.", keeping it at 76 characters or fewer. Leaving it unchanged also satisfies FR5. Keep the comment at `hello.py:7`.
- argparse already supplies every error and help path (FR4, FR5, FR6), so no new code handles them.

**Alternatives rejected**
- Adding a `name` parameter to `hello_world()`. This would change a public, doctested contract that `hld.md` §6 says must stay as it is.
- A custom `type=` or validator that rejects blank values. That would contradict FR3, which requires a fallback rather than an error.
- Setting `allow_abbrev=False`. That would change today's `--h` behaviour and break R6.

## Ordered implementation steps

1. **Add `--name` and its logic.** In `src/testbed_utils/hello.py`:
   - add the `--name` argument to the parser in `main()`;
   - bind the result of `parse_args()`;
   - add the strip-and-fallback and print the greeting;
   - optionally reword `_DESCRIPTION`, keeping it at 76 characters or fewer.

   This advances t1 AC1–AC6 and AC10. The `package-api` layer (`pytest`) covers it. Use only syntax that Python 3.10 accepts. f-strings and `or` are fine.
2. **Test the happy path and case.** In `tests/test_hello_cli.py`, add a class (e.g. `TestName`) with these cases:
   - `["--name", "Alice"]` gives `stdout == "Hello, Alice!\n"`, empty stderr and exit 0 (AC1);
   - `["--name", "alice"]` gives `"Hello, alice!\n"` (AC4, case kept).

   Use placeholder names only (AC11).
3. **Test trimming and inner whitespace.** In the same class:
   - `["--name", "  Bob "]` gives `"Hello, Bob!\n"`;
   - a name with inner whitespace, e.g. `["--name", " Ada  Lee "]`, gives `"Hello, Ada  Lee!\n"`.

   This advances AC4.
4. **Test blank fallback.** Parametrize `""`, `" "` and `"   "`. Each gives `stdout == GREETING`, empty stderr and exit 0. This advances AC3.
5. **Test the missing value.** `["--name"]` gives exit 2, `stdout == ""`, and `usage:` and `error` in stderr. It also asserts that `Hello,` is absent from stderr. This advances AC5.
6. **Keep the regression tests unchanged.** Leave `TestGreeting.test_prints_greeting` and `TestBadOption` as they are. They already prove AC2 and AC6, and they must not be edited to pass.
7. **Tighten the help test.** In `TestHelp.test_help`:
   - pin `COLUMNS=80` with `patch.dict("os.environ", {"COLUMNS": "80"})`;
   - assert that `_DESCRIPTION` equals one stripped line of `stdout.splitlines()`, which proves the one-line summary;
   - assert that `--name` appears in stdout;
   - keep the exit 0, empty stderr, `usage:` and no-greeting assertions.

   Replace the whitespace-collapsed check rather than adding to it. This is a strengthening of the test, not a weakening. This advances AC7.
8. **Leave the public API alone.** Do not change `tests/test_hello.py` or `src/testbed_utils/__init__.py`. Their existing tests prove AC8. If step 1 nevertheless introduces a public helper, add a `>>>` docstring and tests in `tests/test_hello.py` for the happy path, a blank name and no name (AC9).
9. **Create the changelog.** Create `CHANGELOG.md` at the repo root with `# Changelog`, then `## Unreleased`, then one bullet. The bullet says that `testbed-hello` accepts `--name NAME` to print `Hello, NAME!`, with the default unchanged, and cites PLAY-92. This advances AC12. No test layer covers it; the repo gate's `PLAY-G4` rule checks it.
10. **Check the diff size.** Confirm the diff is well under 300 changed lines (AC13). The expected size is about 60.

**Invariants**
- Authorization, tenancy, concurrency and idempotency: not applicable. This is a stateless single-process CLI.
- Validation and error paths come entirely from argparse and are covered by steps 5 and 6.
- No dependencies to acquire beyond the existing `pip install -e ".[test]"`.
- No generated deliverables.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1–10 | `t1`: PLAY-92: add --name option to testbed-hello for a personalised greeting |

The breakdown has one work item, and every step maps to it.

## Verification and CI gate

- **Canonical gate:** run `pip install -e ".[test]"` and then `pytest` from the repo root, once, on the committed SHA. This is the one required layer, `package-api`, and it runs unprivileged in a pod. The authoritative result is the `test` job of `.github/workflows/ci.yml` (Python 3.12) at the PR head.
- **Pass criteria:** `pytest` is fully green. The new tests from steps 2–5 and 7 pass. `TestGreeting`, `TestBadOption` and every test in `tests/test_hello.py` pass unmodified. No other test file changes.
- **CI configuration:** no change. CI checks only Python 3.12, so 3.10 compatibility rests on code review: no syntax or standard-library APIs added after 3.10.
- **Coverage:** no coverage tool exists, so the 90% target cannot be shown in CI. Do not add coverage tooling.
- **Other gates:** `.factory/delivery-assets` does not apply (no binaries). The repo gate needs the `CHANGELOG.md` entry (step 9). `CI_FAIL` must not exist at the repo root.

## Risks and scope guards

**Risks**
- **RK1, drift in the default output.** Mitigation: the default path still prints `hello_world()`, and the byte-exact test stays untouched.
- **RK3, the help summary wraps.** Mitigation: keep `_DESCRIPTION` at 76 characters or fewer, and make the tightened single-line assertion run at a pinned 80 columns.
- **Help text leaks the greeting.** A `--name` help string containing `Hello, world!` would fail `test_help`. Mitigation: word the help text without the literal.
- **Python 3.10 compatibility is not tested in CI.** Mitigation: use only basic syntax.

**Scope guards: the implement phase must NOT**
- touch `pyproject.toml`, `.github/workflows/ci.yml`, `src/testbed_utils/__init__.py`, other modules (`numsummary.py`, `pdfutils.py`, `guestbook/`…), or other test files;
- add any runtime or test dependency, or coverage or lint tooling;
- change `hello_world()`'s signature, return value or doctest;
- set `allow_abbrev=False`, catch `SystemExit`, add custom validation, change exit codes, or handle `-`-prefixed names or repeated `--name`;
- read the name from an environment variable or a file, change its case, or translate the greeting;
- delete, skip or loosen any existing assertion in `TestGreeting`, `TestBadOption` or `tests/test_hello.py`. The help test may only be tightened. A failing required check may be reported as blocked but never weakened.

## Clarification outcomes

None.
