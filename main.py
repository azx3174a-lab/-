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
OWNER_ID = 6081087852  # أنت المطور الأساسي
bot = telebot.TeleBot(TOKEN)

# ملفات البيانات
USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"
ADMINS_FILE = "admins.json"
LINKS_FILE = "links.txt"
TIMER_FILE = "timer.txt"

# دالات البيانات
def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f)

# 2. Flask للسيرفر
app = Flask('')
@app.route('/')
def home(): return "✅ بوت الإدارة يعمل!"
def run_flask(): app.run(host='0.0.0.0', port=8080)

# 3. التحقق من الصلاحيات
def is_admin(user_id):
    admins = load_json(ADMINS_FILE)
    return str(user_id) in admins or user_id == OWNER_ID

def has_permission(user_id, perm):
    if user_id == OWNER_ID: return True
    admins = load_json(ADMINS_FILE)
    user_perms = admins.get(str(user_id), [])
    return perm in user_perms or "full" in user_perms

# 4. أوامر البداية
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # رسالة لوحة المطور/المشرف
    if is_admin(user_id) and message.chat.type == 'private':
        markup = types.InlineKeyboardMarkup(row_width=2)
        btns = []
        if has_permission(user_id, "broadcast"): btns.append(types.InlineKeyboardButton("📢 إذاعة", callback_data="broadcast_menu"))
        if has_permission(user_id, "stats"): btns.append(types.InlineKeyboardButton("📊 إحصائيات", callback_data="stats"))
        btns.append(types.InlineKeyboardButton("🛡️ حماية", callback_data="toggle_protection"))
        
        # قسم المشرفين يظهر للمطور الأساسي فقط
        if user_id == OWNER_ID:
            btns.append(types.InlineKeyboardButton("👥 قسم المشرفين", callback_data="manage_admins"))
            
        markup.add(*btns)
        bot.send_message(message.chat.id, "⚙️ **لوحة التحكم (الإدارة):**", reply_markup=markup, parse_mode="Markdown")

    # رسالة الترحيب العادية
    user_markup = types.InlineKeyboardMarkup()
    user_markup.row(types.InlineKeyboardButton("➕ إضافة رابط", callback_data="add"), 
                    types.InlineKeyboardButton("📋 قائمة الروابط", callback_data="list"))
    user_markup.row(types.InlineKeyboardButton("⏱️ تعديل الوقت", callback_data="set_time"))
    bot.send_message(message.chat.id, "👋 أهلاً بك في رادار المراقبة!", reply_markup=user_markup)

# 5. إدارة المشرفين
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    user_id = call.from_user.id

    if call.data == "manage_admins" and user_id == OWNER_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ إضافة مشرف", callback_data="add_admin_step"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
        bot.edit_message_text("👥 إدارة فريق العمل:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "add_admin_step":
        msg = bot.send_message(call.message.chat.id, "أرسل ID الشخص المراد رفعه كمشرف:")
        bot.register_next_step_handler(msg, process_admin_id)

    elif call.data == "admin_panel":
        # إعادة إظهار القائمة الرئيسية للمطور
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

    # ... (بقية الأزرار: إذاعة، إحصائيات، إلخ)

def process_admin_id(message):
    try:
        new_admin_id = message.text.strip()
        admins = load_json(ADMINS_FILE)
        # نعطي المشرف الجديد صلاحية الإذاعة والإحصائيات كمثال
        admins[new_admin_id] = ["broadcast", "stats"] 
        save_json(ADMINS_FILE, admins)
        bot.reply_to(message, f"✅ تم رفع المستخدم {new_admin_id} كمشرف بصلاحيات محدودة.")
    except:
        bot.reply_to(message, "❌ فشل! تأكد من إرسال أيدي صحيح.")

# 6. التشغيل
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.polling(none_stop=True)
