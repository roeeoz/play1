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
3. **One trailing newline (simplest reading).** The script is `echo "hello world"`, so stdout is
   exactly the 12 bytes `hello world\n`: one line, terminated as every line is, with no spaces
   before or after the text. This was checked on this machine: `od -c` shows
   `h e l l o   w o r l d \n` and the exit code is 0.
4. **No flags or arguments.** The script ignores arguments. No option parsing, no `set -euo`
   boilerplate.

## Done when (observable checks)

Run these from the repo root of the work branch:

- `ls -A hello-world` prints only `hello.sh` (AC2).
- `head -1 hello-world/hello.sh` is exactly `#!/bin/bash` (AC3).
- `git ls-files -s hello-world/hello.sh` shows mode `100755`, so the executable bit is recorded
  in git and not only on disk (AC3).
- `./hello-world/hello.sh` prints `hello world`, and `echo $?` gives `0`. The script runs
  directly, without `bash hello.sh` (AC1, AC3).
- `./hello-world/hello.sh | od -c` shows exactly `h e l l o   w o r l d \n`, and stderr is empty
  (AC4).
- `pytest` passes, including the new `tests/test_hello_world_script.py`.
- The diff against `bench/two-lines/smoke` contains exactly two files:
  `hello-world/hello.sh` and `tests/test_hello_world_script.py`.

## Changes in `play1`

1. **`hello-world/hello.sh`** (new, mode 755). Exact content:

   ```bash
   #!/bin/bash
   echo "hello world"
   ```

   Nothing else goes in the folder: no README, no `.gitkeep`.
   Set the executable bit so that git records it. This checkout has `core.fileMode=true`, so run
   `chmod +x hello-world/hello.sh` before `git add`. Then check `git ls-files -s`. If it shows
   `100644`, run `git update-index --chmod=+x hello-world/hello.sh`.

2. **`tests/test_hello_world_script.py`** (new). Plain pytest that matches the style of
   `tests/test_hello_cli.py`: a module-level constant for the expected output
   (`EXPECTED = "hello world\n"`) and small test functions. Find the script relative to the test
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
- The script uses `echo` rather than `printf`. It is the simplest form, and with a fixed literal
  it is unambiguous.
- Rule 2 of the repo gate (a new shell script must be executable and have a shebang) is met by
  change 1. Rules 1 and 3 are met trivially. Rule 4 is not met, by decision (see answer 1).

## Verification (the build runs these before finishing)

```sh
ls -A hello-world                       # -> hello.sh
head -1 hello-world/hello.sh            # -> #!/bin/bash
git ls-files -s hello-world/hello.sh    # -> 100755 ...
./hello-world/hello.sh; echo "exit=$?"  # -> hello world / exit=0
./hello-world/hello.sh | od -c          # -> h e l l o   w o r l d \n
pip install -e ".[test]" && pytest      # all green, new tests included
git diff --stat bench/two-lines/smoke...HEAD -- . ':!stories'   # -> only the two files above
```

Security checklist (lean line): no secrets, no ID numbers, no SQL, no network access, no new
dependencies.
