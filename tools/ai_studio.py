import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import logging
from datetime import datetime
import pytesseract
from PIL import Image
import os
import db4

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# پیکربندی API جمنای
genai.configure(api_key="AIzaSyAHHkMQa9h_-tbBmyY9qt0v4D14-vgOdHQ")
model = genai.GenerativeModel("gemini-1.5-flash")

active_chats = {}
rename_state = {}

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
        db4.rename_ai_chat(chat_id, new_title)
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
            "لطفاً یک چت را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return

    try:
        chat_id = active_chats[user_id]
        user_message = update.message.text
        logger.info(f"پیام دریافتی: {user_message}")
        
        db4.add_ai_message(chat_id, "user", user_message)
        chat_history = db4.get_ai_chat_history(chat_id)
        
        initial_response = await update.message.reply_text("⌛ در حال آماده‌سازی پاسخ...")
        response = await send_to_gemini_stream(user_message, initial_response, chat_history)
        
        if response and not response.startswith("خطا:"):
            db4.add_ai_message(chat_id, "assistant", response)
        
    except Exception as e:
        logger.error(f"خطا در پردازش پیام: {str(e)}")
        await update.message.reply_text("😕 متأسفانه خطایی رخ داد.")

async def start_ai_chat(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("شروع چت جدید", callback_data="new_chat")],
        [InlineKeyboardButton("چت‌های قبلی", callback_data="select_chat")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        "به بخش هوش مصنوعی ربات خوش آمدید! 👋\n\n"
        "این بخش با استفاده از Google Gemini 1.5 Flash به سؤالات شما پاسخ می‌دهد.\n"
        "می‌توانید یک چت جدید شروع کنید یا از چت‌های قبلی خود ادامه دهید."
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "new_chat":
        chat_id = db4.create_new_ai_chat(user_id, f"چت {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        active_chats[user_id] = chat_id
        await query.edit_message_text(
            f"چت جدید ایجاد شد! حالا می‌توانید سؤال خود را بپرسید."
        )
    
    elif query.data == "select_chat":
        chats = db4.get_user_ai_chats(user_id)
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
        chats = db4.get_user_ai_chats(user_id)
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
        db4.delete_ai_chat(chat_id)
        if user_id in active_chats and active_chats[user_id] == chat_id:
            del active_chats[user_id]
        await query.answer("چت با موفقیت حذف شد.")
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
        image_path = f"temp_image_{user_id}.jpg"
        await file.download_to_drive(image_path)

        extracted_text = ocr_image(image_path)

        if extracted_text.startswith("خطا:"):
            await update.message.reply_text(extracted_text)
            os.remove(image_path)
            return

        db4.add_ai_message(chat_id, "user", f"تصویر: {extracted_text}")

        initial_response = await update.message.reply_text("⌛ در حال پردازش تصویر...")
        chat_history = db4.get_ai_chat_history(chat_id)
        response = await send_to_gemini_stream(extracted_text, initial_response, chat_history)

        if response and not response.startswith("خطا:"):
            db4.add_ai_message(chat_id, "assistant", response)

        os.remove(image_path)

    except Exception as e:
        logger.error(f"خطا در پردازش تصویر: {str(e)}")
        await update.message.reply_text("😕 متأسفانه خطایی رخ داد.")

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(user_id)
    if not language_code:
        language_code = 'en'

    if query.data == "artificial_intelligence_new_chat":
        chat_id = db4.create_new_ai_chat(user_id, f"چت {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        active_chats[user_id] = chat_id
        await query.edit_message_text(languages[language_code]['ai-chat-created'])


def register_handlers(application: Application):
    application.add_handler(CommandHandler('ai', start_ai_chat))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
