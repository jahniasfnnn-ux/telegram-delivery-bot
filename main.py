import os
import telebot
import requests
import base64
from telebot import types
from flask import Flask
from threading import Thread

# 1. إعداد خادم ويب وهمي (لإرضاء Render)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is active!"
def run(): app.run(host='0.0.0.0', port=10000)

# 2. إعداد البوت
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
    bot.send_message(message.chat.id, "مرحباً! أنا جاهز للتحكم في موقعك.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "get_data":
        _, content = get_file_content()
        bot.send_message(call.message.chat.id, f"المحتوى الحالي:\n{content}")
    elif call.data == "edit_prompt":
        bot.send_message(call.message.chat.id, "أرسل لي النص الجديد الآن:")
        bot.register_next_step_handler(call.message, process_edit)

def process_edit(message):
    new_text = message.text
    sha, _ = get_file_content()
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"message": "Update", "content": base64.b64encode(new_text.encode()).decode(), "sha": sha}
    r = requests.put(url, headers=headers, json=data)
    if r.status_code == 200:
        bot.send_message(message.chat.id, "تم التعديل بنجاح!")
    else:
        bot.send_message(message.chat.id, "خطأ في الاتصال.")

# 3. تشغيل الخادم والبوت معاً
if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
