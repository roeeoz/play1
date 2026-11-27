# SMKL-2 — Hello world bash script in a dedicated folder

## Context
Developers want a minimal runnable shell script as a starting point, in its own
folder so nothing existing gets cluttered. The new folder is `hello-world/` and
holds only `hello.sh`. The script has a `#!/bin/bash` shebang, is executable, and
prints exactly `hello world`. Out of scope: other scripts, CI/CD changes,
documentation files.

Repo findings (play1, branch `halo/feat/smkl-2-20261127-180526`, cut from
`bench/two-lines/smoke`):
- There is no `hello-world/` folder yet, and no AGENTS.md, CLAUDE.md or `.factory/memory/`.
- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` is the repo's merge
  request gate. Its frontmatter registers it in the `mr-gate` slot. It applies to
  every pull request ("Check the pull request's diff against these rules"):
  - **Rule 2** (lines 14–15): a new shell script must be executable and start
    with a shebang. This story's script meets it.
  - **Rule 4** (lines 17–20): the pull request has to add a line under
    `## Unreleased` in `CHANGELOG.md`. The rule tells the pull request's author
    to create that file, with that heading, if it is missing; the gate itself
    never creates it ("Do not change any file", line 29). If the diff leaves
    `CHANGELOG.md` untouched, the gate raises a finding with severity `blocker`
    and id `PLAY-G4`. Line 29 says `pass` is false whenever any blocker exists,
    so `PLAY-G4` blocks the merge request outright; it is not advisory.
    `CHANGELOG.md` does not exist in the repo yet.
- CI (`.github/workflows/ci.yml`) runs `pytest` plus a `CI_FAIL` marker check.
  Neither is affected by this change.

## Decision for the developer at approval: `CHANGELOG.md`
The story puts documentation files out of scope. The repo gate's rule 4 blocks
any pull request that doesn't touch `CHANGELOG.md`. Both can't hold, so the
developer chooses when approving:
- **A: approve the plan as written (step 2 included).** Add a root-level
  `CHANGELOG.md` holding only the one entry this rule needs. `hello-world/` still
  holds only `hello.sh`, so AC2 holds. Approving the plan as written counts as
  accepting this one exception to the story's scope.
- **B: strike step 2.** The change is only `hello-world/hello.sh`, as the story
  says. The repo gate then fails with `PLAY-G4`, the merge request stays blocked,
  and the story can't merge until the gate or the story changes.

## Changes
1. **Create `hello-world/hello.sh`** with exactly these two lines:
   ```bash
   #!/bin/bash
   printf 'hello world'
   ```
   - The output bytes are exactly `hello world`: no leading or trailing
     whitespace, no newline, and no further lines. That meets AC4 even when the
     output is compared byte for byte, and AC1 ("prints exactly") under any
     reading. `echo` would add a trailing `\n`, and a newline is whitespace, so
     `printf` is used. The visible side effect is that the shell prompt follows
     straight after the text on the same line when the script runs in a terminal.
   - Set the executable bit with `chmod +x hello-world/hello.sh`. Confirm git
     records it as `100755` (`git ls-files -s hello-world/hello.sh`). If it
     doesn't, run `git update-index --chmod=+x hello-world/hello.sh`.
   - Add nothing else to `hello-world/`: no README and no `.gitkeep` (AC2).
2. **Create `CHANGELOG.md`** at the repo root. Do this only under decision A above:
   ```markdown
   # Changelog

   ## Unreleased

   - SMKL-2: add `hello-world/hello.sh`, a hello-world bash script in its own folder.
   ```

No other files change. There is no pytest test, so CI stays as it is (CI/CD is out of scope).

## Verification (run from the repo root)
- AC1 and AC3: `./hello-world/hello.sh; s=$?; echo; echo "exit=$s"` prints
  `hello world`, then `exit=0`. The script runs directly, through its shebang. The
  bare `echo` only adds a line break after the output.
- AC4: `[ "$(./hello-world/hello.sh | od -c)" = "$(printf 'hello world' | od -c)" ]`
  succeeds, which proves the output is exactly those 11 bytes.
  `./hello-world/hello.sh | wc -c` prints `11`.
- AC2: `ls -A hello-world` lists only `hello.sh`, and `git ls-files hello-world`
  lists only `hello-world/hello.sh`.
- Shebang and mode: `head -1 hello-world/hello.sh` prints `#!/bin/bash`, and
  `git ls-files -s hello-world/hello.sh` shows `100755`.
- Scope: `git diff --stat bench/two-lines/smoke...HEAD` lists exactly
  `hello-world/hello.sh`, plus `CHANGELOG.md` under decision A.
- Regression: `pip install -e ".[test]" && pytest` still passes. Nothing Python changed.

Commit in one commit on the work branch, with a message that starts with
`SMKL-2:`. The platform pushes the branch and opens the merge request.
