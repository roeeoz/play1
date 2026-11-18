# מסמך מפרט — SCRUM-10: סקריפט bash של hello world בתיקייה ייעודית (טיוטה — ממתין לתשובות)

## 1. סקירת היכולת

- **מה נבנה (לפי הסיפור):** תיקייה בשם `hello-world` בשורש המאגר play1, שבה קובץ אחד בלבד, `hello.sh`: סקריפט bash עם שורת shebang ‏`#!/bin/bash`, הרשאות הרצה, שמדפיס בדיוק "hello world" לפלט התקני ומסתיים בקוד 0.
- **הבעיה:** מפתח במאגר צריך נקודת פתיחה מינימלית, מאומתת וניתנת להרצה לכתיבת סקריפטים, בלי לערבב אותה בתיקיות הקיימות.
- **משתמשים:** מפתח שעובד במאגר play1.
- **סוג הסיפור:** הסיפור היחיד באפיק, עדיפות Must, גודל XS (כנקודה אחת), עוקב אחר R1, R2, R3, R4 · שלבים 1–4 · סיכון RK1, בלי חוסמים ובלי תנאים מקדימים.

> **ממצא מהמאגר — הסיבה שהטיוטה ממתינה.** התוצר שהסיפור מבקש **כבר קיים** בענף הבסיס `main` (וגם בענף העבודה):
> - `hello-world/hello.sh` נוסף בקומיט `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder"), במצב `100755` (ניתן להרצה), ותוכנו `#!/bin/bash` ו-`echo "hello world"`.
> - התיקייה `hello-world/` מכילה את הקובץ הזה בלבד.
> - הרצה של `./hello-world/hello.sh` מדפיסה `hello world` ואחריו תו שורה חדשה אחד, ומסתיימת בקוד 0.
> - `tests/test_hello_sh.py` כבר בודק את כל ארבעת התרחישים (פלט, קוד יציאה, shebang, הרשאות, תיקייה עם קובץ יחיד), ומצפה לפלט `"hello world\n"` בדיוק.
>
> לכן לא ברור מה הסיפור הזה אמור לשנות — ראו שאלה Q1 בסעיף 8.

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
- **FR6 (ממתין ל-Q2)** — האם תו שורה חדשה אחד בסוף הפלט מותר. *הנחת עבודה:* מותר — זה מסיים השורה הרגיל, וזה מה שהסקריפט הקיים והבדיקה הקיימת עושים; "בלי רווחים מובילים או נגררים ובלי שורות נוספות" פירושו שאין רווחים ואין שורה שנייה.

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
- **שער הבדיקות של המאגר:** `pytest` (לפי `.factory/testing.md` ו-`.github/workflows/ci.yml`) רץ על כל בקשת מיזוג, וכולל את `tests/test_hello_sh.py`, שמקבע את הפלט כ-`"hello world\n"`. כל שינוי בהתנהגות הסקריפט חייב להשאיר את השער ירוק (כלומר לעדכן גם את הבדיקה), ולא ניתן לפטור ממנו.
- מיזוג בקשת המיזוג נעשה בידי אדם אחרי סקירה.

## 7. תכנון טכני (נדחה לשלב STRUCTURE)

אין תכנון טכני בשלב זה. הארכיטקטורה, אופן הבדיקה ופירוק בקשות המיזוג ייקבעו בשלב STRUCTURE לאחר שיוכרע מה הסיפור משנה (Q1).

## 8. שאלות פתוחות

- **Q1 (חוסמת)** — `hello-world/hello.sh` כבר קיים ב-`main` ועומד בכל ארבעת קריטריוני הקבלה, כולל בדיקה אוטומטית ב-`tests/test_hello_sh.py`. מה הסיפור צריך למסור? (א) לסגור את הסיפור כ"כבר נמסר", בלי בקשת מיזוג, עם אימות של הקריטריונים מול `main`; (ב) בקשת מיזוג לאימות בלבד, בלי שינוי בתוצר (למשל רשומה ב-`CHANGELOG.md` שמציינת את SCRUM-10) — שימו לב שזה מוסיף קובץ מחוץ לתיקייה, ש"קבצי תיעוד" מוחרגים בסיפור; (ג) ליצור מחדש בתיקייה בשם אחר. *המלצה:* (א) — התוצר הנדרש כבר קיים ונבדק בשער ה-CI, ושינוי נוסף יחרוג מהתחום שהסיפור קובע. תשובה שהאפיק נועד במפורש לתרגל את המפעל מקצה לקצה עם בקשת מיזוג תשנה את ההמלצה ל-(ב).
- **Q2 (חוסמת)** — תרחיש 4 אומר "בלי רווחים מובילים או נגררים ובלי שורות נוספות". האם תו שורה חדשה אחד בסוף הפלט (`hello world\n`) עומד בזה? *המלצה:* כן — זה מסיים השורה הסטנדרטי של `echo`, וזה מה שהסקריפט והבדיקה הקיימים עושים; תשובה "לא, בלי תו שורה חדשה כלל" פירושה שינוי בסקריפט ובבדיקה הקיימת.
