# Feature Specification Document — e2e-gate-2: Spanish greeting in both repos

## 1. Feature Overview

**Summary.** Spanish becomes a supported greeting language in two repositories, and the Spanish greeting word is the same value in both:

- **pdlc-judge-e2e** (target branch `develop`): the greeting catalog (`greetings/catalog.py`, `GREETINGS`, today only `"en": "Hello"`) gains the entry `"es": "Hola"`, covered by a test.
- **play1** (target branch `main`): the `testbed-hello` console script (`src/testbed_utils/hello.py`; today it accepts no arguments and always prints `Hello, world!`) gains an optional `--lang {en,es}` argument. `en` is the default and prints `Hello, world!`; `es` prints `Hola, world!`. Both are covered by tests.

**Problem statement.** Both repositories only offer an English greeting. The story adds Spanish as a second language in both, with one shared Spanish word (`Hola`), so the two stay consistent.

**Target users / actors.** Developers and the factory's end-to-end checks: people who call `greeting("es")` from the pdlc-judge-e2e catalog, and people who run the `testbed-hello` command in play1.

## 2. Goals & Non-Goals

### Goals
- G1: In pdlc-judge-e2e, `greeting("es")` returns `Hola`, and `GREETINGS` contains `"es": "Hola"`.
- G2: In play1, `testbed-hello --lang es` prints `Hola, world!`.
- G3: In play1, `testbed-hello` with no argument and `testbed-hello --lang en` both print `Hello, world!`, exactly as the command does today.
- G4: The Spanish word is exactly the same value (`Hola`) in both repositories.
- G5: Each repository's own tests cover its new behavior and still pass under that repository's test gate.

### Non-Goals
- No language other than `en` and `es`.
- No other change to behavior in either repository ("No other behaviour changes"). That covers: the English catalog entry, the `greeting()` error for unknown languages, the `hello_world()` function and its `Hello, world!` result, the `--help` description sentence, and the existing handling of unrecognized options.
- The second word stays `world` in English. The Spanish output is `Hola, world!`, not a full Spanish sentence.
- play1 does not import or read the pdlc-judge-e2e catalog. The two repositories stay independent; only the value is shared.
- No change to other greeting scripts in play1 (`hello-world/hello.sh`, `qa/*`).

## 3. Functional Requirements

**pdlc-judge-e2e — greeting catalog**
- FR1: `GREETINGS` contains `"es": "Hola"` in addition to the unchanged `"en": "Hello"`.
- FR2: `greeting("es")` returns `"Hola"`.
- FR3: `greeting("en")` still returns `"Hello"`. `greeting` called with any language not in the catalog (e.g. `"xx"`) still raises `KeyError`.
- FR4: A test asserts FR2. The suite passes under the repository's declared gate, `python3 -m unittest discover -s tests -t .` (`.factory/testing.md`). That includes the existing rule that every greeting is a capitalised alphabetic word, which `Hola` meets.

**play1 — `testbed-hello` console script**
- FR5: The command accepts an optional `--lang` argument whose allowed values are `en` and `es`.
- FR6: With no `--lang`, the command prints `Hello, world!` followed by a newline to standard output, writes nothing to standard error, and exits with code 0. This is unchanged from today.
- FR7: `--lang en` behaves exactly as FR6.
- FR8: `--lang es` prints `Hola, world!` followed by a newline to standard output, writes nothing to standard error, and exits with code 0.
- FR9: Edge case: a `--lang` value outside `{en,es}` (e.g. `fr`, or `ES` in another case) is rejected the way the command already rejects bad input. Nothing goes to standard output, a usage line and an error go to standard error, and the exit code is 2. This follows from the `{en,es}` set the story states and from the command's existing bad-option behavior (`tests/test_hello_cli.py`, `TestBadOption`).
- FR10: `--help` keeps its current description sentence and now also lists the `--lang` option. Unrecognized options (`--bogus`, `-x`, a stray positional `extra`) are still rejected as today.
- FR11: Tests cover both the default/`en` output and the `es` output. The full suite passes under the repository's gate, `pip install -e ".[test]"` then `pytest` (`.factory/testing.md`, `.github/workflows/ci.yml`).

