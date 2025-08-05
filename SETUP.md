# הוראות התקנה והפעלה - מעקב הודעות טלגרם

## שלב 1: קבלת פרטי API מטלגרם

1. **היכנס ל:** https://my.telegram.org
2. **התחבר עם מספר הטלפון שלך**
3. **לחץ על "API development tools"**
4. **מלא את הפרטים:**
   - App title: `Telegram Monitor`
   - Short name: `telegram_monitor`
   - Platform: `Desktop`
   - Description: `Personal telegram message monitor`
5. **לחץ על "Create application"**
6. **שמור את הפרטים:**
   - `api_id` (מספר)
   - `api_hash` (מחרוזת)

## שלב 2: התקנת Python ותלויות

### התקנת Python:
```bash
# macOS (עם Homebrew)
brew install python

# או הורד ישירות מ: https://www.python.org/downloads/
```

### התקנת התלויות:
```bash
pip3 install -r requirements.txt
```

## שלב 3: הגדרת הסקריפט

### עריכת telegram_monitor.py:
```python
# החלף את השורות הבאות עם הפרטים שלך:
API_ID = "12345678"  # המספר שקיבלת
API_HASH = "abcdef1234567890abcdef1234567890"  # המחרוזת שקיבלת
PHONE = "+972501234567"  # מספר הטלפון שלך עם קוד מדינה
WEBHOOK_URL = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
```

### עריכת manage_groups.py:
```python
# החלף את השורות הבאות עם אותם פרטים:
API_ID = "12345678"
API_HASH = "abcdef1234567890abcdef1234567890"
PHONE = "+972501234567"
WEBHOOK_URL = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
```

## שלב 4: הפעלה ראשונית

### הפעלת מנהל הקבוצות:
```bash
python3 manage_groups.py
```

**בפעם הראשונה:**
1. תקבל הודעת SMS עם קוד אימות
2. הכנס את הקוד
3. אם יש סיסמה דו-שלבית, הכנס גם אותה

### הוספת קבוצות:
1. בחר אפשרות 2 - "הוסף קבוצה"
2. הכנס שם לקבוצה (לדוגמה: "קבוצת עבודה")
3. הכנס קישור לקבוצה (אחד מהפורמטים):
   - `https://t.me/groupname`
   - `@groupname`
   - `t.me/groupname`
   - `groupname`

## שלב 5: הפעלת המעקב

### הפעלת המוניטור:
```bash
python3 telegram_monitor.py
```

**הסקריפט יעבוד ברקע ו:**
- יעקוב אחרי הודעות בקבוצות שהוספת
- ישלח כל הודעה לוובהוק
- ישמור לוגים בקובץ `telegram_monitor.log`
- ישמור נתונים במסד נתונים `telegram_monitor.db`

## שלב 6: בדיקת הפונקציונליות

1. **שלח הודעה בקבוצה שאתה עוקב אחריה**
2. **בדוק את הוובהוק שלך** - תקבל הודעה עם כל הפרטים
3. **בדוק את הלוגים** בקובץ `telegram_monitor.log`

## מבנה הקבצים

```
telegram/
├── index.html              # ממשק משתמש (דמו)
├── telegram_monitor.py     # הסקריפט הראשי
├── manage_groups.py        # מנהל קבוצות
├── requirements.txt        # תלויות Python
├── telegram_monitor.db     # מסד נתונים (נוצר אוטומטית)
├── telegram_monitor.log    # לוגים (נוצר אוטומטית)
├── session_name.session    # פרטי התחברות (נוצר אוטומטית)
├── README.md              # קובץ זה
└── SETUP.md               # הוראות התקנה
```

## פתרון בעיות

### שגיאה: "Phone number invalid"
- ודא שמספר הטלפון כולל קוד מדינה (+972...)

### שגיאה: "API_ID/API_HASH invalid"
- בדוק שהפרטים נכונים מ-my.telegram.org

### שגיאה: "Group not found"
- ודא שאתה חבר בקבוצה
- ודא שהקישור נכון

### שגיאה: "Webhook failed"
- בדוק שהכתובת נכונה
- בדוק שהוובהוק פעיל

## הערות חשובות

⚠️ **אזהרה:** הסקריפט משתמש בחשבון האישי שלך. אל תשתף את פרטי ההתחברות.

🔒 **אבטחה:** הקובץ `session_name.session` מכיל פרטי התחברות. שמור אותו במקום בטוח.

📱 **הגבלות:** טלגרם מגביל את מספר ההודעות שאפשר לקרוא. אל תעקוב אחרי יותר מדי קבוצות.

## תמיכה

אם יש בעיות:
1. בדוק את הלוגים ב-`telegram_monitor.log`
2. בדוק את מסד הנתונים ב-`telegram_monitor.db`
3. נסה להפעיל מחדש את הסקריפט 