# Work-item breakdown — QA-20261108-S5 Build the newsletter banner as static HTML

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | QA-20261108-S5 Build the newsletter banner as static HTML (qa/s5-banner.html) |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "QA-20261108-S5 Build the newsletter banner as static HTML (qa/s5-banner.html)",
    "summary": "**Intent:** add one self-contained static page that rebuilds the approved PLAY-160 Acme home page, with the newsletter sign-up banner directly under the hero heading. This is the single deliverable of PLAY-161; play1 is the only target repo.\n\n**Owns:** `qa/s5-banner.html` (new).\n\n**Consumes (read-only, never merged or checked out):** the PLAY-160 design at `stories/PLAY-160/design/screens/`, commit `066dff3`, identical screens to `ee6192d`:\n- `home-page-banner-default.default.html`\n- the `*.mobile.html` variants\n- `tokens.css`\n\n**Must not touch:** `tests/`, `CHANGELOG.md`, `.github/`, `pyproject.toml`, any other file. No `CI_FAIL` file.\n\n**Acceptance criteria:**\n1. Opening `qa/s5-banner.html` in a browser shows, in order:\n   - a dark-blue top bar with the \"Acme\" wordmark and nav Home, Products, About, Contact\n   - the hero heading \"Welcome to Acme\", then the newsletter banner, then the tagline \"Tools that make your day simpler.\" and an orange \"Shop now\" button\n   - three cards: \"Fast delivery / Orders ship in 24 hours.\", \"Free returns / 30 days, no questions.\", \"Support / We answer within an hour.\"\n   - the footer \"© 2026 Acme Inc.\"\n2. Banner content:\n   - an element with the accessible name \"Newsletter sign-up\"\n   - an email input whose accessible label is \"Email address\" (visually hidden) and whose helper text is \"Your email address\"\n   - a button labelled \"Subscribe\"\n   - no other banner text\n3. Banner styling: max-width 520px, background #eef2ff, border #c7d2fe, Subscribe button #1e3a8a. Side by side with the approved PLAY-160 desktop screens, the page and banner look the same, with no dark review strip.\n4. On first load the email field is empty and shows only the neutral helper text. No preset value, no reader@example.com, no real address anywhere in the file.\n5. Typing an address and then clicking Subscribe or pressing Enter does nothing visible or external:\n   - no reload, no navigation, no network request\n   - no success, error, confirmation or invalid-email message\n   - the typed text stays in the field\n   - the same holds with an empty field\n   - the file contains no `<form>`, no `action` and no `<script>`\n6. At a viewport of about 375–390px the page matches the approved PLAY-160 phone screens:\n   - heading at 32px\n   - compact top bar\n   - email field stacked above a full-width Subscribe button\n   - feature cards in one column\n   - desktop layout remains fluid\n7. All styling is inline in the file. The browser's network panel shows no request beyond the HTML file itself: no external or local stylesheet, font, script, library or image. Fonts are Helvetica, Arial, sans-serif.\n8. The file is well under 300 lines.\n9. The PR's only code change is the new `qa/s5-banner.html`. Plan documents under `stories/PLAY-161/` are excluded from this judgement.\n10. The PR description references PLAY-161 and the epic PRD \"QA-20261108-S5 newsletter banner\" (Confluence page 33128450). Any deviation from the design is named in the PR summary.\n11. The existing CI passes unchanged: `pytest` green with the test job under 60 seconds, and the gate job green.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
