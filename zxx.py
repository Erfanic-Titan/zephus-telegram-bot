from pyrogram import Client, filters, enums
from pyrogram.types import ReplyKeyboardRemove
from buttons2 import *
from languages import *
import os
from db4 import *
import time
import re
import logging
import google.generativeai as genai
from PIL import Image
import pytesseract
from datetime import datetime

# تنظیمات لاگینگ
logger = logging.getLogger(__name__)

# تنظیمات محیطی
bot_token = os.environ.get("TOKEN", "8061997306:AAHptuoOIUD19MszIqtVhdwSZz_NbtKLj8Q") 
api_hash = os.environ.get("HASH", "a7d65ff251cb1c8cf51f3ca1b90b5a0a") 
api_id = os.environ.get("ID", "25791738")

# تنظیمات Gemini
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# ایجاد نمونه ربات
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# متغیرهای وضعیت
user_type_status = {}
active_ai_chats = {}
rename_state = {}

@app.on_message(filters.command("start"))
def start(client_parametr, info_message_parametr):
    chat_id_user_start = info_message_parametr.from_user.id
    first_name = info_message_parametr.from_user.first_name
    last_name = info_message_parametr.from_user.last_name

    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chat_id_user_start)

    if it_is_true_exists:
        keyboards = create_keyboard(language_code,'welcome-send-text')
        info_message_parametr.reply(languages[language_code]['welcome-send-text'], reply_markup=keyboards, reply_to_message_id=info_message_parametr.id)
    else:
        info_message_parametr.reply(languages['start-text'], reply_markup=keyboard_select_orders_or_tools, reply_to_message_id=info_message_parametr.id)

