import telebot
from telebot import types
import json
import os

# 1. ضع توكن البوت الخاص بك هنا بين العلامتين
BOT_TOKEN = "8584559549:AAGcj1iJ_njxd2xP_X8vkbTLb92BQnv-34s"
# 2. ضع معرف التلغرام الخاص بك (كأدمن) لتصلك إشعارات الدفع (أرقام بدون فواصل)
ADMIN_ID =    6062763146 

bot = telebot.TeleBot(BOT_TOKEN) 
ACCOUNTS_FILE = "accounts_stock.json"
PENDING_ORDERS = {}

def load_stock():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"fc": [], "siege": [], "pubg": [], "freefire": []}

def save_stock(data):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot.message_handler(commands=['add'])
def add_account(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.reply_to(message, "📝 ارسل اللعبة أولاً بالظبط من هذه الخيارات:\n(pubg أو fc أو siege أو freefire)")
    bot.register_next_step_handler(msg, process_category)

def process_category(message):
    category = message.text.lower().strip()
    stock = load_stock()
    if category not in stock:
        bot.reply_to(message, "❌ اسم اللعبة غير صحيح.")
        return
    msg = bot.reply_to(message, f"📥 الحين ارسل بيانات الحساب كاملة (الإيميل والباسورد):")
    bot.register_next_step_handler(msg, lambda m: save_account_data(m, category))

def save_account_data(message, category):
    account_details = message.text
    stock = load_stock()
    stock[category].append(account_details)
    save_stock(stock)
    bot.reply_to(message, f"✅ تم إضافة الحساب بنجاح! المتوفر في {category}: ({len(stock[category])})")

@bot.message_handler(commands=['start'])
def start_customer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("buy_"):
        category = args[1].replace("buy_", "")
        initiate_purchase(message, category)
        return
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🎮 تصفح الألعاب المتاحة", callback_data="view_stock"))
    bot.send_message(message.chat.id, f"مرحباً بك يا {message.from_user.first_name} في نظام التسليم الآلي! 🤖", reply_markup=markup)

def initiate_purchase(message, category):
    stock = load_stock()
    if category not in stock or len(stock[category]) == 0:
        bot.send_message(message.chat.id, "⚠️ نعتذر منك! هذا القسم نفد من المخزن حالياً.")
        return
    prices = {"fc": "150$", "siege": "90$", "pubg": "120$", "freefire": "75$"}
    price = prices.get(category, "حسب الاتفاق")
    payment_info = f"🛒 *طلب شراء حساب {category.upper()}*\n\n💵 السعر: {price}\n🏦 *بيانات التحويل (بنكك):*\n• رقم الحساب: `249900863926`\n\n⚠️ بعد التحويل، ارسل **صورة إشعار التحويل** هنا فوراً!"
    bot.send_message(message.chat.id, payment_info, parse_mode="Markdown")
    PENDING_ORDERS[message.chat.id] = category

@bot.message_handler(content_types=['photo'])
def handle_payment_proof(message):
    chat_id = message.chat.id
    if chat_id not in PENDING_ORDERS: return
    category = PENDING_ORDERS[chat_id]
    bot.send_message(chat_id, "⏳ جاري إرسال إشعار الدفع للإدارة للتحقق الفوري..")
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ موافقة وتسليم", callback_data=f"approve_{chat_id}_{category}"),
        types.InlineKeyboardButton("❌ رفض الطلب", callback_data=f"reject_{chat_id}")
    )
    bot.send_message(ADMIN_ID, f"🔔 *طلب دفع جديد!*\n👤 الزبون: {message.from_user.first_name}\n🎮 اللعبة: {category.upper()}", parse_mode="Markdown")
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data.split("_")
    action = data[0]
    if action == "approve":
        customer_id = int(data[1])
        category = data[2]
        stock = load_stock()
        if len(stock[category]) == 0: return
        delivered_account = stock[category].pop(0)
        save_stock(stock)
        bot.send_message(customer_id, f"🎉 *تم تأكيد دفعك بنجاح!*\n\n📦 *إليك بيانات حسابك:*\n`{delivered_account}`", parse_mode="Markdown")
        bot.edit_message_caption("✅ تم قبول الطلب وتسليم الحساب بنجاح!", chat_id=call.message.chat.id, message_id=call.message.message_id)
        if customer_id in PENDING_ORDERS: del PENDING_ORDERS[customer_id]
    elif action == "reject":
        customer_id = int(data[1])
        bot.send_message(customer_id, "❌ نعتذر منك، تم رفض طلبك! يرجى التأكد من الإشعار.")
        bot.edit_message_caption("❌ تم رفض هذا الطلب.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        if customer_id in PENDING_ORDERS: del PENDING_ORDERS[customer_id]

bot.infinity_polling()
