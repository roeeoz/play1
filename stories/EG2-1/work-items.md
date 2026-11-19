# Work-item breakdown — e2e-gate-2 spanish greeting in both repos

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | pdlc-judge-e2e: add Spanish greeting "es": "Hola" to the catalog |  |
| 2 | t2 | play1: add --lang {en,es} to testbed-hello |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "181c059c-8487-462e-b8c9-980580fefebb",
    "title": "pdlc-judge-e2e: add Spanish greeting \"es\": \"Hola\" to the catalog",
    "summary": "**Intent:** Add Spanish to the greeting catalog so `greeting(\"es\")` returns `Hola`, the shared Spanish word for this story. This repo owns the catalog.\n\n**Owns:** `greetings/catalog.py` (the `GREETINGS` data only), `tests/test_catalog.py`.\n**Consumes:** nothing from another ticket.\n\n**Acceptance criteria:**\n- `GREETINGS` equals `{\"en\": \"Hello\", \"es\": \"Hola\"}`; the value is exactly `Hola` (capital H, no accent, no punctuation).\n- `greeting(\"es\")` returns `\"Hola\"`, asserted by a new test in `tests/test_catalog.py`.\n- `greeting(\"en\")` still returns `\"Hello\"`; `greeting(\"xx\")` and `greeting(\"ES\")` raise `KeyError` (lookup stays case-sensitive); the existing error message and `greeting()` logic are unchanged.\n- The existing capitalised-alphabetic-word test still passes with the new entry.\n- `python3 -m unittest discover -s tests -t .` passes from the repo root (the gate in `.factory/testing.md`); no new dependency, no other behaviour change.",
    "dependsOn": [],
    "requirementRefs": []
  },
  {
    "ref": "t2",
    "repoId": "674de8fd-0dc3-4ecc-a171-00f73cf6af23",
    "title": "play1: add --lang {en,es} to testbed-hello",
    "summary": "**Intent:** Give the `testbed-hello` console script an optional `--lang` option (`en` default, `es` prints `Hola, world!`). This repo owns the CLI; it must not import or read the pdlc-judge-e2e catalog.\n\n**Owns:** `src/testbed_utils/hello.py` (`main()` and any new language→greeting mapping), `tests/test_hello_cli.py`.\n**Consumes (must stay unchanged):** `hello_world()` no-arg result `Hello, world!` and its doctest, `_DESCRIPTION`, `src/testbed_utils/__init__.py`, `tests/test_hello.py`, `pyproject.toml` entry point `testbed-hello = \"testbed_utils.hello:main\"`.\n\n**Acceptance criteria:**\n- `testbed-hello` (no args) prints exactly `Hello, world!\\n` to stdout, empty stderr, exit 0.\n- `testbed-hello --lang en` (and `--lang=en`) prints exactly `Hello, world!\\n`, empty stderr, exit 0.\n- `testbed-hello --lang es` (and `--lang=es`) prints exactly `Hola, world!\\n`, empty stderr, exit 0 — the word is exactly `Hola`.\n- `--lang fr`, `--lang ES` (case-sensitive) and `--lang` with no value: empty stdout, stderr contains `usage:` and `error`, exit 2. Tests assert only these stable parts (plus that the invalid-choice error names `en` and `es`), not argparse's exact message text, which varies across Python 3.10–3.13.\n- `--help` exits 0 with empty stderr, still shows the unchanged `_DESCRIPTION` sentence, lists `--lang` with its `{en,es}` choices, and does not contain `Hello, world!`.\n- `--bogus`, `-x` and `extra` are still rejected with exit 2 (existing `TestBadOption` unchanged and passing).\n- `hello_world()` still returns `Hello, world!` with its doctest passing; `tests/test_hello.py` passes unmodified.\n- New tests drive the real `main()` (existing `run_main` helper) for the default, `en`, `es` and invalid-value cases.\n- `pip install -e \".[test]\"` then `pytest` passes; layout gate rules hold (source under `src/`, tests under `tests/`, no file >200 KB); no `CI_FAIL` file; no other script (`hello-world/hello.sh`, `qa/*`) changed.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
