# Specification — Add a --json output flag to the CLI

# Feature Specification Document

## 1. Feature Overview

Add a new `testbed-utils` CLI entry point to the `testbed_utils` package. The CLI exposes all exported library functions as subcommands. A global `--json` flag switches all output — results and errors — from plain text to machine-readable JSON, enabling use in shell pipelines with `jq` and similar tools.

**Problem statement:** Scripting and automation users cannot consume the library's functionality from the shell without writing ad-hoc Python wrapper scripts. No CLI exists today. The ticket's premise that "the output is human-readable today" is inaccurate; there is no output at all. Both the CLI and the `--json` flag are new.

**Target users / actors:** Scripting users — developers and CI/CD pipelines that invoke shell commands and process their output programmatically.

---

## 2. Goals & Non-Goals

### Goals
- Create a `testbed-utils` CLI entry point that exposes all six exported library functions as subcommands.
- Add a global `--json` flag that switches stdout to a `{"result": <value>}` JSON envelope on success.
- When `--json` is active, errors are written to stdout as `{"error": "<message>"}` with exit code 1 instead of plain-text stderr messages.
- Without `--json`, each subcommand prints its return value as a plain string to stdout and exits 0; errors go to stderr.

### Non-Goals
- Adding any library functions not already exported by the package.
- Building a REST, RPC, or interactive interface.
- Shell completion scripts.
- Per-subcommand `--json` flags (the flag is global only).

---

## 3. Functional Requirements

**FR1 — CLI entry point:** The package installs a `testbed-utils` command available on PATH after `pip install -e .`.

**FR2 — Subcommands:** Each of the six exported library functions becomes a subcommand. Function arguments map 1-to-1 to positional CLI arguments in declaration order. Subcommand names use kebab-case derived from the function name (e.g., `days_between` → `days-between`).

**FR3 — Default (plain-text) output:** Without `--json`, each subcommand prints `str(result)` to stdout and exits 0.

**FR4 — Global `--json` flag:** `--json` is accepted immediately after `testbed-utils` (before the subcommand name). It controls the output format for all subcommands uniformly.

**FR5 — JSON success output:** With `--json`, a successful subcommand writes `{"result": <value>}` to stdout and exits 0. The value uses the native JSON type for the return: number for `int`/`float`, string for `str`, boolean for `bool`.

**FR6 — JSON error output:** With `--json`, any error (wrong argument count, invalid argument type, or library exception) writes `{"error": "<human-readable message>"}` to stdout and exits 1.

**FR7 — Plain-text error output:** Without `--json`, errors are written to stderr and the CLI exits 1; stdout is empty.

**FR8 — Help:** `testbed-utils --help` and `testbed-utils <subcommand> --help` print usage and exit 0.

---

## 4. User Experience & Behavior

### Happy path — plain text
```
$ testbed-utils days-between 2024-01-01 2024-03-01
60
```

### Happy path — JSON (integer)
```
$ testbed-utils --json days-between 2024-01-01 2024-03-01
{"result": 60}
```

### Happy path — JSON (boolean)
```
$ testbed-utils --json is-weekend 2024-01-06
{"result": true}
```

### Happy path — JSON (string)
```
$ testbed-utils --json humanize-delta 3600
{"result": "1 hour"}
```

### Error — plain text (wrong arg count)
```
$ testbed-utils days-between 2024-01-01
error: days-between requires 2 arguments, got 1   # to stderr
(exit 1)
```

### Error — JSON (wrong arg count)
```
$ testbed-utils --json days-between 2024-01-01
{"error": "days-between requires 2 arguments, got 1"}
(exit 1, message on stdout so jq can parse it)
```

### Pipeline use-case
```
$ testbed-utils --json days-between 2024-01-01 2024-03-01 | jq .result
60
```

---

## 5. Acceptance Criteria

- **AC1:** `pip install -e .` makes `testbed-utils` available on PATH.
- **AC2:** Each of the six exported library functions is reachable as a subcommand; calling it with correct arguments prints the correct result and exits 0.
- **AC3:** `testbed-utils --json <subcommand> <args>` writes valid JSON to stdout; `jq .result` extracts the value.
- **AC4:** The JSON success envelope is always `{"result": <value>}` with the value in its native JSON type (number / string / boolean).
- **AC5:** Any error under `--json` produces `{"error": "<message>"}` on stdout and exits 1; `jq .error` extracts the message.
- **AC6:** Any error without `--json` writes a message to stderr, nothing to stdout, and exits 1.
- **AC7:** `testbed-utils --help` and `testbed-utils <subcommand> --help` print usage and exit 0.
- **AC8:** All existing and new pytest tests pass; CI remains green; no `CI_FAIL` file is introduced.
- **AC9:** New tests cover both the default and `--json` output paths for each subcommand, and the error path under `--json`.

---

## 6. Dependencies & Constraints

- Depends only on the six functions already exported by `textutils.py` and `dateutils.py`; no new library functions are in scope.
- The chosen CLI framework must be declared as a project dependency in `pyproject.toml` alongside a `[project.scripts]` entry for `testbed-utils`.
- The CI gate (`pytest` + absence of `CI_FAIL`) must remain green.
- The `--json` flag must be global — one flag controls both success and error output format uniformly across all subcommands.

---

## 7. Technical Design (deferred to STRUCTURE)

Choices deferred: CLI framework (argparse stdlib vs. click/typer), `pyproject.toml` entry-point wiring, argument-type coercion strategy, subcommand dispatch pattern, and test harness integration. The STRUCTURE stage owns these decisions.

**Product constraint handed to STRUCTURE:** Under `--json`, the entire stdout stream must be valid JSON at all times — no mixed plain-text and JSON lines. Argparse's default plain-text error messages must be suppressed or intercepted.

---

## 8. Open Questions

None blocking. The following were resolved by assumption for this testbed fixture and should be confirmed at STRUCTURE review:
- All six exported functions are exposed (not a curated subset).
- CLI invocation name is `testbed-utils`.
- JSON success envelope is `{"result": value}` (not a bare scalar).
- JSON error envelope `{"error": "message"}` is written to stdout (not stderr) so the entire stdout stream remains valid JSON under `--json`.
