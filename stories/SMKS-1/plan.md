# Plan — Hello world bash script in a dedicated folder (SMKS-1)

## Context

SMKS-1 adds `hello-world/hello.sh`, a bash script at the root of `play1`. It sits alone in its own folder, starts with `#!/bin/bash`, is executable, and prints exactly `hello world` to stdout with exit code 0. The four acceptance criteria are: exact output with exit 0 (scenario 1), the folder holds only `hello.sh` (scenario 2), the script runs directly through its shebang (scenario 3), and the captured output is exact (scenario 4). Pytest tests in `tests/` verify it, and a `CHANGELOG.md` line satisfies the repository gate. The change lands on the work branch `halo/feat/smks-1-20261125-120918`, cut from the frozen target branch `bench/two-lines/smoke`. The approved requirement is in `spec.md`, the design in `hld.md` and the breakdown (one work item, `t1`) in `work-items.md`. All three sit beside this file in `stories/SMKS-1/`.

## Research findings

- **What exists today:** the repository holds only Python: `src/testbed_utils/`, `src/guestbook/` and `tests/`. There is no `hello-world/` folder, no `CHANGELOG.md`, no `.gitattributes` and no shell script. `git ls-files -s` lists no file with mode `100755`, so this is the repository's first executable file. The checkout has `core.fileMode=true`.
- **Must be created:** `hello-world/hello.sh`, `tests/test_hello_sh.py` and `CHANGELOG.md`. No existing file changes.
- **Test collection:** `pyproject.toml:26-28` sets `[tool.pytest.ini_options] testpaths = ["tests"]` and `addopts = "-q"`. Any `tests/test_*.py` is collected automatically, and there is no `conftest.py`.
- **Test-style patterns:**
  - `tests/test_hello_cli.py:9-30` uses a module-level expected constant (`GREETING`) and one test class per behaviour. It asserts exact `stdout`, `stderr == ""` and the exit code.
  - `tests/test_pdfutils.py:7` and `tests/test_pdf_extract_cli.py:10` locate files relative to the test with `pathlib.Path(__file__).parent`, which is the idiom for finding the repository root.
  - No existing test uses `subprocess`. The new test is the first to run an external process, using only the standard library (`subprocess`, `pathlib`, `os`).
- **Canonical gate:**
  - `.factory/testing.md:3` declares `test-gate: pytest`, with one required layer, `package-api` (`runBy: canonical-gate`, `.factory/testing.md:39-47`).
  - CI runs it in `.github/workflows/ci.yml:12-24`: the `test` job installs Python 3.12 on `ubuntu-latest`, runs `pip install -e ".[test]"`, then runs `pytest`.
  - The `gate` job (`.github/workflows/ci.yml:26-38`) fails only if a root `CI_FAIL` file exists. It is not a quality layer.
  - The repository has no linter, formatter or type checker (`.factory/testing.md:8-10`).
- **Repository layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:14-20`):
  - Rule 1: tests go under `tests/`.
  - Rule 2: a new shell script is executable and starts with a shebang.
  - Rule 3: no file is over 200 KB.
  - Rule 4: the PR adds a line under `## Unreleased` in `CHANGELOG.md`, creating the file if needed. Missing it is blocker `PLAY-G4`.
- **Contracts touched:**
  - The CLI contract in `hld.md` §5: stdout is exactly the bytes `hello world\n`, stderr is empty, exit status is 0, and it works from any current directory.
  - The file contract: the first line is `#!/bin/bash`, the git mode is `100755`, and `hello-world/` holds only `hello.sh`.
  - No API, schema, shared constant or other repository is involved. The script has no external data dependency.
- **Remaining unknowns:** none that block. The repository has no `AGENTS.md`, `CLAUDE.md` or `.factory/memory/`.

## Locked decisions and assumptions

**Locked decisions**
- The path is `hello-world/hello.sh` at the repository root, and the folder holds no other file (spec FR1, AC scenario 2).
- The first line is exactly `#!/bin/bash` and the file is executable (spec FR2, AC scenario 3, repo-gate rule 2).
- With no arguments, stdout is `hello world` ended by a single LF, stderr is empty and the exit code is 0 (spec FR3, §6 line-ending reading, AC scenarios 1 and 4).
- The script has no `--help`, no flags and no argument refusal. This is a recorded exception to the product memory `qa-script-standing-rule` (spec FR4, §6). No test asserts behaviour with arguments.
- The tests live in `tests/` and run under `pytest` (spec FR5, `.factory/testing.md`).
- `CHANGELOG.md` is created with `## Unreleased` and one line under it (spec FR6, repo-gate rule 4).
- The tests run the script directly as a subprocess, without a `bash` prefix, and locate it from the test file's path. The executable bit is carried in git, never set by `chmod` in the test (`hld.md` §6).
- `.github/workflows/ci.yml`, `pyproject.toml`, `src/` and `README.md` stay unchanged (spec non-goals, `hld.md` §2).
- All work is one work item, `t1` (`work-items.md`).

