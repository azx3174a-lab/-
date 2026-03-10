import telebot
import os
from flask import Flask
import threading
import time
import requests
from telebot import types

# 1. الإعدادات الأساسية
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
OWNER_ID = 6081087852  # 💡 حط الأيدي حقك هنا يا عبد العزيز
RENDER_URL = "https://commander-bot-dxgc.onrender.com"

app = Flask('')

@app.route('/')
def home(): return "📡 رادار المراقبة يعمل بنجاح!"

# 2. نظام النغز الذاتي (كل 5 دقائق)
def self_ping():
    while True:
        try:
            requests.get(RENDER_URL, timeout=10)
            print("🕒 تم الفحص الدوري: السيرفر مستقر")
        except: pass
        time.sleep(5 * 60)

# 3. لوحة التحكم بالشكل القديم (الأزرار الكبيرة)
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📊 إحصائيات")
    btn2 = types.KeyboardButton("📢 إذاعة")
    btn3 = types.KeyboardButton("👥 قسم المشرفين")
    btn4 = types.KeyboardButton("🛡️ حماية المحتوى")
    btn5 = types.KeyboardButton("📋 قائمة الروابط")
    btn6 = types.KeyboardButton("➕ إضافة رابط")
    btn7 = types.KeyboardButton("🕒 تعديل الوقت")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id == OWNER_ID:
        welcome_text = (
            "⚙️ لوحة التحكم الخاصة بالإدارة:\n\n"
            "👋 أهلاً بك في رادار المراقبة!\n"
            "⏱️ الفحص كل: 5 دقائق."
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())
    else:
        bot.reply_to(message, "❌ عذراً، هذا الرادار خاص بالمدير فقط.")

# 4. معالجة الأوامر (أمثلة)
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "📊 إحصائيات":
        bot.reply_to(message, "📊 إحصائيات الرادار: مستقر ✅")
    elif message.text == "🛡️ حماية المحتوى":
        bot.reply_to(message, "🛡️ تم تفعيل حماية المحتوى بنجاح.")
    # يمكنك إضافة بقية وظائف الأزرار هنا بنفس الطريقة

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    threading.Thread(target=self_ping, daemon=True).start()
    print("📡 رادار المراقبة متصل...")
    bot.polling(none_stop=True)
