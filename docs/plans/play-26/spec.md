# Feature Specification Document

## 1. Feature Overview

**Summary:** A `testbed-num-summary` console script that reads a list of numbers — from a file path argument or from standard input — and prints a six-statistic summary (count, min, max, mean, median, 90th percentile) to standard output, built on top of the `mean`, `median`, and `percentile` helpers already merged in `numutils` (US-01).

**Problem statement:** A package user who has a file of numbers, or numbers on standard input, currently has no way to get a quick statistical summary without writing Python code or pulling in a library like numpy. This script closes that gap with a zero-code, dependency-free command-line tool.

**Target users / actors:** Package users of testbed-utils who want a quick numeric summary from the command line, without writing any code.

---

## 2. Goals & Non-Goals

### Goals
- Let a user get count, min, max, mean, median, and the 90th percentile of a list of numbers by running one command against a file or piped input.
- Support both a file-path argument and standard input as number sources, with whitespace- or newline-separated numbers.
- Refuse to read a user-supplied file path that resolves outside the current working directory at invocation, protecting the user from accidentally exposing files outside the intended location.
- Give a clear, single-line error message (to standard error, non-zero exit) when there are no numbers to summarize, or when the given path is not allowed.
- Answer `--help` with a one-line description of the script's purpose.
- Introduce no new runtime dependency.

### Non-Goals
- Any statistic beyond count, min, max, mean, median, and the 90th percentile (e.g., standard deviation, variance, mode, or an arbitrary user-chosen percentile).
- Any GUI, web service, database, or network interaction.
- Changes to the CI gate mechanism.
- Reading numbers in any format other than whitespace- or newline-separated plain numbers.

---

## 3. Functional Requirements

- **FR1 — Input sourcing:** The script shall accept an optional file-path argument. When given, it reads numbers from that file. When omitted, it reads numbers from standard input. Numbers may be separated by whitespace and/or newlines.
- **FR2 — Path safety:** Before opening a user-supplied file path, the script shall resolve the path fully (following any symlinks and collapsing relative segments) and confirm the resolved path is the current working directory at invocation, or a location beneath it. If the resolved path falls outside that directory (whether the input path was absolute, like `/etc/passwd`, or relative and traverses outward), the script shall refuse to open the file. A relative path that contains `..` segments but still resolves to a location inside the working directory is allowed. The script never executes or imports file content — it only reads it as text.
- **FR3 — Statistics computation:** Using the existing `numutils` helpers, the script shall compute count, min, max, mean, median, and the 90th percentile of the numbers found.
- **FR4 — Success output:** On success, the script shall print exactly six lines to standard output, in this fixed order: `count: <value>`, `min: <value>`, `max: <value>`, `mean: <value>`, `median: <value>`, `p90: <value>`, and exit with status 0.
- **FR5 — Empty-input error:** If no numbers are found in the input (file or stdin), the script shall print exactly one line to standard error stating that no numbers were found, print nothing to standard output, and exit with a non-zero status.
- **FR6 — Disallowed-path error:** If the given file path is rejected per FR2, the script shall print exactly one line to standard error stating that the path is not allowed, and exit with a non-zero status.
- **FR7 — Help text:** Running the script with `--help` (and no other arguments) shall print a one-line summary of the script's purpose to standard output and exit 0.

**Edge cases covered:**
- A single-number input (count of 1; min, max, mean, median, and p90 all equal that number).
- Numbers supplied via piped standard input rather than a file.
- A path argument that is absolute and outside the working directory (e.g., `/etc/passwd`) — rejected.
- A path argument that contains `..` but still resolves inside the working directory — accepted.
- A file that exists but contains no parseable numbers — treated as empty input.

---

## 4. User Experience & Behavior

**Flow 1 — Summarize a file:** The user runs `testbed-num-summary path/to/numbers.txt`. The script prints the six summary lines to the terminal and exits cleanly.

**Flow 2 — Summarize piped input:** The user pipes numbers into the script, e.g. `printf "10\n20\n30\n" | testbed-num-summary`, with no file argument. The script reads from standard input and prints the same six-line summary.

**Flow 3 — Empty input:** The user points the script at a file with no numbers in it (or pipes empty input). Instead of a summary, the user sees one line on standard error saying no numbers were found, sees nothing on standard output, and the command's exit status is non-zero (scriptable failure).

**Flow 4 — Disallowed path:** The user supplies a path that resolves outside the directory they invoked the command from (for example, an absolute system path, or a relative path engineered to escape via `../../`). The script does not open the file; the user sees one line on standard error saying the path is not allowed, and the exit status is non-zero.

