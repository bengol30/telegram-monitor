# 🚀 מדריך מפורט ל-Railway - שלב אחר שלב

## 📋 מה נצטרך:
1. חשבון GitHub (חינמי)
2. חשבון Railway (חינמי)
3. הקוד שלך ב-GitHub

---

## 🎯 שלב 1: הכנת הקוד ל-GitHub

### 1.1 יצירת ריפוזיטורי ב-GitHub
1. היכנס ל-github.com
2. לחץ על הכפתור הירוק "New" (או "+" → "New repository")
3. תן שם: `telegram-monitor`
4. בחר "Public"
5. לחץ "Create repository"

### 1.2 העלאת הקוד (אם אין לך Git מותקן)
```bash
# התקנת Git (אם לא מותקן)
# macOS:
brew install git

# או הורדה מהאתר הרשמי: https://git-scm.com/
```

### 1.3 העלאת הקבצים
```bash
# בתיקיית הפרויקט שלך
cd /Users/bengoproductions/Library/CloudStorage/GoogleDrive-bengo0469@gmail.com/האחסון\ שלי/תוכנות\ שבניתי/telegram

# אתחול Git
git init

# הוספת כל הקבצים
git add .

# יצירת commit ראשון
git commit -m "Initial commit - Telegram Monitor"

# הוספת remote (החלף YOUR_USERNAME בשם המשתמש שלך ב-GitHub)
git remote add origin https://github.com/YOUR_USERNAME/telegram-monitor.git

# העלאה ל-GitHub
git branch -M main
git push -u origin main
```

---

## 🚂 שלב 2: הגדרת Railway

### 2.1 יצירת חשבון Railway
1. היכנס ל-railway.app
2. לחץ "Get Started"
3. בחר "Continue with GitHub"
4. אשר את ההרשאות

### 2.2 יצירת פרויקט חדש
1. בדף הבית של Railway, לחץ "New Project"
2. בחר "Deploy from GitHub repo"
3. חפש את הריפוזיטורי `telegram-monitor` שלך
4. לחץ עליו

### 2.3 הגדרת משתני סביבה
1. אחרי שהפרויקט נוצר, לחץ על "Variables" בתפריט הצד
2. לחץ "New Variable"
3. הוסף את המשתנים הבאים אחד אחד:

```
API_ID = 29517731
API_HASH = 1ea4799dac3759058d07f2508979ecb2
PHONE = +972508585661
WEBHOOK_URL = https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06
```

### 2.4 הגדרת Build
1. לחץ על "Settings" בתפריט הצד
2. תחת "Build & Deploy":
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 stable_monitor.py`

---

## 🔧 שלב 3: הפעלת האפליקציה

### 3.1 בדיקת הלוגים
1. לחץ על "Deployments" בתפריט הצד
2. לחץ על ה-deployment האחרון
3. לחץ על "View Logs"

### 3.2 אימות ראשוני
בפעם הראשונה שהאפליקציה תרוץ, תצטרך להזין קוד אימות:
1. שלח הודעה לטלגרם שלך עם הקוד
2. היכנס ללוגים ב-Railway
3. הזין את הקוד כשהאפליקציה מבקשת

---

## 📊 שלב 4: מעקב וניטור

### 4.1 בדיקת סטטוס
- **Dashboard**: רואה את הסטטוס הכללי
- **Deployments**: רואה את כל ההפעלות
- **Variables**: מנהל משתני סביבה
- **Logs**: רואה לוגים בזמן אמת

### 4.2 לוגים חשובים לבדוק:
```
✅ התחברות הצליחה!
📋 קבוצות במעקב:
🎧 מאזין יציב הותקן
⚡ הסקריפט עובד!
```

---

## ⚠️ פתרון בעיות נפוצות

### בעיה: "Build failed"
**פתרון:**
1. בדוק שה-requirements.txt קיים
2. בדוק שהקבצים הועלו ל-GitHub
3. בדוק את הלוגים של ה-build

### בעיה: "Connection timeout"
**פתרון:**
1. בדוק שמשתני הסביבה נכונים
2. נסה להפעיל מחדש
3. בדוק את הלוגים

### בעיה: "Session file not found"
**פתרון:**
1. זה נורמלי בפעם הראשונה
2. הזן את קוד האימות
3. קובץ ה-session יישמר אוטומטית

---

## 🔄 שלב 5: עדכונים עתידיים

### עדכון הקוד:
```bash
# עדכן את הקוד המקומי
# הוסף שינויים
git add .
git commit -m "Update description"
git push origin main

# Railway יעדכן אוטומטית!
```

### בדיקת עדכונים:
1. היכנס ל-Railway
2. בדוק את ה-Deployments
3. וודא שהאפליקציה עובדת

---

## 📱 בדיקת שהכול עובד

### 1. בדיקת לוגים:
- היכנס ל-Logs ב-Railway
- חפש: "✅ הסקריפט עובד!"

### 2. בדיקת וובהוק:
- שלח הודעה בקבוצה
- בדוק שההודעה הגיעה לוובהוק

### 3. בדיקת יציבות:
- האפליקציה צריכה לרוץ ברציפות
- לוגים צריכים להופיע כל כמה דקות

---

## 💡 טיפים חשובים:

1. **שמור על הלוגים פתוחים** - כך תוכל לראות מה קורה
2. **בדוק את ה-Dashboard** - וודא שהאפליקציה פעילה
3. **שמור את הקישור ל-Railway** - לנוחות עתידית
4. **בדוק את ה-Usage** - וודא שלא חורגים מהמגבלות החינמיות

---

## 🎉 סיכום:

אחרי שתסיים את כל השלבים:
- ✅ התוכנה תרוץ 24/7 על Railway
- ✅ כל הודעה תישלח לוובהוק
- ✅ תוכל לראות לוגים בזמן אמת
- ✅ הכל חינמי לחלוטין!

**התוכנה שלך תעבוד ברציפות ותעקוב אחרי כל ההודעות!** 🚀 