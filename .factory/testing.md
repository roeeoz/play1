# Testing

test-gate: pytest

The repository's canonical gate is the `test` job in `.github/workflows/ci.yml`:
`pip install -e ".[test]"` (precondition) followed by `pytest` as its own step,
on Python 3.12. `pytest` is the aggregate gate command — run it from the repo
root after the editable install. There is no linter, formatter, type checker or
coverage tool configured anywhere in this repository, so install + `pytest` is
the complete pre-merge check.

The workflow's second job, `gate`, fails if and only if a file named `CI_FAIL`
exists at the repository root. It is a deterministic testbed switch, not a
quality check, and it is not a declared layer.

## What the gate proves

`pytest` is a production-path layer here, not a surrogate. The package uses a
setuptools `src/` layout (`[tool.setuptools.packages.find] where = ["src"]`)
and the suite contains no `conftest.py` and no `sys.path` manipulation, so the
only way a test can import `testbed_utils` is through the installed
distribution. Every test therefore exercises the artefact the repository
actually ships, through its real public import surface — including
`tests/test_pdf_extract_cli.py`, which drives the `pdf-extract` console
entry point's `main()` over real PDF fixtures.

`runBy` is `canonical-gate` because the repository's own gate owns this
command: `.github/workflows/ci.yml` runs `pytest` as its own step in the
`test` job on every `pull_request`, so the layer is credited from the
provider run observed at the exact head. The command also runs unprivileged
in a local pod (`pip install -e ".[test]" && pytest`), and running it locally
is a useful pre-push check — but a local run can only ever observe the tree
before the delivery commit exists, so the provider run at the exact head is
the authoritative result for this layer.

<!-- halo:test-layers -->
```json
{
  "layers": [
    {
      "id": "package-api",
      "class": "production-path",
      "command": "pytest",
      "required": true,
      "runBy": "canonical-gate"
    }
  ],
  "policyNotApplicable": "This repository configures no licence, compliance or dependency-policy check: pyproject.toml declares a single proprietary-licensed package with one runtime dependency (pypdf) and one test extra (pytest), and no SBOM, licence-scan, audit or dependency-review step exists in .github/workflows/ci.yml or anywhere else in the repo. There is no such layer to declare."
}
```