**Cross-repository**
- FR12: The Spanish word is the identical string `Hola` (capital H, no accent, no punctuation) in both repositories.

## 4. User Experience & Behavior

**Key flows (terminal, play1):**

| Command | stdout | stderr | exit code |
| --- | --- | --- | --- |
| `testbed-hello` | `Hello, world!` | (empty) | 0 |
| `testbed-hello --lang en` | `Hello, world!` | (empty) | 0 |
| `testbed-hello --lang es` | `Hola, world!` | (empty) | 0 |
| `testbed-hello --lang fr` | (empty) | usage line + error naming the allowed choices | 2 |
| `testbed-hello --help` | usage that includes `--lang`, plus the existing description | (empty) | 0 |

**Library flow (pdlc-judge-e2e):** `greeting("es")` → `'Hola'`; `greeting("en")` → `'Hello'`; `greeting("xx")` → `KeyError`, as today.

The only output format is a plain single line of text on standard output. No styling, colour or other sensory requirement was requested.

## 5. Acceptance Criteria

1. In pdlc-judge-e2e, `GREETINGS` in `greetings/catalog.py` contains `"es": "Hola"`, and `greeting("es")` returns `"Hola"`.
2. In pdlc-judge-e2e, a test asserts that `greeting("es")` returns `"Hola"`, and `python3 -m unittest discover -s tests -t .` passes from the repository root.
3. In pdlc-judge-e2e, `greeting("en")` still returns `"Hello"`, and `greeting("xx")` still raises `KeyError`.
4. In play1, running `testbed-hello` with no arguments prints exactly `Hello, world!` and a newline to standard output, with empty standard error and exit code 0.
5. In play1, running `testbed-hello --lang en` prints exactly `Hello, world!` and a newline to standard output, with empty standard error and exit code 0.
6. In play1, running `testbed-hello --lang es` prints exactly `Hola, world!` and a newline to standard output, with empty standard error and exit code 0.
7. In play1, running `testbed-hello --lang fr` prints nothing to standard output, prints a usage line and an error to standard error, and exits with code 2.
8. In play1, `testbed-hello --help` exits 0, still shows the existing description and lists the `--lang` option. `--bogus`, `-x` and `extra` are still rejected with exit code 2.
9. In play1, tests cover the default/`en` output and the `es` output, and `pytest` passes after `pip install -e ".[test]"`.
10. The Spanish word is the identical string `Hola` in pdlc-judge-e2e's `GREETINGS["es"]` and in play1's `testbed-hello --lang es` output.
11. Each repository's pull request shows its required checks green. Neither pull request changes behavior beyond criteria 1–10.

## 6. Dependencies & Constraints (product-level)

- The work covers two repositories with one pull request each: play1 into `main`, and pdlc-judge-e2e into `develop`. Neither depends on the other being merged first. A person merges each pull request after review.
- Each repository's gates apply as they stand:
  - play1: the `test` job (`pip install -e ".[test]"` + `pytest`), the `gate` job (no `CI_FAIL` file at the root), and the layout gate (source under `src/`, tests under `tests/`, new shell scripts executable with a shebang, no file over 200 KB).
  - pdlc-judge-e2e: the unittest gate declared in `.factory/testing.md`. The repository has no CI workflow.
- Neither repository has a `CLAUDE.md`, `AGENTS.md` or `.factory/memory/`.
- Existing play1 tests that pin today's behavior (`tests/test_hello.py`, `tests/test_hello_cli.py`) must keep passing. The story's "no other behaviour changes" rule requires it.

## 7. Technical Design (deferred to STRUCTURE)

Deferred to STRUCTURE: how the language choice reaches the greeting in play1 (for example, whether `hello_world()` gains a parameter or a separate mapping is added). Any such change must keep `hello_world()` returning `Hello, world!` and keep its doctest passing. Also deferred: how the tests are organised in each repository.

## 8. Open Questions (if any remain)

- None blocking.
- Assumption to confirm at review: an unsupported `--lang` value is rejected with exit code 2 and a usage error (FR9 / AC7). This follows from the stated `{en,es}` set and the command's existing bad-input behavior, not from an explicit sentence in the story.
- Matching is case-sensitive: `--lang ES` is rejected. This follows from the lowercase `{en,es}` set the story states.
