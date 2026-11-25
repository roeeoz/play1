# SMKL-2 — Hello world bash script in a dedicated folder

One repository changes: `play1`, on branch `halo/feat/smkl-2-20261125-120917`, merging into
`bench/two-lines/smoke`. Size XS.

## Developer's answers (settled — no open questions)

The developer answered the first plan's questions: "keep exactly to the story. The script lives
at hello-world/hello.sh, takes no flags beyond what the story names, and the tests go where the
repository's existing tests live. Anything else: your call, simplest reading." Applied as:

1. **No `CHANGELOG.md`.** The story puts documentation files out of scope and the developer said
   to keep exactly to the story, so the build does **not** create or edit `CHANGELOG.md`.
   Known consequence: the repo's merge-request layout gate
   (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 4) requires a line under
   `## Unreleased` in `CHANGELOG.md` and will report blocker `PLAY-G4` on this PR. That is
   expected and accepted. The build must not "fix" it by adding the file. Whoever merges decides
   whether to add the entry.
2. **Tests go in `tests/`**, where the existing pytest suite lives: one file,
   `tests/test_hello_world_script.py`. No change to `.github/workflows/ci.yml`. The existing
   `pytest` job picks the file up.
3. **One trailing newline (simplest reading).** The script uses `echo`, so stdout is the greeting
   followed by one `\n`: one line, terminated as every line is, with no spaces before or after
   the text. The greeting itself was changed later. See "Requirement change" below for the exact
   text and bytes.
4. **No flags or arguments.** The script ignores arguments. No option parsing, no `set -euo`
   boilerplate.

## Requirement change from the developer (overrides AC1 and AC4 text)

After the plan was approved, the developer changed one requirement: "the default greeting must end
with two exclamation marks, exactly `Hello, World!!`. Everything else stays as approved."

- The script's output is now exactly `Hello, World!!`, not the story's lowercase `hello world`.
  Wherever AC1 and AC4 say "hello world", read `Hello, World!!`: capital H, comma, one space,
  capital W, two `!`. Everything else in those criteria still holds: exit code 0, exactly one line,
  no spaces before or after the text, and one trailing `\n` as in answer 3. stdout is exactly the
  15 bytes `Hello, World!!\n`.
- **Which greeting.** This story ships only `hello-world/hello.sh`, so the change applies to that
  script. The repo also has a Python console script, `testbed-hello` (`src/testbed_utils/hello.py`),
  which returns `"Hello, world!"`. It is outside this story and the build does **not** change it,
  or `tests/test_hello.py` / `tests/test_hello_cli.py`.
- **Quoting.** Use single quotes: `echo 'Hello, World!!'`. `!!` is bash history expansion.
  History expansion is off in non-interactive scripts, so double quotes would work too, but single
  quotes make the literal safe if someone pastes the line into an interactive shell. This was
  checked on this machine: `od -c` shows `H e l l o ,   W o r l d ! ! \n` and the exit code is 0.
- The published story in Jira (SMKL-2) still says `hello world`. This plan does not change the
  ticket. Updating its acceptance criteria is up to the developer or PO.

## Done when (observable checks)

Run these from the repo root of the work branch:

- `ls -A hello-world` prints only `hello.sh` (AC2).
- `head -1 hello-world/hello.sh` is exactly `#!/bin/bash` (AC3).
- `git ls-files -s hello-world/hello.sh` shows mode `100755`, so the executable bit is recorded
  in git and not only on disk (AC3).
- `./hello-world/hello.sh` prints `Hello, World!!`, and `echo $?` gives `0`. The script runs
  directly, without `bash hello.sh` (AC1, AC3).
- `./hello-world/hello.sh | od -c` shows exactly `H e l l o ,   W o r l d ! ! \n`, and stderr is
  empty (AC4, as changed).
- `pytest` passes, including the new `tests/test_hello_world_script.py`.
- The diff against `bench/two-lines/smoke` contains exactly two files:
  `hello-world/hello.sh` and `tests/test_hello_world_script.py`.

## Changes in `play1`

1. **`hello-world/hello.sh`** (new, mode 755). Exact content:

   ```bash
   #!/bin/bash
   echo 'Hello, World!!'
   ```

   Nothing else goes in the folder: no README, no `.gitkeep`.
   Set the executable bit so that git records it. This checkout has `core.fileMode=true`, so run
   `chmod +x hello-world/hello.sh` before `git add`. Then check `git ls-files -s`. If it shows
   `100644`, run `git update-index --chmod=+x hello-world/hello.sh`.

