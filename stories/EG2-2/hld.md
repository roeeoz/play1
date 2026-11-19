# HLD — EG2-2: Spanish greeting in both repositories

## 1. System overview

- **What:** add Spanish (`es`, word `Hola`) as a supported greeting language in two independent repositories.
  - `roeeoz/pdlc-judge-e2e` (base `develop`): the `GREETINGS` dict in `greetings/catalog.py:5-7` gains `"es": "Hola"`; `greeting("es")` returns `Hola`.
  - `roeeoz/play1` (base `main`): the `testbed-hello` console script (`pyproject.toml:17` → `testbed_utils.hello:main`, `src/testbed_utils/hello.py:20-23`) accepts optional `--lang {en,es}` (default `en`) and prints `Hola, world!` for `es`.
- **Problem:** both repos greet in English only; `testbed-hello` takes no argument other than `--help`.
- **Responsibility split:** each repo owns its own copy of the word `Hola`; there is no code dependency between them (spec §2 out of scope). Identity (FR9) is enforced by each repo testing against the same literal `Hola`.

## 2. Architecture overview

- **pdlc-judge-e2e — greeting catalog.** Pure-stdlib module `greetings/catalog.py` (dict + lookup function raising `KeyError` for unknown codes). Tests: `tests/test_catalog.py` (unittest). Gate: `python3 -m unittest discover -s tests -t .` (`.factory/testing.md`); no CI workflow, no external deps.
- **play1 — `testbed-hello` CLI.** Module `src/testbed_utils/hello.py`: `hello_world()` (public, exported from `testbed_utils.__init__`, has a doctest) and `main()` (argparse, prog `testbed-hello`, description `_DESCRIPTION`). Tests: `tests/test_hello.py` (function, export, doctest) and `tests/test_hello_cli.py` (drives `main()` with patched `sys.argv`, captures stdout/stderr/exit code). Gates: CI `test` job (`pip install -e ".[test]"` + `pytest`, Python 3.12, `.github/workflows/ci.yml`), `gate` job (`CI_FAIL` marker), and the layout gate `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (Python under `src/`, tests under `tests/`, new shell scripts executable with shebang, no file > 200 KB).
- No `CLAUDE.md`, `AGENTS.md` or `.factory/memory/` exists in either repo.
- External dependencies: none new (argparse is stdlib).

## 3. Data flow

- **Catalog (sync, in-process):** caller → `greeting(lang)` → membership check on `GREETINGS` → return word, or raise `KeyError`.
- **CLI (sync, single process):** `testbed-hello [--lang L]` → argparse validates `L ∈ {en, es}` (default `en`) → greeting word for `L` → stdout `"<Word>, world!\n"`, exit 0. Invalid/missing value → argparse prints usage + error to stderr, exits 2 before any greeting is printed. `--help` → usage on stdout, exit 0, no greeting.
- No persistence, no events, no network.

## 4. Component breakdown

| Component | Responsibility | Inputs / outputs | Repository |
| --- | --- | --- | --- |
| Greeting catalog (`greetings/catalog.py`) | Map language code → greeting word | `lang` str → word, or `KeyError` | roeeoz/pdlc-judge-e2e |
| Catalog tests (`tests/test_catalog.py`) | Assert `es` → `Hola`; keep existing assertions | — | roeeoz/pdlc-judge-e2e |
| `testbed-hello` CLI (`src/testbed_utils/hello.py`) | Parse `--lang`, print greeting line | argv → stdout line / stderr usage + exit code | roeeoz/play1 |
| CLI + function tests (`tests/test_hello_cli.py`, `tests/test_hello.py`) | Cover default, `en`, `es`, invalid, help, `hello_world()` unchanged | — | roeeoz/play1 |

## 5. Interface contracts

- **Catalog (Python API):** `greeting("es") == "Hola"`; `greeting("en") == "Hello"`; `greeting("xx")` raises `KeyError`; `GREETINGS` keys exactly `{"en", "es"}`. Every value stays a single alphabetic, capitalised word (existing test).
- **CLI (observable, verified with Python 3.13 argparse in this turn):**

| Invocation | stdout | stderr | exit |
| --- | --- | --- | --- |
| `testbed-hello` | `Hello, world!\n` | empty | 0 |
| `testbed-hello --lang en` / `--lang=en` | `Hello, world!\n` | empty | 0 |
| `testbed-hello --lang es` / `--lang=es` | `Hola, world!\n` | empty | 0 |
| `testbed-hello --lang fr` (or `ES`, any non-`en`/`es`) | empty | `usage: testbed-hello [-h] [--lang {en,es}]` + `error: argument --lang: invalid choice: ...` | 2 |
| `testbed-hello --lang` (no value) | empty | usage + `error: argument --lang: expected one argument` | 2 |
| `testbed-hello --help` | usage mentioning `--lang {en,es}`, existing `_DESCRIPTION`, no `Hello, world!` / `Hola, world!` | empty | 0 |

- Values are case-sensitive (`ES` is rejected). A repeated `--lang` takes the last value (argparse default; not specified, not tested as a requirement).
- `hello_world()` keeps its signature and return value `Hello, world!` and stays exported from `testbed_utils`.
- **Cross-repo contract:** none at runtime. FR9 is the shared literal `Hola`, asserted independently in each repo's tests.

## 6. Key technical decisions

- **argparse `choices`** for `--lang` (default `en`): gives exactly the FR6 rejection behaviour (usage + error on stderr, exit 2, nothing on stdout) that the existing bad-option tests (`tests/test_hello_cli.py:44-52`) already pin, with no custom validation. Alternative (free string + manual check) rejected: duplicates argparse and risks a different error shape.
- **`hello_world()` untouched**; the Spanish line is produced inside `hello.py` by whatever small internal mapping the implementer chooses. Changing `hello_world()`'s signature was rejected to keep its doctest, export and spec §2 guarantee intact.
- **No shared code between repos** (spec §2): play1 must not import the catalog. Duplicating one word is cheaper and safer than a cross-repo dependency.
- **Two independent tickets, no `dependsOn`:** the repos share nothing at build time; each PR can merge on its own and be built in parallel.

## 7. Risks, constraints and assumptions

- **Risk — drift of `Hola` between repos (FR9):** mitigated by each repo's tests asserting the exact literal `Hola` (play1: exact stdout `Hola, world!\n`).
- **Risk — help text leaking a greeting:** the `--lang` help string must not contain `Hello, world!` (existing help test) nor `Hola, world!`.
- **Constraint — argparse abbreviation:** `allow_abbrev` is on by default, so `--la es` is accepted. Existing behaviour for the parser; harmless and not changed.
- **Constraint — Python versions:** CI runs 3.12; argparse `choices` error wording differs slightly across versions, so tests assert `usage:` and `error` in stderr (as existing tests do), not the full message.
- **Constraint — gates:** play1 changes stay under `src/` and `tests/`, no new shell scripts, no large files, no `CI_FAIL`. pdlc-judge-e2e tests stay stdlib `unittest`.
- **Assumption (from spec §8):** unsupported `--lang` is rejected with exit 2 like any bad argument; no epic PRD/backlog was available, design rests on the spec and the code.
- Performance, scale and security: not applicable beyond the above (in-process string lookup, no I/O beyond stdout).
