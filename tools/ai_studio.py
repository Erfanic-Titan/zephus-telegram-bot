from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import google.generativeai as genai
from datetime import datetime
import logging
import os
from db4 import database_create_connection
import tempfile
from PIL import Image
import pytesseract
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
import fitz

# تنظیم لاگر
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# تنظیمات Gemini
GOOGLE_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

class AiStudio:
    def __init__(self, app: Client):
        self.app = app
        self.db = database_create_connection()
        self.active_chats = {}
        self.setup_handlers()

    def setup_handlers(self):
        @self.app.on_callback_query(filters.regex('^artificial-intelligence'))
        async def on_ai_callback(client, callback_query):
            chat_id = callback_query.from_user.id
            self.active_chats[chat_id] = True
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("شروع گفتگوی جدید 💭", callback_data="ai_new_chat")],
                [InlineKeyboardButton("بازگشت به ابزارها ⬅️", callback_data="back_to_tools")]
            ])
            
            await callback_query.edit_message_text(
                "به بخش هوش مصنوعی خوش آمدید! 🤖\n"
                "می‌توانید از طریق متن، تصویر، صدا و یا فایل با من در ارتباط باشید.",
                reply_markup=keyboard
            )

        @self.app.on_message(filters.private & filters.text & ~filters.command & self.is_chat_active)
        async def handle_text(client, message: Message):
            chat_id = message.from_user.id
            initial_message = await message.reply_text("🤔 در حال پردازش...")
            
            try:
                response = await self.get_ai_response(message.text)
                await initial_message.edit_text(response)
            except Exception as e:
                logger.error(f"خطا در دریافت پاسخ: {str(e)}")
                await initial_message.edit_text("😕 متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.")

        @self.app.on_message(filters.private & filters.photo & self.is_chat_active)
        async def handle_photo(client, message: Message):
            chat_id = message.from_user.id
            initial_message = await message.reply_text("🔍 در حال پردازش تصویر...")
            
            try:
                photo_path = await message.download()
                text = self.extract_text_from_image(photo_path)
                os.remove(photo_path)
                
                if text:
                    response = await self.get_ai_response(f"تصویر ارسالی شامل این متن است:\n{text}")
                    await initial_message.edit_text(response)
                else:
                    await initial_message.edit_text("متأسفانه نتوانستم متنی از تصویر استخراج کنم.")
            except Exception as e:
                logger.error(f"خطا در پردازش تصویر: {str(e)}")
                await initial_message.edit_text("😕 متأسفانه در پردازش تصویر خطایی رخ داد.")

        @self.app.on_message(filters.private & (filters.voice | filters.audio) & self.is_chat_active)
        async def handle_audio(client, message: Message):
            chat_id = message.from_user.id
            initial_message = await message.reply_text("🎵 در حال پردازش صدا...")
            
            try:
                file = await message.download()
                text = await self.extract_text_from_audio(file)
                os.remove(file)
                
                if text:
                    response = await self.get_ai_response(f"متن استخراج شده از صدا:\n{text}")
                    await initial_message.edit_text(response)
                else:
                    await initial_message.edit_text("متأسفانه نتوانستم متنی از صدا استخراج کنم.")
            except Exception as e:
                logger.error(f"خطا در پردازش صدا: {str(e)}")
                await initial_message.edit_text("😕 متأسفانه در پردازش صدا خطایی رخ داد.")

        @self.app.on_message(filters.private & filters.document & self.is_chat_active)
        async def handle_document(client, message: Message):
            chat_id = message.from_user.id
            initial_message = await message.reply_text("📄 در حال پردازش فایل...")
            
            try:
                file = await message.download()
                text = await self.extract_text_from_document(file, message.document.mime_type)
                os.remove(file)
                
                if text:
                    response = await self.get_ai_response(f"متن استخراج شده از فایل:\n{text}")
                    await initial_message.edit_text(response)
                else:
                    await initial_message.edit_text("متأسفانه نتوانستم متنی از فایل استخراج کنم.")
            except Exception as e:
                logger.error(f"خطا در پردازش فایل: {str(e)}")
                await initial_message.edit_text("😕 متأسفانه در پردازش فایل خطایی رخ داد.")

    def is_chat_active(self, chat_id):
        return chat_id in self.active_chats

    async def get_ai_response(self, text):
        try:
            response = model.generate_content(text)
            return response.text
        except Exception as e:
            logger.error(f"خطا در دریافت پاسخ از AI: {str(e)}")
            raise

    def extract_text_from_image(self, image_path):
        try:
            image = Image.open(image_path)
            return pytesseract.image_to_string(image, lang='fas+eng')
        except Exception as e:
            logger.error(f"خطا در استخراج متن از تصویر: {str(e)}")
            return None

    async def extract_text_from_audio(self, audio_path):
        try:
            # تبدیل فایل صوتی به WAV
            audio = AudioSegment.from_file(audio_path)
            wav_path = tempfile.mktemp(suffix='.wav')
            audio.export(wav_path, format="wav")
            
            # تشخیص متن از صدا
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='fa-IR')
            
            os.remove(wav_path)
            return text
        except Exception as e:
            logger.error(f"خطا در استخراج متن از صدا: {str(e)}")
            return None

    async def extract_text_from_document(self, file_path, mime_type):
        try:
            if mime_type == 'application/pdf':
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            # اضافه کردن پشتیبانی از سایر فرمت‌های فایل در صورت نیاز
            return None
        except Exception as e:
            logger.error(f"خطا در استخراج متن از فایل: {str(e)}")
            return None

    def cleanup_chat(self, chat_id):
        if chat_id in self.active_chats:
            del self.active_chats[chat_id]