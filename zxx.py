from pyrogram import Client, filters, enums
from pyrogram.types import ReplyKeyboardRemove
from buttons2 import *
from languages import *
from tools.ai_studio import register_handlers
import os
from db4 import *
import time
import re
import logging
from telegram.ext import Application

logger = logging.getLogger(__name__)

bot_token = os.environ.get("TOKEN", "8") 
api_hash = os.environ.get("HASH", "a") 
api_id = os.environ.get("ID", "3")

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
user_type_status = {}

# اضافه کردن هندلرهای هوش مصنوعی
telegram_app = Application.builder().token(bot_token).build()
register_handlers(telegram_app)

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

[بقیه توابع موجود بدون تغییر]

def main():
    # راه‌اندازی هر دو اپلیکیشن
    telegram_app.run_polling(close_loop=False)  # اجرای async
    app.run()  # اجرای sync

if __name__ == '__main__':
    main()
