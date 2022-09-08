#t.me/py_amv_bot

import telebot
from secrets import TOKEN
import requests

print("Telebot 't.me/py_amv_bot' is running.\nQuit the telebot with CTRL-BREAK.")
bot = telebot.TeleBot(TOKEN)


CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                 "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                 "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id", "pinned_message"]


COMMANDS = [
        'start',
        'delete',
        'registration',
        'help',
        'now',
        'tomorrow',
        'today',
        'date'
]

@bot.message_handler(commands=COMMANDS)
def bot_function(msg):
    try:
        resp = requests.get("http://127.0.0.1:8000/bot", {"command": msg.text, "id": msg.chat.id})
        resp = resp.text
    except:
        resp = "Сервер недоступен"  
    try:
        bot.send_message(msg.chat.id, resp, parse_mode="html")
    except:
        resp = requests.get("http://127.0.0.1:8000/bot", {"command": "/delete", "id": msg.chat.id})



@bot.message_handler(content_types=CONTENT_TYPES)
def bot_not_support(msg):
    bot.send_message(msg.chat.id, "Данный запрос не поддерживается", parse_mode="html")
    
bot.infinity_polling()     


