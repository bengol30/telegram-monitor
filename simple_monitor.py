#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
from datetime import datetime
from telethon import TelegramClient, events
import aiohttp
import sqlite3

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleTelegramMonitor:
    def __init__(self):
        # פרטי התחברות
        self.api_id = "29517731"
        self.api_hash = "1ea4799dac3759058d07f2508979ecb2"
        self.phone = "+972508585661"
        self.webhook_url = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
        
        # יצירת לקוח
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        
        # קבוצות למעקב
        self.monitored_groups = []
        
    async def start(self):
        """התחלת החיבור והמעקב"""
        try:
            logger.info("מתחבר לטלגרם...")
            
            # התחברות
            await self.client.start(phone=self.phone)
            logger.info("✅ התחברתי לטלגרם בהצלחה!")
            
            # הגדרת מאזין להודעות
            @self.client.on(events.NewMessage())
            async def handle_new_message(event):
                await self.process_message(event)
            
            logger.info("🎧 מאזין להודעות הותקן")
            logger.info("📱 הסקריפט עובד! שלח הודעה בקבוצה כדי לבדוק")
            
            # הפעלת הסקריפט
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"❌ שגיאה: {e}")
    
    async def process_message(self, event):
        """עיבוד הודעה חדשה"""
        try:
            # קבלת פרטי ההודעה
            message = event.message
            chat = await event.get_chat()
            sender = await event.get_sender()
            
            # הדפסת פרטי ההודעה
            logger.info(f"📨 הודעה חדשה:")
            logger.info(f"   👥 קבוצה: {chat.title if hasattr(chat, 'title') else 'Unknown'}")
            logger.info(f"   👤 שולח: {sender.first_name if sender else 'Unknown'}")
            logger.info(f"   💬 תוכן: {message.text[:50] if message.text else 'No text'}...")
            
            # הכנת נתונים לוובהוק
            webhook_data = {
                "message_id": message.id,
                "group_id": str(chat.id),
                "group_name": chat.title if hasattr(chat, 'title') else 'Unknown',
                "sender_id": sender.id if sender else 0,
                "sender_name": sender.first_name if sender else "Unknown",
                "sender_username": sender.username if sender else None,
                "message_text": message.text or "",
                "timestamp": datetime.now().isoformat(),
                "message_type": "text",
                "has_media": message.media is not None
            }
            
            # שליחה לוובהוק
            success = await self.send_to_webhook(webhook_data)
            
            if success:
                logger.info("✅ נשלח לוובהוק בהצלחה!")
            else:
                logger.error("❌ שגיאה בשליחת וובהוק")
                
        except Exception as e:
            logger.error(f"❌ שגיאה בעיבוד הודעה: {e}")
    
    async def send_to_webhook(self, data):
        """שליחת נתונים לוובהוק"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"❌ שגיאה בשליחת וובהוק: {e}")
            return False

async def main():
    """פונקציה ראשית"""
    monitor = SimpleTelegramMonitor()
    await monitor.start()

if __name__ == "__main__":
    print("🚀 מתחיל מעקב הודעות טלגרם...")
    print("📱 הסקריפט יעקוב אחרי כל ההודעות שאתה מקבל")
    print("🔗 כל הודעה תישלח לוובהוק")
    print("⏹️  לחץ Ctrl+C כדי לעצור")
    print("-" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 הסקריפט נעצר")
    except Exception as e:
        print(f"❌ שגיאה: {e}") 