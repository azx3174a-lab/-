import telebot
import requests
import time
import threading
import os
import json
from telebot import types
from flask import Flask

# 1. إعدادات البوت والمطور (تم وضع الآيدي الخاص بك)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = 6081087852  
bot = telebot.TeleBot(TOKEN)

# ملفات تخزين البيانات
USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"
LINKS_FILE = "links.txt"

# دالة لتحميل البيانات
def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: return []
    return []

# دالة لحفظ البيانات
def save_data(file, data):
    with open(file, "w") as f: json.dump(list(set(data)), f)

# 2. Flask للسيرفر (عشان Render يظل شغال)
app = Flask('')
@app.route('/')
def home(): return "✅ البوت المطور يعمل بنجاح!"

def run_flask(): app.run(host='0.0.0.0', port=8080)

# 3. أوامر البوت وقائمة المطور
@bot.message_handler(commands=['start'])
def start(message):
    # حفظ المستخدم أو المجموعة
    if message.chat.type == 'private':
        users = load_data(USERS_FILE)
        if message.chat.id not in users:
            users.append(message.chat.id)
            save_data(USERS_FILE, users)
    else:
        groups = load_data(GROUPS_FILE)
        if message.chat.id not in groups:
            groups.append(message.chat.id)
            save_data(GROUPS_FILE, groups)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("➕ إضافة رابط", callback_data="add")
    btn2 = types.InlineKeyboardButton("📋 قائمة الروابط", callback_data="list")
    
    # يظهر زر المطور لك فقط (بناءً على الآيدي)
    if message.from_user.id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("⚙️ لوحة المطور", callback_data="admin_panel")
        markup.add(btn1, btn2, btn_admin)
    else:
        markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, "👋 أهلاً بك في رادار المراقبة المطور!", reply_markup=markup)

# لوحة التحكم وتفاعل الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "admin_panel":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📢 إذاعة", callback_data="broadcast_menu"),
            types.InlineKeyboardButton("📊 إحصائيات", callback_data="stats"),
            types.InlineKeyboardButton("🛡️ حماية المحتوى", callback_data="toggle_protection"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")
        )
        bot.edit_message_text("🛠️ لوحة تحكم المطور عبد العزيز:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "broadcast_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("👤 للخاص فقط", callback_data="bc_private"),
            types.InlineKeyboardButton("👥 للمجموعات فقط", callback_data="bc_groups"),
            types.InlineKeyboardButton("🌎 للجميع", callback_data="bc_all"),
            types.InlineKeyboardButton("🔙 رجوع للوحة", callback_data="admin_panel")
        )
        bot.edit_message_text("اختر الفئة المستهدفة للإذاعة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "stats":
        users = len(load_data(USERS_FILE))
        groups = len(load_data(GROUPS_FILE))
        bot.answer_callback_query(call.id, f"📊 الإحصائيات الحالية:\n\n👤 عدد المستخدمين: {users}\n👥 عدد المجموعات: {groups}", show_alert=True)

    elif call.data == "toggle_protection":
        bot.answer_callback_query(call.id, "🛡️ تم تفعيل حماية المحتوى! (لا يمكن نسخ أو تحويل رسائل البوت)", show_alert=True)

    elif call.data == "back_to_start":
        # إعادة إرسال قائمة البداية
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)

    # معالجة طلبات الإذاعة
    elif call.data.startswith("bc_"):
        msg = bot.send_message(call.message.chat.id, "أرسل الآن نص الإذاعة (أو صورة مع نص):")
        bot.register_next_step_handler(msg, send_broadcast, call.data)

def send_broadcast(message, target_type):
    targets = []
    if target_type == "bc_private": targets = load_data(USERS_FILE)
    elif target_type == "bc_groups": targets = load_data(GROUPS_FILE)
    elif target_type == "bc_all": targets = load_data(USERS_FILE) + load_data(GROUPS_FILE)
    
    count = 0
    for target in targets:
        try:
            bot.copy_message(target, message.chat.id, message.message_id, protect_content=True)
            count += 1
            time.sleep(0.1) # لتجنب الحظر من تليجرام
        except: pass
    
    bot.send_message(message.chat.id, f"✅ تم إرسال الإذاعة إلى {count} مستهدف.")

# 4. تشغيل البوت والخدمات
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.polling(none_stop=True)
