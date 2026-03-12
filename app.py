from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os
import psycopg2
from psycopg2.extras import DictCursor
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = "eyin_auth_system_v21"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # جدول الإعدادات
    cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
    cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
    # جدول المستخدمين الجديد
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # تحديث جدول المنتجات ليرتبط بالمستخدم
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            name TEXT,
            price TEXT,
            image_url TEXT,
            description TEXT,
            whatsapp TEXT
        )
    """)
    # جدول التعليقات
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY, 
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            author TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# --- نظام تسجيل الدخول ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone = %s AND password = %s", (phone, password))
        user = cur.fetchone()
        cur.close(); conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_phone'] = user['phone']
            return redirect(url_for('index'))
        flash('❌ عذراً، رقم الجوال أو كلمة المرور غير صحيحة', 'error')
    return render_template_string('''
        <div dir="rtl" style="font-family:sans-serif; text-align:center; padding:50px;">
            <h2>تسجيل الدخول برقم الجوال</h2>
            <form method="post" style="display:inline-block; width:300px;">
                <input type="text" name="phone" placeholder="رقم الجوال" required style="width:100%; padding:10px; margin:5px;"><br>
                <input type="password" name="password" placeholder="كلمة المرور" required style="width:100%; padding:10px; margin:5px;"><br>
                <button type="submit" style="width:100%; padding:10px; background:#4f46e5; color:white; border:none; border-radius:5px;">دخول</button>
            </form>
            <p>ليس لديك حساب؟ <a href="/register">إنشاء حساب جديد</a></p>
            <a href="/">العودة للمتجر</a>
        </div>
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (phone, password))
            conn.commit()
            flash('✅ تم إنشاء الحساب بنجاح، يمكنك الدخول الآن', 'success')
            return redirect(url_for('login'))
        except:
            flash('❌ هذا الرقم مسجل مسبقاً', 'error')
        finally:
            cur.close(); conn.close()
    return render_template_string('''
        <div dir="rtl" style="font-family:sans-serif; text-align:center; padding:50px;">
            <h2>إنشاء حساب جديد بالرقم</h2>
            <form method="post" style="display:inline-block; width:300px;">
                <input type="text" name="phone" placeholder="رقم الجوال (966...)" required style="width:100%; padding:10px; margin:5px;"><br>
                <input type="password" name="password" placeholder="اختر كلمة مرور" required style="width:100%; padding:10px; margin:5px;"><br>
                <button type="submit" style="width:100%; padding:10px; background:#25d366; color:white; border:none; border-radius:5px;">تسجيل</button>
            </form>
            <p>لديك حساب؟ <a href="/login">تسجيل دخول</a></p>
        </div>
    ''')

@app.route('/logout_user')
def logout_user():
    session.clear()
    return redirect(url_for('index'))

# --- الصفحة الرئيسية ---
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    
    # معالجة الحذف (لصاحب الإعلان فقط)
    if request.method == 'POST' and request.form.get('action') == 'delete':
        if 'user_id' in session:
            cur.execute("DELETE FROM products WHERE id = %s AND user_id = %s", (request.form.get('id'), session['user_id']))
            conn.commit()
            flash('✅ تم حذف المنتج', 'success')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.execute("SELECT * FROM comments ORDER BY created_at ASC")
    all_comments = cur.fetchall()
    cur.execute("SELECT value FROM settings WHERE key = 'logo'")
    logo = cur.fetchone()
    cur.close(); conn.close()
    
    logo_url = logo['value'] if logo and logo['value'] else ""
    
    html = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر عين</title>
        <style>
            :root { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --muted: #64748b; --primary: #4f46e5; --border: #e2e8f0; --btn-bg: #000000; --btn-text: #ffffff; }
            [data-theme="dark"] { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --muted: #94a3b8; --primary: #818cf8; --border: #334155; --btn-bg: #ffffff; --btn-text: #000000; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; transition: 0.3s; }
            .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; }
            .theme-btn { background: var(--btn-bg); color: var(--btn-text); border: none; padding: 8px; border-radius: 50%; cursor: pointer; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto; }
            .card { background: var(--card); border-radius: 20px; border: 1px solid var(--border); overflow: hidden; padding: 15px; }
            .card img { width: 100%; height: 200px; object-fit: contain; border-radius: 10px; }
            .btn-buy { background: #25d366; color: white; text-decoration: none; display: block; text-align: center; padding: 10px; border-radius: 10px; font-weight: bold; margin-top: 10px; }
            .nav-link { text-decoration: none; color: var(--primary); font-weight: bold; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="header">
            <div style="display:flex; align-items:center; gap:10px;">
                {% if logo_url %}<img src="{{ logo_url }}" width="40" height="40" style="border-radius:50%;">{% endif %}
                <h2 style="margin:0;">متجر عيـن</h2>
            </div>
            <div style="display:flex; gap:15px; align-items:center;">
                {% if session.get('user_id') %}
                    <span style="font-size:12px;">مرحباً: {{ session['user_phone'] }}</span>
                    <button onclick="document.getElementById('addModal').style.display='flex'" style="background:var(--primary); color:white; border:none; padding:8px 12px; border-radius:8px; cursor:pointer;">+ إعلان</button>
                    <a href="/logout_user" class="nav-link" style="color:#ef4444;">خروج</a>
                {% else %}
                    <a href="/login" class="nav-link">تسجيل دخول</a>
                {% endif %}
                <button class="theme-btn" onclick="toggleTheme()" id="theme-icon">🌙</button>
            </div>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}{% for c, m in messages %}<div style="text-align:center; padding:10px; color:{{ '#22c55e' if c=='success' else '#ef4444' }};">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}">
                <h3>{{ p['name'] }}</h3>
                <div style="font-weight:bold; color:var(--primary);">{{ p['price'] }} ريال</div>
                <p style="font-size:0.9rem; color:var(--muted);">{{ p['description'] }}</p>
                <a href="https://wa.me/{{ p['whatsapp'] }}" class="btn-buy" target="_blank">واتساب</a>
                
                {% if session.get('user_id') == p['user_id'] %}
                <form method="post" style="margin-top:10px;">
                    <input type="hidden" name="id" value="{{ p['id'] }}">
                    <input type="hidden" name="action" value="delete">
                    <button type="submit" style="background:#ef4444; color:white; border:none; width:100%; padding:5px; border-radius:5px; cursor:pointer;">حذف إعلاني 🗑️</button>
                </form>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        <div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); align-items:center; justify-content:center; z-index:100;">
            <div style="background:var(--card); padding:20px; border-radius:20px; width:90%; max-width:400px;">
                <h3>إضافة إعلان جديد</h3>
                <form action="/add_public" method="post" enctype="multipart/form-data">
                    <input type="text" name="name" placeholder="اسم المنتج" required style="width:100%; padding:10px; margin:5px 0;">
                    <input type="number" name="price" placeholder="السعر" required style="width:100%; padding:10px; margin:5px 0;">
                    <textarea name="description" placeholder="وصف السلعة" style="width:100%; padding:10px; margin:5px 0;"></textarea>
                    <input type="file" name="image_file" required style="margin:10px 0;">
                    <button type="submit" style="width:100%; padding:10px; background:var(--primary); color:white; border:none; border-radius:10px;">نشر الإعلان</button>
                    <button type="button" onclick="document.getElementById('addModal').style.display='none'" style="width:100%; background:none; border:none; color:var(--muted); margin-top:10px;">إلغاء</button>
                </form>
            </div>
        </div>

        <script>
            function toggleTheme() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                document.getElementById('theme-icon').innerText = newTheme === 'dark' ? '☀️' : '🌙';
            }
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html, products=products, all_comments=all_comments, logo_url=logo_url)

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect(url_for('login'))
    name, price, desc = request.form.get('name'), request.form.get('price'), request.form.get('description')
    img_data = ""
    if 'image_file' in request.files:
        f = request.files['image_file']
        img_data = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, description, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)", 
                (session['user_id'], name, price, img_data, desc, session['user_phone']))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('index'))

@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400': session['logged_in'] = True
        elif 'logged_in' in session:
            conn = get_db_connection(); cur = conn.cursor()
            if request.form.get('action') == 'admin_delete':
                cur.execute("DELETE FROM products WHERE id = %s", (request.form.get('id'),))
                conn.commit()
            cur.close(); conn.close()
            return redirect(url_for('admin'))
    if not session.get('logged_in'): return '🔐 <form method="post"><input type="password" name="password"><button type="submit">دخول</button></form>'
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall()
    cur.close(); conn.close()
    return render_template_string('''<div dir="rtl"><h2>لوحة الإدارة</h2>{% for p in prods %}<div>{{ p['name'] }} <form method="post"><input type="hidden" name="action" value="admin_delete"><input type="hidden" name="id" value="{{ p['id'] }}"><button type="submit">حذف نهائي</button></form></div>{% endfor %}<a href="/">عودة</a></div>''', prods=prods)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
