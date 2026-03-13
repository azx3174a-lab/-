from flask import Flask, render_template_string, request, redirect, url_for, session
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_custom_v36"

# !!! ضع رقم واتسابك هنا لاستقبال طلبات الأكواد !!!
ADMIN_WHATSAPP = "966550963174" 

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
        cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
        cur.execute("INSERT INTO settings (key, value) VALUES ('store_name', 'eyin') ON CONFLICT (key) DO NOTHING")
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT, user_id INTEGER)")
        conn.commit(); cur.close(); conn.close()
    except: pass

init_db()

def get_settings():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT key, value FROM settings")
    rows = cur.fetchall(); cur.close(); conn.close()
    return {r['key']: r['value'] for r in rows}

# --- القالب الموحد ---
LAYOUT_START = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ settings['store_name'] }}</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --border: #334155; --primary: #818cf8; --btn-bg: #fff; --btn-text: #000; }
        [data-theme="light"] { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --border: #e2e8f0; --primary: #4f46e5; --btn-bg: #000; --btn-text: #fff; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; transition: 0.3s; }
        .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
        .logo-container { display: flex; align-items: center; gap: 10px; }
        .logo-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
        .theme-btn { background: var(--btn-bg); color: var(--btn-text); border: none; cursor: pointer; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto; }
        .card { background: var(--card); border-radius: 20px; border: 1px solid var(--border); padding: 15px; }
        .auth-box { max-width: 380px; margin: 40px auto; text-align: center; }
        .slogan { font-size: 1.2rem; font-weight: bold; margin-bottom: 25px; padding: 15px; border: 2px solid var(--primary); border-radius: 15px; color: var(--primary); background: rgba(129, 140, 248, 0.1); }
        .auth-card { background: var(--card); padding: 30px; border-radius: 25px; border: 1px solid var(--border); }
        input, textarea { width: 100%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text); box-sizing: border-box; }
        .main-btn { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 10px; }
    </style>
</head>
<body data-theme="dark">
    <div class="header">
        <div class="logo-container">
            {% if settings['logo'] %}<img src="{{ settings['logo'] }}" class="logo-img">{% endif %}
            <h2 style="margin:0;">{{ settings['store_name'] }}</h2>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
"""

LAYOUT_END = """
            <button class="theme-btn" onclick="toggleTheme()" id="theme-icon">🌙</button>
        </div>
    </div>
    <script>
        function toggleTheme() {
            var b = document.body;
            var t = b.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            b.setAttribute('data-theme', t);
            localStorage.setItem('eyin_theme', t);
            document.getElementById('theme-icon').innerText = (t === 'dark' ? '☀️' : '🌙');
        }
        document.body.setAttribute('data-theme', localStorage.getItem('eyin_theme') || 'dark');
    </script>
