# Plan — EG2-2: Spanish greeting in both repositories

## Context

EG2-2 adds Spanish (`es` → `Hola`) as a supported greeting language in two independent repositories. In `roeeoz/pdlc-judge-e2e` (target branch `develop`), `greeting("es")` must return `Hola` (spec AC1, AC2). In `roeeoz/play1` (target branch `main`), the `testbed-hello` console script gains an optional `--lang {en,es}` (default `en`) and prints `Hola, world!` for `es`. Default output, help, error handling and `hello_world()` stay as they are (AC3–AC7). The literal `Hola` must be identical in both repos (AC8). The approved requirement `spec.md`, the design `hld.md` and the breakdown `work-items.md` (t1, t2) sit beside this file in `stories/EG2-2/` of the play1 checkout.

## Research findings

**pdlc-judge-e2e (work item t1)**
- `greetings/catalog.py:5-7`: `GREETINGS: dict[str, str] = {"en": "Hello"}`. `greeting(lang)` (`greetings/catalog.py:10-18`) raises `KeyError` for unknown codes and has a doctest for `"en"` (`:13-14`).
- `tests/test_catalog.py:6-15`: three unittest cases: English, unknown → `KeyError`, and every value is capitalised and alphabetic (`word[:1].isupper() and word.isalpha()`). `Hola` passes the last rule.
- Gate (`.factory/testing.md`): `python3 -m unittest discover -s tests -t .`. Stdlib only, no CI workflow. Docstring doctests are not collected by this command, so a docstring example is documentation only.
- No `CLAUDE.md`, `AGENTS.md` or `.factory/memory/`.

**play1 (work item t2)**
- `src/testbed_utils/hello.py:20-23`: `main()` builds `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)`, calls `parse_args()` and prints `hello_world()`. `hello_world()` (`:11-17`) returns `"Hello, world!"` and has a doctest. `_DESCRIPTION` (`:8`) must stay ≤76 characters (comment `:7`).
- Entry point `testbed-hello = "testbed_utils.hello:main"` (`pyproject.toml:17`). Export `hello_world` (`src/testbed_utils/__init__.py:9,17`). Both stay unchanged.
- `tests/test_hello_cli.py`: helper `run_main(args)` (`:12-22`) patches `sys.argv`, captures stdout and stderr, and maps `SystemExit` to an exit code. `GREETING = "Hello, world!\n"` (`:9`). Existing cases: default (`:25-30`), `--help` (`:33-40`, asserts `usage:`, `_DESCRIPTION` with whitespace normalised, and no `Hello, world!`), bad options `--bogus`/`-x`/`extra` → exit 2 (`:43-51`).
- `tests/test_hello.py:9-31` pins `hello_world()`, its package export and its doctest.
- No other file references `testbed-hello` or `testbed_utils.hello`. `hello-world/hello.sh` and `qa/s3-hello.sh` are separate scripts with their own tests and are untouched.
- Gate (`.factory/testing.md`): one required layer `package-api`, `pip install -e ".[test]"` then `pytest` (CI `test` job, Python 3.12, `.github/workflows/ci.yml`). The `gate` job fails only if `CI_FAIL` exists. Layout gate `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`: Python under `src/`, tests under `tests/`, new shell scripts executable with a shebang, no file > 200 KB. No linter or formatter is configured.
- No `CLAUDE.md`, `AGENTS.md` or `.factory/memory/`.

**Unknowns remaining:** none blocking. Argparse error wording differs between versions. Tests therefore assert `usage:` and `error` substrings, as the existing tests do.

## Locked decisions and assumptions

**Locked decisions**
- Spanish word is exactly `Hola`; `, world!` is not translated (spec §2, FR9).
- `--lang` choices are exactly `en`, `es`, default `en`, case-sensitive. An invalid or missing value exits 2 with usage and error on stderr and no greeting (spec FR3–FR6; hld §5 table).
- Use argparse `choices` for validation (hld §6).
- `hello_world()` signature, return value, doctest and export are unchanged (spec §2, hld §6).
- No code dependency between repos; play1 does not import the catalog (spec §2, hld §6).
- `GREETINGS` keys are exactly `{"en", "es"}` (hld §5, t1 AC).
- t1 and t2 are independent, with no `dependsOn` (`work-items.md`).

