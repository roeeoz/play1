# Feature Specification Document

## 1. Feature Overview
- **Summary:** The repository has a minimal, runnable hello-world bash script, `hello.sh`, in its own folder, `hello-world`. Run directly, it prints exactly "hello world" and exits successfully.
- **Problem statement:** Developers in this repository want a verified, runnable starting point for shell scripting that doesn't clutter existing directories.
- **Target users / actors:** a developer working in this repository.
- **Current state of the target branch (`main`, b7b5d0a):** `hello-world/hello.sh` already exists. Commit 65938b5 added it. Its content is `#!/bin/bash` followed by `echo "hello world"`, it is stored as executable (mode 100755), and it is the only file in `hello-world/`. Running `./hello-world/hello.sh` prints `hello world` followed by one line break and exits with 0. `tests/test_hello_sh.py` already checks the exit code, the exact output, the empty error output, the shebang, the executable bit and the folder isolation, and its 6 tests pass. The repository runs `pytest` on every pull request.

## 2. Goals & Non-Goals
### Story context
This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A folder named `hello-world` exists at the repository root and contains only `hello.sh`.
- `hello.sh` starts with the shebang `#!/bin/bash` and is executable, so a developer can run it as `./hello-world/hello.sh` without typing `bash`.
- Running it prints exactly the lowercase text `hello world` to standard output and exits with code 0.
- Delivery shows that each acceptance criterion holds on the target branch. Under assumption A1, the existing script already meets them, so the delivery is that confirmation.

### Non-Goals
- Additional scripts.
- CI/CD integration, including any change to the repository's workflows.
- Documentation files: no README in `hello-world/` and no other documentation for this story.
- Rewriting, renaming or moving the existing `hello-world/hello.sh`, or adding any other file to `hello-world/`.

## 3. Functional Requirements
- **FR1: location.** The repository contains a folder named `hello-world` at its root, and inside it a file named `hello.sh`.
- **FR2: folder isolation.** `hello.sh` is the only file in `hello-world`.
- **FR3: direct execution.** `hello.sh` starts with the line `#!/bin/bash` and has executable permissions. Running `./hello-world/hello.sh` from the repository root runs the script without invoking `bash` explicitly.
- **FR4: output.** When run, the script writes the lowercase text `hello world` to standard output. There is no leading whitespace, no trailing space or tab, and no other line. The output ends with a single line break (assumption A2).
- **FR5: exit status.** The script exits with code 0.
- **Inputs:** none. The script takes no arguments and reads no input.
- **Outputs:** the standard output described in FR4, and exit code 0.
- **Edge case:** the output is captured and compared exactly, as in criterion 4. It is the single line `hello world`, with nothing before it, nothing after it on the same line, and no further lines.

## 4. User Experience & Behavior
- **Main flow:** from the repository root, a developer runs `./hello-world/hello.sh`. The terminal shows `hello world` on one line, and the shell returns exit status 0.
- **Folder check:** a developer lists `hello-world/` and sees only `hello.sh`.
- **Output format:** plain lowercase `hello world`, with no prefix, suffix, colour or extra lines.
- **User-facing error states:** the story defines none. The script has no failure path.

## 5. Acceptance Criteria
1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)
- **Requirement source:** the story text and its four acceptance criteria are the whole requirement, as the developer stated in this intake. Where they are silent, the simplest reading is taken and recorded as an assumption below.
- **Existing deliverable:** `hello-world/hello.sh` and `tests/test_hello_sh.py` are already on `main`. The story calls the folder "new", but under A1 it is met by what is already there.
- **Other stories:** other stories in this repository (PLAY-156, PLAY-172) treat `hello-world/hello.sh` as existing and unchanged. Keeping the script as it is keeps those stories' expectations intact.
- **Repository gate:** `pytest` runs on every pull request. Whatever this story delivers has to keep the existing tests green. That gate can't be waived. The factory never merges: a person merges the pull request after review.
- **Traceability:** the story traces to R1–R4, steps 1–4 and RK1 of the epic. That material wasn't available to this intake, so the trace couldn't be checked.

## 7. Technical Design (deferred to STRUCTURE)
STRUCTURE decides how delivery is shown and whether a pull request is opened when nothing needs to change. For example, the delivery could be test evidence that maps each criterion to the existing checks. Any change STRUCTURE proposes must not add files to `hello-world/`, must not change the script's output, and must keep `tests/test_hello_sh.py` consistent with the script.

### Assumptions (simplest reading, per the developer's instruction)
- **A1: done means the existing script is confirmed, not rebuilt.** `main` already meets all four criteria, so the delivery confirms this and leaves `hello-world/hello.sh` and its tests unchanged. *Risk if wrong:* if a fresh or different implementation was intended, this story delivers no change and would have to be reopened.
- **A2: one trailing line break is allowed.** In criterion 4, "no trailing whitespace and no additional lines" allows the single line break that ends the `hello world` line. It rules out spaces or tabs and any second line. *Risk if wrong:* if a consumer needs the bare 11 characters with no line break, both the script and its test have to change, which collides with PLAY-172's requirement that the script stays unchanged.
- **A3: no decisions are carried over.** No decisions were reused from the earlier stories with the same title (SCRUM-1, SCRUM-2). This spec stands on the story text and this intake alone.

## 8. Open Questions
- Delivery mechanics, for STRUCTURE and not the product: if the factory can't open a pull request with no changes, how is the evidence for A1 delivered? Any answer must still leave `hello-world/` and the script's output unchanged.
- The epic trace IDs (R1–R4, steps 1–4, RK1) haven't been checked against the epic material.
