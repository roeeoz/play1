# HLD — PLAY-167: farewell script `qa/20261109-s3/bye.sh`

Target repo: roeeoz/play1 · base branch: `qa-20261109-s3-base` · spec: `stories/PLAY-167/spec.md` · epic PRD: Confluence pageId 34013185 (backlog 34177025).

## 1. System Overview
- **What is built:** one bash script, `qa/20261109-s3/bye.sh`. It always prints `bye`. When its first argument is not empty, it prints a second line, `bye <first argument>`. It exits 0.
- **Problem:** the factory needs a very small request that goes from spec to a single merged PR: one story, one script and one CHANGELOG line (G3).
- **Responsibilities:** print fixed greeting lines to stdout and exit 0. No file I/O, no input validation, no help text.

## 2. Architecture Overview
- **Component:** a standalone CLI script that does not depend on the Python package `play1` or its tests.
- **Location:** `qa/20261109-s3/` already exists on the base branch and holds only `BASE_MARKER.md`, which must not change. It sits next to the existing `qa/s3-a.sh` and `qa/s3-hello.sh`, which must not change either.
- **Repo-gate obligations** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):
  - Rule 2: a new shell script is executable and starts with a shebang.
  - Rule 3: no file is larger than 200 KB.
  - Rule 4 (PLAY-G4): one line under `## Unreleased` in `CHANGELOG.md`.
- **External dependencies:** only `/bin/bash`, which exists on ubuntu-latest CI and in dev environments (bash 5.x). No third-party code (Infrastructure R2, Compliance R6).

## 3. Data Flow Design
- Synchronous, single process: argv → decide whether a name was given → stdout → exit code.
- `$1` is unset or empty → one line: `bye`.
- `$1` is not empty → two lines: `bye`, then `bye ` followed by `$1` exactly as given.
- `$2` and any later arguments are ignored.
- No state is kept, no files are read or written, and no events are produced.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
| --- | --- | --- | --- |
| `qa/20261109-s3/bye.sh` | Print the general farewell and, when a name is given, the personal farewell | Input: zero or more CLI args. Output: 1–2 lines on stdout, exit 0 | roeeoz/play1 |
| `CHANGELOG.md`, one line | Meet repo-gate PLAY-G4 | One `- PLAY-167: add ...` line after the PLAY-156 line under `## Unreleased` | roeeoz/play1 |

## 5. Interface Contracts
- **CLI contract** (the only interface):

| Invocation | Output | Exit code |
| --- | --- | --- |
| no arguments | `bye` | 0 |
| `""` | `bye` | 0 |
| `Alice` | `bye`, then `bye Alice` | 0 |
| `Alice Bob` | `bye`, then `bye Alice` | 0 |
| `"Alice Smith"` | `bye`, then `bye Alice Smith` | 0 |
| `--help` | `bye`, then `bye --help` | 0 |

- The output contains exactly these lines, each ending in LF, with nothing on stderr.
- There are no APIs, events or cross-repo contracts.

## 6. Key Technical Decisions
- **`#!/bin/bash`, not `#!/bin/sh`:** the PO decided this (spec FR1, P1). It knowingly departs from the `#!/bin/sh` style of the other `qa/` scripts and from PLAY-156's HLD §6. The script needs nothing bash-specific, so the choice carries no behavioral risk.
- **Name printed literally:** the name is passed as a quoted argument to a format string and is never placed inside the format string. Names containing `%`, `\` or a leading `-` (such as `--help` or `-n`) then print exactly as given, and a name with a space stays whole (FR6). A prototype check confirmed this on bash 5.2.
- **Empty first argument counts as no name** (FR5), so an empty string doesn't produce a trailing `bye ` line.
- **Exit code 0 is natural:** the script has no failure path. The implementer must make sure the last command doesn't leave a non-zero status, for example from a false test.
- **No pytest test:** the spec puts tests out of scope (RK2). Acceptance is shown by manual runs recorded in the PR description.
- **One-line purpose comment on line 2:** optional. It follows the `qa/` convention, and the implementer may include it.
- **Alternatives rejected:**
  - A Python console script: it would touch the package and break the 'one script' scope.
  - Adding a pytest test: out of scope.
  - Splitting the CHANGELOG line into its own PR: each PR must pass the gate on its own.

## 7. Risks & Constraints
- **Executable bit:** the file must be committed as mode `100755`, which `git ls-files -s` shows. Rule 2 fails otherwise, and CI will not catch it.
- **LF line endings:** the file must not use CRLF, or the shebang breaks.
- **No CI coverage of the output:** pytest (`testpaths = ["tests"]`) never runs the script. The PR description must show manual runs of acceptance criteria 1–4, 7 and 8 with their exit codes.
- **Scope (FR9):** the diff outside `stories/PLAY-167/` must be exactly the new `bye.sh` and one CHANGELOG line. The PR must not add a `CI_FAIL` file and must not touch `tests/`, `.github/`, `pyproject.toml`, `qa/s3-a.sh`, `qa/s3-hello.sh` or `qa/20261109-s3/BASE_MARKER.md`.
- **Test-time budget (G4):** adding no tests leaves the existing pytest suite and its duration unchanged, well under 60 s.
- **Scale and security:** neither applies. The script does no file I/O (Security R5 n/a), and examples use only made-up names (Security R4).
- **Traceability (Compliance R7):** the PR body cites PLAY-167 and the epic PRD.
