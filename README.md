# מעקב הודעות טלגרם - Telegram Message Monitor

אפליקציה לניהול מעקב אחרי הודעות בקבוצות טלגרם ושליחתן לוובהוק באמצעות המשתמש האישי שלך.

## תכונות

- ✨ מעקב אמיתי אחרי הודעות טלגרם
- 📱 שימוש בחשבון האישי שלך (ללא בוט)
- 🔗 שליחה אוטומטית לוובהוק
- 📊 שמירת נתונים במסד נתונים SQLite
- 🌐 ממשק ניהול פשוט
- 📝 לוגים מפורטים
- 🔒 אבטחה מלאה

## התקנה מהירה

### 1. קבלת פרטי API
1. היכנס ל: https://my.telegram.org
2. התחבר עם מספר הטלפון שלך
3. לחץ על "API development tools"
4. צור אפליקציה חדשה
5. שמור את `api_id` ו-`api_hash`

### 2. התקנת Python ותלויות
```bash
# התקן Python (אם לא מותקן)
brew install python

# התקן תלויות
pip3 install -r requirements.txt
```

### 3. הגדרת הסקריפט
ערוך את הקבצים `telegram_monitor.py` ו-`manage_groups.py`:
```python
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
PHONE = "YOUR_PHONE_NUMBER"  # עם קוד מדינה (+972...)
WEBHOOK_URL = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
```

### 4. הפעלה
```bash
# הוספת קבוצות
python3 manage_groups.py

# הפעלת המעקב
python3 telegram_monitor.py
```

## שימוש

### הוספת קבוצות:
1. הפעל `python3 manage_groups.py`
2. בחר אפשרות 2 - "הוסף קבוצה"
3. הכנס שם וקישור לקבוצה
4. חזור על התהליך לכל קבוצה

### הפעלת המעקב:
1. הפעל `python3 telegram_monitor.py`
2. הסקריפט יעבוד ברקע
3. כל הודעה בקבוצות תשלח לוובהוק

### פורמטי קישורים נתמכים:
- `https://t.me/groupname`
- `@groupname`
- `t.me/groupname`
- `groupname`

## מבנה הפרויקט

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
└── SETUP.md               # הוראות מפורטות
```

## פורמט הוובהוק

כל הודעה נשלחת לוובהוק בפורמט הבא:
```json
{
  "message_id": 123456,
  "group_id": "-1001234567890",
  "group_name": "שם הקבוצה",
  "group_link": "https://t.me/groupname",
  "sender_id": 987654321,
  "sender_name": "שם השולח",
  "sender_username": "username",
  "message_text": "תוכן ההודעה",
  "timestamp": "2024-01-01T12:00:00",
  "message_type": "text",
  "has_media": false
}
```

## תכונות טכניות

- **Telethon Library:** שימוש בספריית Telethon לחיבור לטלגרם
- **SQLite Database:** שמירת קבוצות והודעות במסד נתונים מקומי
- **Async/Await:** עיבוד אסינכרוני להודעות
- **Logging:** לוגים מפורטים לקובץ ומסך
- **Error Handling:** טיפול בשגיאות מתקדם

## הערות חשובות

⚠️ **אזהרה:** הסקריפט משתמש בחשבון האישי שלך. אל תשתף את פרטי ההתחברות.

🔒 **אבטחה:** הקובץ `session_name.session` מכיל פרטי התחברות. שמור אותו במקום בטוח.

📱 **הגבלות:** טלגרם מגביל את מספר ההודעות שאפשר לקרוא. אל תעקוב אחרי יותר מדי קבוצות.

## פתרון בעיות

### שגיאות נפוצות:
- **Phone number invalid:** ודא שמספר הטלפון כולל קוד מדינה
- **API_ID/API_HASH invalid:** בדוק את הפרטים מ-my.telegram.org
- **Group not found:** ודא שאתה חבר בקבוצה
- **Webhook failed:** בדוק את כתובת הוובהוק

### לוגים:
- בדוק את הקובץ `telegram_monitor.log` לפרטים
- בדוק את מסד הנתונים `telegram_monitor.db`

## תמיכה

לפרטים נוספים והוראות מפורטות, ראה את הקובץ `SETUP.md`.

## רישיון

MIT License 