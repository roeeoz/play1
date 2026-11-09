# PLAY-167 — Draft (intake in progress, NOT the final spec)

**Story:** סקריפט פרידה שמדפיס "bye", ועם שם גם פרידה אישית
**Epic:** QA-20261109-S3 farewell script (PLAY-166); source: the Epic PRD page in Confluence, version 1
**Target branch:** `qa-20261109-s3-base` (repo roeeoz/play1)

## What is understood
- **User:** the person who runs the factory's QA checks (the PO and the developer who opened the epic).
- **Value:** prove that a one-file request goes through the factory and ends in one pull request.
- **Behavior (Epic PRD §3–4, R1–R4):**
  - `qa/20261109-s3/bye.sh` with no argument prints exactly `bye` and exits 0.
  - With a name, it prints exactly `bye` and then `bye <name>`, and exits 0.
  - Only the first word counts as the name.
  - `--help` is treated as a name.
- **Out of scope:** an automated test for the script, a help message, input validation, documentation changes, and any other story.

## Repository facts checked at intake
- `qa/20261109-s3/` exists on the base and contains only `BASE_MARKER.md`. `bye.sh` does not exist yet.
- The sibling scripts `qa/s3-a.sh` and `qa/s3-hello.sh` are executable and start with `#!/bin/sh`.
- Repo gate (mr-gate):
  - Rule 2: a new shell script must be executable and start with a shebang.
  - Rule 4: every PR must add a line under `## Unreleased` in `CHANGELOG.md`, or blocker PLAY-G4 is raised.
- CI runs `pytest` (testpaths = tests). No test touches `qa/20261109-s3/`.
- The factory puts `stories/PLAY-167/*` on the same branch as the PR.

## Story context (as published, pending P0 answers)
בתוך הסיפור: הקובץ החדש `qa/20261109-s3/bye.sh` בלבד, לצד סקריפטי הבדיקה הקיימים בתיקייה `qa/`. מחוץ לסיפור: כל קובץ אחר, בדיקה אוטומטית לסקריפט, הודעת עזרה ובדיקת קלט. בקשת המיזוג מציינת את הסיפור הזה ואת מסמך האפיון.

## Acceptance criteria (as published)
1. תרחיש 1: מסלול תקין — הרצה בלי שם. **בהינתן** המאגר אחרי המיזוג, **כאשר** מריצים `qa/20261109-s3/bye.sh` בלי ארגומנט, **אז** הפלט הוא שורה אחת בדיוק: `bye`, **וגם** קוד היציאה הוא 0.
2. תרחיש 2: מסלול תקין — הרצה עם שם. **בהינתן** המאגר אחרי המיזוג, **כאשר** מריצים `qa/20261109-s3/bye.sh Alice`, **אז** הפלט הוא שתי שורות בדיוק: `bye` ואחריה `bye Alice`, **וגם** קוד היציאה הוא 0.
3. תרחיש 3: מקרה קצה — כמה מילים. **בהינתן** המאגר אחרי המיזוג, **כאשר** מריצים `qa/20261109-s3/bye.sh Alice Bob`, **אז** הפלט הוא שתי שורות בדיוק: `bye` ואחריה `bye Alice`, **וגם** המילה `Bob` אינה מופיעה בפלט.
4. תרחיש 4: מקרה קצה — הערך `--help`. **בהינתן** המאגר אחרי המיזוג, **כאשר** מריצים `qa/20261109-s3/bye.sh --help`, **אז** הפלט הוא שתי שורות בדיוק: `bye` ואחריה `bye --help`, **וגם** קוד היציאה הוא 0.
5. תרחיש 5: גבול התחום — קובץ אחד בלבד. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** בודקים את רשימת הקבצים שהיא משנה, **אז** מופיע בה רק הקובץ החדש `qa/20261109-s3/bye.sh`, **וגם** `qa/s3-a.sh` ו-`qa/s3-hello.sh` נשארים ללא שינוי.  ← **BLOCKED:** this conflicts with gate rule 4 (CHANGELOG line) and with the factory's plan folder; see P0-1 and P0-2.
6. תרחיש 6: רגרסיה — הבדיקות האוטומטיות. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** הבדיקות האוטומטיות הנדרשות של play1 רצות עליה, **אז** כולן עוברות, **וגם** שלב הבדיקות מסתיים בפחות מ-60 שניות.

## Pending decisions
- **P0-1:** CHANGELOG line (option a) or a gate rule change made first (option b).
- **P0-2:** whether `stories/PLAY-167/` is excluded from the file-list check in criterion 5.
- **P1:** shebang — default is `#!/bin/bash`, per the epic's "bash script".
