import telebot
from flask import Flask
from threading import Thread

# ضع التوكين هنا مباشرة
TOKEN = "8584559549:AAE5cOA8MvZu5yTvrop2QI0WlYqB_bVz-88" 

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is working!"
def run(): app.run(host='0.0.0.0', port=10000)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "تم التشغيل بنجاح وبدون إعدادات!")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
