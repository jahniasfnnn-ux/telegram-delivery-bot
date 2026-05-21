import os
import telebot
import requests
import base64
from flask import Flask
from threading import Thread

# إعدادات البوت
TOKEN = os.environ.get('TOKEN')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO = os.environ.get('REPO')
FILE_PATH = os.environ.get('FILE_PATH')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل الآن!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

@bot.message_handler(commands=['get'])
def handle_get(message):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            content = base64.b64decode(r.json()['content']).decode('utf-8')
            bot.reply_to(message, f"المحتوى:\n{content}")
        else:
            bot.reply_to(message, f"خطأ GitHub: {r.status_code}")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    # تشغيل الويب في خيط منفصل (Thread)
    Thread(target=run_web).start()
    # تشغيل البوت
    bot.polling(none_stop=True)
