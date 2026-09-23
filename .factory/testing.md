# Testing

test-gate: pytest

The gate is the repository's pre-existing canonical command, unchanged. It is
what `README.md` documents for local development and what `.github/workflows/ci.yml`
runs as its own step (`- name: Run pytest` / `run: pytest`) after
`pip install -e ".[test]"` on the provider's standard hosted runner. This file
only declares that gate and what it proves; it does not add, rename, narrow, or
replace any check.

## What the gate proves

`testbed-utils` ships as an importable Python distribution (`src/testbed_utils`,
plus the `pdf-extract` console script declared in `pyproject.toml`). CI installs
that distribution with `pip install -e ".[test]"` and the suite then imports the
installed package — `from testbed_utils.dateutils import ...`,
`from testbed_utils.pdfutils import main` — and calls the shipped functions
directly. For a library, that importable surface is the artefact the repository
ships, so the suite is classified `production-path` rather than `surrogate`: no
stub, fake, or re-implementation stands in for the code that is published.

One honest limit, pre-existing and not introduced here:
`tests/test_pdf_extract_cli.py` exercises the `pdf-extract` CLI by patching
`sys.argv` and calling `pdfutils.main()` in-process, so it executes the shipped
command's code but not the console-script entry-point wiring via a subprocess.
That gap belongs to the `pdf-extract` script, not to this delivery's artefact.

The repository configures no linter, formatter, or type checker, so `pytest` is
the entire gate. There is no licence, compliance, or dependency-policy check to
declare.

<!-- halo:test-layers -->
```json
{
  "layers": [
    {
      "id": "pytest-suite",
      "class": "production-path",
      "command": "pytest",
      "required": true,
      "runBy": "local"
    }
  ],
  "policyNotApplicable": "The repository declares no licence, compliance, or dependency-policy check: pyproject.toml sets a single license field and one runtime dependency (pypdf), and neither the CI workflow nor any config file runs a policy scanner. There is no such layer to declare."
}
```
