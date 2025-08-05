FROM python:3.9-slim

# הגדרת תיקיית עבודה
WORKDIR /app

# העתקת קבצי requirements
COPY requirements.txt .

# התקנת תלויות
RUN pip install --no-cache-dir -r requirements.txt

# העתקת קבצי הפרויקט
COPY . .

# הגדרת משתני סביבה
ENV PYTHONUNBUFFERED=1

# הרצת הסקריפט
CMD ["python3", "stable_monitor.py"] 