# Work-item breakdown — QA-20261124-N1 a helper that doubles a number

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add double(n) helper in testbed_utils.doubler, export it from the package root, with pytest tests |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "29ac813e-5088-44e7-a070-28c81f32b634",
    "title": "Add double(n) helper in testbed_utils.doubler, export it from the package root, with pytest tests",
    "summary": "**Intent:** Deliver SCRUM-127 end to end in `roeeoz/play1`: a pure helper `double(n)` returning `n * 2`, importable from `testbed_utils.doubler` and from the package root `testbed_utils`, covered by a pytest file that runs in the repo's `pytest` gate.\n\n**Owns:**\n- `src/testbed_utils/doubler.py` (new)\n- `tests/test_doubler.py` (new)\n- `src/testbed_utils/__init__.py` (edit: one import of `double` and one `\"double\"` entry in `__all__`, kept alphabetical; nothing else in the file changes)\n\n**Consumes, read-only:**\n- `src/testbed_utils/numutils.py` and `tests/test_numutils.py` as the style pattern (module docstring, type hints, docstring with doctest example, export/`__all__` test)\n- `.factory/testing.md`, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, `.github/workflows/ci.yml` (gates)\n- `stories/SCRUM-127/*` (plan documents)\n\n**Must not modify:** any other file under `src/` or `tests/` — including `tests/test_qa_20261122_s4_base.py` — and `pyproject.toml`, `.github/`, `qa/`.\n\n**Acceptance criteria:**\n1. `from testbed_utils.doubler import double` works; the function takes one parameter named `n`.\n2. For integers, `double(n)` returns `n * 2`: `double(3) == 6`, `double(0) == 0`, `double(-4) == -8`.\n3. `from testbed_utils import double` works, returns the same function object as `testbed_utils.doubler.double`, and `\"double\"` is in `testbed_utils.__all__`; every name previously in `__all__` is still there.\n4. `tests/test_doubler.py` exists under `tests/` and asserts criterion 2 for at least one positive, zero and one negative integer, plus criterion 3; it imports only through the installed package (no `conftest.py`, no `sys.path` changes).\n5. The helper prints nothing, performs no I/O, and adds no input validation: non-integer input is neither rejected nor tested.\n6. Any doctest example in `doubler.py` passes.\n7. After `pip install -e \".[test]\"`, `pytest` from the repo root passes every test in `tests/test_doubler.py` and all previously passing tests still pass; the only failing test is the pre-existing `tests/test_qa_20261122_s4_base.py::test_pre_existing_failure_on_the_qa_base`, which this change leaves untouched.\n8. The diff satisfies the repo gate: source only under `src/`, tests only under `tests/`, no file over 200 KB, no new dependency, no new console script.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
