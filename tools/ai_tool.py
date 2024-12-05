import os
import logging
from datetime import datetime
import google.generativeai as genai
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from db4 import database_create_connection

# تنظیم لاگر
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# تنظیمات Gemini
GOOGLE_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# ذخیره‌سازی چت‌های فعال
active_ai_chats = {}

class AiTool:
    def __init__(self, app: Client):
        self.app = app
        self.db_connection = database_create_connection()
        self.setup_handlers()

    def setup_handlers(self):
        @self.app.on_callback_query(filters.regex('^artificial-intelligence'))
        async def ai_start(client, callback_query):
            chat_id = callback_query.from_user.id
            active_ai_chats[chat_id] = True
            keyboard = [
                [InlineKeyboardButton("شروع چت جدید 💭", callback_data='ai_new_chat')],
                [InlineKeyboardButton("بازگشت ⬅️", callback_data='back-tools')]
            ]
            await callback_query.edit_message_text(
                "به بخش هوش مصنوعی خوش آمدید! 🤖\n"
                "می‌توانید از طریق متن، تصویر، صدا و یا فایل با من در ارتباط باشید.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        @self.app.on_message(filters.private & filters.text & ~filters.command & active_ai_chats.get)
        async def handle_ai_message(client, message):
            chat_id = message.from_user.id
            if not active_ai_chats.get(chat_id):
                return
            
            initial_message = await message.reply_text("🤔 در حال فکر کردن...")
            try:
                response = model.generate_content(message.text)
                await initial_message.edit_text(response.text)
            except Exception as e:
                logger.error(f"خطا در دریافت پاسخ از Gemini: {e}")
                await initial_message.edit_text("متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.")

        # اضافه کردن هندلرهای دیگر برای پردازش تصویر، صدا و فایل
        # ...

    def stop_chat(self, chat_id):
        if chat_id in active_ai_chats:
            del active_ai_chats[chat_id]