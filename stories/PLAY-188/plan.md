# PLAY-188 — Implementation plan: `testbed-hello --version`

## Context

PLAY-188 (epic PLAY-187) adds a `--version` option to the `testbed-hello` console script. `testbed-hello --version` prints exactly one line, `testbed-hello <version>`, to stdout and exits 0 without the greeting. The version is the one the installed `testbed-utils` distribution declares (today `0.1.0`). `--help` lists the option. The greeting, the help screen and unknown-option handling stay as today. No version number and no other tool changes. The change lands in `roeeoz/play1` on the work branch `halo/feat/play-188-20261120-160042`, cut from `main`. `spec.md` (acceptance criteria 1–7, FR1–FR7), `hld.md` (CLI contract §5, decisions §6) and `work-items.md` (single work item `t1`) sit beside this file in `stories/PLAY-188/`.

## Research findings

**Change surface**
- `src/testbed_utils/hello.py:20-23`: `main()` builds `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)`, calls `parser.parse_args()` and prints `hello_world()`. It defines no options, so `--version` currently exits 2 as an unrecognized argument.
- `src/testbed_utils/hello.py:7-8`: `_DESCRIPTION` must stay at 76 characters or fewer so argparse keeps it on one line. Leave it unchanged.
- `src/testbed_utils/hello.py:11-17`: `hello_world()` and its doctest are checked by `tests/test_hello.py:18-28`. Do not touch them.

**Version declarations (two copies, risk RK1)**
- `pyproject.toml:7`: `version = "0.1.0"` is the source of the installed distribution metadata. The distribution name is `name = "testbed-utils"` (`pyproject.toml:6`).
- `src/testbed_utils/__init__.py:28`: `__version__ = "0.1.0"` is a hand-maintained second copy.
- `src/testbed_utils/__init__.py:9` imports `testbed_utils.hello` before line 28 defines `__version__`. A module-level `from testbed_utils import __version__` in `hello.py` would therefore hit a partially initialised package and raise `ImportError`. The fallback must be read lazily, inside the function that runs on `--version`.
- `src/` contains no use of `importlib.metadata`. Stdlib `importlib.metadata.version()` and `PackageNotFoundError` are available on the declared `requires-python = ">=3.10"` (`pyproject.toml:9`), so no dependency is added.

**Entry point**
- `pyproject.toml:18`: `testbed-hello = "testbed_utils.hello:main"`. Unchanged.

**Existing tests**
- `tests/test_hello_cli.py:12-22`: `run_main(args)` patches `sys.argv`, redirects stdout and stderr, and catches `SystemExit`. New tests reuse it.
- `tests/test_hello_cli.py:25-30` `TestGreeting`, `:33-40` `TestHelp` (asserts `_DESCRIPTION in " ".join(stdout.split())`), `:43-51` `TestBadOption` (parametrized over `--bogus`, `-x`, `extra`, exit 2). Their assertions stay as they are.
- `tests/test_hello.py` covers the library function and doctest only. Not touched.

**Gate**
- `.factory/testing.md`: `local-test-gate: pip install -q -e ".[test]" && pytest`. There is one declared layer, `package-api` (production-path, `pytest`, `runBy: canonical-gate`). The repo has no linter, formatter, type checker or coverage tool.
- `.github/workflows/ci.yml`: job `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12 with a 5-minute timeout. Job `gate` fails only if `CI_FAIL` exists at the repo root.
- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` sets the MR layout rules: Python source under `src/`, tests under `tests/`, no file over 200 KB.

**Parallel work**
- `origin/halo/feat/play-186-20261119-171026` (commit `81084d5`, "greet by optional name") edits the same `main()` and is not in `main` (`git merge-base --is-ancestor` reports not merged). This is RK3. It does not affect this plan's base.

**Remaining unknowns:** none that block. The output form (PRD Q1) is settled as `testbed-hello <version>` by spec AC 1.

## Locked decisions and assumptions

**Locked decisions**
- Output is exactly `testbed-hello <version>\n` on stdout, with exit 0, empty stderr and no greeting (spec AC 1–2; hld §5).
- The version is the installed distribution's declared version, not a constant (spec AC 3, FR3; hld §6).
- `--help` lists `--version`, keeps the one-line description and exits 0 (spec AC 4, FR4).
- No-argument and unknown-option behaviour are unchanged: `Hello, world!` with exit 0, and usage plus `error:` with exit 2 (spec AC 5–6).
- `pyproject.toml`, `__init__.py`, other tools and CI are not changed (spec AC 7, FR7; work-items `t1` "Consumes").
- There is no short alias, so `-V` stays exit 2. `--version` combined with other arguments follows standard argparse behaviour (hld §5; `t1` AC 7–8).
- If no `testbed-utils` metadata is found, the code falls back to `testbed_utils.__version__` (hld §5; `t1` AC 4).
- Version source is `importlib.metadata`, with argparse's built-in `action="version"` (hld §6).

