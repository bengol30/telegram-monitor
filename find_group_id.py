#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from telethon import TelegramClient

async def find_group_id():
    """מציאת ה-ID של קבוצה ספציפית"""
    api_id = "29517731"
    api_hash = "1ea4799dac3759058d07f2508979ecb2"
    phone = "+972508585661"
    
    client = TelegramClient('session_name', api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        print("✅ התחברתי לטלגרם")
        
        # חיפוש הקבוצה לפי שם
        target_group_name = "קבוצה לבדיקה"
        
        print(f"\n🔍 מחפש קבוצה: {target_group_name}")
        print("-" * 50)
        
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                if target_group_name.lower() in dialog.title.lower():
                    print(f"📱 נמצאה קבוצה:")
                    print(f"   שם: {dialog.title}")
                    print(f"   ID: {dialog.id}")
                    print(f"   סוג: {'קבוצה' if dialog.is_group else 'ערוץ'}")
                    print(f"   פרטי: {'כן' if dialog.entity.username else 'לא'}")
                    print()
                    
                    # ניסיון לקבל מידע נוסף
                    try:
                        entity = await client.get_entity(dialog.id)
                        if hasattr(entity, 'participants_count'):
                            print(f"   👥 מספר חברים: {entity.participants_count}")
                    except:
                        print("   ❓ לא ניתן לקבל מידע נוסף")
                    
                    print("-" * 50)
        
        print("\n📋 כל הקבוצות שלך:")
        print("-" * 30)
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                print(f"📱 {dialog.title} (ID: {dialog.id})")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(find_group_id()) 