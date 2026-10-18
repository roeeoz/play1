# High-Level Design — Guestbook Page (s2)

## 1. System Overview

**What is being built:** A server-rendered HTML page that lets anonymous visitors browse and post guestbook entries, consuming the existing JSON API endpoints from s1.

**Problem:** play1 has a functional guestbook API but no browser-facing UI. Visitors cannot read or write entries without crafting raw HTTP requests.

**Key responsibilities:** Render all entries newest-first with relative timestamps; accept new entries via an inline form; provide validation feedback and an empty-state message.

## 2. Architecture Overview

- **Single Flask app** (`src/guestbook/app.py`): The existing `create_app()` factory gains two new routes — a GET for rendering the page and a POST for handling form submissions (POST-redirect-GET pattern). No Blueprints; follows the existing inline-route style.
- **Jinja2 template** (`src/guestbook/templates/guestbook.html`): First template in the project. Contains HTML structure, embedded `<style>` block, entry list, submission form, and empty-state message. Jinja2 autoescape (enabled by default for `.html`) prevents XSS.
- **Relative-time computation:** Server-side, in the route handler. Parses each entry's `created_at` ISO-8601 timestamp, computes the timedelta against UTC now, and passes the result through the existing `testbed_utils.dateutils.humanize_delta` function. Pre-formatted strings are passed to the template.
- **No new dependencies.** Flask (already installed) includes Jinja2. `humanize_delta` is already in `testbed_utils`.

## 3. Data Flow Design

**Browse (GET):**
1. Browser → `GET /guestbook` → route handler
2. Handler calls the storage layer's `list_entries()` (same function the API uses)
3. Handler parses `created_at` strings, computes relative time via `humanize_delta`
4. Handler passes enriched entries to `render_template('guestbook.html', ...)`
5. Jinja2 renders HTML → 200 response to browser

**Post (POST):**
1. Browser submits form → `POST /guestbook` → route handler
2. Handler validates name/message (non-empty, within length limits after stripping whitespace)
3. On validation failure: re-renders the page with error messages and the existing entries (no redirect)
4. On success: calls `insert_entry()`, then redirects (302) to `GET /guestbook` (PRG pattern)
5. Browser follows redirect → fresh GET renders updated list with the new entry at top

All processing is synchronous. No events, queues, or async flows.

## 4. Component Breakdown

| Component | Responsibility | Repository |
|---|---|---|
| Page route handler (`app.py`) | GET: fetch entries, compute relative times, render template. POST: validate form input, create entry, redirect or re-render with errors. | roeeoz/play1 |
| Guestbook template (`templates/guestbook.html`) | HTML layout: entry list (per-entry container with `data-entry-id` for s3 extensibility), submission form, empty-state message, embedded CSS. | roeeoz/play1 |
| Page tests (`tests/test_guestbook_page.py`) | Verify all six acceptance criteria via Flask test client HTML assertions. | roeeoz/play1 |

Existing components consumed without modification: `storage.py` (list/insert), `validation.py` (validate_entry), `testbed_utils.dateutils.humanize_delta`.

## 5. Interface Contracts

**New routes (consumed by browser, not by other services):**
- `GET /guestbook` → 200 with rendered HTML
- `POST /guestbook` → 302 redirect to `/guestbook` on success; 200 with re-rendered HTML (including error messages) on validation failure

**Consumed API contract (s1, frozen):**
- Entry shape: `{id: int, author: str, message: str, created_at: str}`
- Timestamp format: `%Y-%m-%dT%H:%M:%S.%fZ`
- Storage functions: `list_entries(db_path)`, `insert_entry(db_path, author, message)`

**s3 extensibility contract:**
- Each entry rendered inside a distinct container element with `data-entry-id` attribute carrying the entry's `id`. s3 can attach a delete button inside this container.

## 6. Key Technical Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Form submission | POST-redirect-GET (no JS) | Simplest; "without manual refresh" is satisfied by automatic redirect. No JS dependency. |
| CSS | Embedded `<style>` in template | No existing `static/` directory; keeps the feature self-contained in one template file. |
| Relative time | Server-side via `humanize_delta` | Reuses existing utility; keeps template logic-free; spec does not require live-updating times. |
| Timestamp parsing | `datetime.strptime` with known format | Safe across Python 3.10+ (avoids `fromisoformat` trailing-Z issue on 3.10). |
| Route path | `/guestbook` | Natural, concise, matches the feature name. |
| UI language | English | Codebase and all utilities are English; spec notes this assumption. |

## 7. Risks & Constraints

- **s3 parallel merge risk (low):** s2 and s3 both touch `app.py` (s2 adds page routes, s3 adds delete endpoint). Mitigated by s3 depending on s1 not s2 — the routes are additive and touch different URL paths. Entry HTML uses `data-entry-id` so s3 can add a delete button without reworking markup.
- **First template in project (low):** No existing template patterns to follow, but Flask's conventions are well-defined and the template directory auto-resolves from the app's `root_path`.
- **No pagination (accepted):** All entries rendered on every page load. Accepted product decision; no mitigation needed for s2.
