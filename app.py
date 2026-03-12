from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_admin_panel_v28"

# !!! بيانات الإدارة - يفضل تغيير الباسورد !!!
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
ADMIN_WHATSAPP = "966550963174"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
    # قيم افتراضية للإعدادات
    defaults = {
        'store_name': 'متجر عيـن',
        'logo': '',
        'twitter': '',
        'instagram': '',
        'tiktok': ''
    }
    for k, v in defaults.items():
        cur.execute("INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO NOTHING", (k, v))
    
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, user_id INTEGER, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT)")
    conn.commit(); cur.close(); conn.close()

init_db()

def get_settings():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT key, value FROM settings")
    s = {row[0]: row[1] for row in cur.fetchall()}
    cur.close(); conn.close()
    return s

# --- لوحة التحكم (Admin) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged'):
        if request.method == 'POST':
            if request.form.get('user') == ADMIN_USER and request.form.get('pass') == ADMIN_PASS:
                session['admin_logged'] = True
                return redirect(url_for('admin'))
        return '''<div dir="rtl" style="text-align:center; padding:50px;">
                    <form method="post">
                        <input name="user" placeholder="اسم المستخدم"><br><br>
                        <input type="password" name="pass" placeholder="كلمة المرور"><br><br>
                        <button type="submit">دخول الإدارة</button>
                    </form></div>'''
    
    s = get_settings()
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); all_prods = cur.fetchall()
    cur.close(); conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة التحكم</title>
        <style>
            :root { --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --primary: #4f46e5; }
            body { font-family: sans-serif; background: var(--bg); color: var(--text); padding: 20px; }
            .section { background: var(--card); padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #ddd; }
            input { width: 100%; padding: 10px; margin: 10px 0; border-radius: 8px; border: 1px solid #ccc; }
            .save-btn { background: #22c55e; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
            .del-btn { background: #ef4444; color: white; border: none; padding: 5px 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>⚙️ مركز التحكم بالمتجر</h1>
        <a href="/">⬅️ عودة للموقع</a> | <a href="/admin_logout" style="color:red;">خروج</a>
        
        <div class="section">
            <h3>🎨 إعدادات المظهر والهوية</h3>
            <form action="/admin/update_settings" method="post" enctype="multipart/form-data">
                <label>اسم المتجر:</label>
                <input type="text" name="store_name" value="{{ s['store_name'] }}">
                <label>تحديث الشعار (اختياري):</label>
                <input type="file" name="logo_file">
                <hr>
                <h3>📱 مواقع التواصل الاجتماعي</h3>
                <input type="text" name="twitter" placeholder="رابط تويتر" value="{{ s['twitter'] }}">
                <input type="text" name="instagram" placeholder="رابط انستقرام" value="{{ s['instagram'] }}">
                <input type="text" name="tiktok" placeholder="رابط تيك توك" value="{{ s['tiktok'] }}">
                <button type="submit" class="save-btn">حفظ التغييرات ✅</button>
            </form>
        </div>

        <div class="section">
            <h3>📦 إدارة جميع الإعلانات</h3>
            <table border="1" style="width:100%; border-collapse: collapse; text-align:center;">
                <tr><th>المنتج</th><th>صاحب الإعلان</th><th>الإجراء</th></tr>
                {% for p in prods %}
                <tr>
                    <td>{{ p['name'] }}</td>
                    <td>{{ p['whatsapp'] }}</td>
                    <td>
                        <form action="/admin/delete_any" method="post">
                            <input type="hidden" name="id" value="{{ p['id'] }}">
                            <button class="del-btn">حذف نهائي</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    ''', s=s, prods=all_prods)

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    if not session.get('admin_logged'): return redirect('/admin')
    conn = get_db_connection(); cur = conn.cursor()
    
    # تحديث النصوص
    fields = ['store_name', 'twitter', 'instagram', 'tiktok']
    for field in fields:
        cur.execute("UPDATE settings SET value = %s WHERE key = %s", (request.form.get(field), field))
    
    # تحديث الشعار إذا تم رفعه
    if 'logo_file' in request.files and request.files['logo_file'].filename != '':
        f = request.files['logo_file']
        img_data = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
        cur.execute("UPDATE settings SET value = %s WHERE key = 'logo'", (img_data,))
    
    conn.commit(); cur.close(); conn.close()
    return redirect('/admin')

# --- الصفحة الرئيسية المحدثة ---
@app.route('/')
def index():
    s = get_settings()
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); products = cur.fetchall()
    cur.close(); conn.close()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ s['store_name'] }}</title>
        <style>
            :root { --bg: #ffffff; --card: #f1f5f9; --text: #1e293b; --primary: #4f46e5; }
            [data-theme="dark"] { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #818cf8; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; transition: 0.3s; padding-bottom: 100px; }
            .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto; }
            .card { background: var(--card); border-radius: 20px; padding: 15px; border: 1px solid #ddd; }
            .footer { position: fixed; bottom: 0; left: 0; width: 100%; background: var(--card); padding: 15px; text-align: center; border-top: 1px solid #ddd; display: flex; justify-content: center; gap: 20px; }
            .social-icon { text-decoration: none; font-size: 20px; }
            .theme-btn { background: #000; color: #fff; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; }
            [data-theme="dark"] .theme-btn { background: #fff; color: #000; }
        </style>
    </head>
    <body>
        <div class="header">
            <div style="display:flex; align-items:center; gap:10px;">
                {% if s['logo'] %}<img src="{{ s['logo'] }}" width="45" style="border-radius:50%;">{% endif %}
                <h2 style="margin:0;">{{ s['store_name'] }}</h2>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
                {% if session.get('user_id') %}
                    <a href="/my-ads">إعلاناتي</a>
                    <button onclick="document.getElementById('addModal').style.display='flex'" style="background:var(--primary); color:white; border:none; padding:8px 15px; border-radius:10px;">+ إعلان</button>
                {% else %}
                    <a href="/login">دخول</a>
                {% endif %}
                <button class="theme-btn" onclick="toggleTheme()" id="t-btn">🌙</button>
            </div>
        </div>

        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] }}" style="width:100%; height:180px; object-fit:contain; border-radius:10px;">
                <h3>{{ p['name'] }}</h3>
                <div style="color:var(--primary); font-weight:bold;">{{ p['price'] }} ريال</div>
                <a href="https://wa.me/{{ p['whatsapp'] }}" style="display:block; background:#22c55e; color:white; text-align:center; padding:10px; border-radius:10px; text-decoration:none; margin-top:10px;">واتساب</a>
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            {% if s['twitter'] %}<a href="{{ s['twitter'] }}" class="social-icon">𝕏</a>{% endif %}
            {% if s['instagram'] %}<a href="{{ s['instagram'] }}" class="social-icon">📸</a>{% endif %}
            {% if s['tiktok'] %}<a href="{{ s['tiktok'] }}" class="social
