# Work-item breakdown — 20261119-024045Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | SCRUM-27: confirm hello-world/hello.sh and record it in CHANGELOG.md |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "SCRUM-27: confirm hello-world/hello.sh and record it in CHANGELOG.md",
    "summary": "**Intent:** The hello-world script the story asks for already exists on `main` and meets every acceptance criterion. This PR keeps it exactly as it is, keeps the existing test passing, and adds the SCRUM-27 line to `CHANGELOG.md`, which the repository gate (PLAY-G4) requires of every PR.\n\n**Owns:** `CHANGELOG.md` (append one line under `## Unreleased`, after the existing entries).\n**Consumes (read-only, must NOT be modified):** `hello-world/hello.sh` (git mode 100755), `tests/test_hello_sh.py`, `.github/workflows/ci.yml`.\n\n**Acceptance criteria:**\n- `CHANGELOG.md` gets exactly one new line under `## Unreleased`, starting `- SCRUM-27:`, describing the `hello-world/hello.sh` script that prints `hello world`. The existing entries and the heading stay unchanged.\n- The diff touches no file other than `CHANGELOG.md`: `hello-world/hello.sh` stays byte-identical and keeps git mode 100755. No new script, folder, README or docs file is added. `.github/workflows/ci.yml` is unchanged.\n- `hello-world/` still contains only `hello.sh`.\n- Running `./hello-world/hello.sh` from the repo root (no `bash` prefix) prints exactly `hello world` plus one terminating newline, writes nothing to stderr and exits 0. This holds for Scenarios 1, 3 and 4 (the single newline is allowed per spec A2).\n- `pip install -e \".[test]\" && pytest` passes, including all 6 tests in `tests/test_hello_sh.py`. No `CI_FAIL` file exists at the repo root.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
