import google.generativeai as genai
from db4 import *
from languages import languages
import logging
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
genai.configure(api_key="AIzaSyAHHkMQa9h_-tbBmyY9qt0v4D14-vgOdHQ")
model = genai.GenerativeModel("gemini-1.5-flash")

# نگهداری وضعیت چت‌های فعال و تغییر نام
active_ai_chats = {}
rename_state = {}

async def handle_ai_message(message, user_id, language_code):
    """پردازش پیام‌های متنی ارسال شده به هوش مصنوعی"""
    
    if user_id not in active_ai_chats:
        return languages[language_code]['ai-select-chat-first']

    try:
        chat_id = active_ai_chats[user_id]
        
        # ذخیره پیام کاربر
        add_ai_message(chat_id, "user", message)
        
        # دریافت تاریخچه چت
        chat_history = get_ai_chat_history(chat_id)
        
        # ساخت پرامپت با تاریخچه
        prompt = ""
        for role, content in chat_history:
            if role == "user":
                prompt += f"Human: {content}\n"
            else:
                prompt += f"Assistant: {content}\n"
        
        prompt += f"Human: {message}\nAssistant: "
        
        # دریافت پاسخ از جمنای
        response = model.generate_content(prompt)
        response_text = response.text
        
        # ذخیره پاسخ
        add_ai_message(chat_id, "assistant", response_text)
        
        return response_text

    except Exception as e:
        logger.error(f"خطا در پردازش پیام: {str(e)}")
        return languages[language_code]['ai-error']

async def handle_ai_photo(photo, user_id, language_code):
    """پردازش تصاویر ارسال شده به هوش مصنوعی"""
    
    if user_id not in active_ai_chats:
        return languages[language_code]['ai-select-chat-first']

    try:
        chat_id = active_ai_chats[user_id]
        image_path = f"temp_image_{user_id}.jpg"
        
        # دانلود و ذخیره موقت تصویر
        await photo.download(image_path)
        
        # استخراج متن از تصویر
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)
        
        # حذف فایل موقت
        os.remove(image_path)
        
        if not extracted_text.strip():
            return languages[language_code]['ai-no-text-found']
        
        # ذخیره متن استخراج شده
        add_ai_message(chat_id, "user", f"[تصویر] {extracted_text}")
        
        # دریافت پاسخ از مدل
        response = await handle_ai_message(extracted_text, user_id, language_code)
        
        return response

    except Exception as e:
        logger.error(f"خطا در پردازش تصویر: {str(e)}")
        if os.path.exists(image_path):
            os.remove(image_path)
        return languages[language_code]['ai-error']

def set_active_chat(user_id, chat_id):
    """تنظیم چت فعال برای کاربر"""
    active_ai_chats[user_id] = chat_id

def get_active_chat(user_id):
    """دریافت چت فعال کاربر"""
    return active_ai_chats.get(user_id)

def set_rename_state(user_id, chat_id):
    """تنظیم وضعیت تغییر نام چت"""
    rename_state[user_id] = chat_id

def get_rename_state(user_id):
    """دریافت وضعیت تغییر نام چت"""
    return rename_state.get(user_id)

def clear_rename_state(user_id):
    """پاک کردن وضعیت تغییر نام چت"""
    if user_id in rename_state:
        del rename_state[user_id]