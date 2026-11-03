# Work-item breakdown — ברכה בשם שהמפתח מציין ב-testbed-hello

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | PLAY-92: add --name option to testbed-hello for a personalised greeting |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "PLAY-92: add --name option to testbed-hello for a personalised greeting",
    "summary": "**Intent:** Let a developer run `testbed-hello --name NAME` and get `Hello, NAME!`, while the output without a name and every error and help path stay exactly as they are today. It is one module plus its tests in roeeoz/play1, the only repo that owns `testbed-hello`. The PR names PLAY-92 and the Epic PRD.\n\n**Owns:**\n- `src/testbed_utils/hello.py`: the `--name` option, trimming and fallback, and an optional `_DESCRIPTION` rewording;\n- `tests/test_hello_cli.py`: new and tightened CLI tests;\n- `tests/test_hello.py`: only if a new public helper is added;\n- `CHANGELOG.md`: new file, needed by repo-gate rule PLAY-G4.\n\n**Consumes, read-only:** `pyproject.toml` (entry point unchanged) and `src/testbed_utils/__init__.py` (leave it alone unless a new helper is deliberately exported).\n\n**Must not touch:** other modules, CI config, dependencies.\n\n**Acceptance criteria:**\n1. `testbed-hello --name Alice` prints exactly the single line `Hello, Alice!` and exits 0.\n2. `testbed-hello` with no arguments prints exactly `Hello, world!` followed by one newline, with empty stderr, and exits 0 (byte-for-byte as today).\n3. `testbed-hello --name \"\"`, `--name \" \"` and `--name \"   \"` each print `Hello, world!` and exit 0.\n4. `testbed-hello --name \"  Bob \"` prints `Hello, Bob!`. `testbed-hello --name alice` prints `Hello, alice!` (case kept). Whitespace inside a name is kept. Both exit 0.\n5. `testbed-hello --name` with no value prints nothing on stdout, shows a usage line and an error message on stderr, and exits 2.\n6. `testbed-hello --bogus`, `testbed-hello -x` and `testbed-hello extra` each print nothing on stdout, show usage and an error on stderr, and exit 2, as today.\n7. `testbed-hello --help` exits 0 and prints no greeting. It shows the usage line, a summary on exactly one stdout line, and an options entry for `--name`. The test checks the one-line summary directly, not through whitespace-collapsed matching.\n8. The public `hello_world()` still returns `Hello, world!`, is still exported from the package root, and its doctest still passes.\n9. Any new public function has a docstring with a runnable `>>>` example (run by the existing module doctest test) and tests for the happy path, a boundary case (blank or whitespace name) and the no-name case.\n10. No new runtime or test dependencies. The code stays compatible with Python 3.10 and newer.\n11. All tests run in-process through the existing harness, with no network, clock or file access, and use placeholder names only.\n12. `CHANGELOG.md` exists with a `## Unreleased` section that has an entry describing the new `--name` option for `testbed-hello`.\n13. `pytest` passes, and the diff is ≤ 300 changed lines.\n14. `testbed-hello --name \"Ada Lovelace\"` prints exactly the single line `Hello, Ada Lovelace!` and exits 0: a name with an inner space is greeted whole, not split or rejected. A unit test in `tests/test_hello_cli.py` asserts this exact output.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
