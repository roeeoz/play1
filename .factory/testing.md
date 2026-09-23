# Testing

test-gate: pytest
local-test-gate: python3 -m venv .venv && .venv/bin/pip install -e ".[test]" && .venv/bin/python -m pytest
local-test-gate-platforms: darwin/arm64, darwin/amd64, linux/amd64, linux/arm64

The canonical gate is this repository's pytest suite, exactly as
`.github/workflows/ci.yml` runs it: `pip install -e ".[test]"` to install the
package with its test extras, then `pytest` (configuration lives in
`pyproject.toml`: `testpaths = ["tests"]`, `addopts = "-q"`).

No linter, formatter, type-checker or doctest run is configured in this
repository, so `pytest` is the whole test aggregate. The module doctests in
`src/testbed_utils/textutils.py` are style convention only — they are not part
of the gate and prove nothing on their own.

The provider enforces a **second** required job on every pull request: the
`gate` job in `.github/workflows/ci.yml`, which fails if a `CI_FAIL` marker
file exists at the repository root. It is not expressible as a standalone
aggregate command in that workflow, so it is declared below as its own policy
layer rather than folded into `test-gate:`. A change that passes `pytest` but
adds a `CI_FAIL` marker is still red on the provider.

## Running the layers (required environment)

Every layer command below assumes the package has been installed from
`pyproject.toml` and that the resulting environment's `bin` directory is first
on `PATH` — the same condition the provider gate creates with its
`pip install -e ".[test]"` step:

```sh
python3 -m venv .venv
.venv/bin/pip install -e ".[test]"
export PATH="$PWD/.venv/bin:$PATH"   # now `pytest` and `python` are the project's
```

This setup is not optional bookkeeping; it is what makes the layer commands
mean anything:

- **Run the layers with the project environment first on `PATH`.** An ambient
  interpreter may resolve `import testbed_utils` to a *different* editable
  checkout installed elsewhere on the machine, in which case `pytest` fails
  collection (or, worse, passes against code that is not this checkout).
- **`python` comes from the virtualenv.** A bare `python` does not exist on
  every host (macOS ships only `python3`); the virtualenv provides `bin/python`
  so the `installed-package-api` command below resolves to the interpreter that
  has this checkout's distribution installed.

`.venv/` is git-ignored, so this leaves the working tree clean.

<!-- halo:test-layers -->
```json
{
  "layers": [
    {
      "id": "unit",
      "class": "surrogate",
      "command": "pytest",
      "required": true,
      "runBy": "local"
    },
    {
      "id": "installed-package-api",
      "class": "production-path",
      "command": "python -c \"import testbed_utils; assert testbed_utils.word_count('the quick brown fox') == 4; assert testbed_utils.sentence_count('Is this fast? Yes! It works.') == 3; assert testbed_utils.reading_time_minutes(450) == 3\"",
      "required": true,
      "runBy": "local"
    },
    {
      "id": "ci-fail-marker",
      "class": "policy",
      "command": "test ! -f CI_FAIL",
      "required": true,
      "runBy": "local"
    }
  ]
}
```

Notes on the layers:

- `unit` is the provider-canonical gate command itself; the GitHub Actions
  `test` job runs `pytest` verbatim (`.github/workflows/ci.yml`, "Run pytest").
  It is declared `runBy: local` because it also runs in the delivery pod once
  the environment above is in place, so it is proven locally at the delivered
  revision in addition to whatever the provider observes.
- `installed-package-api` executes the artefact this repository actually ships
  — the installed `testbed_utils` distribution — through its package-root
  public API, in a separate process, outside the test suite. It is the
  production-path check for a library whose shipped surface is its importable
  API. The provider does not run it, so this pod must.
- `ci-fail-marker` mirrors the provider's second required job. It adds no
  obligation that the provider does not already enforce: any change failing it
  is already red on the `gate` job.
