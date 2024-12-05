from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from languages import *
from db4 import check_for_existence_in_the_database


keyboard_select_orders_or_tools = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("فارسی 🇮🇷", callback_data="fa"),
        InlineKeyboardButton("ENGLISH 🇬🇧", callback_data="en")
    ]
])


def create_keyboard(language_code, keyboards_type):
    if keyboards_type == 'tools':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['management-and-growth-for-page-and-channel'], callback_data='management-and-growth-for-page-and-channel')],
            [InlineKeyboardButton(languages[language_code]['media-downloader'], callback_data='media-downloader')],
            [InlineKeyboardButton(languages[language_code]['file-format-converter'], callback_data='file-format-converter')],
            [InlineKeyboardButton(languages[language_code]['file-link-converter'], callback_data='file-link-converter')],
            [InlineKeyboardButton(languages[language_code]['file-quality-editor'], callback_data='file-quality-editor')],
            [InlineKeyboardButton(languages[language_code]['ip-network-tool'], callback_data='ip-network-tool')],
            [InlineKeyboardButton(languages[language_code]['bypass-sanctions'], callback_data='bypass-sanctions')],
            [InlineKeyboardButton(languages[language_code]['antivirus-antiscammer'], callback_data='antivirus-antiscammer')],
            [InlineKeyboardButton(languages[language_code]['fact-checker'], callback_data='fact-checker')],
            [InlineKeyboardButton(languages[language_code]['smart-music-finder'], callback_data='smart-music-finder')],
            [InlineKeyboardButton(languages[language_code]['smart-feed-reader'], callback_data='smart-feed-reader')],
            [InlineKeyboardButton(languages[language_code]['smart-translator'], callback_data='smart-translator')],
            [InlineKeyboardButton(languages[language_code]['live-stock-market'], callback_data='live-stock-market')],
            [InlineKeyboardButton(languages[language_code]['temporary-email-sms'], callback_data='temporary-email-sms')],
            [InlineKeyboardButton(languages[language_code]['apply-assistant'], callback_data='apply-assistant')],
            [InlineKeyboardButton(languages[language_code]['telegram-search'], callback_data='telegram-search')],
            [InlineKeyboardButton(languages[language_code]['voice-text-converter'], callback_data='voice-text-converter')],
            [InlineKeyboardButton(languages[language_code]['movie-series-downloader'], callback_data='movie-series-downloader')],
            [InlineKeyboardButton(languages[language_code]['book-article-downloader'], callback_data='book-article-downloader')],
            [InlineKeyboardButton(languages[language_code]['artificial-intelligence'], callback_data='artificial-intelligence')],
            [
                InlineKeyboardButton(languages[language_code]['account'], callback_data='account'),
                InlineKeyboardButton(languages[language_code]['setting'], callback_data='setting')
            ],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='back-menu-for-else')]
        ])

    elif keyboards_type == 'orders':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['gift-card-request'], callback_data='gift-card-request')],
            [InlineKeyboardButton(languages[language_code]['gem-and-rewards-request'], callback_data='gem-and-rewards-request')],
            [InlineKeyboardButton(languages[language_code]['seo-request'], callback_data='seo-request')],
            [InlineKeyboardButton(languages[language_code]['website-design-request'], callback_data='website-design-request')],
            [InlineKeyboardButton(languages[language_code]['bot-design-request'], callback_data='bot-design-request')],
            [InlineKeyboardButton(languages[language_code]['server-request'], callback_data='server-request')],
            [InlineKeyboardButton(languages[language_code]['security-request'], callback_data='security-request')],
            [InlineKeyboardButton(languages[language_code]['project-upload-channel'], callback_data='project-upload-channel')],
            [InlineKeyboardButton(languages[language_code]['account-request-channel'], callback_data='account-request-channel')],
            [
                InlineKeyboardButton(languages[language_code]['account'], callback_data='account'),
                InlineKeyboardButton(languages[language_code]['setting'], callback_data='setting')
            ],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='back-menu-for-else')]
        ])

    elif keyboards_type == 'setting':
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(languages[language_code]['change-language'], callback_data='change-language'),
                InlineKeyboardButton(languages[language_code]['2fa'], callback_data='2fa')
            ],
            [InlineKeyboardButton(languages[language_code]['clear-database'], callback_data='clear-database')],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='back-home')]
        ])

    elif keyboards_type == 'change-language':
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("فارسی 🇮🇷", callback_data="fa-change"),
                InlineKeyboardButton("ENGLISH 🇬🇧", callback_data="en-change")
            ],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='setting')]
        ])

    elif keyboards_type == '2fa':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='setting')]
        ])

    elif keyboards_type == 'clear-database':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['clear-database-nope'], callback_data='clear-database-nope')],
            [InlineKeyboardButton(languages[language_code]['clear-database-yes'], callback_data='clear-database-yes')],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='setting')]
        ])

    elif keyboards_type == 'account':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['account-upgrade'], callback_data='account-upgrade')],
            [InlineKeyboardButton(languages[language_code]['account-status-guide'], callback_data='account-status-guide')],
            [
                InlineKeyboardButton(languages[language_code]['recovery-account'], callback_data='recovery-account'),
                InlineKeyboardButton(languages[language_code]['invitation-to-friends'], callback_data='invitation-to-friends')
            ],
            [
                InlineKeyboardButton(languages[language_code]['history-of-my-account'], callback_data='history-of-my-account'),
                InlineKeyboardButton(languages[language_code]['wallet-recharge'], callback_data='wallet-recharge')
            ],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='back-home')]
        ])

    elif keyboards_type == 'account-upgrade':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['activate-with-user-name-and-password'], callback_data='activate-with-user-name-and-password')],
            [InlineKeyboardButton(languages[language_code]['activate-with-email-and-password'], callback_data='activate-with-email-and-password')],
            [InlineKeyboardButton(languages[language_code]['activate-with-phone'], callback_data='activate-with-phone')],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='account')]
        ])

    elif keyboards_type == 'text-announcement-to-declare-the-end-of-the-request-for-email-and-password-operations':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='account-upgrade')]
        ])

    elif keyboards_type == 'activate-with-phone':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['activate-with-phone-text-button-nope'], callback_data='activate-with-phone-text-button-nope')]
        ])

    elif keyboards_type == 'send-button-number':
        keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("ارسال شماره تلفن", request_contact=True)],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    elif keyboards_type == 'account-status-guide':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='account')]
        ])

    elif keyboards_type == 'recovery-account':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='account')]
        ])

    elif keyboards_type == 'invitation-to-friends':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='account')]
        ])

    elif keyboards_type == 'history-of-my-account':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='account')]
        ])

    elif keyboards_type == 'wallet-recharge':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='account')]
        ])

    else:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(languages[language_code]['tools'], callback_data="tools"),
                InlineKeyboardButton(languages[language_code]['orders'], callback_data="orders")
            ],
            [
                InlineKeyboardButton(languages[language_code]['account'], callback_data="account"),
                InlineKeyboardButton(languages[language_code]['setting'], callback_data="setting")
            ]
        ])

#ai
def create_keyboard(language_code, keyboards_type):
    if keyboards_type == 'artificial-intelligence':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(languages[language_code]['ai-new-chat'], callback_data='new_chat')],
            [InlineKeyboardButton(languages[language_code]['ai-previous-chats'], callback_data='select_chat')],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='tools')]
        ])
        
    elif keyboards_type == 'ai-chat-management':
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(languages[language_code]['ai-rename-chat'], callback_data='rename_chat'),
                InlineKeyboardButton(languages[language_code]['ai-delete-chat'], callback_data='delete_chat')
            ],
            [InlineKeyboardButton(languages[language_code]['back'], callback_data='select_chat')]
        ])

    elif keyboards_type == 'ai-confirm-delete':
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅", callback_data='confirm_delete'),
                InlineKeyboardButton("❌", callback_data='select_chat')
            ]
        ])

    return keyboard
