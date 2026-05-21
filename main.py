import os, telebot, requests, base64
from telebot import types
from flask import Flask
from threading import Thread

# تشغيل خادم ويب وهمي لـ Render
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is live!"
def run_web(): app.run(host='0.0.0.0', port=10000)

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

# دالة لجلب البيانات
def get_data():
    try:
        url = f"https://api.github.com/repos/{os.environ.get('REPO')}/contents/{os.environ.get('FILE_PATH')}"
        headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            d = r.json()
            return d['sha'], base64.b64decode(d['content']).decode('utf-8')
    except: pass
    return None, None

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("👁‍🗨 عرض", callback_data="get"),
           types.InlineKeyboardButton("✏️ تعديل", callback_data="edit"),
           types.InlineKeyboardButton("📊 حالة", callback_data="stat"),
           types.InlineKeyboardButton("🌐 رابط", callback_data="link"))
    bot.send_message(m.chat.id, "لوحة التحكم جاهزة:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    bot.answer_callback_query(c.id)
    if c.data == "get":
        _, txt = get_data()
        bot.send_message(c.message.chat.id, txt or "فارغ")
    elif c.data == "edit":
        bot.send_message(c.message.chat.id, "أرسل النص الجديد:")
        bot.register_next_step_handler(c.message, lambda m: update(m))
    elif c.data == "stat": bot.send_message(c.message.chat.id, "✅ يعمل")
    elif c.data == "link": bot.send_message(c.message.chat.id, os.environ.get('SITE_URL', 'لا يوجد'))

def update(m):
    sha, _ = get_data()
    if sha:
        url = f"https://api.github.com/repos/{os.environ.get('REPO')}/contents/{os.environ.get('FILE_PATH')}"
        requests.put(url, headers={"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}, 
                     json={"message":"upd", "content":base64.b64encode(m.text.encode()).decode(), "sha":sha})
        bot.send_message(m.chat.id, "تم التحديث!")

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
