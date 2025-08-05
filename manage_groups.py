#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sqlite3
from telegram_monitor import TelegramMonitor

class GroupManager:
    def __init__(self, api_id: str, api_hash: str, phone: str, webhook_url: str):
        self.monitor = TelegramMonitor(api_id, api_hash, phone, webhook_url)
    
    async def start_client(self):
        """התחלת החיבור לטלגרם"""
        await self.monitor.client.start(phone=self.monitor.phone)
        print("✅ התחברתי לטלגרם בהצלחה")
    
    async def add_group(self, group_link: str, group_name: str):
        """הוספת קבוצה חדשה"""
        try:
            success = await self.monitor.add_group(group_link, group_name)
            if success:
                print(f"✅ נוספה קבוצה: {group_name}")
            else:
                print(f"❌ שגיאה בהוספת קבוצה: {group_name}")
        except Exception as e:
            print(f"❌ שגיאה: {e}")
    
    async def remove_group(self, group_link: str):
        """הסרת קבוצה"""
        try:
            success = await self.monitor.remove_group(group_link)
            if success:
                print(f"✅ הוסרה קבוצה: {group_link}")
            else:
                print(f"❌ שגיאה בהסרת קבוצה: {group_link}")
        except Exception as e:
            print(f"❌ שגיאה: {e}")
    
    async def list_groups(self):
        """הצגת רשימת קבוצות"""
        conn = sqlite3.connect(self.monitor.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT group_name, group_link, is_active, created_at 
            FROM groups 
            ORDER BY created_at DESC
        ''')
        
        groups = cursor.fetchall()
        conn.close()
        
        if not groups:
            print("📝 אין קבוצות במעקב")
            return
        
        print("\n📋 רשימת קבוצות במעקב:")
        print("-" * 80)
        
        for name, link, active, created in groups:
            status = "🟢 פעיל" if active else "🔴 לא פעיל"
            print(f"📱 {name}")
            print(f"   🔗 {link}")
            print(f"   📊 {status}")
            print(f"   📅 {created}")
            print("-" * 80)
    
    async def get_stats(self):
        """הצגת סטטיסטיקות"""
        stats = await self.monitor.get_stats()
        
        print("\n📊 סטטיסטיקות:")
        print("-" * 40)
        print(f"📱 קבוצות פעילות: {stats['active_groups']}")
        print(f"💬 הודעות שנשלחו: {stats['sent_messages']}")
        print(f"🕐 הודעה אחרונה: {stats['last_message'] or 'אין'}")
        print("-" * 40)
    
    async def close(self):
        """סגירת החיבור"""
        await self.monitor.client.disconnect()

async def main():
    """תפריט ניהול קבוצות"""
    # הגדרות - יש להחליף עם הפרטים שלך
    API_ID = "29517731"
    API_HASH = "1ea4799dac3759058d07f2508979ecb2"
    PHONE = "+972508585661"
    WEBHOOK_URL = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
    
    manager = GroupManager(API_ID, API_HASH, PHONE, WEBHOOK_URL)
    
    try:
        await manager.start_client()
        
        while True:
            print("\n🤖 מנהל קבוצות טלגרם")
            print("=" * 40)
            print("1. 📋 הצג קבוצות")
            print("2. ➕ הוסף קבוצה")
            print("3. ➖ הסר קבוצה")
            print("4. 📊 הצג סטטיסטיקות")
            print("5. 🚪 יציאה")
            
            choice = input("\nבחר אפשרות (1-5): ").strip()
            
            if choice == "1":
                await manager.list_groups()
                
            elif choice == "2":
                name = input("שם הקבוצה: ").strip()
                link = input("קישור לקבוצה: ").strip()
                
                if name and link:
                    await manager.add_group(link, name)
                else:
                    print("❌ אנא מלא את כל השדות")
                    
            elif choice == "3":
                link = input("קישור לקבוצה להסרה: ").strip()
                
                if link:
                    confirm = input("האם אתה בטוח? (y/n): ").strip().lower()
                    if confirm == 'y':
                        await manager.remove_group(link)
                else:
                    print("❌ אנא הכנס קישור")
                    
            elif choice == "4":
                await manager.get_stats()
                
            elif choice == "5":
                print("👋 להתראות!")
                break
                
            else:
                print("❌ בחירה לא תקינה")
                
    except KeyboardInterrupt:
        print("\n👋 להתראות!")
    except Exception as e:
        print(f"❌ שגיאה: {e}")
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main()) 