**Flow 5 — Help:** The user runs `testbed-num-summary --help` and sees a single line describing the script's purpose (e.g., "Print mean, median and the 90th percentile of the numbers in a file."), and the command exits 0.

**Output format (user-observed, exact):** Six lines, always in this order, each `"<name>: <value>"`:
```
count: 5
min: 1
max: 5
mean: 3
median: 3
p90: 4.6
```
No extra lines, headers, or decoration are printed on success.

**Error messages (user-observed):** Exactly one line on standard error in each error case — one wording for "no numbers found," a different wording for "path not allowed." Nothing is printed to standard output in either error case.

---

## 5. Acceptance Criteria

1. **Happy path — file input.** Given a fixture file containing `"1 2 3 4 5"`, running the script with that file's path prints exactly: `count: 5`, `min: 1`, `max: 5`, `mean: 3`, `median: 3`, `p90: 4.6` (six lines, this order) to standard output, and exits 0.
2. **Happy path — stdin input.** Given `"10"`, `"20"`, `"30"` piped to standard input with no file argument, the script prints `count: 3`, `min: 10`, `max: 30`, `mean: 20`, `median: 20`, `p90: 28` to standard output, and exits 0.
3. **Boundary — single number.** Given a fixture file containing `"42"`, the script prints `count: 1`, `min: 42`, `max: 42`, `mean: 42`, `median: 42`, `p90: 42`, and exits 0.
4. **Error — empty input.** Given a fixture file with no numbers, the script prints exactly one line to standard error stating no numbers were found, prints nothing to standard output, and exits non-zero.
5. **Error — path escapes the working directory.** Given a file path that resolves outside the current working directory at invocation (e.g., an absolute path like `/etc/passwd`, verified by resolving the path and checking it is not the working directory or a location beneath it), the script refuses to open the file, prints exactly one line to standard error stating the path is not allowed, and exits non-zero.
6. **Accepted — path contains `..` but resolves inside the working directory.** Given a relative path containing `..` segments whose fully resolved location is still within the current working directory, the script accepts and reads it normally (no rejection).
7. **Help.** Given `--help` and no other arguments, the script prints a one-line summary of its purpose to standard output and exits 0.

---

## 6. Dependencies & Constraints (product-level)

- **Depends on US-01:** the `mean`, `median`, and `percentile` helpers in `numutils` — already merged and available.
- **No new runtime dependency** may be introduced by this script; if a test-only dependency is needed, it must be declared under the optional test extra, not as a runtime dependency.
- **Deterministic CI:** all new tests must use in-memory data, fixture files, or simulated standard input — never a real interactive terminal, the network, or the system clock.
- **Directory anchor for path safety (confirmed by the developer):** the "intended directory" that a supplied path must stay within is the current working directory at the moment the script is invoked. A path is rejected if, after being fully resolved, it is not that directory or a location beneath it — regardless of whether the original input path was absolute or relative, and regardless of whether it contains `..` segments (a `..`-containing path that still resolves inside the working directory is accepted).
- **Out of scope:** any statistic beyond the six named; any third-party numeric library; any GUI, web, database, or network surface.

---

## 7. Technical Design (deferred to STRUCTURE)

The following are noted as product-imposed constraints only; STRUCTURE owns how they are implemented:
- The path-resolution and containment check (comparing a fully resolved path against the fully resolved working directory) is a confirmed behavioral requirement driving Acceptance Criteria 5–6, but the specific resolution mechanism, symlink-handling edge cases beyond "resolve fully," and code structure are for STRUCTURE to design.
- Exact wording of the two error messages, the precise non-zero exit code(s) used for each error path, and numeric formatting/precision for statistic values beyond what the worked examples pin down, are left to STRUCTURE (see Open Questions).
- Module/file layout (e.g., whether the script lives in its own module or elsewhere) and its `pyproject.toml` console-script entry are STRUCTURE decisions.

---

## 8. Open Questions

- **Numeric formatting:** worked examples are consistent with Python's default numeric string formatting, but no fixed decimal precision is specified for values that don't divide evenly (e.g., a mean with a long decimal expansion). Non-blocking; STRUCTURE may pin this down, defaulting to plain Python formatting if not otherwise specified.
- **Exit code values:** the specific non-zero exit code for each of the two error paths (empty input, disallowed path) is intentionally left unpinned — any non-zero value satisfies the acceptance criteria as written. Non-blocking.
