# Implementation Plan — Guestbook Page (s2, work item t1)

> CANARY-PLAN-TOP-3K: the POST handler logs the new entry id at INFO.


## Context

play1 has a working guestbook JSON API (s1, merged) but no browser-facing page. This plan adds a server-rendered HTML page at `GET /guestbook` that displays all entries newest-first with relative timestamps, a submission form that creates entries via `POST /guestbook` (POST-redirect-GET), and validation feedback for empty/whitespace-only fields. This is the first HTML template in the project.

## Approach

All work belongs to a single work item (t1). The implementation order is: (1) create the Jinja2 template, (2) add the two new routes to `app.py`, (3) write the test suite. The routes reuse the existing `storage.list_entries`, `storage.insert_entry`, `validation.validate_entry`, and `testbed_utils.dateutils.humanize_delta` without modification. The POST handler follows the POST-redirect-GET pattern — no JavaScript needed. Embedded CSS in the template avoids creating a `static/` directory.

## Steps

### Step 1 — Create the Jinja2 template

**Work item:** t1  
**Creates:** `src/guestbook/templates/guestbook.html`

Create the `templates/` directory under `src/guestbook/` and add `guestbook.html` with:

- Standard HTML5 document structure with `<meta charset="utf-8">` and a page title (e.g. "Guestbook").
- An embedded `<style>` block with basic layout/typography styles for the page, form, and entry list.
- A **submission form** (`<form method="post" action="/guestbook">`) containing:
  - A text input for `name` (with `required` attribute, `maxlength="50"`, labeled "Name").
  - A textarea for `message` (with `required` attribute, `maxlength="300"`, labeled "Message").
  - A submit button.
- A **validation error area**: if the template variable `errors` is non-empty, render each field error in a visible element (e.g. `<p class="error">`).
- An **entry list section**:
  - If entries list is empty: render a `<p>` with text "No comments yet."
  - Otherwise: for each entry, render a container element (e.g. `<article>` or `<div>`) with `data-entry-id="{{ entry.id }}"` containing:
    - Author name in a `<strong>` or similar element.
    - Relative timestamp (pre-computed string passed from the handler) in a `<time>` or `<span>` element.
    - Message text in a `<p>` element.
- Use standard Jinja2 `{{ variable }}` syntax (no `| safe` filter) — Jinja2 autoescaping on `.html` files prevents XSS.
- If `errors` is present, pre-fill form fields with `form_data.name` / `form_data.message` so the visitor doesn't lose their input on validation failure.

### Step 2 — Add page routes to `app.py`

**Work item:** t1  
**Edits:** `src/guestbook/app.py`

Inside `create_app()`, after the existing API routes, add:

