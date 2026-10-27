# High-Level Design — s1: CLI subcommand: parse two ISO dates and report the day count

## 1. System Overview

**What is being built:** A new CLI subcommand for testbed-utils that accepts two ISO 8601 date strings (with optional trailing Z), computes the absolute calendar-day count between them, and prints the result. It is backed by a new public helper function in `dateutils.py`.

**Problem:** No user-facing CLI exists for date-distance computation. The existing `days_between` is internal, takes `date` objects, and returns a signed value.

**Key responsibilities:** ISO date string parsing (including trailing-Z stripping), input validation with graceful error reporting, absolute day-count computation, CLI argument handling and help text.

## 2. Architecture Overview

- **Single module (`dateutils.py`)** gains one new public function and one `main()` entry point, following the `hello.py` / `pdfutils.py` pattern of co-locating the helper and CLI in the same file.
- **`__init__.py`** adds the new public function to the import line and `__all__`.
- **`pyproject.toml`** gains one `[project.scripts]` entry pointing to `testbed_utils.dateutils:main`.
- **No new modules, packages, or dependencies.**

## 3. Data Flow

1. User invokes the CLI with two positional string arguments.
2. `main()` uses `argparse` to parse the two positional args.
3. Each argument is stripped of an optional trailing Z, then passed to `date.fromisoformat()`.
4. The absolute day count is computed: `abs((d1 - d2).days)`.
5. The result is printed to stdout as a single line of plain text; exit 0.
6. On invalid input, an error message goes to stderr; exit 1.

## 4. Component Breakdown

| Component | Responsibility | Repository |
|---|---|---|
| New public function in `dateutils.py` | Accept two date strings, validate, return absolute day count | roeeoz/play1 |
| `main()` in `dateutils.py` | argparse CLI entry point, error handling, output | roeeoz/play1 |
| `__init__.py` update | Re-export the new public function | roeeoz/play1 |
| `pyproject.toml` update | Register the console script | roeeoz/play1 |
| Unit + CLI tests | Cover happy path, zero-day, invalid input, trailing Z, help | roeeoz/play1 |

## 5. Interface Contracts

- **Public function:** Accepts two `str` arguments (ISO 8601, optional trailing Z), returns `int` (absolute day count), raises `ValueError` on invalid input.
- **CLI:** Two positional arguments, stdout for result, stderr for errors, exit 0 on success, non-zero on failure. `--help` prints a one-line description.
- **Contract for s2:** s2 will extend `main()` to also print weekday listings after the day-count line, reusing the same argparse structure and parsing logic. The two positional args and the parsing/validation path are the stable contract surface.

## 6. Key Technical Decisions

- **Trailing-Z stripping:** `arg.rstrip('Z')` before `date.fromisoformat()` — portable across CPython 3.10+.
- **Co-located `main()`:** Matches `hello.py`/`pdfutils.py` pattern; `test_dateutils.py` does not assert public names, so adding `main` is safe.
- **Separate CLI test file:** Following the repo's established pattern (`test_hello_cli.py`, `test_pdf_extract_cli.py`).
- **Output format:** Deferred to implementer (spec OQ1); either bare number or labeled format is acceptable.

## 7. Risks & Constraints

- **Python 3.10 compatibility:** `date.fromisoformat()` in 3.10 accepts only `YYYY-MM-DD`; trailing Z must be stripped beforehand.
- **s2 extensibility:** `main()` and argparse structure must be cleanly extensible so s2 can add weekday output without refactoring argument parsing.
- **300-line budget:** Estimated at ~200 lines total; well within limit.
