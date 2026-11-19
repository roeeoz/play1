# Feature Specification Document — `testbed-hello` greets by name

## 1. Feature Overview

**What is being built.** An optional `--name NAME` argument for the `testbed-hello`
console script (entry point `testbed_utils.hello:main`, declared in `pyproject.toml`
under `[project.scripts]`). Run with no arguments, the script keeps printing
`Hello, world!`; run with `--name NAME`, it prints `Hello, NAME!`.

**Problem.** Today the script (`src/testbed_utils/hello.py`, `main()`) accepts no
arguments other than `--help`. Any other argument is rejected with a usage error
(exit code 2), so a caller cannot get a personalised greeting.

**Target users.** Whoever runs `testbed-hello` from a terminal or a script, here the
developers and pipelines that use this testbed repository.

## 2. Goals & Non-Goals

### Goals
- G1. A caller can pass `--name NAME` and get `Hello, NAME!` on standard output.
- G2. Calling the script without `--name` behaves exactly as it does today.
- G3. Automated tests cover both cases and sit next to the existing hello tests
  (`tests/test_hello_cli.py`, `tests/test_hello.py`).

### Non-Goals
- No other behaviour changes, as the story states. That covers the `hello_world()`
  library function and its `'Hello, world!'` doctest, the package export
  (`testbed_utils.hello_world`), the help description text, and the error handling
  for unrecognised options.
- No short alias (such as `-n`), no positional name, no environment variable or
  config file as a source of the name, and no other greeting wording.
- No changes to the other console scripts, `qa/` scripts, or the `hello-world/`
  folder.

## 3. Functional Requirements

- **FR1 — Default greeting unchanged.** Input: `testbed-hello` with no arguments.
  Output: exactly `Hello, world!` followed by a newline on standard output, nothing on
  standard error, exit code 0 (matching the current test in `tests/test_hello_cli.py`).
- **FR2 — Greeting by name.** Input: `testbed-hello --name NAME`. Output: exactly
  `Hello, NAME!` followed by a newline on standard output, with NAME inserted exactly
  as given. Nothing on standard error, exit code 0. Example: `--name Alice` prints
  `Hello, Alice!`.
- **FR3 — Optional.** `--name` is optional. Leaving it out is the FR1 case, not an
  error.
- **FR4 — Tests.** Automated tests cover FR1 and FR2. They go next to the existing
  hello tests under `tests/` and run in the repository's `pytest` gate.
- **FR5 — Nothing else changes.** `--help` still exits 0 with the usage text and the
  existing description. Unrecognised options and stray positional arguments (for
  example `--bogus`, `-x`, `extra`) are still rejected with a usage error and exit
  code 2. `hello_world()` still returns `'Hello, world!'`.

**Edge cases.**
- `--name` given without a value is an incomplete option. The script reports a usage
  error and exits with code 2, as it does today for any argument it cannot accept.
  This error path is already in the product and comes with the option; it adds no
  new behaviour.
- NAME values that contain spaces (quoted by the shell) are inserted verbatim, as
  FR2 says.
- An empty NAME (`--name ""`) is not addressed by the story. See Open Questions.

## 4. User Experience & Behavior

**Flow.** The user runs `testbed-hello` and sees `Hello, world!`. They run
`testbed-hello --name Alice` and see `Hello, Alice!`. They run `testbed-hello --help`
and see the usage text, which now lists the `--name` option together with the
existing description.

**Output format.** The greeting is a single line on standard output and nothing is
added to it. On success nothing is written to standard error.

**Errors.** No new user-facing error messages. Invalid invocations show the same
standard usage/error output on standard error as they do today, with exit code 2.

No visual style, sound, or motion requirements apply. This is a plain CLI.

## 5. Acceptance Criteria

1. Happy path, greeting by name. **Given** the installed package, **when** the user runs `testbed-hello --name Alice`, **then** standard output is exactly `Hello, Alice!` followed by a newline, **and** standard error is empty and the exit code is 0.
2. Regression, default greeting. **Given** the installed package, **when** the user runs `testbed-hello` with no arguments, **then** standard output is exactly `Hello, world!` followed by a newline, **and** standard error is empty and the exit code is 0.
3. Scope boundary, help and invalid arguments unchanged. **Given** the installed package, **when** the user runs `testbed-hello --help`, **then** it exits 0 with the usage text and the existing description, **and** `--bogus`, `-x` or `extra` still exit 2 with a usage error on standard error and nothing on standard output.
4. Scope boundary, library function unchanged. **Given** the package, **when** `testbed_utils.hello_world()` is called, **then** it returns `'Hello, world!'`, **and** its docstring example still passes.
5. Tests present. **Given** the pull request, **when** its `test` CI job runs `pytest`, **then** it includes tests for both the no-argument and the `--name` cases next to the existing hello tests under `tests/`, **and** the job is green.

## 6. Dependencies & Constraints (product-level)

- Repository rules that apply to every pull request: Python source under `src/` and
  tests under `tests/` (the play1 layout gate, `.factory/plugins/claims-dev/skills/repo-gate`),
  plus `pip install -e ".[test]"` and `pytest` green in `.github/workflows/ci.yml`
  (`.factory/testing.md`). The story fits both, and no exemption is needed.
- A person reviews and merges the pull request. "Done" is shown by the pull
  request's required checks being green.
- No dependency on other stories.

## 7. Technical Design (deferred to STRUCTURE)

How the option is parsed and how the greeting is composed is left to STRUCTURE.
The product constraints are that `hello_world()` keeps its current contract and
that the default output stays byte-for-byte the same.

## 8. Open Questions

- Empty name (`--name ""`). The story does not say what happens. Read literally,
  FR2 prints `Hello, !`. No acceptance criterion pins it, and STRUCTURE should not
  add special handling (such as an error, or falling back to `world`) unless the
  product owner asks for it.
