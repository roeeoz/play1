# Feature Specification Document

## 1. Feature Overview

**Summary:** A guestbook page for play1 that displays all guestbook entries (newest first) and allows anonymous visitors to post new entries via an inline form. Built on top of the guestbook JSON API delivered in story s1.

**Problem statement:** play1 has a functional guestbook API (s1, merged) but no user-facing page to interact with it. Visitors currently have no way to read or post guestbook entries through a browser.

**Target users / actors:** Anonymous visitor — any person who navigates to the guestbook page in their browser. No authentication, no accounts, no roles.

---

## 2. Goals & Non-Goals

### Goals
- Allow visitors to browse all guestbook entries in reverse chronological order with human-readable relative timestamps.
- Allow visitors to submit a new guestbook entry (name + message) that appears at the top of the list immediately after submission.
- Provide clear feedback on empty form fields and an informative empty state when no entries exist.

### Non-Goals
- Deleting entries (covered by s3, a separate parallel story).
- User registration or authentication.
- Content moderation (flagging, approval, blocking, reporting).
- Pagination of the entry list.
- Rich text formatting in messages.
- Search, filtering, or sorting controls.
- Real-time updates from other visitors (e.g., live-polling or WebSocket push).

---

## 3. Functional Requirements

- **FR1 — Display entries:** The page fetches all guestbook entries from the API and renders them in newest-first order. Each entry displays three pieces of information: the author's name, the message text, and a relative timestamp indicating how long ago the entry was posted (e.g., "5 minutes ago", "2 hours ago", "3 days ago").

- **FR2 — Empty state:** When no guestbook entries exist, the page displays a human-readable message indicating there are no entries yet (e.g., "No comments yet"), rather than showing a blank area or an error.

- **FR3 — Submission form:** The page includes a form with two input fields — name and message — and a submit action, enabling visitors to compose a new guestbook entry.

- **FR4 — Create entry:** Submitting the form with valid (non-empty) name and message fields creates a new entry via the API. The newly created entry appears at the top of the entry list without requiring the visitor to manually refresh or navigate away from the page.

- **FR5 — Input validation feedback:** Attempting to submit the form with one or both fields empty is prevented. The visitor sees a clarifying indication of what needs to be corrected. No entry is created on the server.

- **FR6 — Form reset after success:** After a successful submission, both the name and message fields in the form are cleared, leaving the form ready for a new entry.

---

## 4. User Experience & Behavior

### Key User Flows

**Flow 1 — Browse the guestbook:**
1. Visitor navigates to the guestbook page.
2. The page loads and displays all entries, with the newest entry at the top.
3. Each entry shows the author's name, message text, and a relative timestamp (e.g., "5 minutes ago").
4. The visitor scrolls down to read older entries.

**Flow 2 — Post a new entry:**
1. Visitor types their name in the name field.
2. Visitor types their message in the message field.
3. Visitor submits the form.
4. The new entry appears at the top of the entry list.
5. The form fields are cleared.

**Flow 3 — Empty field validation:**
1. Visitor leaves one or both form fields empty.
2. Visitor attempts to submit.
3. Submission is blocked; a clarifying message indicates the issue.
4. No entry is created. The entry list is unaffected.

**Flow 4 — Empty guestbook:**
1. Visitor navigates to the guestbook page when no entries have been posted.
2. The page displays a message such as "No comments yet."
3. The submission form is visible and functional.

### States the User Observes
| State | What the visitor sees |
|---|---|
| Loaded with entries | Entry list (newest first) + submission form |
| Loaded, empty | "No comments yet" message + submission form |
| Validation error | Clarifying message on the form; entry list unchanged |
| Post-submission success | New entry at top of list; form fields cleared |

### User-Facing Edge Cases
- **Relative time labels** are computed when the page is rendered. They are not required to update in real time without a page refresh.
- **All entries are displayed** without pagination, regardless of how many exist. This is an accepted product decision from the epic.
- **Whitespace-only input** is treated as empty by the API (which trims input). The form should not allow submission of whitespace-only fields.

---

## 5. Acceptance Criteria

1. **AC1 — Entry display:** Opening the guestbook page displays all entries sorted from newest to oldest. Each entry shows the author's name, the message text, and a relative publish time (e.g., "5 minutes ago").

2. **AC2 — Empty state:** When no entries exist, the page displays a message indicating there are no comments yet. No error is shown.

3. **AC3 — Form presence:** The page displays a submission form with a name field, a message field, and a submit action.

4. **AC4 — Successful submission:** Submitting the form with a non-empty name and non-empty message creates a new entry that appears at the top of the entry list without requiring the visitor to navigate away or manually refresh.

5. **AC5 — Validation blocking:** Submitting the form with an empty (or whitespace-only) name or message field is blocked. A clarifying indication is shown to the visitor. No entry is created.

6. **AC6 — Form reset:** After a successful submission, the name and message fields in the form are cleared.

---

## 6. Dependencies & Constraints (product-level)

- **Depends on s1 (Guestbook API — merged):** The page consumes the `POST /api/guestbook/entries` and `GET /api/guestbook/entries` endpoints. The API contract (field names, sort order, validation rules, error envelope) is frozen per the s1 specification.
- **Parallel with s3 (Delete entry):** s3 is being built in parallel and will add a delete button to entries the visitor posted in the current session. s2 must not include any delete functionality. The entry rendering should use a clear, extensible structure so s3 can add the delete affordance without reworking the entry display.
- **Dependency-light constraint:** The project explicitly requires a dependency-light approach. No additional Python packages or frontend frameworks should be added beyond what the project already uses (Flask, stdlib).
- **Safe content rendering:** User-submitted names and messages are displayed in HTML. The rendering must not allow script injection (XSS). The mechanism is deferred to STRUCTURE, but the product requires that user content is displayed safely.

---

## 7. Technical Design (deferred to STRUCTURE)

The following decisions are deferred to the STRUCTURE stage:
- Template strategy (Jinja2 templates, template directory layout)
- CSS approach (inline styles, embedded stylesheet, external file)
- JavaScript inclusion (vanilla JS for form submission, or pure server-side POST-redirect-GET)
- Route path for the guestbook page
- Relative-time computation (server-side in template, client-side JS, or import from existing `testbed_utils.dateutils.humanize_delta`)
- HTML test strategy (how to verify rendered page content in automated tests)
- Entry HTML structure (considering s3's need to add a delete button)

Technical constraints the product imposes:
- Must consume the existing s1 API contract without modification.
- Relative time must be computed from the `created_at` ISO-8601 UTC timestamp.
- No additional runtime dependencies.

---

## 8. Open Questions

1. **UI language:** The story and epic documentation are written in Hebrew, and the relative-time example uses Hebrew ("לפני 5 דקות"). However, the codebase, API, and existing utilities all use English. This specification assumes the page UI is in English (labels, empty-state message, relative-time strings). If Hebrew is required, the product owner should state this explicitly.
