# מסמך מפרט — SCRUM-24: דוח הוצאות חודשי מתוך פנקס CSV

> **סטטוס: טיוטה — לא מוכן.** שאלה חוסמת אחת פתוחה (Q1, יומן השינויים — ראו סעיף 8).

**מאגר:** play1, ענף בסיס `main` · **עוקב אחר:** R1 (פענוח CSV), R2 (אימות שורות), R3 (דוח חודשי), R4 (המרת מטבע ועיגול), R5 (שורת פקודה) · שלבים 1–8 · סיכונים RK1, RK2 · **עדיפות:** Must · **גודל:** M (כ-5 נקודות, כפי שנמסר) · **חוסמים:** אין (לפי הסיפור).

## 1. סקירת היכולת

- **מה נבנה:** חבילת Python חדשה בשם `ledger`, בספרייה הסטנדרטית בלבד, תחת `src/`, עם בדיקות תחת `tests/`. היא קוראת פנקס CSV, מאמתת כל שורה, ומפיקה דוח חודשי — הכנסות, הוצאות, נטו וסיכום לפי קטגוריה — במטבע בסיס, דרך `python -m ledger report`, כטקסט או כ-JSON.
- **הבעיה:** מפתח שמנהל פנקס אישי או של צוות קטן בקובץ CSV צריך היום גיליון אלקטרוני כדי לראות סיכום חודשי. סכום שגוי שנובע משורה פגומה אינו נראה; הכלי צריך להצביע על השורה לפי מספרה במקום להפיק סכום שגוי.
- **משתמשים:** מפתח שמחזיק פנקס CSV ורוצה סיכום חודשי מהטרמינל, וכן מפתח שקורא לחבילה מקוד (`parse_csv`, `parse_lines`, `monthly_report`).
- **פריטי עבודה (כפי שנמסרו בסיפור):** t1 — המודל ופענוח ה-CSV; t2 — הדוח החודשי; t3 — שורת הפקודה. כל אחד תלוי בקודמו.

## 2. מטרות ומה מחוץ לתחום

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

> הערת קליטה: השורה הועתקה מילה במילה. הסיפא "changes to any existing file of the repository" מתנגשת בשער המאגר שמחייב שורה ב-`CHANGELOG.md` הקיים (Q1). אם מנהל המוצר יאשר את ההמלצה, השורה תתעדכן כך שתתיר שורה אחת תחת `## Unreleased` ב-`CHANGELOG.md`.

### מטרות

- מפתח מריץ פקודה אחת ומקבל סיכום דטרמיניסטי של חודש אחד: מספר התנועות, הכנסות, הוצאות, נטו, וקטגוריות לפי גודל מוחלט — במטבע בסיס לבחירתו (ILS, USD או EUR).
- שורה פגומה לעולם אינה מפיקה סכום שגוי: הכלי עוצר בשורה הפגומה הראשונה ומציג את מספר השורה הפיזי ואת הסיבה בנוסח מדויק.
- הכסף מדויק: `Decimal` מקצה לקצה, המרה בדיוק מלא, עיגול אחד לשני מקומות אחרי הסכימה, חצי לזוגי.
- הדוח זמין גם כ-JSON שבו סכומים הם מחרוזות, כדי שלא יאבד דיוק.
- הבדיקות מריצות את נקודת הכניסה האמיתית של החבילה המותקנת.

### מחוץ לתחום

