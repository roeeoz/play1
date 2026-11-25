# SMKL-2 — Hello world bash script in a dedicated folder

One repository changes: `play1`, on branch `halo/feat/smkl-2-20261125-120917`, merging into
`bench/two-lines/smoke`. Size XS.

## Questions for the approver (answer before approving, or accept the defaults)

1. **CHANGELOG.md entry (default: add it).** The repo's merge-request gate
   (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 4) blocks any PR whose diff
   does not add a line under `## Unreleased` in `CHANGELOG.md` (blocker `PLAY-G4`). No
   `CHANGELOG.md` exists yet, so the build creates it with that heading and one line. The story
   lists "documentation files" as out of scope; I read that as "no README/docs inside or about the
   script", and the changelog as a repo-process requirement outside `hello-world/`, so folder
   isolation (AC2) is unaffected. Say so if you want it left out — the gate will then block the PR.
2. **pytest test for the script (default: add it).** The story excludes CI/CD integration; I do
   not touch `.github/workflows/ci.yml`. But the repo's only gate is `pytest` over `tests/`
   (`.factory/testing.md`), so one test file `tests/test_hello_world_script.py` makes the
   acceptance criteria checked on every PR by the existing job. It lives in `tests/`, not in
   `hello-world/`. Say so if you want no test file.
3. **Trailing newline (default: one newline).** AC4 says "no leading or trailing whitespace and
   no additional lines". The script prints `hello world` followed by a single `\n` (one terminated
   line, as `echo` does — without it the shell prompt lands on the same line). Stdout is exactly
   the 12 bytes `hello world\n`. If "no trailing whitespace" is meant byte-for-byte (11 bytes, no
   newline), say so and the script uses `printf 'hello world'` instead.

## Done when (observable checks)

From the repo root of the merged branch:

- `ls -A hello-world` prints only `hello.sh` (AC2).
- `head -1 hello-world/hello.sh` is exactly `#!/bin/bash` (AC3).
- `git ls-files -s hello-world/hello.sh` shows mode `100755` — the executable bit is in git, not
  only on the local disk (AC3).
- `./hello-world/hello.sh` prints `hello world` and `echo $?` gives `0` (AC1, AC3 — run directly,
  not via `bash hello.sh`).
- `./hello-world/hello.sh | od -c` shows exactly `h e l l o   w o r l d \n` — lowercase, no
  leading/trailing spaces, one line, nothing on stderr (AC4; see question 3).
- `pytest` passes, including the new `tests/test_hello_world_script.py`.
- `CHANGELOG.md` exists with `## Unreleased` and a line describing this change (question 1).

## Changes in `play1`

1. **`hello-world/hello.sh`** (new, mode 755). Exact content:

   ```bash
   #!/bin/bash
   echo "hello world"
   ```

   Nothing else in the folder — no README, no `.gitkeep`.
   Set the executable bit so git records it: `chmod +x hello-world/hello.sh` before `git add`
   (this checkout has `core.fileMode=true`), then confirm with `git ls-files -s` (mode
   `100755`); if it shows `100644`, run `git update-index --chmod=+x hello-world/hello.sh`.

2. **`tests/test_hello_world_script.py`** (new). Plain pytest, matching `tests/test_hello_cli.py`
   style (module-level constant for the expected output, small test functions/classes). Locate the
   script relative to the test file (`Path(__file__).resolve().parent.parent / "hello-world" /
   "hello.sh"`) so it does not depend on the cwd. Tests:
   - runs `subprocess.run([str(script)], capture_output=True, text=True)` — invoked directly, no
     `bash` prefix — and asserts `returncode == 0`, `stdout == "hello world\n"`, `stderr == ""`
     (AC1, AC3, AC4);
   - first line of the file is `#!/bin/bash` (AC3);
   - `os.access(script, os.X_OK)` is true (AC3);
   - the `hello-world` directory's entries are exactly `["hello.sh"]` (AC2).
   No new dependencies (stdlib only). CI runs on `ubuntu-latest`, where `/bin/bash` exists and
   `actions/checkout` preserves the git executable bit.

3. **`CHANGELOG.md`** (new, repo root):

   ```markdown
   # Changelog

   ## Unreleased

   - SMKL-2: add `hello-world/hello.sh`, a minimal hello-world bash script.
   ```

Not touched: `.github/workflows/ci.yml`, `README.md`, `pyproject.toml`, `src/`. No other repo is
involved; nothing is exposed to or needed from another repository.

## Decisions and assumptions

- Folder at the repo root (`hello-world/`), since AC1 runs `./hello-world/hello.sh` from the root.
- `echo` over `printf`: simplest form, and bash's builtin `echo` with a fixed literal has no
  portability issue here.
- No `set -euo pipefail` or other boilerplate: the story asks for a minimal script, and the extra
  lines add nothing to a single `echo`.
- The repo-gate's rule 2 (new shell script is executable and has a shebang) is satisfied by
  change 1.

## Verification (the build runs these before finishing)

```sh
ls -A hello-world                       # -> hello.sh
head -1 hello-world/hello.sh            # -> #!/bin/bash
git ls-files -s hello-world/hello.sh    # -> 100755 ...
./hello-world/hello.sh; echo "exit=$?"  # -> hello world / exit=0
./hello-world/hello.sh | od -c          # -> h e l l o   w o r l d \n
pip install -e ".[test]" && pytest      # all green, new tests included
```

Security checklist (lean line): no secrets, no IDs, no SQL, no network, no new dependencies.
