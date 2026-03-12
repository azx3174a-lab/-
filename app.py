from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_fix_v26"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# --- دالة إصلاح قاعدة البيانات تلقائياً ---
def fix_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # إنشاء الجداول الأساسية إذا لم توجد
    cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
    cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT)")
    
    # إضافة الأعمدة الناقصة لجدول المنتجات لتجنب خطأ 500
    try:
        cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
    except: pass
    
    conn.commit()
    cur.close()
    conn.close()

# تنفيذ الإصلاح عند تشغيل التطبيق
fix_db()

# --- صفحة إعلاناتي الشخصية ---
@app.route('/my-ads')
def my_ads():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products WHERE user_id = %s ORDER BY id DESC", (session['user_id'],))
    user_products = cur.fetchall()
    cur.close(); conn.close()
    return render_template_string('''
        <div dir="rtl" style="font-family:sans-serif; padding:20px;">
            <h2>📦 إعلاناتي</h2>
            <a href="/">⬅️ العودة للمتجر</a><hr>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:20px;">
                {% for p in products %}
                <div style="border:1px solid #ddd; padding:15px; border-radius:15px;">
                    <img src="{{ p['image_url'] }}" style="width:100%; height:150px; object-fit:contain;">
                    <h3>{{ p['name'] }}</h3>
                    <form action="/delete_product" method="post"><input type="hidden" name="id" value="{{ p['id'] }}"><button type="submit" style="background:red; color:white; border:none; width:100%; padding:10px; border-radius:10px;">حذف 🗑️</button></form>
                </div>
                {% endfor %}
            </div>
        </div>
    ''', products=user_products)

# --- الصفحة الرئيسية ---
@app.route('/')
def index():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); products = cur.fetchall()
    cur.execute("SELECT value FROM settings WHERE key = 'logo'"); logo = cur.fetchone()
    cur.close(); conn.close(); logo_url = logo['value'] if logo else ""
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر عين</title>
        <style>
            :root { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --primary: #4f46e5; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; }
            .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto; }
            .card { background: var(--card); border-radius: 20px; border: 1px solid #e2e8f0; padding: 15px; }
            .btn-buy { background: #22c55e; color: white; text-decoration: none; display: block; text-align: center; padding: 12px; border-radius: 12px; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <div style="display:flex; align-items:center; gap:10px;">
                {% if logo_url %}<img src="{{ logo_url }}" width="40" height="40" style="border-radius:50%;">{% endif %}
                <h2 style="margin:0;">متجر عيـن</h2>
            </div>
            <div>
                {% if session.get('user_id') %}
                    <a href="/my-ads" style="text-decoration:none; margin-left:10px;">إعلاناتي</a>
                    <button onclick="document.getElementById('addModal').style.display='flex'" style="background:var(--primary); color:white; border:none; padding:8px 12px; border-radius:10px;">+ إعلان</button>
                {% else %}
                    <a href="/login" style="text-decoration:none; color:var(--primary); font-weight:bold;">دخول</a>
                {% endif %}
            </div>
        </div>
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}" style="width:100%; height:200px; object-fit:contain;">
                <h3>{{ p['name'] }}</h3>
                <div style="font-weight:bold; color:var(--primary);">{{ p['price'] }} ريال</div>
                <p>{{ p['description'] }}</p>
                <a href="https://wa.me/{{ p['whatsapp'] }}" class="btn-buy" target="_blank">واتساب</a>
            </div>
            {% endfor %}
        </div>
        <div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); align-items:center; justify-content:center; z-index:100;">
            <div style="background:white; padding:20px; border-radius:20px; width:90%; max-width:400px;">
                <h3>إضافة إعلان جديد</h3>
                <form action="/add_public" method="post" enctype="multipart/form-data">
                    <input type="text" name="name" placeholder="اسم المنتج" required style="width:100%; padding:10px; margin:5px 0;">
                    <input type="number" name="price" placeholder="السعر" required style="width:100%; padding:10px; margin:5px 0;">
                    <textarea name="description" placeholder="وصف السلعة" style="width:100%; padding:10px; margin:5px 0;"></textarea>
                    <input type="file" name="image_file" required style="margin:10px 0;">
                    <button type="submit" style="width:100%; padding:12px; background:var(--primary); color:white; border:none; border-radius:10px;">نشر الآن</button>
                    <button type="button" onclick="document.getElementById('addModal').style.display='none'" style="width:100%; background:none; border:none; color:#999; margin-top:10px;">إلغاء</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    ''', products=products, logo_url=logo_url)

# --- مسارات تسجيل الدخول والتحقق (نفس النسخة السابقة مع تجميل) ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_phone = "966" + request.form.get('phone')
        otp_code = str(random.randint(1000, 9999))
        session['temp_user'] = {'phone': full_phone, 'password': request.form.get('password'), 'otp': otp_code}
        return redirect(url_for('verify_otp'))
    return render_template_string('<div dir="rtl" style="text-align:center; padding:50px;"><h2>تسجيل جديد</h2><form method="post">966+ <input type="number" name="phone" required><br><input type="password" name="password" placeholder="كلمة المرور" required><br><button type="submit">دخول</button></form></div>')

@app.route('/verify', methods=['GET', 'POST'])
def verify_otp():
    if 'temp_user' not in session: return redirect(url_for('register'))
    otp = session['temp_user']['otp']
    wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text=كود تفعيل متجر عين لرقبي هو: {otp}"
    if request.method == 'POST':
        if request.form.get('otp') == otp:
            conn = get_db_connection(); cur = conn.cursor(); t = session['temp_user']
            cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (t['phone'], t['password']))
            conn.commit(); cur.close(); conn.close(); session.pop('temp_user'); return redirect(url_for('login'))
    return render_template_string(f'<div dir="rtl" style="text-align:center; padding:50px;"><h2>تحقق</h2><a href="{wa_link}" target="_blank">اضغط هنا لطلب الكود من الإدارة</a><br><br><form method="post"><input type="number" name="otp" placeholder="ادخل الكود"><button type="submit">تأكيد</button></form></div>')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = "966" + request.form.get('phone')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone = %s AND password = %s", (phone, request.form.get('password')))
        user = cur.fetchone(); cur.close(); conn.close()
        if user: session['user_id'] = user['id']; session['user_phone'] = user['phone']; return redirect(url_for('index'))
    return render_template_string('<div dir="rtl" style="text-align:center; padding:50px;"><h2>دخول</h2><form method="post">966+ <input type="number" name="phone" required><br><input type="password" name="password" required><br><button type="submit">دخول</button></form></div>')

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect(url_for('login'))
    img_data = f"data:{request.files['image_file'].content_type};base64,{base64.b64encode(request.files['image_file'].read()).decode('utf-8')}"
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, description, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)", 
                (session['user_id'], request.form.get('name'), request.form.get('price'), img_data, request.form.get('description'), session['user_phone']))
    conn.commit(); cur.close(); conn.close(); return redirect(url_for('index'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if 'user_id' in session:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = %s AND user_id = %s", (request.form.get('id'), session['user_id']))
        conn.commit(); cur.close(); conn.close()
    return redirect(url_for('my_ads'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
