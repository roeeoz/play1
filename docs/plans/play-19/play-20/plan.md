# Implementation plan — Guestbook JSON API (s1) for roeeoz/play1

| Field | Value |
| --- | --- |
| Work item | t1 — Guestbook JSON API: Flask service with SQLite storage, validation, tests, and run docs |
| Repo / branch | `roeeoz/play1` (`971bf272-f661-4343-ba13-83764c3aec1f`), branch `halo/feat/play-20` off `main` at `d656cd3` |
| Tier | T3 (one work item, no dependencies) |
| Inputs | `docs/plans/play-19/play-20/{spec,hld,work-items}.md` (this folder); `pyproject.toml`; `README.md`; `.gitignore`; `.factory/testing.md`; `.github/workflows/ci.yml`; `src/testbed_utils/*.py`; `tests/test_*.py` |

## Context

Story s1 adds play1's first HTTP surface: a JSON API that creates guestbook entries and lists them newest-to-oldest. The acceptance criteria (spec §5, AC1–AC7) require a create endpoint that validates `author` (1–50 characters) and `message` (1–300 characters), stamps a server-side creation time, rejects bad input without storing anything, and a list endpoint that returns every entry as a JSON array in a strictly deterministic newest-first order, `[]` when empty, all 100 entries after 100 creates, and runs as a standalone service beside the untouched `testbed_utils` package. The HLD fixes Flask 3 plus stdlib `sqlite3`, the routes, the response shape and the error envelope; s2 (page) and s3 (self-delete) build on that contract in parallel once this merges, so the contract freezes at merge. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `docs/plans/play-19/play-20/`.

## Research findings

### Change surface

| Path | Action | Why |
| --- | --- | --- |
| `src/guestbook/__init__.py` | **create** | Package marker with module docstring; re-exports `create_app`. Setuptools auto-discovers it via `pyproject.toml:22-23` (`[tool.setuptools.packages.find] where = ["src"]`). |
| `src/guestbook/validation.py` | **create** | Pure validation of the request payload (required, string, strip, length). |
| `src/guestbook/storage.py` | **create** | SQLite schema, `init_db`, `insert_entry`, `list_entries`; one connection per call. |
| `src/guestbook/app.py` | **create** | `create_app(db_path=None)` factory, the two routes, the error envelope helper, the `main()` console entry. |
| `tests/test_guestbook_api.py` | **create** | AC coverage through `app.test_client()` against a per-test temporary SQLite file. |
| `pyproject.toml` | **edit** (2 lines) | `"flask>=3"` appended to `dependencies` (`pyproject.toml:12`); `guestbook = "guestbook.app:main"` appended under `[project.scripts]` (`pyproject.toml:14-17`). |
| `README.md` | **edit** (append) | New `## Guestbook API` section after the last existing section (`README.md:92-97`). |

**Not touched:** `src/testbed_utils/**`, every existing `tests/test_*.py`, `tests/fixtures/**`, `.github/workflows/ci.yml`, `.factory/**`, `.gitignore`, `docs/argo-agent-runs.md`, `docs/plans/play-24/**`. No `CI_FAIL` exists at the root today (verified) and none may be created.

### Repository ground truth

