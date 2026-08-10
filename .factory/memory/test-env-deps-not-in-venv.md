# pytest and pypdf are not installed in /opt/venv — install to /tmp/pkgs to run tests

The agent venv at `/opt/venv` only contains the agent's own dependencies (anthropic, httpx, etc).
Neither `pytest`, `pypdf`, nor `testbed-utils` itself are installed there.

The package egg-info lives at `/workspace/src/testbed_utils.egg-info`, so
`importlib.metadata.version("testbed-utils")` works when `/workspace/src` is on `sys.path`.

To run tests:
```
pip install --target /tmp/pkgs pypdf pytest
PYTHONPATH="/tmp/pkgs:/workspace/src" python3 -m pytest tests/
```

This matches `pip install -e ".[test]"` from the README but without needing venv write access.
