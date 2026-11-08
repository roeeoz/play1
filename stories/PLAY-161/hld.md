# PLAY-161 — High-Level Design: newsletter banner as static HTML

## 1. System overview
- **What is built:** one self-contained static page, `qa/s5-banner.html`, in `roeeoz/play1`. It shows the approved PLAY-160 design: the existing Acme home page with a newsletter sign-up banner (email field + `Subscribe`) directly under the hero heading.
- **Problem:** the real home page is in no repository. The static page is the agreed way to show the banner (PRD §7).
- **Responsibilities:** reproduce the design's structure, content and look on desktop and phone. Show the three designed states (empty, typed, after Subscribe) without any submit, storage or network effect. Load nothing external.

## 2. Architecture overview
- **One component:** a single HTML document with an inline `<style>` block. There is no server, no script, no build step and no assets.
- **Boundary:** the file lives under `qa/`, which no test, CI job or packaging step reads. `pyproject.toml` sets `testpaths = ["tests"]`, and CI only runs `pytest` plus the `CI_FAIL` gate.
- **External dependencies:** none. The fonts are system fonts (`Helvetica, Arial, sans-serif`).
- **Design source (read-only):** `stories/PLAY-160/design/screens/` at commit `066dff3`. Its screens and tokens are identical to `ee6192d`. The source files are `home-page-banner-default.default.html`, the `.mobile.html` variants, and `tokens.css`. They are read from git objects only. The PLAY-160 branch is never merged, rebased or checked out.

## 3. Data flow
- **Static render only.** The browser loads one file and renders it.
- **User input:** text typed into the email field stays in that DOM element. There is no `<form>`, so pressing Enter does not submit. The button is `type="button"`, so clicking it does nothing.
- **No reload, no navigation, no message.** Constraint validation for `type="email"` never fires because nothing is ever submitted, so there is no invalid-email state, as the design specifies.
- **No events, no persistence, no async work.**

## 4. Component breakdown
| Component | Responsibility | Inputs / outputs | Repo |
| --- | --- | --- | --- |
| `qa/s5-banner.html` | Page markup and inline styles. **Top bar:** Acme wordmark; nav Home / Products / About / Contact. **Hero:** h1 "Welcome to Acme" → newsletter banner → tagline "Tools that make your day simpler." → orange "Shop now". **Features:** three cards (Fast delivery, Free returns, Support). **Footer:** "© 2026 Acme Inc." | In: the PLAY-160 design files (read only). Out: the rendered page in a browser. | roeeoz/play1 |

**Banner contract, from the design (FR2):**
- A group with the accessible name "Newsletter sign-up".
- A visually hidden label "Email address" bound to an `type=email` input. The input has helper (placeholder) text "Your email address", no `value`, and autocomplete off.
- A button labelled `Subscribe`.
- Max-width 520px, background #eef2ff, border #c7d2fe, button colour #1e3a8a.
- No other banner text.

## 5. Interface contracts
- **No APIs, events or cross-repo contracts.**
- The only "interface" is the visual and behavioural contract with the approved PLAY-160 screens. The page is checked against them by eye, side by side (spec §8).

## 6. Key technical decisions
- **Inline everything (FR6).** The relevant parts of `tokens.css` are embedded in a `<style>` block.
  - The design's CSS custom properties are kept as variables, so a reviewer can diff the page against tokens.css.
  - The `.review` strip rules and the state-simulation classes (`.is-focus`) are dropped. Real `:focus` / `:focus-visible` rules give the same behaviour.
- **Responsive phone layout (FR5).** The design ships separate `.mobile.html` files, scoped with `body.mobile`. These are turned into one `@media (max-width: 480px)` block with the design's phone values:
  - h1 32px
  - top bar 56px high, 16px padding
  - nav gap 12px, 14px text
  - banner stacked in a column with a full-width button
  - features in one column
  - smaller footer
  - **Why 480px:** it is above the design's 375–390px target and below small tablets.
- **Desktop is fluid**, like the design screens (drawn at 1200px, no max-width on body). The banner itself is capped at 520px.
- **Base the page on the default-state screen.** Never copy the `value="reader@example.com"` found in the typed and after-Subscribe screens (R5 / FR3).
- **No `<form>`, no `action`, no JavaScript** (spec §7, R4). This is what keeps "after Subscribe" identical to the typed state, with the text kept.
- **Nav links have no `href`, as in the design.** Shop now and the nav are existing behaviour and out of scope, so the page does not navigate anywhere either.
- **Alternatives rejected:**
  - A separate CSS file: violates the one-file rule.
  - A JS `preventDefault` on a form: no JS is allowed.
  - Literal values instead of variables: equivalent, but harder to review.
  - Following the PLAY-114 test + CHANGELOG precedent: ruled out by spec §2 and AC5.

## 7. Risks & constraints
- **Copying from the design.** Copying `reader@example.com`, the `.review` strip, `.is-focus`, or the link to the external `tokens.css` would break R5, FR6 or AC4. Mitigation: AC on the ticket; inline all styles.
- **Submit regressions.** Adding a `<form>` or a success text would break R4/RK1. Mitigation: AC on the ticket.
- **AC5 scope.** The work branch also carries `stories/PLAY-161/*.md` plan documents. AC5 is judged on the code change: the only product/code file added is `qa/s5-banner.html`. No test, CHANGELOG, CI, `pyproject.toml` or `CI_FAIL` change.
- **Visual fidelity (RK2).** Fidelity is checked manually; there is no visual-diff tool. The page follows the approved screens at desktop and at about 390px.
- **Size (G3).** About 100–130 lines, well under 300.
- **Operational.** There is no runtime and no scaling concern. CI time is unchanged, because pytest does not collect `qa/` (G4: under 60s).
