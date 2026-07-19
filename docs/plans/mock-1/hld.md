# High-level design — Add a --json output flag to the CLI

# High-Level Design: testbed-utils CLI Entry Point

## 1. System Overview

**What is being built:** A `testbed-utils` command-line entry point added to the existing `testbed_utils` Python package. The CLI wraps the six already-exported library functions as positional subcommands and adds a global `--json` flag that switches all output (results and errors) from plain text to machine-readable JSON envelopes.

**Problem statement:** Scripting users and CI/CD pipelines cannot consume `testbed_utils` functionality without writing ad-hoc Python wrappers. No CLI exists today.

**Key responsibilities:**
- Install a `testbed-utils` binary on PATH via `pyproject.toml` `[project.scripts]`
- Dispatch to six library functions by subcommand name (kebab-case)
- Coerce string CLI arguments to the types each function requires
- Emit output to stdout in plain-text (`str(result)`) or JSON (`{"result": value}`) format
- Intercept ALL error paths — argparse parse errors and library exceptions — and route them consistently to stderr (plain) or stdout (JSON envelope) controlled by the global `--json` flag

---

## 2. Architecture Overview

All changes are fully contained within the `play1` repository. No new external services, processes, or inter-repo dependencies are introduced.

**Components:**
- `pyproject.toml` — adds `[project.scripts]` entry; no new runtime dependency (argparse is stdlib)
- `src/testbed_utils/cli.py` — new CLI implementation module
- `tests/test_cli.py` — new pytest test suite

**Module ownership:**
- `cli.py` imports from `testbed_utils` (via `__init__.py` / `__all__`); it does NOT modify any library code
- Tests invoke the CLI via `subprocess.run(["testbed-utils", ...])` to exercise the real installed entry point

---

## 3. Data Flow Design

```
User invocation: testbed-utils [--json] <subcommand> [args...]
        │
        ▼
  CustomParser (argparse subclass)
        │  overrides error() → checks '--json' in sys.argv
        │  on parse error:
        │     --json → print({"error":"..."}) to stdout; exit(1)
        │     plain  → print(msg) to stderr;            exit(1)
        │
        ▼
  Argument coercion layer (per subcommand)
        │  date args   → datetime.date.fromisoformat(arg)
        │  delta arg   → timedelta(seconds=int(arg))
        │  int args    → int(arg)
        │  str args    → arg (pass-through)
        │  ValueError  → routed to unified error handler
        │
        ▼
  Library function call
        │  Exception   → routed to unified error handler
        │
        ▼
  Output
        ├── --json success → print(json.dumps({"result": value})); exit(0)
        ├── --json error   → print(json.dumps({"error": msg}));    exit(1)
        ├── plain  success → print(str(result));                    exit(0)
        └── plain  error   → print(msg, file=sys.stderr);           exit(1)
```

Processing is fully synchronous. No queues, background threads, or IPC.

---

## 4. Component Breakdown

### 4.1 CLI Module — `src/testbed_utils/cli.py`

**Responsibility:** Argparse-based dispatcher owning argument parsing, type coercion, function dispatch, and output formatting.

**Key design decisions:**

| Decision | Choice | Rationale |
|---|---|---|
| CLI framework | stdlib argparse | Zero new runtime dependencies; no change to `pyproject.toml` `dependencies` |
| `--json` error interception | `CustomParser` subclass overrides `error()` | Prevents argparse's built-in `sys.exit(2)` + stderr write from corrupting stdout under `--json`; checks `'--json' in sys.argv` (deterministic for a global pre-subcommand flag) |
| `date` coercion | `datetime.date.fromisoformat(arg)` | Matches spec examples; Python 3.7+; raises `ValueError` on malformed input |
| `timedelta` coercion | `timedelta(seconds=int(arg))` | Matches spec example `humanize-delta 3600`; `int()` raises `ValueError` on bad input |
| `truncate` `suffix` param | Optional positional (`nargs="?"`, default `"..."`) | FR2 requires positional args in declaration order; optional positional is consistent |
| JSON serialization | `json.dumps` (stdlib) | Correctly serializes Python `True`/`False` → JSON `true`/`false`; no manual bool check needed |

**Inputs:** `sys.argv`  
**Outputs:** stdout (result or JSON envelope), stderr (plain errors), exit code 0 or 1  
**Repository:** play1

### 4.2 Entry Point Wiring — `pyproject.toml`

**Responsibility:** Declares `testbed-utils = "testbed_utils.cli:main"` under a new `[project.scripts]` table, making the command available on PATH after `pip install -e .`.

**Repository:** play1

### 4.3 Test Suite — `tests/test_cli.py`

**Responsibility:** Class-based pytest suite covering all six subcommands in both plain-text and `--json` modes, plus error paths.

**Test strategy:** `subprocess.run(["testbed-utils", ...], capture_output=True, text=True)` — exercises the real installed entry point (verifies AC1). `json.loads(proc.stdout)` verifies JSON structure.

**Repository:** play1

---

## 5. Interface Contracts

### CLI interface (external)

```
testbed-utils [--json] <subcommand> [args...]

Subcommands:
  days-between    <start:ISO-date> <end:ISO-date>         → int
  humanize-delta  <delta:int-seconds>                     → str
  is-weekend      <day:ISO-date>                           → bool
  slugify         <text:str>                               → str
  truncate        <text:str> <max_length:int> [suffix:str] → str
  word-count      <text:str>                               → int

Global flags:
  --json   Switch all output to JSON envelopes (before subcommand name)
  --help   Print usage and exit 0
```

### JSON success envelope
```json
{"result": <json-number|json-string|json-boolean>}
```

### JSON error envelope (written to stdout; exit 1)
```json
{"error": "<human-readable message>"}
```

---

## 6. Key Technical Decisions

**Argparse error interception:** The only non-trivial engineering challenge is that `ArgumentParser.error()` is called before `parse_args()` completes, so `--json` may not yet appear in the namespace. The solution: in `CustomParser.error()`, inspect `sys.argv` directly for the string `'--json'`. This is safe and deterministic because `--json` is defined as a global flag that must appear before the subcommand name (a well-defined position in `sys.argv`).

**No new runtime dependency:** Using argparse (stdlib) avoids adding a `[project.dependencies]` list to `pyproject.toml`. The CI `pip install -e ".[test]"` command already installs everything needed.

**`truncate` suffix as optional positional:** Exposes the default parameter at the CLI boundary without introducing a named optional flag, keeping the interface consistent with FR2.

---

## 7. Risks & Constraints

| Risk | Severity | Mitigation |
|---|---|---|
| Argparse `error()` fires before full parse; `--json` not yet in namespace | Medium | Check `'--json' in sys.argv` inside `error()` — deterministic for a global pre-subcommand flag |
| `bool` is subclass of `int` in Python | Low | `json.dumps` handles correctly; Python `True` → JSON `true` natively |
| `truncate` with negative `max_length` raises `ValueError` in library | Low | Caught by the uniform `except (ValueError, Exception)` wrapper in dispatch |
| CI installs with `pip install -e ".[test]"` must pick up entry point | Low | `[project.scripts]` is a standard setuptools mechanism; no runtime dep added |
| Tests must run against the installed entry point (AC1) | Low | `subprocess.run(["testbed-utils", ...])` is the correct test strategy; entry point is on PATH after editable install |
