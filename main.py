import telebot
import os
import google.generativeai as genai
from flask import Flask
import threading
import time
import requests

# 1. إعدادات المفاتيح من Render
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = "https://commander-bot-dxgc.onrender.com" # رابط بوتك في ريندر

# إعداد محرك Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "🤖 بوت القائد الذكي يعمل الآن!"

# 2. نظام النغز الذاتي (كل 5 دقائق)
def self_ping():
    while True:
        try:
            requests.get(RENDER_URL, timeout=10)
            print("🚀 تم نغز الذكاء الاصطناعي بنجاح")
        except: pass
        time.sleep(5 * 60)

# 3. استقبال السوالف والرد عليها
@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    try:
        # إظهار حالة "يكتب الآن..."
        bot.send_chat_action(message.chat.id, 'typing')
        
        # إرسال الرسالة لـ Gemini
        response = model.generate_content(message.text)
        
        # الرد بالذكاء الاصطناعي
        bot.reply_to(message, response.text, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "❌ حصل خطأ في الاتصال بالذكاء الاصطناعي، تأكد من المفتاح في ريندر.")

# 4. التشغيل
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    threading.Thread(target=self_ping, daemon=True).start()
    bot.polling(none_stop=True)
