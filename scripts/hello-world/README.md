# Hello World — PDLC Smoke-Test

## Purpose

This directory is the authoritative location for Hello World PDLC smoke-test artifacts. It was created to validate the Halo platform's end-to-end product development lifecycle pipeline.

## Usage

Run the script with:

```shell
bash scripts/hello-world/hello_world.sh
```

## PDLC Note

This folder and its contents exist as a platform test case, not a general-purpose scripting framework. The files here are deliberately minimal and serve only to exercise the Halo PDLC pipeline from feature definition through to CI validation.

## Folder Map

| File | Description |
|------|-------------|
| `hello_world.sh` | The primary bash script; prints `Hello, World!` and exits 0. Owned by F2. |
| `test/hello_world.bats` | bats-core test file; asserts the script exits 0 and produces the expected output. Owned by F3. |
| `.github/workflows/hello-world.yml` | GitHub Actions CI workflow; runs shellcheck and the bats test on every push and pull request. Owned by F3. |