**Assumptions**
- *The test environment has the editable install, so metadata reports `0.1.0`.* Evidence: `.factory/testing.md` and `ci.yml` both run `pip install -e ".[test]"`, and the `src/` layout has no `conftest.py`, so tests only import through the installed distribution. If this is wrong, the exact-`0.1.0` test fails. That failure is the intended signal.
- *Patching the name `version` as `hello.py` binds it is enough to simulate another installed version.* Evidence: `hello.py` will import `from importlib.metadata import PackageNotFoundError, version`, and `unittest.mock.patch` on `testbed_utils.hello.version` replaces the binding `main()` resolves. If the version lookup is instead written as `importlib.metadata.version(...)`, patch `importlib.metadata.version` instead. Keep whichever binding the code uses consistent with the test.
- *argparse writes the version to stdout on Python 3.10+.* Evidence: argparse has done this since 3.4, and hld §3 confirms it on 3.12. If this is wrong, AC 1's stdout and empty-stderr assertion fails visibly.

## Solution proposal

Keep the existing argparse CLI and add one standard version action. This is the smallest change that meets every criterion.

1. **Version resolution.** Add a small private helper in `src/testbed_utils/hello.py` (new, for example `_package_version()`):
   - It returns `version("testbed-utils")` from `importlib.metadata`.
   - On `PackageNotFoundError`, it lazily imports and returns `testbed_utils.__version__`. The import is inside the function body to avoid the circular import described in Research findings.
   - It is called only when the parser is built.
   - Metadata lookup on the greeting path is a cheap local read, and the fallback guarantees it never raises. This satisfies `t1` AC 4 ("greeting and `--help` never fail because metadata is missing").
2. **Parser.** In `main()`, add `parser.add_argument("--version", action="version", version=f"%(prog)s {_package_version()}")`:
   - `%(prog)s` expands to `testbed-hello`.
   - argparse prints the version to stdout, exits 0 and short-circuits before `print(hello_world())`. This covers AC 1 and AC 2.
   - argparse lists `--version` under options with its default help text, which covers AC 4.
   - Pass `help=` with a short phrase such as "show the program's version and exit" only if the default text is unacceptable. The default is acceptable.
3. **No other module changes.** `__init__.py` keeps its `__version__`, which is used only as the fallback.

**Alternatives rejected**
- *`testbed_utils.__version__` as the primary source.* It is a second, hand-maintained copy that can drift from `pyproject.toml`, so it fails the intent of AC 3 and RK1 (hld §6).
- *A hand-rolled `--version` flag (`store_true` plus an explicit `print` and `sys.exit(0)`).* It duplicates what argparse already does, including stdout output, exit code, help listing and short-circuiting, and adds branches to test.
- *Resolving the version lazily only when `--version` is parsed (a custom `Action`).* It adds a class for no observable benefit, because the fallback already makes eager resolution safe.

## Ordered implementation steps

1. **Add the version helper.** In `src/testbed_utils/hello.py`:
   - Import `PackageNotFoundError` and `version` from `importlib.metadata`.
   - Add the private helper described in the Solution proposal, with the distribution name spelled `"testbed-utils"` exactly as `pyproject.toml:6` does and a function-local `from testbed_utils import __version__` fallback.
   - Advances AC 1 and AC 3 (`t1` AC 3–4). Layer: `package-api` (`pytest`).
2. **Register `--version`.** In `main()` (`src/testbed_utils/hello.py:20-23`), add `--version` with `action="version"` and `version="%(prog)s <helper result>"` before `parse_args()`.
   - Leave `_DESCRIPTION`, `hello_world()` and the greeting print unchanged.
   - Do not add `-V` or `-v`.
   - Advances AC 1, 2 and 4 (`t1` AC 1, 2, 5, 8). Layer: `package-api`.
3. **Add CLI tests.** In `tests/test_hello_cli.py`, add a `TestVersion` class that reuses `run_main`, with tests for:
   - **Exact output.** `--version` returns exit 0, stdout `== "testbed-hello 0.1.0\n"` and stderr `== ""` (AC 1).
   - **No greeting.** `Hello, world!` is in neither stdout nor stderr (AC 2).
   - **Metadata drives the output.** Patch `testbed_utils.hello.version` to return `"9.9.9"`, then assert stdout `== "testbed-hello 9.9.9\n"` (AC 3).
   - **Drift guard.** `testbed_utils.__version__ == importlib.metadata.version("testbed-utils")` (AC 3, RK1).
   - **Missing-metadata fallback.** Patch `version` to raise `PackageNotFoundError`. Assert that `--version` prints `testbed-hello ` + `testbed_utils.__version__`, and that `[]` still prints `GREETING` with exit 0 (`t1` AC 4).
   - **Combined arguments.** Parametrize `["--version", "extra"]` and `["--bogus", "--version"]`, each expecting exit 0 and the version line, which pins hld §5 (`t1` AC 8). Also check `["--version", "--help"]`, which prints the version.
   - Layer: `package-api`.