- **Package layout:** `src/` layout, name `testbed-utils`, version `0.1.0`, `requires-python = ">=3.10"`, single runtime dependency `pypdf`, test extra `pytest>=8` (`pyproject.toml:5-20`). Three console scripts already exist (`pyproject.toml:14-17`); the new one follows the same `module:main` form.
- **Gate:** `.factory/testing.md:3` declares `test-gate: pytest`; the `test` job in `.github/workflows/ci.yml:12-24` runs `pip install -e ".[test]"` then `pytest` on Python 3.12, `ubuntu-latest`, with workflow-level `permissions: contents: read` (`ci.yml:8-9`). The `gate` job (`ci.yml:26-38`) fails iff `CI_FAIL` exists. No linter, formatter, type checker or coverage tool exists. The declared test layer is `package-api` (class production-path, run by the canonical gate; `.factory/testing.md:36-50`).
- **Existing suite:** 74 test functions across eight files under `tests/` (the "38 tests" figure in the injected plan narrative is stale; `tests/test_hello*.py`, `tests/test_num*.py` and `tests/test_numutils.py` were added since). No `conftest.py`, no `sys.path` manipulation: tests import only the installed distribution, so `src/guestbook/` must be importable after `pip install -e ".[test]"`.
- **Conventions (from `src/testbed_utils/numsummary.py:1-10`, `hello.py:1-5`, `textutils.py:1-9`):** one-line module docstring, `from __future__ import annotations`, stdlib imports then package imports, docstrings on public functions, `main()` without arguments as the console entry. Tests use `class Test<Behaviour>` groups, plain asserts and `pytest.mark.parametrize` (`tests/test_hello_cli.py:25-50`).
- **`.gitignore`:** `instance/` is ignored (`.gitignore:65`, verified with `git check-ignore`); `db.sqlite3` is also ignored (`.gitignore:61`) but only at that exact name. `src/guestbook/**` and `tests/test_guestbook_api.py` are not ignored (verified).
- **`.factory/memory/`:** absent. `CLAUDE.md` / `AGENTS.md`: absent.
- **`textutils.word_count`** (`src/testbed_utils/textutils.py:46-52`) treats whitespace-only text as zero words; the HLD cites this as the precedent for strip-then-validate.

### Toolchain facts verified in a throwaway virtualenv (Python 3.14, macOS, nothing written to the repo)

- `pip install "flask>=3"` resolves to Flask 3.1.3 and installs exactly seven distributions: `Flask`, `Werkzeug` 3.1.9, `Jinja2`, `MarkupSafe`, `itsdangerous`, `click`, `blinker`. One correction to the HLD's "pure Python" claim: `MarkupSafe` ships an optional compiled speedup (`_speedups.*.so`) with a pure-Python fallback; no package *requires* a compiled extension. The dependency-light constraint holds.
- `flask.__version__` still exists in 3.1.3 but emits a `DeprecationWarning` (removed in 3.2). Use `importlib.metadata.version("flask")` if a version is ever needed; the plan needs none.
- `request.get_json(silent=True, force=True)` returns: `None` for a non-JSON body, for an empty body and for the literal `null`; `[]` for a JSON array; the `dict` for a JSON object, also when sent with `Content-Type: text/plain`. So the single check `isinstance(payload, dict)` separates `invalid_json` from a validatable object. Consequence: a syntactically valid JSON object sent with a non-JSON content type is accepted (lenient); the tests must not assert the opposite.
- `jsonify([])` returns status 200 with body `[]`; returning `(jsonify(obj), 201)` yields 201. Flask's default JSON provider sets `sort_keys=True` and `ensure_ascii=True`, so non-ASCII authors/messages are emitted as `\uXXXX` escapes. That is valid JSON and `response.get_json()` decodes it; no change needed.
- `Flask.run()` calls `options.setdefault("threaded", True)`, so the `guestbook` console script serves requests from multiple threads. The storage layer must therefore not share one `sqlite3` connection across threads.
- stdlib `sqlite3`: 100 inserts from an 8-thread pool, each opening its own connection to the same file and closing it, produced 100 unique ids with no `database is locked` error, both with the default 5-second busy timeout and with an explicit `timeout=5`. `ORDER BY created_at DESC, id DESC` returned a strictly descending id sequence for rows sharing one `created_at` value.
- `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")` renders `2026-10-11T14:03:27.123456Z`. `datetime.UTC` is Python 3.11+ and must not be used (`requires-python >= 3.10`).
- `app.test_client()` instances created per thread work concurrently against one app.

### Contracts touched

**Provided (frozen at merge; consumed by s2 and s3):**

