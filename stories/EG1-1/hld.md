# HLD — EG1-1: `testbed-hello` greets by name

## 1. System Overview

- **What:** an optional `--name NAME` option on the existing `testbed-hello` console
  script (`pyproject.toml` `[project.scripts]` → `testbed_utils.hello:main`).
  No argument → `Hello, world!` (unchanged); `--name NAME` → `Hello, NAME!`.
- **Today:** `src/testbed_utils/hello.py:20-23` — `main()` builds an
  `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)` with no
  arguments, calls `parse_args()` (so anything except `-h/--help` exits 2) and prints
  `hello_world()`. The code matches what the spec describes.
- **Responsibility:** one module (`hello.py`) and its CLI tests
  (`tests/test_hello_cli.py`). Everything else is out of scope.

## 2. Architecture Overview

- Single repository `roeeoz/play1`, single module `src/testbed_utils/hello.py`.
  No new modules, dependencies, entry points or config.
- The library function `hello_world()` (`hello.py:11-17`, doctest
  `'Hello, world!'`) and its package export (`src/testbed_utils/__init__.py:9,17`)
  stay untouched; the name-aware greeting is composed inside the CLI layer only.
- External dependency: stdlib `argparse` only (already used).
- Repository gates every PR must pass: `.github/workflows/ci.yml` `test` job
  (`pip install -e ".[test]"` then `pytest`, Python 3.12; `.factory/testing.md`),
  `gate` job (no `CI_FAIL` file), and the layout gate
  `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (source under `src/`,
  tests under `tests/`). No linter/formatter is configured. No `.factory/memory/`
  exists.

## 3. Data Flow Design

Synchronous, in-process, stateless:

1. `sys.argv` → argparse parser (now declaring `--name`, one value, default absent).
2. Parse failure (unknown option, stray positional, `--name` without a value) →
   argparse prints usage + error to stderr, exits 2; nothing on stdout.
3. Success → if `--name` was not given, print `hello_world()`; otherwise print
   `Hello, ` + NAME verbatim + `!`. One line, newline-terminated, stdout only, exit 0.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `testbed-hello` CLI (`src/testbed_utils/hello.py`, `main()`) | Parse `--name`, choose and print the greeting | argv → stdout line / stderr usage error + exit code | `roeeoz/play1` |
| `hello_world()` (same file) | Canonical default greeting — **unchanged** | — → `'Hello, world!'` | `roeeoz/play1` |
| CLI tests (`tests/test_hello_cli.py`) | Cover FR1, FR2, edge cases, keep help/bad-option regressions | — | `roeeoz/play1` |
| Library tests (`tests/test_hello.py`) | Existing; must keep passing unchanged (FR5, AC4) | — | `roeeoz/play1` |

## 5. Interface Contracts

CLI contract (the only interface; no APIs, events or cross-repo contracts):

| Invocation | stdout | stderr | exit |
|---|---|---|---|
| `testbed-hello` | `Hello, world!\n` | empty | 0 |
| `testbed-hello --name Alice` | `Hello, Alice!\n` | empty | 0 |
| `testbed-hello --name=Alice` | `Hello, Alice!\n` | empty | 0 |
| `testbed-hello --name "Ada Lovelace"` | `Hello, Ada Lovelace!\n` (verbatim, spaces kept) | empty | 0 |
| `testbed-hello --name ""` | `Hello, !\n` (literal FR2; no special handling, per spec Open Questions) | empty | 0 |
| `testbed-hello --name A --name B` | `Hello, B!\n` (argparse: last one wins) | empty | 0 |
| `testbed-hello --name` | empty | usage + `argument --name: expected one argument` | 2 |
| `testbed-hello --name -x` / `--name --bogus` | empty | same usage error (argparse treats a dash-led token as an option; `--name=-x` is the way to pass such a name) | 2 |
| `testbed-hello --help` | usage text incl. `[--name NAME]`, the unchanged `_DESCRIPTION`, no `Hello, world!` | empty | 0 |
| `testbed-hello --bogus` / `-x` / `extra` | empty | usage error | 2 |

Behaviour verified by running stdlib `argparse` (Python 3.13 locally; behaviour is
identical on the 3.10–3.12 range `pyproject.toml` declares and CI's 3.12).

## 6. Key Technical Decisions

- **Compose the named greeting in the CLI, not in `hello_world()`.** Keeps the
  library contract, its doctest and the package export byte-for-byte unchanged
  (spec Non-Goals, AC4). Alternative — adding a parameter to `hello_world()` —
  rejected: it changes the library surface the spec freezes.
- **"Not given" vs. "given empty" are distinct.** The default path is taken only
  when `--name` is absent; `--name ""` follows FR2 literally (`Hello, !`). No
  validation, trimming or fallback to `world`.
- **Use argparse's standard option handling** (long option only, one value, no
  `-n` alias, no positional, no env var). The `--name` help text must not contain
  the literal `Hello, world!` (the existing help test asserts its absence) and
  `_DESCRIPTION` stays unchanged.
- **Assumption — argparse prefix abbreviation left at its default.** argparse
  accepts unambiguous prefixes (`--nam Bob` → `Hello, Bob!`), exactly as `--he`
  already works for `--help` today. This is standard library behaviour, not a new
  alias; the spec's "no short alias" targets `-n`. Risk if wrong: a prefix that
  exited 2 before now greets; low impact, reversible by disabling abbreviation.
  Not pinned by a test either way.

## 7. Risks & Constraints

- **Regression risk** on the existing help and bad-option tests
  (`tests/test_hello_cli.py:33-53`): mitigated by keeping them unchanged and green.
- **Encoding:** names are printed verbatim through `print`; non-ASCII names rely on
  the stdout encoding (UTF-8 on CI/ubuntu). No special handling — consistent with
  "inserted exactly as given".
- **Scale / performance / security:** none material — a local, stateless,
  one-shot CLI; NAME is only echoed to the caller's own stdout (no shell, file or
  network use).
- **Gates:** source stays under `src/`, tests under `tests/`; no new files over
  200 KB; no `CI_FAIL` file.
