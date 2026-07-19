# High-Level Design: play1 Notes API

## 1. System Overview

A net-new HTTP API surface added to the `play1` repository, exposing two endpoints — `POST /notes` and `GET /search` — backed entirely by an in-process Python list. No external services, databases, or filesystem writes are involved. All changes are additive; no existing file is modified for functional reasons.

---

## 2. Architecture Overview

```
┌──────────────────────────────────────────────┐
│               play1 process                  │
│                                              │
│  HTTP Client                                 │
│      │                                       │
│      ▼                                       │
│  ┌──────────────────┐   ┌─────────────────┐  │
│  │  Flask App        │──▶│   NoteStore     │  │
│  │  app.py           │   │   notes.py      │  │
│  │  POST /notes      │   │  list[Note]     │  │
│  │  GET  /search     │   │  int counter    │  │
│  └──────────────────┘   └─────────────────┘  │
└──────────────────────────────────────────────┘
```

| Component | Responsibility | File |
|-----------|---------------|------|
| `NoteStore` | In-memory create + search | `src/testbed_utils/notes.py` |
| Flask App | HTTP routing, validation, serialization | `src/testbed_utils/app.py` |
| Unit tests | NoteStore isolation | `tests/test_note_store.py` |
| Integration tests | Full HTTP surface via test client | `tests/test_notes_api.py` |
| Benchmark | Assert p95 < 200 ms at 10 000 notes | `tests/test_bench.py` |

---

## 3. Data Flow Design

**POST /notes**
```
Client → POST /notes {title, body}
  → Flask: parse JSON body
  → validate: title and body must be non-empty strings
      missing or empty → 400 {"field": "<name>", "error": "required and must be non-empty"}
  → NoteStore.create(title, body) → Note(id, title, body)
  → 201 {"id": int, "title": str, "body": str}
```

**GET /search**
```
Client → GET /search?q=<text>
  → Flask: extract q param
  → q absent → 400 {"error": "q is required"}
  → NoteStore.search(q): case-insensitive substring scan, insertion order
  → 200 [{"id": int, "title": str, "body": str}, ...]  ([] when no match)
```

---

## 4. Component Breakdown

### NoteStore — `src/testbed_utils/notes.py`
```python
@dataclass
class Note:
    id: int
    title: str
    body: str

class NoteStore:
    def __init__(self):
        self._notes: list[Note] = []
        self._next_id: int = 1

    def create(self, title: str, body: str) -> Note: ...
    def search(self, q: str) -> list[Note]: ...  # q.lower() in title.lower() or body.lower()
```

### Flask App — `src/testbed_utils/app.py`
- `create_app(store: NoteStore | None = None) -> Flask`
- Module-level `_store = NoteStore()` used when no store injected (production path)
- `POST /notes` route: validate → create → jsonify → 201
- `GET /search` route: get q → 400 if absent → search → jsonify → 200

---

## 5. Interface Contracts

**POST /notes**
- Request: `Content-Type: application/json`, `{"title": str, "body": str}`
- 201 OK: `{"id": int, "title": str, "body": str}`
- 400 Bad Request: `{"field": "title" | "body", "error": "required and must be non-empty"}`

**GET /search**
- Request: `GET /search?q=<string>`
- 200 OK: `[{"id": int, "title": str, "body": str}, ...]` (empty array on no match, never 404)
- 400 Bad Request (absent q): `{"error": "q is required"}`

---

## 6. Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| HTTP framework | Flask 3.x | Minimal dep; built-in test client; synchronous; no async complexity |
| ID type | Sequential integer (1, 2, 3…) | Deterministic, ordered, simplest; aligns with insertion-order guarantee |
| Storage structure | `list[Note]` + `int` counter | O(1) append; O(n) scan over 10 k short notes < 10 ms on modern CPython |
| Missing `q` param | 400 `{"error": "q is required"}` | Absent param is a client error, distinct from an empty result set |
| App factory | `create_app(store=None)` | Fresh store injected per test; production uses module-level singleton |
| Existing CI | No modification needed | `.github/workflows/ci.yml` already runs `pytest tests/` and the gate check; new tests are auto-discovered |

---

## 7. Risks & Constraints

- **Thread safety**: `list` and `int` counter are not thread-safe. Flask dev server and pytest test client are both single-threaded; no lock needed at this scope. A threaded WSGI deployment would require a `threading.Lock`.
- **CI gate**: `ci.yml` fails if `CI_FAIL` exists at repo root. Implementation must never create or reference this file.
- **Performance**: `str.lower() in str.lower()` over 10 000 short strings runs comfortably within 10 ms; the 200 ms p95 target has an order-of-magnitude margin.
- **Dependency addition**: `flask>=3` added to both `[project.dependencies]` and `[project.optional-dependencies] test` in `pyproject.toml`. Flask 3.x supports Python ≥ 3.9, compatible with the `>=3.10` constraint.