| Surface | Contract |
| --- | --- |
| `POST /api/guestbook/entries` | Body: JSON object with `author` (string) and `message` (string). Success: `201`, body `{"id": <int>, "author": <str>, "message": <str>, "created_at": <str>}`. Stored and returned values are the stripped strings. Any client-supplied `created_at` or `id` is ignored. |
| `GET /api/guestbook/entries` | `200`, JSON array of objects with the same four keys, ordered `created_at DESC, id DESC`. `[]` when empty. No pagination. |
| `created_at` | ISO-8601 UTC with microseconds and a `Z` suffix: `%Y-%m-%dT%H:%M:%S.%fZ`. Set by the server. |
| `id` | SQLite `INTEGER PRIMARY KEY AUTOINCREMENT`, stable and unique; s3 will delete by it. |
| Validation failure | `400`, body `{"error": {"code": "validation_error", "fields": {"author": "<msg>", "message": "<msg>"}}}`; `fields` lists only failing fields. Message text is English and is **not** part of the contract. |
| Non-JSON or non-object body | `400`, body `{"error": {"code": "invalid_json"}}` (no `fields` key). |
| Validation rule | Field missing, not a `str`, empty after `strip()`, or longer than the limit after `strip()` → rejected. Length counted in Python code points: `author` 1–50, `message` 1–300. |
| Configuration | `GUESTBOOK_DB_PATH` environment variable; default `instance/guestbook.sqlite3` relative to the current working directory. `create_app(db_path=...)` overrides both. |
| Run | `pip install -e .` then `guestbook` starts Flask's dev server on `127.0.0.1:5000`. |

**Consumed:** nothing from `testbed_utils`. Cross-repo contracts: none.

### Resolved unknowns

| Question | Resolution | Basis |
| --- | --- | --- |
| Whitespace-only `author`/`message` (spec §8) | Treated as empty → `validation_error`. Stored values are stripped. | HLD §5 "ריק אחרי strip"; work-item AC "whitespace-only … returns 400"; `word_count` precedent. |
| Error message format (spec §8) | Per-field envelope as in the table above. | HLD §5; work-item AC. |
| Non-dict JSON (`[]`, `null`, `"x"`) | `invalid_json`, nothing stored. | HLD §5; verified `get_json` behaviour. |
| Valid JSON object with a non-JSON `Content-Type` | Accepted (`force=True`). | Verified; simplest rule that never returns Werkzeug's HTML 415 page to s2. |
| Thread safety of SQLite under the dev server | One `sqlite3.connect(path)` per storage call, closed with `contextlib.closing`; no shared connection; no `check_same_thread=False`. | Verified 100 concurrent inserts; `Flask.run` is threaded by default. |
| `created_at` precision | Microseconds, fixed format string. `isoformat()` is rejected because it renders `+00:00`, not `Z`. | HLD §5 requires the `Z` suffix; `Date.parse` in s2 accepts the fixed form. |
| Default DB location | `instance/guestbook.sqlite3` relative to CWD; `init_db` creates the parent directory. | `.gitignore:65`; HLD §2. Flask's own `instance_path` is not used because it resolves relative to the package, which would place the file inside `src/` for an editable install. |
| Python version floor | 3.10 syntax only: `timezone.utc`, `X | None` annotations under `from __future__ import annotations`. | `pyproject.toml:10`; CI uses 3.12; local is 3.14. |
| Test isolation | `create_app(db_path=str(tmp_path / "test.sqlite3"))` per test; no env var leakage between tests. | Work-item AC "isolated temporary database per test". |

### Remaining unknowns

None that block implementation. The Werkzeug busy-timeout default (5 s) is sufficient for the 20-thread test; if the test ever reports `database is locked`, pass `timeout=5` explicitly before changing strategy.

## Locked decisions and assumptions

**Locked decisions**

