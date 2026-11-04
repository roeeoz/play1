# Work-item breakdown — 20261031-145900Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add hello-world/hello.sh executable bash script with subprocess acceptance test |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "6334bfc5-8cee-4bf0-a5f8-07de553c1efa",
    "title": "Add hello-world/hello.sh executable bash script with subprocess acceptance test",
    "summary": "**Intent:** deliver the story's only product addition: a directly executable bash script `hello-world/hello.sh` that prints exactly `hello world`. Add a pytest check, outside the folder, that verifies it in the existing CI test job. play1 is the only target repo and owns the whole change.\n\n**Owns:** `hello-world/hello.sh` (new, git mode 100755) and `tests/test_hello_sh.py` (new).\n\n**Consumes, read-only:** the existing pytest configuration in `pyproject.toml` and the CI `test` job in `.github/workflows/ci.yml`. Neither is modified.\n\n**Must not touch:** `src/` (including the Python hello module and the `testbed-hello` command), `tests/test_hello.py`, `tests/test_hello_cli.py`, `pyproject.toml`, `.github/`, `README`, `.gitignore`, and any `.gitattributes`.\n\n**Conditional:** if the owner resolves the open P0 by letting the repo-gate win, this ticket also creates and owns `CHANGELOG.md` with a `## Unreleased` section containing one entry for the new script. Otherwise no `CHANGELOG.md` is created.\n\n**Acceptance criteria:**\n- A top-level folder `hello-world/` exists. It contains exactly one entry, `hello.sh`, and no hidden files.\n- The first line of `hello-world/hello.sh` is exactly `#!/bin/bash`.\n- `git ls-files -s hello-world/hello.sh` reports mode `100755`, so the file is executable in a fresh clone.\n- Running `./hello-world/hello.sh` from the repo root without typing `bash` writes exactly the bytes `hello world\\n` to stdout, writes nothing to stderr, and exits 0. Exactly means:\n  - lowercase, one space between the words, no punctuation;\n  - no leading or trailing spaces or tabs;\n  - a single LF, with no CR and no second line.\n- Running the script by absolute path from a different working directory (for example a temp dir) gives identical stdout and exit code 0. Repeated runs give identical output.\n- The script file is plain ASCII with LF line endings: no BOM, no CR characters, no trailing whitespace.\n- `tests/test_hello_sh.py`:\n  - runs the script as a subprocess, without passing it to bash;\n  - asserts every point above: exact stdout bytes, exit 0, shebang line, executable permission, folder contains only `hello.sh`, and the same output from two different working directories;\n  - passes under the existing `pytest` command, with no change to CI configuration or pytest settings.\n- The existing test suite, including the Python hello tests, still passes unchanged.\n- The diff against the base branch adds only `hello-world/hello.sh` and `tests/test_hello_sh.py` (plus `CHANGELOG.md` only under the conditional above). No existing file is modified.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
