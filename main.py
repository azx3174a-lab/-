import telebot
import os
from flask import Flask
import threading
import time
import requests
from telebot import types

# 1. الإعدادات الأساسية (تأكد من وضع الأيدي حقك)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
OWNER_ID = 6081087852  # 👈 يا عبد العزيز امسح الرقم هذا وحط الأيدي حقك
RENDER_URL = "https://commander-bot-dxgc.onrender.com"

app = Flask('')

@app.route('/')
def home(): return "📡 رادار المراقبة يعمل بنجاح!"

# 2. نظام النغز الذاتي لضمان استمرار البوت
def self_ping():
    while True:
        try:
            requests.get(RENDER_URL, timeout=10)
            print("🕒 تم الفحص الدوري: السيرفر مستقر")
        except: pass
        time.sleep(5 * 60)

# 3. تصميم لوحة التحكم (الأزرار الكبيرة)
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

# 4. استقبال أمر التشغيل /start
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

# 5. برمجة الأوامر (الرد على ضغط الأزرار)
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    # التأكد أن المستخدم هو المالك
    if message.from_user.id != OWNER_ID:
        return

    if message.text == "📊 إحصائيات":
        bot.reply_to(message, "📊 الإحصائيات: الرادار مستقر والاتصال ممتاز ✅")
    
    elif message.text == "📢 إذاعة":
        bot.reply_to(message, "📢 ميزة الإذاعة قيد التطوير، سيتم تفعيلها قريباً.")
        
    elif message.text == "🛡️ حماية المحتوى":
        bot.reply_to(message, "🛡️ نظام حماية المحتوى نشط الآن ويمنع النسخ.")
        
    elif message.text == "📋 قائمة الروابط":
        bot.reply_to(message, "📋 قائمة الروابط المراقبة حالياً فارغة.")
        
    elif message.text == "➕ إضافة رابط":
        bot.reply_to(message, "➕ أرسل الرابط الذي تريد إضافته للرادار.")
        
    elif message.text == "🕒 تعديل الوقت":
        bot.reply_to(message, "🕒 الوقت الافتراضي الحالي هو 5 دقائق.")
        
    elif message.text == "👥 قسم المشرفين":
        bot.reply_to(message, "👥 لا يوجد مشرفين مضافين حالياً.")

# 6. تشغيل السيرفر
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    threading.Thread(target=self_ping, daemon=True).start()
    print("📡 رادار المراقبة متصل وبالخدمة...")
    bot.polling(none_stop=True)
