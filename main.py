from flask import Flask
from threading import Thread
import requests
import time

app = Flask('')

@app.route('/')
def home():
    return "مركز القيادة يعمل!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# قائمة بروابط بوتاتك اللي تبيها ما تنام
URLS = [
    "https://your-bot.replit.app" 
]

def ping_bots():
    while True:
        for url in URLS:
            try:
                requests.get(url)
                print(f"تم إنعاش: {url}")
            except:
                print(f"فشل الاتصال بـ: {url}")
        time.sleep(300) 

if __name__ == "__main__":
    keep_alive()
    ping_bots()
