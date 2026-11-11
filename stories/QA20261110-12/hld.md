# HLD — QA20261110-12: the `hello aw` script and its CI test

## 1. System overview
- **What is built:** a shell script, `qa/20261111-aw/hello.sh`, that prints exactly `hello aw` and one newline. A pytest test runs it on every PR and checks that output.
- **Problem:** the factory needs proof that a tiny epic gets through every stage up to merge. That proof only counts if the test runs in the PR's required checks. The previous sanity check (PLAY-175) put its test under `qa/`, so CI never ran it (RK1).
- **Responsibilities:**
  - The script produces the exact output.
  - The test fails on any change to stdout, stderr or the exit code.

## 2. Architecture overview
- **Repository:** roeeoz/play1 only. There are two new files and no edits to existing files (FR5).
- **The script, `qa/20261111-aw/hello.sh`:**
  - POSIX `sh` only, because `/bin/sh` is dash on the CI machines.
  - Same layout as the existing `qa/` scripts: shebang, comment, `printf`.
  - Committed with mode 100755.
- **The test, `tests/test_qa_20261111_aw_hello.py`:**
  - Collected by the existing pytest setup (`testpaths = ["tests"]`).
  - Run by the existing `test` job in `.github/workflows/ci.yml` on every `pull_request`.
- **External dependencies:** none. The test uses only the standard library (`subprocess`, `pathlib`) plus pytest, which is already the `[test]` extra.

## 3. Data flow
1. A developer or the CI job runs `qa/20261111-aw/hello.sh`. It writes `hello aw\n` to stdout and exits 0.
2. On a PR, the CI `test` job runs `pip install -e ".[test]"` and then `pytest`.
   - pytest collects the new test.
   - The test finds the script from the repo root, runs it directly in a subprocess with a timeout, and captures stdout and stderr.
   - It checks exact equality.
3. The test's pass or fail result appears in the PR's checks. A person merges only when every check is green.

Everything runs synchronously. There are no events, state or persistence.

## 4. Components

| Component | Responsibility | Inputs / outputs | Repo |
| --- | --- | --- | --- |
| `qa/20261111-aw/hello.sh` | Prints the exact greeting. | Takes no input and ignores any arguments. Writes `hello aw\n` to stdout, nothing to stderr, and exits 0. | roeeoz/play1 |
| `tests/test_qa_20261111_aw_hello.py` | Checks the script's output exactly. | Reads the script's path inside the repo. Produces a pytest pass or fail. | roeeoz/play1 |

## 5. Interface contracts
- **What the script guarantees:**
  - stdout is the bytes `hello aw\n` and nothing else.
  - stderr is empty.
  - The exit code is 0.
  - It can be run directly as an executable file.
- There are no APIs, events or cross-repo contracts.

## 6. Key technical decisions
- **pytest file under `tests/`, not a shell test under `qa/`.** This is the only place the CI `test` job collects tests, so it is what closes RK1.
- **Run the script directly, not through `sh hello.sh`.** That way the test also catches a missing executable bit or a broken shebang.
- **Compare for exact equality, not containment.**
  - `stdout == "hello aw\n"` catches extra, missing or different characters, and both a missing newline and an extra one (RK2).
  - `stderr == ""` and `returncode == 0` cover AC4.
- **Follow the existing pattern** from `tests/test_qa_20261109_s1_a.py`:
  - Find the repo root from `__file__`.
  - Use `subprocess.run` with `capture_output`, `text` and a timeout.
  - The test may also assert the file's shape (shebang, executable bit, no `\r`) in the same file.
- **Alternatives rejected:**
  - A shell test under `qa/`: CI never runs it. That is exactly the RK1 failure.
  - A new CI step: the spec rules out changing the build process.
  - Registering the script as a console script: out of scope, and the spec says the registered commands must not change.

## 7. Risks & constraints
- **Repo gate rule 4 (PLAY-G4) conflicts with the spec.**
  - The `claims-dev` repo-gate expects a new line under `## Unreleased` in `CHANGELOG.md`.
  - FR5 and AC6 forbid changing any existing file, and the spec calls this "a deliberate departure".
  - The design follows the spec. If the gate is active on this PR, its blocker has to be waived for this story by someone with authority. The build must not resolve this on its own.
- **Executable bit or CRLF line endings.** Either one breaks running the script directly. The test catches both, and the committed mode has to be 100755.
- **Required checks.** If branch protection doesn't make the `test` job a required check, a red test doesn't technically block merge. The human approval step still applies (spec §8).
- **Runtime and stability.** The current suite runs about 133 tests in under 1 second. The new test adds milliseconds, has no network, clock or time dependency, and its subprocess timeout guards against a hang. It works on CPython 3.10 and later.
- **Scope.** The diff must not touch the existing `qa/` scripts, the existing `tests/test_qa_*` files, `pyproject.toml`, `CHANGELOG.md` or CI. Those existing tests pin the earlier scripts, so editing them would turn CI red.
