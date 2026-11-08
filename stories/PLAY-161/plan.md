# PLAY-161 — Implementation plan: newsletter banner as static HTML

## Context

PLAY-161 adds one self-contained static page, `qa/s5-banner.html` (new), to `roeeoz/play1`. The page rebuilds the approved PLAY-160 design: the Acme home page with a newsletter sign-up banner (email field plus `Subscribe`) directly under the hero heading "Welcome to Acme". The acceptance criteria require five things. The banner must show under the heading and look like the design (AC1). Subscribe and Enter must do nothing: no message, nothing stored or sent (AC2). The field must open empty, with neutral helper text only (AC3). The page must load nothing external (AC4). The PR must add only that one file and cite PLAY-161 and the epic PRD (AC5). Existing CI must stay green in under 60s (AC6). The change lands on the work branch `halo/feat/play-161-20261108-063753`, which merges into `main`. `spec.md` (the requirement), `hld.md` (the design) and `work-items.md` (one work item, `t1`) are in the same folder as this file, `stories/PLAY-161/`.

## Research findings

**Change surface**
- `qa/` holds two shell helpers, `qa/s3-a.sh` and `qa/s3-hello.sh`. It has no HTML file. `qa/s5-banner.html` is new.
- The product has no web UI and no HTML, CSS, theme or component library. The only `*.html` files in the repo are other initiatives' design artefacts under `stories/*/design/`. The spec (§2) and PRD (§7) exclude those as sources.
- `src/guestbook/` is a Flask JSON API with no templates, so no existing component or layout shell applies.

**Gate and tests**
- `.factory/testing.md` declares one required layer, `package-api`: the command is `pytest`, run by `canonical-gate`. There is no linter, formatter or type checker.
- The test job in `.github/workflows/ci.yml:23-24` runs `pytest` with `timeout-minutes: 5` (`ci.yml:15`).
- The `gate` job (`ci.yml:32-38`) fails only when `CI_FAIL` exists at the repo root.
- `pyproject.toml:27` sets `testpaths = ["tests"]`, so `qa/` is never collected.
- No test in `tests/` references `qa/` HTML or globs `*.html`. `tests/test_qa_s3_greeting.py` and `tests/test_hello_sh.py` test the shell helpers only.
- Adding the HTML file therefore cannot change which tests run or how long they take.

**Design source** (read-only copy at `/halo-out/design-reference/PLAY-160/`, commit `066dff3`)
- The markup basis is `screens/home-page-banner-default.default.html`. It has:
  - a top bar with the `Acme` wordmark and the nav `Home`/`Products`/`About`/`Contact` (no `href`)
  - the hero `h1`, then `div.banner[role=group][aria-label="Newsletter sign-up"]`, then the tagline and `a.cta` "Shop now"
  - three `.card`s and the `footer`
- The banner's controls are:
  - a `label.vh` "Email address" bound to `input#newsletter-email` (`type="email"`, `autocomplete="off"`, `placeholder="Your email address"`)
  - `button type="button"` "Subscribe"
- The `.mobile.html` variants differ only in `body class="mobile"`, the title and the review strip.
- The email-typed and after-Subscribe screens add `value="reader@example.com" class="is-focus"` (`home-page-banner-email-typed.default.html:20`). They are state pictures, not markup to copy.
- `screens/tokens.css` holds:
  - the page and banner tokens (`:root`)
  - the review-strip rules (`tokens.css:39`), which are not part of the design
  - the banner rules (`tokens.css:60-68`), including the `.is-focus` simulation classes (`:64`, `:67`)
  - the phone overrides scoped to `body.mobile` (`tokens.css:71` onward)
- `screens/index.html` says what changes from today: only the banner between the heading and the tagline. Mobile is derived from the desktop screenshot.

**Screen sources (structure inventory)**
- All three screens (banner default, email typed, after Subscribe) are based on the attached screenshot `QA-20261108-S5-home-page`, with the banner marked `new`.
- No checkout renders the home page (structure.md; PRD §5, §8). The real home page is outside this story's repositories and is not changed. The static page is the agreed stand-in (PRD §7, spec §1).

**External data:** none.

**Remaining unknowns**
- Pixel fidelity has no automated check. It is judged by eye, side by side (spec §8).

## Locked decisions and assumptions

**Locked decisions**
- Exactly one new file, `qa/s5-banner.html`, with no other code change. Source: spec FR7 and AC5; `work-items.md` `t1` "Must not touch".
- No `<form>`, no `action`, no `<script>`. The button is `type="button"`. Source: spec §7, FR4; hld §3, §6; design build hints in `screens/index.html`.
- No preset value and no `reader@example.com`. The placeholder is "Your email address". Source: spec FR3; PRD R5; hld §6.
- All styles go in an inline `<style>` block, with system fonts `Helvetica, Arial, sans-serif` and no external or local stylesheet. Source: spec FR6; hld §2, §6.
- The design's CSS custom properties are kept as variables. The review strip and `.is-focus` classes are dropped, and real `:focus`/`:focus-visible` rules are used instead. Source: hld §6.
- Phone layout is one `@media (max-width: 480px)` block that carries the `body.mobile` values. Desktop stays fluid and the banner is capped at 520px. Source: hld §6; spec FR5.
- The banner's content, accessible names and colours are fixed: `#eef2ff`, `#c7d2fe` and `#1e3a8a`. Source: spec FR2; hld §4.
- Nav links and Shop now have no `href`. Source: hld §6; design.
- No test, CHANGELOG entry, CI change or `pyproject.toml` change. Source: spec §2; hld §6 (rejects the PLAY-114 precedent).
- The PR body cites PLAY-161 and the epic PRD (Confluence page 33128450), and names every deviation from the design. Source: AC5; `t1` AC10.

