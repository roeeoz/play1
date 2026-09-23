# Testing

test-gate: pytest

The canonical gate is this repository's pytest suite, exactly as
`.github/workflows/ci.yml` runs it: `pip install -e ".[test]"` to install the
package with its test extras, then `pytest` (configuration lives in
`pyproject.toml`: `testpaths = ["tests"]`, `addopts = "-q"`).

No linter, formatter, type-checker or doctest run is configured in this
repository, so `pytest` is the whole gate. The module doctests in
`src/testbed_utils/textutils.py` are style convention only — they are not part
of the gate and prove nothing on their own.

Both layers below run in an environment where the package has been installed
from `pyproject.toml`, exactly as the provider gate installs it.

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
    }
  ],
  "policyNotApplicable": "This repository declares no licence, compliance or dependency-policy checks. It is a proprietary single-dependency fixture package (pypdf) with no SBOM, licence-scan or dependency-audit tooling configured in pyproject.toml or the CI workflow, so there is no policy layer to run."
}
```

Notes on the layers:

- `unit` is the provider-canonical gate command itself; the GitHub Actions
  `test` job runs `pytest` verbatim. It also runs in the delivery pod, so it is
  declared `runBy: local` and proven locally at the delivered revision in
  addition to whatever the provider observes.
- `installed-package-api` executes the artefact this repository actually ships
  — the installed `testbed_utils` distribution — through its package-root
  public API, in a separate process, from outside the test suite. It is the
  production-path check for a library whose shipped surface is its importable
  API.
