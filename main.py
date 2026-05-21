import os
import telebot
import requests
import base64

TOKEN = os.environ.get('TOKEN')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO = os.environ.get('REPO')
FILE_PATH = os.environ.get('FILE_PATH')

bot = telebot.TeleBot(TOKEN)

# دالة لجلب البيانات
def get_file_content():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()['sha'], base64.b64decode(r.json()['content']).decode('utf-8')
    return None, None

# دالة لتحديث البيانات
@bot.message_handler(commands=['edit'])
def edit_data(message):
    new_text = message.text.replace('/edit', '').strip()
    if not new_text:
        bot.reply_to(message, "يرجى كتابة النص الجديد بعد الأمر /edit")
        return
    
    sha, _ = get_file_content()
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "message": "Update from Bot",
        "content": base64.b64encode(new_text.encode()).decode(),
        "sha": sha
    }
    r = requests.put(url, headers=headers, json=data)
    
    if r.status_code == 200:
        bot.reply_to(message, "تم تحديث بيانات الموقع بنجاح!")
    else:
        bot.reply_to(message, f"خطأ في التحديث: {r.status_code}")

@bot.message_handler(commands=['get'])
def handle_get(message):
    _, content = get_file_content()
    bot.reply_to(message, f"المحتوى الحالي:\n{content}")

print("البوت يعمل الآن ومستعد للتحكم...")
bot.infinity_polling()
