import telebot
import os
from flask import Flask
import threading
import time
import requests
from bs4 import BeautifulSoup # مكتبة لسحب الأخبار

# 1. الإعدادات
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
OWNER_ID = 6081087852  # 👈 حط الأيدي حقك هنا يا عبد العزيز
LAST_NEWS_TITLE = "" # لتخزين آخر خبر تم إرساله ومنع التكرار

app = Flask('')
@app.route('/')
def home(): return "📈 رادار تداول نشط الآن"

# 2. وظيفة جلب الأخبار من موقع تداول
def fetch_tadawul_news():
    global LAST_NEWS_TITLE
    url = "https://www.saudiexchange.sa/wps/portal/saudiexchange/newsandannouncements/market-news?locale=ar"
    
    while True:
        try:
            response = requests.get(url, timeout=20)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن أول خبر في القائمة (حسب هيكلة موقع تداول)
            news_section = soup.find('div', class_='news_announcement_item') 
            if news_section:
                title = news_section.find('h3').text.strip()
                link = "https://www.saudiexchange.sa" + news_section.find('a')['href']
                
                # إذا كان الخبر جديد ولم يتم إرساله من قبل
                if title != LAST_NEWS_TITLE:
                    message = f"🔔 **خبر جديد من تداول:**\n\n📍 {title}\n\n🔗 [رابط الخبر]({link})"
                    bot.send_message(OWNER_ID, message, parse_mode="Markdown")
                    LAST_NEWS_TITLE = title
                    print(f"✅ تم إرسال خبر: {title}")
        except Exception as e:
            print(f"❌ خطأ في جلب الأخبار: {e}")
        
        time.sleep(120) # يفحص الموقع كل دقيقتين (120 ثانية)

# 3. تشغيل السيرفر
if __name__ == "__main__":
    # تشغيل مراقب الأخبار في خلفية الكود
    threading.Thread(target=fetch_tadawul_news, daemon=True).start()
    
    # تشغيل Flask للبقاء حياً على Render
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    
    print("🚀 رادار تداول بدأ العمل...")
    bot.polling(none_stop=True)
