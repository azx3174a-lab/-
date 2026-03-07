import telebot
import requests
import time
import threading
import os
from telebot import types
from flask import Flask

# 1. إعداد التوكن من السيرفر (آمن)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 2. إعدادات الوقت والروابط
LINKS_FILE = "links.txt"
TIMER_FILE = "timer.txt"

def get_interval():
    if os.path.path.exists(TIMER_FILE):
        try:
            with open(TIMER_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 5
    return 5

def save_interval(minutes):
    with open(TIMER_FILE, "w") as f:
        f.write(str(minutes))

# 3. Flask للسيرفر
app = Flask('')

@app.route('/')
def home():
    return "✅ البوت المراقب يعمل بنجاح!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 4. خيط المراقبة (الرادار)
def monitor_threads():
    while True:
        interval = get_interval()
        if os.path.exists(LINKS_FILE):
            with open(LINKS_FILE, "r") as f:
                links = f.readlines()
            for link in links:
                link = link.strip()
                if link:
                    try:
                        requests.get(link, timeout=10)
                        print(f"🚀 تم نغز: {link}")
                    except:
                        print(f"❌ فشل نغز: {link}")
        time.sleep(interval * 60)

# 5. أوامر البوت
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("➕ إضافة رابط", callback_data="add")
    btn2 = types.InlineKeyboardButton("📋 قائمة الروابط", callback_data="list")
    btn3 = types.InlineKeyboardButton("⏱️ تعديل الوقت", callback_data="set_time")
    markup.add(btn1, btn2, btn3)
    
    interval = get_interval()
    bot.send_message(message.chat.id, f"👋 مرحباً بك في رادار المراقبة!\n\nنحن الآن ننغز الروابط كل {interval} دقائق.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "add":
        msg = bot.send_message(call.message.chat.id, "ارسل رابط الـ Webview اللي تبي نراقبه:")
        bot.register_next_step_handler(msg, save_link)
    elif call.data == "list":
        if os.path.exists(LINKS_FILE):
            with open(LINKS_FILE, "r") as f:
                links = f.read()
            if links.strip():
                bot.send_message(call.message.chat.id, f"🔗 الروابط المراقبة حالياً:\n\n{links}")
            else:
                bot.send_message(call.message.chat.id, "القائمة فارغة 💨")
        else:
            bot.send_message(call.message.chat.id, "لا توجد روابط مضافة بعد.")
    elif call.data == "set_time":
        msg = bot.send_message(call.message.chat.id, "أرسل عدد الدقائق الجديد (رقم فقط):")
        bot.register_next_step_handler(msg, update_timer)

def save_link(message):
    link = message.text
    if "http" in link:
        with open(LINKS_FILE, "a") as f:
            f.write(link + "\n")
        bot.reply_to(message, "✅ تم إضافة الرابط بنجاح!")
    else:
        bot.reply_to(message, "❌ خطأ! يرجى إرسال رابط صحيح.")

def update_timer(message):
    try:
        new_time = int(message.text)
        if new_time < 1:
            bot.reply_to(message, "⚠️ أقل وقت مسموح هو دقيقة واحدة.")
            return
        save_interval(new_time)
        bot.reply_to(message, f"✅ تم تحديث وقت الفحص إلى {new_time} دقائق.")
    except:
        bot.reply_to(message, "❌ يرجى إرسال رقم صحيح فقط.")

# 6. تشغيل كل شيء
if __name__ == "__main__":
    # تشغيل Flask في خيط منفصل
    threading.Thread(target=run_flask).start()
    # تشغيل الرادار في خيط منفصل
    threading.Thread(target=monitor_threads).start()
    # تشغيل بوت التليجرام
    bot.polling(none_stop=True)
