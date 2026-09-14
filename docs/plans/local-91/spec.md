# Feature Specification Document

## 1. Feature Overview

F1 — Folder Scaffold establishes `scripts/hello-world/` as the committed, documented anchor directory for all Hello World PDLC smoke-test artifacts. It delivers a single `README.md` covering four required content sections. No script, test, or CI file is created here.

**Problem statement:** Git does not track empty directories. Without a committed file in the target path, downstream features (F2: script, F3: tests + CI) have no guaranteed location to write into. Contributors also need human-readable context explaining why the folder exists and what belongs in it.

**Target users / actors:**
- Contributors encountering the folder for the first time after cloning.
- Downstream automation (F2, F3) that depends on the directory being present before writing into it.

---

## 2. Goals & Non-Goals

### Goals
- Commit `scripts/hello-world/` as a persistent directory in the repository root.
- Deliver `scripts/hello-world/README.md` covering all four required sections.
- Establish the canonical usage command as the human-readable entry point for the folder.

### Non-Goals
- Creating `hello_world.sh` — owned by F2.
- Creating any test file — owned by F3.
- Creating any CI workflow file — owned by F3.
- Modifying the existing `.github/workflows/ci.yml`.
- Adding a `.gitkeep` (the README satisfies the committed-file requirement on its own).

---

## 3. Functional Requirements

- **FR1**: The directory `scripts/hello-world/` MUST exist as a committed path in the repository root.
- **FR2**: `scripts/hello-world/README.md` MUST exist and be committed.
- **FR3**: The README MUST contain a **Purpose statement** identifying the folder as the authoritative location for Hello World PDLC smoke-test artifacts, created to validate the Halo platform's end-to-end product development lifecycle pipeline.
- **FR4**: The README MUST contain a **Usage instruction** section with the exact command `bash scripts/hello-world/hello_world.sh` presented verbatim inside a fenced shell code block.
- **FR5**: The README MUST contain a **PDLC note** stating that this folder and its contents exist as a platform test case, not a general-purpose scripting framework.
- **FR6**: The README MUST contain a **Folder map** listing each expected file in the folder (the script, the test file, and the CI workflow) with a brief description of each.
- **FR7**: No file other than `README.md` SHALL be created by this feature, inside or outside `scripts/hello-world/`.

---

## 4. User Experience & Behavior

**First-time contributor flow:**
1. Contributor clones the repository and navigates to `scripts/hello-world/`.
2. They see `README.md` immediately — no guessing what the folder is for.
3. Reading the README they learn the canonical invocation, the PDLC context, and what files to expect once F2 and F3 have landed.

**Downstream feature flow (F2, F3):**
1. F2 begins implementation knowing `scripts/hello-world/` already exists and writes `hello_world.sh` into it without needing to create the directory.
2. F3 begins knowing both the directory and the script exist and writes the test file and CI workflow without recreating any predecessor artifact.

**Edge case — contributor cloning between F1 and F2:**
The folder map in the README references `hello_world.sh`, the bats test file, and the CI workflow as expected files, none of which exist yet. This forward-documentation mismatch is cosmetic and intentional for a smoke-test repository.

---

## 5. Acceptance Criteria

- **AC1**: `scripts/hello-world/` is present as a committed directory (`git ls-files scripts/hello-world/` returns at least one entry).
- **AC2**: `scripts/hello-world/README.md` exists and is committed.
- **AC3**: `README.md` contains a purpose statement identifying the folder as the authoritative location for Hello World PDLC smoke-test artifacts.
- **AC4**: `README.md` contains the exact fenced shell code block with `bash scripts/hello-world/hello_world.sh` as the usage command — no variation in path or command name.
- **AC5**: `README.md` contains a PDLC note stating the folder exists as a platform test case, not a general-purpose scripting framework.
- **AC6**: `README.md` contains a folder map section listing the expected script, test file, and CI workflow with brief descriptions of each.
- **AC7**: No file named `hello_world.sh`, no test file, and no CI workflow file exists under `scripts/hello-world/` after this feature lands.
- **AC8**: No changes are made to `.github/workflows/ci.yml` or any other pre-existing file in the repository.

---

## 6. Dependencies & Constraints (product-level)

- **Inbound dependencies:** None. F1 is the root of the dependency chain and consumes nothing from other features.
- **Outbound seam:** The committed `scripts/hello-world/` directory is the shared contract that F2 and F3 depend on. F1 MUST land on the shared branch before either downstream feature begins.
- **Locked path:** `scripts/hello-world/` is fixed by the Foundation Contract; renaming is out of scope.
- **Locked invocation string:** `bash scripts/hello-world/hello_world.sh` must appear verbatim in the README with no substitution.

---

## 7. Technical Design (deferred to STRUCTURE)

Branching strategy (main vs. shared feature branch), commit structure, and tooling choices are deferred to the STRUCTURE stage. The one product-imposed constraint is that the committed directory must be present on whatever branch F2 and F3 will build on.

---

## 8. Open Questions

- **Branch target:** The repository currently has only a `main` branch. The Foundation Contract does not specify whether F1 pushes directly to `main` or to a dedicated shared feature branch. The STRUCTURE stage must resolve this before implementation, since F2 and F3 must build on the same branch as F1.
