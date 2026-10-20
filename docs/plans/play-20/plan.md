# תוכנית מימוש — t1: Guestbook JSON API (roeeoz/play1)

## 1. Context

מוסיפים ל-play1 את המשטח ה-HTTP הראשון שלו: API בפורמט JSON לספר אורחים עם שתי נקודות קצה, יצירת רשומה ורשימת כל הרשומות מהחדשה לישנה. הריפו מכיל היום רק את חבילת `testbed_utils`, ללא שרת או שכבת התמדה. השירות נבנה כחבילה חדשה `src/guestbook/` על Flask 3 ו-SQLite מה-stdlib, והחוזה שהוא חושף (נתיבים, שדות, מעטפת שגיאה, `id` יציב) נקפא במיזוג כי s2 (דף) ו-s3 (מחיקה) נבנים עליו במקביל בגל הבא.

## 2. Approach

פריט עבודה יחיד (t1), PR אחד, קומיטים קטנים בסדר שמאפשר להריץ בדיקות אחרי כל שלב. בונים מלמטה למעלה: תלויות ו-packaging, אחר כך שני המודולים הטהורים (ולידציה, אחסון) שנבדקים בנפרד, אחר כך אפליקציית Flask שמחברת אותם, ולבסוף בדיקות HTTP דרך test client ותיעוד.

שימוש חוזר בקיים:
- `[tool.setuptools.packages.find] where=["src"]` מגלה את החבילה החדשה אוטומטית. אין לשנות שם/גרסה של החבילה.
- CI מריץ `pip install -e ".[test]"` ואז `pytest`, לכן הוספת `flask` ל-`dependencies` מספיקה. אין לגעת ב-`.github/workflows/ci.yml` ואין ליצור `CI_FAIL`.
- `.gitignore` כבר מכיל `instance/`, לכן נתיב DB ברירת מחדל `instance/guestbook.sqlite3` לא דורש שינוי.
- קונבנציות הקוד הקיימות: `from __future__ import annotations`, docstrings במודולים, מחלקות `TestXxx` עם מתודות `test_*` ב-pytest.

אילוצים: `requires-python >= 3.10`, לכן אין להשתמש ב-`datetime.UTC` (קיים רק מ-3.11). `src/testbed_utils/**` והבדיקות הקיימות (38) נשארים ללא שינוי.

## 3. Steps

כל השלבים שייכים ל-t1.

### שלב 1 — packaging (`pyproject.toml`)
- להוסיף `"flask>=3"` למערך `dependencies` (לצד `pypdf`).
- להוסיף סעיף `[project.scripts]` עם `guestbook = "guestbook.app:main"`.
- לא לשנות `[project.optional-dependencies].test`, `[tool.pytest.ini_options]`, או הגדרות setuptools.
- אימות: `pip install -e ".[test]"` בסביבה נקייה מתקין Flask ועוד 6 חבילות טהורות בלבד (Werkzeug, Jinja2, MarkupSafe, itsdangerous, click, blinker).

### שלב 2 — חבילה וולידציה (`src/guestbook/__init__.py`, `src/guestbook/validation.py`)
- `__init__.py`: docstring קצר (המשטח ה-HTTP הראשון של play1) וייצוא `create_app` מ-`guestbook.app`.
- `validation.py`: קבועים `AUTHOR_MAX = 50`, `MESSAGE_MAX = 300`, ופונקציה טהורה:
  `validate_entry(payload: object) -> tuple[dict[str, str] | None, dict[str, str]]`.
  - אם `payload` אינו `dict`: מחזירה `(None, {})` והקורא מטפל בזה כ-`invalid_json` (או לחלופין הקורא בודק `isinstance` לפני הקריאה, לבחירת המיישם, אך עקבי).
  - לכל שדה (`author`, `message`): חסר / לא `str` / ריק אחרי `strip()` / אורך אחרי strip מעל המקסימום, נכשל עם הודעה קבועה באנגלית פשוטה, למשל `"is required"`, `"must be a string"`, `"must be between 1 and 50 characters"`. האורך נמדד ב-code points (`len` על מחרוזת Python).
  - הצלחה: `({"author": stripped, "message": stripped}, {})`. כשל: `(None, {field: msg, ...})` רק עם השדות שנכשלו.

### שלב 3 — אחסון (`src/guestbook/storage.py`)
- `sqlite3` בלבד. סכימה:
  `CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL)`.
- פונקציות:
  - `init_db(path: str) -> None`: יוצר את תיקיית האב אם חסרה (`Path(path).parent.mkdir(parents=True, exist_ok=True)`) ומריץ את ה-DDL.
  - `insert_entry(path, author, message, created_at) -> dict`: INSERT, מחזיר `{"id": cursor.lastrowid, "author", "message", "created_at"}`.
  - `list_entries(path) -> list[dict]`: `SELECT id, author, message, created_at FROM entries ORDER BY created_at DESC, id DESC`.
