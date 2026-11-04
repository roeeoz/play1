# Newsletter sign-up journey — Structure

## Personas

| Persona | Needs | Pain points |
|---|---|---|
| **First-time visitor** — someone browsing the public site who wants product updates | Hear about new releases without creating an account; quick, low-commitment sign-up | Creating an account is too heavy; no lightweight channel exists today |
| **Returning visitor** — someone who already signed up and lands on the page again | Not be penalised or confused if they submit the same address a second time | Seeing an "already subscribed" message leaks whether the address is on the list |

## User interaction

```mermaid
flowchart TD
    A["Welcome — default"] -->|Sign up| B["Sign-up form — default"]
    A2["Welcome — empty\n(no release yet)"] -->|Sign up| B

    B -->|Back| A
    B -->|Subscribe\n(validation fails)| C["Sign-up form — validation error\n(invalid email / consent missing / both)"]
    C -->|Fix & Subscribe\n(validation fails again)| C
    C -->|Back| A
    C -->|Fix & Subscribe\n(validation passes)| D["Sign-up form — loading"]
    B -->|Subscribe\n(validation passes)| D

    D -->|Submission succeeds| F["Confirmation — default"]
    D -->|Submission fails| E["Sign-up form — submission failed"]

    E -->|Try again\n(validation passes)| D
    E -->|Back| A

    F -->|Back to site| G(("Exit"))
```

## Screen inventory

| Screen | Purpose | Main elements | States |
|---|---|---|---|
| **Welcome** | Explain the newsletter (new releases, at most once a month) and invite the visitor to sign up | Headline, short description copy, **Sign up** button | **default** — standard copy; **empty** — no release announced yet, copy still invites sign-up |
| **Sign-up form** | Collect email address and explicit consent | Email input field, consent checkbox (label: "Send me the product newsletter. I can unsubscribe at any time."), **Subscribe** button, **Back** link | **default** — empty form ready for input; **validation error** — inline message beside each invalid control (invalid email, consent not ticked, or both); **loading** — spinner or equivalent, Subscribe button disabled; **submission failed** — banner or inline message saying sign-up did not go through, input preserved, option to try again |
| **Confirmation** | Tell the visitor to check their inbox | Confirmation message naming the submitted email address, **Back to site** link | **default** |

## Open branches

None. The story, the PRD and the acceptance criteria are consistent and fully specify the journey, the screens and their states. No structural decision requires designer input before prototyping.