| Decision | Source |
| --- | --- |
| Routes `POST`/`GET /api/guestbook/entries`; status `201`/`200`/`400`; four-key entry shape; per-field `validation_error` envelope; `invalid_json` envelope without `fields` | `hld.md` §5; work-item t1 AC |
| Flask 3.x is the only new runtime dependency; storage is stdlib `sqlite3` | `hld.md` §2, §6; spec §6 "dependency-light" |
| `id` is a stable unique integer (needed by s3); order is `created_at DESC, id DESC` | `hld.md` §5, §6; spec §6 |
| `created_at` is server-set, ISO-8601 UTC ending in `Z`; client value ignored | `hld.md` §5; spec FR1 |
| Validation: required, string, strip, 1–50 / 1–300 code points; stored value is stripped | `hld.md` §5; work-item AC |
| DB path configurable by environment variable, default under `instance/` | `hld.md` §2; work-item AC; `.gitignore:65` |
| `guestbook` console script in `[project.scripts]`; README section documenting endpoints, envelope, DB variable, run and test | `hld.md` §4, §5; work-item AC |
| Tests in `tests/test_guestbook_api.py` via Flask's test client with a temporary DB per test; full `pytest` stays green | `hld.md` §4; work-item AC; `.factory/testing.md:3` |
| `src/testbed_utils/**`, existing tests and `.github/workflows/ci.yml` unchanged; no `CI_FAIL` | work-item t1 "Consumes (read-only)"; `hld.md` §7 |
| No DELETE, UI, pagination, auth, moderation | spec §2 Non-Goals |

**Assumptions**

| Assumption | Evidence | If wrong |
| --- | --- | --- |
| Microsecond precision in `created_at` is acceptable to s2 | HLD fixes only "ISO-8601 UTC with `Z`"; `Date.parse` handles fractional seconds | s2 truncates on its side; the API format does not change after merge. |
| Lenient content-type handling (valid JSON object accepted regardless of `Content-Type`) is acceptable | HLD only specifies behaviour for invalid JSON and non-object bodies | Tighten to `is_json` check in a follow-up; no s2/s3 code depends on rejection. |
| English error message text may change freely | HLD §5 marks the text as display material for s2; spec §3 requires no specific text | s2 maps by field name, not by text; no impact. |
| Microsecond timestamp plus `id` tiebreak makes the order absolute across restarts | SQLite `AUTOINCREMENT` never reuses ids; verified ordering query | None foreseen; the tiebreak is the guarantee. |
| The dev server binding `127.0.0.1:5000` is the intended run mode | HLD §5 "שרת פיתוח מקומי"; README states local-only | Host/port become CLI flags in a later story; not in scope here. |

## Solution proposal

**Approach.** One new package `src/guestbook/` with three small modules and one test file, wired by two appended lines in `pyproject.toml`, documented by one appended README section. Nothing in `testbed_utils` changes. The package is discovered by the existing `[tool.setuptools.packages.find]` block, so `pip install -e ".[test]"` (what CI runs) installs Flask and makes `guestbook` importable without any CI change.

**Module boundaries.**

1. `validation.py` — pure function `validate_entry(payload: dict) -> tuple[dict[str, str] | None, dict[str, str]]` plus constants `AUTHOR_MAX = 50`, `MESSAGE_MAX = 300`. For each of `author` and `message`: missing → `"is required"`; not a `str` → `"must be a string"`; empty after `strip()` or over the limit → `"must be between 1 and N characters"`. Success returns the stripped values and an empty error dict. No Flask import, so it is unit-testable in isolation and reusable by s3.
2. `storage.py` — `init_db(path)` creates the parent directory and runs `CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL)`; `insert_entry(path, author, message, created_at) -> dict` returns the full row using `lastrowid`; `list_entries(path) -> list[dict]` selects with `ORDER BY created_at DESC, id DESC`. Every function opens its own `sqlite3.connect(path)` inside `contextlib.closing` and commits before closing. No module-level state.
3. `app.py` — `create_app(db_path: str | None = None) -> Flask` resolves the path (`db_path` argument → `GUESTBOOK_DB_PATH` → `instance/guestbook.sqlite3`), stores it in `app.config["GUESTBOOK_DB_PATH"]`, calls `init_db`, and registers the two routes. `_utc_now_iso()` produces the timestamp. `_error(code, status, fields=None)` builds the envelope. POST: `payload = request.get_json(silent=True, force=True)`; non-dict → `invalid_json`; `validate_entry` errors → `validation_error`; else insert and return 201. GET: `jsonify(list_entries(...))`. `main()` calls `create_app().run()`.
4. `__init__.py` — docstring and `from guestbook.app import create_app`.

