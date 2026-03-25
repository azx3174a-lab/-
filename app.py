__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import sqlite3
import base64
from flask import Flask, render_template_string, request, redirect, url_for, session
import threading
import time
import requests
from io import BytesIO

app = Flask(__name__)
app.secret_key = "ein_store_secure_key_v2" # مفتاح تشفير الجلسة
DB_NAME = "database.db"
ADMIN_PASSWORD = "3174" # كلمة مرور لوحة التحكم

# --- 1. إعداد قاعدة البيانات ---
# قمنا بتعديل جدول settings ليخزن بيانات الصورة (img_data) بدلاً من الرابط
def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            # إنشاء جدول الإعدادات إذا لم يكن موجوداً
            conn.execute('''CREATE TABLE IF NOT EXISTS settings (
                                id INTEGER PRIMARY KEY, 
                                logo_img_data TEXT
                            )''')
            # إنشاء جدول المنتجات إذا لم يكن موجوداً
            conn.execute('''CREATE TABLE IF NOT EXISTS products (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                name TEXT, 
                                price TEXT, 
                                description TEXT, 
                                img_data TEXT
                            )''')
            
            # وضع شعار افتراضي إذا كان الجدول فارغاً
            if not conn.execute("SELECT * FROM settings").fetchone():
                # شعار افتراضي رمزي (Placeholder) بصيغة Base64
                default_logo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5QMCEToXBd6mYAAABvVJREFUeNrtXXtoXFUU/83MvDP3vWcmSZMmLdP20bZpU9vUalVaxVpEitqiFasVfIHYClor+Mco+McoKArig/pAFHwUfBSf+ChWfIIVfIIVXwXfRUVEWpImbZpm0zSZmSSTuXdmfvxxZ5I0vXfmzj333mTSfDAsyT0zd875zvnO75xzf4CJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiUlX5N8OYFfBfR+A4wAOAegFsAOAqR9vAygAuAzgFwC3AfwC4AKAi/rfS/wY+p4P3I64fFzL5fN83MOfvO+j4pcoP2wE0AfgVAB/Vf+T8mOqG9sL4D6uR4H4M9w2uP8WAPcCeI74W64E68E+AnAPgF+XgXUf8fX8D6wXAVzD9XyN9V5cD/Y34us5VAPrGICrXF9XgvVFXM//wfoSrvVwDaxf4fo1rsF+9XANrBfi+jWu447XG9vO7mD3Y9vFHZ6/rC5D7rN6P7Z/G67/7G4H0v3E378dYve67t5XwX85wN/F9XN7D5p4fSbe+0pT3W5rXb/f2zbw938C/C1UvX4S//4D9Ym5m/YAsNvbI/0S4M8b+I/45C72R1Vb940Xwz5S7R/r75H6m7ifA/wS/W+T+tWk67OqrbuW9u5S9fT7G6m6P9bXm4H65v678Wj/mFTn6fofA/wGq7WfWp9XdbbXUvWfS3V9pv67AL8UqvP09f5K/V5v/6vS3fUvP6f6bS7Xp9W5V9X6RKrPrfUvP6f6bT4f3yXUObvWp9X6ZKp/OdfP7z3o5u7tB38N4Ge4ftYm4i5X/z5S/2T9Z1R/C/f3U7W/S+pfK9dPdZ6u9TNV67tNdbv43UeqX/zY5W4/2eP937Wf9vYvF9W5pXp7b6XqHn5P//6q0t4HqbqH7S/V9mUv55bq3N469yr9e7v+nLp6/N3q7f0V9XvO//p6P1b693w9r0p3d7vWd5vqnFvL9V84V1vHwS0Wv6D4mMTfN4qPSf7rR/ER4D4f7iA+A9wnKvxR4C4f7kAV/ij98wXf46M9Y984N/beF8G87/i9b9vT964b+/rL8bXf8vunC37O5v2SgV9fGf+G5eFvX5m+R7wP+6C38379B+r/Vqof9mHVv454X9tT4P7j5bF9VfO5b4/F59w778bHnNf5vG/4Oedl/9vjY3PO5594XvfB/85/Y87bfeF7N+6vE7N6z7Yn3w5X9Y5tV77vV/COfTdfpfrvP/bXn3H//Xf8O/bd/bXid9w794l98p9SHeofVv0f7jWf4/t7zfH/wB1vOq/j5e8Xf5P44zXfI/O4z3u1jnuYf6C5b0Cpf9wH74r9vS+K/v7P4v3YftrX59X47bivv76G344v2L/p9+Nrsf8I4H0L/bWv0/rFqC8H4Ivx+W583ov4H8D5OnwX8L6G/wEAv8Z6AcAF4u95XUv8594B8A6xvoPrG7wX4X+2H6wG1m0A3gZwC9d7uG4mto//0Y5XFdfDdbSrfbWrbO94O8p//9XOf//vUuI/X3f8N+M+5XjVw74n6f2P0mP/E/T/3P09v74mO79v4X/N1/S7W79T6u5n//tUv4v/BvAn9L+r/bT/BfT/HPr/C51X1v8bWv5/Xcv7v5F//zD9PwD/F9X//87//6fXj9f3S7y+4S9fP9666yvVzXU21X/27//7wK+wTqG9F9Y63FvCehv/j7H/5+z+Zvrv95V//646n+4r5L9/pPoYfF/v/+b/V/W8/qF5//v/4wK7u9v//3U6D4//X/5+YmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiYmJiUlfEP8F+xK5T4MId6AAAAAASUVORK5CYII="
                conn.execute("INSERT INTO settings (logo_img_data) VALUES (?)", (default_logo,))
            conn.commit()
    except Exception as e:
        print(f"قاعدة البيانات جاهزة. خطأ (إن وجد): {e}")

