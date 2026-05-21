import os
import telebot
import requests
import base64
from telebot import types
from flask import Flask
from threading import Thread

# تشغيل خادم ويب وهمي (ليظل البوت متصلاً)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is active!"
def run(): app.run(host='0.0.0.0', port=10000)

TOKEN = os.environ.get('TOKEN')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO = os.environ.get('REPO')
FILE_PATH = os.environ.get('FILE_PATH')
SITE_URL = os.environ.get('SITE_URL') # ضف رابط موقعك في Environment Variables في Render

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
    markup = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton("👁‍🗨 عرض البيانات", callback_data="get_data")
    b2 = types.InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_prompt")
    b3 = types.InlineKeyboardButton("📊 حالة الموقع", callback_data="status")
    b4 = types.InlineKeyboardButton("🌐 رابط الموقع", callback_data="link")
    markup.add(b1, b2, b3, b4)
    bot.send_message(message.chat.id, "مرحباً! اختر إجراءً من لوحة التحكم:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id)
    if call.data == "get_data":
        _, content = get_file_content()
        bot.send_message(call.message.chat.id, f"المحتوى الحالي:\n{content}")
    elif call.data == "edit_prompt":
        bot.send_message(call.message.chat.id, "أرسل النص الجديد:")
        bot.register_next_step_handler(call.message, process_edit)
    elif call.data == "status":
        bot.send_message(call.message.chat.id, "✅ البوت يعمل بكفاءة.")
    elif call.data == "link":
        bot.send_message(call.message.chat.id, f"رابط موقعك: {SITE_URL}")

def process_edit(message):
    new_text = message.text
    sha, _ = get_file_content()
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"message": "Update", "content": base64.b64encode(new_text.encode()).decode(), "sha": sha}
    requests.put(url, headers=headers, json=data)
    bot.send_message(message.chat.id, "تم التحديث بنجاح!")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
