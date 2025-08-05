#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
from datetime import datetime

async def test_webhook():
    """בדיקת הוובהוק"""
    webhook_url = "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06"
    
    test_data = {
        "test": True,
        "message": "בדיקת וובהוק",
        "timestamp": datetime.now().isoformat(),
        "source": "Telegram Monitor Test"
    }
    
    print("🧪 בודק וובהוק...")
    print(f"📤 שולח: {test_data}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                print(f"📥 תגובה: {response.status}")
                
                if response.status == 200:
                    print("✅ וובהוק עובד!")
                    response_text = await response.text()
                    print(f"📄 תוכן התגובה: {response_text}")
                else:
                    print("❌ וובהוק לא עובד")
                    
    except Exception as e:
        print(f"❌ שגיאה: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook()) 