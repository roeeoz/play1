# Newsletter sign-up page — Structure

## Personas

### First-time visitor (main persona)

- **Who**: A visitor to the product's public site who has not signed up before.
- **Needs**: Hear about new releases (at most once a month) with just an email address — no account, no sign-in.
- **Pain points**: Today the only way to stay informed is to create an account, which most visitors do not want. They may arrive on a phone as often as on a desktop.

### Returning visitor

- **Who**: A visitor who signed up before and comes back to the page.
- **Needs**: Go through the same journey without friction; if they submit the same address again, land on the Confirmation screen as usual.
- **Pain points**: Being told "you are already subscribed" would reveal list membership — the journey must never do that.

## User interaction

```mermaid
flowchart TD
    Entry([Visitor arrives on the public site page]) --> W{Release announced yet?}
    W -->|yes| W1[Welcome — default]
    W -->|no| W2[Welcome — empty]
    W1 -->|"Sign up"| F0[Sign-up form — default]
    W2 -->|"Sign up"| F0

    F0 -->|"Subscribe"| V{Client-side validation}
    V -->|email not valid| F1[Sign-up form — invalid email]
    V -->|consent not ticked| F2[Sign-up form — consent missing]
    V -->|both valid| FL[Sign-up form — loading<br/>Subscribe disabled]

    F1 -->|"Correct email, Subscribe"| V
    F2 -->|"Tick consent, Subscribe"| V

    FL -->|accepted — new or already-listed address| C[Confirmation — default]
    FL -->|failed| FE[Sign-up form — submission failed<br/>input kept]
    FE -->|"Try again"| V

    F0 -->|"Back"| W1
    F1 -->|"Back"| W1
    F2 -->|"Back"| W1
    FE -->|"Back"| W1

    C -->|"Back to the site"| Exit([Public site])
```

All screens are laid out for desktop and phone width; the phone layout changes the layout only, never the path.

## Screen inventory

| Screen | Purpose | Main elements | States |
|---|---|---|---|
| **Welcome** | Say what the newsletter is and invite the visitor in (FR1) | Headline; short description: new releases, at most once a month; latest release teaser (when one exists); primary button "Sign up" | **Default** — with the latest release mentioned. **Empty** — no release announced yet; copy still invites the sign-up, "Sign up" unchanged. No loading or error state. |
| **Sign-up form** | Collect an email address and explicit consent (FR2–FR5) | Email field with label; consent checkbox, unticked by default, with full wording "Send me the product newsletter. I can unsubscribe at any time."; primary button "Subscribe"; "Back" link to Welcome | **Default** — empty field, unticked checkbox. **Error: invalid email** — message in words beside the email field, input kept. **Error: consent missing** — message beside the checkbox asking for consent, email kept. (Both messages show together if both fail.) **Loading** — Subscribe shows progress and is disabled; inputs locked. **Error: submission failed** — message that the sign-up did not go through, all input kept, "Try again" action. |
| **Confirmation** | Tell the visitor to check their inbox to confirm (FR6) | Heading; message naming the address the mail went to; "Back to the site" link | **Default** — identical for a new and an already-listed address. No loading, error or empty state. |
| **Public site** (exit) | Where "Back to the site" leads; existing page, not designed in this story | — | — |

Mobile (Scenario 6): every screen fits a phone width without horizontal scrolling; email field, checkbox (with its label as tap target), buttons and links are sized for touch.

## Open branches

1. **Where does "Back to the site" lead?** The sources say "a way back to the site" without naming the page. Assumed: the public site home page.
2. **Both validation errors at once.** If the email is invalid *and* consent is missing, the sources do not say whether one or both messages appear. Assumed: both messages show together, each beside its control, so the visitor fixes everything in one pass.
3. **What the Welcome screen shows when a release exists.** The "empty" state implies the default mentions a release, but the sources do not say how. Assumed: one line naming the latest release; the empty state replaces it with copy about upcoming releases.
