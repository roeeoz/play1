# Feature Specification Document

## 1. Feature Overview
- **Summary:** add a new top-level folder `hello-world/` to the repository. It holds one bash script, `hello.sh`, that a developer can run directly and that prints `hello world`.
- **Problem statement:** a developer in this repository has no minimal, verified shell script to start from. The repository has no shell scripts today, and its only hello feature is written in Python. The new script must not clutter existing directories (source: the story's user story and context).
- **Target users / actors:** a developer working in this repository who needs a minimal runnable shell script as a starting point.

## 2. Goals & Non-Goals
### Goals
- A dedicated `hello-world/` folder at the repository root that holds only `hello.sh`.
- `hello.sh` runs directly as `./hello-world/hello.sh`, without being passed to bash, because it has the `#!/bin/bash` shebang and executable permission.
- Running the script prints exactly the lowercase text `hello world` and exits with code 0.

### Non-Goals (from the story's out-of-scope list, and the simplest reading of it)
- Any additional scripts.
- CI/CD integration: no change to pipeline configuration.
- Documentation files: none is created, and no existing one is edited, including the repository readme.
- Any change to the repository's existing Python hello feature (its module, its `testbed-hello` command and its tests). That feature prints `Hello, world!`, a different text, and stays exactly as it is.

## 3. Functional Requirements
- **FR1:** The repository contains a top-level folder named `hello-world`.
- **FR2:** The `hello-world` folder contains exactly one file, `hello.sh`, and nothing else.
- **FR3:** The first line of `hello.sh` is the shebang `#!/bin/bash`.
- **FR4:** `hello.sh` is executable, and the permission is recorded in the repository, so it is still executable in a fresh clone.
- **FR5:** Running `hello.sh` writes one line to standard output: the lowercase text `hello world` (one space between the words, no punctuation), ended by a single line break. Nothing comes before the text. No spaces or tabs come after it. There is no second line.
- **FR6:** Running `hello.sh` ends with exit code 0.
- **Inputs:** none. The script takes no arguments and reads no input.
- **Outputs:** the line described in FR5 on standard output, and exit code 0.
- **Edge cases:** the output is the same no matter which directory the script is run from. The script gives the same output on every run.

## 4. User Experience & Behavior
- **Main flow:** from the repository root, the developer runs `./hello-world/hello.sh`. The terminal shows `hello world` on a line of its own and the command ends successfully.
- **Direct execution:** the developer doesn't have to type `bash hello.sh`. The script runs as a command on its own.
- **Output format:** a single line containing exactly lowercase `hello world`, followed by the line break that ends the line. No leading or trailing spaces or tabs, no other characters and no other lines.
- **Folder contents:** listing `hello-world/` shows only `hello.sh`.
- **States and errors:** there are no other states and no error messages the user sees. The script has one behaviour and it always succeeds.

## 5. Acceptance Criteria
1. **Script execution (happy path).** Given the repository contains `hello-world/hello.sh`, when a developer runs `./hello-world/hello.sh` from the repository root, then standard output is exactly `hello world` followed by one line break, and the exit code is 0.
2. **Folder isolation (happy path).** Given the `hello-world` folder exists, when a developer lists its contents, hidden files included, then the only file present is `hello.sh`.
3. **Direct execution via shebang (happy path).** Given `hello.sh` has `#!/bin/bash` as its first line and is executable in a fresh clone of the repository, when a developer runs it without typing `bash`, then it runs successfully.
4. **Output exactness (edge case).** Given the script is run, when its standard output is captured, then it is exactly the lowercase text `hello world` with no leading or trailing spaces or tabs and no additional lines; the only thing after the text is the single line break that ends the line.
5. **Nothing else changes (scope).** Given the change is complete, when the repository is compared with its previous state, then the only product addition is `hello-world/hello.sh`: no existing file is edited (the readme and the Python hello feature included), no documentation file is added and no CI/CD configuration changes.

## 6. Dependencies & Constraints (product-level)
- This is the epic's only story. It has no pre-conditions, no blockers and no dependent stories (source: the story's context).
- Priority: Must. Size: XS (about 1).
- The change must not affect the existing Python hello feature or any existing directory.
- The story text and its acceptance criteria are the whole requirement. The developer confirmed this during intake.

## 7. Technical Design (deferred to STRUCTURE)
The tech lead decides:
- how the script produces the line in FR5;
- how the executable permission is recorded in the repository so that a fresh clone keeps it;
- how line endings and encoding are kept from adding stray characters to the output;
- whether to add an automated check that confirms acceptance criteria 1, 3 and 4.

The product requirements impose two constraints:
- Any automated check must sit outside `hello-world/` (FR2).
- Any automated check must not change CI/CD configuration (Non-Goals).

## 8. Open Questions
None block this story. The following are recorded as assumptions, following the developer's instruction to take the simplest reading where the story is silent:
- **A1:** The output may end with one line break. "No trailing whitespace and no additional lines" is read as excluding spaces or tabs after the text and any second line, not the line break that ends the single line.
- **A2:** No documentation is edited, including the repository readme.
- **A3:** An automated check is optional and is the tech lead's decision. It is not part of the definition of done.
- **A4:** The story traces to R1–R4 and RK1, but their text wasn't available. The story and its acceptance criteria are taken as the complete requirement, so coverage against those items was not checked.