**Key design decisions.**

- **Flask over FastAPI** (HLD §6, confirmed): seven distributions, no required compiled extension, built-in test client and threaded dev server.
- **Per-call SQLite connections**: the simplest correct strategy under Flask's threaded dev server and under a parallel test; verified with 100 concurrent inserts. A shared connection with a lock was rejected because it adds state to the app object and a lock to every request for no measurable benefit at this scale.
- **Order by `created_at DESC, id DESC`** rather than `id DESC` alone: `id` alone would satisfy the tests today, but the HLD contract names creation time as the primary key of the order and s2 displays relative time; keeping both columns in the `ORDER BY` makes the contract and the query say the same thing.
- **Fixed `strftime` format, not `isoformat()`**: guarantees the `Z` suffix and a constant width, which keeps string ordering in SQLite equal to chronological ordering.
- **`get_json(silent=True, force=True)`**: one call covers malformed JSON, empty body, wrong content type and `null`, all of which become `None` and map to `invalid_json`; nothing in the handler can raise Werkzeug's HTML error pages.
- **`validate_entry` always receives a `dict`**: the route performs the `isinstance` guard, so validation never has to defend against non-mapping input.
- **DB path relative to CWD, not Flask's `instance_path`**: with an editable install `app.instance_path` resolves next to `src/guestbook/`, which would write a database inside the source tree; CWD-relative `instance/` is what `.gitignore:65` already protects.
- **No `conftest.py`**: the repo has none, and a single fixture inside `tests/test_guestbook_api.py` is enough.

**Alternatives rejected.** In-memory list storage (loses entries on restart, needs a hand-rolled id counter, `:memory:` SQLite is per-connection and would break the per-call strategy). A `Blueprint` (one app, two routes; adds a layer with no second consumer). Pydantic or marshmallow validation (new dependencies for two fields).

## Ordered implementation steps

All steps belong to work item t1. Dependencies are acquired by `pip install -e ".[test]"` from a fresh virtualenv (no warm cache assumed); the only new dependency is `flask>=3`, resolved from PyPI by pip. No generated deliverables, no binaries, nothing for `.factory/delivery-assets`.

1. **Packaging.** Edit `pyproject.toml`: change line 12 to `dependencies = ["pypdf", "flask>=3"]`; add `guestbook = "guestbook.app:main"` as the last line of `[project.scripts]`. Touch nothing else in the file. Advances AC7. Covered by the `package-api` layer indirectly (every later test imports `guestbook`, which only works if this step is right).
2. **Validation module.** Create `src/guestbook/validation.py` per the Solution proposal. Advances AC1, AC2. Covered by `tests/test_guestbook_api.py::TestCreateValidation` and `::TestCreateEntry` (layer `package-api`).
3. **Storage module.** Create `src/guestbook/storage.py` per the Solution proposal, including parent-directory creation in `init_db`. Advances AC3, AC4, AC5, AC6. Covered by `::TestListEntries`, `::TestNoPagination`, `::TestAppSetup`.
4. **App factory and routes.** Create `src/guestbook/app.py` and `src/guestbook/__init__.py` per the Solution proposal. Advances AC1–AC7. Covered by every class in `tests/test_guestbook_api.py`.
5. **Tests.** Create `tests/test_guestbook_api.py` with a `client(tmp_path)` fixture (`create_app(db_path=str(tmp_path / "test.sqlite3")).test_client()`) and a `post(client, body)` helper, with the classes in the Verification section. Advances AC1–AC7. This step *is* the `package-api` layer addition.
6. **README.** Append a `## Guestbook API` section to `README.md` after line 97 covering: both endpoints with one `curl` example each, the success and error envelopes, `GUESTBOOK_DB_PATH` and its default, `pip install -e .` → `guestbook`, `pytest`, and a one-line note that the dev server has no auth or rate limiting and is for local use. Advances AC7. No test layer covers documentation; state that in the evidence.
7. **Local gate and hygiene check.** Run the Verification commands from a clean temporary worktree; confirm `git status --short` lists only the seven paths in the change surface and that no `CI_FAIL`, `instance/` or `*.sqlite3` file is staged. Then commit once on the checked-out branch with a message that names work item t1 and ends with the session's attribution line. Do not push; do not open a PR.

