# SMKL-1 — Hello world bash script in a dedicated folder

## Context

SMKL-1 is the epic's only story. It asks for a minimal, runnable bash starting point:
- a new top-level folder `hello-world/` containing exactly one file, `hello.sh`;
- the script starts with a `#!/bin/bash` shebang and is executable;
- it prints exactly `hello world` and exits 0.

AC4 says the captured output must be exactly that lowercase string, with no leading or
trailing whitespace and no extra lines. So the script prints **no trailing newline**.

The story puts these out of scope: additional scripts, CI/CD integration and
documentation files. The delivery is therefore the single script and nothing else.

Repo facts (play1, branch `halo/feat/smkl-1-20261127-213539`, cut from `bench/two-lines/smoke`):
- The repo has no shell scripts and no `CHANGELOG.md`.
- The CI gate is `pytest` (see `.github/workflows/ci.yml` and `.factory/testing.md`).
  This change touches no Python, so the gate's result does not change.
- `git config core.fileMode` is `true`, so git records the executable bit as mode `100755`.
- The repo's layout gate is `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`. Two of
  its rules apply here (both verified in the file):
  - **Rule 2:** a new shell script must be executable and start with a shebang. This
    change satisfies it.
  - **Rule 4:** "A pull request whose diff does not touch `CHANGELOG.md` breaks this rule:
    one `blocker` with id `PLAY-G4`". The story excludes documentation files, so this plan
    adds no changelog. See the approver note below.

## Change

**`hello-world/hello.sh`** (new, mode 100755). The file contains exactly these two lines:
```bash
#!/bin/bash
printf 'hello world'
```
- Use `printf` instead of `echo` so that standard output is exactly the 11 bytes
  `hello world`, with no newline (AC1, AC4).
- Make the file executable with `chmod +x hello-world/hello.sh`.
- Confirm that `git ls-files -s hello-world/hello.sh` shows mode `100755`. If it does not,
  run `git update-index --chmod=+x hello-world/hello.sh` (AC3).
- Add no other file to `hello-world/`: no README and no `.gitkeep` (AC2).
- Change no other file in the repo: no test module, no CI change and no changelog.

> **Decision for the approver: the repo layout gate's changelog rule.** As planned, this
> merge request does not touch `CHANGELOG.md`. The layout gate's rule 4 will therefore
> report blocker `PLAY-G4`, and the gate will fail the merge request.
>
> The story lists documentation files as out of scope, so the plan follows the story. If
> you want the gate to pass, approve adding `CHANGELOG.md` at the repo root. It would
> contain only `## Unreleased` and the line
> `- Add hello-world/hello.sh, a minimal hello world bash script (SMKL-1).`
> The file sits outside `hello-world/`, so AC2 still holds.

## Verification

Run these by hand from the repo root of the checkout:
```bash
./hello-world/hello.sh; echo; echo "exit=$?"   # prints: hello world / exit=0  (no bash prefix: AC1, AC3)
./hello-world/hello.sh | od -c                 # exactly: h e l l o   w o r l d  — no \n (AC4)
[ "$(./hello-world/hello.sh | wc -c)" -eq 11 ] && echo ok   # byte-exact length
ls -A hello-world                              # hello.sh only (AC2)
head -1 hello-world/hello.sh                   # #!/bin/bash (AC3)
git ls-files -s hello-world/hello.sh           # mode 100755 (AC3)
pip install -e ".[test]" && pytest             # existing gate stays green
```
Before committing, check the diff against `harel-dev:security-checklist`. Expect it to be
clean: the diff contains no secrets, no outbound hosts and no dependencies.

Commit on the work branch with a message that references SMKL-1. The platform pushes the
branch and opens the merge request.
