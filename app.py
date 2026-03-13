from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

# !!! الربط مع ملف admin.py !!!
try:
    from admin import admin_bp
except ImportError:
    admin_bp = None

app = Flask(__name__)
app.secret_key = "eyin_final_stable_v45"

# تسجيل لوحة التحكم إذا الملف موجود
if admin_bp:
    app.register_blueprint(admin_bp)

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

def get_safe_settings():
    try:
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT key, value FROM settings")
        rows = cur.fetchall(); cur.close(); conn.close()
        res = {r['key']: r['value'] for r in rows}
        if 'store_name' not in res or not res['store_name']: res['store_name'] = "eyin"
        return res
    except: return {'store_name': 'eyin', 'logo': ''}

# القالب الموحد للمتجر
HTML_LAYOUT = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ st['store_name'] }}</title>
    <style>
        :root { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --border: #e2e8f0; --primary: #4f46e5; }
        [data-theme="dark"] { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --border: #334155; --primary: #818cf8; }
        body { font-family: sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; transition: 0.3s; min-height: 100vh; }
        .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto; }
        .card { background: var(--card); border-radius: 20px; padding: 15px; border: 1px solid var(--border); }
        .auth-box { max-width: 380px; margin: 40px auto; text-align: center; }
        .slogan { font-size: 1.1rem; font-weight: bold; margin-bottom: 20px; padding: 15px; border: 2px solid var(--primary); border-radius: 15px; color: var(--primary); background: rgba(129, 140, 248, 0.1); }
        .auth-card { background: var(--card); padding: 25px; border-radius: 20px; border: 1px solid var(--border); }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text); box-sizing: border-box; }
        .main-btn { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .alert { background: #ef4444; color: white; padding: 10px; border-radius: 10px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body data-theme="dark">
    <div class="header">
        <div style="display:flex; align-items:center; gap:10px;">
            {% if st['logo'] %}<img src="{{ st['logo'] }}" style="width:35px; height:35px; border-radius:50%;">{% endif %}
            <h2 style="margin:0;">{{ st['store_name'] }}</h2>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
            {% if session.get('user_id') %}
                <a href="/my-ads" style="text-decoration:none; color:var(--primary); font-weight:bold; font-size:14px;">إعلاناتي</a>
                <button onclick="document.getElementById('addModal').style.display='flex'" style="background:var(--primary); color:white; border:none; padding:8px 12px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:12px;">+ إعلان</button>
                <a href="/logout_user" style="color:red; text-decoration:none; font-size:12px;">خروج</a>
            {% endif %}
            <button onclick="toggleTheme()" style="cursor:pointer; border-radius:50%; width:35px; height:35px; border:none; background:var(--card); color:var(--text);" id="t-btn">🌙</button>
        </div>
    </div>

    <div style="max-width:380px; margin:auto; margin-top:20px;">
        {% with messages = get_flashed_messages() %}
          {% if messages %}{% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}{% endif %}
        {% endwith %}
    </div>

    {% block content %}{% endblock %}

    <script>
        function toggleTheme() {
            const b = document.body;
            const t = b.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            b.setAttribute('data-theme', t);
            localStorage.setItem('theme', t);
            document.getElementById('t-btn').innerText = t === 'dark' ? '☀️' : '🌙';
        }
        document.body.setAttribute('data-theme', localStorage.getItem('theme') || 'dark');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user_id' not in session: return redirect('/register')
    st = get_safe_settings()
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div class="grid">
        {% for p in prods %}
        <div class="card">
            <img src="{{p['image_url']}}" style="width:100%; height:180px; object-fit:contain; border-radius:10px;">
            <h3>{{p['name']}}</h3>
            <p style="color:var(--primary); font-weight:bold;">{{p['price']}} ريال</p>
            <p style="font-size:0.85rem; opacity:0.8;">{{p['description']}}</p>
            <a href="https://wa.me/{{p['whatsapp']}}" style="background:#22c55e; color:white; display:block; text-align:center; padding:10px; border-radius:10px; text-decoration:none; font-weight:bold; margin-top:10px;">واتساب</a>
        </div>
        {% endfor %}
    </div>
    <div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); align-items:center; justify-content:center; z-index:100;">
        <div style="background:var(--card); padding:20px; border-radius:20px; width:90%; max-width:400px;">
            <h3>نشر إعلان</h3>
            <form action="/add_public" method="post" enctype="multipart/form-data">
                <input type="text" name="name" placeholder="المنتج" required>
                <input type="number" name="price" placeholder="السعر" required>
                <textarea name="description" placeholder="الوصف..."></textarea>
                <input type="file" name="image_file" required>
                <button type="submit" class="main-btn">نشر</button>
                <button type="button" onclick="document.getElementById('addModal').style.display='none'" style="width:100%; margin-top:10px; background:none; border:none; color:gray; cursor:pointer;">إلغاء</button>
            </form>
        </div>
    </div>
    '''), st=st, prods=prods)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        p = "966"+request.form.get('phone')
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE phone = %s", (p,))
        if cur.fetchone():
            flash('الرقم مسجل مسبقاً، سجل دخولك')
            cur.close(); conn.close(); return redirect('/login')
        cur.close(); conn.close()
        session['temp'] = {'p': p, 'pw': request.form.get('password'), 'otp': str(random.randint(1000,9999))}
        return redirect('/verify')
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div class="auth-box">
        <div class="slogan">عـيـن فراش لك و عـيـن لحافي</div>
        <div class="auth-card">
            <h2>إنشاء حساب</h2>
            <form method="post">
                966+ <input type="number" name="phone" placeholder="5xxxxxxxx" required>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit" class="main-btn">تسجيل</button>
            </form>
            <p>لديك حساب؟ <a href="/login" style="color:var(--primary);">دخول</a></p>
        </div>
    </div>
    '''), st=get_safe_settings())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        p, pw = "966"+request.form.get('phone'), request.form.get('password')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone=%s AND password=%s", (p, pw))
        u = cur.fetchone(); cur.close(); conn.close()
        if u: session['user_id']=u['id']; session['user_phone']=u['phone']; return redirect('/')
        flash('الرقم أو كلمة المرور خطأ')
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div class="auth-box">
        <div class="slogan">عـيـن فراش لك و عـيـن لحافي</div>
        <div class="auth-card">
            <h2>دخول</h2>
            <form method="post">
                966+ <input type="number" name="phone" required>
                <input type="password" name="password" required>
                <button type="submit" class="main-btn">دخول</button>
            </form>
        </div>
    </div>
    '''), st=get_safe_settings())

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'temp' not in session: return redirect('/register')
    otp = session['temp']['otp']
    if request.method == 'POST':
        if request.form.get('otp') == otp:
            conn = get_db_connection(); cur = conn.cursor(); t = session['temp']
            cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (t['p'], t['pw']))
            conn.commit(); cur.close(); conn.close(); session.pop('temp')
            return redirect('/login')
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', f'''
    <div class="auth-box"><div class="auth-card">
        <h2>التحقق</h2>
        <a href="https://wa.me/966500000000?text=كود:{otp}" target="_blank" style="background:#25d366; color:white; padding:12px; text-decoration:none; border-radius:10px; display:block; margin-bottom:10px;">طلب الكود واتساب</a>
        <form method="post"><input type="number" name="otp" required><button type="submit" class="main-btn">تأكيد</button></form>
    </div></div>
    '''), st=get_safe_settings())

@app.route('/my-ads')
def my_ads():
    if 'user_id' not in session: return redirect('/login')
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products WHERE user_id=%s ORDER BY id DESC", (session['user_id'],))
    prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div style="padding:20px; max-width:1000px; margin:auto;">
        <h2>📦 إعلاناتي</h2> <a href="/" style="color:var(--primary); text-decoration:none;">⬅️ عودة</a>
        <div class="grid">
            {% for p in prods %}
            <div class="card">
                <img src="{{p['image_url']}}" style="width:100%; height:150px; object-fit:contain;">
                <h3>{{p['name']}}</h3>
                <form action="/delete_product" method="post"><input type="hidden" name="id" value="{{p['id']}}"><button type="submit" style="background:red; color:white; border:none; width:100%; padding:5px; border-radius:5px; cursor:pointer;">حذف</button></form>
            </div>
            {% endfor %}
        </div>
    </div>
    '''), st=get_safe_settings(), prods=prods)

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect('/login')
    f = request.files['image_file']; img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, description, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)", (session['user_id'], request.form.get('name'), request.form.get('price'), img, request.form.get('description'), session['user_phone']))
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
