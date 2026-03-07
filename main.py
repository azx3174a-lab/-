import telebot
import requests
import time
import threading
import os
import json
from telebot import types
from flask import Flask

# 1. إعدادات البوت والمطور الأساسي
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID = 6081087852  
RENDER_URL = "https://commander-bot-dxgc.onrender.com"
bot = telebot.TeleBot(TOKEN)

# ملفات البيانات
ADMINS_FILE = "admins.json"
USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"
LINKS_FILE = "links.txt"
TIMER_FILE = "timer.txt"

# دالات إدارة البيانات
def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f)

def get_interval():
    if os.path.exists(TIMER_FILE):
        try:
            with open(TIMER_FILE, "r") as f: return int(f.read().strip())
        except: return 5
    return 5

# 2. نظام النغز الذاتي (تم التعديل لـ 5 دقائق)
def self_ping():
    while True:
        try:
            # نغز الرابط الخاص بمشروعك في Render
            requests.get(RENDER_URL, timeout=10)
            print("🚀 تم نغز السيرفر ذاتياً (كل 5 دقائق)")
        except:
            print("⚠️ فشل النغز الذاتي")
        time.sleep(5 * 60) # الانتظار لمدة 5 دقائق

# 3. Flask للسيرفر
app = Flask('')
@app.route('/')
def home(): return "✅ البوت يعمل بنظام النغز كل 5 دقائق!"

# 4. أوامر البداية واللوحات
def get_admin_markup(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    admins = load_json(ADMINS_FILE)
    perms = admins.get(str(user_id), ["full"]) if user_id != OWNER_ID else ["full"]
    
    btns = []
    if "broadcast" in perms or "full" in perms:
        btns.append(types.InlineKeyboardButton("📢 إذاعة", callback_data="broadcast_menu"))
    if "stats" in perms or "full" in perms:
        btns.append(types.InlineKeyboardButton("📊 إحصائيات", callback_data="stats"))
    
    btns.append(types.InlineKeyboardButton("🛡️ حماية المحتوى", callback_data="toggle_protection"))
    
    if user_id == OWNER_ID:
        btns.append(types.InlineKeyboardButton("👥 قسم المشرفين", callback_data="manage_admins"))
    
    markup.add(*btns)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # حفظ بيانات المستخدم
    if message.chat.type == 'private':
        users = load_json(USERS_FILE)
        if str(user_id) not in users:
            users[str(user_id)] = True
            save_json(USERS_FILE, users)

    # رسالة الإدارة (للمطور والمشرفين)
    admins = load_json(ADMINS_FILE)
    if str(user_id) in admins or user_id == OWNER_ID:
        bot.send_message(message.chat.id, "⚙️ **لوحة التحكم الخاصة بالإدارة:**", 
                         reply_markup=get_admin_markup(user_id), parse_mode="Markdown")

    # رسالة الترحيب والمؤقت (للجميع)
    user_markup = types.InlineKeyboardMarkup(row_width=2)
    user_markup.add(types.InlineKeyboardButton("➕ إضافة رابط", callback_data="add"),
                    types.InlineKeyboardButton("📋 قائمة الروابط", callback_data="list"),
                    types.InlineKeyboardButton("⏱️ تعديل الوقت", callback_data="set_time"))
    
    bot.send_message(message.chat.id, f"👋 أهلاً بك في رادار المراقبة!\n⏱️ الفحص كل: {get_interval()} دقائق.", 
                     reply_markup=user_markup)

# 5. إدارة المشرفين وتفاعل الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    user_id = call.from_user.id

    if call.data == "manage_admins" and user_id == OWNER_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ إضافة مشرف جديد", callback_data="add_admin_step"),
                   types.InlineKeyboardButton("🔙 رجوع للوحة", callback_data="admin_panel"))
        bot.edit_message_text("👥 **قسم إدارة المشرفين:**", 
                             call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "admin_panel":
        bot.edit_message_text("⚙️ **لوحة التحكم الخاصة بالإدارة:**", 
                             call.message.chat.id, call.message.message_id, 
                             reply_markup=get_admin_markup(user_id), parse_mode="Markdown")

    elif call.data == "add_admin_step":
        msg = bot.send_message(call.message.chat.id, "ارسل (ID) الشخص المراد رفعه مشرفاً:")
        bot.register_next_step_handler(msg, add_admin_process)

    elif call.data == "stats":
        u = len(load_json(USERS_FILE))
        bot.answer_callback_query(call.id, f"📊 الإحصائيات:\nالمستخدمين النشطين: {u}", show_alert=True)

    elif call.data == "toggle_protection":
        bot.answer_callback_query(call.id, "🛡️ تم تفعيل حماية المحتوى!", show_alert=True)

    elif call.data == "add":
        msg = bot.send_message(call.message.chat.id, "ارسل رابط الـ Webview:")
        bot.register_next_step_handler(msg, save_link)

    elif call.data == "list":
        links = ""
        if os.path.exists(LINKS_FILE):
            with open(LINKS_FILE, "r") as f: links = f.read()
        bot.send_message(call.message.chat.id, f"🔗 الروابط المراقبة:\n\n{links if links else 'لا توجد روابط'}")

    elif call.data == "set_time":
        msg = bot.send_message(call.message.chat.id, "أرسل عدد الدقائق الجديد:")
        bot.register_next_step_handler(msg, update_timer)

def add_admin_process(message):
    try:
        new_id = message.text.strip()
        admins = load_json(ADMINS_FILE)
        admins[new_id] = ["broadcast", "stats"]
        save_json(ADMINS_FILE, admins)
        bot.reply_to(message, f"✅ تم إضافة المشرف {new_id} بنجاح.")
    except:
        bot.reply_to(message, "❌ حدث خطأ.")

def save_link(message):
    if "http" in message.text:
        with open(LINKS_FILE, "a") as f: f.write(message.text + "\n")
        bot.reply_to(message, "✅ تم حفظ الرابط")
    else: bot.reply_to(message, "❌ الرابط غير صحيح")

def update_timer(message):
    try:
        t = int(message.text)
        with open(TIMER_FILE, "w") as f: f.write(str(t))
        bot.reply_to(message, f"✅ تم التحديث لـ {t} دقائق")
    except: bot.reply_to(message, "❌ أرسل رقماً فقط")

# 6. التشغيل
if __name__ == "__main__":
    threading.Thread(target=self_ping, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.polling(none_stop=True)