**Assumptions**
- *The design's own values are the product look.* Evidence: play1 has no theme, components or styles to build the page from. Consequence if wrong: if the "never copy tokens.css" rule must win, there is no product look to fall back on, so the page could not be built at all. hld §6 already settles this.
- *AC5's "no other file changed" is judged on the code change, excluding the platform-committed `stories/PLAY-161/*.md`.* Evidence: hld §7; `t1` AC9. Consequence if wrong: the PR would show plan documents as extra files. The platform owns those commits, and this stage cannot remove them.
- *The 480px breakpoint is acceptable.* Evidence: hld §6; the design targets 375–390px. Consequence if wrong: only the breakpoint value changes.

## Solution proposal

**Approach.** Write `qa/s5-banner.html` as one HTML5 document (`lang="en"`, `charset utf-8`, `viewport` meta) whose body follows the default-state design screen.

Put one inline `<style>` block in `<head>`, built from `tokens.css` with these changes:
- Keep the `:root` tokens and the existing-page rules (top bar, hero, CTA, features, cards, footer).
- Keep the banner rules, with `.is-focus` removed from the selectors so only `:focus` and `:focus-visible` remain.
- Keep the `.vh` visually-hidden rule.
- Turn every `body.mobile X` rule into `X` inside `@media (max-width: 480px)`. Drop `body.mobile { max-width: 390px }`, because on a real phone the viewport is the width.
- Drop the review-strip rules.

**Covering the three designed states without a script**
- The *default* state is the markup as written.
- The *email typed* state is the browser's normal text entry, with the `:focus` outline in `--c-focus`.
- The *after Subscribe* state, with typed text or with an empty field, follows from having no `<form>` and a `type="button"` button. Pressing it does nothing, and Enter has no form to submit. The text stays, nothing reloads, no validation message fires, and there is no network request.

So all four designed state pages (desktop and mobile) come from one static document, and none needs extra markup.

**Key decisions**
- Base the page on the default screen, never the typed screens, so no address enters the file.
- Keep the tokens as CSS variables so a reviewer can diff the page against `tokens.css`.
- The page is about 110–130 lines, well under the 300-line G3 limit.

**Alternatives rejected**
- A separate CSS file breaks the one-file rule (AC5) and adds a local request (AC4).
- `<form>` with JS `preventDefault`: JS is out of scope (spec §7).
- `<form>` without `action`: it submits to itself, reloads and clears the field, which breaks FR4.
- Hard-coded literal values: equivalent in effect, but harder to review.
- Adding a pytest content check: forbidden by AC5/spec §2. No HTML test layer exists, and inventing one is out of scope.

**Deviations from the design to name in the PR:** two.
- The mobile layout is a media query, not a separate `body.mobile` page.
- The review strip and the `.is-focus` simulation classes are omitted.

## Ordered implementation steps

1. **Create the document shell.** Add `qa/s5-banner.html` with doctype, `lang="en"`, `meta charset`, the `viewport` meta and the title "Acme — Home". Add no `<link>`, `<script>`, `<img>` or `@import`.
   - Advances: AC4, AC5.
   - Test layer: none exists for HTML. Verified by manual check (Verification §).
2. **Inline the styles.** In a `<style>` block, carry over:
   - the `:root` tokens and existing-page rules from `tokens.css`
   - the banner rules with `.is-focus` removed
   - the `.vh` rule
   - an `@media (max-width: 480px)` block mapped from the `body.mobile` overrides: top bar 56px with 16px padding, wordmark 20px, nav gap 12px at 14px, hero padding 40px 16px, `h1` 32px, banner as a column with 12px padding and a full-width button, features in one column with 16px gap and padding, footer `16px 16px 80px`

   Leave out the `.review` rules.
   - Designed screens: all three screens, desktop and mobile. Based on the screenshot `QA-20261108-S5-home-page`; the banner is `new`.
   - Advances: AC1, AC4.
   - Test layer: manual side-by-side check.
