# High-Level Design — F1: Folder Scaffold

## 1. System Overview
- **What:** Commit `scripts/hello-world/README.md` into the `roeeoz/play1` repository, implicitly creating the `scripts/hello-world/` directory as a tracked git path.
- **Problem:** Git does not track empty directories; without a committed file at the target path, downstream features F2 and F3 have no guaranteed location to write into.
- **Responsibilities:** Establish the directory anchor, deliver human-readable documentation covering purpose, usage, PDLC context, and folder map.

## 2. Architecture Overview
- Single file change in a single repository — no services, no runtime components.
- `scripts/hello-world/README.md` is the sole deliverable; the directory is created implicitly by placing the file there.
- No modifications to any pre-existing file (`.github/workflows/ci.yml` is explicitly out of scope).

## 3. Data Flow Design
- Static documentation commit; no runtime data flow.
- Downstream seam: the committed `scripts/hello-world/` path is the contract consumed by F2 (writes `hello_world.sh`) and F3 (writes test + CI workflow).

## 4. Component Breakdown
- **Component:** `scripts/hello-world/README.md`
  - Responsibility: Document purpose, canonical invocation, PDLC context, and expected folder contents.
  - Inputs: None.
  - Outputs: Committed file at `scripts/hello-world/README.md`.
  - Repository: `roeeoz/play1`

## 5. Interface Contracts
- **Outbound seam:** `scripts/hello-world/` directory present and committed — verified by `git ls-files scripts/hello-world/` returning at least one entry.
- No API, event, or cross-repo contract.

## 6. Key Technical Decisions
- README chosen over `.gitkeep` as the committed anchor — provides documentation value at zero extra cost.
- Branch strategy: F1 opens a PR from a new feature branch (e.g. `feature/hello-world`) into `main`; F2 and F3 branch from or stack on the same branch so the directory is guaranteed present.

## 7. Risks & Constraints
- **Forward-reference in folder map:** README lists files (`hello_world.sh`, test file, CI workflow) that do not exist until F2/F3 land. This is intentional per spec.
- **Branch sequencing:** F2 and F3 must not branch from `main` before F1 merges; the platform's `dependsOn` build-order enforcement mitigates this.
- **ci.yml side-effect:** Any PR from this branch triggers the existing Python CI jobs — both will pass since no Python code is touched and no `CI_FAIL` file is created.
