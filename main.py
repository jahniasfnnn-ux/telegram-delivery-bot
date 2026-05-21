import telebot
import requests

TOKEN = '8584559549:AAE5cOA8MvZu5yTvrop2QI0WlYqB_bVz-88'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['get'])
def get_handler(message):
    # هذا مجرد اختبار لاتصال البوت
    bot.reply_to(message, "تم استلام الأمر، جاري التحقق...")

print("البوت يعمل الآن...")
bot.polling()
