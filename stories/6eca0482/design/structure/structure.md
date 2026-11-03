# Newsletter sign-up page — Structure

The visitor gets from the Welcome screen through the Sign-up form to the Confirmation screen, with no account. There are three screens. The form has five states, and every screen has a desktop layout and a phone layout.

## Personas

### First-time visitor (main persona)

- **Who**: Someone on the product's public site for the first time who wants to hear about new releases.
- **Needs**: Sign up with only an email address and an explicit consent, quickly, on desktop or on a phone. Know what they are signing up for (new releases, at most once a month). Know what happens next (check the inbox to confirm).
- **Pain points**: Today the only way to hear about releases is to create an account, and most visitors do not want one. A form that loses what they typed when something goes wrong.

### Returning visitor

- **Who**: Someone who signed up before and comes back to the page.
- **Needs**: Go through the same journey without friction. If they submit the same address again, they see the Confirmation screen again.
- **Pain points**: No new pain point. The design constraint is privacy: nothing in the journey may reveal whether an address is already on the list. Duplicate and new sign-ups look the same.

## User interaction

```mermaid
flowchart TD
    Entry([Visitor arrives on the sign-up page]) --> W

    subgraph Welcome
        W[Welcome — default<br/>latest release announced]
        WE[Welcome — empty<br/>no release announced yet]
    end

    Entry -. no release announced yet .-> WE
    W -->|Sign up| F
    WE -->|Sign up| F

    subgraph SignUp[Sign-up form]
        F[Sign-up form — default<br/>empty email, consent unticked]
        FI[Sign-up form — invalid email<br/>message beside the field]
        FC[Sign-up form — consent missing<br/>message beside the checkbox]
        FL[Sign-up form — loading<br/>Subscribe disabled]
        FX[Sign-up form — submission failed<br/>input kept, Try again]
    end

    F -->|Subscribe| V{Valid email<br/>and consent ticked?}
    V -->|email not valid| FI
    V -->|consent not ticked| FC
    V -->|both valid| FL
    FI -->|fix email, Subscribe| V
    FC -->|tick consent, Subscribe| V
    FL -->|submission fails| FX
    FX -->|Try again| FL
    FL -->|submission succeeds<br/>new or already-listed address| C

    F -->|Back| W
    FI -->|Back| W
    FC -->|Back| W
    FX -->|Back| W

    C[Confirmation — default<br/>check your inbox at the address you entered]
    C -->|Back to the site| Exit([Leaves the journey: public site])
```

Notes on the diagram:
- If the email is not valid *and* the consent is not ticked, both messages show at once. The Sign-up form shows each control's message beside it (FR3).
- "Back" goes to the Welcome screen variant the visitor came from.
- `Entry` and `Exit` are the edges of the journey, not screens. The public site itself is out of scope.
- Every screen and state needs a desktop layout and a phone layout (Scenario 6). The flow is the same on both.

## Screen inventory

| Screen | Purpose | Main elements | States |
|---|---|---|---|
| **Welcome** | Says what the newsletter is and invites the visitor to sign up (FR1). | Headline. Short description: new releases, at most once a month, no account needed. One primary action, "Sign up". | **Default**: the copy can mention the latest release. **Empty**: no release announced yet; the copy still invites the sign-up and the "Sign up" button stays the same. Loading and error: not applicable, the screen is static. |
| **Sign-up form** | Collects an email address and an explicit consent, and submits them (FR2–FR5). | Email field with a visible label. Consent checkbox, unticked by default, with the full wording beside it: "Send me the product newsletter. I can unsubscribe at any time." One primary action, "Subscribe". A "Back" link to Welcome. A place for a message beside each control. A form-level message area for the failed submission. | **Default**: email empty, consent unticked. **Invalid email**: a message in words beside the field; the input is kept. **Consent missing**: a message beside the checkbox asking for the consent; the email is kept. Both messages can show together. **Loading**: Subscribe shows progress and cannot be pressed again; the input stays visible. **Submission failed** (error): says the sign-up did not go through, keeps the email and the consent as entered, and offers "Try again". Empty: not applicable. |
| **Confirmation** | Tells the visitor to check their inbox to confirm (FR6). | Message to check the inbox to confirm. The address the mail was sent to. One action back to the site. | **Default** only. The copy is identical for new and already-listed addresses, so it reveals nothing about list membership. |

Phone layout for every screen: a single column that fits the screen width with no horizontal scrolling. The email field, the checkbox and its label, and every button are large enough to tap. The full consent wording wraps. It is never cut short.

## Open branches

In each case below I chose the simplest option that keeps the journey complete. Confirm or change these before the Prototype step:

1. **Where "Back to the site" lands on the Confirmation screen.** The story only says "a way back to the site". I chose the public site's home page.
2. **What the Welcome screen says in each state.** The PRD defines the empty state as "no release announced yet". I assumed the default state can mention the latest release, and the empty state uses general copy ("be the first to hear when we release"). Both keep the same "Sign up" action. Please confirm the default Welcome screen should mention a release at all.
3. **When validation runs.** I chose to validate when the visitor presses "Subscribe" (FR3: "before it submits"), with no checking while they type. A message clears once the visitor fixes that field and submits again.
