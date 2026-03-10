import telebot
import os
from flask import Flask
import threading
import time
import requests

# 1. إعدادات البوت الأساسية
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
OWNER_ID = 123456789  # 💡 ضع الأيدي الخاص بك هنا
RENDER_URL = "https://commander-bot-dxgc.onrender.com"

# قائمة المشرفين (تخزن في الذاكرة مؤقتاً)
admins = {}

app = Flask('')

@app.route('/')
def home(): return "✅ بوت القائد يعمل بنجاح!"

# 2. نظام النغز الذاتي (إبقاء البوت حياً)
def self_ping():
    while True:
        try:
            requests.get(RENDER_URL, timeout=10)
            print("🚀 تم نغز السيرفر بنجاح")
        except: pass
        time.sleep(5 * 60)

# 3. أوامر لوحة التحكم
@bot.message_handler(commands=['start', 'panel'])
def send_panel(message):
    if message.from_user.id == OWNER_ID or message.from_user.id in admins:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"))
        markup.add(telebot.types.InlineKeyboardButton("📢 إذاعة", callback_data="broadcast"))
        bot.reply_to(message, "🛠️ أهلاً بك في لوحة تحكم القائد:", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ عذراً، هذا البوت خاص بالمطور فقط.")

# 4. تشغيل السيرفر والبوت
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    threading.Thread(target=self_ping, daemon=True).start()
    print("🤖 بوت القائد متصل الآن...")
    bot.polling(none_stop=True)
