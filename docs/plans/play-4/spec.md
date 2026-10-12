## Story
As a maintainer I want one shared shell helper file that the release scripts source, so the version string is computed in one place.

## Acceptance criteria
1. The repo gains `scripts/lib/common.sh` defining a function `project_version` that prints the version from `pyproject.toml`.
2. The file is a library that other scripts source with `. scripts/lib/common.sh`; it is not run directly, so it has no shebang line and is not executable.
3. A unit test under `tests/` runs `bash -c ". scripts/lib/common.sh; project_version"` and checks the printed version matches pyproject.toml.
