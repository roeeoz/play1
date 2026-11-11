# Feature Specification Document — QA20261110-10: הרצת סקריפט שמדפיס "hello from a3"

## 1. Feature Overview
- **Summary:** Add one QA shell script to play1, `qa/20261111-a3/hello.sh`. When run with no input, it prints exactly one line, `hello from a3`, and exits with code 0. The PR also adds the one CHANGELOG line that the repository gate requires. Nothing else changes.
- **Problem statement:** The Epic PRD, "a3 one-line hello script (round 2)", tests whether the development factory can take a small, precise request all the way to a merged change without widening it. Its leading indicator is a PR that delivers one product file and passes all its automated checks.
- **Target users / actors:** The factory's product owner and developer (Ally PO & DEV). They run the script to confirm the factory delivered exactly what was asked, then review and merge the PR.

## 2. Goals & Non-Goals
### Story context
בתוך הסיפור: קובץ חדש אחד, `qa/20261111-a3/hello.sh`, שמדפיס "hello from a3" ויוצא עם קוד 0, בלי קלט ובלי רכיב חיצוני, ושורה אחת שמתארת אותו תחת `## Unreleased` ב-`CHANGELOG.md`. מחוץ לסיפור: בדיקות חדשות, `--help` או אפשרויות, רישום כפקודה של החבילה, תיעוד אחר, גרסה, ותוצרי הסבב הקודם (`qa/20261110-a3`).

### Goals
- A runnable script at `qa/20261111-a3/hello.sh` that prints exactly `hello from a3` and exits with code 0 (PRD R1, R5).
- The script needs no input and no external component beyond a standard POSIX shell (PRD R2, adapted to the shell script).
- Everything that works in play1 today keeps working, and all required checks are green (PRD R3).
- The PR names this story and the epic PRD it came from (PRD R4).
- Serves goal G3, small composable additions. Keeps G4, fast CI, intact because no test is added.

### Non-Goals
- New automated tests for the script.
- `--help`, options, arguments or any input handling.
- Registering the script as a package console script.
- Docs, version bump, or any CHANGELOG change beyond the single line the gate requires.
- Any change to existing play1 code, scripts or tests.
- Any action on the round-1 path `qa/20261110-a3`, which doesn't exist.
- A Python implementation. The PO chose a shell script so the change meets gate rule 1 without an exemption.