**New imports** (at the top of the file):
- `from flask import render_template, request, redirect` (some may already be imported — add only what's missing).
- `from datetime import datetime, timezone` (may partially exist).
- `from testbed_utils.dateutils import humanize_delta`.

**`GET /guestbook` route:**
1. Call `storage.list_entries(db_path)` to get all entries.
2. For each entry, parse `entry["created_at"]` using `datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")` and attach `timezone.utc`.
3. Compute `delta = created_dt - datetime.now(timezone.utc)` (negative timedelta → `humanize_delta` produces "X ago" suffix).
4. Add a `relative_time` key to each entry dict with the `humanize_delta(delta)` result.
5. Return `render_template("guestbook.html", entries=entries, errors={}, form_data={})`.

**`POST /guestbook` route:**
1. Extract `author = request.form.get("name", "")` and `message = request.form.get("message", "")`.
2. Call `validate_entry({"author": author, "message": message})`.
3. If validation fails (errors dict is non-empty): fetch entries via `list_entries`, compute relative times (same logic as GET), and return `render_template("guestbook.html", entries=entries, errors=errors, form_data={"name": author, "message": message})` with status 200.
4. If validation succeeds: call `insert_entry(db_path, validated_entry["author"], validated_entry["message"], _utc_now_iso())` (reuse the existing private `_utc_now_iso()` helper since it's in the same module), then return `redirect("/guestbook", code=302)`.

Note: The redirect after successful POST means the subsequent GET renders the form with empty fields (AC6 — form reset).

### Step 3 — Write the test suite

**Work item:** t1  
**Creates:** `tests/test_guestbook_page.py`

Follow the existing test conventions from `test_guestbook_api.py`: pytest, class-based grouping, local fixtures (`db_path`, `app`, `client`), plain `assert` statements.

Define fixtures:
- `db_path` — uses `tmp_path`.
- `app` — calls `create_app(db_path=str(db_path))`.
- `client` — calls `app.test_client()`.
- A helper function to insert entries directly via `storage.insert_entry` for test setup.

**Test classes and cases:**

`TestGuestbookPageDisplay` (AC1, AC2, AC8):
- `test_get_shows_entries_newest_first` — Insert two entries with different timestamps, GET `/guestbook`, assert 200, assert both author names and messages appear in the HTML, assert the newer entry appears before the older one in the response body.
- `test_entry_displays_relative_time` — Insert an entry with a known `created_at`, freeze or mock `datetime.now` if needed, GET `/guestbook`, assert the response contains a relative time string (e.g. check for "ago" or a specific `humanize_delta` output).
- `test_empty_state_shows_message` — GET `/guestbook` with no entries, assert 200, assert response contains "No comments yet".
- `test_entries_have_data_entry_id` — Insert an entry, GET `/guestbook`, assert response contains `data-entry-id="{id}"` for the entry's id.

`TestGuestbookPageForm` (AC3, AC6):
- `test_form_present` — GET `/guestbook`, assert response contains a `<form` element, an input with `name="name"`, an input/textarea with `name="message"`, and a submit element.
- `test_form_cleared_after_success` — POST valid data, follow the redirect, assert the form fields in the response HTML do not contain the submitted values.

`TestGuestbookPageSubmission` (AC4, AC5):
- `test_post_valid_creates_entry_and_redirects` — POST with valid name and message, assert 302 redirect to `/guestbook`. Follow redirect, assert the new entry's author and message appear in the HTML.
- `test_post_empty_name_shows_error` — POST with empty name, assert 200 (not redirect), assert error message in HTML, assert no entry was created (list_entries returns empty).
- `test_post_empty_message_shows_error` — POST with empty message, same assertions.
- `test_post_whitespace_only_blocked` — POST with whitespace-only name or message, assert no entry created, error shown.

`TestGuestbookPageSecurity` (AC7, AC9):
- `test_xss_in_author_escaped` — Insert an entry with `author="<script>alert(1)</script>"`, GET `/guestbook`, assert the literal `<script>` tag does NOT appear in the response (it should be escaped as `&lt;script&gt;`).
- `test_xss_in_message_escaped` — Same test for the message field.
- `test_no_delete_functionality` — GET `/guestbook`, assert response does not contain a delete button/link/form.

### Step 4 — Run the test gate

Run `pytest` from the repo root. All existing tests (s1 API tests) and all new page tests must pass. Fix any failures before proceeding.

## Verification

| AC | Verified by |
|---|---|
| AC1 — entries displayed newest-first with relative time | `test_get_shows_entries_newest_first`, `test_entry_displays_relative_time` |
| AC2 — empty state message | `test_empty_state_shows_message` |
| AC3 — form with name, message, submit | `test_form_present` |
| AC4 — valid POST creates entry, appears at top | `test_post_valid_creates_entry_and_redirects` |
| AC5 — empty/whitespace POST blocked with error | `test_post_empty_name_shows_error`, `test_post_empty_message_shows_error`, `test_post_whitespace_only_blocked` |
| AC6 — form reset after success | `test_form_cleared_after_success` |
| AC7 — XSS safety | `test_xss_in_author_escaped`, `test_xss_in_message_escaped` |
| AC8 — `data-entry-id` on each entry | `test_entries_have_data_entry_id` |
| AC9 — no delete functionality | `test_no_delete_functionality` |

Final gate: `pytest` passes all tests (existing + new).

## Risks & Open Points

1. **`insert_entry` signature:** The research confirms `insert_entry(db_path, author, message, created_at)` takes four arguments — the caller must supply the timestamp. The POST handler should reuse the existing `_utc_now_iso()` helper from `app.py` (same module, so the private function is accessible). If the function signature has changed since research, adjust accordingly.

2. **`validate_entry` input shape:** The research shows `validate_entry` expects `{"author": ..., "message": ...}`. The HTML form uses `name="name"` for the author field (matching the user-facing label). The POST handler must map `request.form["name"]` → `payload["author"]` when calling `validate_entry`.

3. **Relative-time sign convention:** `humanize_delta` appends "ago" for negative deltas. The handler must compute `created_dt - now` (not `now - created_dt`) to get a negative delta. Verify with a quick test if unsure.

4. **s3 merge conflict (low risk):** Both s2 and s3 add routes to `create_app()`. Since the routes are additive and at different URL paths, git merge should resolve automatically. The `data-entry-id` contract ensures s3 can add delete buttons without touching s2's template structure.
