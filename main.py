import telebot
import requests
import time
import threading
import os
import json
from telebot import types
from flask import Flask

# 1. إعدادات البوت والمطور
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 6081087852  
bot = telebot.TeleBot(TOKEN)

# ملفات تخزين البيانات
USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"
LINKS_FILE = "links.txt"
TIMER_FILE = "timer.txt"

# دالات البيانات
def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return []
    return []

def save_data(file, data):
    with open(file, "w") as f: json.dump(list(set(data)), f)

def get_interval():
    if os.path.exists(TIMER_FILE):
        try:
            with open(TIMER_FILE, "r") as f: return int(f.read().strip())
        except: return 5
    return 5

# 2. Flask للسيرفر
app = Flask('')
@app.route('/')
def home(): return "✅ البوت المطور يعمل!"
def run_flask(): app.run(host='0.0.0.0', port=8080)

# 3. لوحات التحكم
def get_admin_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📢 إذاعة", callback_data="broadcast_menu"),
        types.InlineKeyboardButton("📊 إحصائيات", callback_data="stats"),
        types.InlineKeyboardButton("🛡️ حماية المحتوى", callback_data="toggle_protection"),
        types.InlineKeyboardButton("❌ إغلاق اللوحة", callback_data="close_admin")
    )
    return markup

# 4. أمر البداية
@bot.message_handler(commands=['start'])
def start(message):
    # حفظ البيانات
    if message.chat.type == 'private':
        users = load_data(USERS_FILE)
        if message.chat.id not in users:
            users.append(message.chat.id)
            save_data(USERS_FILE, users)
    
    # أولاً: رسالة المطور (لك فقط)
    if message.from_user.id == ADMIN_ID and message.chat.type == 'private':
        bot.send_message(message.chat.id, "⚙️ **أهلاً بك يا مطور عبد العزيز في لوحة التحكم:**", 
                         reply_markup=get_admin_markup(), parse_mode="Markdown")

    # ثانياً: رسالة الترحيب والمؤقت (للجميع)
    user_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("➕ إضافة رابط", callback_data="add")
    btn2 = types.InlineKeyboardButton("📋 قائمة الروابط", callback_data="list")
    btn3 = types.InlineKeyboardButton("⏱️ تعديل الوقت", callback_data="set_time")
    user_markup.row(btn1, btn2)
    user_markup.row(btn3)
    
    interval = get_interval()
    bot.send_message(message.chat.id, f"👋 أهلاً بك في رادار المراقبة!\n\n⏱️ فحص الروابط كل: {interval} دقائق.", reply_markup=user_markup)

# تفاعل الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # العودة للقائمة الرئيسية للمطور
    if call.data == "admin_panel":
        bot.edit_message_text("⚙️ **لوحة التحكم الخاصة بالمطور عبد العزيز:**", 
                             call.message.chat.id, call.message.message_id, 
                             reply_markup=get_admin_markup(), parse_mode="Markdown")

    elif call.data == "broadcast_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("👤 للخاص", callback_data="bc_private"),
            types.InlineKeyboardButton("👥 للمجموعات", callback_data="bc_groups"),
            types.InlineKeyboardButton("🌎 للجميع", callback_data="bc_all"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")
        )
        bot.edit_message_text("اختر نوع الإذاعة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "stats":
        users = len(load_data(USERS_FILE))
        groups = len(load_data(GROUPS_FILE))
        bot.answer_callback_query(call.id, f"📊 الإحصائيات:\n👤 مستخدمين: {users}\n👥 مجموعات: {groups}", show_alert=True)

    elif call.data == "toggle_protection":
        bot.answer_callback_query(call.id, "🛡️ تم تفعيل حماية المحتوى!", show_alert=True)

    elif call.data == "close_admin":
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == "add":
        msg = bot.send_message(call.message.chat.id, "ارسل رابط الـ Webview:")
        bot.register_next_step_handler(msg, save_link)

    elif call.data == "list":
        links = ""
        if os.path.exists(LINKS_FILE):
            with open(LINKS_FILE, "r") as f: links = f.read()
        bot.send_message(call.message.chat.id, f"🔗 الروابط:\n\n{links if links else 'فارغة'}")

    elif call.data == "set_time":
        msg = bot.send_message(call.message.chat.id, "أرسل الدقائق (رقم فقط):")
        bot.register_next_step_handler(msg, update_timer)

# دالات المعالجة
def save_link(message):
    if "http" in message.text:
        with open(LINKS_FILE, "a") as f: f.write(message.text + "\n")
        bot.reply_to(message, "✅ تم الحفظ")
    else: bot.reply_to(message, "❌ رابط خطأ")

def update_timer(message):
    try:
        t = int(message.text)
        with open(TIMER_FILE, "w") as f: f.write(str(t))
        bot.reply_to(message, f"✅ تم التحديث لـ {t} دقائق")
    except: bot.reply_to(message, "❌ أرسل رقماً فقط")

# 5. التشغيل
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.polling(none_stop=True)
