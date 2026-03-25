__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for
import threading
import time
import requests

app = Flask(__name__)
DB_NAME = "database.db"

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, logo_url TEXT)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS products 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, description TEXT, img_url TEXT)''')
            if not conn.execute("SELECT * FROM settings").fetchone():
                conn.execute("INSERT INTO settings (logo_url) VALUES ('https://via.placeholder.com/150')")
            conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")

init_db()

# --- 2. وظيفة النغز الذاتي (Keep-alive) ---
def keep_alive():
    url = "https://eyin.onrender.com"
    while True:
        try:
            requests.get(url, timeout=10)
        except:
            pass
        time.sleep(180)

# --- 3. المتجر الرئيسي ---
@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        logo = conn.execute("SELECT logo_url FROM settings WHERE id=1").fetchone()
        logo_url = logo[0] if logo else "https://via.placeholder.com/150"
        products = conn.execute("SELECT name, price, description, img_url FROM products").fetchall()
    
    html_template = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجري الإلكتروني</title>
        <style>
            :root { --primary: #8A2BE2; --bg: #f4f7f6; }
            body { font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; }
            header { background: white; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .logo { max-width: 100px; border-radius: 50%; margin-bottom: 10px; }
            .container { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1200px; margin: 40px auto; padding: 0 20px; }
            .card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; transition: 0.3s; }
            .card img { width: 100%; height: 200px; object-fit: cover; }
            .info { padding: 20px; }
            .price { color: var(--primary); font-weight: bold; font-size: 1.3em; margin: 10px 0; display: block; }
            .btn { background: var(--primary); color: white; padding: 10px 25px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; }
            .admin-link { position: fixed; bottom: 10px; left: 10px; color: #ccc; text-decoration: none; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <header>
            <img src="{{ logo_url }}" class="logo">
            <h1>مرحباً بكم في متجرنا</h1>
        </header>
        <div class="container">
            {% for p in products %}
            <div class="card">
                <img src="{{ p[3] if p[3] else 'https://via.placeholder.com/300' }}">
                <div class="info">
                    <h3>{{ p[0] }}</h3>
                    <p>{{ p[2] }}</p>
                    <span class="price">{{ p[1] }}</span>
                    <a href="https://wa.me/966XXXXXXXXX?text=أريد طلب: {{ p[0] }}" class="btn">اطلب عبر واتساب</a>
                </div>
            </div>
            {% endfor %}
        </div>
        <a href="/admin" class="admin-link">لوحة التحكم</a>
    </body>
    </html>
    """
    return render_template_string(html_template, logo_url=logo_url, products=products)

# --- 4. لوحة التحكم ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    with sqlite3.connect(DB_NAME) as conn:
        if request.method == 'POST':
            if 'add' in request.form:
                conn.execute("INSERT INTO products (name, price, description, img_url) VALUES (?, ?, ?, ?)", 
                             (request.form['n'], request.form['p'], request.form['d'], request.form['i']))
            elif 'up_logo' in request.form:
                conn.execute("UPDATE settings SET logo_url = ? WHERE id=1", (request.form['l'],))
            elif 'del' in request.form:
                conn.execute("DELETE FROM products WHERE id = ?", (request.form['id'],))
            conn.commit()
            return redirect(url_for('admin'))

        products = conn.execute("SELECT * FROM products").fetchall()
        logo_res = conn.execute("SELECT logo_url FROM settings WHERE id=1").fetchone()
        logo = logo_res[0] if logo_res else "https://via.placeholder.com/150"

    admin_html = f"""
    <html dir="rtl"><head><meta charset="UTF-8"><style>
        body {{ font-family: sans-serif; padding: 20px; background: #eee; }}
        .section {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 10px; }}
        input, textarea {{ width: 100%; padding: 8px; margin: 5px 0; }}
        button {{ background: #28a745; color: white; border: none; padding: 10px; cursor: pointer; }}
    </style></head><body>
        <h1>لوحة تحكم المتجر ⚙️</h1>
        <div class="section">
            <h3>تحديث الشعار</h3>
            <form method="POST"><input type="text" name="l" value="{logo}"><button name="up_logo">تحديث</button></form>
        </div>
        <div class="section">
            <h3>إضافة منتج</h3>
            <form method="POST">
                <input name="n" placeholder="الاسم" required>
                <input name="p" placeholder="السعر" required>
                <textarea name="d" placeholder="الوصف"></textarea>
                <input name="i" placeholder="رابط الصورة">
                <button name="add">حفظ المنتج</button>
            </form>
        </div>
        <div class="section">
            <h3>المنتجات الحالية</h3>
            {''.join([f"<p>{p[1]} - <form method='POST' style='display:inline'><input type='hidden' name='id' value='{p[0]}'><button name='del' style='background:red'>حذف</button></form></p>" for p in products])}
        </div>
        <a href="/">العودة للمتجر</a>
    </body></html>
    """
    return render_template_string(admin_html)

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