## 3. Functional Requirements
- **FR1 (output):** Running `qa/20261111-a3/hello.sh` with no arguments and no stdin writes exactly `hello from a3` followed by one newline to stdout. It writes nothing to stderr.
- **FR2 (exit):** The script exits with code 0.
- **FR3 (how it's run):** It can be run as `sh qa/20261111-a3/hello.sh` or directly as `./qa/20261111-a3/hello.sh`. It is executable and starts with a shebang, like the existing qa scripts.
- **FR4 (no dependencies):** It relies only on a standard POSIX shell. It doesn't read files, use the network, or need anything installed beyond what play1 installs today.
- **FR5 (CHANGELOG):** The PR adds exactly one line under `## Unreleased` in `CHANGELOG.md` describing the new script, in the style of the existing entries.
- **FR6 (traceability):** The PR description names story QA20261110-10, "הרצת סקריפט שמדפיס "hello from a3"", and the epic PRD it came from.
- **Inputs:** none. **Outputs:** one stdout line and exit code 0.
- **Edge cases:** Any arguments or stdin are outside the contract. No option behaviour is specified, and none is added.

## 4. User Experience & Behavior
- **Flow:** The PO opens the PR. They see one product file, `qa/20261111-a3/hello.sh`, the CHANGELOG line, the factory's plan folder `stories/QA20261110-10/`, traceability to the story and PRD, and green required checks. After a person merges it, the PO runs the script and sees `hello from a3`.
- **Output format:** exactly one plain-text line, `hello from a3`, ending in a newline. No banner, colour or extra whitespace, and nothing on stderr.
- **States:** none. There is no UI, prompt or interaction. No design is required.

## 5. Acceptance Criteria
1. תרחיש 1: מסלול תקין — הרצת הסקריפט. **בהינתן** play1 אחרי המיזוג, **כאשר** המשתמש מריץ את `qa/20261111-a3/hello.sh` בלי שום קלט, **אז** מודפסת בדיוק שורה אחת, "hello from a3", **וגם** הסקריפט יוצא עם קוד יציאה 0.
2. תרחיש 2: מסלול תקין — בלי רכיב חיצוני. **בהינתן** סביבה עם shell סטנדרטי (`/bin/sh`) ובה רק מה ש-play1 מתקינה היום, **כאשר** המשתמש מריץ את הסקריפט, **אז** מודפסת השורה "hello from a3" והיציאה בקוד 0, **וגם** לא נדרשה התקנה של שום רכיב חיצוני נוסף.
3. תרחיש 3: רגרסיה — מה שעובד היום ממשיך לעבוד. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** הבדיקות האוטומטיות של play1 רצות עליה, **אז** כל הבדיקות הנדרשות עוברות, **וגם** הסקריפטים הקיימים בתיקייה `qa` מדפיסים ויוצאים בדיוק כמו לפני השינוי.
4. תרחיש 4: גבול התחום — קובץ מוצר אחד בלבד. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר בודק את רשימת הקבצים ששונו, מלבד תיקיית התוכנית `stories/QA20261110-10/`, **אז** נוסף רק `qa/20261111-a3/hello.sh` ונוספה שורה אחת תחת `## Unreleased` ב-`CHANGELOG.md`, **וגם** אין בה בדיקות, תיעוד אחר, שינוי גרסה או רישום כפקודה של החבילה.
5. תרחיש 5: מסלול תקין — עקיבות בבקשת המיזוג. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר פותח אותה, **אז** התיאור שלה מציין את הסיפור "הרצת סקריפט שמדפיס "hello from a3"" ואת מסמך הדרישות של האפיק שממנו נגזר.
6. תרחיש 6: מקרה שגיאה — בדיקה אוטומטית נכשלת. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר בא לאשר אותה, **אז** כל הבדיקות האוטומטיות הנדרשות שלה מוצגות כעוברות (ירוקות), **וגם** כל עוד אחת מהן נכשלת, בקשת המיזוג מוצגת כלא מוכנה למיזוג.

## 6. Dependencies & Constraints (product-level)
- **CI is the gate (R3, Engineering requirements):** the PR is ready to merge only with every required check green, and a person merges it after review. The required checks are `test` (pytest on Python 3.12) and `gate`.
- **play1 repository gate (`mr-gate`):**
  - Rule 1: Python only under `src/`. Met, because no Python file is added.
  - Rule 2: a new shell script is executable and starts with a shebang.
  - Rule 3: no file larger than 200 KB.
  - Rule 4 / PLAY-G4: one line under `## Unreleased` in `CHANGELOG.md`.

  All of these must hold mechanically.
- **Evidence for AC3:** a green pytest run, which covers `qa/s3-hello.sh`, `qa/s3-a.sh` and `qa/20261109-s1/a.sh`. Plus a manual run of the existing `qa` scripts, including `qa/20261110-s3/test_hello.sh`, showing their output and exit codes are unchanged.
- **Evidence for AC2:** a manual run with `/bin/sh` and no extra installs.
- **G3:** one product file plus the CHANGELOG line, far under 300 changed lines.
- **No secrets (R4):** nothing sensitive in the script, PR or commits.
- **No licence concerns (R6):** no third-party code.
- **Traceability (R7):** the PR names QA20261110-10 and the epic PRD.

## 7. Technical Design (deferred to STRUCTURE)
The exact script body, shebang choice, the CHANGELOG wording and how the manual evidence is captured belong to STRUCTURE and PLAN. The product only requires the behaviour above, the gate rules in §6, and a change that stays within the one-product-file scope.

## 8. Open Questions
- The Epic PRD (R1, §7) and the backlog still name `qa/20261111-a3/hello.py` and Python. This story now delivers `hello.sh` on the PO's decision. Whether to update the PRD to match is the PO's call, and it doesn't block delivery.
