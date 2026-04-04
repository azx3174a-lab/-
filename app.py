__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "sub_manager_no_pass"
DB_NAME = "subs.db"

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS subs 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, renew_date TEXT)''')
        conn.commit()

init_db()

# --- 2. الواجهة الرئيسية (بدون قفل) ---
@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        subs = conn.execute("SELECT id, name, price, renew_date FROM subs").fetchall()
        total_res = conn.execute("SELECT SUM(price) FROM subs").fetchone()[0]
        total = round(total_res, 2) if total_res else 0
    
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مدير الاشتراكات 💳</title>
        <style>
            body { font-family: sans-serif; background: #f8f9fa; margin: 0; padding: 15px; color: #333; }
            .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
            .total-card { background: linear-gradient(135deg, #25D366, #075E54); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; }
            .sub-item { display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid #f1f1f1; align-items: center; }
            .price { font-weight: bold; color: #2ecc71; font-size: 1.1em; }
            .btn-del { color: #ff4757; text-decoration: none; border: 1px solid #ff4757; padding: 3px 10px; border-radius: 6px; font-size: 0.8em; transition: 0.3s; }
            .btn-del:hover { background: #ff4757; color: white; }
            input, button { width: 100%; margin: 8px 0; padding: 12px; border-radius: 10px; border: 1px solid #ddd; box-sizing: border-box; }
            button { background: #075E54; color: white; border: none; font-weight: bold; cursor: pointer; font-size: 1em; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="total-card">
                <p style="margin:0; opacity:0.9;">مجموع التزاماتك الشهرية</p>
                <h1 style="margin:5px 0; font-size: 2.2em;">{{total}} <small style="font-size:0.5em;">ريال</small></h1>
            </div>

            <h3 style="text-align:right; margin-bottom:10px;">الاشتراكات النشطة 📋</h3>
            {% for s in subs %}
            <div class="sub-item">
                <div style="text-align:right;">
                    <b style="font-size:1.05em;">{{s[1]}}</b><br>
                    <small style="color:#888;">موعد التجديد: {{s[3]}}</small>
                </div>
                <div style="text-align:left;">
                    <div class="price">{{s[2]}} ريال</div>
                    <a href="/delete/{{s[0]}}" class="btn-del" onclick="return confirm('هل تريد حذف هذا الاشتراك؟')">حذف</a>
                </div>
            </div>
            {% endfor %}

            <div style="margin-top:30px; background:#fdfdfd; padding:15px; border-radius:15px; border: 1px dashed #ccc;">
                <h4 style="margin-top:0;">إضافة اشتراك جديد ➕</h4>
                <form method="POST" action="/add">
                    <input name="n" placeholder="اسم الخدمة (مثلاً: ايكلاود)" required>
                    <input name="p" type="number" step="0.01" placeholder="السعر الشهري" required>
                    <input name="d" type="date" required>
                    <button type="submit">إضافة للقائمة</button>
                </form>
            </div>
        </div>
    </body></html>
    """
    return render_template_string(html, subs=subs, total=total)

# --- 3. العمليات ---
@app.route('/add', methods=['POST'])
def add():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO subs (name, price, renew_date) VALUES (?, ?, ?)", 
                     (request.form['n'], request.form['p'], request.form['d']))
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM subs WHERE id = ?", (id,))
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
