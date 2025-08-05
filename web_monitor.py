#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import time
import os
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError
import aiohttp
from aiohttp import web
import signal
import sys
import threading

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebTelegramMonitor:
    def __init__(self):
        # פרטי התחברות - מקבלים ממשתני סביבה
        self.api_id = os.getenv("API_ID", "29517731")
        self.api_hash = os.getenv("API_HASH", "1ea4799dac3759058d07f2508979ecb2")
        self.phone = os.getenv("PHONE", "+972508585661")
        self.webhook_url = os.getenv("WEBHOOK_URL", "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06")
        
        # שם קובץ session קבוע
        self.session_name = 'telegram_web_session'
        
        # יצירת לקוח
        self.client = TelegramClient(
            self.session_name, 
            self.api_id, 
            self.api_hash,
            connection_retries=10,
            retry_delay=3,
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
        self.is_connected = False
        self.auth_status = "not_started"  # not_started, waiting_code, connected, error
        
        # משתנים לאימות
        self.pending_auth = False
        self.auth_code = None
        
        # הגדרת סיגנל לעצירה מסודרת
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """טיפול בסיגנל עצירה"""
        logger.info("📴 מקבל סיגנל עצירה...")
        self.is_running = False
        
    async def start_web_server(self):
        """הפעלת שרת web"""
        app = web.Application()
        
        # הגדרת routes
        app.router.add_get('/', self.home_page)
        app.router.add_post('/auth', self.handle_auth)
        app.router.add_get('/status', self.get_status)
        app.router.add_get('/logs', self.get_logs)
        app.router.add_post('/restart', self.restart_monitor)
        
        # הפעלת שרת
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
        await site.start()
        
        logger.info(f"🌐 שרת web פועל על פורט {os.getenv('PORT', 8080)}")
        return runner
        
    async def home_page(self, request):
        """דף הבית"""
        html = """
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>טלגרם מוניטור - ניהול התחברות</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                    color: #333;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }
                .header h1 {
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }
                .content {
                    padding: 30px;
                }
                .status-card {
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-left: 5px solid #007bff;
                }
                .auth-form {
                    background: #e3f2fd;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-left: 5px solid #2196f3;
                }
                .form-group {
                    margin-bottom: 15px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #555;
                }
                input[type="text"] {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    font-size: 16px;
                    box-sizing: border-box;
                }
                input[type="text"]:focus {
                    border-color: #667eea;
                    outline: none;
                }
                .btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 30px;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                .btn:hover {
                    transform: translateY(-2px);
                }
                .btn:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                    transform: none;
                }
                .logs {
                    background: #1e1e1e;
                    color: #00ff00;
                    padding: 20px;
                    border-radius: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    max-height: 300px;
                    overflow-y: auto;
                    white-space: pre-wrap;
                }
                .status-indicator {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                .status-connected { background: #28a745; }
                .status-waiting { background: #ffc107; }
                .status-error { background: #dc3545; }
                .status-disconnected { background: #6c757d; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📱 טלגרם מוניטור</h1>
                    <p>ניהול התחברות ומעקב אחרי הודעות</p>
                </div>
                
                <div class="content">
                    <div class="status-card">
                        <h3>📊 סטטוס המערכת</h3>
                        <div id="status">
                            <span class="status-indicator status-disconnected"></span>
                            <span id="status-text">טוען...</span>
                        </div>
                        <p>📱 טלפון: """ + self.phone + """</p>
                        <p>📨 הודעות שנשלחו: <span id="message-count">0</span></p>
                        <p>🕒 הודעה אחרונה: <span id="last-message">אין</span></p>
                    </div>
                    
                    <div class="auth-form" id="auth-form" style="display: none;">
                        <h3>🔐 התחברות לטלגרם</h3>
                        <p>שלח הודעה לטלגרם עם קוד אימות וזן אותו כאן:</p>
                        <form id="auth-code-form">
                            <div class="form-group">
                                <label for="auth-code">קוד אימות:</label>
                                <input type="text" id="auth-code" name="auth_code" placeholder="הזן את הקוד שקיבלת" required>
                            </div>
                            <button type="submit" class="btn">🔐 התחבר</button>
                        </form>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <button class="btn" onclick="restartMonitor()">🔄 הפעל מחדש</button>
                        <button class="btn" onclick="refreshStatus()">🔄 רענן סטטוס</button>
                    </div>
                    
                    <div>
                        <h3>📋 לוגים בזמן אמת</h3>
                        <div class="logs" id="logs">טוען לוגים...</div>
                    </div>
                </div>
            </div>
            
            <script>
                // רענון אוטומטי
                setInterval(refreshStatus, 5000);
                setInterval(refreshLogs, 3000);
                
                async function refreshStatus() {
                    try {
                        const response = await fetch('/status');
                        const data = await response.json();
                        
                        const statusText = document.getElementById('status-text');
                        const statusIndicator = document.querySelector('.status-indicator');
                        const authForm = document.getElementById('auth-form');
                        const messageCount = document.getElementById('message-count');
                        const lastMessage = document.getElementById('last-message');
                        
                        // עדכון סטטוס
                        statusText.textContent = data.status;
                        statusIndicator.className = 'status-indicator status-' + data.status_type;
                        
                        // הצגת/הסתרת טופס אימות
                        if (data.needs_auth) {
                            authForm.style.display = 'block';
                        } else {
                            authForm.style.display = 'none';
                        }
                        
                        // עדכון סטטיסטיקות
                        messageCount.textContent = data.message_count;
                        lastMessage.textContent = data.last_message || 'אין';
                        
                    } catch (error) {
                        console.error('שגיאה ברענון סטטוס:', error);
                    }
                }
                
                async function refreshLogs() {
                    try {
                        const response = await fetch('/logs');
                        const logs = await response.text();
                        document.getElementById('logs').textContent = logs;
                    } catch (error) {
                        console.error('שגיאה ברענון לוגים:', error);
                    }
                    }
                
                async function restartMonitor() {
                    try {
                        await fetch('/restart', { method: 'POST' });
                        alert('המערכת מופעלת מחדש...');
                        setTimeout(refreshStatus, 2000);
                    } catch (error) {
                        console.error('שגיאה בהפעלה מחדש:', error);
                    }
                }
                
                // טיפול בטופס אימות
                document.getElementById('auth-code-form').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const authCode = document.getElementById('auth-code').value;
                    if (!authCode) return;
                    
                    try {
                        const response = await fetch('/auth', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ auth_code: authCode })
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            alert('✅ התחברות הצליחה!');
                            document.getElementById('auth-code').value = '';
                            refreshStatus();
                        } else {
                            alert('❌ שגיאה בהתחברות: ' + result.error);
                        }
                    } catch (error) {
                        alert('❌ שגיאה בשליחת הקוד');
                    }
                });
                
                // טעינה ראשונית
                refreshStatus();
                refreshLogs();
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
        
    async def handle_auth(self, request):
        """טיפול בקוד אימות"""
        try:
            data = await request.json()
            auth_code = data.get('auth_code')
            
            if not auth_code:
                return web.json_response({'success': False, 'error': 'קוד אימות חסר'})
            
            logger.info(f"🔐 מקבל קוד אימות: {auth_code}")
            
            # ניסיון התחברות עם הקוד
            try:
                await self.client.start(phone=self.phone, code=auth_code)
                self.is_connected = True
                self.auth_status = "connected"
                self.pending_auth = False
                
                logger.info("✅ התחברות הצליחה!")
                
                # הפעלת המעקב
                asyncio.create_task(self.start_monitoring())
                
                return web.json_response({'success': True})
                
            except Exception as e:
                logger.error(f"❌ שגיאה בהתחברות: {e}")
                return web.json_response({'success': False, 'error': str(e)})
                
        except Exception as e:
            logger.error(f"❌ שגיאה בטיפול בקוד אימות: {e}")
            return web.json_response({'success': False, 'error': str(e)})
    
    async def get_status(self, request):
        """קבלת סטטוס המערכת"""
        status_data = {
            'status': self.get_status_text(),
            'status_type': self.get_status_type(),
            'needs_auth': self.pending_auth and not self.is_connected,
            'message_count': self.message_count,
            'last_message': self.last_message_time.isoformat() if self.last_message_time else None,
            'is_connected': self.is_connected
        }
        return web.json_response(status_data)
    
    async def get_logs(self, request):
        """קבלת לוגים"""
        # כאן אפשר להוסיף לוגים מתקדמים יותר
        logs = f"""
=== לוגים אחרונים ===
סטטוס: {self.get_status_text()}
הודעות: {self.message_count}
מחובר: {self.is_connected}
אימות נדרש: {self.pending_auth}
        """
        return web.Response(text=logs)
    
    async def restart_monitor(self, request):
        """הפעלה מחדש של המעקב"""
        try:
            logger.info("🔄 מפעיל מחדש...")
            self.is_connected = False
            self.auth_status = "not_started"
            self.pending_auth = False
            
            # ניסיון התחברות מחדש
            await self.connect_with_retry()
            
            return web.json_response({'success': True})
        except Exception as e:
            logger.error(f"❌ שגיאה בהפעלה מחדש: {e}")
            return web.json_response({'success': False, 'error': str(e)})
    
    def get_status_text(self):
        """קבלת טקסט סטטוס"""
        if self.is_connected:
            return "מחובר ועובד"
        elif self.pending_auth:
            return "ממתין לקוד אימות"
        elif self.auth_status == "error":
            return "שגיאה בהתחברות"
        else:
            return "לא מחובר"
    
    def get_status_type(self):
        """קבלת סוג סטטוס"""
        if self.is_connected:
            return "connected"
        elif self.pending_auth:
            return "waiting"
        elif self.auth_status == "error":
            return "error"
        else:
            return "disconnected"
    
    async def start(self):
        """התחלת המערכת"""
        try:
            logger.info("🚀 מתחיל מערכת web...")
            
            # הפעלת שרת web
            runner = await self.start_web_server()
            
            # ניסיון התחברות ראשוני
            await self.connect_with_retry()
            
            # המתנה לסיום
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ שגיאה קריטית: {e}")
        finally:
            await self.cleanup()
    
    async def connect_with_retry(self):
        """התחברות עם ניסיונות מרובים"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"📱 מתחבר לטלגרם... (ניסיון {attempt + 1}/{max_retries})")
                
                # בדיקה אם יש קובץ session קיים
                if os.path.exists(f"{self.session_name}.session"):
                    logger.info("📁 נמצא קובץ session קיים")
                
                await self.client.start(phone=self.phone)
                self.is_connected = True
                self.auth_status = "connected"
                self.pending_auth = False
                
                logger.info("✅ התחברות הצליחה!")
                
                # הפעלת המעקב
                asyncio.create_task(self.start_monitoring())
                return
                
            except SessionPasswordNeededError:
                logger.error("🔐 נדרשת סיסמה דו-שלבית")
                self.auth_status = "error"
                raise
            except Exception as e:
                error_msg = str(e)
                if "EOF when reading a line" in error_msg or "code" in error_msg.lower():
                    logger.warning("⚠️ נדרש אימות ראשוני")
                    self.pending_auth = True
                    self.auth_status = "waiting_code"
                    logger.info("📱 שלח הודעה לטלגרם עם קוד אימות")
                    logger.info("🌐 היכנס לממשק ה-web להזנת הקוד")
                    return
                else:
                    logger.error(f"❌ שגיאה בהתחברות: {e}")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5
                        logger.info(f"⏳ מחכה {wait_time} שניות לפני ניסיון נוסף...")
                        await asyncio.sleep(wait_time)
                    else:
                        self.auth_status = "error"
                        raise
        
        self.auth_status = "error"
        raise Exception("❌ לא הצלחתי להתחבר אחרי כל הניסיונות")
    
    async def start_monitoring(self):
        """התחלת המעקב אחרי הודעות"""
        try:
            # הדפסת מידע על הקבוצות
            await self.print_group_info()
            
            # הגדרת מאזין להודעות
            self.setup_message_handler()
            
            logger.info("🎧 מאזין web הותקן")
            logger.info("🌐 הסקריפט עובד עם ממשק web!")
            logger.info("📱 שלח הודעה בקבוצה כדי לבדוק")
            
        except Exception as e:
            logger.error(f"❌ שגיאה בהתחלת המעקב: {e}")
    
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
            asyncio.create_task(self.process_message(event))
    
    async def process_message(self, event):
        """עיבוד הודעה"""
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
            
            # טיפול בסוגים שונים של שולחים
            if hasattr(sender, 'first_name'):
                sender_name = sender.first_name
                sender_username = getattr(sender, 'username', None)
            elif hasattr(sender, 'title'):
                sender_name = sender.title
                sender_username = None
            else:
                sender_name = "Unknown"
                sender_username = None
                
            logger.info(f"   👤 שולח: {sender_name}")
            logger.info(f"   💬 תוכן: {message.text[:50] if message.text else 'No text'}...")
            
            # הכנת נתונים לוובהוק
            webhook_data = {
                "message_id": message.id,
                "group_id": str(chat.id),
                "group_name": chat.title,
                "sender_id": sender.id if sender else 0,
                "sender_name": sender_name,
                "sender_username": sender_username,
                "message_text": message.text or "",
                "timestamp": datetime.now().isoformat(),
                "message_type": "text",
                "has_media": message.media is not None,
                "group_type": "private" if chat.id < 0 else "public"
            }
            
            # שליחה לוובהוק
            success = await self.send_to_webhook(webhook_data)
            
            processing_time = time.time() - start_time
            if success:
                logger.info(f"✅ נשלח לוובהוק! (זמן: {processing_time:.2f} שניות)")
            else:
                logger.error(f"❌ שגיאה בשליחת וובהוק (זמן: {processing_time:.2f} שניות)")
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ שגיאה בעיבוד הודעה (זמן: {processing_time:.2f} שניות): {e}")
    
    async def send_to_webhook(self, data):
        """שליחה לוובהוק"""
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.webhook_url,
                    json=data,
                    headers={'Content-Type': 'application/json'},
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        logger.error(f"❌ שגיאה בוובהוק: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ שגיאה בשליחת וובהוק: {e}")
            return False
    
    async def cleanup(self):
        """ניקוי ומתנתקות"""
        try:
            logger.info("🧹 מנקה ומתנתק...")
            if self.client.is_connected():
                await self.client.disconnect()
            logger.info("👋 הסקריפט נעצר")
        except Exception as e:
            logger.error(f"❌ שגיאה בניקוי: {e}")

async def main():
    """פונקציה ראשית"""
    monitor = WebTelegramMonitor()
    try:
        await monitor.start()
    except KeyboardInterrupt:
        logger.info("📴 מקבל סיגנל עצירה...")
    except Exception as e:
        logger.error(f"❌ שגיאה קריטית: {e}")
    finally:
        await monitor.cleanup()

if __name__ == "__main__":
    print("🚀 מתחיל מערכת web לטלגרם מוניטור...")
    print("🌐 הסקריפט יעבוד עם ממשק web")
    print("🔗 כל הודעה תישלח לוובהוק מיד")
    print("⏹️  לחץ Ctrl+C כדי לעצור")
    print("-" * 60)
    
    asyncio.run(main()) 