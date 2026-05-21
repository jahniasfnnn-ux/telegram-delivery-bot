import os, telebot
from flask import Flask
from threading import Thread

# إعداد البوت
bot = telebot.TeleBot(os.environ.get('TOKEN'))

# خادم ويب وهمي (ضروري جداً في Render)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=10000)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "البوت يعمل الآن بنجاح!")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
