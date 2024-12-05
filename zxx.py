from pyrogram import Client, filters, enums
from pyrogram.types import ReplyKeyboardRemove
from buttons2 import *
from languages import *
import os
from db4 import *
import time
import re
import logging

#log
logger = logging.getLogger(__name__)

# env
bot_token = os.environ.get("TOKEN", "8") 
api_hash = os.environ.get("HASH", "a") 
api_id = os.environ.get("ID", "3")

# bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
user_type_status = {}

active_ai_chats = {}

@app.on_message(filters.command("start"))
def start(client_parametr, info_message_parametr):
	#start.cius = info_message_parametr.from_user.id
	chat_id_user_start = info_message_parametr.from_user.id
	first_name = info_message_parametr.from_user.first_name
	last_name = info_message_parametr.from_user.last_name
#user_name = info_message_parametr.from_user.username
#language_code = info_message_parametr.from_user.language_code

	it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chat_id_user_start)

	if it_is_true_exists == True:
		keyboards = create_keyboard(language_code,'welcome-send-text')
		info_message_parametr.reply(languages[language_code]['welcome-send-text'], reply_markup=keyboards, reply_to_message_id=info_message_parametr.id)
	else:
		info_message_parametr.reply(languages['start-text'], reply_markup=keyboard_select_orders_or_tools, reply_to_message_id=info_message_parametr.id)

@app.on_callback_query()
def handle_callback_query_for_select_language(client, callback_query):
    data = callback_query.data
    user_id_user_click_callback = callback_query.from_user.id
    chat_id_user_click_callback = callback_query.message.chat.id
    first_name_user_click_callback = callback_query.from_user.first_name
    last_name_user_click_callback = callback_query.from_user.last_name
    user_name_user_click_callback = callback_query.from_user.username
    #message = callback_query.message

    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chat_id_user_click_callback)
    print(it_is_true_exists,chat_id, first_name, last_name, user_name, language_code)
    #print(ui)

    if data in ('fa','en'):
        database_insert_data (chat_id_user_click_callback, first_name_user_click_callback, last_name_user_click_callback, user_name_user_click_callback, data)
        callback_query.answer(languages[data]['select-language'])
        keyboards = create_keyboard(data,'select-language')
        callback_query.edit_message_text(text=languages[data]['welcome-send-text'], reply_markup=keyboards)

    if data in ('tools','orders','setting','account'):
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
    
    if data == 'change-language':
        keyboards = create_keyboard(language_code, f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
        
    if data in ('fa-change','en-change'):
        result_change = data.split('-')[0]
        #change database for language
        callback_query.answer(languages[result_change]['change-language-db-text'])
        
    if data == '2fa':
    	#unknown

        keyboards = create_keyboard(language_code, f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
        
    if data == 'clear-database':
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards) 

    if data == 'clear-database-yes':
        #dell database
        callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes'])
        time.sleep(2)
        callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes2'])
        time.sleep(2)
        callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes3'])
        time.sleep(2)
        callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes4'])
        time.sleep(2)
        callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes5'])
        time.sleep(1)
        callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes6'])
        time.sleep(1)
        callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes7'])
        
        
    if data == 'clear-database-nope':
        keyboards = create_keyboard(language_code, 'back-menu-for-else')
        callback_query.edit_message_text(text=languages[language_code]['welcome-send-text'], reply_markup=keyboards)
        
    if data == 'account-upgrade':
        keyboards = create_keyboard(language_code, f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)   
    
    if data == 'active-by-user-password':
        #send user name of the after password
	    #clear text is tag script
		#hashing password
    
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)     
    
    if data == 'activate-with-email-and-password':
        #send email of the after password
    	#filter of emil in gmail
	    #clear text is tag script
	    #hashing password
        state = user_type_status.get(chat_id_user_click_callback, None)
        if state is None:
            user_type_status[chat_id_user_click_callback] = "waiting_for_email"
            callback_query.edit_message_text(text=languages[language_code]['a-written-text-for-requesting-to-send-an-email'])
        
        if data == 'activate-with-phone':
         #send phone
         #check code by iran
         user_type_status[chat_id_user_click_callback] = "waiting_for_phone"
        state = user_type_status.get(chat_id_user_click_callback, None)
        #print(state)
        keyboards = create_keyboard(language_code, f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
        if state == "waiting_for_phone":
            keyboards = create_keyboard(language_code, 'send-button-number')
            callback_query.message.reply_text(languages[language_code]['xx'], reply_markup=keyboards)
            #print(user_type_status)
            #print(state)
	         
        if data == 'activate-with-phone-text-button-nope':
        #del user_type_status[chat_id_user_click_callback]
	    #callback_query.answer("dell dell", show_alert=True)
         user_type_status.pop(chat_id_user_click_callback, None)
        remove_keyboard = ReplyKeyboardRemove()
        callback_query.message.reply_text(languages[language_code]['deleted-keyboard-send-phone'], reply_markup=remove_keyboard)
        keyboards = create_keyboard(language_code, 'account-upgrade')
        callback_query.edit_message_text(languages[language_code]['account-upgrade-text'], reply_markup=keyboards)
	
	
	
    if data == 'account-status-guide':
    	#fetch one database status user if phone active
    	#text for status account user
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
        
    if data == 'recovery-account':
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
        #unknown
        
    if data == 'invitation-to-friends':
    	#send text for link
	    #create link zir
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
        
    if data == 'history-of-my-account':
        #fetchall columns database is not data hidden
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards)
    	
        
    if data == 'wallet-recharge':
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code][f'{data}-text'], reply_markup=keyboards) 
    	#unknown
    	

    if data == 'back-home':
        keyboards = create_keyboard(language_code,f'{data}')
        callback_query.edit_message_text(text=languages[language_code]['welcome-send-text'], reply_markup=keyboards)
        
        


