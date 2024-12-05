import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ConversationHandler
import asyncio
import logging
import sqlite3
from datetime import datetime
import pytesseract
from PIL import Image
import os

# فعال کردن لاگینگ
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# پیکربندی API جمنای
genai.configure(api_key="d")
model = genai.GenerativeModel("gemini-1.5-flash")

# تعریف state ها برای conversation handler

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 
        (chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER,
         title TEXT,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages
        (message_id INTEGER PRIMARY KEY AUTOINCREMENT,
         chat_id INTEGER,
         role TEXT,
         content TEXT,
         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (chat_id) REFERENCES chats(chat_id))
        ''')
        self.conn.commit()
    
    def create_new_chat(self, user_id, title):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO chats (user_id, title) VALUES (?, ?)',
            (user_id, title)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def rename_chat(self, chat_id, new_title):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE chats SET title = ? WHERE chat_id = ?',
            (new_title, chat_id)
        )
        self.conn.commit()
    
    def delete_chat(self, chat_id):
        cursor = self.conn.cursor()
        # حذف پیام‌های چت
        cursor.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
        # حذف خود چت
        cursor.execute('DELETE FROM chats WHERE chat_id = ?', (chat_id,))
        self.conn.commit()
    
    def get_user_chats(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT chat_id, title FROM chats WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        )
        return cursor.fetchall()
    
    def add_message(self, chat_id, role, content):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)',
            (chat_id, role, content)
        )
        self.conn.commit()
    
    def get_chat_history(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT role, content FROM messages WHERE chat_id = ? ORDER BY timestamp',
            (chat_id,)
        )
        return cursor.fetchall()

db = DatabaseManager()
active_chats = {}
rename_state = {}  # برای نگهداری وضعیت تغییر نام چت

async def show_chat_management_options(chat_id, title):
    keyboard = [
        [
            InlineKeyboardButton("✏️ تغییر نام", callback_data=f"rename_{chat_id}"),
            InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_{chat_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="select_chat")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    # اگر در حالت تغییر نام هستیم
    if user_id in rename_state:
        chat_id = rename_state[user_id]
        new_title = update.message.text
        db.rename_chat(chat_id, new_title)
        del rename_state[user_id]
        await update.message.reply_text(f"نام چت به '{new_title}' تغییر کرد.")
        return
    
    # اگر کاربر چت فعال ندارد
    if user_id not in active_chats:
        keyboard = [
            [InlineKeyboardButton("چت جدید", callback_data="new_chat")],
            [InlineKeyboardButton("انتخاب چت قبلی", callback_data="select_chat")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "لطفاً اول یک چت را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return

    try:
        chat_id = active_chats[user_id]
        user_message = update.message.text
        logger.info(f"پیام دریافتی: {user_message}")
        
        # ذخیره پیام کاربر
        db.add_message(chat_id, "user", user_message)
        
        # دریافت تاریخچه چت
        chat_history = db.get_chat_history(chat_id)
        
        # ارسال پیام اولیه
        initial_response = await update.message.reply_text("⌛ در حال آماده‌سازی پاسخ...")
        
        # دریافت پاسخ از جمنای
        response = await send_to_gemini_stream(user_message, initial_response, chat_history)
        
        # ذخیره پاسخ جمنای
        if response and not response.startswith("خطا:"):
            db.add_message(chat_id, "assistant", response)
        
    except Exception as e:
        logger.error(f"خطا در پردازش پیام: {str(e)}")
        await update.message.reply_text("😕 متأسفانه خطایی رخ داد.")

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("شروع چت جدید", callback_data="new_chat")],
        [InlineKeyboardButton("چت‌های قبلی", callback_data="select_chat")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        "سلام! 👋\n\n"
        "من یک ربات هوش مصنوعی هستم که با کمک Google Gemini 1.5 Flash به سؤالات شما پاسخ می‌دهم.\n"
        "می‌توانید یک چت جدید شروع کنید یا از چت‌های قبلی خود ادامه دهید."
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "new_chat":
        chat_id = db.create_new_chat(user_id, f"چت {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        active_chats[user_id] = chat_id
        await query.edit_message_text(
            f"چت جدید ایجاد شد! حالا می‌توانید سؤال خود را بپرسید."
        )
    
    elif query.data == "select_chat":
        chats = db.get_user_chats(user_id)
        if not chats:
            await query.edit_message_text("شما هنوز چتی ندارید. می‌توانید یک چت جدید شروع کنید.")
            return
            
        keyboard = []
        for chat_id, title in chats:
            keyboard.append([
                InlineKeyboardButton(f"💬 {title}", callback_data=f"chat_{chat_id}"),
                InlineKeyboardButton("⚙️", callback_data=f"manage_{chat_id}")
            ])
        keyboard.append([InlineKeyboardButton("➕ چت جدید", callback_data="new_chat")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("چت مورد نظر را انتخاب کنید:", reply_markup=reply_markup)
    
    elif query.data.startswith("chat_"):
        chat_id = int(query.data.split("_")[1])
        active_chats[user_id] = chat_id
        await query.edit_message_text(
            f"چت انتخاب شد! می‌توانید به گفتگو ادامه دهید."
        )
    
    elif query.data.startswith("manage_"):
        chat_id = int(query.data.split("_")[1])
        chats = db.get_user_chats(user_id)
        title = next((title for cid, title in chats if cid == chat_id), None)
        if title:
            reply_markup = await show_chat_management_options(chat_id, title)
            await query.edit_message_text(
                f"مدیریت چت: {title}",
                reply_markup=reply_markup
            )
    
    elif query.data.startswith("rename_"):
        chat_id = int(query.data.split("_")[1])
        rename_state[user_id] = chat_id
        await query.edit_message_text(
            "لطفاً نام جدید چت را وارد کنید:"
        )
    
    elif query.data.startswith("delete_"):
        chat_id = int(query.data.split("_")[1])
        keyboard = [
            [
                InlineKeyboardButton("✅ بله", callback_data=f"confirm_delete_{chat_id}"),
                InlineKeyboardButton("❌ خیر", callback_data="select_chat")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "آیا از حذف این چت اطمینان دارید؟",
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("confirm_delete_"):
        chat_id = int(query.data.split("_")[2])
        db.delete_chat(chat_id)
        if user_id in active_chats and active_chats[user_id] == chat_id:
            del active_chats[user_id]
        await query.answer("چت با موفقیت حذف شد.")
        # بازگشت به لیست چت‌ها
        await button_handler(update, context)
    

async def send_to_gemini_stream(message, telegram_message, chat_history=None):
    try:
        await telegram_message.edit_text("🤔 در حال فکر کردن...")
        
        prompt = ""
        if chat_history:
            for role, content in chat_history:
                if role == "user":
                    prompt += f"Human: {content}\n"
                else:
                    prompt += f"Assistant: {content}\n"
        
        prompt += f"Human: {message}\nAssistant: "
        
        response = model.generate_content(prompt, stream=True)
        
        full_response = ""
        last_update = ""
        buffer = ""
        
        for chunk in response:
            if chunk.text:
                buffer += chunk.text
                
                if len(buffer) >= 30 or '.' in buffer or '\n' in buffer:
                    full_response += buffer
                    if full_response != last_update:
                        try:
                            await telegram_message.edit_text(full_response)
                            last_update = full_response
                        except Exception as edit_error:
                            logger.error(f"خطا در آپدیت پیام: {str(edit_error)}")
                        buffer = ""
        
        if buffer:
            full_response += buffer
            try:
                await telegram_message.edit_text(full_response)
            except Exception as final_error:
                logger.error(f"خطا در آپدیت نهایی: {str(final_error)}")
        
        return full_response

    except Exception as e:
        error_message = f"خطا: {str(e)}"
        logger.error(error_message)
        await telegram_message.edit_text(error_message)
        return error_message
    
def ocr_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"خطا در OCR تصویر: {e}"


async def handle_photo(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in active_chats:
        await update.message.reply_text("لطفا ابتدا یک چت را انتخاب کنید.")
        return

    chat_id = active_chats[user_id]
    try:
        file = await update.message.photo[-1].get_file()
        image_path = f"temp_image_{user_id}.jpg"  # مسیر موقت برای ذخیره تصویر، منحصر به فرد برای هر کاربر
        await file.download_to_drive(image_path)

        extracted_text = ocr_image(image_path)

        if extracted_text.startswith("خطا:"):
            await update.message.reply_text(extracted_text)
            os.remove(image_path)  # حذف تصویر موقت در صورت خطا
            return

        db.add_message(chat_id, "user", f"تصویر: {extracted_text}")

        initial_response = await update.message.reply_text("⌛ در حال پردازش تصویر...")

        chat_history = db.get_chat_history(chat_id)
        response = await send_to_gemini_stream(extracted_text, initial_response, chat_history)

        if response and not response.startswith("خطا:"):
            db.add_message(chat_id, "assistant", response)

        os.remove(image_path)  # حذف تصویر موقت پس از پردازش

    except Exception as e:
        logger.error(f"خطا در پردازش تصویر: {str(e)}")
        await update.message.reply_text("😕 متأسفانه خطایی رخ داد.")


def main():
    telegram_token = 'test'
    
    application = Application.builder().token(telegram_token).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    logger.info("ربات شروع به کار کرد...")
    application.run_polling()

if __name__ == '__main__':
    main()
