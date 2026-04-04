__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3
import threading
import time
from datetime import datetime, timedelta
import requests
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "sub_manager_whatsapp_auth"
DB_NAME = "subs.db"

# --- إعدادات CallMeBot ---
# ملاحظة: يجب أن تحصل على الـ API KEY من البوت (+34 621 07 33 87) على الواتساب
API_KEY = "YOUR_API_KEY_HERE" 

def send_whatsapp_msg(phone, text):
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={text}&apikey={API_KEY}"
    try: requests.get(url, timeout=10)
    except: pass

# --- دالة التذكير التلقائي في الخلفية ---
def check_reminders():
    while True:
        try:
            with sqlite3.connect(DB_NAME) as conn:
                # نجلب الاشتراكات مع رقم الجوال المرتبط بها
                subs = conn.execute("SELECT name, renew_date, user_phone FROM subs").fetchall()
                tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                
                for name, r_date, phone in subs:
                    if r_date == tomorrow:
                        msg = f"⚠️ تذكير: اشتراك ({name}) سيجدد غداً!"
                        send_whatsapp_msg(phone, msg)
        except: pass
        time.sleep(86400) # فحص يومي

# --- إعداد قاعدة البيانات ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS subs 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, renew_date TEXT, user_phone TEXT)''')
        conn.commit()

init_db()

# --- واجهة تسجيل الدخول بالرقم ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone').strip().replace('+', '')
        if len(phone) > 8: # تحقق بسيط من طول الرقم
            session['user_phone'] = phone
            return redirect(url_for('index'))
    return '''
    <body style="font-family:sans-serif; text-align:center; padding-top:100px; background:#f0f2f5;">
        <div style="display:inline-block; background:white; padding:40px; border-radius:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1);">
            <h2 style="color:#075E54;">دخول مدير الاشتراكات 🟢</h2>
            <p style="color:#666;">أدخل رقم واتسابك (بالصيغة الدولية)</p>
            <form method="POST">
                <input name="phone" placeholder="9665XXXXXXXX" required style="padding:12px; width:250px; border:1px solid #ddd; border-radius:8px;"><br><br>
                <button style="padding:12px 30px; background:#25D366; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">دخول وتفعيل التنبيهات</button>
            </form>
        </div>
    </body>
    '''

# --- الواجهة الرئيسية ---
@app.route('/')
def index():
    if 'user_phone' not in session: return redirect(url_for('login'))
    
    phone = session['user_phone']
    with sqlite3.connect(DB_NAME) as conn:
        subs = conn.execute("SELECT id, name, price, renew_date FROM subs WHERE user_phone = ?", (phone,)).fetchall()
        total_res = conn.execute("SELECT SUM(price) FROM subs WHERE user_phone = ?", (phone,)).fetchone()[0]
        total = round(total_res, 2) if total_res else 0
    
    html = """
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>اشتراكاتي 💳</title>
        <style>
            body { font-family: sans-serif; background: #f8f9fa; padding: 15px; }
            .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            .header { background: #075E54; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
            .sub-item { display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid #eee; }
            .btn-del { color: red; text-decoration: none; font-size: 0.8em; }
            input, button { width: 100%; margin: 5px 0; padding: 12px; border-radius: 8px; border: 1px solid #ddd; }
            button { background: #25D366; color: white; border: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <p style="margin:0;">مرحباً بك: {{phone}}</p>
                <h1 style="margin:10px 0;">{{total}} ريال/شهر</h1>
            </div>
            {% for s in subs %}
            <div class="sub-item">
                <div style="text-align:right;"><b>{{s[1]}}</b><br><small>تجديد: {{s[3]}}</small></div>
                <div style="text-align:left;"><b>{{s[2]}} ريال</b><br><a href="/delete/{{s[0]}}" class="btn-del">حذف</a></div>
            </div>
            {% endfor %}
            <form method="POST" action="/add" style="margin-top:20px;">
                <input name="n" placeholder="اسم الاشتراك" required>
                <input name="p" type="number" step="0.01" placeholder="السعر" required>
                <input name="d" type="date" required>
                <button>إضافة وإرسال تذكير للواتساب 📱</button>
            </form>
            <center><a href="/logout" style="color:#999; font-size:0.8em; text-decoration:none;">تسجيل الخروج</a></center>
        </div>
    </body></html>
    """
    return render_template_string(html, subs=subs, total=total, phone=phone)

@app.route('/add', methods=['POST'])
def add():
    if 'user_phone' in session:
        phone = session['user_phone']
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO subs (name, price, renew_date, user_phone) VALUES (?, ?, ?, ?)", 
                         (request.form['n'], request.form['p'], request.form['d'], phone))
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    if 'user_phone' in session:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("DELETE FROM subs WHERE id = ? AND user_phone = ?", (id, session['user_phone']))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    threading.Thread(target=check_reminders, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
