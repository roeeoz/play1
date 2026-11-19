# HLD — EG2-1: Spanish greeting in both repos

## 1. System Overview

- **What:** add Spanish (`es` → `Hola`) as a second greeting language in two independent repositories.
  - `roeeoz/pdlc-judge-e2e` (base `develop`): one new entry in the greeting catalog `greetings/catalog.py` (`GREETINGS`, today `{"en": "Hello"}`), plus a unittest.
  - `roeeoz/play1` (base `main`): an optional `--lang {en,es}` option on the `testbed-hello` console script (`src/testbed_utils/hello.py`, entry point `testbed-hello = "testbed_utils.hello:main"` in `pyproject.toml`), plus pytest coverage.
- **Problem:** both repos only greet in English; the story adds Spanish with one shared word, `Hola` (capital H, no accent, no punctuation).
- **Responsibilities:** each repo owns its own change and its own tests; there is no runtime link between them. The shared value is kept consistent by both work items' acceptance criteria pinning the literal `Hola`.

## 2. Architecture Overview

- **pdlc-judge-e2e — greeting catalog.** `greetings/catalog.py` holds the `GREETINGS` dict and `greeting(lang)`, which raises `KeyError` for unknown codes (catalog.py:17-19). Tests in `tests/test_catalog.py` (stdlib `unittest`) already include a rule that every greeting is a capitalised alphabetic word (`Hola` satisfies it). Only data changes; `greeting()` is untouched.
- **play1 — `testbed-hello`.** `src/testbed_utils/hello.py` defines `_DESCRIPTION`, `hello_world()` (returns `"Hello, world!"`, with a doctest pinned by `tests/test_hello.py`) and `main()`, which builds an `argparse.ArgumentParser(prog="testbed-hello", description=_DESCRIPTION)` and prints `hello_world()`. The change lives entirely inside this module: `main()` gains the `--lang` option and selects the greeting from it. `hello_world()`, `_DESCRIPTION` and the package export in `src/testbed_utils/__init__.py` are unchanged.
- **External dependencies:** none new. play1 uses stdlib `argparse`; pdlc-judge-e2e uses only the stdlib.
- **Boundaries:** play1 does not import or read the pdlc-judge-e2e catalog (spec Non-Goal). Other play1 greeting scripts (`hello-world/hello.sh`, `qa/*`) are out of scope.

## 3. Data Flow Design

All synchronous, in-process; no events, I/O beyond stdout/stderr, or persisted state.

- **Catalog:** caller → `greeting("es")` → lookup in `GREETINGS` → `"Hola"`; unknown code → `KeyError` (unchanged).
- **CLI:** `sys.argv` → argparse (`--lang`, choices `en`/`es`, default `en`) → language-to-greeting selection → one line on stdout, exit 0. An invalid or missing `--lang` value is rejected by argparse before anything is printed: usage + error on stderr, exit 2.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
| --- | --- | --- | --- |
| Greeting catalog (`greetings/catalog.py`) + `tests/test_catalog.py` | Map language code → greeting word; add `"es": "Hola"` | `lang` str → word str / `KeyError` | `roeeoz/pdlc-judge-e2e` (181c059c-…) |
| `testbed-hello` CLI (`src/testbed_utils/hello.py`) + `tests/test_hello_cli.py` | Parse `--lang`, print the greeting | argv → stdout line, stderr, exit code | `roeeoz/play1` (674de8fd-…) |

## 5. Interface Contracts

**Catalog (Python API, pdlc-judge-e2e):** `greeting("en")` → `'Hello'`; `greeting("es")` → `'Hola'`; any other code (e.g. `"xx"`, `"ES"`) → `KeyError` as today. `GREETINGS == {"en": "Hello", "es": "Hola"}`.

**CLI (play1), behaviour verified with stdlib argparse:**

| Invocation | stdout | stderr | exit |
| --- | --- | --- | --- |
| `testbed-hello` | `Hello, world!\n` | empty | 0 |
| `testbed-hello --lang en` / `--lang=en` | `Hello, world!\n` | empty | 0 |
| `testbed-hello --lang es` / `--lang=es` | `Hola, world!\n` | empty | 0 |
| `--lang fr`, `--lang ES`, `--lang ""` | empty | `usage:` line + `error: argument --lang: invalid choice: ...` naming `en`, `es` | 2 |
| `--lang` (no value) | empty | `usage:` line + `error: argument --lang: expected one argument` | 2 |
| `--lang es --lang en` | last value wins (`Hello, world!`) — argparse default | empty | 0 |
| `--help` | usage containing `[--lang {en,es}]`, the unchanged `_DESCRIPTION` sentence, and an options entry for `--lang` | empty | 0 |
| `--bogus`, `-x`, `extra` | empty | usage + error | 2 (unchanged) |

**Cross-repo contract:** the Spanish word is the literal `Hola` in both. No code-level coupling.

## 6. Key Technical Decisions

- **play1: keep `hello_world()` unchanged; select the greeting in the CLI layer** (a small language→greeting mapping in `hello.py`, the implementer's choice of shape). Rationale: `tests/test_hello.py` pins `hello_world() == "Hello, world!"`, its doctest and its export; spec §7 requires both to survive. Alternative (adding an optional `lang` parameter to `hello_world()`) is acceptable only if the no-argument call and doctest are unchanged — left to the implementer within that constraint.
- **Validation via argparse `choices`**, so invalid values get the command's existing rejection path (usage + error on stderr, exit 2) — matches `TestBadOption` and FR9. Case-sensitive (`ES` rejected) per spec §8.
- **No shared module between repos** (spec Non-Goal); consistency enforced by tests in each repo asserting the literal `Hola`.
- **Tests organisation:** pdlc-judge-e2e extends `tests/test_catalog.py`; play1 extends `tests/test_hello_cli.py` using its existing `run_main` helper (drives the real `main()` through the installed package — the declared production-path layer in `.factory/testing.md`).

## 7. Risks & Constraints

- **argparse error text varies across Python versions** (play1 supports `>=3.10`, CI runs 3.12; this design was checked on 3.13). Tests must assert stable parts only — exit code 2, empty stdout, `usage:` and `error` on stderr, and that `en`/`es` are named — never the exact quoting of the choices list.
- **Help text:** `TestHelp` asserts `_DESCRIPTION` appears in help (whitespace-normalised) and that `Hello, world!` does not appear in help; the `--lang` help string must not contain `Hello, world!`.
- **Abbreviation (assumption, accepted):** argparse's default `allow_abbrev` makes `--la es` resolve to `--lang es`. Prefixes of `--lang` were previously rejected; accepting them is inherent to adding the option the standard way and is not called out by the spec. Risk is negligible; no test should rely on it either way.
- **Gates:** play1 — CI `test` (`pip install -e ".[test]"` + `pytest`), `gate` (no `CI_FAIL`), layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`: source in `src/`, tests in `tests/`, no file >200 KB). pdlc-judge-e2e — `python3 -m unittest discover -s tests -t .` (no CI workflow). Neither repo has `CLAUDE.md`/`AGENTS.md`/`.factory/memory/`.
- **Scale/security:** not applicable — a static string lookup and a local CLI with no external input beyond argv.
- **Integration:** the two PRs are independent; either can merge first.