**Assumptions**
- *The folder-isolation test checks the on-disk listing of `hello-world/`.*
  - Evidence: AC scenario 2 says "when a developer lists its contents", and `hld.md` §7 asks the test to check the folder.
  - If wrong: a stray local `.DS_Store` fails the test on a developer Mac, though never in CI, whose checkout is fresh. The test then reports a real FR1 breach rather than being weakened.
- *`printf 'hello world\n'` or `echo hello world` produce identical bytes on bash 3.2 (macOS) and bash 5.x (ubuntu-latest).*
  - Evidence: `hld.md` §7. Neither form uses escapes or flags whose handling differs between shells.
  - If wrong: the byte-exact test fails loudly on the platform that differs.
- *Running from "any other directory" can be proven by running the subprocess with `cwd` set to a pytest `tmp_path`.*
  - Evidence: the `work-items.md` acceptance criterion and `hld.md` §5.
  - If wrong: no consequence. The script reads nothing relative to cwd.

## Solution proposal

**The script.** Add `hello-world/hello.sh` with LF line endings and the shebang `#!/bin/bash` on line 1. Its body is a single statement that writes `hello world` plus a newline to stdout; `printf 'hello world\n'` is preferred because its output is unambiguous across bash versions. There is no comment banner that could be mistaken for output, no argument parsing and no strict-mode boilerplate. Strict mode is allowed but adds nothing here. Commit the file with mode `100755`, using `chmod +x`, which `core.fileMode=true` records, and confirm with `git ls-files -s`. The script stays outside the Python package: it is not added to `[project.scripts]` and is not installed.

**The tests.** Add `tests/test_hello_sh.py` in the style of `tests/test_hello_cli.py`:
- Set module-level constants:
  - `REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent`
  - `SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"`
  - `EXPECTED_STDOUT = b"hello world\n"`
- Add a small helper that runs `subprocess.run([str(SCRIPT)], capture_output=True, cwd=...)`. The list holds the script path only, with no `bash` element and no `shell=True`. The helper returns the returncode and the stdout and stderr bytes.
- Group the tests into classes that mirror the acceptance criteria:
  - output and exit code (scenario 1)
  - folder isolation (scenario 2)
  - direct execution through the shebang (scenario 3)
  - output exactness (scenario 4)

Comparing raw bytes catches CR, BOM, whitespace and extra lines in a single assertion. A second assertion mimics `$(...)`, which strips only trailing newlines, and checks that the captured value equals `"hello world"`. That assertion states the user-facing contract.

**The changelog.** Create `CHANGELOG.md` with `## Unreleased` and one bullet describing the new script.

**Alternatives rejected:**
- *A `[project.scripts]` entry or a Python wrapper:* the spec asks for a bash script in its own folder.
- *Running the script as `bash hello.sh` in the tests:* this would not prove the shebang or the executable bit (scenario 3).
- *Calling `chmod` inside the test:* this would hide a lost mode.
- *Putting the tests inside `hello-world/`:* this breaks FR1 and repo-gate rule 1.
- *Adding a `.gitattributes` to force LF:* this is outside the change surface, and the byte-exact test already guards against CRLF.

## Ordered implementation steps

1. **Create `hello-world/hello.sh`** (new). Line 1 is exactly `#!/bin/bash`, the body prints `hello world` plus a newline, and the file uses LF endings with no other files in the folder. Make it executable so git records `100755`.
   - Advances: AC scenarios 1, 2, 3 and 4.
   - Test layer: `package-api` (`pytest`), through step 2.
   - Implicit invariants: there is no input, authorization, concurrency or state. The error path is "nothing can fail". No dependency to acquire, since `/bin/bash` ships on ubuntu-latest and macOS.
2. **Create `tests/test_hello_sh.py`** (new), using only the standard library. Cover these cases:
   - **Scenario 1:** running `SCRIPT` directly from `REPO_ROOT` exits with returncode 0, `stdout == EXPECTED_STDOUT` and `stderr == b""`.
   - **Scenario 1, any cwd:** the same three assertions with `cwd=tmp_path`.
   - **Scenario 2:** the names in `SCRIPT.parent` (via `os.listdir` or `iterdir`) equal exactly `["hello.sh"]`.
   - **Scenario 3:** the first line of `SCRIPT` read as bytes is exactly `b"#!/bin/bash\n"`, which also rules out CRLF. `os.access(SCRIPT, os.X_OK)` is true. The direct-exec run above succeeds, and the helper never prefixes `bash`.
   - **Scenario 4:** `stdout` decodes as ASCII. `stdout.decode().rstrip("\n") == "hello world"` mimics `$(...)`. `stdout.count(b"\n") == 1`, and stdout contains no `b"\r"`. These are redundant with the byte equality but each states one clause of the criterion.
   - Add no test that passes arguments (spec FR4).
   - Advances: AC scenarios 1, 2, 3 and 4.
   - Test layer: `package-api` (`pytest`), collected via `testpaths = ["tests"]` (`pyproject.toml:27`).