@app.on_callback_query()
def handle_callback_query(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    first_name = callback_query.from_user.first_name
    last_name = callback_query.from_user.last_name
    user_name = callback_query.from_user.username

    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chat_id)

    # هندلر زبان
    if data in ('fa','en'):
        database_insert_data(chat_id, first_name, last_name, user_name, data)
        callback_query.answer(languages[data]['select-language'])
        keyboards = create_keyboard(data,'select-language')
        callback_query.edit_message_text(text=languages[data]['welcome-send-text'], reply_markup=keyboards)

    # هندلر منوهای اصلی
    elif data in ('tools','orders','setting','account'):
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)

    # هندلر هوش مصنوعی
    elif data == "artificial-intelligence":
        keyboards = create_keyboard(language_code, 'artificial-intelligence')
        callback_query.edit_message_text(
            text=languages[language_code]['ai-welcome'],
            reply_markup=keyboards
        )

    elif data == "ai-new-chat":
        chat_id = create_new_ai_chat(
            user_id, 
            f"چت {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        active_ai_chats[user_id] = chat_id
        callback_query.edit_message_text(
            text=languages[language_code]['ai-new-chat'],
            reply_markup=create_keyboard(language_code, 'back-tools')
        )

    elif data == "ai-select-chat":
        chats = get_user_ai_chats(user_id)
        if not chats:
            callback_query.edit_message_text(
                text=languages[language_code]['ai-no-chats'],
                reply_markup=create_keyboard(language_code, 'artificial-intelligence')
            )
            return

        keyboard = []
        for chat_id, title in chats:
            keyboard.append([
                InlineKeyboardButton(f"💬 {title}", callback_data=f"ai_chat_{chat_id}"),
                InlineKeyboardButton("⚙️", callback_data=f"ai_manage_{chat_id}")
            ])
        keyboard.append([InlineKeyboardButton(languages[language_code]['back'], callback_data="artificial-intelligence")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        callback_query.edit_message_text(
            text=languages[language_code]['ai-select-chat'],
            reply_markup=reply_markup
        )

    elif data.startswith("ai_chat_"):
        chat_id = int(data.split("_")[2])
        active_ai_chats[user_id] = chat_id
        callback_query.edit_message_text(
            text=languages[language_code]['ai-chat-selected'],
            reply_markup=create_keyboard(language_code, 'back-tools')
        )
    
    elif data.startswith("ai_manage_"):
        chat_id = int(data.split("_")[2])
        reply_markup = create_keyboard(language_code, 'ai-chat-management')
        callback_query.edit_message_text(
            text=languages[language_code]['ai-manage-chat'],
            reply_markup=reply_markup
        )
    
    elif data == "ai-rename-chat":
        if user_id in active_ai_chats:
            rename_state[user_id] = active_ai_chats[user_id]
            callback_query.edit_message_text(
                text=languages[language_code]['ai-enter-new-name']
            )
    
    elif data == "ai-delete-chat":
        if user_id in active_ai_chats:
            chat_id = active_ai_chats[user_id]
            delete_ai_chat(chat_id)
            del active_ai_chats[user_id]
            callback_query.answer(languages[language_code]['ai-chat-deleted'])
            keyboards = create_keyboard(language_code, 'artificial-intelligence')
            callback_query.edit_message_text(
                text=languages[language_code]['ai-welcome'],
                reply_markup=keyboards
            )

    # هندلرهای موجود
    elif data == 'change-language':
        keyboards = create_keyboard(language_code, f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
        
    elif data in ('fa-change','en-change'):
        result_change = data.split('-')[0]
        callback_query.answer(languages[result_change]['change-language-db-text'])
        
    # سایر هندلرهای موجود بدون تغییر ...

@app.on_message(filters.private & filters.text)
async def handle_messages(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chat_id)
    
    # بررسی وضعیت تغییر نام چت هوش مصنوعی
    if user_id in rename_state:
        chat_id = rename_state[user_id]
        new_title = message.text
        rename_ai_chat(chat_id, new_title)
        del rename_state[user_id]
        await message.reply_text(
            languages[language_code]['ai-chat-renamed'],
            reply_markup=create_keyboard(language_code, 'artificial-intelligence')
        )
        return
    
    # بررسی چت فعال هوش مصنوعی
    if user_id in active_ai_chats:
        try:
            processing_message = await message.reply_text(
                languages[language_code]['ai-processing']
            )
            
            chat_id = active_ai_chats[user_id]
            user_message = message.text
            
            # ذخیره پیام کاربر
            add_ai_message(chat_id, "user", user_message)
            
            # دریافت تاریخچه چت
            chat_history = get_ai_chat_history(chat_id)
            
            # ساخت پرامپت
            prompt = ""
            for role, content in chat_history[-5:]:  # استفاده از 5 پیام آخر برای کنترل طول تاریخچه
                if role == "user":
                    prompt += f"Human: {content}\n"
                else:
                    prompt += f"Assistant: {content}\n"
            
            prompt += f"Human: {user_message}\nAssistant: "
            
            # دریافت پاسخ از مدل
            try:
                await processing_message.edit_text(languages[language_code]['ai-thinking'])
                response = model.generate_content(prompt)
                response_text = response.text
                
                # ذخیره پاسخ
                add_ai_message(chat_id, "assistant", response_text)
                
                # ارسال پاسخ به کاربر
                await processing_message.edit_text(response_text)
                
            except Exception as e:
                logger.error(f"خطا در دریافت پاسخ از مدل: {str(e)}")
                await processing_message.edit_text(languages[language_code]['ai-error'])
            
        except Exception as e:
            logger.error(f"خطا در پردازش پیام: {str(e)}")
            await message.reply_text(languages[language_code]['ai-error'])
        return

    # پردازش سایر پیام‌های متنی (کد موجود)
    state = user_type_status.get(chat_id, None)
    
    if state == "waiting_for_email":
        user_input = message.text
        email_is_or_not_safe, safe_input_email = sanitize_input(user_input)

        if is_valid_gmail(safe_input_email):
            message.reply(languages[language_code]['written-text-for-a-password-request'], reply_to_message_id=message.id)
            user_type_status[chat_id] = "waiting_for_password"
        else:
            message.reply(languages[language_code]['the-written-text-for-an-incorrect-email'], reply_to_message_id=message.id)

@app.on_message(filters.private & filters.photo)
async def handle_photos(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chat_id)
    
    # پردازش تصویر برای چت هوش مصنوعی
    if user_id in active_ai_chats:
        try:
            processing_message = await message.reply_text(
                languages[language_code]['ai-processing']
            )
            
            # دانلود تصویر
            image_path = f"temp_image_{user_id}.jpg"
            await message.photo[-1].download(image_path)
            
            try:
                # استخراج متن از تصویر
                img = Image.open(image_path)
                extracted_text = pytesseract.image_to_string(img)
                
                if not extracted_text.strip():
                    await processing_message.edit_text(
                        languages[language_code]['ai-no-text-found']
                    )
                    return
                
                chat_id = active_ai_chats[user_id]
                
                # ذخیره متن استخراج شده
                add_ai_message(chat_id, "user", f"[تصویر] {extracted_text}")
                
                # ساخت پرامپت با متن استخراج شده
                chat_history = get_ai_chat_history(chat_id)
                prompt = ""
                for role, content in chat_history[-5:]:
                    if role == "user":
                        prompt += f"Human: {content}\n"
                    else:
                        prompt += f"Assistant: {content}\n"
                
                prompt += f"Human: لطفاً این متن را تحلیل کنید: {extracted_text}\nAssistant: "
                
                # دریافت پاسخ از مدل
                await processing_message.edit_text(languages[language_code]['ai-thinking'])
                response = model.generate_content(prompt)
                response_text = response.text
                
                # ذخیره و ارسال پاسخ
                add_ai_message(chat_id, "assistant", response_text)
                await processing_message.edit_text(response_text)
                
            except Exception as e:
                logger.error(f"خطا در پردازش تصویر: {str(e)}")
                await processing_message.edit_text(languages[language_code]['ai-error'])
            
            finally:
                # حذف فایل موقت
                if os.path.exists(image_path):
                    os.remove(image_path)
                    
        except Exception as e:
            logger.error(f"خطا در دریافت تصویر: {str(e)}")
            await message.reply_text(languages[language_code]['ai-error'])
        return

    # پردازش سایر تصاویر (اگر نیاز باشد)

@app.on_message(filters.contact)
def handle_contact(client, message):
    chid = message.from_user.id
    chtid = message.chat.id
    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chtid)
    
    phone_number = message.contact.phone_number
    formatted_number = "+" + phone_number
    country_code = phone_number[:2]
    local_number = phone_number[2:]
    
    user_type_status.pop(chtid, None)
    
    remove_keyboard = ReplyKeyboardRemove()
    message.reply_text(
        languages[language_code]['deleted-keyboard-send-phone'],
        reply_markup=remove_keyboard
    )

# توابع کمکی
def is_valid_gmail(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(pattern, email) is not None

def sanitize_input(user_input):
    dangerous_pattern = r'[<>;&\'"\/();{}[\]\\#|^]'
    if re.search(dangerous_pattern, user_input):
        safe_output_password = re.sub(dangerous_pattern, '00', user_input)
        return False, safe_output_password
    else:
        return True, user_input

def validate_password(password):
    if len(password) == 12:
        pattern = r'^[!?@$*()0-9a-zA-Z]+$'
        return re.match(pattern, password) is not None
    return False

# اجرای ربات
print('Bot starting...')
app.run()