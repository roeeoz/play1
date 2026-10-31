# High-Level Design: hello-world bash script (story 46d9546d)

## 1. System Overview
- **What:** a new top-level folder `hello-world/` holding exactly one file, `hello.sh`. It is a directly executable bash script that prints `hello world` and exits 0.
- **Problem:** the repository has no minimal, verified shell script to start from. Its only hello feature is Python (`testbed-hello`, which prints `Hello, world!`), and that stays as it is.
- **Responsibilities:**
  - Produce the exact output defined in FR5.
  - Be directly executable through the shebang, with the executable bit recorded in git.
  - Leave every existing file unchanged.

## 2. Architecture Overview
- **Components:**
  - **C1, the hello script** (`hello-world/hello.sh`): the product deliverable.
  - **C2, the acceptance test** (`tests/test_hello_sh.py`): an optional check (spec A3) that the tech lead chooses to include.
- **Boundaries:**
  - C1 is self-contained: no inputs, no dependencies beyond `/bin/bash`.
  - C2 only runs C1 as an external process. It imports nothing from `src/`.
- **Ownership:** both belong to the single ticket t1 in repo play1.
- **External dependencies:**
  - `/bin/bash` on the developer machine and on the CI runner (ubuntu-latest).
  - The existing CI `test` job (`pip install -e ".[test]"` then `pytest`, `testpaths = ["tests"]`), which needs no changes.

## 3. Data Flow Design
- **Synchronous and local only:**
  1. The developer (or pytest) executes `hello-world/hello.sh`.
  2. The kernel reads the `#!/bin/bash` shebang and starts bash.
  3. The script writes `hello world\n` to stdout.
  4. The process exits 0.
- No state, no persistence, no events, no network.
- The test calls the script by an absolute path built from the test file's location. It sets two working directories, the repo root and a temporary directory, to show the output doesn't depend on the working directory.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| C1 `hello-world/hello.sh` | Print exactly `hello world` plus one LF, then exit 0 | In: none (no arguments, no stdin). Out: stdout `hello world\n`, exit code 0 | play1 |
| C2 `tests/test_hello_sh.py` | Check AC1–AC4 and FR1–FR6 automatically in the existing pytest/CI layer | In: the C1 file on disk. Out: pytest pass/fail | play1 |

## 5. Interface Contracts
- **CLI contract of `hello.sh`:**
  - Invocation: `./hello-world/hello.sh` from any working directory, called by relative or absolute path.
  - Arguments: none.
  - Stdout: the bytes `hello world\n` (`68 65 6c 6c 6f 20 77 6f 72 6c 64 0a`).
  - Stderr: empty.
  - Exit code: 0.
- **File contract:**
  - First line is exactly `#!/bin/bash`.
  - Git mode is `100755`.
  - Plain ASCII with LF line endings: no BOM, no CR, no trailing whitespace.
  - `hello-world/` holds no other entry, hidden files included.
- There are no cross-repo contracts.

## 6. Key Technical Decisions
- **Output:**
  - A single `echo`/`printf` of the literal text, chosen by the implementer.
  - No dependence on the environment, locale, arguments or working directory. That makes the output deterministic.
- **Executable bit:**
  - Recorded in the git index as mode `100755`, by setting it before staging or with `git update-index --chmod=+x`.
  - The implementer verifies it with `git ls-files -s`.
- **Line endings and encoding:**
  - The file is written as plain ASCII with LF endings.
  - **No `.gitattributes` is added.** It would be a new root file, which breaks AC5.
  - Instead, the byte-exact output assertion and a no-CR content check in C2 catch a CRLF regression in CI.
  - Alternative considered: `*.sh text eol=lf`. Rejected for scope, but it can be raised in a later story.
- **Automated check (spec A3):**
  - Included as `tests/test_hello_sh.py`. It is test code, not a product addition, and lives outside `hello-world/` (FR2).
  - It runs in the existing CI `test` job with no CI change.
  - It is the repo's first subprocess-based test. The pattern is local to this file.
- **Changelog / repo-gate conflict (open, P0):**
  - Default: the spec's AC5 wins, so no `CHANGELOG.md`. The PR then gets the repo-gate PLAY-G4 blocker, which a human has to waive.
  - If the owner decides the gate wins, the same ticket also creates `CHANGELOG.md` with one `## Unreleased` entry, and AC5 is amended.

## 7. Risks & Constraints
- **Gate conflict:** repo-gate rule 4 (PLAY-G4) against spec AC5/A2. A human decision is needed (see the P0 question).
- **Lost executable bit:** if the file is created through an API or tool that ignores file mode, FR4/AC3 fail in a fresh clone. Mitigations:
  - the implementer verifies mode `100755` in the index;
  - the test asserts the file is executable.
- **Stray bytes:** CRLF, a BOM or trailing whitespace would break AC4. The byte-exact assertion catches them.
- **Stray files:** an editor or OS file such as `.DS_Store` committed into `hello-world/` breaks AC2. The test asserts the folder lists exactly `["hello.sh"]`.
- **Portability:** `#!/bin/bash` is fixed by the spec. Systems without `/bin/bash` (for example NixOS) are out of scope. ubuntu-latest CI has it.
- **No regression:** `src/`, `pyproject.toml`, the Python hello tests, `ci.yml` and `README` are untouched.
- **Scale and performance:** not applicable. The script is a single process start and one write.
- **Security:** not applicable. There is no input, no network and no privileged operation.