4. **Extend regression tests without weakening them.**
   - In `TestHelp.test_help` (`tests/test_hello_cli.py:34-40`), add `assert "--version" in stdout`. Keep every existing assertion (AC 4).
   - Add `"-V"` and `"--no-such-option"` to the `TestBadOption` parametrize list (`tests/test_hello_cli.py:44`) (AC 6; `t1` AC 7).
   - Leave `TestGreeting` as is (AC 5).
   - Layer: `package-api`.
5. **Scope check (AC 7).** Confirm that the diff touches only `src/testbed_utils/hello.py` and `tests/test_hello_cli.py`:
   - `pyproject.toml:7` and `src/testbed_utils/__init__.py:28` still read `0.1.0`.
   - Other tools are unchanged, and their existing suites (`tests/test_num_summary_cli.py`, `tests/test_pdf_extract_cli.py`, `tests/test_guestbook_api.py`) cover them unchanged.
   - Layer: `package-api` (full suite).

**Invariants**
- There is no authorization, tenancy or concurrency surface: this is a single-process CLI.
- Error paths are covered by step 4 (exit 2) and the missing-metadata path by step 3.
- Tests run in process with no network, clock or files outside `tests/fixtures` (G4).

**Dependencies**
- No new dependencies are added. `importlib.metadata` is stdlib, and `pytest>=8` comes from the existing `test` extra, installed fresh by `pip install -e ".[test]"`.
- There are no generated deliverables or binaries.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1 | `t1` | PLAY-188: add --version to testbed-hello |
| 2 | `t1` | PLAY-188: add --version to testbed-hello |
| 3 | `t1` | PLAY-188: add --version to testbed-hello |
| 4 | `t1` | PLAY-188: add --version to testbed-hello |
| 5 | `t1` | PLAY-188: add --version to testbed-hello |

`t1` is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate (provider CI, `.github/workflows/ci.yml` job `test`, Python 3.12):** `pip install -e ".[test]"`, then `pytest`. Job `gate` must stay green, so no `CI_FAIL` file may be added.
- **Local run:** the single local run is the gate's own, `run-tests-gate.sh --run` on the committed SHA, which runs `local-test-gate: pip install -q -e ".[test]" && pytest` from `.factory/testing.md`. Do not run the canonical command by hand beside it, and do not use a second worktree.
- **Required layer:** `package-api` (production-path, `pytest`). It runs in a pod unprivileged, and its authoritative credit is the provider run at the exact head. No other layer exists, and none is added.
- **Provider CI configuration:** no change needed.
- **`.factory/delivery-assets`:** not applicable, because no binary is added.
- **The gate must show:**
  - `pytest` passes in full, including the new `TestVersion` tests and the unchanged `TestGreeting`, `TestHelp` and `TestBadOption` assertions, the `tests/test_hello.py` doctest check, and the other tools' suites.
  - The run finishes well under 60 seconds (G4).
  - The repo-gate layout rules hold: code under `src/`, tests under `tests/`, no file over 200 KB.
  - The diff is under 300 lines (G3).

## Risks and scope guards

**Risks**
- **RK1, version drift between `pyproject.toml` and `__version__`.** Mitigated by using metadata as the source, the drift-guard test and the patched `9.9.9` test (step 3).
- **Circular import.** A module-level import of `__version__` in `hello.py` breaks the package import (`__init__.py:9` comes before `:28`). Mitigated by importing it inside the helper, and caught by every test that imports `testbed_utils`.
- **RK2, regressions in greeting, help or bad-option handling.** Mitigated by the unchanged existing assertions plus the additions in step 4.
- **RK3, PLAY-186 greet-by-name.** `origin/halo/feat/play-186-20261119-171026` edits the same `main()` and test file. Whichever merges second rebases onto the first. Do not merge or port that branch here.

**Scope guards (the implement phase must NOT)**
- Change `pyproject.toml`, `src/testbed_utils/__init__.py` (including `__version__`), `.github/workflows/ci.yml`, `.factory/` or any other tool (`pdfutils.py`, `numsummary.py`, `src/guestbook/`).
- Change `_DESCRIPTION`, `hello_world()` or its doctest.
- Add a `-V` or `-v` alias, a `--name` option, or extra version information such as Python version or build date.
- Add a dependency, a `conftest.py` or `sys.path` manipulation, or a new test framework or layer.
- Delete, skip, loosen or rewrite an existing assertion in `tests/test_hello_cli.py` or elsewhere. A failing check may be reported as blocked, but never made green that way.
- Bump the version number or refactor unrelated code.

## Clarification outcomes

None. No question was needed: PRD Q1 (output form) is settled by spec AC 1 and is non-blocking, and every other point is fixed by `spec.md`, `hld.md` or the repository.
