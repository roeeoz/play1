# Demerzel coding-phase testbed

Fixture content for **deterministic coding-phase testing of the Demerzel agent**
(per `pdlc-infra/docs/plans/coding-phase-testing-plan.md`, option O6). It gives
the agent real branch/PR/push targets, real GitHub Actions CI classification,
and a deterministic fix loop — realism without flakiness.

**There is no shared testbed repo and no default.** Each developer installs this
content into a GitHub repo they control and configures their own access token —
deterministic CI must not fight other users of a shared repo.

## Setup (once per developer)

1. **Pick or create a repo you control** and push this content to it
   (`git push <your-remote> main`). Any personal repo works.
2. **Configure the GitHub PAT** the dev stack uses to clone/push and poll PRs.
   `pdlc-infra/scripts/dev` resolves it from the environment, first match wins:
   `GITHUB_TOKEN`, `GH_TOKEN`, `GH_PAT`, or the `GH_PAT_TOKENS` JSON map
   (typically set in `.env`). The token needs `repo` scope on your test repo.
   There is no default — `dev up` warns when no token resolves, and real-mode
   coding runs will fail to push without one.
3. **Register the repo in your dev stack** (UI → Repos, or `POST /api/repos`
   with the repo URL). `stepctl repos` then shows its id/name — that is the
   value the `--repo` flag takes below.

## What's in here

- `src/testbed_utils/` — a tiny, real Python package (text + date helpers),
  deliberately simple and genuinely extendable. Canned tasks target it.
- `src/guestbook/` — a small Flask JSON API for guestbook entries (see
  [Guestbook API](#guestbook-api)), living alongside `testbed_utils`.
- `tests/` — a small passing pytest suite.
- `.github/workflows/ci.yml` — two jobs, total runtime well under a minute:
  - **test** — installs the package and runs pytest.
  - **gate** — **fails if and only if a file named `CI_FAIL` exists at the
    repo root** ("CI_FAIL marker present — remove it to make CI green");
    green when it is absent.

The gate makes the fix loop deterministic: a task that creates `CI_FAIL` turns
CI genuinely red → the real poller classifies `ci_failed` with real check
output → fix-pr (reason says remove it) → CI green → merge. Real
branch/PR/push, real classification, the full retro-attributed score shape.

## Local development

```bash
pip install -e ".[test]"   # or: uv pip install -e ".[test]"
pytest
```

## Canned tasks

Seed via `stepctl` (plan §O3). API base defaults to `http://localhost:30080/api`.
Replace `<your-test-repo>` with your registered repo's name or id
(`stepctl repos`).

### Task A — deterministic fix loop (the CI_FAIL gimmick)

A T2 task whose implementation makes CI genuinely red, so the real fix loop
runs against a real, coherent failure (plan §7, Recipe 1).

```bash
stepctl seed --state structured --repo <your-test-repo> --items 1 --tier T2 \
  --title "Add a CI_FAIL marker file at the repository root. Create an empty file named exactly CI_FAIL (no extension) at the repo root and commit it. Do not modify any other files."
stepctl implement <wid>          # real coding pod → real branch + PR; gate job goes red
# real poll classifies ci_failed ("CI_FAIL marker present — remove it to make CI green")
# → fix-pr removes CI_FAIL → gate green → merge
stepctl inspect <fid> --langfuse
```

Alternatively, drive the fix step directly against an already-red PR
(a branch containing `CI_FAIL`), per Recipe 1:

```bash
stepctl seed --state in_review --repo <your-test-repo> --pr <red PR url> --suppress-poll
stepctl implement <wid>          # parks in awaitMerge (no pod — idempotent resume)
stepctl fix <wid> --event ci_failed --summary "gate failed: CI_FAIL present" --detail-file ci.txt
stepctl inspect <fid> --langfuse # kpi.attempts + fix-pr scorecard/judge scores on the trace
stepctl merge <wid>              # → implement.final.* + postmortem on the session
```

### Task B — small real feature (function + tests)

A well-specified T2 feature against the package (plan §7, Recipe 3): a real
implement step producing a real branch and PR that should pass CI first try.

```bash
stepctl seed --state structured --repo <your-test-repo> --items 1 --tier T2 \
  --title "Add ordinal(n: int) -> str to src/testbed_utils/textutils.py returning the ordinal string for a non-negative integer: 1 -> '1st', 2 -> '2nd', 3 -> '3rd', 4 -> '4th', 11 -> '11th', 12 -> '12th', 13 -> '13th', 21 -> '21st', 101 -> '101st'. Raise ValueError for negative input. Export it from testbed_utils/__init__.py and add pytest tests in tests/test_textutils.py covering the 1/2/3 suffixes, the 11-13 exceptions, a large number, and the negative-input error."
stepctl implement <wid>          # real coding pod → real branch + PR on the testbed
stepctl inspect <fid> --langfuse
```

## Caveat — what CI_FAIL runs do and do not prove

Per plan §O6: the `CI_FAIL` gimmick tests **CI classification and loop
mechanics, not fix quality**. A one-file-delete fix is trivially "addressed" —
do **not** read fix-judge values from testbed CI_FAIL runs as evidence about
the judge or about real-world fix quality.

## Guestbook API

A small JSON API for guestbook entries — play1's first HTTP surface. It lives
in `src/guestbook/` and depends only on Flask; storage is the stdlib `sqlite3`
module.

### Running it

```bash
pip install -e .
guestbook                  # Flask dev server on http://127.0.0.1:5000
pytest tests/test_guestbook_api.py
```

Entries are stored in a SQLite file. The path comes from the
`GUESTBOOK_DB_PATH` environment variable and defaults to
`instance/guestbook.sqlite3` relative to the working directory (`instance/` is
git-ignored):

```bash
GUESTBOOK_DB_PATH=/tmp/guestbook.sqlite3 guestbook
```

The dev server has no authentication, moderation or rate limiting — it is for
local use only.

### `POST /api/guestbook/entries`

Body: a JSON object with `author` (1–50 characters after trimming) and
`message` (1–300 characters after trimming). Both are required; the stored
values are the trimmed ones. `created_at` is set by the server, so any `id` or
`created_at` sent by the client is ignored.

```bash
curl -s -X POST http://127.0.0.1:5000/api/guestbook/entries \
  -H 'Content-Type: application/json' \
  -d '{"author": "Ada", "message": "Hello there"}'
# 201
# {"author":"Ada","created_at":"2026-10-11T14:03:27.123456Z","id":1,"message":"Hello there"}
```

### `GET /api/guestbook/entries`

Returns 200 and a JSON array of every entry, newest first (by `created_at`
descending, then `id` descending, so the order is absolute and stable across
calls). No pagination; an empty guestbook returns `[]`.

```bash
curl -s http://127.0.0.1:5000/api/guestbook/entries
```

### Error envelope

Both failure modes return 400 with the same shape:

```json
{"error": {"code": "validation_error", "fields": {"author": "is required"}}}
```

- `validation_error` — `fields` lists only the fields that failed, each with a
  human-readable message. A field fails when it is missing, not a string,
  empty or whitespace-only after trimming, or over its length limit.
- `invalid_json` — the body was not a JSON object (malformed, empty, or a
  non-object such as an array or `null`). No `fields` key.

Nothing is stored when a request is rejected.

NOTE: HALO-53 scenario run 2026-10-14
