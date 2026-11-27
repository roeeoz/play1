# SMKL-1: Hello world bash script in a dedicated folder

The plan adds one file to play1: `hello-world/hello.sh`. It is an executable bash script that prints exactly `hello world`. Nothing else in the repository changes.

## 1. Your choice

None.

## 2. Decided differently from what was asked

None. The plan does what the story asks and nothing more. The same rule has a cost: the merge request will fail the repository's layout check. Sections 4 and 8 explain why.

## 3. What changes for people

- Developers get a new top-level folder, `hello-world/`, containing only `hello.sh`.
- Running `./hello-world/hello.sh` prints `hello world` and exits with code 0.
- The output has no trailing newline, so in a terminal the shell prompt appears on the same line, directly after `hello world`.
- Nothing changes for users, operators or admins of anything already in the repository.

## 4. Decisions and assumptions

**Decisions** (all made in planning; the developer has not ruled on any):

- **No newline after the output.** The script uses `printf 'hello world'`. Acceptance criterion 4 rules out trailing whitespace and extra lines, so the output is exactly those 11 bytes. Not chosen: `echo "hello world"`, which adds a newline. That reads more naturally in a terminal but breaks the criterion as written.
- **No changelog entry.** The story puts documentation files out of scope.
  - Not chosen: adding `CHANGELOG.md` with one line for SMKL-1 under `## Unreleased`.
  - The repository's layout check requires that entry, so the merge request will fail it (see Risks).
  - If you want the check to pass, approve the changelog line. It sits outside `hello-world/`, so the "only `hello.sh` in the folder" criterion still holds.
- **No automated test.** The story puts additional scripts and CI/CD integration out of scope. Each acceptance criterion is checked by hand before commit instead.
  - Not chosen: a pytest module that would run the script on every merge request.
  - Consequence: nothing in CI catches a later change that breaks the script.
- **Folder at the repository root,** named `hello-world` as the story says.

**Assumptions:**

- *Checked in the code:* the repository has no `hello-world/` folder and no existing shell scripts or `CHANGELOG.md`, so nothing clashes.
- *Checked in the code:* git in this repository records file permissions, so the executable bit is committed with the file.
- *Checked in the code:* the existing CI runs Python tests only. This change touches no Python, so their result stays as it was.
- *Not checked:* that `/bin/bash` exists wherever developers run the script. The story requires this shebang, and macOS and common Linux distributions provide it. Where it is missing, the script fails to start with "bad interpreter".

## 5. Removed or switched off

Nothing.

## 6. Data, security and privacy

- The script reads no input, stores no data, opens no network connection and has no dependencies.
- The change adds no secrets and no permissions.

## 7. Between repositories

Not applicable: only play1 changes, and nothing has to land first.

## 8. Risks, and what was not tried

- **The layout check will block the merge request** as planned. The repository's own layout check (the `repo-gate` skill under `.factory/plugins/claims-dev`, rule 4) raises blocker `PLAY-G4` on any merge request that doesn't touch `CHANGELOG.md`. Approving the one-line changelog entry from section 4 clears it.
- **No regression guard.** Because there is no automated test, a later edit could break the script's exact output without CI noticing.
- **Not tried:** running the script on Windows, or anywhere without bash.

## 9. Done when

| Check | Expected |
|---|---|
| `./hello-world/hello.sh` (run without `bash` in front) | prints `hello world`, exit code 0 |
| Output captured byte by byte | exactly `hello world`, 11 bytes, no newline |
| `ls -A hello-world` | `hello.sh` only |
| First line of `hello.sh` | `#!/bin/bash` |
| File mode as recorded in git | `100755` (executable) |
| Existing CI `pytest` job | still passes |