- אסטרטגיית threads: חיבור חדש לכל קריאה בתוך `with sqlite3.connect(path) as conn` (עם `closing` כדי לסגור בפועל). אין חיבור משותף, אין `check_same_thread=False`, אין נעילה ידנית. SQLite מטפל בנעילת הקובץ בין threads של שרת הפיתוח.

### שלב 4 — אפליקציה ו-entry point (`src/guestbook/app.py`)
- `create_app(db_path: str | None = None) -> Flask`:
  - פתרון נתיב DB: פרמטר, אחרת `os.environ.get("GUESTBOOK_DB_PATH")`, אחרת `instance/guestbook.sqlite3` יחסית ל-CWD. שומר ב-`app.config["GUESTBOOK_DB_PATH"]` וקורא `init_db` בזמן היצירה.
  - פונקציית עזר `_error(code: str, status: int, fields: dict | None = None)` שמחזירה `{"error": {"code": code}}` ומוסיפה `fields` רק אם נמסר.
  - פונקציית עזר `_utc_now_iso() -> str`: `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")`. לא להשתמש ב-`isoformat()` (מחזיר `+00:00`) ולא ב-`datetime.UTC`.
  - `POST /api/guestbook/entries`: `payload = request.get_json(silent=True, force=True)`. אם `payload` אינו `dict` (כולל `None` עבור body לא-JSON או JSON `null`): 400 `invalid_json`. אחרת `validate_entry`; אם יש שגיאות: 400 `validation_error` עם `fields`. אחרת `insert_entry` עם `created_at` מהשרת (כל `created_at` מהלקוח מוזנח פשוט כי לא נקרא) ומחזירים 201 עם הרשומה.
  - `GET /api/guestbook/entries`: 200 עם `jsonify(list_entries(...))`, מערך ריק כשאין רשומות.
- `main() -> None`: `create_app().run()` (שרת פיתוח מקומי, ברירת מחדל 127.0.0.1:5000). זהו היעד של ה-console script.
- לא להסתמך על `flask.__version__` (הוצא משימוש ב-3.1).

### שלב 5 — בדיקות (`tests/test_guestbook_api.py`)
- fixture `client(tmp_path)`: `create_app(db_path=str(tmp_path / "test.sqlite3"))` ואז `app.test_client()`. DB זמני מבודד לכל בדיקה.
- helper `post(client, body)` שקורא `client.post("/api/guestbook/entries", json=body)`.
- מחלקות בדיקה (ראו מיפוי בסעיף 4):
  - `TestCreateEntry`: הצלחה (201, 4 שדות, `created_at` מסתיים ב-`Z` ונפרס עם `%Y-%m-%dT%H:%M:%S.%fZ`, ערכים trimmed), `created_at` מהלקוח מוזנח, גבולות בדיוק 50/300 מתקבלים, תווים לא-ASCII נספרים כ-code points.
  - `TestCreateValidation`: `pytest.mark.parametrize` על author/message חסר, `None`, מספר, `""`, `"   "`, 51 / 301 תווים. כל מקרה: 400, `code == "validation_error"`, `fields` מכיל בדיוק את השדות שנכשלו, ואחריו GET מחזיר `[]`. מקרה נוסף ששני השדות נכשלים יחד ושניהם מופיעים ב-`fields`.
  - `TestInvalidJson`: body טקסט לא-JSON (`data="not json"`), body מערך, body `null`. כל אחד: 400 `invalid_json` ללא `fields`, GET מחזיר `[]`.
  - `TestListEntries`: DB ריק מחזיר 200 ו-`[]`; אחרי שתי יצירות כל אלמנט עם 4 מפתחות; סדר לפי `id` יורד; שתי קריאות GET עוקבות מחזירות תוצאה זהה.
  - `TestNoPagination`: לולאה של 100 POST, GET מחזיר 100, רשימת ה-`id` יורדת מונוטונית.
  - `TestAppSetup`: `create_app(db_path=...)` יוצר את קובץ ה-DB בנתיב שנמסר (כולל תיקייה חסרה); `GUESTBOOK_DB_PATH` דרך `monkeypatch.setenv` מכובד כשלא נמסר פרמטר; 20 יצירות במקביל דרך `ThreadPoolExecutor` (test client נפרד לכל thread מאותה אפליקציה) ואז GET מחזיר 20 עם `id` ייחודיים.

### שלב 6 — תיעוד (`README.md`)
- להוסיף סעיף חדש `## Guestbook API` בסוף הקובץ, בלי לשנות את הסעיפים הקיימים (ה-README הוא fixture של Demerzel). הסעיף הוא feature-scoped ואינו מספור משותף, לכן אין סיכון התנגשות עם s2/s3 שיוסיפו סעיפים משלהם.
- תוכן: שתי נקודות הקצה עם דוגמת בקשה ותגובה, מעטפת השגיאה (`validation_error` עם `fields`, `invalid_json`), משתנה `GUESTBOOK_DB_PATH` וברירת המחדל `instance/guestbook.sqlite3` (יחסית ל-CWD), הרצה (`pip install -e .` ואז `guestbook`), בדיקה (`pytest`), והערה שזה שרת פיתוח מקומי ללא auth או rate limit.

