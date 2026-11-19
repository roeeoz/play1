# Work-item breakdown — e2e-gate-1 hello greets by name

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add optional --name NAME to testbed-hello with tests |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "940db9b3-3388-4d4a-b2c3-33e67f1284c6",
    "title": "Add optional --name NAME to testbed-hello with tests",
    "summary": "**Intent** — Let `testbed-hello --name NAME` print `Hello, NAME!` while the no-argument run keeps printing `Hello, world!`; the CLI and its tests live in `roeeoz/play1`, so the whole story is one PR.\n\n**Owns** — `src/testbed_utils/hello.py` (`main()` only; `hello_world()`, its docstring/doctest and `_DESCRIPTION` stay unchanged), `tests/test_hello_cli.py` (add tests; existing tests stay as they are).\n**Consumes (read-only, must not change)** — `src/testbed_utils/__init__.py`, `tests/test_hello.py`, `pyproject.toml` (`testbed-hello` entry point), `.github/workflows/ci.yml`, `.factory/testing.md`.\n\n**Acceptance criteria**\n- `testbed-hello` (no args): stdout exactly `Hello, world!\\n`, stderr empty, exit 0.\n- `testbed-hello --name Alice`: stdout exactly `Hello, Alice!\\n`, stderr empty, exit 0; `--name=Alice` gives the same.\n- NAME is inserted verbatim: `--name \"Ada Lovelace\"` → `Hello, Ada Lovelace!\\n`; `--name \"\"` → `Hello, !\\n` (no validation, trimming or fallback to `world`); repeated `--name A --name B` → `Hello, B!\\n`.\n- `--name` with no value exits 2 with a usage error on stderr and nothing on stdout.\n- `--help` exits 0, stderr empty, stdout contains the usage text, lists `--name NAME`, still contains the unchanged description, and does not contain `Hello, world!`.\n- `--bogus`, `-x` and `extra` still exit 2 with a usage error on stderr and nothing on stdout; no `-n` short alias, positional name or environment-variable source is added.\n- `testbed_utils.hello_world()` still returns `'Hello, world!'`, its doctest passes, and `tests/test_hello.py` passes unmodified.\n- New tests in `tests/test_hello_cli.py` cover the no-argument case, the `--name` case, the verbatim/space and empty-name cases and the missing-value error; `pip install -e \".[test]\" && pytest` is green (CI `test` job), source stays under `src/` and tests under `tests/`.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
