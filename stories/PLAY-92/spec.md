# Feature Specification Document — PLAY-92: Personalised greeting for `testbed-hello` (`--name`)

_Traceability: story PLAY-92 (ברכה בשם שהמפתח מציין ב-testbed-hello), epic "ברכה אישית ל-testbed-hello" — Epic PRD (Confluence, version 1), requirements R1–R6, risks RK1–RK3; User Story Backlog, wave 1 (only story in the epic)._

## 1. Feature Overview

**Summary.** Add one optional command-line option, `--name NAME`, to the existing console script `testbed-hello` in the play1 package. With a non-blank name the tool prints `Hello, NAME!`; without the option, or with a blank name, it keeps printing exactly `Hello, world!` as it does today.

**Problem statement.** Today `testbed-hello` always prints the fixed line `Hello, world!`. A developer who wants a greeting addressed to a different name cannot get one (Epic PRD §1.1).

**Target users / actors.** Developers running `testbed-hello` from a terminal (Epic PRD §1.2). The tool prints a single line and makes no decisions for them.

## 2. Goals & Non-Goals

### Goals
- A developer gets a greeting addressed to a name of their choice in one command (`testbed-hello --name Alice` → `Hello, Alice!`).
- Anyone invoking the tool as today sees no change at all: output without `--name` stays byte-for-byte `Hello, world!` followed by a single newline (RK1).
- A blank name never yields a broken greeting; it falls back to `Hello, world!`.
- `--help` keeps a one-line summary, now also lists `--name`, and exits successfully (product goal G2).
- Serves product goals G1 (trustworthy: happy path, boundary and error cases tested; package coverage stays ≥ 90%), G2 (discoverable), G3 (small: one module plus its tests, ≤ 300 changed lines), and holds G4 as a control (tests stay fast and deterministic) — per *play1 — goals and success metrics*, Product goals.

### Non-Goals (Epic PRD §8, story context)
- Any other change to `testbed-hello`'s behaviour or to other tools in the package.
- New external/runtime dependencies.
- Changing the name's letter case, translating the greeting, or greetings in other languages.
- Taking the name from any source other than the command line (file, environment variable).
- Any graphical UI or operations work (environments, permissions, build pipeline).

## 3. Functional Requirements

**Inputs:** the command line of `testbed-hello`: optionally `--name` followed by one value, or `--help`.
**Output:** exactly one line on standard output (greeting) or the help/usage text; an exit status.

- **FR1 — Greeting by name (R1, Must).** When invoked with `--name` and a value that is not blank after trimming, the tool prints a single line `Hello, NAME!`, where NAME is the given value with leading and trailing whitespace removed and letter case unchanged, and exits successfully (status 0).
  - Example: `--name Alice` → `Hello, Alice!`; `--name "  Bob "` → `Hello, Bob!`; `--name alice` → `Hello, alice!` (case kept).
  - Whitespace inside the name is kept as given (only the start and end are trimmed).