@app.on_message(filters.private & filters.text)
def handler_email(client, message):
    chat_id_user_active_with_email_password = message.chat.id
    #print(chat_id_user_active_with_email_password)
    #print('user_type', user_type_status)
    
    chid = message.from_user.id
    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chid)
    
    state = user_type_status.get(chat_id_user_active_with_email_password, None)
    #print('before if state', state)
        
    if state == "waiting_for_email":
        user_input = message.text
        #print('user_input', user_input)
        
        email_is_or_not_safe ,safe_input_email = sanitize_input(user_input)
        #print('safe input email', safe_input_email)

        if is_valid_gmail(safe_input_email):
            message.reply(languages[language_code]['written-text-for-a-password-request'], reply_to_message_id=message.id)
            #print('user_input2', user_input)
            user_type_status[chat_id_user_active_with_email_password] = "waiting_for_password"
            #print('email:', user_type_status)
        else:
            message.reply(languages[language_code]['the-written-text-for-an-incorrect-email'], reply_to_message_id=message.id)
            #print('after', state)
            #print('after', user_type_status)

    elif state == "waiting_for_password":
        user_input_password = message.text 
        password_is_or_not_safe , safe_output_password = sanitize_input(user_input_password)

        if password_is_or_not_safe == False:
            message.reply(languages[language_code]['written-text-for-unsafe-characters'])
            #user_type_status[chat_id_user_active_with_email_password] = "waiting_for_password"
            #print('danger:', user_type_status)
        else:
            if validate_password(safe_output_password):
                keyboards = create_keyboard(language_code, 'text-announcement-to-declare-the-end-of-the-request-for-email-and-password-operations')
                message.reply(languages[language_code]['text-announcement-to-declare-the-end-of-the-request-for-email-and-password-operations'], reply_markup=keyboards)
                user_type_status.pop(chat_id_user_active_with_email_password, None)
                print(user_type_status)
            else:
                message.reply(languages[language_code]['text-for-password-length'])
                #user_type_status[chat_id_user_active_with_email_password] = "waiting_for_password"
                #print('len:', user_type_status)
 
    else:
        #user_type_status[chat_id_user_active_with_email_password] = "waiting_for_password"
        #print('email:', user_type_status)
        #state = "waiting_for_password"
        #print('email:', state)
        pass

def is_valid_gmail(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(pattern, email) is not None

def sanitize_input(user_input):
    dangerous_pattern = r'[<>;&\'"\/();{}[\]\\#|^]'
    if re.search(dangerous_pattern, user_input):
        safe_output_password = re.sub(dangerous_pattern, '00', user_input)
        return False,safe_output_password
    else:
        return True,user_input

def validate_password(password):
    if len(password) == 12:
        pattern = r'^[!?@$*()0-9a-zA-Z]+$'
        return re.match(pattern, password) is not None
    return False


@app.on_message(filters.contact)
def handle_contact(client, message):
	chid = message.from_user.id
	chtid = message.chat.id
	#state = user_type_status.get(chtid, None)
	it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chtid)
	phone_number = message.contact.phone_number
	formatted_number = "+" + phone_number
	country_code = phone_number[:2]
	local_number = phone_number[2:]
	user_type_status.pop(chtid, None)
	print("شماره فرمت شده:", formatted_number)
	print("کد کشور:", country_code)
	print("شماره محلی:", local_number)
	#print(f"کاربر {chid,chtid} شماره تلفن {phone_number} را ارسال کرد.")
	remove_keyboard = ReplyKeyboardRemove()
	message.reply_text(languages[language_code]['deleted-keyboard-send-phone'], reply_markup=remove_keyboard)


app.run()
