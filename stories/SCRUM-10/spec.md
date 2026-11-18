# מסמך מפרט — SCRUM-10: סקריפט bash של hello world בתיקייה ייעודית

## 1. סקירת היכולת

- **מה נבנה (לפי הסיפור):** תיקייה בשם `hello-world` בשורש המאגר play1, שבה קובץ אחד בלבד, `hello.sh`: סקריפט bash עם שורת shebang ‏`#!/bin/bash`, הרשאות הרצה, שמדפיס בדיוק "hello world" לפלט התקני ומסתיים בקוד 0.
- **הבעיה:** מפתח במאגר צריך נקודת פתיחה מינימלית, מאומתת וניתנת להרצה לכתיבת סקריפטים, בלי לערבב אותה בתיקיות הקיימות.
- **משתמשים:** מפתח שעובד במאגר play1.
- **סוג הסיפור:** הסיפור היחיד באפיק, עדיפות Must, גודל XS (כנקודה אחת), עוקב אחר R1, R2, R3, R4 · שלבים 1–4 · סיכון RK1, בלי חוסמים ובלי תנאים מקדימים.

> **ממצא מהמאגר.** התוצר שהסיפור מבקש **כבר קיים** בענף הבסיס `main` (וגם בענף העבודה):
> - `hello-world/hello.sh` נוסף בקומיט `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder"), במצב `100755` (ניתן להרצה), ותוכנו `#!/bin/bash` ו-`echo "hello world"`.
> - התיקייה `hello-world/` מכילה את הקובץ הזה בלבד.
> - הרצה של `./hello-world/hello.sh` מדפיסה `hello world` ואחריו תו שורה חדשה אחד, ומסתיימת בקוד 0.
> - `tests/test_hello_sh.py` כבר בודק את כל ארבעת התרחישים (פלט, קוד יציאה, shebang, הרשאות, תיקייה עם קובץ יחיד), ומצפה לפלט `"hello world\n"` בדיוק.
>
> **הנחה A1 (לפי הנחיית המפתח: "הקריאה הפשוטה ביותר"):** הדרישה היא המצב הסופי שקריטריוני הקבלה מתארים. מאחר שהוא כבר מתקיים ב-`main`, הסיפור נמסר באימות של ארבעת הקריטריונים מול הקוד, בלי ליצור, לשנות או להוסיף קבצים מעבר לנדרש. אם האימות בשלב המימוש יגלה פער כלשהו, משלימים רק אותו, בתוך התחום. *סיכון:* ייתכן שלא תיפתח בקשת מיזוג עם שינוי קוד; אם הכוונה הייתה לתרגל בקשת מיזוג מקצה לקצה, ההנחה הזו לא תשרת אותה.

## 2. מטרות ומה מחוץ לתחום

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### מטרות

- למפתח יש סקריפט bash מינימלי שאפשר להריץ ישירות (`./hello-world/hello.sh`) ושמדפיס בדיוק "hello world".
- הסקריפט מבודד בתיקייה משלו, בלי קבצים נוספים בה ובלי לגעת בתיקיות הקיימות.

### מחוץ לתחום

- סקריפטים נוספים.
- שילוב ב-CI/CD.
- קבצי תיעוד (בתוך התיקייה ומחוצה לה).
- שינוי בסקריפטים הקיימים תחת `qa/` ובשאר המאגר.

## 3. דרישות פונקציונליות

- **FR1** — בשורש המאגר קיימת תיקייה בשם `hello-world`.
- **FR2** — בתיקייה קובץ אחד בלבד, `hello.sh`.
- **FR3** — השורה הראשונה של `hello.sh` היא `#!/bin/bash`.
- **FR4** — לקובץ הרשאות הרצה, כך שאפשר להריץ אותו ישירות בלי `bash hello.sh`.
- **FR5** — הרצה מדפיסה לפלט התקני בדיוק את המחרוזת "hello world" באותיות קטנות, ומסתיימת בקוד 0.
- **FR6 (הנחה A2)** — תו שורה חדשה אחד המסיים את השורה (`hello world\n`) מותר ועומד בתרחיש 4: "בלי רווחים מובילים או נגררים ובלי שורות נוספות" פירושו שאין רווחים לפני הטקסט או אחריו בתוך השורה, ואין שורה שנייה. זו הקריאה הפשוטה ביותר — כך `echo` מסיים שורה, וכך מצפים הסקריפט והבדיקה הקיימים. *סיכון:* מי שמשווה את הפלט בייט-לבייט בלי תו שורה חדשה יראה אי-התאמה.

## 4. חוויית משתמש והתנהגות

- **זרימה:** המפתח מריץ מהשורש `./hello-world/hello.sh` ורואה בטרמינל `hello world`; הפקודה מסתיימת בהצלחה (קוד 0), בלי פלט שגיאה.
- **אין** ממשק, הודעות או מצבים נוספים. אין דרישת מראה מעבר לטקסט המדויק.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. תלויות ואילוצים

- **ענף בסיס:** `main` של play1 — שבו התוצר כבר קיים (קומיט `65938b5`).
- **שער הבדיקות של המאגר:** `pytest` (לפי `.factory/testing.md` ו-`.github/workflows/ci.yml`) רץ על כל בקשת מיזוג, וכולל את `tests/test_hello_sh.py`, שמקבע את הפלט כ-`"hello world\n"`. כל שינוי חייב להשאיר את השער ירוק, ולא ניתן לפטור ממנו.
- מיזוג בקשת המיזוג נעשה בידי אדם אחרי סקירה.

## 7. תכנון טכני (נדחה לשלב STRUCTURE)

אין תכנון טכני בשלב זה. אופן האימות מול `main` ופירוק העבודה (אם בכלל נדרש שינוי, לפי הנחה A1) ייקבעו בשלב STRUCTURE.

## 8. שאלות פתוחות

אין שאלות חוסמות. המפתח הנחה לקחת את הקריאה הפשוטה ביותר היכן שהסיפור שותק; שתי השאלות שנשאלו נסגרו כהנחות:

- **A1** — הסיפור נמסר באימות מול `main`, שבו התוצר כבר קיים; משלימים רק פער שיתגלה (סעיף 1).
- **A2** — תו שורה חדשה אחד בסוף הפלט עומד בתרחיש 4 (FR6).
