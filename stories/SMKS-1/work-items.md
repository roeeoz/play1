# Work-item breakdown — Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add hello-world/hello.sh with pytest coverage and changelog line |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "8f33756e-ec87-40d9-ad6b-cebeffef7fbf",
    "title": "Add hello-world/hello.sh with pytest coverage and changelog line",
    "summary": "**Intent:** Ship the executable bash script `hello-world/hello.sh` that prints exactly `Hello, World!!` (the developer's change of 2026-11-25, replacing the spec's lowercase `hello world`), verified by pytest in `tests/`, with the `CHANGELOG.md` line the play1 repo gate (rule 4) requires. One XS slice in `play1`, the only repo.\n\n**Owns:** `hello-world/hello.sh` (new, git mode 100755, LF line endings), `tests/test_hello_sh.py` (new), `CHANGELOG.md` (new).\n**Consumes (unchanged):** `pyproject.toml` `[tool.pytest.ini_options]` (testpaths = tests), `.github/workflows/ci.yml` `test` job (runs `pytest`), `tests/test_hello_cli.py` as the style pattern for exact stdout/stderr/exit assertions.\n\n**Acceptance criteria:**\n- `hello-world/` at the repo root contains exactly one file, `hello.sh` — no README, tests or other files.\n- The first line of `hello.sh` is exactly `#!/bin/bash`; the file is committed executable (mode 100755) with LF line endings.\n- Running `./hello-world/hello.sh` directly (no `bash` prefix) with no arguments, from the repo root or any other directory, writes exactly the bytes `Hello, World!!\\n` to stdout, nothing to stderr, and exits 0.\n- `$(./hello-world/hello.sh)` yields exactly `Hello, World!!`: capital `H` and `W`, a comma, one space, two exclamation marks, no leading/trailing whitespace, no carriage return, no second line, no banner or extra text.\n- `src/testbed_utils/hello.py` and `tests/test_hello_cli.py` (the separate Python CLI greeting `Hello, world!`) are unchanged.\n- The script adds no flags, `--help` or argument handling (recorded exception to the `qa/` script rule); no test asserts behavior with arguments.\n- New pytest tests in `tests/` run the script as a subprocess directly (exercising the shebang and exec bit, not via `bash hello.sh`), locate it relative to the test file rather than the cwd, and cover: exact stdout bytes, empty stderr, exit code 0, the `$(...)`-style captured value, the shebang line, the file being executable, and the folder listing only `hello.sh`.\n- `CHANGELOG.md` is created at the repo root with a `## Unreleased` heading and one line under it describing this change.\n- `pip install -e \".[test]\" && pytest` passes from the repo root with the new tests included; `.github/workflows/ci.yml`, `pyproject.toml`, `src/` and `README.md` are unchanged.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
