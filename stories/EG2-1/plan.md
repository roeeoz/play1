# Plan — EG2-1: Spanish greeting in both repos

## Context

EG2-1 adds Spanish (`es` → `Hola`) as a second greeting language in two independent repositories. In `roeeoz/pdlc-judge-e2e` (base `develop`) the greeting catalog gains `"es": "Hola"` (AC1–AC3). In `roeeoz/play1` (base `main`) the `testbed-hello` console script gains an optional `--lang {en,es}` option, where `es` prints `Hola, world!` (AC4–AC9). The Spanish word is the identical literal `Hola` in both (AC10), and each pull request stays green with no other behaviour change (AC11). Each repository gets its own pull request from branch `halo/feat/eg2-1-20261119-135842`. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/EG2-1/` of the play1 checkout. The work items are `t1` (pdlc-judge-e2e) and `t2` (play1).

## Research findings

**pdlc-judge-e2e (checkout at `4cc0d3f`)**
- `greetings/catalog.py:5-7` defines `GREETINGS: dict[str, str] = {"en": "Hello",}`.
- `greetings/catalog.py:10-18`: `greeting(lang)` raises `KeyError(f"no greeting for language {lang!r}")` when `lang not in GREETINGS`, otherwise returns the value. The lookup is case-sensitive. The docstring holds a doctest for `"en"`. The unittest gate does not collect doctests.
- `tests/test_catalog.py:6-16`: `CatalogTest` has `test_english_greeting`, `test_unknown_language_is_an_error` (`"xx"`) and `test_every_greeting_is_a_capitalised_word`, which iterates `GREETINGS`. `Hola` passes the last rule (`"H".isupper()`, `"Hola".isalpha()`).
- Gate: `.factory/testing.md` declares `python3 -m unittest discover -s tests -t .` from the repo root. It uses only the stdlib, needs no install step and has no CI workflow. `tests/__init__.py` exists, so discovery imports `greetings` from the root.
- There is no `CLAUDE.md`, `AGENTS.md` or `.factory/memory/`.

**play1 (checkout at `a24a68a`)**
- `src/testbed_utils/hello.py:8`: `_DESCRIPTION = "Print a hello-world greeting to standard output."`. The comment at `:7` keeps it at or under 76 characters.
- `src/testbed_utils/hello.py:11-17`: `hello_world()` returns `"Hello, world!"` and has a doctest.
- `src/testbed_utils/hello.py:20-23`: `main()` builds `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)`, calls `parse_args()` and prints `hello_world()`. This is the whole change surface.
- `pyproject.toml` declares the entry point `testbed-hello = "testbed_utils.hello:main"`, `requires-python = ">=3.10"`, `testpaths = ["tests"]` and `addopts = "-q"`.
- `src/testbed_utils/__init__.py:9` re-exports `hello_world`. It does not change.
- `tests/test_hello.py:8-30` pins `hello_world() == "Hello, world!"`, the package export and the doctest (`doctest.testmod(hello)` with `failed == 0`). Any new docstring example in `hello.py` must also pass.
- `tests/test_hello_cli.py:12-22`: the `run_main(args)` helper patches `sys.argv`, captures stdout and stderr, and turns `SystemExit` into an exit code.
  - `TestGreeting` (`:25-30`) covers the no-argument case.
  - `TestHelp` (`:33-40`) asserts `usage:` is present, asserts `_DESCRIPTION` is present after whitespace normalisation, and asserts `Hello, world!` is absent from the help text.
  - `TestBadOption` (`:43-51`) checks `--bogus`, `-x` and `extra`: exit 2, empty stdout, `usage:` and `error` on stderr.
- Gate: `.factory/testing.md` names one required layer, `package-api` (`pytest`, production-path, `runBy: canonical-gate`). Its local form is `pip install -q -e ".[test]" && pytest`. `.github/workflows/ci.yml` runs job `test` (Python 3.12) and job `gate` (fails iff `CI_FAIL` exists at the root). The layout gate lives in `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`: source under `src/`, tests under `tests/`, new shell scripts executable with a shebang, and no file over 200 KB.
- No linter, formatter or type checker is configured in either repository.
- No external data or cross-system dependency exists. There are no open unknowns.

## Locked decisions and assumptions

**Locked decisions**
- The Spanish word is the literal `Hola` in both repos: capital H, no accent, no punctuation (spec FR12, AC10).
- `GREETINGS == {"en": "Hello", "es": "Hola"}`. `greeting()` logic and its error message stay unchanged (t1, hld §5).
- `--lang` accepts exactly `en` and `es`. The default is `en`. Matching is case-sensitive (spec FR5, §8; hld §6).
- Invalid values go through argparse `choices`: empty stdout, usage and error on stderr, exit 2 (spec FR9, hld §6).
- `hello_world()` with no arguments, its doctest, `_DESCRIPTION`, `src/testbed_utils/__init__.py` and `tests/test_hello.py` stay unchanged (spec §7, t2 "Consumes").
- play1 does not import the pdlc-judge-e2e catalog (spec Non-Goals).
- The Spanish output is `Hola, world!`. The second word stays `world` (spec Non-Goals).
- Tests assert only the stable parts of argparse errors, never the exact quoting of choices (hld §7, t2).

**Assumptions**
- The `--lang` help string avoids the text `Hello, world!`. Evidence: `TestHelp` (`tests/test_hello_cli.py:40`). If wrong, the existing test fails.
- argparse prints `{en,es}` in the usage line and in the options entry on Python 3.10–3.13. Evidence: the stdlib formats `choices` that way and the hld checked it on 3.13. If wrong, the new help assertion breaks on a version. Assert `--lang` and both `en` and `es` separately as a fallback.
- `allow_abbrev` stays at its default, so `--la es` resolves to `--lang`. The hld accepts this. No test relies on it.

## Solution proposal

**pdlc-judge-e2e (t1):** this is a data-only change. Add `"es": "Hola"` to `GREETINGS` after `"en"`. Do not touch `greeting()`. Extend `CatalogTest` with a Spanish lookup test, an exact-catalog equality test and a case-sensitivity test (`"ES"` raises `KeyError`). The existing tests cover `en`, `xx` and the capitalised-word rule.

**play1 (t2):** select the greeting in the CLI layer and leave `hello_world()` untouched.
- Add a module-private mapping in `src/testbed_utils/hello.py`: `_GREETINGS = {"en": "Hello, world!", "es": "Hola, world!"}`. This is new.
- Use `hello_world()` as the source of the English value, so the existing contract stays the single origin of `Hello, world!`.
- In `main()`, call `parser.add_argument("--lang", choices=<the mapping's keys, en then es>, default="en", help=...)`. Store the result of `parse_args()` and print the mapped greeting.
- Keep the help string short and free of `Hello, world!`, for example "greeting language (default: en)".

argparse supplies all the edge-case behaviour from hld §5:
- Invalid choice or missing value: exit 2.
- `--lang=es` form: accepted.
- Repeated `--lang`: the last value wins.
- `--help` listing: includes `--lang`.
- Unknown options: still rejected.

**Alternatives rejected:**
- Adding a `lang` parameter to `hello_world()`. The hld allows it, but it widens the public function and its doctest surface for no benefit to the ACs.
- Importing the catalog from pdlc-judge-e2e. The spec Non-Goal forbids it.
- Hand-written validation instead of `choices`. It duplicates argparse's existing rejection path that `TestBadOption` already relies on.

## Ordered implementation steps

**Work item t1 — `roeeoz/pdlc-judge-e2e`**
1. Edit `greetings/catalog.py:5-7`: add the entry `"es": "Hola",` to `GREETINGS`. Change nothing else. Advances AC1 and AC10. Test layer: the unittest suite in `tests/test_catalog.py`.
2. Extend `CatalogTest` in `tests/test_catalog.py`. Advances AC2, AC3 and AC10. Test layer: unittest gate.
   - Add `test_spanish_greeting`: `greeting("es") == "Hola"`.
   - Add `test_catalog_contents`: `GREETINGS == {"en": "Hello", "es": "Hola"}`.
   - Add `test_language_code_is_case_sensitive`: `greeting("ES")` raises `KeyError`.
   - Keep the three existing tests unmodified.
3. Run `python3 -m unittest discover -s tests -t .` from the repo root. Advances AC2 and AC11. It needs no dependency install.

**Work item t2 — `roeeoz/play1`**

4. Edit `src/testbed_utils/hello.py`. Advances AC4–AC8 and AC10. Test layer: `package-api` (`pytest`, `tests/test_hello_cli.py`).
   - Add the private language→greeting mapping beside `_DESCRIPTION`, with `"en"` mapped to `hello_world()`'s value and `"es"` mapped to `"Hola, world!"`.
   - In `main()`, add the `--lang` argument with `choices` taken from the mapping in `en`, `es` order and `default="en"`.
   - Print `mapping[args.lang]`.
   - Do not modify `hello_world()`, its docstring, `_DESCRIPTION` or its comment.
   - Any new docstring must hold no `>>>` example that could fail `doctest.testmod(hello)`.
5. Extend `tests/test_hello_cli.py` using the existing `run_main` helper. Add a module constant `GREETING_ES = "Hola, world!\n"`. Test layer: `package-api` (pytest).
   - Add a parametrized test over `["--lang", "en"]` and `["--lang=en"]`: exit 0, stdout `== GREETING`, stderr `== ""`. Advances AC5 and AC9.
   - Add a parametrized test over `["--lang", "es"]` and `["--lang=es"]`: exit 0, stdout `== GREETING_ES`, stderr `== ""`. Advances AC6, AC9 and AC10.
   - Add a parametrized invalid-value test over `["--lang", "fr"]`, `["--lang", "ES"]` and `["--lang", ""]`: exit 2, stdout `== ""`, `usage:` and `error` in stderr, and `en` and `es` both present in stderr. Advances AC7.
   - Add a missing-value test (`["--lang"]`): exit 2, empty stdout, `usage:` and `error` in stderr. Advances AC7.
   - Add a help test (or extend `TestHelp` with a new method): `--help` exits 0 with empty stderr, `--lang` and `{en,es}` appear in stdout, `_DESCRIPTION` is still present and `Hello, world!` is absent. Advances AC8.
   - Leave `TestGreeting` (AC4), the existing `TestHelp` assertions and `TestBadOption` (AC8) unmodified.
6. Run `pip install -q -e ".[test]" && pytest` from the repo root. Advances AC9 and AC11. `tests/test_hello.py` must pass unmodified. Dependencies come from the editable install. Do not assume a warm cache.

**Implicit invariants**
- Authorization and tenancy: not applicable. Both changes are local, static lookups.
- Concurrency and idempotency: not applicable. The mapping is immutable module state.
- Validation and error paths: argparse `choices` handles them. Steps 5 and 2 cover them (invalid, empty, missing, wrong case, unknown catalog code).
- Generated deliverables: none, so no `.factory/delivery-assets` entry is needed.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1, 2, 3 | t1 | pdlc-judge-e2e: add Spanish greeting "es": "Hola" to the catalog |
| 4, 5, 6 | t2 | play1: add --lang {en,es} to testbed-hello |

Both work items are covered. They have no dependency on each other.

## Verification and CI gate

**pdlc-judge-e2e**
- Gate: `python3 -m unittest discover -s tests -t .` from the repo root, run once on the committed SHA.
- It needs only the stdlib and runs in a pod.
- The repository has no provider CI workflow, so this local run is the only check.
- To pass, it must show all `CatalogTest` tests passing: 3 existing and 3 new, 0 failures and 0 errors.

**play1**
- Gate: `pip install -q -e ".[test]" && pytest` from the repo root (`.factory/testing.md`), run once on the committed SHA.
- The required layer is `package-api` (`pytest`, production-path). It runs in a pod.
- The authoritative result is the provider `test` job on Python 3.12 at the PR head. The `gate` job must also be green, which means no `CI_FAIL` file.
- The layout gate must pass: changes only under `src/` and `tests/`, no new shell scripts, and every file under 200 KB.
- To pass, the full suite must be green, including the unmodified `tests/test_hello.py` and the existing `TestGreeting`, `TestHelp` and `TestBadOption` tests, plus the new `--lang` tests.
- The change needs no CI configuration in either repo.

## Risks and scope guards

**Risks**
- argparse error and help wording differs across Python 3.10–3.13. Mitigation: assert only exit code, empty stdout, `usage:`, `error`, `en`/`es` and `--lang`. Never assert exact message text or the quoting of choices.
- The `--lang` help text could contain `Hello, world!` and break `TestHelp:40`. Mitigation: use a help string without example output.
- A new doctest in `hello.py` could fail `tests/test_hello.py:27-30`. Mitigation: add no `>>>` examples.

**Scope guards (the implement phase must NOT):**
- Change `hello_world()`, its doctest, `_DESCRIPTION`, `src/testbed_utils/__init__.py`, `pyproject.toml` or `tests/test_hello.py`.
- Change `greeting()` logic or its `KeyError` message in `greetings/catalog.py`.
- Add any language beyond `en`/`es`, translate `world`, or make matching case-insensitive.
- Import, vendor or read the pdlc-judge-e2e catalog from play1. Add no shared module.
- Touch `hello-world/hello.sh`, `qa/*`, their tests, or other play1 modules (`guestbook`, `pdfutils`, ...).
- Add dependencies, a linter, a new test framework or CI configuration.
- Edit or weaken existing tests (`TestGreeting`, `TestHelp`, `TestBadOption`, `CatalogTest`), or skip or delete any check to get green. A blocked check is reported, never weakened.
- Add a `CI_FAIL` file. Edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
