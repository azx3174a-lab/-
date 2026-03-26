__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3
import base64
from flask import Flask, render_template_string, request, redirect, url_for, session
import threading
import time
import requests

app = Flask(__name__)
app.secret_key = "ein_store_v2_key"
DB_NAME = "database.db"
ADMIN_PASSWORD = "123" 

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, logo_img_data TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, description TEXT, img_data TEXT)''')
        if not conn.execute("SELECT * FROM settings").fetchone():
            conn.execute("INSERT INTO settings (logo_img_data) VALUES ('')")
        conn.commit()

def keep_alive():
    url = "https://eyin.onrender.com"
    while True:
        try: requests.get(url, timeout=10)
        except: pass
        time.sleep(180)

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        logo_res = conn.execute("SELECT logo_img_data FROM settings WHERE id=1").fetchone()
        logo_data = logo_res[0] if logo_res else ""
        products = conn.execute("SELECT name, price, description, img_data FROM products").fetchall()
    
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر عين</title>
        <style>
            :root { --primary: #8A2BE2; --bg: #f4f7f6; }
            body { font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; }
            header { background: white; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .logo { max-width: 100px; border-radius: 50%; }
            .container { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1200px; margin: 40px auto; padding: 0 20px; }
            .card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; }
            .card img { width: 100%; height: 200px; object-fit: cover; }
            .info { padding: 20px; }
            .price { color: var(--primary); font-weight: bold; font-size: 1.2em; }
            .btn { background: var(--primary); color: white; padding: 10px 25px; border-radius: 25px; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <header><img src="{{l}}" class="logo"><h1>متجر عين</h1></header>
        <div class="container">
            {% for p in products %}
            <div class="card">
                <img src="{{p[4] if p[4] else p[3]}}">
                <div class="info">
                    <h3>{{p[0]}}</h3><p>{{p[2]}}</p><span class="price">{{p[1]}}</span><br><br>
                    <a href="https://wa.me/966XXXXXXXXX?text=طلب: {{p[0]}}" class="btn">اطلب واتساب</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </body></html>
    """
    return render_template_string(html, l=logo_data, products=products)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'login_pass' in request.form:
        if request.form['login_pass'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
    if not session.get('logged_in'):
        return '<form method="POST" style="text-align:center;padding-top:100px;"><input type="password" name="login_pass"><button>دخول</button></form>'

    with sqlite3.connect(DB_NAME) as conn:
        if request.method == 'POST':
            if 'add' in request.form:
                file = request.files['img']
                if file:
                    img_data = f"data:{file.content_type};base64,{base64.b64encode(file.read()).decode('utf-8')}"
                    conn.execute("INSERT INTO products (name, price, description, img_data) VALUES (?, ?, ?, ?)", (request.form['n'], request.form['p'], request.form['d'], img_data))
            elif 'up_logo' in request.form:
                file = request.files['logo_img']
                if file:
                    logo_data = f"data:{file.content_type};base64,{base64.b64encode(file.read()).decode('utf-8')}"
                    conn.execute("UPDATE settings SET logo_img_data = ? WHERE id=1", (logo_data,))
            elif 'del' in request.form:
                conn.execute("DELETE FROM products WHERE id = ?", (request.form['id'],))
            conn.commit()
            return redirect(url_for('admin'))
        products = conn.execute("SELECT * FROM products").fetchall()
    return render_template_string('<html dir="rtl"><body><h2>لوحة التحكم</h2><form method="POST" enctype="multipart/form-data"><h3>شعار المتجر:</h3><input type="file" name="logo_img"><button name="up_logo">تحديث الشعار</button><h3>إضافة منتج:</h3><input name="n" placeholder="الاسم"><input name="p" placeholder="السعر"><textarea name="d"></textarea><input type="file" name="img"><button name="add">حفظ</button></form><hr>{% for p in products %}<p>{{p[1]}} <form method="POST" style="display:inline"><input type="hidden" name="id" value="{{p[0]}}"><button name="del">حذف</button></form></p>{% endfor %}</body></html>', products=products)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
