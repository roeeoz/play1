# scripts/hello-world

## Purpose

This directory is the authoritative location for Hello World PDLC smoke-test artifacts. It was created to validate the Halo platform's end-to-end product development lifecycle pipeline — from product intent through scaffolding, implementation, testing, and CI gate — using the simplest possible runnable artifact.

## Usage

Run the Hello World script with:

```shell
bash scripts/hello-world/hello_world.sh
```

## PDLC Note

This folder and its contents exist as a platform test case, not a general-purpose scripting framework. No argument parsing, environment configuration, or cross-platform packaging is provided or intended. The sole purpose is to exercise the Halo PDLC pipeline end-to-end with a minimal, deterministic deliverable.

## Folder Map

| File | Owner | Description |
|------|-------|-------------|
| `hello_world.sh` | F2 — script | Bash script that prints `Hello, World!` and exits 0. Entry point for manual and CI execution. |
| `test/hello_world.bats` | F3 — integration | bats-core test file that executes `hello_world.sh` and asserts the expected output. |
| `.github/workflows/hello-world.yml` | F3 — integration | GitHub Actions CI workflow that runs `shellcheck` and the bats test suite on every push and pull request. |
