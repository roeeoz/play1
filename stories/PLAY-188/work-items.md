# Work-item breakdown — מפתח רואה את גרסת החבילה מתוך testbed-hello

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | PLAY-188: add --version to testbed-hello |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "PLAY-188: add --version to testbed-hello",
    "summary": "**Intent:** Add a `--version` option to the `testbed-hello` console script that prints one line `testbed-hello <version>` — the version the installed `testbed-utils` distribution declares — to stdout and exits 0 without the greeting, while greeting, `--help` and unknown-option behaviour stay as today (spec FR1–FR7). See `stories/PLAY-188/hld.md` §5 for the settled CLI contract and edge cases.\n\n**Owns:** `src/testbed_utils/hello.py`, `tests/test_hello_cli.py` (add tests; existing tests keep their assertions).\n**Consumes (read-only, must not change):** `pyproject.toml` (`version = \"0.1.0\"`, `[project.scripts] testbed-hello`), `src/testbed_utils/__init__.py` (`__version__ = \"0.1.0\"`), `.github/workflows/ci.yml`, `.factory/testing.md`.\n\n**Acceptance criteria:**\n1. `testbed-hello --version` writes exactly `testbed-hello 0.1.0\\n` to stdout, nothing to stderr, exit code 0.\n2. `Hello, world!` appears nowhere in the output of `--version`.\n3. The printed version is the installed distribution's declared version, not a constant: a test that makes the installed metadata report a different version (e.g. `9.9.9`) sees `testbed-hello 9.9.9`; a test asserts the package's `__version__` equals the installed metadata version.\n4. If no installed `testbed-utils` metadata is found, `--version` prints the package's `__version__`; the greeting and `--help` never fail because metadata is missing.\n5. `testbed-hello --help` exits 0, shows the one-line description unchanged, and lists `--version`; `Hello, world!` is not printed.\n6. `testbed-hello` with no arguments prints `Hello, world!\\n` and exits 0 (unchanged).\n7. `--no-such-option`, `-x`, `extra`, `-V` each exit 2 with usage and an `error:` line on stderr, empty stdout, no greeting.\n8. `--version` combined with other arguments follows standard argparse behaviour (version line, exit 0) per hld.md §5; no short alias is added.\n9. `pyproject.toml` and `__init__.py` still declare `0.1.0`; no other tool, dependency or CI file changes.\n10. `pip install -e \".[test]\" && pytest` passes; tests are in-process with no network, clock or files outside `tests/fixtures`; diff under 300 lines; code under `src/`, tests under `tests/`.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
