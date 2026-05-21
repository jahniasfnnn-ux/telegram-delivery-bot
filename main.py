import os
import telebot
import requests
import base64
from telebot import types

TOKEN = os.environ.get('TOKEN')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO = os.environ.get('REPO')
FILE_PATH = os.environ.get('FILE_PATH')

bot = telebot.TeleBot(TOKEN)

def get_file_content():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()['sha'], base64.b64decode(r.json()['content']).decode('utf-8')
    return None, None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("عرض المحتوى", callback_data="get_data"))
    markup.add(types.InlineKeyboardButton("تعديل البيانات", callback_data="edit_prompt"))
    bot.send_message(message.chat.id, "أهلاً بك في لوحة تحكم موقعك:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "get_data":
        _, content = get_file_content()
        bot.answer_callback_query(call.id, "جاري الجلب...")
        bot.send_message(call.message.chat.id, f"المحتوى الحالي:\n{content}")
    elif call.data == "edit_prompt":
        bot.send_message(call.message.chat.id, "أرسل النص الجديد:")
        bot.register_next_step_handler(call.message, process_edit)

def process_edit(message):
    new_text = message.text
    sha, _ = get_file_content()
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"message": "Update via bot", "content": base64.b64encode(new_text.encode()).decode(), "sha": sha}
    r = requests.put(url, headers=headers, json=data)
    if r.status_code == 200:
        bot.send_message(message.chat.id, "تم التحديث بنجاح!")
    else:
        bot.send_message(message.chat.id, "خطأ في التحديث.")

bot.infinity_polling()