**Assumptions**
- The Spanish line in play1 comes from a small private mapping in `hello.py` (for example language → greeting word, formatted as `f"{word}, world!"`), or from `hello_world()` for `en`. Evidence: hld §6 leaves the mapping to the implementer. If wrong: the internal shape changes, but the observable contract does not.
- Adding a `>>> greeting("es")` example to the catalog docstring is optional, because the gate does not run doctests. If wrong (a doctest runner is added later), the example still passes.

## Solution proposal

**pdlc-judge-e2e:** add one entry, `"es": "Hola"`, to `GREETINGS`. `greeting()` already handles lookup and the `KeyError` path, so no logic changes. Add a unittest asserting `greeting("es") == "Hola"` and one asserting `set(GREETINGS) == {"en", "es"}`. The existing capitalised-word test covers the new value automatically.

**play1:** in `main()`, add `parser.add_argument("--lang", choices=("en", "es"), default="en", help=...)`. Then print the greeting for `args.lang`. A module-private mapping (`en` → `Hello`, `es` → `Hola`) keeps the change in one place. `en` output must stay byte-identical to `hello_world()`. Either print `hello_world()` for `en`, or assert equality in a test. The help string must not contain `Hello, world!` or `Hola, world!`. A neutral wording such as "greeting language (default: en)" works. Argparse already produces the required error shape (usage + `error: argument --lang: invalid choice` / `expected one argument`, exit 2), which is the same shape the existing bad-option tests pin.

**Alternatives rejected:**
- A `lang` parameter on `hello_world()`: rejected because it changes a public, doctested signature that the spec freezes.
- Free-string `--lang` with manual validation: rejected because it duplicates argparse and risks a different error shape.
- Importing the pdlc-judge-e2e catalog into play1: rejected because the spec forbids a cross-repo dependency.

## Ordered implementation steps

**Work item t1 — `roeeoz/pdlc-judge-e2e`**
1. Add `"es": "Hola"` to `GREETINGS` in `greetings/catalog.py:5-7`. Optionally add a `>>> greeting("es")` / `'Hola'` docstring example. Advances AC1 and AC8. Covered by the unittest layer (`tests/`).
2. In `tests/test_catalog.py`, add `test_spanish_greeting` (`greeting("es") == "Hola"` and `GREETINGS["es"] == "Hola"`) and `test_supported_languages` (`set(GREETINGS) == {"en", "es"}`). Keep the three existing tests unchanged; they cover the AC2 regression and `KeyError` paths. Advances AC1, AC2 and AC8. Layer: unittest.
3. Run `python3 -m unittest discover -s tests -t .` from the repo root. No dependencies to acquire (stdlib only).

**Work item t2 — `roeeoz/play1`**
4. In `src/testbed_utils/hello.py` `main()` (`:20-23`):
   - Add the `--lang` option with `choices` `en`/`es` and default `en`, with a help string that contains no greeting line.
   - Bind `args = parser.parse_args()`.
   - Print `Hola, world!` for `es` and `Hello, world!` for `en`, through a private mapping (or `hello_world()` for `en`).
   - Leave `hello_world()`, `_DESCRIPTION` and the module docstring's meaning unchanged.

   Advances AC3, AC4, AC5 and AC6. Layer: `package-api` (pytest).
