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

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleWebMonitor:
    def __init__(self):
        # פרטי התחברות
        self.api_id = os.getenv("API_ID", "29517731")
        self.api_hash = os.getenv("API_HASH", "1ea4799dac3759058d07f2508979ecb2")
        self.phone = os.getenv("PHONE", "+972508585661")
        self.webhook_url = os.getenv("WEBHOOK_URL", "https://hook.eu1.make.com/xngg9dxi7nc0x5q5jhshb74xmhfpeg06")
        
        # שם קובץ session
        self.session_name = 'telegram_simple_session'
        
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
        self.needs_auth = False
        
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
        app.router.add_post('/restart', self.restart_system) # Add restart route
        
        # הפעלת שרת
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
        await site.start()
        
        logger.info(f"🌐 שרת web פועל על פורט {os.getenv('PORT', 8080)}")
        return runner
        
    async def home_page(self, request):
        """דף הבית - פשוט ונוח"""
        html = """
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>טלגרם מוניטור - התחברות</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f0f2f5;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e1e5e9;
                }
                .header h1 {
                    color: #1a73e8;
                    margin: 0;
                    font-size: 2em;
                }
                .status-box {
                    background: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 30px;
                    text-align: center;
                }
                .status-connected {
                    border-color: #28a745;
                    background: #d4edda;
                }
                .status-waiting {
                    border-color: #ffc107;
                    background: #fff3cd;
                }
                .status-error {
                    border-color: #dc3545;
                    background: #f8d7da;
                }
                .auth-section {
                    background: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 8px;
                    padding: 25px;
                    margin-bottom: 20px;
                    display: none;
                }
                .auth-section.show {
                    display: block;
                }
                .auth-section h3 {
                    margin-top: 0;
                    color: #1976d2;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: bold;
                    color: #555;
                }
                input[type="text"] {
                    width: 100%;
                    padding: 15px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    font-size: 18px;
                    box-sizing: border-box;
                }
                input[type="text"]:focus {
                    border-color: #1a73e8;
                    outline: none;
                }
                .btn {
                    background: #1a73e8;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 8px;
                    font-size: 18px;
                    cursor: pointer;
                    margin: 5px;
                    min-width: 150px;
                }
                .btn:hover {
                    background: #1557b0;
                }
                .btn:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                }
                .btn-success {
                    background: #28a745;
                }
                .btn-warning {
                    background: #ffc107;
                    color: #333;
                }
                .btn-danger {
                    background: #dc3545;
                }
                .message {
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    font-weight: bold;
                }
                .message.success {
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
                .message.error {
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
                .message.info {
                    background: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                }
                .stats {
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 20px;
                }
                .stats h4 {
                    margin-top: 0;
                    color: #495057;
                }
                .auth-steps {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .auth-steps h4 {
                    margin-top: 0;
                    color: #856404;
                }
                .auth-steps ol {
                    margin: 0;
                    padding-right: 20px;
                }
                .auth-steps li {
                    margin-bottom: 10px;
                    line-height: 1.5;
                }
                .connection-info {
                    background: #e3f2fd;
                    border: 1px solid #2196f3;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .connection-info h4 {
                    margin-top: 0;
                    color: #1976d2;
                }
                .connection-info p {
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📱 טלגרם מוניטור</h1>
                    <p>ניהול התחברות ומעקב אחרי הודעות</p>
                </div>
                
                <div class="status-box" id="status-box">
                    <h3>📊 סטטוס המערכת</h3>
                    <p id="status-text">טוען...</p>
                    <p>📱 טלפון: """ + self.phone + """</p>
                    
                    <div style="margin-top: 20px;">
                        <button class="btn btn-success" onclick="showAuthSection()">🔐 מצב התחברות</button>
                        <button class="btn" onclick="refreshStatus()">🔄 רענן סטטוס</button>
                        <button class="btn btn-warning" onclick="restartSystem()">🔄 הפעל מחדש</button>
                    </div>
                </div>
                
                <div class="auth-section" id="auth-section">
                    <h3>🔐 אזור התחברות מלא</h3>
                    
                    <div class="connection-info">
                        <h4>📋 מידע התחברות</h4>
                        <p><strong>טלפון:</strong> """ + self.phone + """</p>
                        <p><strong>API ID:</strong> """ + self.api_id + """</p>
                        <p><strong>קבוצות במעקב:</strong> 4 קבוצות</p>
                        <p><strong>וובהוק:</strong> פעיל</p>
                    </div>
                    
                    <div class="auth-steps">
                        <h4>📝 הוראות התחברות</h4>
                        <ol>
                            <li><strong>שלח הודעה לטלגרם</strong> עם קוד אימות (5 ספרות)</li>
                            <li><strong>הזן את הקוד</strong> בשדה למטה</li>
                            <li><strong>לחץ על "התחבר"</strong> כדי להתחיל</li>
                            <li><strong>חכה לאישור</strong> שההתחברות הצליחה</li>
                        </ol>
                    </div>
                    
                    <form id="auth-form">
                        <div class="form-group">
                            <label for="auth-code">🔢 קוד אימות (5 ספרות):</label>
                            <input type="text" id="auth-code" name="auth_code" 
                                   placeholder="הזן את הקוד שקיבלת מטלגרם (לדוגמה: 12345)" 
                                   maxlength="6" autocomplete="off" pattern="[0-9]{5,6}">
                        </div>
                        <button type="submit" class="btn btn-success" id="auth-btn">🔐 התחבר לטלגרם</button>
                        <button type="button" class="btn btn-danger" onclick="hideAuthSection()">❌ סגור</button>
                    </form>
                    
                    <div id="auth-message"></div>
                </div>
                
                <div class="stats">
                    <h4>📈 סטטיסטיקות</h4>
                    <p>📨 הודעות שנשלחו: <span id="message-count">0</span></p>
                    <p>🕒 הודעה אחרונה: <span id="last-message">אין</span></p>
                    <p>🔗 סטטוס וובהוק: <span id="webhook-status">בדיקה...</span></p>
                </div>
            </div>
            
            <script>
                // רענון אוטומטי כל 3 שניות
                setInterval(refreshStatus, 3000);
                
                function showAuthSection() {
                    document.getElementById('auth-section').classList.add('show');
                    document.getElementById('auth-code').focus();
                }
                
                function hideAuthSection() {
                    document.getElementById('auth-section').classList.remove('show');
                    document.getElementById('auth-message').innerHTML = '';
                }
                
                async function refreshStatus() {
                    try {
                        const response = await fetch('/status');
                        const data = await response.json();
                        
                        const statusBox = document.getElementById('status-box');
                        const statusText = document.getElementById('status-text');
                        const messageCount = document.getElementById('message-count');
                        const lastMessage = document.getElementById('last-message');
                        const webhookStatus = document.getElementById('webhook-status');
                        
                        // עדכון סטטוס
                        statusText.textContent = data.status;
                        
                        // עדכון צבעי סטטוס
                        statusBox.className = 'status-box status-' + data.status_type;
                        
                        // עדכון סטטיסטיקות
                        messageCount.textContent = data.message_count;
                        lastMessage.textContent = data.last_message || 'אין';
                        
                        // עדכון סטטוס וובהוק
                        if (data.is_connected) {
                            webhookStatus.textContent = '✅ פעיל';
                            webhookStatus.style.color = '#28a745';
                        } else {
                            webhookStatus.textContent = '❌ לא פעיל';
                            webhookStatus.style.color = '#dc3545';
                        }
                        
                        // הצגת אזור התחברות אם נדרש
                        if (data.needs_auth) {
                            showAuthSection();
                            showMessage('⚠️ נדרש קוד אימות - שלח הודעה לטלגרם', 'info');
                        }
                        
                    } catch (error) {
                        console.error('שגיאה ברענון סטטוס:', error);
                    }
                }
                
                async function restartSystem() {
                    if (confirm('האם אתה בטוח שברצונך להפעיל מחדש את המערכת?')) {
                        try {
                            const response = await fetch('/restart', { method: 'POST' });
                            const result = await response.json();
                            
                            if (result.success) {
                                showMessage('🔄 המערכת מופעלת מחדש...', 'info');
                                setTimeout(refreshStatus, 2000);
                            } else {
                                showMessage('❌ שגיאה בהפעלה מחדש: ' + result.error, 'error');
                            }
                        } catch (error) {
                            showMessage('❌ שגיאה בהפעלה מחדש', 'error');
                        }
                    }
                }
                
                // טיפול בטופס התחברות
                document.getElementById('auth-form').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const authCode = document.getElementById('auth-code').value.trim();
                    const authBtn = document.getElementById('auth-btn');
                    const authMessage = document.getElementById('auth-message');
                    
                    if (!authCode) {
                        showMessage('❌ אנא הזן קוד אימות', 'error');
                        return;
                    }
                    
                    if (!/^[0-9]{5,6}$/.test(authCode)) {
                        showMessage('❌ הקוד חייב להיות 5-6 ספרות', 'error');
                        return;
                    }
                    
                    // הצגת טעינה
                    authBtn.disabled = true;
                    authBtn.textContent = '⏳ מתחבר...';
                    showMessage('⏳ מתחבר לטלגרם...', 'info');
                    
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
                            showMessage('✅ התחברות הצליחה! המערכת עובדת', 'success');
                            document.getElementById('auth-code').value = '';
                            setTimeout(() => {
                                hideAuthSection();
                                refreshStatus();
                            }, 2000);
                        } else {
                            showMessage('❌ שגיאה בהתחברות: ' + result.error, 'error');
                        }
                    } catch (error) {
                        showMessage('❌ שגיאה בשליחת הקוד', 'error');
                    } finally {
                        // החזרת כפתור למצב רגיל
                        authBtn.disabled = false;
                        authBtn.textContent = '🔐 התחבר לטלגרם';
                    }
                });
                
                function showMessage(text, type) {
                    const authMessage = document.getElementById('auth-message');
                    authMessage.className = 'message ' + type;
                    authMessage.textContent = text;
                }
                
                // טעינה ראשונית
                refreshStatus();
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
                self.needs_auth = False
                
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
            'message_count': self.message_count,
            'last_message': self.last_message_time.isoformat() if self.last_message_time else None,
            'is_connected': self.is_connected,
            'needs_auth': self.needs_auth
        }
        return web.json_response(status_data)
    
    def get_status_text(self):
        """קבלת טקסט סטטוס"""
        if self.is_connected:
            return "✅ מחובר ועובד - המערכת עוקבת אחרי הודעות"
        elif self.needs_auth:
            return "⚠️ ממתין לקוד אימות - שלח הודעה לטלגרם"
        else:
            return "❌ לא מחובר - הזן קוד אימות"
    
    def get_status_type(self):
        """קבלת סוג סטטוס"""
        if self.is_connected:
            return "connected"
        elif self.needs_auth:
            return "waiting"
        else:
            return "error"
    
    async def start(self):
        """התחלת המערכת"""
        try:
            logger.info("🚀 מתחיל מערכת web פשוטה...")
            
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
                self.needs_auth = False
                
                logger.info("✅ התחברות הצליחה!")
                
                # הפעלת המעקב
                asyncio.create_task(self.start_monitoring())
                return
                
            except SessionPasswordNeededError:
                logger.error("🔐 נדרשת סיסמה דו-שלבית")
                self.needs_auth = True
                raise
            except Exception as e:
                error_msg = str(e)
                if "EOF when reading a line" in error_msg or "code" in error_msg.lower():
                    logger.warning("⚠️ נדרש אימות ראשוני")
                    self.needs_auth = True
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
                        self.needs_auth = True
                        raise
        
        self.needs_auth = True
        raise Exception("❌ לא הצלחתי להתחבר אחרי כל הניסיונות")
    
    async def start_monitoring(self):
        """התחלת המעקב אחרי הודעות"""
        try:
            # הדפסת מידע על הקבוצות
            await self.print_group_info()
            
            # הגדרת מאזין להודעות
            self.setup_message_handler()
            
            logger.info("🎧 מאזין פשוט הותקן")
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
    
    async def restart_system(self, request):
        """הפעלה מחדש של המערכת"""
        try:
            logger.info("🔄 מתחיל מחדש את המערכת...")
            
            # איפוס משתנים
            self.is_connected = False
            self.needs_auth = False
            
            # ניסיון התחברות מחדש
            await self.connect_with_retry()
            
            return web.json_response({'success': True})
        except Exception as e:
            logger.error(f"❌ שגיאה בהפעלה מחדש: {e}")
            return web.json_response({'success': False, 'error': str(e)})
    
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
    monitor = SimpleWebMonitor()
    try:
        await monitor.start()
    except KeyboardInterrupt:
        logger.info("📴 מקבל סיגנל עצירה...")
    except Exception as e:
        logger.error(f"❌ שגיאה קריטית: {e}")
    finally:
        await monitor.cleanup()

if __name__ == "__main__":
    print("🚀 מתחיל מערכת web פשוטה לטלגרם מוניטור...")
    print("🌐 הסקריפט יעבוד עם ממשק web נוח")
    print("🔗 כל הודעה תישלח לוובהוק מיד")
    print("⏹️  לחץ Ctrl+C כדי לעצור")
    print("-" * 60)
    
    asyncio.run(main()) 