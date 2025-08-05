#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from telethon import TelegramClient, events
import aiohttp
from datetime import datetime

class PublicGroupTester:
    def __init__(self):
        self.api_id = "29517731"
        self.api_hash = "1ea4799dac3759058d07f2508979ecb2"
        self.phone = "+972508585661"
        self.webhook_url = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        
    async def start(self):
        """בדיקת קבוצות ציבוריות"""
        try:
            await self.client.start(phone=self.phone)
            print("✅ התחברתי לטלגרם")
            
            # בדיקת קבוצות שאתה חבר בהן
            print("\n📋 קבוצות שאתה חבר בהן:")
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    print(f"   📱 {dialog.title} (ID: {dialog.id})")
                    print(f"      🔗 {dialog.entity.username if hasattr(dialog.entity, 'username') else 'Private'}")
                    print(f"      👥 {dialog.entity.participants_count if hasattr(dialog.entity, 'participants_count') else 'Unknown'} חברים")
                    print()
            
            # הגדרת מאזין רק לקבוצות ציבוריות
            @self.client.on(events.NewMessage(chats=lambda e: e.is_group or e.is_channel))
            async def handle_message(event):
                await self.process_message(event)
            
            print("🎧 מאזין לקבוצות ציבוריות הותקן")
            print("📱 שלח הודעה בקבוצה ציבורית כדי לבדוק")
            
            await self.client.run_until_disconnected()
            
        except Exception as e:
            print(f"❌ שגיאה: {e}")
    
    async def process_message(self, event):
        """עיבוד הודעה"""
        try:
            message = event.message
            chat = await event.get_chat()
            sender = await event.get_sender()
            
            print(f"\n📨 הודעה חדשה:")
            print(f"   👥 קבוצה: {chat.title}")
            print(f"   👤 שולח: {sender.first_name if sender else 'Unknown'}")
            print(f"   💬 תוכן: {message.text[:100] if message.text else 'No text'}")
            
            # שליחה לוובהוק
            webhook_data = {
                "message_id": message.id,
                "group_id": str(chat.id),
                "group_name": chat.title,
                "sender_id": sender.id if sender else 0,
                "sender_name": sender.first_name if sender else "Unknown",
                "message_text": message.text or "",
                "timestamp": datetime.now().isoformat(),
                "test": True
            }
            
            success = await self.send_to_webhook(webhook_data)
            if success:
                print("✅ נשלח לוובהוק!")
            else:
                print("❌ שגיאה בשליחת וובהוק")
                
        except Exception as e:
            print(f"❌ שגיאה בעיבוד: {e}")
    
    async def send_to_webhook(self, data):
        """שליחת וובהוק"""
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
            print(f"❌ שגיאה בשליחת וובהוק: {e}")
            return False

async def main():
    tester = PublicGroupTester()
    await tester.start()

if __name__ == "__main__":
    print("🧪 בדיקת קבוצות ציבוריות")
    print("=" * 40)
    asyncio.run(main()) 