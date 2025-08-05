#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError
import aiohttp
import signal
import sys

# הגדרת לוגים מפורטים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FastTelegramMonitor:
    def __init__(self):
        # פרטי התחברות
        self.api_id = "29517731"
        self.api_hash = "1ea4799dac3759058d07f2508979ecb2"
        self.phone = "+972508585661"
        self.webhook_url = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
        
        # יצירת לקוח עם הגדרות מותאמות
        self.client = TelegramClient(
            'session_name', 
            self.api_id, 
            self.api_hash,
            connection_retries=10,
            retry_delay=1,
            timeout=30,
            auto_reconnect=True
        )
        
        # רשימת קבוצות למעקב
        self.target_groups = [
            -1002633249593,  # Forex.Daddy SILVER
            -1001397114707,  # ynet חדשות
            -1001436772127,  # צופר - צבע אדום
            -4911850781,     # קבוצה לבדיקה
        ]
        
        # סטטיסטיקות
        self.message_count = 0
        self.last_message_time = None
        self.is_running = True
        
        # הגדרת סיגנל לעצירה מסודרת
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """טיפול בסיגנל עצירה"""
        logger.info("📴 מקבל סיגנל עצירה...")
        self.is_running = False
        
    async def start(self):
        """התחלת החיבור והמעקב"""
        try:
            logger.info("🚀 מתחיל מעקב מהיר...")
            
            # התחברות עם ניסיונות חוזרים
            await self.connect_with_retry()
            
            # הדפסת מידע על הקבוצות
            await self.print_group_info()
            
            # הגדרת מאזין להודעות
            self.setup_message_handler()
            
            logger.info("🎧 מאזין מהיר הותקן")
            logger.info("⚡ הסקריפט עובד במהירות גבוהה!")
            logger.info("📱 שלח הודעה בקבוצה כדי לבדוק")
            
            # לולאה ראשית עם בדיקות תקופתיות
            while self.is_running:
                try:
                    # בדיקה שהחיבור פעיל
                    if not self.client.is_connected():
                        logger.warning("⚠️ החיבור נותק, מתחבר מחדש...")
                        await self.connect_with_retry()
                    
                    # המתנה קצרה
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ שגיאה בלולאה הראשית: {e}")
                    await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"❌ שגיאה קריטית: {e}")
        finally:
            await self.cleanup()
    
    async def connect_with_retry(self):
        """התחברות עם ניסיונות חוזרים"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                logger.info(f"📱 מתחבר לטלגרם... (ניסיון {attempt + 1}/{max_retries})")
                await self.client.start(phone=self.phone)
                logger.info("✅ התחברות הצליחה!")
                return
            except FloodWaitError as e:
                wait_time = e.seconds
                logger.warning(f"⏳ צריך לחכות {wait_time} שניות...")
                await asyncio.sleep(wait_time)
            except SessionPasswordNeededError:
                logger.error("🔐 נדרשת סיסמה דו-שלבית")
                raise
            except Exception as e:
                logger.error(f"❌ שגיאה בהתחברות: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                else:
                    raise
    
    async def print_group_info(self):
        """הדפסת מידע על הקבוצות"""
        logger.info("📋 קבוצות במעקב:")
        for group_id in self.target_groups:
            try:
                entity = await self.client.get_entity(group_id)
                logger.info(f"   📱 {entity.title} (ID: {group_id})")
            except Exception as e:
                logger.warning(f"   ❓ לא ניתן לגשת לקבוצה {group_id}: {e}")
    
    def setup_message_handler(self):
        """הגדרת מאזין להודעות"""
        @self.client.on(events.NewMessage(chats=self.target_groups))
        async def handle_new_message(event):
            # עיבוד מהיר של ההודעה
            asyncio.create_task(self.process_message_fast(event))
    
    async def process_message_fast(self, event):
        """עיבוד מהיר של הודעה"""
        start_time = time.time()
        
        try:
            # קבלת פרטי ההודעה
            message = event.message
            chat = await event.get_chat()
            sender = await event.get_sender()
            
            # עדכון סטטיסטיקות
            self.message_count += 1
            self.last_message_time = datetime.now()
            
            # הדפסת פרטי ההודעה
            logger.info(f"📨 הודעה #{self.message_count}:")
            logger.info(f"   👥 קבוצה: {chat.title}")
            logger.info(f"   👤 שולח: {sender.first_name if sender else 'Unknown'}")
            logger.info(f"   💬 תוכן: {message.text[:50] if message.text else 'No text'}...")
            
            # הכנת נתונים לוובהוק
            webhook_data = {
                "message_id": message.id,
                "group_id": str(chat.id),
                "group_name": chat.title,
                "sender_id": sender.id if sender else 0,
                "sender_name": sender.first_name if sender else "Unknown",
                "sender_username": sender.username if sender else None,
                "message_text": message.text or "",
                "timestamp": datetime.now().isoformat(),
                "message_type": "text",
                "has_media": message.media is not None,
                "group_type": "private" if chat.id < 0 else "public",
                "processing_time": time.time() - start_time
            }
            
            # שליחה מהירה לוובהוק
            success = await self.send_to_webhook_fast(webhook_data)
            
            processing_time = time.time() - start_time
            if success:
                logger.info(f"✅ נשלח לוובהוק! (זמן עיבוד: {processing_time:.2f} שניות)")
            else:
                logger.error(f"❌ שגיאה בשליחת וובהוק (זמן עיבוד: {processing_time:.2f} שניות)")
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ שגיאה בעיבוד הודעה (זמן עיבוד: {processing_time:.2f} שניות): {e}")
    
    async def send_to_webhook_fast(self, data):
        """שליחה מהירה לוובהוק"""
        try:
            timeout = aiohttp.ClientTimeout(total=5)  # timeout קצר יותר
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.webhook_url,
                    json=data,
                    headers={'Content-Type': 'application/json'},
                ) as response:
                    return response.status == 200
        except asyncio.TimeoutError:
            logger.error("⏰ timeout בשליחת וובהוק")
            return False
        except Exception as e:
            logger.error(f"❌ שגיאה בשליחת וובהוק: {e}")
            return False
    
    async def cleanup(self):
        """ניקוי לפני יציאה"""
        logger.info("🧹 מנקה ומתנתק...")
        if self.client.is_connected():
            await self.client.disconnect()
        logger.info("👋 הסקריפט נעצר")

async def main():
    """פונקציה ראשית"""
    monitor = FastTelegramMonitor()
    await monitor.start()

if __name__ == "__main__":
    print("⚡ מתחיל מעקב מהיר אחרי הודעות טלגרם...")
    print("🚀 הסקריפט יעבוד במהירות גבוהה ויציבות")
    print("🔗 כל הודעה תישלח לוובהוק מיד")
    print("⏹️  לחץ Ctrl+C כדי לעצור")
    print("-" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 הסקריפט נעצר")
    except Exception as e:
        print(f"❌ שגיאה: {e}") 