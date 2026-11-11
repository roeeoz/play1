# Ticket draft (not final) — QA20261110-10: הרצת סקריפט שמדפיס "hello from a3"

**Status:** waiting for answers to P0 questions 1–3. The story's text below is unchanged; the proposed changes are marked.

## User story
בתור מנהל המוצר והמפתח של מפעל הפיתוח, אני רוצה להריץ ב-play1 סקריפט שמדפיס שורה אחת, "hello from a3", כדי שאוכל לוודא שהמפעל מסר בדיוק את הבקשה הקטנה שביקשתי, בלי להרחיב אותה.

## Context and description (unchanged until answers arrive)
בתוך הסיפור: קובץ חדש אחד, `qa/20261111-a3/hello.py`, שמדפיס "hello from a3" ויוצא עם קוד 0, בלי קלט ובלי רכיב חיצוני. מחוץ לסיפור: בדיקות חדשות, `--help` או אפשרויות, רישום כפקודה של החבילה, תיעוד, יומן שינויים, גרסה, ותוצרי הסבב הקודם (`qa/20261110-a3`).

## What is clear (from the story and the PRD)
- Run `python qa/20261111-a3/hello.py` with no input: it prints exactly one line, `hello from a3`, and exits with code 0 (R1, R5).
- Python ≥ 3.10 with only what play1 installs today; no new dependency, and `pyproject.toml` is unchanged (R2).
- Existing qa scripts and the package keep working, and the required checks (pytest) stay green (R3).
- The PR names story QA20261110-10 and the epic PRD "a3 one-line hello script (round 2)" (R4).
- Out of scope: new tests, `--help`/options, console-script registration, docs, version, and round-1 artefacts `qa/20261110-a3` (which doesn't exist in the repo).

## Conflicts with the repo gate (must be resolved; a gate can't be waived for one story)
| Gate rule (play1 repo-gate) | Conflicts with | Possible resolutions |
| --- | --- | --- |
| PLAY-G4: a line under `## Unreleased` in `CHANGELOG.md` | AC4, PRD §8 ("no changelog") | Add the line to the scope, or change the rule in the repo first |
| Rule 1: Python source only under `src/` | The fixed path `qa/20261111-a3/hello.py` | Change the rule in the repo first, or change the path/language |
| (Factory convention) the plan folder `stories/QA20261110-10/` lands on the branch | The literal reading of AC4 | Decide whether AC4 counts the whole diff or only the delivered change |

## Acceptance criteria (as published; proposed changes marked)
1. תרחיש 1: מסלול תקין — הרצת הסקריפט. **בהינתן** play1 אחרי המיזוג, **כאשר** המשתמש מריץ את `qa/20261111-a3/hello.py` ב-Python בלי שום קלט, **אז** מודפסת בדיוק שורה אחת, "hello from a3", **וגם** הסקריפט יוצא עם קוד יציאה 0.
2. תרחיש 2: מסלול תקין — גרסת Python הנתמכת. **בהינתן** סביבה עם Python 3.10 ובה רק מה ש-play1 מתקינה היום, **כאשר** המשתמש מריץ את הסקריפט, **אז** מודפסת השורה "hello from a3" והיציאה בקוד 0, **וגם** לא נדרשה התקנה של שום רכיב חיצוני נוסף.
3. תרחיש 3: רגרסיה — מה שעובד היום ממשיך לעבוד. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** הבדיקות האוטומטיות של play1 רצות עליה, **אז** כל הבדיקות הנדרשות עוברות, **וגם** הסקריפטים הקיימים בתיקייה `qa` מדפיסים ויוצאים בדיוק כמו לפני השינוי.
4. תרחיש 4: גבול התחום — קובץ אחד בלבד. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר בודק את רשימת הקבצים ששונו, **אז** הקובץ היחיד שנוסף או שונה הוא `qa/20261111-a3/hello.py`, **וגם** אין בה בדיקות, תיעוד, שינוי גרסה או רישום כפקודה של החבילה. — *Pending P0 questions 1 and 3; the wording will change to match the answer.*
5. תרחיש 5: מסלול תקין — עקיבות בבקשת המיזוג. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר פותח אותה, **אז** התיאור שלה מציין את הסיפור "הרצת סקריפט שמדפיס "hello from a3"" ואת מסמך הדרישות של האפיק שממנו נגזר.
6. תרחיש 6: מקרה שגיאה — בדיקה אוטומטית נכשלת. — *Proposed rewording (a person merges, never the factory):* **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר בא לאשר אותה, **אז** כל הבדיקות האוטומטיות הנדרשות שלה מוצגות כעוברות (ירוקות), **וגם** כל עוד אחת מהן נכשלת, בקשת המיזוג מוצגת כלא מוכנה למיזוג.