- **FR2 — Default unchanged (R2, Must).** When invoked without `--name`, the tool prints exactly `Hello, world!` followed by a single newline — identical character for character to today — with nothing on standard error, and exits with status 0.
- **FR3 — Blank name falls back (R3, Must).** When the value given to `--name` is empty (`""`) or whitespace only (e.g. `" "`, `"   "`), the tool prints `Hello, world!` and exits with status 0.
- **FR4 — `--name` without a value is an error (R4, Should; PRD §7 decision).** When `--name` is given with no value after it, the tool behaves like any malformed command today: it shows a usage line and an error message on standard error, prints no greeting, and exits with failure status 2 (today's status for malformed commands).
- **FR5 — Help (R5, Must).** `testbed-hello --help` shows a usage line, a summary that fits on one line, and the options including `--name`; it prints no greeting and exits with status 0. If the summary wording is updated to mention a name it must still print on one line.
- **FR6 — Other malformed commands unchanged (R6, Must).** An unknown option (e.g. `--bogus`, `-x`) or an extra word (e.g. `extra`) continues to show usage and an error on standard error, prints no greeting, and exits with status 2, exactly as today.

## 4. User Experience & Behavior

**Main flow (Epic PRD §3):**
1. The developer runs `testbed-hello` in a terminal, with or without `--name NAME`.
2. If a non-blank name was given, the tool prints `Hello, NAME!` (trimmed, case kept); otherwise it prints `Hello, world!`. The tool exits successfully.

**Exception flows:**
| Situation | What the developer sees | Exit |
| --- | --- | --- |
| `--name ""` or `--name "   "` | `Hello, world!` | 0 |
| `--name` with nothing after it | usage + error message on stderr, no greeting | 2 |
| Unknown option or extra word | usage + error message on stderr, no greeting (as today) | 2 |
| `--help` | usage, one-line summary, options list including `--name`; no greeting | 0 |

**Output format:** the greeting is a single line, `Hello, <name>!` — no extra spaces, punctuation or blank lines. The default line is exactly `Hello, world!`.

## 5. Acceptance Criteria

From the published story (verbatim intent):
1. **Happy path — greeting by name.** Given a developer in a terminal, when they run `testbed-hello --name Alice`, then the output is the single line `Hello, Alice!`, and the tool exits successfully (status 0).
2. **Regression — no name, output unchanged.** Given a developer in a terminal, when they run `testbed-hello` with no options, then standard output is exactly `Hello, world!` plus one newline (one line only, as today), and the tool exits with status 0.
3. **Edge case — empty or whitespace-only name.** Given a developer in a terminal, when they run `testbed-hello --name "   "` or `testbed-hello --name ""` (and likewise `--name " "`), then the output is `Hello, world!`, and the tool exits with status 0.
4. **Scope boundary — help screen.** Given a developer in a terminal, when they run `testbed-hello --help`, then a one-line summary and the `--name` option are shown with no greeting, and the tool exits with status 0.

Making the in-scope behaviours in the story's context explicit (story description; PRD R4, R6, §7):
5. **Trimming, case kept.** `testbed-hello --name "  Bob "` prints `Hello, Bob!`; `testbed-hello --name alice` prints `Hello, alice!`; both exit 0.
6. **Error case — `--name` without a value.** `testbed-hello --name` prints no greeting on stdout, shows a usage line and an error on stderr, and exits with status 2.
7. **Regression — other malformed commands.** `testbed-hello --bogus`, `testbed-hello -x` and `testbed-hello extra` each print no greeting, show usage and an error on stderr, and exit with status 2, as today.

Definition of done: all of the above verified by automated tests that run without network, clock, or file access outside `tests/fixtures`; every required CI check green; the PR names PLAY-92 and the Epic PRD.

## 6. Dependencies & Constraints (product-level)

- **CI is the merge gate** (Engineering requirements — Infrastructure R3): merges only with every required check green; no manual merge.
- **No new dependencies** (Epic PRD §7; Engineering requirements — Infrastructure R2, Compliance R6).
- **Python floor 3.10** as declared by the project (Engineering requirements — Infrastructure R1).
- **Placeholder names only** in tests, no real personal data (Engineering requirements — Security R4).
- **Traceability**: the PR names PLAY-92 and the Epic PRD (Engineering requirements — Compliance R7).
- **Size**: one module plus its tests, ≤ 300 changed lines (product goal G3); new public functions, if any, need a docstring with an example (G2) and happy-path, boundary and error tests (G1); package coverage stays ≥ 90%.
- No other stories depend on or are depended on by this one.

## 7. Technical Design (deferred to STRUCTURE)

Architecture and interface details are for the STRUCTURE stage. Product-imposed constraints to respect: the existing public `hello_world()` (exported and doctested) must keep returning `Hello, world!`; the `--help` summary must still print on one line; the failure exit status for malformed commands stays 2; tests stay in-process and deterministic.

## 8. Open Questions (non-blocking)

1. **PM confirmation of PRD §7 decisions.** Trimming leading/trailing whitespace and treating `--name` with no value as an error are marked "for PM approval" in the Epic PRD; the published story adopts both. If reversed, FR1/FR4 and criteria 5/6 change.
2. **Names beginning with `-`.** Is it acceptable that a name like `-Al` must be passed as `--name=-Al` (since `--name -Al` reads as a missing value)? Not specified; working assumption: acceptable, no special handling.
3. **Repeated `--name`.** Behaviour when `--name` is given twice is not specified; working assumption: not in scope, no criterion.
4. **Coverage measurement.** The ≥ 90% package coverage target is not measured in CI; it can only be checked manually.
