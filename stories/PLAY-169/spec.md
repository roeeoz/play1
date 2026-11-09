# Feature Specification Document — PLAY-169: סקריפט הבדיקה a מדפיס "a" ומסתיים בהצלחה

## 1. Feature Overview
- **Summary:** Add one standalone test script, `qa/20261109-s6/a.sh`, to the play1 package. When it runs, it prints the single line `a` and exits with code 0. The pull request also carries one `CHANGELOG.md` line under `## Unreleased`.
- **Problem statement:** The factory's single-story controls probe (epic QA-20261109-S6, PLAY-168) needs a trivial change. It shows that a one-story epic can go through every factory stage (define, structure, implement, approval) and end in one mergeable pull request without breaking the existing CI.
- **Target users / actors:** The PO and development team (Ally PO & DEV), who are testing the development factory. They run the script from the command line and review the pull request.

## 2. Goals & Non-Goals
### Story context
בתוך הסיפור: קובץ חדש אחד, `qa/20261109-s6/a.sh`, בדומה לסקריפטים הקיימים בתיקיית `qa/`, ושורה אחת ב-`CHANGELOG.md` תחת `## Unreleased` שנדרשת בשער בקשות השינוי של המאגר; מסמכי הסיפור של המפעל תחת `stories/PLAY-169/` מותרים בבקשת השינוי. מחוץ לסיפור: כל קובץ מוצר אחר (כולל בדיקות ותיעוד נוסף), הסקריפט `c.sh`, תמיכה ב-`--help`, ושינוי בסקריפטים הקיימים או בקוד החבילה.

### Goals
- Running `qa/20261109-s6/a.sh` prints exactly one line, `a`, and exits 0 (Epic PRD R1, R2).
- The change is minimal: one new script and one CHANGELOG line. The existing GitHub `test` and `gate` jobs keep passing (Epic PRD R3; goal G3).
- The pull request names this story and the epic's PRD, and contains no secrets or personal data (engineering requirements R4, R7).

### Non-Goals
- Any other product or repository file, including tests and other documentation.
- `qa/20261109-s6/c.sh`.
- `--help` or any command-line options. The script is not a registered console script of the package (Epic PRD, assumptions).
- Changes to the existing `qa/` scripts or to the package code.
- Any other user story.

## 3. Functional Requirements
- **FR1:** Running `qa/20261109-s6/a.sh` from the command line, with no input or arguments, writes exactly one line to standard output, and its content is exactly `a`.
- **FR2:** The script exits with code 0.
- **FR3:** The script follows the existing `qa/` scripts (`qa/s3-a.sh`, `qa/s3-hello.sh`): it can be run directly from the command line. It lives in the new subfolder `qa/20261109-s6/`.
- **FR4:** `CHANGELOG.md` gets exactly one new line under `## Unreleased` that records the new script. No other line of `CHANGELOG.md` changes.
- **FR5:** No other product or repository file is added, changed or deleted. The factory's own story documents under `stories/PLAY-169/` are allowed in the pull request.
- **Inputs:** none. **Outputs:** the line `a` and exit code 0. **Edge cases:** none beyond those above; the script takes no input.

## 4. User Experience & Behavior
- **Flow:** the team runs `qa/20261109-s6/a.sh`, sees `a` immediately, and the command succeeds. There are no prompts and no other output.
- **Pull request:** the reviewer sees `a.sh`, one CHANGELOG line and the factory's story documents. The description names PLAY-169 and the Epic PRD.
- **Output format:** exactly the single line `a` with no other text on stdout.
- **No UI:** this is a command-line script, so there is no design.

## 5. Acceptance Criteria
1. תרחיש 1: מסלול תקין — הרצת הסקריפט. **בהינתן** החבילה אחרי מיזוג השינוי, **כאשר** מריצים את `qa/20261109-s6/a.sh` משורת הפקודה, **אז** הפלט הוא שורה אחת בלבד שתוכנה בדיוק "a", **וגם** הפקודה מסתיימת בקוד יציאה 0.
2. תרחיש 2: גבול התחום — סקריפט אחד ושורת CHANGELOG אחת. **בהינתן** בקשת השינוי של הסיפור, **כאשר** הצוות בודק את רשימת הקבצים שבה, **אז** היא מוסיפה את `qa/20261109-s6/a.sh` ושורה אחת ב-`CHANGELOG.md` תחת `## Unreleased` (ומלבדם רק את מסמכי הסיפור תחת `stories/PLAY-169/`), **וגם** אף קובץ מוצר אחר (כולל `qa/20261109-s6/c.sh`, בדיקות או תיעוד) אינו נוסף, משתנה או נמחק.
3. תרחיש 3: רגרסיה — הבדיקות הנדרשות עוברות. **בהינתן** בקשת השינוי של הסיפור, **כאשר** הבדיקות האוטומטיות הנדרשות (המשימות `test` ו-`gate` ב-GitHub) רצות עליה, **אז** כולן מסתיימות בהצלחה, **וגם** השינוי מתמזג רק אחרי שאדם אישר אותו.
4. תרחיש 4: גבול התחום — עקיבות בבקשת השינוי. **בהינתן** בקשת השינוי של הסיפור, **כאשר** הצוות קורא את תיאורה, **אז** הוא מציין את הסיפור הזה ואת מסמך הדרישות של האפיק, **וגם** אין בה ובקובץ סודות או מידע אישי.

## 6. Dependencies & Constraints (product-level)
- No dependencies on other stories. This is the epic's only story (wave 1).
- Engineering requirements: R3 (CI is the gate), R4 (no secrets) and R7 (traceability: the PR names the story and the PRD). R2 and R6 do not apply because the script adds no dependency.
- The repository's merge-request gate rule PLAY-G4 requires the PR to touch `CHANGELOG.md`. The one CHANGELOG line meets it.
- Goal G3: well under 300 changed lines.

## 7. Technical Design (deferred to STRUCTURE)
The file's exact content, header comment and file mode are left to STRUCTURE. The existing `qa/` scripts are the model.

## 8. Open Questions
None.