</body>
</html>
"""

def wrap(content, settings):
    user_nav = ""
    if 'user_id' in session:
        user_nav = f'<a href="/my-ads" style="text-decoration:none; color:var(--primary); font-weight:bold; font-size:14px;">إعلاناتي</a><button onclick="document.getElementById(\'addModal\').style.display=\'flex\'" style="background:var(--primary); color:white; border:none; padding:8px 12px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:12px;">+ إعلان</button><a href="/logout_user" style="color:red; font-size:12px; text-decoration:none;">خروج</a>'
    return render_template_string(LAYOUT_START + user_nav + LAYOUT_END.replace('</body>', content + '</body>'), settings=settings)

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('register'))
    st = get_settings()
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    
    cards = "".join([f'<div class="card"><img src="{p["image_url"]}" style="width:100%; height:180px; object-fit:contain; border-radius:10px;"><h3>{p["name"]}</h3><div style="font-weight:bold; color:var(--primary);">{p["price"]} ريال</div><p style="font-size:0.8rem;">{p["description"]}</p><a href="https://wa.me/{p["whatsapp"]}" style="background:#22c55e; color:white; text-decoration:none; display:block; text-align:center; padding:10px; border-radius:10px; font-weight:bold;">واتساب</a></div>' for p in prods])
    modal = '<div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); align-items:center; justify-content:center; z-index:100;"><div style="background:var(--card); padding:20px; border-radius:20px; width:90%; max-width:400px;"><h3>نشر إعلان</h3><form action="/add_public" method="post" enctype="multipart/form-data"><input type="text" name="name" placeholder="ماذا تبيع؟" required><input type="number" name="price" placeholder="السعر" required><textarea name="description" placeholder="الوصف"></textarea><input type="file" name="image_file" required><button type="submit" class="main-btn">نشر الآن</button><button type="button" onclick="document.getElementById(\'addModal\').style.display=\'none\'" style="width:100%; margin-top:10px; background:none; border:none; color:gray;">إلغاء</button></form></div></div>'
    return wrap(f'<div class="grid">{cards}</div>{modal}', st)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['temp'] = {'p': "966"+request.form.get('phone'), 'pw': request.form.get('password'), 'otp': str(random.randint(1000,9999))}
        return redirect('/verify')
    return wrap('''
    <div class="auth-box">
        <div class="slogan">عـيـن فراش لك و عـيـن لحافي</div>
        <div class="auth-card">
            <h2 style="margin-top:0;">إنشاء حساب</h2>
            <form method="post">
                <div style="display:flex; align-items:center; background:var(--bg); border:1px solid var(--border); border-radius:10px; padding:0 10px;">
                    <span style="font-weight:bold; opacity:0.7;">966+</span>
                    <input type="number" name="phone" placeholder="5xxxxxxxx" required style="border:none; margin:0;">
                </div>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit" class="main-btn">تسجيل</button>
            </form>
            <p style="font-size:14px; margin-top:20px;">لديك حساب؟ <a href="/login" style="color:var(--primary); text-decoration:none; font-weight:bold;">دخول</a></p>
        </div>
    </div>
    ''', get_settings())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        p, pw = "966"+request.form.get('phone'), request.form.get('password')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone=%s AND password=%s", (p, pw))
        u = cur.fetchone(); cur.close(); conn.close()
        if u: session['user_id']=u['id']; session['user_phone']=u['phone']; return redirect('/')
    return wrap('''
    <div class="auth-box">
        <div class="slogan">عـيـن فراش لك و عـيـن لحافي</div>
        <div class="auth-card">
            <h2 style="margin-top:0;">تسجيل دخول</h2>
            <form method="post">
                <div style="display:flex; align-items:center; background:var(--bg); border:1px solid var(--border); border-radius:10px; padding:0 10px;">
                    <span style="font-weight:bold; opacity:0.7;">966+</span>
                    <input type="number" name="phone" placeholder="5xxxxxxxx" required style="border:none; margin:0;">
                </div>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit" class="main-btn">دخول</button>
            </form>
            <p style="font-size:14px; margin-top:20px;">جديد؟ <a href="/register" style="color:var(--primary); text-decoration:none; font-weight:bold;">أنشئ حساب</a></p>
        </div>
    </div>
    ''', get_settings())

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'temp' not in session: return redirect('/register')
    otp = session['temp']['otp']
    wa = f"https://wa.me/{ADMIN_WHATSAPP}?text=كود تفعيل متجر عين: {otp}"
    if request.method == 'POST':
        if request.form.get('otp') == otp:
            conn = get_db_connection(); cur = conn.cursor(); t = session['temp']
            cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (t['p'], t['pw']))
            conn.commit(); cur.close(); conn.close(); session.pop('temp'); return redirect('/')
    return wrap(f'''<div class="auth-box"><div class="auth-card"><h2>تحقق</h2><a href="{wa}" target="_blank" style="background:#25d366; color:white; padding:15px; text-decoration:none; border-radius:12px; display:block; margin-bottom:20px;">طلب الكود واتساب</a><form method="post"><input type="number" name="otp" required><button type="submit" class="main-btn">تأكيد</button></form></div></div>''', get_settings())

@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400': session['admin']=True
        elif session.get('admin'):
            conn = get_db_connection(); cur = conn.cursor()
            action = request.form.get('action')
            if action == 'update_logo':
                f = request.files['logo_file']
                if f:
                    img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
                    cur.execute("UPDATE settings SET value=%s WHERE key='logo'", (img,))
            elif action == 'update_name':
                cur.execute("UPDATE settings SET value=%s WHERE key='store_name'", (request.form.get('store_name'),))
            elif action == 'delete':
                cur.execute("DELETE FROM products WHERE id=%s", (request.form.get('id'),))
            conn.commit(); cur.close(); conn.close(); return redirect('/eyin-control')
    if not session.get('admin'): return '<form method="post" style="padding:50px; text-align:center;">🔐 <input type="password" name="password"><button type="submit">دخول</button></form>'
    st = get_settings()
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    p_list = "".join([f'<div style="border-bottom:1px solid #ddd; padding:10px; display:flex; justify-content:space-between;"><span>{p["name"]}</span> <form method="post" style="display:inline;"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="{p["id"]}"><button type="submit" style="color:red; background:none; border:none; cursor:pointer;">حذف</button></form></div>' for p in prods])
    return f'''<div dir="rtl" style="padding:20px; font-family:sans-serif; max-width:500px; margin:auto;"><h2>🛠️ إعدادات المتجر</h2><div style="background:#f0f0f0; padding:15px; border-radius:15px; margin-bottom:10px;"><h3>1️⃣ الشعار</h3><form method="post" enctype="multipart/form-data"><input type="hidden" name="action" value="update_logo"><input type="file" name="logo_file" required><button type="submit">تحديث</button></form></div><div style="background:#f0f0f0; padding:15px; border-radius:15px; margin-bottom:10px;"><h3>2️⃣ الاسم</h3><form method="post"><input type="hidden" name="action" value="update_name"><input type="text" name="store_name" value="{st['store_name']}" required><button type="submit">حفظ</button></form></div><hr>{p_list}<br><a href="/">العودة</a></div>'''

@app.route('/my-ads')
def my_ads():
    if 'user_id' not in session: return redirect('/login')
    st = get_settings()
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products WHERE user_id=%s ORDER BY id DESC", (session['user_id'],))
    prods = cur.fetchall(); cur.close(); conn.close()
    cards = "".join([f'<div class="card"><img src="{p["image_url"]}" style="width:100%; height:150px; object-fit:contain;"><h3>{p["name"]}</h3><form action="/delete_product" method="post"><input type="hidden" name="id" value="{p["id"]}"><button type="submit" style="background:#ef4444; color:white; border:none; width:100%; padding:8px; border-radius:8px; cursor:pointer;">حذف</button></form></div>' for p in prods])
    return wrap(f'<h2>📦 إعلاناتي</h2><div class="grid">{cards}</div>', st)

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect('/login')
    f = request.files['image_file']; img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, description, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)", 
                (session['user_id'], request.form.get('name'), request.form.get('price'), img, request.form.get('description'), session['user_phone']))
    conn.commit(); cur.close(); conn.close(); return redirect('/')

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if 'user_id' in session:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id=%s AND user_id=%s", (request.form.get('id'), session['user_id']))
        conn.commit(); cur.close(); conn.close()
    return redirect('/my-ads')

@app.route('/logout_user')
def logout_user(): session.clear(); return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