**Implicit invariants the implement phase must cover.**

- *Authorization and tenancy:* none by design (spec Non-Goals); do not add any.
- *Concurrency and idempotency:* per-call connections; a concurrent-create test; creates are not idempotent and must not be (two identical POSTs produce two entries with distinct ids).
- *Validation and error paths:* every rejected request leaves the table unchanged; a following GET must return the pre-request list. Both fields are validated independently so a request can fail on both at once.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1 | t1 | Guestbook JSON API: Flask service with SQLite storage, validation, tests, and run docs |
| 2 | t1 | same |
| 3 | t1 | same |
| 4 | t1 | same |
| 5 | t1 | same |
| 6 | t1 | same |
| 7 | t1 | same |

`work-items.md` holds exactly one work item; every step maps to it. No planning gap.

## Verification and CI gate

**Canonical gate** (`.factory/testing.md:3`, `.github/workflows/ci.yml:21-24`), in order, from a clean temporary worktree at the committed SHA:

```bash
git worktree add /tmp/play1-verify <sha>
cd /tmp/play1-verify
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest
```

Then, in the same worktree:

```bash
pytest tests/test_guestbook_api.py -v
pip list --format=freeze | grep -i -E 'flask|werkzeug|jinja2|markupsafe|itsdangerous|click|blinker'
GUESTBOOK_DB_PATH=/tmp/play1-verify-gb.sqlite3 guestbook &   # Ctrl-C / kill after the curls
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' \
  -d '{"author":"a","message":"b"}' http://127.0.0.1:5000/api/guestbook/entries
curl -s http://127.0.0.1:5000/api/guestbook/entries
git diff --stat main
git diff main -- pyproject.toml
git status --short
test ! -e CI_FAIL && echo "no CI_FAIL"
```

**What the gate must show.**

- `pytest` green: all 74 existing tests plus every test in `tests/test_guestbook_api.py`, on Python 3.12 in CI and locally (3.14).
- `pip list` shows exactly the seven Flask-family distributions as the only additions beyond `pypdf`, `pytest` and their own dependencies.
- The POST `curl` prints `201`; the GET `curl` prints a one-element array with `id`, `author`, `message`, `created_at`.
- `git diff --stat main` lists exactly: `pyproject.toml`, `README.md`, `src/guestbook/__init__.py`, `src/guestbook/validation.py`, `src/guestbook/storage.py`, `src/guestbook/app.py`, `tests/test_guestbook_api.py`. `git diff main -- pyproject.toml` shows two added fragments and nothing removed.
- No `CI_FAIL`, no `instance/` or `.sqlite3` file in `git status`.

**Required test content in `tests/test_guestbook_api.py`** (layer `package-api`, production-path, runs in a pod and in CI):

