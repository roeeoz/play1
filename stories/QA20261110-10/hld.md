# HLD — QA20261110-10: run a script that prints "hello from a3"

## 1. System overview
- **What:** a new QA shell script in play1, `qa/20261111-a3/hello.sh`. Run with no input, it prints exactly `hello from a3` followed by a newline and exits with code 0. The PR also adds the one `CHANGELOG.md` line that the repository gate requires.
- **Problem:** the epic tests whether the factory can deliver a small, precise request without widening it. The leading indicator is one product file, with green required checks.
- **Responsibilities:** print one exact line and exit 0. Leave everything that exists in play1 unchanged.

## 2. Architecture overview
- **Components:**
  1. The script `qa/20261111-a3/hello.sh`. It is standalone: it doesn't depend on the `play1` package and isn't registered as a console script.
  2. One appended bullet under `## Unreleased` in `CHANGELOG.md`.
- **Boundaries:**
  - Nothing under `src/`, `tests/`, `pyproject.toml`, `.github/`, `hello-world/` or other `qa/` paths is touched.
  - The plan folder `stories/QA20261110-10/` belongs to the factory and is outside the product scope.
- **External dependencies:** none beyond a POSIX `/bin/sh`. On the CI runner and locally that is `dash`.
- **Repository:** roeeoz/play1 only (`3de95313-a662-49a5-b8a0-56b5dd990c4d`).

## 3. Data flow
- It is synchronous and trivial: the user runs `sh qa/20261111-a3/hello.sh` or `./qa/20261111-a3/hello.sh`, the shell runs one `printf`, and the script writes to stdout and exits 0.
- It reads no input, files, network or environment. It has no state, events or async processing.

## 4. Component breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `qa/20261111-a3/hello.sh` | Print the greeting | In: none. Out: stdout `hello from a3\n`, empty stderr, exit 0 | roeeoz/play1 |
| `CHANGELOG.md` entry | Record the addition, which gate rule 4 (PLAY-G4) requires | One bullet appended under `## Unreleased` | roeeoz/play1 |

## 5. Interface contracts
- **Command-line contract:** no arguments and no stdin. Exactly one line, `hello from a3` plus LF, goes to stdout. Nothing goes to stderr. The exit code is 0. Any arguments or stdin are outside the contract, and no option handling is added.
- **File contract:**
  - Mode 100755 in git (`core.fileMode=true`).
  - The first line is `#!/bin/sh`.
  - LF line endings, no CR.
  - Far under 200 KB.
- **CHANGELOG contract:** one new bullet, appended at the end of the `## Unreleased` list. It follows the existing form ``- <KEY>: add `<path>`, a QA script that prints `<text>`.``. No existing line is edited.
- **Cross-repo contracts:** none.

## 6. Key technical decisions
- **POSIX `sh` and `printf` rather than `bash` and `echo`:** this matches the `qa/` convention and gives the same output under dash, bash and busybox. `echo`'s handling of escapes and `-n` varies between shells.
- **Shell rather than Python:** settled by the PO. It satisfies gate rule 1 (Python only under `src/`) without an exemption.
- **One comment line after the shebang:** follows the repo convention, for example `qa/20261110-s3/hello.sh`. The comment names the story.
- **No tests:** an explicit spec non-goal. Evidence for AC2 and AC3 is a manual run recorded in the PR description, together with the existing green pytest run in CI.
- **Alternatives rejected:**
  - A `test_hello.sh` like PLAY-175's: it breaks AC4.
  - A pytest file: it breaks the non-goals and AC4.
  - A console-script entry: a non-goal.

## 7. Risks & constraints
- **Missing executable bit:** if the file is committed without mode 100755, gate rule 2 fails and the `./` invocation fails. Verify with `git ls-files -s`.
- **CRLF or a trailing-whitespace variant:** would break the exact output or the shebang. Keep LF endings.
- **Missing or altered CHANGELOG line:** a missing line raises the PLAY-G4 blocker, and editing an existing line breaks AC4.
- **Scope creep (RK1):** any extra product file breaks AC4.
- **CI and performance:** CI is unchanged, so G4's test-time budget is unaffected. There are no secrets and no third-party code.
- **Branch protection:** whether `test` and `gate` are marked required on `main` can't be seen from the checkout. The spec asserts that they are.
