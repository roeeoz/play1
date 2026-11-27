# SMKL-1 — Hello world bash script in a dedicated folder

**The script is already in the repo.** `hello-world/hello.sh` and a test for it both reached `main` in earlier commits, and the script already passes all four acceptance criteria. Unless you choose otherwise below, the build changes no product file.

## Left for you to choose: the trailing newline

The script prints `hello world` and then a newline. Acceptance criterion 4 says "no trailing whitespace". Read literally, that rules out the newline.

- **Default, if you say nothing:** keep the newline. It ends the single line of output and does not add a second line. Shell capture (`$(…)`) gives exactly `hello world`, and the existing test already expects the newline.
- **The alternative:** print `hello world` with nothing after it. The build changes one line in the script and two lines in the test. The cost is that in a terminal, the prompt then appears on the same line as the output.

## 1. Decided differently from what was asked

- **Story, criterion 4:** by default the output keeps its trailing newline, which differs from the literal wording. The reason and the alternative are in the section above.
- **Story, "Out of scope: documentation files":** the build adds a build log in the story's folder (`stories/SMKL-1/`), not in the product. The factory records every build in such a log. No README or other documentation is added to `hello-world/` or anywhere else in the product.
- The developer has made no rulings yet.

## 2. What changes for people

Nothing, with the default. Developers already have `./hello-world/hello.sh` on `main`. With the alternative, the script's output loses its final newline.

## 3. Decisions and assumptions

- **Decision:** reuse the existing script and test rather than write them again. Not chosen: rewriting them, which would create churn for no gain.
- **Decision:** keep the trailing newline by default. The reasons and the alternative are in the first section.
- **Decision:** the merge request carries only the story folder (plan, this summary, the build log). Its description cites the existing commits and the check results. Not chosen: closing the story with no merge request. That remains available if you prefer it.
- **Assumption, checked in the code:** the script and its test are on `main`. Both commits that added or changed them are in `main`'s history, and the work branch is at the same commit as `main`.
- **Assumption, checked in the code:** the script has the `#!/bin/bash` first line, is executable in git, is the only file in `hello-world/`, and printed `hello world` and exited with 0 when run.
- **Assumption, not checked here:** CI (pytest, Python 3.12 on Linux) passes at the merge request's head. If it does not, the build log and the CI run will show it.

## 4. Removed or switched off

Nothing.

## 5. Data, security and privacy

Nothing. The script reads no input, stores no data, makes no network calls and handles no secrets.

## 6. Between repositories

None. Only `play1` is involved, and nothing has to land first.

## 7. Risks, and what was not tried

- The story repeats work already on `main`, so its merge request has no product change by default. The risk is a reviewer expecting code and finding only the story folder.
- Not tried: running the script under a shell other than bash, or on a system without `/bin/bash`. The story asks for `#!/bin/bash`.

## 8. Done when

| Check | Expected |
|---|---|
| Run `./hello-world/hello.sh` | Prints `hello world` (with the newline, unless you chose the alternative) and exits 0 |
| List `hello-world/` | Only `hello.sh` |
| First line of the script | `#!/bin/bash` |
| File mode in git | Executable (`100755`) |
| `pytest` in CI on the merge request | Passes, including the hello-world tests |
