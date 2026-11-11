# Ticket draft (not final) — QA20261110-10: הרצת סקריפט שמדפיס "hello from a3"

**Status:** P0.1, P0.3 and all P1s are settled. Still waiting for an answer on gate rule 1 (Python outside `src/`): either change the rule in the repo first, or change the story's path or language.

## User story
בתור מנהל המוצר והמפתח של מפעל הפיתוח, אני רוצה להריץ ב-play1 סקריפט שמדפיס שורה אחת, "hello from a3", כדי שאוכל לוודא שהמפעל מסר בדיוק את הבקשה הקטנה שביקשתי, בלי להרחיב אותה.

## Context and description (changed per the answer to P0.1)
בתוך הסיפור: קובץ חדש אחד, `qa/20261111-a3/hello.py`, שמדפיס "hello from a3" ויוצא עם קוד 0, בלי קלט ובלי רכיב חיצוני, ושורה אחת שמתארת אותו תחת `## Unreleased` ב-`CHANGELOG.md`. מחוץ לסיפור: בדיקות חדשות, `--help` או אפשרויות, רישום כפקודה של החבילה, תיעוד אחר, גרסה, ותוצרי הסבב הקודם (`qa/20261110-a3`).

## Decisions recorded
- **P0.1:** the PR adds one CHANGELOG line under `## Unreleased`. This satisfies gate rule PLAY-G4 and matches the precedent of PLAY-114, 156, 172 and 175.
- **P0.3:** AC4 counts only the delivered product change. The factory plan folder `stories/QA20261110-10/` and the CHANGELOG line are excluded.
- **P1, output:** stdout is exactly `hello from a3` followed by a newline, and stderr is empty.
- **P1, Python 3.10:** CI runs 3.12 only, so a manual run on 3.10 is accepted as evidence for AC2.
- **P1, regression:** AC3 needs a green pytest run, plus a manual run of the existing `qa` scripts (including `qa/20261110-s3/test_hello.sh`) showing their output is unchanged.
- **AC6:** reworded. A person merges, so the criterion is what the PR shows.

## Open (P0): gate rule 1
| Gate rule (play1 repo-gate) | Conflicts with | Options the factory can honour |
| --- | --- | --- |
| Rule 1: "Python source lives under `src/`" | The path `qa/20261111-a3/hello.py` (the first `.py` outside `src/`; earlier qa scripts were all `.sh`) | (a) Change rule 1 in play1 first, in a separate approved PR, then deliver as written. (b) Change the story's path or language so the rule is already met, e.g. `qa/20261111-a3/hello.sh`. |

## Acceptance criteria (proposed; changes marked)
1. תרחיש 1: מסלול תקין — הרצת הסקריפט. **בהינתן** play1 אחרי המיזוג, **כאשר** המשתמש מריץ את `qa/20261111-a3/hello.py` ב-Python בלי שום קלט, **אז** מודפסת בדיוק שורה אחת, "hello from a3", **וגם** הסקריפט יוצא עם קוד יציאה 0.
2. תרחיש 2: מסלול תקין — גרסת Python הנתמכת. **בהינתן** סביבה עם Python 3.10 ובה רק מה ש-play1 מתקינה היום, **כאשר** המשתמש מריץ את הסקריפט, **אז** מודפסת השורה "hello from a3" והיציאה בקוד 0, **וגם** לא נדרשה התקנה של שום רכיב חיצוני נוסף.
3. תרחיש 3: רגרסיה — מה שעובד היום ממשיך לעבוד. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** הבדיקות האוטומטיות של play1 רצות עליה, **אז** כל הבדיקות הנדרשות עוברות, **וגם** הסקריפטים הקיימים בתיקייה `qa` מדפיסים ויוצאים בדיוק כמו לפני השינוי.
4. *(Changed per P0.1 and P0.3)* תרחיש 4: גבול התחום — קובץ מוצר אחד בלבד. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר בודק את רשימת הקבצים ששונו, מלבד תיקיית התוכנית `stories/QA20261110-10/`, **אז** נוסף רק `qa/20261111-a3/hello.py` ונוספה שורה אחת תחת `## Unreleased` ב-`CHANGELOG.md`, **וגם** אין בה בדיקות, תיעוד אחר, שינוי גרסה או רישום כפקודה של החבילה.
5. תרחיש 5: מסלול תקין — עקיבות בבקשת המיזוג. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר פותח אותה, **אז** התיאור שלה מציין את הסיפור "הרצת סקריפט שמדפיס "hello from a3"" ואת מסמך הדרישות של האפיק שממנו נגזר.
6. *(Reworded: a person merges, never the factory)* תרחיש 6: מקרה שגיאה — בדיקה אוטומטית נכשלת. **בהינתן** בקשת המיזוג של הסיפור, **כאשר** מנהל המוצר בא לאשר אותה, **אז** כל הבדיקות האוטומטיות הנדרשות שלה מוצגות כעוברות (ירוקות), **וגם** כל עוד אחת מהן נכשלת, בקשת המיזוג מוצגת כלא מוכנה למיזוג.