5. Extend `tests/test_hello_cli.py`, reusing `run_main` and `GREETING`:
   - **Default and English:** default and `--lang en` → exit 0, stdout `== GREETING`, stderr empty (AC4).
   - **Spanish:** `--lang es` and `--lang=es` → stdout exactly `"Hola, world!\n"`, stderr empty, exit 0 (AC3, AC8).
   - **Invalid value:** parametrised `--lang fr`, `--lang ES`, bare `--lang` → exit 2, stdout `""`, `usage:` and `error` in stderr, neither greeting in stdout or stderr (AC5).
   - **Help:** in `TestHelp`, also assert `--lang`, `en` and `es` appear in stdout and `Hola, world!` does not (AC6).
   - **Existing bad-option cases:** in `TestBadOption`, keep the existing cases and add `Hola, world!` not in stderr.

   Layer: `package-api`.
6. Leave `tests/test_hello.py` as is. It already pins `hello_world()`, its export and its doctest (AC6). Add nothing unless the implementer adds a test that `en` CLI output equals `hello_world() + "\n"`, which belongs in `test_hello_cli.py`.
7. Run `pip install -e ".[test]"` (pulls `pypdf`, `flask>=3` and `pytest>=8` from the index; do not assume a warm cache), then `pytest` from the repo root (AC7).

Invariants:
- **Authorization, tenancy, concurrency, idempotency:** not applicable. Both changes are a pure in-process lookup and a single stdout write.
- **Validation and error paths:** covered by argparse `choices` and the step 5 invalid-value tests, plus the existing `KeyError` test.

Generated deliverables: none.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1, 2, 3 | t1 | pdlc-judge-e2e: add Spanish (es → Hola) to the greeting catalog |
| 4, 5, 6, 7 | t2 | play1: testbed-hello accepts --lang {en,es} and prints Hola, world! for es |

Both work items are covered. AC8 (cross-repo identity) is satisfied by the literal `Hola` asserted in step 2 and step 5. No runtime check spans both repos, by design.

## Verification and CI gate

- **pdlc-judge-e2e:**
  - Gate: `python3 -m unittest discover -s tests -t .` from the repo root, run once on the committed SHA. Runs in a pod.
  - There is no provider CI, so this local run is the gate.
  - It must show all five tests (three existing, two new) passing.
- **play1:**
  - Canonical order: `pip install -e ".[test]"`, then `pytest` (the `package-api` layer, required, `runBy: canonical-gate`). Runs in a pod; the provider CI `test` job on Python 3.12 at the exact head is authoritative.
  - It must show the whole suite green, including the existing `test_hello.py`, `test_hello_cli.py` and unrelated tests, plus the new `--lang` cases.
  - The `gate` job stays green (no `CI_FAIL`).
  - The layout gate passes: changes only under `src/` and `tests/`, no new shell scripts, no large files.
- **CI and delivery assets:** no CI configuration changes in either repo. No `.factory/delivery-assets` obligation (no binary is added).

## Risks and scope guards

**Risks**
- **Argparse message wording varies across Python versions.** Mitigation: assert `usage:`/`error` substrings and the exit code, not full messages.
- **The help text could leak a greeting line.** Mitigation: use a neutral help string, and the help test asserts neither greeting appears.
- **The `en` output could drift from `hello_world()`.** Mitigation: derive the `en` output from `hello_world()` or pin it with `GREETING`.
- **Argparse prefix matching (`allow_abbrev`) accepts `--la es`.** This is existing parser behaviour. Do not change it or test it as a requirement.

**Scope guards — the implement phase must NOT:**
- Change `hello_world()`'s signature or return value, `_DESCRIPTION`, the package `__all__`, or `pyproject.toml`.
- Touch `pdf-extract`, `testbed-num-summary`, `guestbook`, `qa/`, `hello-world/`, `README.md` or CI workflows in play1.
- Make play1 depend on or import pdlc-judge-e2e, or add any language beyond `en`/`es`, or translate `, world!`.
- Change `greeting()` logic or the existing catalog tests, or add third-party dependencies to pdlc-judge-e2e.
- Edit `spec.md`, `hld.md` or `work-items.md`.
- Make a check green by deleting, skipping or weakening any existing test (including `TestBadOption` and `TestHelp`). Report a failing check as blocked instead.

## Clarification outcomes

None.
