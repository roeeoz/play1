# Work-item breakdown — QA-20261122-S2 Add a hello helper in qa/s2_hello.py

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/s2-hello.sh greeting script and its qa/s2-hello-test.sh test |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add qa/s2-hello.sh greeting script and its qa/s2-hello-test.sh test",
    "summary": "**Intent:** Deliver the whole PLAY-190 capability in one PR: a bash script that greets a name and rejects the empty string, plus a bash test script that proves both acceptance cases. The spec replaces the ticket title's Python module `qa/s2_hello.py` with bash, because of repo-gate rule 1.\n\n**Owns (creates):** `qa/s2-hello.sh`, `qa/s2-hello-test.sh`. **Consumes (reads only, as a pattern):** `qa/20261110-s3/test_hello.sh`, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`. **Must not change:** any existing file, including `src/`, `tests/`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/` and the existing `qa/` files.\n\n**Acceptance criteria:**\n- The diff adds exactly two files, `qa/s2-hello.sh` and `qa/s2-hello-test.sh`, both committed executable (git mode 100755), each with the first line `#!/usr/bin/env bash` (repo-gate rule 2).\n- `qa/s2-hello.sh Ada` prints exactly `Hello, Ada!` followed by one newline to stdout, prints nothing to stderr, and exits 0.\n- `qa/s2-hello.sh ''` prints `name must not be empty` (one line) to stderr, prints nothing to stdout, and exits 1.\n- Only the exact empty string counts as empty: `qa/s2-hello.sh '   '` prints `Hello,    !` and exits 0.\n- The name is printed literally: `qa/s2-hello.sh -n` prints `Hello, -n!` and `qa/s2-hello.sh '%s'` prints `Hello, %s!`.\n- With no argument the script behaves like the empty name (stderr message, exit 1); extra arguments after the first are ignored.\n- `bash -n qa/s2-hello.sh qa/s2-hello-test.sh` (syntax check) exits 0 with no output, and is run before `qa/s2-hello-test.sh`.\n- `qa/s2-hello-test.sh` runs `qa/s2-hello.sh` for `Ada` and for `''`, checks stdout (exact bytes, including the single trailing newline), stderr and exit code for each, and exits 0 only when both pass; otherwise it exits non-zero with a `FAIL:` line on stderr naming the failing case.\n- `qa/s2-hello-test.sh` finds the target relative to its own location, so it passes when run from the repo root and from another directory.\n- Breaking the greeting (e.g. a changed message or exit code) makes `qa/s2-hello-test.sh` exit non-zero.\n- `pytest` (the repo's CI gate, `.factory/testing.md`) still passes unchanged; the PR description quotes the output and exit codes of `qa/s2-hello-test.sh`, `qa/s2-hello.sh Ada` and `qa/s2-hello.sh ''` as evidence, since CI does not run the bash test.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
