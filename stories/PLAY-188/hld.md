# PLAY-188 — High-Level Design: `testbed-hello --version`

## 1. System Overview

- **What is built:** a `--version` option on the existing `testbed-hello` console script that prints exactly one line, `testbed-hello <version>`, to stdout and exits 0, without the greeting (spec FR1–FR3).
- **Problem:** today `src/testbed_utils/hello.py` `main()` builds an `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)` with no options, so `--version` is rejected as an unrecognized argument (exit 2).
- **Responsibilities:** report the version the *installed* distribution `testbed-utils` declares (`pyproject.toml` `version = "0.1.0"`); list `--version` in `--help`; keep greeting / help / bad-option behaviour unchanged (FR4–FR6); change no version number and no other tool (FR7).

## 2. Architecture Overview

- Single component, single repo (`roeeoz/play1`), single module: `src/testbed_utils/hello.py`. No new module, no new dependency (`importlib.metadata` is stdlib on the declared `requires-python = ">=3.10"`).
- Entry point unchanged: `pyproject.toml` `[project.scripts] testbed-hello = "testbed_utils.hello:main"`.
- Tests: `tests/test_hello_cli.py` (existing CLI tests, driven via `main()` with patched `sys.argv` — the pattern to extend). `tests/test_hello.py` (library/doctest tests) is untouched.
- Not touched: `pyproject.toml`, `src/testbed_utils/__init__.py` (both keep `0.1.0`), other tools (`pdfutils.py`, `numsummary.py`, `src/guestbook/`), CI (`.github/workflows/ci.yml`), `.factory/`.

## 3. Data Flow Design

Synchronous, in-process:

1. User runs `testbed-hello --version`.
2. `main()` resolves the version from the installed distribution metadata of `testbed-utils` (stdlib `importlib.metadata`).
3. argparse's standard version action prints `testbed-hello <version>` + newline to **stdout** (verified on Python 3.12: argparse ≥3.4 writes version to stdout) and exits 0 — before the greeting line is reached.
4. Without `--version`, flow is exactly today's: parse → print `Hello, world!` → exit 0; `--help` → usage + description + options (now including `--version`) → exit 0; unknown option → usage + error on stderr → exit 2.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repo |
| --- | --- | --- | --- |
| `testbed-hello` CLI (`src/testbed_utils/hello.py`) | Parse args; print version line or greeting | argv → stdout/stderr text + exit code | `roeeoz/play1` |
| CLI tests (`tests/test_hello_cli.py`) | Prove FR1–FR7 at the CLI boundary | — | `roeeoz/play1` |

## 5. Interface Contracts

CLI contract (the only interface):

| Invocation | stdout | stderr | Exit |
| --- | --- | --- | --- |
| `testbed-hello --version` | exactly `testbed-hello <installed version>\n` (today `testbed-hello 0.1.0\n`) | empty | 0 |
| `testbed-hello` | `Hello, world!\n` | empty | 0 |
| `testbed-hello --help` | usage, one-line description `_DESCRIPTION`, options incl. `--version` | empty | 0 |
| `testbed-hello --no-such-option` / `-x` / `extra` | empty | usage + `error:` line | 2 |

Edge cases settled (argparse standard behaviour, probed on Python 3.12):

- `--version` combined with other arguments (`--version extra`, `--version --bogus`, `--bogus --version`): the version action runs when reached and exits 0 with the version line; it is not an error. Accepted as standard argparse behaviour.
- `--help --version` → help, exit 0; `--version --help` → version, exit 0 (first one wins).
- Unambiguous prefix `--vers` is accepted like `--he` is today (argparse `allow_abbrev` default kept).
- No short alias: `-V` and `-v` stay unrecognized (exit 2) — the spec names only `--version`.
- Version source missing (package imported from source without an install, so no `testbed-utils` distribution metadata): `--version` falls back to the package's `__version__` (`0.1.0`); the greeting and `--help` paths must never fail because metadata is absent.

## 6. Key Technical Decisions

- **Version source = installed distribution metadata** (`importlib.metadata`, distribution name `testbed-utils`). This is literally "the version the installed package declares" (FR3, RK1) and is generated from `pyproject.toml`. Alternative considered: reading `testbed_utils.__version__` — rejected as primary because it is a hand-maintained second copy that can drift from `pyproject.toml`; kept only as the no-metadata fallback.
- **Drift guard:** a test asserts `testbed_utils.__version__` equals the installed metadata version, so the two declarations cannot silently diverge (RK1).
- **argparse built-in version action** rather than a hand-rolled flag: gives stdout output, exit 0, help listing and correct short-circuit of the greeting for free, consistent with the existing argparse-based CLI.
- **No change to version numbers, `pyproject.toml`, other tools or CI** (FR7, G3).

## 7. Risks & Constraints

- **RK1 version drift:** mitigated by metadata as source + drift-guard test + a test that patches the metadata version (e.g. `9.9.9`) and asserts the output follows it (not a constant).
- **RK2 regressions:** existing `TestGreeting`, `TestHelp`, `TestBadOption` in `tests/test_hello_cli.py` keep passing unchanged in assertion; the help test still sees `_DESCRIPTION` on one line.
- **RK3 parallel epic "e2e-halo135 greet by name"** also edits `src/testbed_utils/hello.py` and `tests/test_hello_cli.py`; whichever merges second rebases onto the first. Not blocking.
- **Gates:** CI `test` job (`pip install -e ".[test]"` then `pytest`, Python 3.12, 5-minute timeout); `gate` job (no `CI_FAIL`); repo-gate skill `.factory/plugins/claims-dev/skills/repo-gate` (code in `src/`, tests in `tests/`, no file > 200 KB). Tests are in-process, no network/clock/files outside `tests/fixtures` (G4); change well under 300 lines (G3).
- No security, scale or performance surface: one local read of package metadata per invocation.

## 8. Assumptions

- Output form is `testbed-hello <version>` (PRD Q1, non-blocking; the spec settles it as the working assumption). If the PM picks the bare number, only the version string format and its test change.
- The editable install (`pip install -e .`) exposes `testbed-utils` metadata with version `0.1.0` — this is how the CI and `.factory/testing.md` run the suite.