2. **`tests/test_hello_world_script.py`** (new). Plain pytest that matches the style of
   `tests/test_hello_cli.py`: a module-level constant for the expected output
   (`EXPECTED = "Hello, World!!\n"`) and small test functions. Find the script relative to the test
   file with `Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"`, so the tests
   don't depend on the cwd. Use only the stdlib (`os`, `subprocess`, `pathlib`) and add no
   dependencies. Tests:
   - Run `subprocess.run([str(SCRIPT)], capture_output=True, text=True)`. This invokes the script
     directly, with no `bash` prefix. Assert `returncode == 0`, `stdout == EXPECTED` and
     `stderr == ""` (AC1, AC3, AC4).
   - The first line of the file is `#!/bin/bash` (AC3).
   - `os.access(SCRIPT, os.X_OK)` is true (AC3).
   - `sorted(os.listdir(SCRIPT.parent)) == ["hello.sh"]` (AC2).

   CI runs on `ubuntu-latest`, which has `/bin/bash`, and `actions/checkout` preserves git's
   executable bit.

The build does not touch `CHANGELOG.md`, `.github/workflows/ci.yml`, `README.md`,
`pyproject.toml`, `src/`, or any other file. No other repository is involved. This change exposes
nothing to another repository and needs nothing from one.

## Decisions and assumptions

- The folder sits at the repo root (`hello-world/`), because AC1 runs `./hello-world/hello.sh`
  from the root.
- The script uses `echo` rather than `printf`. It is the simplest form, and with a fixed
  single-quoted literal it is unambiguous.
- Rule 2 of the repo gate (a new shell script must be executable and have a shebang) is met by
  change 1. Rules 1 and 3 are met trivially. Rule 4 is not met, by decision (see answer 1).

## Why the tests sit where they do, and what breaks them

**Place.** The tests go in `tests/`, as the developer asked. That is also the only path the
repo's gate runs: `pyproject.toml` sets `testpaths = ["tests"]`, and the `test` job in
`.github/workflows/ci.yml` runs `pytest` on every pull request (see `.factory/testing.md`). Any
other location would either not run or would need a CI change, and the story rules CI changes
out.

**Layer.** These are black-box process tests. They run the real file the way a developer runs it
(`./hello-world/hello.sh` with no `bash` prefix) and look at stdout, stderr and the exit code. The
script is not part of the installed `testbed_utils` package, so the tests read it from the
checkout through `__file__`. That checkout file is the thing the story ships. Reading the file's
text or mocking the shell would not test AC1/AC3: only a real exec proves that the shebang and the
executable bit work.

**What would break them**, beyond a real regression in the script:
- **Executable bit lost.** If the file is committed as `100644`, or checked out with
  `core.fileMode=false`, or extracted from an archive that drops modes, the `os.access` check
  fails and `subprocess.run` raises `PermissionError`. This is the main reason the build checks
  `git ls-files -s` for `100755`.
- **CRLF line endings.** A Windows checkout with `core.autocrlf=true` turns the shebang into
  `#!/bin/bash\r`, and exec fails with "bad interpreter". The repo has no `.gitattributes`, and
  the build adds none (out of scope).
- **No `/bin/bash`.** Windows without WSL, or a minimal container such as Alpine without bash,
  cannot run the script. CI's `ubuntu-latest` and macOS both have `/bin/bash`; the macOS one
  (3.2) was checked.
- **Stray files in `hello-world/`.** The folder-isolation test is strict on purpose (AC2), so a
  Finder `.DS_Store`, an editor swap file or any other file in that folder fails it locally. CI
  gets a clean checkout and is not affected. Nothing writes there at test time: Python is never
  imported from it, so no `__pycache__` appears.
- **Moving or renaming the folder or script.** The tests use a fixed path relative to `tests/`.
- **A `noexec` mount** of the checkout also blocks direct execution.

Changing the working directory does not break them, because the path is resolved from `__file__`.
Neither does whether the package is installed, because the tests import nothing from `src/`.

## Verification (the build runs these before finishing)

```sh
ls -A hello-world                       # -> hello.sh
head -1 hello-world/hello.sh            # -> #!/bin/bash
git ls-files -s hello-world/hello.sh    # -> 100755 ...
./hello-world/hello.sh; echo "exit=$?"  # -> Hello, World!! / exit=0
./hello-world/hello.sh | od -c          # -> H e l l o ,   W o r l d ! ! \n
pip install -e ".[test]" && pytest      # all green, new tests included
git diff --stat bench/two-lines/smoke...HEAD -- . ':!stories'   # -> only the two files above
```

Security checklist (lean line): no secrets, no ID numbers, no SQL, no network access, no new
dependencies.