## 4. Verification

**במהלך הפיתוח:** אחרי שלב 1 `pip install -e ".[test]"` בסביבה נקייה. אחרי שלבים 2 ו-3 אפשר להריץ בדיקות יחידה ישירות על `validate_entry` ועל `storage` (חלק מ-`tests/test_guestbook_api.py`, או בדיקות מהירות ב-REPL). אחרי שלב 4 `pytest` מלא, ואז `guestbook` ידני עם `curl` על שתי נקודות הקצה.

**מיפוי קריטריוני קבלה לבדיקות:**

| AC | בדיקה |
|---|---|
| 1 יצירה תקינה מחזירה רשומה עם זמן שרת | `TestCreateEntry`: 201, 4 שדות, `Z`, trimmed, `created_at` מהלקוח מוזנח |
| 2 דחייה ללא שמירה | `TestCreateValidation` + `TestInvalidJson`: 400 עם המעטפת הנכונה, GET עוקב מחזיר `[]` |
| 3 רשימה עם כל השדות | `TestListEntries`: כל אלמנט עם `id`, `author`, `message`, `created_at` |
| 4 סדר מוחלט מהחדשה לישנה | `TestListEntries`: `id` יורד, שתי קריאות זהות; `TestNoPagination`: 100 `id` יורדים מונוטונית |
| 5 ריק מחזיר `[]` | `TestListEntries` על DB טרי |
| 6 100 רשומות ללא חיתוך | `TestNoPagination` |
| 7 משטח HTTP עצמאי, threads, נתיב DB | `TestAppSetup`: קובץ DB נוצר, env var מכובד, 20 יצירות במקביל |

**בדיקה סופית לפני PR:** `pytest` מלא עובר (38 קיימות + החדשות), `pip freeze` מראה רק Flask ו-6 התלויות הטרנזיטיביות שנוספו, `git status` מראה שינויים רק ב-`pyproject.toml`, `README.md`, `src/guestbook/`, `tests/test_guestbook_api.py`. אין קובץ `CI_FAIL`. הרצה ידנית של `guestbook` ו-`curl -X POST -H 'Content-Type: application/json' -d '{"author":"a","message":"b"}' localhost:5000/api/guestbook/entries` ואז GET.

## 5. Risks & open points

- **החוזה נקפא במיזוג.** s2 ו-s3 בונים עליו במקביל. כל שינוי בשמות שדות, נתיבים, קודי סטטוס או מעטפת שגיאה אחרי המיזוג שובר אותם. הרשומה המוחזרת מ-POST ומ-GET חייבת להיות זהה במבנה.
- **פורמט `created_at`.** מוצע `%Y-%m-%dT%H:%M:%S.%fZ` (microseconds). אם s2 מעדיף שניות שלמות יש להחליט לפני המיזוג. JavaScript `Date.parse` מקבל את שני הפורמטים.
- **Werkzeug 3 מחזיר 415 על mimetype לא-JSON.** נפתר עם `get_json(silent=True, force=True)`. `silent=True` מחזיר `None` גם על JSON `null` תקין, וזה מתאים כי `null` אינו אובייקט. הבדיקות ב-`TestInvalidJson` מגנות על זה.
- **בטיחות threads.** נבחר חיבור חדש לכל קריאה במקום חיבור משותף עם נעילה (החלטה שה-HLD השאיר למיישם). פשוט ונכון לשרת פיתוח; העלות של פתיחת חיבור לקובץ SQLite זניחה בהיקף הזה. הבדיקה המקבילית מכסה את הנתיב.
- **`payload` לא-dict.** ההחלטה אם `validate_entry` או ה-route בודקים `isinstance(payload, dict)` היא פרט מימוש. חשוב רק שהתוצאה היא 400 `invalid_json` ולא `validation_error`.
- **נתיב DB ברירת מחדל יחסי ל-CWD.** מתועד ב-README. הבדיקות אינן נוגעות בו כי הן תמיד מקבלות נתיב זמני.
- **הודעות שגיאה באנגלית בלבד.** אם s2 ירצה עברית, המיפוי יהיה בצד s2 לפי שם השדה. לא חלק מהחוזה.
- **אין הגנות by design.** ללא auth, rate limit או הגבלת גודל GET. מקובל לפי ה-non-goals ומתועד כ-local development only.
- **סביבה מקומית מול CI.** המחקר אומת על Python 3.14, CI רץ על 3.12, והריפו מבטיח 3.10. הקוד נמנע מ-`datetime.UTC` ומתחביר חדש מ-3.11 ואילך.
