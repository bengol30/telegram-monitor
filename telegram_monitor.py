#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import os
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat
import aiohttp
import sqlite3
from typing import Dict, List, Optional

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramMonitor:
    def __init__(self, api_id: str, api_hash: str, phone: str, webhook_url: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.webhook_url = webhook_url
        self.client = TelegramClient('session_name', api_id, api_hash)
        self.monitored_groups = {}
        self.db_path = 'telegram_monitor.db'
        self.init_database()
        
    def init_database(self):
        """יצירת מסד נתונים SQLite לשמירת קבוצות והודעות"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טבלת קבוצות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY,
                group_id TEXT UNIQUE,
                group_name TEXT,
                group_link TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת הודעות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                message_id INTEGER,
                group_id TEXT,
                sender_id INTEGER,
                sender_name TEXT,
                message_text TEXT,
                timestamp TIMESTAMP,
                sent_to_webhook BOOLEAN DEFAULT 0,
                webhook_response TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("מסד נתונים אותחל בהצלחה")
    
    async def start(self):
        """התחלת החיבור לטלגרם"""
        try:
            await self.client.start(phone=self.phone)
            logger.info("התחברתי לטלגרם בהצלחה")
            
            # טעינת קבוצות ממסד הנתונים
            await self.load_monitored_groups()
            
            # הגדרת מאזין להודעות
            @self.client.on(events.NewMessage(chats=list(self.monitored_groups.keys())))
            async def handle_new_message(event):
                await self.process_message(event)
            
            logger.info("מאזין להודעות הותקן")
            
            # הפעלת הסקריפט
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"שגיאה בהתחברות: {e}")
    
    async def load_monitored_groups(self):
        """טעינת קבוצות ממסד הנתונים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT group_id, group_name, group_link FROM groups WHERE is_active = 1')
        groups = cursor.fetchall()
        
        for group_id, group_name, group_link in groups:
            try:
                # ניסיון לקבל את ה-entity של הקבוצה
                entity = await self.client.get_entity(group_link)
                self.monitored_groups[entity.id] = {
                    'name': group_name,
                    'link': group_link,
                    'entity': entity
                }
                logger.info(f"טעינתי קבוצה: {group_name} (ID: {entity.id})")
            except Exception as e:
                logger.error(f"שגיאה בטעינת קבוצה {group_name}: {e}")
        
        conn.close()
        logger.info(f"טעינתי {len(self.monitored_groups)} קבוצות")
    
    async def add_group(self, group_link: str, group_name: str) -> bool:
        """הוספת קבוצה חדשה למעקב"""
        try:
            # קבלת ה-entity של הקבוצה
            entity = await self.client.get_entity(group_link)
            
            # שמירה למסד הנתונים
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO groups (group_id, group_name, group_link, is_active)
                VALUES (?, ?, ?, 1)
            ''', (str(entity.id), group_name, group_link))
            
            conn.commit()
            conn.close()
            
            # הוספה לזיכרון
            self.monitored_groups[entity.id] = {
                'name': group_name,
                'link': group_link,
                'entity': entity
            }
            
            logger.info(f"נוספה קבוצה: {group_name} (ID: {entity.id})")
            return True
            
        except Exception as e:
            logger.error(f"שגיאה בהוספת קבוצה {group_name}: {e}")
            return False
    
    async def remove_group(self, group_link: str) -> bool:
        """הסרת קבוצה מהמעקב"""
        try:
            entity = await self.client.get_entity(group_link)
            
            # הסרה ממסד הנתונים
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE groups SET is_active = 0 WHERE group_id = ?', (str(entity.id),))
            conn.commit()
            conn.close()
            
            # הסרה מהזיכרון
            if entity.id in self.monitored_groups:
                del self.monitored_groups[entity.id]
            
            logger.info(f"הוסרה קבוצה: {entity.id}")
            return True
            
        except Exception as e:
            logger.error(f"שגיאה בהסרת קבוצה: {e}")
            return False
    
    async def process_message(self, event):
        """עיבוד הודעה חדשה"""
        try:
            # קבלת פרטי ההודעה
            message = event.message
            chat = await event.get_chat()
            
            # בדיקה אם הקבוצה במעקב
            if chat.id not in self.monitored_groups:
                return
            
            group_info = self.monitored_groups[chat.id]
            sender = await event.get_sender()
            
            # שמירת ההודעה למסד הנתונים
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (message_id, group_id, sender_id, sender_name, message_text, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                message.id,
                str(chat.id),
                sender.id if sender else 0,
                sender.first_name if sender else "Unknown",
                message.text or "",
                datetime.now().isoformat()
            ))
            
            message_db_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # הכנת נתונים לוובהוק
            webhook_data = {
                "message_id": message.id,
                "group_id": str(chat.id),
                "group_name": group_info['name'],
                "group_link": group_info['link'],
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
            
            # עדכון סטטוס השליחה
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE messages 
                SET sent_to_webhook = ?, webhook_response = ?
                WHERE id = ?
            ''', (success, "OK" if success else "Failed", message_db_id))
            
            conn.commit()
            conn.close()
            
            if success:
                logger.info(f"נשלחה הודעה לוובהוק: {group_info['name']} - {sender.first_name if sender else 'Unknown'}")
            else:
                logger.error(f"שגיאה בשליחת הודעה לוובהוק: {group_info['name']}")
                
        except Exception as e:
            logger.error(f"שגיאה בעיבוד הודעה: {e}")
    
    async def send_to_webhook(self, data: Dict) -> bool:
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
            logger.error(f"שגיאה בשליחת וובהוק: {e}")
            return False
    
    async def get_stats(self) -> Dict:
        """קבלת סטטיסטיקות"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # מספר קבוצות פעילות
        cursor.execute('SELECT COUNT(*) FROM groups WHERE is_active = 1')
        active_groups = cursor.fetchone()[0]
        
        # מספר הודעות שנשלחו
        cursor.execute('SELECT COUNT(*) FROM messages WHERE sent_to_webhook = 1')
        sent_messages = cursor.fetchone()[0]
        
        # הודעה אחרונה
        cursor.execute('''
            SELECT timestamp FROM messages 
            WHERE sent_to_webhook = 1 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        last_message = cursor.fetchone()
        last_message_time = last_message[0] if last_message else None
        
        conn.close()
        
        return {
            "active_groups": active_groups,
            "sent_messages": sent_messages,
            "last_message": last_message_time
        }

async def main():
    """פונקציה ראשית"""
    # הגדרות - יש להחליף עם הפרטים שלך
    API_ID = "29517731"  # קבל מ: https://my.telegram.org
    API_HASH = "1ea4799dac3759058d07f2508979ecb2"  # קבל מ: https://my.telegram.org
    PHONE = "+972508585661"  # מספר הטלפון שלך עם קוד מדינה (לדוגמה: +972501234567)
    WEBHOOK_URL = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
    
    # יצירת מוניטור
    monitor = TelegramMonitor(API_ID, API_HASH, PHONE, WEBHOOK_URL)
    
    # הפעלת המוניטור
    await monitor.start()

if __name__ == "__main__":
    asyncio.run(main()) 