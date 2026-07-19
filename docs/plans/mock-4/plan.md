# Implementation Plan: play1 Notes API

## Context

Two HTTP endpoints — `POST /notes` and `GET /search` — are being added as a net-new package (`testbed_utils`) to the `play1` repository. API consumers gain the ability to create notes and retrieve them by case-insensitive substring match. All state lives in a Python list for the lifetime of the process; the only new dependency is Flask 3.x.

---

## Approach

Work is delivered in two sequential tickets. **t1** builds the data layer (`notes.py`) and its unit tests with no web-framework dependency — the contract (`NoteStore`, `Note`) that t2 imports. **t2** wires that store into a Flask app factory, adds the `flask>=3` dependency, writes integration tests via the Flask test client, and adds the p95 benchmark. A one-time bootstrap step (prereq) creates the package scaffold before either ticket begins.

Sequencing constraints from the dependency graph:
- Bootstrap → t1 → t2
- `pyproject.toml` gets `flask>=3` in t2, not earlier
- Integration tests and benchmark cannot be written until `app.py` exists

---

## Steps

### Prereq — Bootstrap package scaffold

**Step 1** — Create `pyproject.toml` at repo root:
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "testbed-utils"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
test = ["pytest>=8"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2** — Create `src/testbed_utils/__init__.py` (empty — makes the package importable under the src layout).

**Step 3** — Create `tests/__init__.py` (empty — enables pytest to collect the test directory).

---

### t1 — Note data model and in-memory store

**Step 4** — Create `src/testbed_utils/notes.py`:
- `@dataclass class Note` with fields `id: int`, `title: str`, `body: str`.
- `class NoteStore` with `self._notes: list[Note] = []` and `self._next_id: int = 1`.
- `create(self, title: str, body: str) -> Note`: instantiate `Note(id=self._next_id, title=title, body=body)`, append to `self._notes`, increment `self._next_id`, return the note.
- `search(self, q: str) -> list[Note]`: compute `q_low = q.lower()`, return `[n for n in self._notes if q_low in n.title.lower() or q_low in n.body.lower()]` (preserves insertion order via list iteration).

**Step 5** — Create `tests/test_note_store.py` with the following 9 unit tests (direct import, no HTTP):
1. `test_create_first_note_gets_id_1` — `store.create('T', 'B').id == 1`
2. `test_create_second_note_gets_id_2` — two creates; second note id is 2
3. `test_create_returns_correct_fields` — title and body round-trip exactly
4. `test_search_matches_title_case_insensitive` — query `'NOTE'` matches title `'My note'`
5. `test_search_matches_body_case_insensitive` — query `'NOTE'` matches body `'A note about things'`
6. `test_search_title_only_match` — match via title when body does not contain query
7. `test_search_body_only_match` — match via body when title does not contain query
8. `test_search_returns_empty_list_on_no_match` — query `'xyz'` against unrelated notes returns `[]`
9. `test_search_returns_results_in_insertion_order` — three notes created in order; search returning all three preserves creation order; `test_fresh_store_has_no_notes` — `NoteStore()._notes == []`

Run after this step: `pytest tests/test_note_store.py` — all 9 tests must pass.

---

### t2 — Flask HTTP endpoints, integration tests, p95 benchmark

**Step 6** — Update `pyproject.toml`:
- Add `"flask>=3"` to `[project.dependencies]`.
- Add `"flask>=3"` to `[project.optional-dependencies] test` alongside `pytest`.

**Step 7** — Create `src/testbed_utils/app.py`:

```python
from flask import Flask, jsonify, request
from .notes import Note, NoteStore

_store = NoteStore()

def create_app(store: NoteStore | None = None) -> Flask:
    app = Flask(__name__)
    _s = store if store is not None else _store

    @app.post("/notes")
    def create_note():
        data = request.get_json(silent=True) or {}
        for field in ("title", "body"):
            if not data.get(field):  # missing, None, or empty string
                return jsonify({"field": field, "error": "required and must be non-empty"}), 400
        note = _s.create(data["title"], data["body"])
        return jsonify({"id": note.id, "title": note.title, "body": note.body}), 201

    @app.get("/search")
    def search_notes():
        q = request.args.get("q")
        if q is None:
            return jsonify({"error": "q is required"}), 400
        results = _s.search(q)
        return jsonify([{"id": n.id, "title": n.title, "body": n.body} for n in results]), 200

    return app
```

Validation iterates `("title", "body")` in that order — the first failing field is reported; a non-JSON body is treated as `{}`.

**Step 8** — Create `tests/test_notes_api.py`:

Define a pytest fixture `client` that builds `create_app(store=NoteStore())` and calls `app.test_client()` with `app.config["TESTING"] = True`. Each test receives a fresh client and store.

10 integration tests:
1. `test_post_valid_note_returns_201` — AC1: status 201, response has `id`, `title`, `body`
2. `test_post_missing_title_returns_400` — AC2: body `{"body": "x"}` → 400, response JSON contains `"title"`
3. `test_post_empty_body_returns_400` — AC3: body `{"title": "t", "body": ""}` → 400, response JSON contains `"body"`
4. `test_search_case_insensitive_match` — AC4: create note with body `'A note about things'`, search `q=NOTE` → 200 with that note
5. `test_search_no_match_returns_empty_array` — AC5: `q=zzznomatch` → 200 `[]`
6. `test_search_results_in_insertion_order` — AC6: create three notes, search returns them in creation order
7. `test_search_missing_q_returns_400` — OQ2: `GET /search` with no `q` → 400 `{"error": "q is required"}`
8. `test_search_title_only_match` — query present only in title matches
9. `test_search_body_only_match` — query present only in body matches
10. `test_fresh_store_has_no_notes` — AC8: `GET /search?q=a` on fresh store returns `[]`

Run after this step: `pytest tests/test_note_store.py tests/test_notes_api.py` — all 19 tests must pass.

**Step 9** — Create `tests/test_bench.py`:

```python
import statistics
import time
from testbed_utils.notes import NoteStore
from testbed_utils.app import create_app

def test_p95_search_under_200ms():
    store = NoteStore()
    for i in range(10_000):
        store.create(f"title {i}", f"body content {i}")
    app = create_app(store=store)
    client = app.test_client()
    latencies = []
    for _ in range(200):
        t0 = time.perf_counter()
        client.get("/search?q=xyz")
        latencies.append(time.perf_counter() - t0)
    p95 = statistics.quantiles(latencies, n=20)[18]  # index 18 = 95th percentile
    assert p95 < 0.200, f"p95 latency {p95:.3f}s exceeds 200 ms"
```

The query `xyz` produces no matches — this is worst-case scan (no early exit). 200 iterations give a stable distribution for `statistics.quantiles` with `n=20`.

---

## Verification

| After step | Command | Expected result |
|---|---|---|
| 5 | `pytest tests/test_note_store.py -v` | 9 passed |
| 8 | `pytest tests/test_note_store.py tests/test_notes_api.py -v` | 19 passed |
| 9 | `pytest tests/test_bench.py -v` | 1 passed, p95 assertion holds |
| Final | `pytest tests/ -v` | All tests pass; no `CI_FAIL` file present |

Acceptance criteria cross-check:
- **AC1** → `test_post_valid_note_returns_201`
- **AC2** → `test_post_missing_title_returns_400`
- **AC3** → `test_post_empty_body_returns_400`
- **AC4** → `test_search_case_insensitive_match`
- **AC5** → `test_search_no_match_returns_empty_array`
- **AC6** → `test_search_results_in_insertion_order`
- **AC7** → `test_p95_search_under_200ms`
- **AC8** → `test_fresh_store_has_no_notes`

---

## Risks & Open Points

- **`statistics.quantiles` index**: `quantiles(data, n=20)[18]` returns the 19th of 20 cut points, i.e., the value below which 95 % of the data falls. Verify this index is correct before merge; off-by-one would silently measure p100 or p90.
- **Validation field order**: `POST /notes` reports the first failing field in `("title", "body")` order. Tests in `test_notes_api.py` must be written against whichever order is implemented — they are coupled by design.
- **Non-JSON request body**: `request.get_json(silent=True)` returns `None` for a missing or malformed body; the `or {}` fallback means both fields are then missing, and the 400 response references `title`. A reviewer may want a distinct error message for a completely missing body, but the spec does not require it.
- **Package name in pyproject.toml**: The `[project] name` is set to `testbed-utils` (hyphenated, as is convention), while the importable package is `testbed_utils` (underscored). This is standard setuptools behaviour but should be verified against CI's install invocation if one exists.
- **Thread safety**: `NoteStore` uses a plain `list` and `int` counter with no lock. This is safe for the Flask dev server and pytest test client (both single-threaded) but would require a `threading.Lock` under a threaded WSGI server. No action needed now; noting for future reference.
