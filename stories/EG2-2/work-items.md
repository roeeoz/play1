# Work-item breakdown — e2e-gate-2b spanish greeting in both repos

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | pdlc-judge-e2e: add Spanish (es → Hola) to the greeting catalog |  |
| 2 | t2 | play1: testbed-hello accepts --lang {en,es} and prints Hola, world! for es |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "181c059c-8487-462e-b8c9-980580fefebb",
    "title": "pdlc-judge-e2e: add Spanish (es → Hola) to the greeting catalog",
    "summary": "**Intent:** Add Spanish as a supported language in the greeting catalog so `greeting(\"es\")` returns `Hola` (FR1, FR2, FR9 for this repo). This repo owns its catalog; no code is shared with play1.\n\n**Owns:** `greetings/catalog.py` (the `GREETINGS` entry; docstring example optional), `tests/test_catalog.py`.\n**Consumes:** nothing.\n\n**Acceptance criteria:**\n- `greeting(\"es\")` returns exactly `Hola` (capital H, no punctuation) and `GREETINGS[\"es\"] == \"Hola\"`.\n- `GREETINGS` contains exactly the keys `en` and `es`; `greeting(\"en\")` still returns `Hello`.\n- `greeting(\"xx\")` still raises `KeyError`.\n- A new unittest in `tests/test_catalog.py` asserts `greeting(\"es\") == \"Hola\"`; all existing tests (English greeting, unknown-language error, every greeting is a single capitalised alphabetic word) still pass.\n- `python3 -m unittest discover -s tests -t .` passes from the repo root with stdlib only (no new dependencies).\n- No other behaviour changes.",
    "dependsOn": [],
    "requirementRefs": []
  },
  {
    "ref": "t2",
    "repoId": "674de8fd-0dc3-4ecc-a171-00f73cf6af23",
    "title": "play1: testbed-hello accepts --lang {en,es} and prints Hola, world! for es",
    "summary": "**Intent:** Give the `testbed-hello` console script an optional `--lang` argument (choices `en`, `es`, default `en`) so `--lang es` prints `Hola, world!` while the default output stays `Hello, world!` (FR3–FR8, FR9 for this repo). play1 does not import the pdlc-judge-e2e catalog; the word `Hola` is its own literal.\n\n**Owns:** `src/testbed_utils/hello.py` (`main()` argument parsing and greeting selection), `tests/test_hello_cli.py`; may add assertions to `tests/test_hello.py`.\n**Consumes:** `pyproject.toml` entry point `testbed-hello = testbed_utils.hello:main` (unchanged), `testbed_utils/__init__.py` export of `hello_world` (unchanged).\n\n**Acceptance criteria:**\n- `testbed-hello` and `testbed-hello --lang en` print exactly `Hello, world!\\n` to stdout, empty stderr, exit 0.\n- `testbed-hello --lang es` (and `--lang=es`) prints exactly `Hola, world!\\n` to stdout, empty stderr, exit 0.\n- `testbed-hello --lang fr`, `--lang ES` (values are case-sensitive) and `--lang` with no value: exit 2, empty stdout, stderr contains `usage:` and `error`, and neither `Hello, world!` nor `Hola, world!` appears anywhere in the output.\n- `testbed-hello --help`: exit 0, empty stderr, stdout contains `usage:`, the existing description text and `--lang` (with its `en`/`es` choices), and contains neither `Hello, world!` nor `Hola, world!`.\n- Existing bad-option cases (`--bogus`, `-x`, `extra`) still exit 2 with usage + error on stderr and no greeting.\n- `hello_world()` still returns `Hello, world!` with an unchanged signature, stays exported from `testbed_utils`, and its doctest still passes.\n- New pytest tests in `tests/` cover: default, `--lang en`, `--lang es`, an unsupported value, missing value, and `--lang` appearing in help; the `es` test asserts the exact line `Hola, world!` so the Spanish word is pinned to `Hola`.\n- `pip install -e \".[test]\" && pytest` passes on Python 3.12 (CI `test` job); changes stay under `src/` and `tests/`, no new shell scripts, no file over 200 KB, no `CI_FAIL` file (layout gate and `gate` job stay green).\n- No other behaviour changes: `pdf-extract`, `testbed-num-summary`, `guestbook`, `qa/` and `hello-world/` are untouched; `, world!` is not translated.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