- פורמטים אחרים של קבצים (Excel, JSON כקלט וכו').
- שערי חליפין חיים או מתעדכנים; השערים קבועים.
- הגדרות שנשמרות (קובץ תצורה, משתני סביבה).
- גרפים או כל פלט חזותי.
- כל תלות צד שלישי.
- שינוי בקבצים קיימים של המאגר (כולל `pyproject.toml`, ולכן אין פקודת console script חדשה; הכניסה היא `python -m ledger`) — בכפוף להחלטה על `CHANGELOG.md` (Q1).
- דוח על יותר מחודש אחד, או על טווח תאריכים.

## 3. דרישות פונקציונליות

**פענוח ואימות (t1 — R1, R2)**

- **FR1 — מבנה הפנקס:** קובץ UTF-8 (BOM מותר ומתעלמים ממנו), שורת כותרת שמציינת את העמודות `id`, `date`, `amount`, `currency`, `category`, `memo` בכל סדר; העמודות מותאמות לפי שם, עמודות נוספות מתעלמים מהן. שדות נחתכים מרווחים בקצוות. שורות ריקות או שכולן רווחים מדולגות אך נספרות במספור השורות. memo יכול להיות ריק ויכול להיות במירכאות עם פסיק.
- **FR2 — תנועה:** כל שורה תקינה הופכת ל-`Transaction` קפוא (frozen dataclass) עם `id`, `date` (`datetime.date`), `amount` (`Decimal` בדיוק כטקסט), `currency`, `category`, `memo`, לפי סדר הקובץ.
- **FR3 — שתי נקודות כניסה:** `parse_lines(lines)` מקבל כל iterable של שורות; `parse_csv(path)` פותח את הקובץ ב-`utf-8-sig` ו-`newline=""` ומאציל ל-`parse_lines`.
- **FR4 — שגיאת נתונים:** שורה פגומה מעלה `LedgerError(line, reason)`, ש-`str` שלה הוא `line {line}: {reason}`; מספר השורה פיזי (הכותרת היא 1, שורות ריקות נספרות); העצירה בשורה הפגומה הראשונה. הסיבות בנוסחן המדויק מופיעות בתרחישים 5–7.
- **FR5 — כותרת:** קובץ ריק → `missing header` בשורה 1; עמודות חסרות → `missing column(s): ...` בסדר הקנוני. קובץ עם כותרת בלבד → רשימה ריקה.

**דוח חודשי (t2 — R3, R4)**

- **FR6 — סינון:** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` כולל רק תנועות שהתאריך שלהן בחודש `YYYY-MM`.
- **FR7 — המרה:** כל סכום מומר `amount × rates[currency] ÷ rates[base]` בדיוק Decimal מלא לפני הסכימה. `RATES` קבוע: ILS 1, USD 3.70, EUR 4.00 (ILS ליחידה). השערים ניתנים כפרמטר.
- **FR8 — סכומים:** income = סכום החיוביים, expense = סכום השליליים, net = סכום הכול, וסכום לכל קטגוריה עם מספר תנועותיה. כל נתון מעוגל פעם אחת, באופן עצמאי, לשני מקומות ב-`ROUND_HALF_EVEN`; הדוח אינו מכריח אותם להסתכם.
- **FR9 — סדר וחיתוך:** הקטגוריות (`CategoryTotal(name, total, count)`) ממוינות לפי ערך מוחלט יורד, ובשוויון לפי שם עולה; `top` שומר את N הראשונות בלבד, בלי להשפיע על count/income/expense/net.
- **FR10 — חודש ריק:** דוח אפס, לא שגיאה. `to_dict()` מחזיר סכומים כמחרוזות בשני מקומות.
- **FR11 — שגיאות קורא:** חודש לא תקין, base שאינו מפתח ב-rates, או `top < 1` → `ValueError` (לעולם לא `LedgerError`).

**שורת פקודה (t3 — R5)**

- **FR12 — פקודה:** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`; `--base` ברירת מחדל ILS; `--top` מספר שלם ≥ 1.
- **FR13 — פלט:** טקסט בפורמט המדויק של תרחיש 19 (וכשאין קטגוריות: `categories: none`), או JSON בפורמט תרחיש 20.
- **FR14 — קודי יציאה:** 0 הצלחה; 2 שימוש שגוי (כולל קובץ שלא נפתח) עם הודעה ב-stderr ושום דבר ב-stdout; 3 שגיאת נתונים עם `error: {FILE}:{line}: {reason}` ב-stderr ושום דבר ב-stdout.

## 4. חוויית משתמש והתנהגות

- **זרימה עיקרית:** המפתח מריץ `python -m ledger report ledger.csv --month 2026-03` ומקבל שלוש-עשרה שורות טקסט (בדוגמת התרחיש): כותרות `month`, `base`, `transactions`, `income`, `expense`, `net`, `categories:`, ואחריהן קטגוריה בשורה, בהזחה של שני רווחים, בפורמט `  name: total (count)`. כל סכום תמיד בשני מקומות עשרוניים.
- **JSON:** עם `--json` הפלט הוא אובייקט JSON אחד עם המפתחות `month`, `base`, `count`, `income`, `expense`, `net`, `categories` (רשימת `{name, total, count}`); סכומים הם מחרוזות.
- **מצבים שהמשתמש רואה:** הצלחה (קוד 0, stderr ריק); חודש ללא תנועות — דוח אפס עם `categories: none` (קוד 0); שימוש שגוי (קוד 2, הודעה ב-stderr); שורה פגומה (קוד 3, הודעה אחת ב-stderr שמציינת את הקובץ כפי שנמסר, את מספר השורה ואת הסיבה). בכל מקרה של שגיאה stdout ריק — המשתמש לעולם אינו רואה דוח חלקי.
- **עזרה:** `python -m ledger report --help` מתעד את `--month` ויוצא בקוד 0.
- **דטרמיניזם:** אותו קובץ ואותם ארגומנטים נותנים תמיד אותו פלט בדיוק; אין גישה לרשת.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: a valid file parses in order. Given `tests/fixtures/ledger/sample.csv` holds the header and nine valid rows (seven dated 2026-03, one 2026-02-27, one 2026-04-01; ids `t001`…`t009`), When `parse_csv(path)` is called, Then it returns nine `Transaction` values in file order, each a frozen dataclass with `id` (str), `date` (`datetime.date`), `amount` (`Decimal`, exactly the text's value, so `12000.00` stays `Decimal("12000.00")`), `currency` (str), `category` (str) and `memo` (str, possibly empty).
2. Scenario 2 — Happy path: header order is free and fields are stripped. Given a header `memo,category,currency,amount,date,id` and a row whose fields carry surrounding spaces, When the text is parsed, Then the transaction holds the trimmed values and the columns are matched by name, not by position. Columns beyond the six named ones are ignored.
3. Scenario 3 — Boundary: BOM, blank lines and a quoted memo. Given `tests/fixtures/ledger/bom_blank.csv` starts with a UTF-8 BOM, has blank and whitespace-only lines between rows, an empty memo on one row and a memo quoted because it contains a comma on another, When parsed, Then two transactions are returned, the BOM and the blank lines are ignored, the empty memo is `""` and the quoted memo keeps its comma.
4. Scenario 4 — Boundary: header only. Given a file with the header row and no data rows, When parsed, Then an empty list is returned and no error is raised.
5. Scenario 5 — Error: a bad row raises `LedgerError(line, reason)`. Given a row that cannot become a transaction, When parsed, Then `LedgerError` is raised carrying `line` (the physical line number in the file: the header is line 1 and blank lines count) and `reason`, with `str(error)` equal to `line {line}: {reason}`, and the reason for each case is exactly: a date not matching `YYYY-MM-DD` → `date '2026-3-1' is not YYYY-MM-DD`; a well-formed date that is not a calendar date → `date '2026-02-30' is not a calendar date`; an amount that is not a decimal number, including `NaN` and `Infinity` → `amount 'abc' is not a number`; an amount with more than two decimal places → `amount '1.505' has more than 2 decimal places`; a zero amount → `amount must not be zero`; a currency outside ILS/USD/EUR, compared case-sensitively → `unknown currency 'usd'`; an empty category → `empty category`; an empty id → `empty id`; a row whose field count differs from the header's → `expected 6 fields, got 5`. Parsing stops at the first bad row.
6. Scenario 6 — Error: duplicate id. Given two rows share an id, with a blank line between them, When parsed, Then the error names the second row's line and reads `duplicate id 't1' (first seen on line 2)`.
7. Scenario 7 — Error: header problems. Given a header lacking required columns, When parsed, Then `LedgerError(1, "missing column(s): currency, category, memo")` lists the missing names in the canonical order `id, date, amount, currency, category, memo`; Given an empty file (`tests/fixtures/ledger/empty.csv`, zero bytes), When parsed, Then `LedgerError(1, "missing header")`.
8. Scenario 8 — Edge: two entry points. Given ledger text as any iterable of lines (for example an `io.StringIO`), When `parse_lines(lines)` is called, Then it behaves exactly as `parse_csv` does on a file; `parse_csv(path)` opens the path with encoding `utf-8-sig` and `newline=""` and delegates to `parse_lines`.
9. Scenario 9 — Happy path: March of the sample in ILS. Given the nine sample transactions, When `monthly_report(transactions, "2026-03")` is called, Then the report has `month` `2026-03`, `base` `ILS`, `count` 7, `income` `Decimal("12925.00")`, `expense` `Decimal("-3025.50")`, `net` `Decimal("9899.50")`, and `categories` is the list of `CategoryTotal(name, total, count)` ordered by absolute total descending: salary 12000.00 (1), rent -1500.00 (1), freelance 925.00 (1), groceries -760.50 (2), software -444.00 (1), travel -321.00 (1).
10. Scenario 10 — Happy path: another base currency. Given the sample, When the report is built with `base="USD"`, Then every amount is converted as `amount × RATES[currency] ÷ RATES[base]` at full Decimal precision before summing, so salary totals `3243.24` and freelance `250.00`, and the report's `base` reads `USD`. `RATES` is a module constant mapping `ILS` → `Decimal("1")`, `USD` → `Decimal("3.70")`, `EUR` → `Decimal("4.00")`.
11. Scenario 11 — Boundary: rounding happens once, after summing, half to even. Given one transaction of 0.05 ILS, When reported in base EUR, Then `income` is `0.01` (the exact 0.0125 rounded once); Given three such transactions, Then `income` is `0.04` (the exact sum 0.0375 rounded once), not `0.03` (three individually rounded cents). Every figure (`income`, `expense`, `net`, each category total) is the exact sum quantized to two places with `ROUND_HALF_EVEN`, independently of the others, so the report does not force them to add up.
12. Scenario 12 — Boundary: two places always. Given transactions of 5 ILS and -2 ILS, When reported, Then `str(income)` is `5.00`, `str(expense)` is `-2.00` and `str(net)` is `3.00`.
13. Scenario 13 — Happy path: top-N. Given the sample, When the report is built with `top=2`, Then `categories` is salary then rent only, while `income`, `expense`, `net` and `count` still cover all seven transactions; a `top` larger than the number of categories keeps them all; `top=None` (the default) keeps them all.
14. Scenario 14 — Edge: ties. Given two categories with equal absolute totals, When reported, Then they are ordered by category name ascending.
15. Scenario 15 — Edge: empty month is a zero report. Given the sample, When the report is built for `2026-05`, Then `count` is 0, `income`, `expense` and `net` are `Decimal("0.00")`, `categories` is empty, and `report.to_dict()` is `{"month": "2026-05", "base": "ILS", "count": 0, "income": "0.00", "expense": "0.00", "net": "0.00", "categories": []}`.
16. Scenario 16 — Edge: only the month's transactions count. Given the sample, When the report is built for `2026-02`, Then `categories` is exactly groceries -99.99 (1).
17. Scenario 17 — Edge: rates are a parameter. Given `rates={"ILS": 1, "USD": 2, "EUR": 4}` as Decimals, When a 10 USD transaction is reported in ILS, Then `income` is `20.00`.
18. Scenario 18 — Error: arguments. When `month` is not `YYYY-MM` with a month of 01–12 (`2026-3`, `2026-13`, `2026-00`, `March 2026`, `202603`, the empty string), Then `ValueError` is raised; when `base` is not a key of `rates`, Then `ValueError`; when `top` is less than 1, Then `ValueError`. These are caller errors, never `LedgerError`.
19. Scenario 19 — Happy path: text report. When `python -m ledger report tests/fixtures/ledger/sample.csv --month 2026-03` runs, Then it exits 0 with nothing on stderr and stdout is exactly these thirteen lines: `month: 2026-03`, `base: ILS`, `transactions: 7`, `income: 12925.00`, `expense: -3025.50`, `net: 9899.50`, `categories:`, then one line per category, indented by two spaces, in report order: `  salary: 12000.00 (1)`, `  rent: -1500.00 (1)`, `  freelance: 925.00 (1)`, `  groceries: -760.50 (2)`, `  software: -444.00 (1)`, `  travel: -321.00 (1)`.
20. Scenario 20 — Happy path: JSON with base and top. When the same command runs with `--base USD --top 1 --json`, Then it exits 0 and stdout parses as the JSON object `{"month": "2026-03", "base": "USD", "count": 7, "income": "3493.24", "expense": "-817.70", "net": "2675.54", "categories": [{"name": "salary", "total": "3243.24", "count": 1}]}` — amounts are strings, so no precision is lost.
21. Scenario 21 — Edge: empty month on the command line. When the command runs with `--month 2026-05`, Then it exits 0 and stdout ends with the lines `income: 0.00`, `expense: 0.00`, `net: 0.00`, `categories: none`.
22. Scenario 22 — Error: usage. When the command line is wrong — no subcommand; `--month` missing; `--month 2026-13`; `--top 0`; `--base GBP`; a FILE that cannot be opened — Then the process exits 2, prints nothing on stdout and a message on stderr. `--base` accepts exactly ILS, USD and EUR and defaults to ILS; `--top` accepts integers of at least 1.
23. Scenario 23 — Error: data. When the FILE has a bad row (`tests/fixtures/ledger/bad_amount.csv`, whose third line carries the amount `-2.505`), Then the process exits 3, prints nothing on stdout and stderr is exactly `error: {FILE}:3: amount '-2.505' has more than 2 decimal places` followed by a newline, FILE being the path as given on the command line.
24. Scenario 24 — Happy path: help. When `python -m ledger report --help` runs, Then it exits 0 and stdout documents `--month`.
25. Scenario 25 — Edge: the tests run the real entry point. Given `tests/test_ledger_cli.py`, When it drives the command, Then it does so through `subprocess` with `[sys.executable, "-m", "ledger", ...]`, relying on the installed package and on no `sys.path` manipulation.

## 6. תלויות ואילוצים (ברמת המוצר)

- **תנאי מוקדם — אומת במאגר:** `pyproject.toml` מגלה חבילות תחת `src/` (`[tool.setuptools.packages.find] where = ["src"]`), `testpaths = ["tests"]`, ושער הבדיקות (`.factory/testing.md`, ו-job `test` ב-`.github/workflows/ci.yml`) מריץ `pip install -e ".[test]"` ואז `pytest` על Python 3.12. אין היום `src/ledger/` ואין `tests/test_ledger_*.py`. לכן חבילה חדשה תחת `src/` תותקן ותהיה זמינה ל-`python -m ledger` בלי לגעת ב-`pyproject.toml`.
- **שער המאגר (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** קוד Python תחת `src/` ובדיקות תחת `tests/` (מתקיים); אין קובץ מעל 200KB (מתקיים, הפיקסצ'רים קטנים); **כל בקשת מיזוג חייבת להוסיף שורה תחת `## Unreleased` ב-`CHANGELOG.md`** — אחרת חוסם PLAY-G4. הכלל הזה מתנגש בסעיף "changes to any existing file of the repository" שבהקשר הסיפור — ראו Q1. השער רץ מכנית ואין ממנו פטור.
- **ספרייה סטנדרטית בלבד:** אין תלות חדשה; התלויות הקיימות (`pypdf`, `flask`) אינן בשימוש החבילה.
- **מילון claims (`.factory/plugins/claims-dev/skills/glossary`):** חל על קוד חשבוניות/תביעות; הפנקס אינו כזה, ולכן המונחים income/expense/net של הסיפור נשמרים.
- **בקשת מיזוג:** אדם ממזג אחרי סקירה; המפעל אינו ממזג. "הושלם" נמדד בכך שהבדיקות הנדרשות של בקשת המיזוג ירוקות.

## 7. תכנון טכני (נדחה לשלב STRUCTURE)

ארכיטקטורת המודולים, חלוקה לבקשות מיזוג (האם t1–t3 הם בקשה אחת או שלוש), אופן הפענוח, מבנה ה-argparse ותוכן הפיקסצ'רים מעבר למה שהתרחישים קובעים — כולם בשלב STRUCTURE. אילוצים שהמוצר מטיל: `Decimal` מקצה לקצה; ספרייה סטנדרטית בלבד; כניסה דרך `python -m ledger` (ולא console script, שמחייב שינוי ב-`pyproject.toml`); הפיקסצ'רים `sample.csv`, `bom_blank.csv`, `empty.csv`, `bad_amount.csv` תחת `tests/fixtures/ledger/` צריכים להפיק בדיוק את המספרים שבתרחישים 9–23.

## 8. שאלות פתוחות

- **Q1 (חוסם) — יומן השינויים מול "אין שינוי בקבצים קיימים".** שער play1 חוסם כל בקשת מיזוג שלא מוסיפה שורה תחת `## Unreleased` ב-`CHANGELOG.md` (PLAY-G4), אבל הקשר הסיפור מוציא מהתחום כל שינוי בקובץ קיים. האפשרויות: (א) להרחיב את התחום כך שיתיר שורה אחת (לכל בקשת מיזוג) תחת `## Unreleased` ב-`CHANGELOG.md` שמציינת את SCRUM-24, וכל קובץ קיים אחר נשאר מחוץ לתחום; (ב) לשנות קודם את כלל השער במאגר בשינוי נפרד. **המלצה: (א)** — זה הדפוס של כל סיפור קודם ב-play1 (PLAY-156, PLAY-172, PLAY-175 הוסיפו שורה כזו), והוא לא דורש שינוי ממשל. רק אם יש סיבה שהיומן לא ייגע — (ב).
- **הנחה גלויה (לא חוסמת):** תוכן הפיקסצ'רים מעבר לערכים שהתרחישים מקבעים (תיאורים, מטבע של כל שורה) נקבע ב-STRUCTURE, בתנאי שיפיק בדיוק את הסכומים שבתרחישים 9, 10, 16, 19, 20.