| Class | Covers | AC |
| --- | --- | --- |
| `TestCreateEntry` | 201 with exactly the four keys; `created_at` ends with `Z` and parses with `%Y-%m-%dT%H:%M:%S.%fZ`; returned values are stripped; client-supplied `created_at` and `id` ignored; exactly 50 / 300 characters accepted; Hebrew and emoji counted as code points (a 50-character Hebrew author is accepted) | AC1 |
| `TestCreateValidation` | `parametrize` over each field × {missing, `None`, integer, `""`, `"   "`, limit+1 characters} → 400 `validation_error`, `fields` has exactly the failing key(s); both fields failing together lists both; a following GET returns `[]` | AC2 |
| `TestInvalidJson` | `data="not json"`, body `[]`, body `null`, empty body → 400 `invalid_json`, no `fields` key; following GET returns `[]` | AC2 |
| `TestListEntries` | empty DB → 200 `[]`; after two creates every element has the four keys and equals the POST response; `id` descending; two consecutive GETs are identical | AC3, AC4, AC5 |
| `TestNoPagination` | 100 POSTs → GET returns 100; `id` list strictly decreasing; ordering stable across two GETs | AC4, AC6 |
| `TestAppSetup` | DB file created at the given path including a missing parent directory; `GUESTBOOK_DB_PATH` (monkeypatch) honoured when no argument is passed; 20 concurrent POSTs from a `ThreadPoolExecutor` (one `test_client()` per thread) → GET returns 20 unique ids | AC7, work-item threaded-safety AC |

**Layers that cannot run in a pod:** none. The repository declares one layer and it runs unprivileged. Black-box QA of the running server is not instrumented (no `.factory/runbook.md`); the `curl` checks above are the manual stand-in and must be recorded as such, not as an automated layer.

**CI configuration:** unchanged. The existing workflow already installs `.[test]` and runs `pytest`; adding `flask` to `dependencies` is enough. `.factory/testing.md` is not edited because the gate command does not change. No `.factory/delivery-assets` entry: no binary is added.

## Risks and scope guards

| Risk | Mitigation |
| --- | --- |
| **Contract drift after merge** breaks s2/s3 in flight | Paths, keys, status codes, envelope and `created_at` format are listed under Contracts; tests pin each of them; reviewers reject any post-merge change to them. |
| **`database is locked` in the concurrent test** | Per-call connections verified at 100 concurrent inserts; if it still appears, add `timeout=5` to `sqlite3.connect` before considering any other strategy. |
| **Werkzeug 3 returns an HTML 415 page** for non-JSON content types | `get_json(silent=True, force=True)`; `TestInvalidJson` guards the behaviour. |
| **Python version drift** (local 3.14, CI 3.12, floor 3.10) | Use `timezone.utc`, not `datetime.UTC`; no `match`, no `ExceptionGroup`, no 3.11+ syntax; do not reference `flask.__version__`. |
| **Database file written into the source tree** | DB path is CWD-relative `instance/` (ignored) and tests always pass `tmp_path`; the hygiene check in step 7 fails on any staged `.sqlite3`. |
| **Non-ASCII escaped in JSON (`ensure_ascii=True`)** | Valid JSON; s2 decodes it. Do not change the JSON provider in this story. |
| **Stale narrative numbers** (the injected plan text says 38 existing tests) | The real count is 74; the gate expectation above uses 74. |
| **No automated check for the README** | Reviewer reads the section against the Contracts table. |

**The implement phase must NOT:**

- Touch `src/testbed_utils/**`, any existing `tests/test_*.py`, `tests/fixtures/**`, `.github/workflows/ci.yml`, `.factory/**`, `.gitignore`, `docs/**` outside this plan folder, or the package `name`/`version` in `pyproject.toml`.
- Create `CI_FAIL`, commit an `instance/` directory or any `.sqlite3` file, or add a dependency other than `flask>=3`.
- Add DELETE, HTML templates, static files, pagination, authentication, sessions, rate limiting, CORS, migrations, logging frameworks or a `Blueprint`.
- Weaken the gate: no `pytest` markers that skip the new tests, no `-k` subsets, no `|| true`, no edits to `.factory/testing.md`.
- Push, open a pull request, or switch branches; stop at one local commit on the checked-out branch.

## Clarification outcomes

None. Both open questions in spec §8 (whitespace-only input, error message format) are settled by `hld.md` §5 and the work-item acceptance criteria, as recorded under Resolved unknowns. No `plan-questions.json` is written.
