#t.me/py_amv_bot

import telebot
from secrets import TOKEN
import requests

print("Telebot 't.me/py_amv_bot' is running.\nQuit the telebot with CTRL-BREAK.")
bot = telebot.TeleBot(TOKEN)

commands = [
        'start',
        'delete',
        'registration',
        'help',
        'now'
]

@bot.message_handler(commands=commands)
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


bot.infinity_polling()     


