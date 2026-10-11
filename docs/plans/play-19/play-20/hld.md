# HLD — Guestbook API (s1) עבור roeeoz/play1

## 1. System Overview
- **מה נבנה:** שירות HTTP קטן בפורמט JSON לספר אורחים: יצירת רשומה והחזרת כל הרשומות מהחדשה לישנה. זהו המשטח המקוון הראשון של play1.
- **בעיה:** אין ב-play1 שרת/framework/התמדה; s2 (דף) ו-s3 (מחיקה) נבנים בגל הבא על החוזה שנקבע כאן.
- **אחריות:** ולידציה, שמירה עם זמן יצירה שנקבע בשרת, זיהוי יציב לכל רשומה (לצורך s3), רשימה ממוינת דטרמיניסטית, ללא דפדוף/מודרציה/זהות.

## 2. Architecture Overview
- **חבילה חדשה `src/guestbook/`** (auto-discovered דרך `[tool.setuptools.packages.find] where=["src"]`), לצד `src/testbed_utils/` שנשאר ללא שינוי.
- **Framework: Flask 3.x.** נימוק: 7 חבילות Python טהורות, שרת פיתוח + test client מובנים; FastAPI+uvicorn+httpx = 16 חבילות כולל compiled wheel (pydantic_core) — מנוגד לאילוץ dependency-light.
- **אחסון: SQLite דרך `sqlite3` (stdlib).** אפס תלויות, מעניק autoincrement id (זיהוי לרשומה + שובר-שוויון בסדר) ועמידות לריסטארט. נתיב קובץ ניתן להגדרה (ברירת מחדל תחת `instance/`, שכבר ב-.gitignore); בדיקות משתמשות בנתיב זמני לבידוד מלא.
- **גבולות מודולים (בתוך החבילה, להחלטת המיישם בפרטים):** app factory/routes, שכבת אחסון, ולידציה. כל אחד ניתן לבדיקה בנפרד; ה-API הציבורי הוא רק ה-HTTP.
- **תלויות חיצוניות:** Flask בלבד (מתווסף ל-`dependencies` ב-pyproject; CI מתקין `.[test]` ולכן מקבל אותו).

## 3. Data Flow Design
- **סינכרוני בלבד**, request/response. אין אירועים, אין עבודות רקע.
- **יצירה:** JSON נכנס → פרסינג → ולידציה (נוכחות, strip, אורך) → אם נכשל: 400 ללא כתיבה → אחרת INSERT עם created_at של השרת (UTC) → 201 עם הרשומה המלאה.
- **רשימה:** SELECT כל הרשומות ORDER BY created_at DESC, id DESC → 200 עם מערך (ריק אם אין).

## 4. Component Breakdown
| רכיב | אחריות | קלט/פלט | ריפו |
|---|---|---|---|
| Guestbook Flask app (`src/guestbook/`) | ניתוב, פרסינג JSON, קודי סטטוס, מעטפת שגיאה, entry point להרצה | HTTP JSON ↔ שכבת אחסון | roeeoz/play1 |
| Storage (SQLite, בתוך `src/guestbook/`) | סכימה, INSERT, SELECT ממוין, אתחול DB, בטיחות threads מול שרת הפיתוח | author/message → רשומה עם id/created_at | roeeoz/play1 |
| Validation (בתוך `src/guestbook/`) | חובה, strip, 1–50 / 1–300 תווים | dict → תקין / רשימת שגיאות לפי שדה | roeeoz/play1 |
| Packaging & docs (`pyproject.toml`, `README.md`) | תלות Flask, script להרצה, הוראות | — | roeeoz/play1 |
| Tests (`tests/test_guestbook_api.py`) | כל 7 קריטריוני הקבלה דרך test client | — | roeeoz/play1 |

## 5. Interface Contracts (נקפא עם המיזוג — s2 ו-s3 נבנים עליו במקביל)
- **POST `/api/guestbook/entries`** — body JSON: `author` (string), `message` (string). הצלחה: **201**, body: `{id, author, message, created_at}`. `id` מספר שלם יציב וייחודי; `created_at` ISO-8601 UTC עם סיומת `Z`, נקבע בשרת (ערך שנשלח בקליינט מוזנח).
- **GET `/api/guestbook/entries`** — **200**, body: מערך JSON של רשומות באותו מבנה, מהחדשה לישנה (created_at DESC, ואז id DESC). ללא רשומות: `[]`.
- **שגיאת ולידציה: 400**, body: `{"error": {"code": "validation_error", "fields": {"author": "<הודעה>", "message": "<הודעה>"}}}` — רק שדות שנכשלו מופיעים. s2 יכול להציג הבהרה לפי שדה.
- **JSON לא תקין / body לא-אובייקט: 400** באותה מעטפת עם `code: "invalid_json"` (ללא `fields`).
- **ולידציה:** ערך חסר, לא-מחרוזת, או ריק אחרי strip → נדחה. אורך נבדק על הערך אחרי strip, בתווי Python (code points): author 1–50, message 1–300. הערך הנשמר הוא אחרי strip.
- **הרצה:** `pip install -e .` ואז `guestbook` (script ב-`[project.scripts]`) מעלה שרת פיתוח מקומי; נתיב DB ניתן להגדרה דרך משתנה סביבה.

## 6. Key Technical Decisions
- Flask על פני FastAPI — dependency-light מדיד (7 מול 16 חבילות, ללא compiled).
- SQLite על פני in-memory — אפס תלויות, id יציב ל-s3, עמידות לריסטארט, בידוד בדיקות פשוט דרך נתיב זמני. חלופה in-memory נדחתה: מאבדת רשומות בריסטארט ודורשת מנגנון id ידני.
- שובר-שוויון לפי id — 100 יצירות מהירות יתנגשו בחותמת הזמן; סדר חייב להיות מוחלט (AC4/AC6).
- Strip + code points — עקבי עם `textutils.word_count` שמתייחס לרווחים-בלבד כריק; s2 יתאים את `maxlength` בהתאם.
- מעטפת שגיאה לפי שדה — נדרשת ל-AC5 של s2.

## 7. Risks & Constraints
- **SQLite + שרת פיתוח מרובה-threads:** חיבור לכל בקשה לקובץ (לא `:memory:`) או חיבור משותף עם נעילה — להחלטת המיישם, חובה לכסות בבדיקה בסיסית.
- **החוזה נקפא:** שינוי שמות שדות/פורמט אחרי המיזוג ישבור את s2 ו-s3 שבבנייה. החוזה מתועד לעיל ובתיקט.
- **ללא אמצעי הגנה (by design):** אין auth, אין rate limit, GET ללא הגבלה — מקובל לפי non-goals; לא לחשיפה ציבורית.
- **ריפו משותף כ-fixture של Demerzel:** אין לגעת ב-`testbed_utils`, ב-CI gate או ליצור `CI_FAIL`.
- **אין linter/formatter בריפו:** התאמה ידנית לקונבנציות (`from __future__ import annotations`, docstrings, מחלקות pytest).
