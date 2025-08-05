#!/bin/bash

echo "🚀 מתחיל הגדרת GitHub..."
echo ""

# בדיקה אם Git מותקן
if ! command -v git &> /dev/null; then
    echo "❌ Git לא מותקן. מתקין..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install git
    else
        echo "⚠️ אנא התקן Git מהאתר הרשמי: https://git-scm.com/"
        exit 1
    fi
fi

echo "✅ Git מותקן"

# אתחול Git
if [ ! -d ".git" ]; then
    echo "📁 מאתחל Git repository..."
    git init
fi

# הוספת קבצים
echo "📦 מוסיף קבצים..."
git add .

# יצירת commit
echo "💾 יוצר commit..."
git commit -m "Initial commit - Telegram Monitor"

echo ""
echo "🎯 עכשיו צריך להגדיר את ה-remote:"
echo ""
echo "1. היכנס ל-github.com"
echo "2. צור repository חדש בשם: telegram-monitor"
echo "3. העתק את הפקודה הבאה (החלף YOUR_USERNAME בשם המשתמש שלך):"
echo ""
echo "git remote add origin https://github.com/YOUR_USERNAME/telegram-monitor.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "4. אחרי שתעשה את זה, הרץ:"
echo "   ./deploy_to_railway.sh"
echo ""

echo "✅ הגדרת GitHub הושלמה!" 