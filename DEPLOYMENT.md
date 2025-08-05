# 🚀 הוראות פריסה על ענן

## אפשרויות פריסה:

### 1. Heroku (מומלץ למתחילים)

#### שלב 1: התקנת Heroku CLI
```bash
# macOS
brew install heroku/brew/heroku

# או הורדה מהאתר הרשמי
```

#### שלב 2: יצירת אפליקציה
```bash
# התחברות
heroku login

# יצירת אפליקציה חדשה
heroku create telegram-monitor-yourname

# הגדרת משתני סביבה
heroku config:set API_ID="29517731"
heroku config:set API_HASH="1ea4799dac3759058d07f2508979ecb2"
heroku config:set PHONE="+972508585661"
heroku config:set WEBHOOK_URL="https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"

# העלאה לשרת
git add .
git commit -m "Initial deployment"
git push heroku main

# הפעלת worker
heroku ps:scale worker=1
```

### 2. Railway

#### שלב 1: התחברות
- היכנס ל-railway.app
- התחבר עם GitHub

#### שלב 2: יצירת פרויקט
- לחץ "New Project"
- בחר "Deploy from GitHub repo"
- בחר את הריפוזיטורי שלך

#### שלב 3: הגדרת משתנים
- היכנס ל-Variables
- הוסף את המשתנים הבאים:
  - `API_ID`: 29517731
  - `API_HASH`: 1ea4799dac3759058d07f2508979ecb2
  - `PHONE`: +972508585661
  - `WEBHOOK_URL`: https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06

### 3. DigitalOcean App Platform

#### שלב 1: יצירת אפליקציה
- היכנס ל-DigitalOcean
- בחר "App Platform"
- לחץ "Create App"

#### שלב 2: הגדרת מקור
- בחר GitHub
- בחר את הריפוזיטורי שלך

#### שלב 3: הגדרת build
- Build Command: `pip install -r requirements.txt`
- Run Command: `python3 stable_monitor.py`

#### שלב 4: הגדרת משתנים
- הוסף את המשתנים הסביבתיים

## ⚠️ חשוב לדעת:

1. **אימות ראשוני**: בפעם הראשונה שהאפליקציה תרוץ, תצטרך להזין קוד אימות
2. **Session Files**: קובץ ה-session יישמר על השרת
3. **Logs**: תוכל לראות לוגים דרך ממשק הניהול של הפלטפורמה
4. **Costs**: 
   - Heroku: חינמי לחודש ראשון, אחר כך $7/חודש
   - Railway: חינמי לחודש ראשון, אחר כך $5/חודש
   - DigitalOcean: $5/חודש

## 🔧 פתרון בעיות:

### בעיה: "database is locked"
```bash
# מחק קבצי session ישנים
rm *.session*
```

### בעיה: "connection timeout"
- בדוק שהאינטרנט יציב
- נסה שוב אחרי כמה דקות

### בעיה: "API flood wait"
- הסקריפט יחכה אוטומטית
- אל תפעיל כמה עותקים במקביל

## 📊 מעקב אחרי ביצועים:

- **Heroku**: `heroku logs --tail`
- **Railway**: ממשק הלוגים באתר
- **DigitalOcean**: ממשק הלוגים באתר 