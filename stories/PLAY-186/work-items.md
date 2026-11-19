# Work-item breakdown — כלי הברכה פונה למשתמש בשמו, ובלי שם ממשיך לברך את העולם

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | testbed-hello: greet by optional name, default to Hello, world! |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "testbed-hello: greet by optional name, default to Hello, world!",
    "summary": "**Intent:** Teach the `testbed-hello` console script to accept one optional name after the command and print `Hello, <name>!`, keeping `Hello, world!` byte-identical when no usable name is given, with help and error behaviour preserved (PLAY-186, Epic PLAY-185, R1–R5). Single component in roeeoz/play1.\n\n**Owns:** `src/testbed_utils/hello.py` (greeting function + CLI `main()` + one-line help summary), `tests/test_hello_cli.py`, `tests/test_hello.py`; `src/testbed_utils/__init__.py` only if a new public function is exported.\n**Consumes (unchanged):** `pyproject.toml` entry point `testbed-hello = \"testbed_utils.hello:main\"`, `.factory/testing.md` gate. Must not touch `hello-world/hello.sh`, `qa/`, other tools or CI.\n\n**Acceptance criteria:**\n- `testbed-hello Dana` prints exactly the single line `Hello, Dana!` on stdout, nothing on stderr, exit 0.\n- `testbed-hello` with no argument prints exactly `Hello, world!` + newline (identical to today), exit 0.\n- `testbed-hello \" dana \"` prints `Hello, dana!` (case kept, leading/trailing whitespace removed), exit 0.\n- `testbed-hello \"Dana Star\"` prints `Hello, Dana Star!`, exit 0.\n- `testbed-hello \"\"` and `testbed-hello \" \"` print `Hello, world!`, exit 0.\n- `testbed-hello --help` prints usage, one summary line of the tool (≤ 76 chars, one line at 80 columns) and a description of the optional name including an example name, no greeting line, empty stderr, exit 0.\n- `testbed-hello --bogus` and `testbed-hello -x` print nothing on stdout, usage and an `error` line on stderr, no greeting, exit 2 (as today).\n- Two unquoted words (`testbed-hello Dana Star`) are rejected: nothing on stdout, usage + error on stderr, no greeting, exit 2.\n- A dash-led word given as the name (e.g. `-1`, `-`) is rejected like an unknown option (usage + error on stderr, no greeting, exit 2); after the `--` separator a dash-led name is greeted literally (`testbed-hello -- -x` prints `Hello, -x!`).\n- The previous expectation that the bare word `extra` is rejected is replaced by a test that it is greeted (RK2); `--bogus`/`-x` rejection tests remain.\n- The exported `testbed_utils.hello_world()` called with no argument still returns `Hello, world!` and stays in `testbed_utils.__all__`; every new or changed public function has a docstring with a runnable `>>>` example that passes under the existing doctest test.\n- Tests cover the happy path, each edge case above and the error cases; only fictitious names (Dana, Dana Star) appear; tests use no network, clock or files outside `tests/fixtures`.\n- No new dependency; change stays under 300 lines; `pip install -e \".[test]\" && pytest` passes on Python 3.10+ (CI 3.12), asserting on help content rather than version-specific headings.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
