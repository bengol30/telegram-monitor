#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from telethon import TelegramClient

async def setup_auth():
    """הגדרת אימות פעם אחת"""
    print("🔐 הגדרת אימות טלגרם")
    print("=" * 40)
    
    # פרטי התחברות
    api_id = "29517731"
    api_hash = "1ea4799dac3759058d07f2508979ecb2"
    phone = "+972508585661"
    
    # יצירת לקוח
    client = TelegramClient('session_name', api_id, api_hash)
    
    try:
        print("📱 מתחבר לטלגרם...")
        
        # התחברות עם אימות
        await client.start(phone=phone)
        
        print("✅ התחברות הצליחה!")
        print("💾 פרטי התחברות נשמרו")
        
        # בדיקה שהחיבור עובד
        me = await client.get_me()
        print(f"👤 מחובר כ: {me.first_name} (@{me.username})")
        
        print("\n🎉 הכל מוכן! עכשיו אפשר להפעיל את הסקריפט הראשי")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(setup_auth()) 