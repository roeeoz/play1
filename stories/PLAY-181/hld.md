# High-level design: PLAY-181, a script that prints "hello s3" and its automated test

## 1. System overview
- **What is built:** a standalone Python script `src/qa_20261111_s3.py` that prints `hello s3`, a pytest test `tests/test_qa_20261111_s3.py` that checks what the script outputs, and one `CHANGELOG.md` line under `## Unreleased` for PLAY-181.
- **Problem:** the epic "QA-20261111-S3 hello s3 script" checks that a tiny one-story change can go through the whole pipeline and end as one PR with every required check green, without breaking existing tests.
- **Responsibilities:**
  - the script prints exactly one line, writes nothing to stderr and exits with code 0
  - the test proves that behaviour on every CI run
  - the CHANGELOG line satisfies layout gate rule 4

## 2. Architecture overview
- **Repository:** only `roeeoz/play1` (id `5c6a2c74-bde7-47e2-bb43-d0d8566d942e`), based on `main`.
- **Components:**
  - **Greeting script.** A top-level module in `src/`. It is not a package, not under `[project.scripts]` and not a public function, so it is not picked up by `packages.find` and is not an installed command.
  - **Output test.** Lives in `tests/`. Plain `pytest` collects it through the existing `testpaths = ["tests"]`.
  - **CHANGELOG entry.** One line appended under `## Unreleased`, after the PLAY-175 line.
- **Boundaries:** nothing imports the script, and the test reaches it only as a file on disk. No existing module, config, CI workflow or file under `qa/` changes.
- **External dependencies:** none new. pytest is already in the `test` extra.

## 3. Data flow
- Developer or CI runs `python src/qa_20261111_s3.py` → stdout `hello s3\n`, empty stderr, exit code 0.
- CI `test` job: `pip install -e ".[test]"` → `pytest` → collects `tests/test_qa_20261111_s3.py` → the test starts the script as a child process with the current interpreter → it compares the exit code, stdout and stderr exactly → the test passes or fails.
- Everything runs synchronously in one process tree. There are no events, no network and no clock.

## 4. Component breakdown
| Component | Responsibility | Inputs / outputs | Repo |
| --- | --- | --- | --- |
| `src/qa_20261111_s3.py` | Prints the greeting when run directly | In: none (no args, stdin or config). Out: stdout `hello s3\n`, exit code 0 | roeeoz/play1 |
| `tests/test_qa_20261111_s3.py` | Checks the output a person running the script sees | In: the script file, found relative to the test file. Out: pass or fail | roeeoz/play1 |
| `CHANGELOG.md` (one added line) | Release note, required by gate rule 4 | Out: one line mentioning PLAY-181 and the added script | roeeoz/play1 |

## 5. Interface contracts
- **The script's external contract is a command line.** It takes no arguments. stdout is exactly `hello s3\n`, stderr is empty and the exit code is 0. The script has no Python API.
- **There are no cross-repo contracts, APIs or event schemas.**

## 6. Key technical decisions
- **The test runs the script as a separate process with the current interpreter, and does not import it.**
  - This checks stdout, stderr and the exit code exactly as a person sees them (spec §7).
  - It does not depend on the editable install putting `src/` on the import path.
  - It does not depend on a shebang or the executable bit.
  - It follows the existing pattern in `tests/test_qa_s3_greeting.py` and `tests/test_qa_20261109_s1_a.py`.
  - Rejected alternative: import the module and capture stdout in-process (the `test_hello_cli.py` style). That suits installed console scripts and would not check the exit code of a real run.
- **The print sits behind a guard that only runs it when the file is executed directly.** The editable install makes the module importable, so an unguarded print would fire on any import. The guard costs nothing and does not change FR1 behaviour.
- **The file is a top-level module in `src/`, not a package.** This meets gate rule 1 while respecting the spec's ban on packages, installed commands and public functions. The trade-off is that a normal wheel will not ship it, which is acceptable: it is only a QA practice artifact.
- **No config or CI changes.** `testpaths = ["tests"]` already covers FR3.

## 7. Risks and constraints
- **Scope (AC5):** outside `stories/PLAY-181/`, the diff must be exactly the two new files plus one added line in `CHANGELOG.md`. Existing CHANGELOG lines, including PLAY-175, and everything under `qa/` must stay unchanged (RK2).
- **Epic documents are out of date:** the epic PRD and backlog still name `qa/` paths and "exactly two files". The PR description must explain the agreed change so reviewers aren't confused, and must cite PLAY-181 and the epic PRD (`pageId=36798465`) for FR7.
- **Performance:** the new test runs in about 0.01 s, and the prototype's full suite took about 1.5 s. Both are far inside the 1 s and 60 s limits. A 10 s subprocess timeout keeps a hung run from stalling CI.
- **Compatibility:** the syntax must run on CPython 3.10 and later. CI uses 3.12.
- **Merge:** all required checks must be green (`test`, `gate`, layout gate), no `CI_FAIL` file may exist at the repo root, and only a human merges.