3. **Create `CHANGELOG.md`** (new) at the repository root with the heading `## Unreleased` and one line under it describing the addition of `hello-world/hello.sh`.
   - Advances: spec FR6, repo-gate rule 4.
   - Test layer: none in `pytest`. The layout gate (`repo-gate`, rule 4) checks it on the PR. This is a gate check, not a test layer.
4. **Run the gate once.** Run dev-toolkit's `run-tests-gate.sh --run` on the committed SHA, which runs `pytest` after `pip install -e ".[test]"`. Before that run, confirm `git ls-files -s hello-world/hello.sh` shows `100755`.
   - Advances: all ACs, through the `package-api` layer.

Generated deliverables: none. Binary assets: none, and nothing is declared in `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | `t1` | Add hello-world/hello.sh with pytest coverage and changelog line |
| 2 | `t1` | Add hello-world/hello.sh with pytest coverage and changelog line |
| 3 | `t1` | Add hello-world/hello.sh with pytest coverage and changelog line |
| 4 | `t1` | Add hello-world/hello.sh with pytest coverage and changelog line |

`t1` is the only work item, and every step belongs to it. No gap.

## Verification and CI gate

**Canonical gate.** The `test` job in `.github/workflows/ci.yml:12-24` runs on Python 3.12, `ubuntu-latest`:
1. `pip install -e ".[test]"`
2. `pytest` from the repository root

The `gate` job (`.github/workflows/ci.yml:26-38`) passes as long as no `CI_FAIL` file is added. Do not add one.

**Local run.** The only local run is the gate's own: `run-tests-gate.sh --run` on the committed SHA. Do not also run the canonical command by hand, run a narrower subset first, or set up a second worktree.

**Test layers.** The one required layer is `package-api` (`pytest`, `runBy: canonical-gate`). It runs unprivileged in a pod as long as the pod has `/bin/bash`. The subprocess tests need nothing else.

**Provider CI.** No CI configuration change is needed. The existing `pytest` step collects `tests/test_hello_sh.py`. The `.factory/testing.md` obligations are met with no edit to that file, and `.factory/delivery-assets` does not apply.

**Done when:**
- The provider `test` job is green at the exact head, with `tests/test_hello_sh.py` collected and passing next to the existing suite.
- The `gate` job is green.
- The layout gate reports `pass: true`: the script is executable with a shebang, the tests are in `tests/`, no file is over 200 KB, and `CHANGELOG.md` has its `## Unreleased` line.
- The diff contains exactly `hello-world/hello.sh` (mode `100755`), `tests/test_hello_sh.py` and `CHANGELOG.md`.

## Risks and scope guards

**Risks**
- *The executable bit is lost* (for example, a tool that writes files with `core.fileMode=false`). Direct execution then fails with permission denied. The `os.access` assertion and the direct-exec test fail loudly. Verify `100755` with `git ls-files -s` before the gate run.
- *CRLF line endings.* They break the shebang and the output. The byte-exact shebang and stdout assertions catch them. Write the file with LF.
- *A stray file in `hello-world/`* (`.DS_Store`, an editor backup, `__pycache__`). It breaks FR1 and the isolation test. Create nothing else there, and fix any failure by removing the stray file, never by loosening the assertion.
- *Bash differences between macOS 3.2 and Linux 5.x.* These are avoided by a literal `printf` with no flags.

**Scope guards: the implement phase must NOT:**
- add `--help`, flags, argument refusal, usage text or any output beyond `hello world` (spec FR4, a recorded exception to `qa-script-standing-rule`), or move the script under `qa/`;
- add any other file to `hello-world/` (no README, no tests, no `.gitkeep`);
- touch `.github/workflows/ci.yml`, `pyproject.toml`, `src/`, `README.md`, `.gitignore`, `.factory/` or any existing test, or add a `.gitattributes`;
- register the script in `[project.scripts]` or wrap it in Python;
- call `chmod` from a test, run the script through `bash` in a test, or skip, `xfail` or weaken any assertion to get green;
- add documentation beyond the single `CHANGELOG.md` line;
- create a `CI_FAIL` file.

A failing required check may be reported blocked. It is never made green by deleting, skipping, disabling or weakening it.

## Clarification outcomes

None. The intake settled the only open questions on 2026-11-25 (spec §6, §8): the location and the exception to the `qa/` rule, the trailing newline, and the `CHANGELOG.md` line. No new question was needed.