3. **Write the body markup** in this order:
   - `header.topbar`: wordmark `Acme`; `nav[aria-label="Main"]` with `Home`/`Products`/`About`/`Contact` as `<a>` without `href`
   - `main`, containing `section.hero` with `h1` "Welcome to Acme" and then the banner (`div.banner[role=group][aria-label="Newsletter sign-up"]`, `label.vh[for=newsletter-email]` "Email address", the `input` attributes listed above with no `value`, and `button type="button"` "Subscribe"), then `p.tagline` "Tools that make your day simpler." and `a.cta` "Shop now"
   - `section.features` with the three cards, using the exact titles and lines from the design
   - `footer` "© 2026 Acme Inc."

   Add no other banner text, no `<form>` and no `action`.
   - Designed screens and states: *Home page — banner, default* (empty field); *banner, email typed* (native typing plus `:focus`); *after Subscribe*, both default and empty (inert button). Desktop and mobile throughout. Based on the screenshot; the banner is `new`.
   - Advances: AC1, AC2, AC3.
   - Test layer: manual browser check.
4. **Check the invariants by search.**
   - Searching for `<form`, `action=`, `<script`, `<link`, `@import`, `url(`, `src=`, `http`, `value=` and `@` (apart from `@media`) must find no matches.
   - `wc -l` must be under 300.
   - `git diff --name-only main...HEAD` must list only `qa/s5-banner.html` plus the platform's `stories/PLAY-161/*.md`.
   - Advances: AC2, AC3, AC4, AC5.
   - Test layer: none exists. These are review checks, recorded in the PR.
5. **Run the canonical gate.** Run `pip install -e ".[test]"`, then `pytest` from the repo root. Confirm `CI_FAIL` does not exist.
   - Advances: AC6.
   - Test layer: `package-api` (existing).
6. **PR description** (the platform opens the PR; the build supplies the summary). It must:
   - cite PLAY-161 and the epic PRD "QA-20261108-S5 newsletter banner" (Confluence page 33128450)
   - name the two design deviations from the Solution proposal
   - state that the real home page lives in no checkout and was not changed
   - Advances: AC5.
   - Test layer: none; reviewed.

**Invariant classes**
- Authorization and tenancy: not applicable, because there is no server or data.
- Concurrency and idempotency: not applicable.
- Validation and error paths: by design there is no validation UI. `type="email"` constraint validation never fires because nothing submits (FR4).
- PII: no address appears in the file (R5).

**Dependencies and generated files**
- Dependencies: the gate's only install is `pip install -e ".[test]"` from PyPI. The page itself has none.
- Generated deliverables: none. No binary is added, so there is no `.factory/delivery-assets` obligation.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1–6 | `t1` — QA-20261108-S5 Build the newsletter banner as static HTML (qa/s5-banner.html) |

`t1` is the only work item, and every step maps to it.

## Verification and CI gate

**Canonical gate (`.factory/testing.md`)**
- Run `pip install -e ".[test]"`, then `pytest`, from the repo root. Run it once locally on the committed SHA.
- The provider run of `.github/workflows/ci.yml` at the exact head is authoritative for the `package-api` layer. It runs unprivileged, so it can also run in a pod.
- The `gate` job must be green, which means no `CI_FAIL` at the root.
- No provider CI configuration change is needed. `.factory/delivery-assets` does not apply.

**What the gate must show**
- `pytest` passes, with the same tests as `main` and nothing new collected.
- The `test` job finishes in under 60 seconds.
- `gate` is green.

**Manual checks, recorded in the PR** (the gate cannot prove these; there is no HTML or visual test layer)
- Open `qa/s5-banner.html` from disk at desktop width and at about 390px. Compare it side by side with `home-page-banner-default.default.html` and its `.mobile` variant (AC1).
- Type an address, click Subscribe, then press Enter. Nothing changes and the text stays. Repeat with an empty field (AC2).
- On first load the field shows only "Your email address" (AC3).
- The DevTools network panel shows only the HTML document (AC4).
- The search and line-count checks from step 4 pass.

## Risks and scope guards

**Risks**
- *Copying a state screen's markup* would bring in `reader@example.com` or `.is-focus`, which breaks R5. Mitigation: use only the default screen, and run the `value=` and `@` search in step 4.
- *A `<form>` or link to `tokens.css` added out of habit* would cause a reload or an external request, which breaks AC2 and AC4. Mitigation: the step-4 search.
- *Visual drift (RK2)* has no automated detection. Mitigation: keep the design's tokens verbatim as variables, and do the manual side-by-side check at both widths.
- *Plan documents appear in the PR diff.* This is platform-owned and noted against AC5 (assumption above).

**Scope guards.** The implement phase must NOT:
- touch `tests/`, `CHANGELOG.md`, `.github/`, `pyproject.toml`, `README.md`, `src/` or the existing `qa/*.sh`
- create `CI_FAIL` or any extra file (CSS, image, test)
- add JavaScript, a `<form>`, `action`, an external font or a library
- add a success, error or invalid-email message, or any banner copy beyond the field and `Subscribe`
- give nav or Shop now link targets
- copy the review strip
- edit or commit the design copy, or check out or fetch the PLAY-160 branch
- edit `spec.md`, `hld.md` or `work-items.md`
- delete, skip or weaken any check. A failing `pytest` is reported blocked, never bypassed.

## Clarification outcomes

None.
