# Work-item breakdown — QA-20261122-S3 Add a farewell greeting to greetlib (play2) and a matching qa script in play1

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | play2: add farewell to greetlib with pytest coverage |  |
| 2 | t2 | play1: add standalone s3_greeting farewell module with pytest coverage |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "ca5fc0d8-ad38-480d-a307-2507f6ccc4d4",
    "title": "play2: add farewell to greetlib with pytest coverage",
    "summary": "**Intent:** Add a `farewell` greeting to greetlib, next to `greet` and in the same style, so library callers can get `\"goodbye, <name>\"`. play2 owns greetlib.\n\n**Owns:** `src/greetlib/greet.py` (adds `farewell` only) and a new `tests/test_farewell.py`.\n**Consumes, unchanged:** `src/greetlib/__init__.py`, `tests/test_greet.py`, `pyproject.toml`, `.github/workflows/ci.yml`.\n\n**Acceptance criteria:**\n- `from greetlib.greet import farewell` works. Its `name` parameter is a `str` that defaults to `\"world\"`, and it returns a `str`.\n- `farewell()` returns `\"goodbye, world\"`.\n- `farewell(\"Ada\")` returns `\"goodbye, Ada\"`.\n- `farewell(\"  \")` and `farewell(\"\")` return `\"goodbye, world\"`.\n- `farewell(\"  Ada  \")` returns `\"goodbye, Ada\"`: leading and trailing whitespace is stripped.\n- The output is lowercase `goodbye`, a comma, one space and the name, with no trailing newline or punctuation.\n- Non-str input gets no new validation and fails like `greet` does today.\n- `tests/test_farewell.py` asserts at least the `\"Ada\"` and `\"  \"` cases, plus the default and stripped cases above. It imports from `greetlib.greet`, not from the package root.\n- `greet`, `main`, the `greet` console script, `src/greetlib/__init__.py` and `tests/test_greet.py` are unchanged. `from greetlib import farewell` is not offered.\n- The diff touches exactly `src/greetlib/greet.py` and the one new test file. No `CI_FAIL` file is added.\n- `pip install -e \".[test]\" && pytest` passes on Python 3.12, with the new tests collected through `testpaths = [\"tests\"]`.",
    "dependsOn": [],
    "requirementRefs": []
  },
  {
    "ref": "t2",
    "repoId": "2a317817-a49c-4dce-af15-1a2d90da349a",
    "title": "play1: add standalone s3_greeting farewell module with pytest coverage",
    "summary": "**Intent:** Add a standalone farewell module to play1's existing `testbed_utils` package. It produces the same text as greetlib's `farewell`, built from `FAREWELL_FORMAT`, and does not depend on greetlib. play1 owns its own copy so that each repository stays testable on its own.\n\n**Owns (new files only):** `src/testbed_utils/s3_greeting.py` and `tests/test_s3_greeting.py`.\n**Consumes, unchanged:** the existing `src/testbed_utils/__init__.py` (package marker; not edited, so the module is not re-exported), `pyproject.toml` and `.github/workflows/ci.yml`. It must not touch `tests/test_qa_s3_greeting.py` or anything under `qa/`.\n\n**Acceptance criteria:**\n- `from testbed_utils.s3_greeting import farewell, FAREWELL_FORMAT` works, and `FAREWELL_FORMAT == \"goodbye, {name}\"`.\n- The result of `farewell` is built from `FAREWELL_FORMAT`.\n- `farewell(\"Ada\")` returns `\"goodbye, Ada\"`.\n- `farewell(\"  \")` and `farewell(\"\")` return `\"goodbye, world\"`.\n- `farewell(\"  Ada  \")` returns `\"goodbye, Ada\"`.\n- `farewell()` with no argument returns `\"goodbye, world\"`, matching greetlib.\n- A name that contains braces, such as `\"{x}\"`, is returned literally as `\"goodbye, {x}\"`.\n- The module does not import greetlib, and greetlib does not need to be installed for the module or its test to work.\n- `tests/test_s3_greeting.py` asserts at least `farewell(\"Ada\") == \"goodbye, Ada\"`, `farewell(\"  \") == \"goodbye, world\"` and the `FAREWELL_FORMAT` value.\n- The diff only adds these two files and edits no existing file: no `__init__.py`, `pyproject.toml`, CI or `qa/` change, and no `CI_FAIL` file.\n- It passes the play1 layout gate: source is under `src/`, tests are under `tests/`, and no shell script is added.\n- `pip install -e \".[test]\" && pytest` passes on Python 3.12, with the new test collected through `testpaths = [\"tests\"]`.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