init_db()

# --- 2. وظيفة النغز الذاتي (Keep-alive) ---
def keep_alive():
    url = "https://eyin.onrender.com"
    while True:
        try: requests.get(url, timeout=10)
        except: pass
        time.sleep(180)

# --- 3. صفحة المتجر الأساسية (بدون تغيير في التصميم) ---
@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        logo_res = conn.execute("SELECT logo_img_data FROM settings WHERE id=1").fetchone()
        logo_data = logo_res[0] if logo_res else ""
        products = conn.execute("SELECT name, price, description, img_data FROM products").fetchall()
    
    html_template = """
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
            .logo { max-width: 100px; border-radius: 50%; margin-bottom: 10px; }
            .container { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1200px; margin: 40px auto; padding: 0 20px; }
            .card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; transition: 0.3s; }
            .card:hover { transform: translateY(-5px); }
            .card img { width: 100%; height: 200px; object-fit: cover; }
            .info { padding: 20px; }
            .price { color: var(--primary); font-weight: bold; font-size: 1.3em; margin: 10px 0; display: block; }
            .btn { background: var(--primary); color: white; padding: 10px 25px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; }
            .admin-link { position: fixed; bottom: 10px; left: 10px; color: #ccc; text-decoration: none; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <header>
            <img src="{{ logo_data }}" class="logo">
            <h1>مرحباً بكم في متجر عين</h1>
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
    return render_template_string(html_template, logo_data=logo_data, products=products)

# --- 4. لوحة التحكم (Admin Panel) المحدثة ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # الحماية بكلمة مرور
    if request.method == 'POST' and 'login_pass' in request.form:
        if request.form['login_pass'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "كلمة مرور خاطئة! <a href='/admin'>حاول ثانية</a>"

    if not session.get('logged_in'):
        return '<html dir="rtl"><body style="text-align:center; padding-top:100px; font-family:sans-serif; background:#eee;">' \
               '<div style="background:white; display:inline-block; padding:30px; border-radius:10px;">' \
               '<h2>دخول الإدارة 🔐</h2><form method="POST"><input type="password" name="login_pass" placeholder="كلمة المرور" style="padding:10px;"><br><br>' \
               '<button type="submit" style="padding:10px 20px; background:#8A2BE2; color:white; border:none; border-radius:5px; cursor:pointer;">دخول</button></form></div></body></html>'

    with sqlite3.connect(DB_NAME) as conn:
        if request.method == 'POST':
            # إضافة منتج جديد
            if 'add' in request.form:
                file = request.files['img']
                if file:
                    img_stream = base64.b64encode(file.read()).decode('utf-8')
                    img_data = f"data:{file.content_type};base64,{img_stream}"
                    conn.execute("INSERT INTO products (name, price, description, img_data) VALUES (?, ?, ?, ?)", 
                                 (request.form['n'], request.form['p'], request.form['d'], img_data))
            
            # تحديث الشعار (الرفع المباشر الجديد)
            elif 'up_logo' in request.form:
                file = request.files['logo_img']
                if file:
                    # تحويل صورة الشعار إلى Base64
                    img_stream = base64.b64encode(file.read()).decode('utf-8')
                    logo_data = f"data:{file.content_type};base64,{img_stream}"
                    conn.execute("UPDATE settings SET logo_img_data = ? WHERE id=1", (logo_data,))
            
            # حذف منتج
            elif 'del' in request.form:
                conn.execute("DELETE FROM products WHERE id = ?", (request.form['id'],))
            
            # خروج
            elif 'logout' in request.form:
                session.pop('logged_in', None)
                return redirect(url_for('index'))
            conn.commit()
            return redirect(url_for('admin'))

        products = conn.execute("SELECT * FROM products").fetchall()
        # جلب الشعار لعرضه في لوحة التحكم
        logo_res = conn.execute("SELECT logo_img_data FROM settings WHERE id=1").fetchone()
        current_logo_data = logo_res[0] if logo_res else ""

    admin_html = f"""
    <html dir="rtl"><head><meta charset="UTF-8"><style>
        body {{ font-family: sans-serif; background: #f0f2f5; padding: 20px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; }}
        .box {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        input, textarea {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        button {{ background: #28a745; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; font-weight: bold; }}
        .btn-del {{ background: #dc3545; padding: 5px 10px; font-size: 0.8em; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; border-bottom: 1px solid #eee; text-align: right; }}
        .current-logo {{ max-width: 80px; border-radius: 5px; margin-top: 10px; display: block; }}
    </style></head><body>
        <div class="header">
            <h2>لوحة تحكم متجر عين 👁️</h2>
            <form method="POST"><button name="logout" style="background:#666;">خروج</button></form>
        </div>
        
        <div class="box">
            <h3>تحديث شعار المتجر (رفع مباشر)</h3>
            {% if current_logo_data %}
                <label>الشعار الحالي:</label>
                <img src="{{ current_logo_data }}" class="current-logo">
                <br>
            {% endif %}
            <form method="POST" enctype="multipart/form-data">
                <label>اختر صورة الشعار الجديدة:</label><br>
                <input type="file" name="logo_img" accept="image/*" required><br><br>
                <button name="up_logo" style="background:#8A2BE2;">تحديث الشعار</button>
            </form>
        </div>
        
        <div class="box">
            <h3>إضافة منتج جديد (رفع مباشر للصور)</h3>
            <form method="POST" enctype="multipart/form-data">
                <input name="n" placeholder="اسم المنتج" required>
                <input name="p" placeholder="السعر" required>
                <textarea name="d" placeholder="الوصف"></textarea>
                <label>اختر صورة المنتج:</label><br>
                <input type="file" name="img" accept="image/*" required><br><br>
                <button name="add">حفظ المنتج ونشره</button>
            </form>
        </div>
        
        <div class="box">
            <h3>المنتجات الحالية</h3>
            <table>
                <tr><th>المنتج</th><th>السعر</th><th>التحكم</th></tr>
                {''.join([f"<tr><td>{p[1]}</td><td>{p[2]}</td><td><form method='POST' style='display:inline'><input type='hidden' name='id' value='{p[0]}'><button name='del' class='btn-del'>حذف</button></form></td></tr>" for p in products])}
            </table>
        </div>
        <a href="/">العودة للمتجر</a>
    </body></html>
    """
    return render_template_string(admin_html, current_logo_data=current_logo_data, products=products)

if __name__ == "__main__":
    # إنشاء قاعدة البيانات قبل تشغيل السيرفر
    init_db()
    # تشغيل النغز الذاتي في خلفية منفصلة
    threading.Thread(target=keep_alive, daemon=True).start()
    # تشغيل تطبيق Flask
    app.run(host='0.0.0.0', port=8080)
