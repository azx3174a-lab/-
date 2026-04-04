__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "sub_manager_2026"
DB_NAME = "subs.db"
ADMIN_PASSWORD = "123" # كلمة المرور للدخول

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS subs 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, renew_date TEXT)''')
        conn.commit()

init_db()

# --- 2. الواجهة الرئيسية (عرض الاشتراكات) ---
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    with sqlite3.connect(DB_NAME) as conn:
        subs = conn.execute("SELECT id, name, price, renew_date FROM subs").fetchall()
        total = conn.execute("SELECT SUM(price) FROM subs").fetchone()[0] or 0
    
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مدير الاشتراكات 💳</title>
        <style>
            body { font-family: sans-serif; background: #f0f2f5; margin: 0; padding: 20px; text-align: center; }
            .container { max-width: 600_px; margin: auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            .total-card { background: #8A2BE2; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .sub-item { display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid #eee; align-items: center; }
            .sub-info { text-align: right; }
            .price { font-weight: bold; color: #28a745; }
            .date { font-size: 0.8em; color: #666; }
            .btn-add { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }
            .btn-del { color: red; text-decoration: none; font-size: 0.9em; border: 1px solid red; padding: 2px 8px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="total-card">
                <h2>إجمالي الاشتراكات</h2>
                <h1 style="margin:5px 0;">{{total}} ريال/شهر</h1>
            </div>

            <h3>قائمة الاشتراكات 📋</h3>
            {% for s in subs %}
            <div class="sub-item">
                <div class="sub-info">
                    <div style="font-weight:bold;">{{s[1]}}</div>
                    <div class="date">تاريخ التجديد: {{s[3]}}</div>
                </div>
                <div>
                    <span class="price">{{s[2]}} ريال</span>
                    <a href="/delete/{{s[0]}}" class="btn-del" onclick="return confirm('متأكد؟')">حذف</a>
                </div>
            </div>
            {% endfor %}

            <hr>
            <h4>إضافة اشتراك جديد</h4>
            <form method="POST" action="/add">
                <input name="n" placeholder="اسم الاشتراك (مثلاً: نتفليكس)" required style="width:80%; margin:5px; padding:8px;">
                <input name="p" type="number" step="0.01" placeholder="السعر" required style="width:80%; margin:5px; padding:8px;">
                <input name="d" type="date" required style="width:80%; margin:5px; padding:8px;">
                <button style="width:85%; padding:10px; background:#28a745; color:white; border:none; border-radius:5px; margin-top:10px;">إضافة</button>
            </form>
            <br>
            <a href="/logout" style="color:#666; font-size:0.8em;">تسجيل الخروج</a>
        </div>
    </body></html>
    """
    return render_template_string(html, subs=subs, total=total)

# --- 3. العمليات (إضافة وحذف) ---
@app.route('/add', methods=['POST'])
def add():
    if session.get('logged_in'):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO subs (name, price, renew_date) VALUES (?, ?, ?)", 
                         (request.form['n'], request.form['p'], request.form['d']))
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('logged_in'):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("DELETE FROM subs WHERE id = ?", (id,))
    return redirect(url_for('index'))

# --- 4. نظام الدخول ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('pass') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return '<body style="text-align:center;padding-top:100px;font-family:sans-serif;"><form method="POST"><h2>كلمة مرور المدير</h2><input type="password" name="pass" autofocus><button>دخول</button></form></body>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
