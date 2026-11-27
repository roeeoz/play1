# SMKL-2: Hello world bash script in a dedicated folder

## Your choice: add a `CHANGELOG.md` or not

The story rules out documentation files. The repo's own merge request check, though, fails any pull request that doesn't add a line to `CHANGELOG.md`. That file doesn't exist yet.

- **Approve as written:** the build adds a root-level `CHANGELOG.md` with one line for SMKL-2, and the merge request can pass the check. `hello-world/` still holds only `hello.sh`.
- **Strike the changelog:** the change is exactly what the story says, but the check fails and the merge request stays blocked until either the check or the story changes.

## 1. Decided differently from what was asked

- **Story: "Out of scope: documentation files."** The plan adds `CHANGELOG.md` at the repo root because the repo's merge request check requires it. Approving the plan as written accepts this exception. See the choice above.
- No rulings from the developer yet.

## 2. What changes for people

- Developers get a new folder, `hello-world/`, containing only `hello.sh`. Running `./hello-world/hello.sh` prints `hello world` and exits with code 0.
- The output has no trailing newline, so in a terminal the shell prompt appears right after `hello world` on the same line.
- Under the default choice, the repo also gets a `CHANGELOG.md` with an `## Unreleased` section and one line for this change.

## 3. Decisions and assumptions

**Decisions**
- **`printf 'hello world'`, not `echo`.** The story asks for exactly "hello world" with no trailing whitespace. A newline is whitespace, and `echo` adds one. `printf` writes exactly those 11 bytes, which meets the story however strictly it's read. Not chosen: `echo`, the usual terminal behaviour, which leaves a trailing newline. If you prefer `echo`, say so at approval.
- **No automated test.** The criteria are checked by hand with shell commands during the build. Not chosen: a pytest test. It would run in CI, and the story rules out CI work.
- **The changelog goes at the repo root, not in `hello-world/`**, so the folder keeps only `hello.sh`.

**Assumptions**
- Checked in the code: the merge request check applies to every pull request. A missing changelog line is a blocker, and any blocker fails the check.
- Checked in the code: no `hello-world/` folder and no `CHANGELOG.md` exist yet, so nothing is overwritten.
- Checked in the code: CI runs only the Python tests and a marker-file check, so a shell script doesn't affect it.
- Not checked: the platform enforces the check's failure, rather than only reporting it. If it only reports, the changelog isn't needed to merge, and striking it costs nothing.
- Not checked: every developer machine has `/bin/bash`. On a system without it, the script won't run directly.

## 4. Removed or switched off

Nothing.

## 5. Data, security and privacy

No data is stored or read, nothing is sent over the network, and nothing can be called from outside. The script only prints a fixed string. No secrets and no dependencies are involved.

## 6. Between repositories

None. Only `play1` changes, and nothing has to land first.

## 7. Risks, and what was not tried

- If the executable bit isn't recorded in git, a fresh clone gets a script that can't run directly. The build confirms git stores the file as executable.
- Not tried: running the script on Windows.

## 8. Done when

| Check | Expected |
|---|---|
| `./hello-world/hello.sh` | Prints `hello world` and exits with code 0 |
| Output bytes, compared exactly | Exactly `hello world`: 11 bytes, no newline, no surrounding spaces |
| Contents of `hello-world/`, including hidden files | Only `hello.sh` |
| First line of `hello.sh` | `#!/bin/bash` |
| Git file mode of `hello.sh` | Executable (`100755`) |
| Files changed against `bench/two-lines/smoke` | `hello-world/hello.sh`, plus `CHANGELOG.md` unless struck |
| Existing `pytest` suite | Still passes |
