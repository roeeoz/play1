# PLAY-186 — High-Level Design: testbed-hello greets by name

## 1. System Overview

- **What:** the `testbed-hello` console script (`pyproject.toml` → `testbed-hello = "testbed_utils.hello:main"`) gains one optional positional name: `testbed-hello Dana` prints `Hello, Dana!`; with no name, an empty name or a whitespace-only name it prints `Hello, world!` exactly as today.
- **Problem:** today `main()` in `src/testbed_utils/hello.py` builds an `argparse.ArgumentParser` with no arguments, so any extra word (e.g. `extra`) is rejected with exit 2 (`tests/test_hello_cli.py::TestBadOption`). Per RK2 this changes on purpose: one bare word is now the name.
- **Responsibilities:** parse at most one name, normalise it (strip leading/trailing whitespace, keep case), format the one-line greeting, keep `--help` and unknown-option rejection working.

## 2. Architecture Overview

- Single module, single repo (`roeeoz/play1`): `src/testbed_utils/hello.py` holds both the greeting function and the CLI `main()`. No new module, no new dependency (Engineering R2), no new entry point.
- Public surface: `testbed_utils.hello_world` is re-exported from `src/testbed_utils/__init__.py` (`__all__`) and tested in `tests/test_hello.py` (including the doctest check). It must keep returning `Hello, world!` when called with no argument.
- Tests: `tests/test_hello.py` (function + doctest) and `tests/test_hello_cli.py` (drives `main()` in-process via patched `sys.argv`, captures stdout/stderr and exit code). No network, clock or file access (G4).
- Untouched: `hello-world/hello.sh`, `qa/`, other tools, `.github/workflows/ci.yml`.

## 3. Data Flow Design

Synchronous, in-process: `sys.argv` → argparse (`[-h] [name]`) → name normalisation (`strip()`; empty after strip → no name) → greeting string `"Hello, " + name + "!"` or `"Hello, world!"` → one line on stdout → exit 0. Help → usage + one-line description + name argument text on stdout, exit 0, no greeting. Unknown option / surplus word → argparse usage + `error:` on stderr, nothing on stdout, exit 2.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repo |
| --- | --- | --- | --- |
| Greeting function (`src/testbed_utils/hello.py`, public, exported via `src/testbed_utils/__init__.py`) | Build the greeting for an optional name; no-arg call unchanged | optional name string → greeting string | roeeoz/play1 |
| CLI `main()` (`src/testbed_utils/hello.py`) | Parse argv, print greeting / help / usage error | argv → stdout/stderr + exit code | roeeoz/play1 |
| Tests (`tests/test_hello.py`, `tests/test_hello_cli.py`) | Cover happy path, edges, errors; doctest examples | — | roeeoz/play1 |

## 5. Interface Contracts

CLI contract (the only external interface). Behaviour verified against argparse on CPython 3.12 (an `nargs="?"` positional on the current parser):

| Invocation | stdout | stderr | exit |
| --- | --- | --- | --- |
| `testbed-hello` | `Hello, world!\n` (byte-identical to today) | empty | 0 |
| `testbed-hello Dana` | `Hello, Dana!\n` | empty | 0 |
| `testbed-hello " dana "` | `Hello, dana!\n` | empty | 0 |
| `testbed-hello "Dana Star"` | `Hello, Dana Star!\n` | empty | 0 |
| `testbed-hello ""` / `testbed-hello " "` | `Hello, world!\n` | empty | 0 |
| `testbed-hello --help` / `-h` | usage, the one-line summary, a description of the optional name with an example (e.g. Dana); no greeting | empty | 0 |
| `testbed-hello --bogus` / `-x` | empty | usage + `error:` line, no greeting | 2 |
| `testbed-hello Dana Star` (unquoted, two words) | empty | usage + `error:` line, no greeting | 2 |
| `testbed-hello -1` / `testbed-hello -` (dash-led word) | empty | usage + `error:` line, no greeting | 2 |
| `testbed-hello -- -x` (explicit end-of-options) | `Hello, -x!\n` | empty | 0 |

Python API: the existing exported greeting function still returns `Hello, world!` when called with no argument; any new or changed public function carries a docstring with a runnable `>>>` example (G2).

## 6. Key Technical Decisions

- **Optional positional on the existing argparse parser** rather than hand-parsing `sys.argv`: keeps `--help`, usage text and exit code 2 for unknown options exactly as today (R4, R5). Alternative `--name` option is explicitly out of scope (spec Non-Goals).
- **Two unquoted words are an error, not joined** (spec §8 working assumption; "the tool does not guess"). argparse already does this (`unrecognized arguments: Star`).
- **Dash-led words are always options.** argparse by default accepts `-1` and `-` as a positional value (verified: `Namespace(name='-1')`, `Namespace(name='-')`). FR5 says a word starting with a dash that is not a known option is rejected, so the design rejects every dash-led word given as the name (exit 2, usage + error on stderr, no greeting). The standard `--` separator stays the escape hatch for a literal dash-led name.
- **Normalisation:** Python `str.strip()` (removes leading/trailing whitespace incl. tabs/newlines), case untouched; empty after strip → default greeting. No other validation (length, characters) — out of scope.
- **Greeting logic lives in the public function, the CLI only parses and prints**, so the edge cases are testable without argv; the implementer chooses whether to extend the existing function with an optional parameter or add one, as long as the no-arg contract and export stay.
- **Help summary stays one line ≤ 76 chars** (comment on `_DESCRIPTION` in `src/testbed_utils/hello.py`); it may be reworded to mention the optional name. The existing help test checks `_DESCRIPTION` appears in the help output.

## 7. Risks & Constraints

- **RK2 behaviour change:** `tests/test_hello_cli.py::TestBadOption` currently expects `extra` to be rejected; that case must change to the new greeting, while `--bogus`/`-x` stay rejected. Intended.
- **argparse help header varies by version** (`options:` on 3.10+; the repo requires ≥3.10, CI runs 3.12) — tests must assert on content (`usage:`, summary, name description), not on headings.
- **RK3:** only fictitious names (Dana, Dana Star) in code, docs and tests.
- **G3 size:** one component + its tests, well under 300 changed lines. **G4:** in-process tests, no network/clock/files; suite runtime unaffected.
- **Gates:** `pip install -e ".[test]" && pytest` (`.factory/testing.md`, `.github/workflows/ci.yml`); `repo-gate` layout rules (code under `src/`, tests under `tests/`) — satisfied by construction. No linter/formatter is configured.
- **Performance/security:** trivial; the name is printed verbatim and never executed or stored.

## 8. Assumptions

- Non-ASCII names (e.g. Hebrew) print as given; output encoding is the terminal's (UTF-8 in CI). Not separately tested. Risk if wrong: a garbled name on a non-UTF-8 console only.
- Rejecting dash-led names like `-1` follows FR5's wording; if the PO wants them greeted, only the parser's handling changes.
- The wording-rules page (RK1) was not read; wording follows the PO-approved rules in the spec.
